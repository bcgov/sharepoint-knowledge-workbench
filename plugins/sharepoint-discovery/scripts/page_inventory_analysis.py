"""
page_inventory_analysis.py

Purpose:
    Analyses a classic-SharePoint page/web-part inventory export and produces a
    modernization planning package: per-page classification against an editable rules
    file, a complexity score and label, a disposition worksheet, a page dependency
    matrix, and summary statistics.

    Read-only: reads JSON export files from the local filesystem and writes report
    artifacts to a caller-specified output directory. No SharePoint tenant I/O.

Layer: plugins/sharepoint-discovery -- analysis

Key Input Dependencies:
    - A page inventory JSON array. Each entry:
        FileName, Category, ListTitle, ConnectedWPCount, HasCEWP, HasSEWP,
        WebParts: [{ Category, TypeName, Title, ListName }]
    - A web part migration rules JSON file (see assets/webpart-migration-rules.json).

Provenance:
    Extracted from CMAT `plugins/sharepoint-migration/scripts/page-migration/
    analyse_aspx_content.py` @ 78d6bb91a6c3c01208208a8c2a06f241fef9ce9f. See
    docs/reports/phase-9-reusable-sharepoint-plugin-extraction/provenance.md.
"""

from __future__ import annotations

import json
from collections import defaultdict
from datetime import date
from pathlib import Path

from discovery_inputs import DiscoveryOutcome, DiscoveryStatus, load_json_input, require_output_dir

DOMAIN = "pages"

#: Neutral, project-free default rules shipped with this plugin.
DEFAULT_RULES_PATH = Path(__file__).resolve().parent / "assets" / "webpart-migration-rules.json"

_FALLBACK_RULE = {
    "category": "Other",
    "approach": "custom-exception",
    "modernEquivalent": "Unknown -- manual review required",
    "notes": "",
}


def load_rules(rules_path: str | Path) -> dict:
    """Load a migration rules file. Raises FileNotFoundError if absent."""
    return json.loads(Path(rules_path).read_text(encoding="utf-8"))


def classify_wp_category(category: str, rules: dict) -> dict:
    """Return the rule entry matching `category`, falling back to the 'Other' rule."""
    for rule in rules["webPartRules"]:
        if rule["category"] == category:
            return rule
    for rule in rules["webPartRules"]:
        if rule["category"] == "Other":
            return rule
    return dict(_FALLBACK_RULE)


def compute_complexity(page: dict, rules: dict) -> tuple[float, str]:
    """Return (raw_score, label) for a page, driven entirely by the rules file."""
    weights = rules["complexityWeights"]
    thresholds = rules["complexityThresholds"]

    web_parts = page.get("WebParts") or []
    score = len(web_parts) * weights.get("webPartCount", 0.5)

    if page.get("HasCEWP"):
        score += weights.get("hasCEWP", 1)
    if page.get("HasSEWP"):
        score += weights.get("hasSEWP", 3)
    if page.get("ConnectedWPCount", 0) > 0:
        score += weights.get("hasConnectedWebParts", 3)
    if any(wp.get("Category") == "Sandbox" for wp in web_parts):
        score += weights.get("hasSandbox", 3)

    custom_exceptions = sum(
        1
        for wp in web_parts
        if classify_wp_category(wp.get("Category", "Other"), rules)["approach"] == "custom-exception"
    )
    score += custom_exceptions * weights.get("customExceptionCount", 2)

    if score <= thresholds["low"]:
        label = "Low"
    elif score <= thresholds["medium"]:
        label = "Medium"
    elif score <= thresholds["high"]:
        label = "High"
    else:
        label = "Critical"

    return round(score, 1), label


def disposition_hint(page: dict, rules: dict) -> str:
    hints = rules.get("dispositionHints", {})
    return hints.get(
        page.get("Category", ""), "Review -- apply Keep/Merge/Archive/Delete manually"
    )


def analyse(inventory: list[dict], rules: dict) -> dict:
    """Produce structured planning data from a page/web-part inventory."""
    pages_out: list[dict] = []
    category_counts: dict[str, int] = defaultdict(int)

    for page in inventory:
        web_parts = page.get("WebParts") or []
        score, complexity_label = compute_complexity(page, rules)

        classified = []
        for wp in web_parts:
            category = wp.get("Category", "Other")
            rule = classify_wp_category(category, rules)
            category_counts[category] += 1
            classified.append(
                {
                    "category": category,
                    "typeName": wp.get("TypeName", ""),
                    "title": wp.get("Title", ""),
                    "listName": wp.get("ListName", ""),
                    "approach": rule["approach"],
                    "modernEquivalent": rule["modernEquivalent"],
                }
            )

        pages_out.append(
            {
                "fileName": page.get("FileName", ""),
                "category": page.get("Category", ""),
                "listTitle": page.get("ListTitle", ""),
                "webPartCount": len(web_parts),
                "webPartCategories": sorted({wp["category"] for wp in classified}),
                "hasConnectedWebParts": page.get("ConnectedWPCount", 0) > 0,
                "connectedWebPartCount": page.get("ConnectedWPCount", 0),
                "hasCEWP": bool(page.get("HasCEWP", False)),
                "hasSEWP": bool(page.get("HasSEWP", False)),
                "complexityScore": score,
                "complexityLabel": complexity_label,
                "hasCustomException": any(wp["approach"] == "custom-exception" for wp in classified),
                "dispositionHint": disposition_hint(page, rules),
                "disposition": "",  # filled in by a human reviewer
                "webParts": classified,
            }
        )

    web_part_summary = [
        {
            "category": rule["category"],
            "totalInstances": category_counts.get(rule["category"], 0),
            "approach": rule["approach"],
            "modernEquivalent": rule["modernEquivalent"],
            "notes": rule.get("notes", ""),
        }
        for rule in rules["webPartRules"]
    ]

    stats = {
        "totalPages": len(pages_out),
        "totalWebParts": sum(p["webPartCount"] for p in pages_out),
        "byComplexity": {
            label: sum(1 for p in pages_out if p["complexityLabel"] == label)
            for label in ("Critical", "High", "Medium", "Low")
        },
        "byApproach": {
            "directly-convertible": sum(
                1
                for p in pages_out
                if p["webParts"] and all(wp["approach"] == "directly-convertible" for wp in p["webParts"])
            ),
            "replace-ootb": sum(
                1
                for p in pages_out
                if p["webParts"]
                and not p["hasCustomException"]
                and any(wp["approach"] == "replace-ootb" for wp in p["webParts"])
            ),
            "custom-exception": sum(1 for p in pages_out if p["hasCustomException"]),
            "no-web-parts": sum(1 for p in pages_out if not p["webParts"]),
        },
        "connectedWebPartPages": sum(1 for p in pages_out if p["hasConnectedWebParts"]),
        "scriptEditorPages": sum(1 for p in pages_out if p["hasSEWP"]),
    }

    return {
        "generated": str(date.today()),
        "pages": pages_out,
        "webPartSummary": web_part_summary,
        "dependencyMatrix": sorted(pages_out, key=lambda p: p["complexityScore"], reverse=True),
        "stats": stats,
    }


def generate_report(plan: dict) -> str:
    """Render the planning package as a reviewer-facing Markdown worksheet."""
    stats = plan["stats"]
    lines = [
        "# Classic Page Inventory -- Analysis & Modernization Plan",
        "",
        f"> **Generated:** {plan['generated']}  ",
        f"> **Total pages:** {stats['totalPages']} | **Total web parts:** {stats['totalWebParts']}",
        "",
        "---",
        "",
        "## 1. Summary Statistics",
        "",
        "### Complexity distribution",
        "",
        "| Complexity | Pages |",
        "|:---|---:|",
    ]
    for label in ("Critical", "High", "Medium", "Low"):
        lines.append(f"| {label} | {stats['byComplexity'][label]} |")

    lines += [
        "",
        "### Migration approach distribution",
        "",
        "| Approach | Pages |",
        "|:---|---:|",
        f"| Directly convertible (all web parts) | {stats['byApproach']['directly-convertible']} |",
        f"| Replace out-of-the-box (at least one) | {stats['byApproach']['replace-ootb']} |",
        f"| Custom exception required | {stats['byApproach']['custom-exception']} |",
        f"| No web parts detected | {stats['byApproach']['no-web-parts']} |",
        "",
        f"**Pages with connected web parts:** {stats['connectedWebPartPages']} "
        "(no out-of-the-box modern equivalent -- design a detail page separately)  ",
        f"**Pages with Script Editor web parts:** {stats['scriptEditorPages']} "
        "(blocked in modern SharePoint -- requires an approved SPFx justification)",
        "",
        "---",
        "",
        "## 2. Web Part Classification",
        "",
        "| Category | Total Instances | Migration Approach | Modern Equivalent |",
        "|:---|---:|:---|:---|",
    ]
    for wp in plan["webPartSummary"]:
        if wp["totalInstances"] > 0:
            lines.append(
                f"| {wp['category']} | {wp['totalInstances']} | `{wp['approach']}` | {wp['modernEquivalent']} |"
            )

    lines += [
        "",
        "---",
        "",
        "## 3. Disposition Worksheet",
        "",
        "> **Instructions:** review the `Disposition Hint` column and set `Disposition` for each",
        "> page to one of `Keep` | `Merge` | `Archive` | `Delete`.",
        "",
        "| Page | Category | List | Complexity | WP Count | Custom Exception? | Connected WPs? "
        "| Disposition Hint | **Disposition** |",
        "|:---|:---|:---|:---|---:|:---|:---|:---|:---|",
    ]
    for p in sorted(plan["pages"], key=lambda x: (x["category"], x["fileName"])):
        exception = "Yes" if p["hasCustomException"] else "No"
        connected = f"Yes ({p['connectedWebPartCount']})" if p["hasConnectedWebParts"] else "No"
        hint = p["dispositionHint"].replace("|", "∣")
        lines.append(
            f"| {p['fileName']} | {p['category']} | {p['listTitle'] or '--'} "
            f"| {p['complexityLabel']} ({p['complexityScore']}) | {p['webPartCount']} "
            f"| {exception} | {connected} | {hint} |  |"
        )

    lines += [
        "",
        "---",
        "",
        "## 4. Page Dependency Matrix",
        "",
        "> Sorted by complexity score, descending. Use this to pick representative test pages",
        "> covering each unique web part combination at least once.",
        "",
        "| Page | Complexity | Score | Web Part Categories | Connected? | CEWP? | SEWP? |",
        "|:---|:---|---:|:---|:---|:---|:---|",
    ]
    for p in plan["dependencyMatrix"]:
        categories = ", ".join(p["webPartCategories"]) if p["webPartCategories"] else "--"
        lines.append(
            f"| {p['fileName']} | {p['complexityLabel']} | {p['complexityScore']} | {categories} "
            f"| {'Yes' if p['hasConnectedWebParts'] else 'No'} "
            f"| {'Yes' if p['hasCEWP'] else 'No'} "
            f"| {'Yes' if p['hasSEWP'] else 'No'} |"
        )

    lines += [
        "",
        "---",
        "",
        "## 5. Custom Exception Pages",
        "",
        "> These pages contain web parts requiring a custom (SPFx or low-code) solution.",
        "> Each must be explicitly justified before proceeding.",
        "",
        "| Page | Web Part | Type | Modern Equivalent |",
        "|:---|:---|:---|:---|",
    ]
    exception_rows = [
        f"| {p['fileName']} | {wp['category']} | {wp['typeName'] or '--'} | {wp['modernEquivalent']} |"
        for p in plan["pages"]
        for wp in p["webParts"]
        if wp["approach"] == "custom-exception"
    ]
    lines += exception_rows or ["| -- | -- | -- | No custom exceptions detected |"]

    lines += [
        "",
        "---",
        "",
        "## 6. Connected Web Part Pages",
        "",
        "> These pages use the classic web part connection mechanism. There is no out-of-the-box",
        "> modern equivalent -- each must be redesigned as a detail page or navigation pattern.",
        "",
        "| Page | Connection Count |",
        "|:---|---:|",
    ]
    connected_rows = [
        f"| {p['fileName']} | {p['connectedWebPartCount']} |"
        for p in plan["pages"]
        if p["hasConnectedWebParts"]
    ]
    lines += connected_rows or ["| -- | No connected web part pages detected |"]

    lines += ["", "---", "", "*Full structured data: `page-inventory-plan.json` in the same folder.*"]
    return "\n".join(lines)


def run(
    *,
    inventory_path: str | Path,
    rules_path: str | Path,
    output_dir: str | Path,
) -> DiscoveryOutcome:
    """
    Analyse a page inventory export and write `page-inventory-plan.{json,md}`.

    Returns an honest `DiscoveryOutcome`: no artifacts are written when the inventory
    or rules file is unavailable or unparseable.
    """
    loaded = load_json_input(inventory_path, domain=DOMAIN)
    if not loaded.ok:
        return loaded
    if not isinstance(loaded.data, list):
        return DiscoveryOutcome.failed(
            DOMAIN, f"Expected a JSON array of pages in {inventory_path}, got {type(loaded.data).__name__}."
        )

    rules_loaded = load_json_input(rules_path, domain=DOMAIN)
    if not rules_loaded.ok:
        return DiscoveryOutcome.unavailable(
            DOMAIN, f"Migration rules unavailable: {rules_loaded.detail}"
        )
    rules = rules_loaded.data

    out_dir = require_output_dir(output_dir)
    plan = analyse(loaded.data, rules)

    json_path = out_dir / "page-inventory-plan.json"
    json_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")
    md_path = out_dir / "page-inventory-plan.md"
    md_path.write_text(generate_report(plan), encoding="utf-8")

    artifacts = (str(json_path), str(md_path))
    detail = (
        f"{plan['stats']['totalPages']} page(s), {plan['stats']['totalWebParts']} web part(s) analysed."
    )
    if loaded.status is DiscoveryStatus.EMPTY:
        return DiscoveryOutcome.empty(DOMAIN, "No pages in the inventory export.", plan, artifacts)
    return DiscoveryOutcome.observed(DOMAIN, detail, plan, artifacts)
