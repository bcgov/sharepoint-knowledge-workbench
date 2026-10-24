"""
page_inventory_analysis.py

Purpose:
    Analyses a classic-SharePoint page/web-part inventory export and produces a
    modernization planning package: per-page classification against an editable rules
    file, a complexity score and label, a disposition worksheet, a page dependency
    matrix, and summary statistics.

    Read-only: reads JSON export files from the local filesystem and writes report
    artifacts to a caller-specified output directory. No SharePoint tenant I/O.

Layer: plugins/sharepoint-site-assessment -- analysis

Key Input Dependencies:
    - A page inventory JSON array. Each entry:
        FileName, Category, ListTitle, ConnectedWPCount, HasCEWP, HasSEWP,
        WebParts: [{ Category, TypeName, Title, ListName }]
    - A web part migration rules JSON file (see assets/webpart-migration-rules.json).

Provenance:
    Extracted from the originating SharePoint migration repository's classic-page
    content analysis script at the pinned source commit. See
    docs/reports/phase-9-reusable-sharepoint-plugin-extraction/provenance.md.

Function index:
    - load_rules
    - classify_wp_category
    - compute_complexity
    - disposition_hint
    - analyse
    - generate_report
    - _complexity_distribution_rows
    - _approach_distribution_rows
    - _web_part_classification_rows
    - _disposition_worksheet_rows
    - _dependency_matrix_rows
    - _custom_exception_rows
    - _connected_page_rows
    - run
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


# Return the configured reviewer hint for a page category, or the neutral fallback.
def disposition_hint(page: dict, rules: dict) -> str:
    """Return the configured reviewer hint for a page category, or the neutral fallback."""
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
    lines.extend(_complexity_distribution_rows(stats))
    lines.extend(_approach_distribution_rows(stats))
    lines.extend(_web_part_classification_rows(plan["webPartSummary"]))
    lines.extend(_disposition_worksheet_rows(plan["pages"]))
    lines.extend(_dependency_matrix_rows(plan["dependencyMatrix"]))
    lines.extend(_custom_exception_rows(plan["pages"]))
    lines.extend(_connected_page_rows(plan["pages"]))
    lines.extend(["", "---", "", "*Full structured data: `page-inventory-plan.json` in the same folder.*"])
    return "\n".join(lines)


def _complexity_distribution_rows(stats: dict) -> list[str]:
    """Render the four complexity totals in the established display order."""
    return [f"| {label} | {stats['byComplexity'][label]} |" for label in ("Critical", "High", "Medium", "Low")]


def _approach_distribution_rows(stats: dict) -> list[str]:
    """Render the approach totals and the heading for web-part classification."""
    return [
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


def _web_part_classification_rows(web_part_summary: list[dict]) -> list[str]:
    """Render non-empty web-part categories and start the disposition worksheet."""
    lines = []
    for wp in web_part_summary:
        if wp["totalInstances"] > 0:
            lines.append(
                f"| {wp['category']} | {wp['totalInstances']} | `{wp['approach']}` | {wp['modernEquivalent']} |"
            )
    return lines + [
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


def _disposition_worksheet_rows(pages: list[dict]) -> list[str]:
    """Render sorted page rows for reviewers to assign a disposition."""
    rows = []
    for page in sorted(pages, key=lambda item: (item["category"], item["fileName"])):
        exception = "Yes" if page["hasCustomException"] else "No"
        connected = f"Yes ({page['connectedWebPartCount']})" if page["hasConnectedWebParts"] else "No"
        hint = page["dispositionHint"].replace("|", "∣")
        rows.append(
            f"| {page['fileName']} | {page['category']} | {page['listTitle'] or '--'} "
            f"| {page['complexityLabel']} ({page['complexityScore']}) | {page['webPartCount']} "
            f"| {exception} | {connected} | {hint} |  |"
        )
    return rows + [
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


def _dependency_matrix_rows(pages: list[dict]) -> list[str]:
    """Render page complexity and web-part category rows in matrix order."""
    rows = []
    for page in pages:
        categories = ", ".join(page["webPartCategories"]) if page["webPartCategories"] else "--"
        rows.append(
            f"| {page['fileName']} | {page['complexityLabel']} | {page['complexityScore']} | {categories} "
            f"| {'Yes' if page['hasConnectedWebParts'] else 'No'} "
            f"| {'Yes' if page['hasCEWP'] else 'No'} "
            f"| {'Yes' if page['hasSEWP'] else 'No'} |"
        )
    return rows + [
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


def _custom_exception_rows(pages: list[dict]) -> list[str]:
    """Render each custom-exception web part, or the established empty-state row."""
    exception_rows = [
        f"| {page['fileName']} | {wp['category']} | {wp['typeName'] or '--'} | {wp['modernEquivalent']} |"
        for page in pages
        for wp in page["webParts"]
        if wp["approach"] == "custom-exception"
    ]
    return (exception_rows or ["| -- | -- | -- | No custom exceptions detected |"]) + [
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


def _connected_page_rows(pages: list[dict]) -> list[str]:
    """Render connected-web-part pages, retaining the established empty state."""
    connected_rows = [
        f"| {page['fileName']} | {page['connectedWebPartCount']} |"
        for page in pages
        if page["hasConnectedWebParts"]
    ]
    return connected_rows or ["| -- | No connected web part pages detected |"]


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
