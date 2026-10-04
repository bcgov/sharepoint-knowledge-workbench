"""
forms_analysis.py

Purpose:
    Analyses an exported custom list-form inventory and classifies each form as
    out-of-box, script-based, or InfoPath/custom-layout, with a caller-supplied
    modernization strategy per classification.

    Read-only: reads a JSON export file from the local filesystem and writes report
    artifacts to a caller-specified output directory. No SharePoint tenant I/O.

Layer: plugins/sharepoint-site-assessment -- analysis

Key Input Dependencies:
    - A form inventory JSON array. Each entry:
        listName, isCustomized, hasScript, formType
    - A form classification rules JSON file mapping formKind
      ("outOfBox" | "script" | "infopath") to a strategy string
      (see assets/form-classification-rules.json).

Provenance:
    Extracted from the originating SharePoint migration repository's custom list
    form analysis script at the pinned source commit. See
    docs/reports/phase-9-reusable-sharepoint-plugin-extraction/provenance.md.
"""

from __future__ import annotations

import json
from pathlib import Path

from discovery_inputs import DiscoveryOutcome, DiscoveryStatus, load_json_input, require_output_dir

DOMAIN = "forms"

#: Neutral, project-free default rules shipped with this plugin.
DEFAULT_RULES_PATH = Path(__file__).resolve().parent / "assets" / "form-classification-rules.json"


def load_rules(rules_path: str | Path) -> dict:
    """Load a form classification rules file. Raises FileNotFoundError if absent."""
    return json.loads(Path(rules_path).read_text(encoding="utf-8"))


def _classify(form: dict) -> str:
    if not form.get("isCustomized", False):
        return "outOfBox"
    if form.get("hasScript", False):
        return "script"
    return "infopath"


def analyse(forms: list[dict], rules: dict) -> dict:
    """Produce a classified form inventory from a forms export."""
    strategies = rules.get("strategies", {})
    counts = {"outOfBox": 0, "script": 0, "infopath": 0}
    custom_items: list[dict] = []

    for form in forms:
        kind = _classify(form)
        counts[kind] += 1
        if kind != "outOfBox":
            custom_items.append(
                {
                    "listName": form.get("listName", "Unknown"),
                    "formType": form.get("formType", ""),
                    "formKind": kind,
                    "strategy": strategies.get(kind, "Unknown -- manual review required"),
                }
            )

    return {
        "customItems": custom_items,
        "stats": {
            "totalForms": len(forms),
            "outOfBoxForms": counts["outOfBox"],
            "scriptForms": counts["script"],
            "infopathForms": counts["infopath"],
            "customForms": counts["script"] + counts["infopath"],
        },
    }


def generate_report(plan: dict) -> str:
    """Render the form inventory as a reviewer-facing Markdown worksheet."""
    stats = plan["stats"]
    lines = [
        "# Custom List Forms Inventory",
        "",
        f"**Total forms:** {stats['totalForms']} | "
        f"**Out-of-box:** {stats['outOfBoxForms']} | "
        f"**Custom:** {stats['customForms']} "
        f"(script: {stats['scriptForms']}, InfoPath/layout-only: {stats['infopathForms']})",
        "",
        "---",
        "",
        "## Custom Forms Requiring Modernization",
        "",
        "| List | Form Type | Kind | Strategy |",
        "|:---|:---|:---|:---|",
    ]
    for item in plan["customItems"]:
        lines.append(
            f"| `{item['listName']}` | {item['formType'] or '--'} | {item['formKind']} | {item['strategy']} |"
        )
    if not plan["customItems"]:
        lines.append("| -- | -- | -- | No custom forms detected |")

    lines += ["", "---", "", "*Full structured data: `forms-plan.json` in the same folder.*"]
    return "\n".join(lines)


def run(*, forms_path: str | Path, rules_path: str | Path, output_dir: str | Path) -> DiscoveryOutcome:
    """
    Analyse a form inventory export and write `forms-plan.{json,md}`.

    Returns an honest `DiscoveryOutcome`: no artifacts are written when the
    forms export or rules file is unavailable, unparseable, or not the expected shape.
    """
    loaded = load_json_input(forms_path, domain=DOMAIN)
    if loaded.status in (DiscoveryStatus.FAILED, DiscoveryStatus.FORBIDDEN, DiscoveryStatus.UNAVAILABLE):
        return loaded
    if not isinstance(loaded.data, list):
        return DiscoveryOutcome.failed(
            DOMAIN, f"Expected a JSON array of forms in {forms_path}, got {type(loaded.data).__name__}."
        )

    rules_loaded = load_json_input(rules_path, domain=DOMAIN)
    if not rules_loaded.ok:
        return DiscoveryOutcome.unavailable(DOMAIN, f"Form classification rules unavailable: {rules_loaded.detail}")
    rules = rules_loaded.data

    out_dir = require_output_dir(output_dir)
    plan = analyse(loaded.data, rules)

    json_path = out_dir / "forms-plan.json"
    json_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")
    md_path = out_dir / "forms-plan.md"
    md_path.write_text(generate_report(plan), encoding="utf-8")

    artifacts = (str(json_path), str(md_path))
    detail = f"{plan['stats']['totalForms']} form(s) analysed, {plan['stats']['customForms']} custom."
    if loaded.status is DiscoveryStatus.EMPTY:
        return DiscoveryOutcome.empty(DOMAIN, "No forms in the inventory export.", plan, artifacts)
    return DiscoveryOutcome.observed(DOMAIN, detail, plan, artifacts)
