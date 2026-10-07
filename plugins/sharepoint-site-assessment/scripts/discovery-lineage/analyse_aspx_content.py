#!/usr/bin/env python3
"""
analyse_aspx_content.py
=======================

Stage 3 of the ASPX content analysis pipeline.

Reads:
  - aspx-webpart-inventory.json  (from analyze-aspx-webparts.ps1)
  - webpart-migration-rules.json (editable classification rules)

Produces:
  - aspx-content-plan.json  — structured planning data
  - aspx-content-plan.md    — human-readable disposition worksheet,
                               web part classification table,
                               page dependency matrix, complexity scores

Usage:
    python analyse_aspx_content.py \\
        --inventory  01_source_sharepoint/analysis/aspx-webpart-inventory.json \\
        --rules      assets/templates/webpart-migration-rules.json \\
        --output-dir 01_source_sharepoint/analysis/

Purpose:
    Analyse an ASPX web-part inventory and create a reviewer-ready modernization plan.

Key Input Dependencies:
    - A caller-supplied ASPX web-part inventory JSON, migration-rules JSON, optional config.psd1, and output directory.

Function index:
    - find_asset
    - load_rules
    - classify_wp_category
    - compute_complexity
    - disposition_hint
    - _analyse_page
    - _summarize_web_parts
    - _summarize_pages
    - analyse
    - _complexity_rows
    - _classification_rows
    - _disposition_rows
    - _dependency_rows
    - _custom_exception_rows
    - _connected_rows
    - generate_report
    - main
"""

import argparse
import json
import re
from collections import defaultdict
from datetime import date
from pathlib import Path


# ── Rule helpers ───────────────────────────────────────────────────────────────

def find_asset(name: str) -> Path:
    """Locate a bundled template/rules file under assets/ (plugin source tree: <plugin>/assets; installed skill: <skill>/assets),
    trying assets/templates/<name>, assets/<name> and assets/<lowercase name>."""
    here = Path(__file__).resolve()
    for base in (here.parents[2] / "assets", here.parents[1] / "assets"):
        for candidate in (base / "templates" / name, base / name, base / name.lower()):
            if candidate.exists():
                return candidate
    return here.parents[2] / "assets" / "templates" / name


# Load the caller-selected web-part migration rules from JSON.
def load_rules(rules_path: Path) -> dict:
    """Load the caller-selected web-part migration rules from JSON."""
    return json.loads(rules_path.read_text(encoding="utf-8"))


def classify_wp_category(category: str, rules: dict) -> dict:
    """Return the rule entry whose category matches, falling back to 'Other'."""
    for rule in rules["webPartRules"]:
        if rule["category"] == category:
            return rule
    for rule in rules["webPartRules"]:
        if rule["category"] == "Other":
            return rule
    return {"approach": "custom-exception", "modernEquivalent": "Unknown", "notes": ""}


def compute_complexity(page: dict, rules: dict) -> tuple[float, str]:
    """Return (raw_score, label) for a page."""
    w = rules["complexityWeights"]
    t = rules["complexityThresholds"]

    score = 0.0
    wps = page.get("WebParts", [])

    score += len(wps) * w.get("webPartCount", 0.5)

    if page.get("HasCEWP"):
        score += w.get("hasCEWP", 1)
    if page.get("HasSEWP"):
        score += w.get("hasSEWP", 3)
    if page.get("ConnectedWPCount", 0) > 0:
        score += w.get("hasConnectedWebParts", 3)

    sandbox_count = sum(1 for wp in wps if wp.get("Category") == "Sandbox")
    if sandbox_count:
        score += w.get("hasSandbox", 3)

    custom_exception_count = sum(
        1 for wp in wps
        if classify_wp_category(wp.get("Category", "Other"), rules)["approach"] == "custom-exception"
    )
    score += custom_exception_count * w.get("customExceptionCount", 2)

    if score <= t["low"]:
        label = "Low"
    elif score <= t["medium"]:
        label = "Medium"
    elif score <= t["high"]:
        label = "High"
    else:
        label = "Critical"

    return round(score, 1), label


# Return the configured reviewer hint for a page category, or the neutral fallback.
def disposition_hint(page: dict, rules: dict) -> str:
    """Return the configured reviewer hint for a page category, or the neutral fallback."""
    hints = rules.get("dispositionHints", {})
    return hints.get(page.get("Category", ""), "Review — apply Keep/Merge/Archive/Delete manually")


# ── Core analysis ──────────────────────────────────────────────────────────────


# Classify the web parts on one page and derive its page-level fields.
def _analyse_page(
    page: dict, rules: dict, category_counts: dict[str, int]
) -> dict:
    """Build the analyzed page record and update observed category totals."""
    web_parts = page.get("WebParts", [])
    score, complexity_label = compute_complexity(page, rules)
    classified_wps = []
    for web_part in web_parts:
        category = web_part.get("Category", "Other")
        rule = classify_wp_category(category, rules)
        category_counts[category] += 1
        classified_wps.append({
            "category": category,
            "typeName": web_part.get("TypeName", ""),
            "title": web_part.get("Title", ""),
            "listName": web_part.get("ListName", ""),
            "approach": rule["approach"],
            "modernEquivalent": rule["modernEquivalent"],
        })
    return {
        "fileName": page.get("FileName", ""),
        "category": page.get("Category", ""),
        "listTitle": page.get("ListTitle", ""),
        "webPartCount": len(web_parts),
        "webPartCategories": sorted({wp["category"] for wp in classified_wps}),
        "hasConnectedWebParts": page.get("ConnectedWPCount", 0) > 0,
        "connectedWebPartCount": page.get("ConnectedWPCount", 0),
        "hasCEWP": page.get("HasCEWP", False),
        "hasSEWP": page.get("HasSEWP", False),
        "complexityScore": score,
        "complexityLabel": complexity_label,
        "hasCustomException": any(
            wp["approach"] == "custom-exception" for wp in classified_wps
        ),
        "dispositionHint": disposition_hint(page, rules),
        "disposition": "",
        "webParts": classified_wps,
    }


# Build category totals in the same order as the configured rule entries.
def _summarize_web_parts(category_counts: dict[str, int], rules: dict) -> list[dict]:
    """Create one summary row for each configured category retained by the report."""
    summary = []
    for rule in rules["webPartRules"]:
        category = rule["category"]
        count = category_counts.get(category, 0)
        if count > 0 or category != "Other":
            summary.append({
                "category": category,
                "totalInstances": count,
                "approach": rule["approach"],
                "modernEquivalent": rule["modernEquivalent"],
                "notes": rule["notes"],
            })
    return summary


# Count analyzed pages in the public report's complexity and approach groupings.
def _summarize_pages(pages: list[dict]) -> dict:
    """Calculate totals and grouped counts without changing page analysis records."""
    return {
        "totalPages": len(pages),
        "totalWebParts": sum(page["webPartCount"] for page in pages),
        "byComplexity": {
            label: sum(1 for page in pages if page["complexityLabel"] == label)
            for label in ("Critical", "High", "Medium", "Low")
        },
        "byApproach": {
            "directly-convertible": sum(
                1 for page in pages
                if all(wp["approach"] == "directly-convertible" for wp in page["webParts"])
                and page["webParts"]
            ),
            "replace-ootb": sum(
                1 for page in pages
                if page["webParts"] and not page["hasCustomException"]
                and any(wp["approach"] == "replace-ootb" for wp in page["webParts"])
            ),
            "custom-exception": sum(1 for page in pages if page["hasCustomException"]),
            "no-web-parts": sum(1 for page in pages if not page["webParts"]),
        },
        "connectedWebPartPages": sum(1 for page in pages if page["hasConnectedWebParts"]),
        "sewpPages": sum(1 for page in pages if page["hasSEWP"]),
    }


def analyse(inventory: list[dict], rules: dict) -> dict:
    """
    Produce structured planning data from the web part inventory.

    Returns:
        {
          "pages": [...],            # one entry per page with classification
          "webPartSummary": [...],   # unique WP categories with migration approach
          "dependencyMatrix": [...], # page × layout × WPs × complexity
          "stats": {...}
        }
    """
    category_counts: dict[str, int] = defaultdict(int)
    pages_out = [_analyse_page(page, rules, category_counts) for page in inventory]
    wp_summary = _summarize_web_parts(category_counts, rules)
    matrix = sorted(pages_out, key=lambda page: page["complexityScore"], reverse=True)
    stats = _summarize_pages(pages_out)

    return {
        "generated": str(date.today()),
        "pages": pages_out,
        "webPartSummary": wp_summary,
        "dependencyMatrix": matrix,
        "stats": stats,
    }


# ── Report generation ──────────────────────────────────────────────────────────

# Generate report.
# Render each report section in its established order.
def generate_report(plan: dict) -> str:
    """Render the analysis plan as a reviewer-facing disposition worksheet."""
    stats = plan["stats"]
    lines = [
        "# ASPX Content Analysis & Migration Plan",
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
    lines.extend(_complexity_rows(stats))
    lines.extend(_classification_rows(plan["webPartSummary"]))
    lines.extend(_disposition_rows(plan["pages"]))
    lines.extend(_dependency_rows(plan["dependencyMatrix"]))
    lines.extend(_custom_exception_rows(plan["pages"]))
    lines.extend(_connected_rows(plan["pages"]))
    lines.extend([
        "", "---", "",
        "*Full data: `aspx-content-plan.json` in the same folder.*",
        "*Next step: set Disposition for all rows in Section 3, then feed Keep/Merge pages into `sp-converting-aspx-pages` pipeline.*",
    ])
    return "\n".join(lines)


# Render page-complexity totals and the migration-approach summary.
def _complexity_rows(stats: dict) -> list[str]:
    """Render complexity counts, approach counts, and the classification heading."""
    rows = [f"| {label} | {stats['byComplexity'][label]} |" for label in ("Critical", "High", "Medium", "Low")]
    return rows + [
        "", "### Migration approach distribution", "", "| Approach | Pages |", "|:---|---:|",
        f"| Directly convertible (all WPs) | {stats['byApproach']['directly-convertible']} |",
        f"| Replace OOTB (at least one) | {stats['byApproach']['replace-ootb']} |",
        f"| Custom exception required | {stats['byApproach']['custom-exception']} |",
        f"| No web parts detected | {stats['byApproach']['no-web-parts']} |", "",
        f"**Pages with connected web parts:** {stats['connectedWebPartPages']} (no OOTB SPO equivalent — design detail-page separately)  ",
        f"**Pages with Script Editor WPs:** {stats['sewpPages']} (SEWP blocked in modern SPO — requires SPFx justification)",
        "", "---", "", "## 2. Web Part Classification", "",
        "| Category | Total Instances | Migration Approach | Modern Equivalent |", "|:---|---:|:---|:---|",
    ]


# Render observed web-part categories and start the reviewer worksheet.
def _classification_rows(summary: list[dict]) -> list[str]:
    """Render non-empty category rows followed by the disposition table header."""
    rows = [
        f"| {wp['category']} | {wp['totalInstances']} | `{wp['approach']}` | {wp['modernEquivalent']} |"
        for wp in summary if wp["totalInstances"] > 0
    ]
    return rows + [
        "", "---", "", "## 3. Disposition Worksheet", "",
        "> **Instructions:** Review the `Disposition Hint` column. Set `Disposition` for each page to one of:",
        "> `Keep` | `Merge` | `Archive` | `Delete`",
        "> Pages marked Keep or Merge proceed to `sp-converting-aspx-pages` pipeline.", "",
        "| Page | Category | List | Complexity | WP Count | Custom Exception? | Connected WPs? | Disposition Hint | **Disposition** |",
        "|:---|:---|:---|:---|---:|:---|:---|:---|:---|",
    ]


# Render disposition rows in the original category-and-name order.
def _disposition_rows(pages: list[dict]) -> list[str]:
    """Render sorted page rows and the dependency-matrix heading."""
    rows = []
    for page in sorted(pages, key=lambda item: (item["category"], item["fileName"])):
        exception = "Yes" if page["hasCustomException"] else "No"
        connected = f"Yes ({page['connectedWebPartCount']})" if page["hasConnectedWebParts"] else "No"
        hint = page["dispositionHint"].replace("|", "∣")
        rows.append(
            f"| {page['fileName']} | {page['category']} | {page['listTitle'] or '—'} "
            f"| {page['complexityLabel']} ({page['complexityScore']}) | {page['webPartCount']} "
            f"| {exception} | {connected} | {hint} |  |"
        )
    return rows + [
        "", "---", "", "## 4. Page Dependency Matrix", "",
        "> Pages sorted by complexity score descending. Use this to identify high-risk combinations",
        "> and select representative test pages (aim to cover each unique WP combination at least once).", "",
        "| Page | Complexity | Score | Web Part Categories | Connected? | CEWP? | SEWP? |",
        "|:---|:---|---:|:---|:---|:---|:---|",
    ]


# Render pages in the precomputed complexity order.
def _dependency_rows(matrix: list[dict]) -> list[str]:
    """Render dependency-matrix rows and the custom-exception heading."""
    rows = []
    for page in matrix:
        categories = ", ".join(page["webPartCategories"]) if page["webPartCategories"] else "—"
        connected = "Yes" if page["hasConnectedWebParts"] else "No"
        cewp = "Yes" if page["hasCEWP"] else "No"
        sewp = "Yes" if page["hasSEWP"] else "No"
        rows.append(
            f"| {page['fileName']} | {page['complexityLabel']} | {page['complexityScore']} "
            f"| {categories} | {connected} | {cewp} | {sewp} |"
        )
    return rows + [
        "", "---", "", "## 5. Custom Exception Pages", "",
        "> These pages contain web parts requiring SPFx or Power Apps solutions.",
        "> Each must be explicitly justified (business function, cost, support plan, named approver) before proceeding.", "",
        "| Page | Web Part | Type | Notes |", "|:---|:---|:---|:---|",
    ]


# Render custom-exception web parts and the connected-page table header.
def _custom_exception_rows(pages: list[dict]) -> list[str]:
    """Render custom web-part rows or the established no-exceptions message."""
    rows = [
        f"| {page['fileName']} | {wp['category']} | {wp['typeName'] or '—'} | {wp.get('modernEquivalent', '—')} |"
        for page in pages for wp in page["webParts"] if wp["approach"] == "custom-exception"
    ]
    return (rows or ["| — | — | — | No custom exceptions detected |"]) + [
        "", "---", "", "## 6. Connected Web Part Pages", "",
        "> These pages use the SP2016 web part connection mechanism (parent list filters child web parts on row select).",
        "> There is no OOTB equivalent in modern SPO. Each must be redesigned as a detail-page or navigation pattern.", "",
        "| Page | Connection Count |", "|:---|---:|",
    ]


# Render connected pages or the no-connections message.
def _connected_rows(pages: list[dict]) -> list[str]:
    """Render only pages with connected web parts, preserving the empty-state wording."""
    rows = [
        f"| {page['fileName']} | {page['connectedWebPartCount']} |"
        for page in pages if page["hasConnectedWebParts"]
    ]
    return rows or ["| — | No connected web part pages detected |"]


# ── Entry point ────────────────────────────────────────────────────────────────

# Parse the command-line options, run the selected workflow, and report its outputs.
def main() -> None:
    """Parse the command-line options, run the selected workflow, and report its outputs."""
    p = argparse.ArgumentParser(
        description="Analyse ASPX web part inventory and produce a migration planning report."
    )
    p.add_argument("--inventory", help="Path to aspx-webpart-inventory.json")
    p.add_argument("--rules", help="Path to webpart-migration-rules.json (defaults to standard template)")
    p.add_argument("--output-dir", help="Directory for output files")
    p.add_argument("--config", help="Path to config.psd1 file for dynamic ExportBase resolution")
    args = p.parse_args()

    project_root = Path(__file__).resolve().parents[4]
    export_base = "01_source_sharepoint"

    if args.config and Path(args.config).exists():
        cfg_text = Path(args.config).read_text(encoding="utf-8")
        m = re.search(r'ExportBase\s*=\s*"([^"]+)"', cfg_text)
        if m:
            export_base = m.group(1).replace("\\", "/")

    target_root = project_root / export_base

    rules_input = args.rules
    if rules_input:
        rules_input = re.sub(r'sharepoint-\s+migration', 'sharepoint-migration', rules_input).replace('\r', '').replace('\n', '').strip()
    else:
        rules_input = str(find_asset("webpart-migration-rules.json"))

    inventory_str = args.inventory
    if inventory_str:
        inventory_str = inventory_str.replace('\r', '').replace('\n', '').strip()
    else:
        inventory_str = str(target_root / "analysis" / "aspx-webpart-inventory.json")

    out_dir_str = args.output_dir
    if out_dir_str:
        out_dir_str = out_dir_str.replace('\r', '').replace('\n', '').strip()
    else:
        out_dir_str = str(target_root / "analysis")

    inventory_path = Path(inventory_str)
    rules_path = Path(rules_input)
    out_dir = Path(out_dir_str)
    out_dir.mkdir(parents=True, exist_ok=True)

    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    rules = load_rules(rules_path)

    plan = analyse(inventory, rules)

    json_out = out_dir / "aspx-content-plan.json"
    json_out.write_text(json.dumps(plan, indent=2), encoding="utf-8")
    print(f"  Saved JSON : {json_out}")

    md_out = out_dir / "aspx-content-plan.md"
    md_out.write_text(generate_report(plan), encoding="utf-8")
    print(f"  Saved MD   : {md_out}")

    stats = plan["stats"]
    live_scan_file = out_dir / "legacy_webparts_scan_results.csv"
    live_count_msg = ""
    if live_scan_file.exists():
        lines = live_scan_file.read_text(encoding="utf-8").strip().splitlines()
        if len(lines) > 1:
            live_count_msg = f" (Note: Live WPM scan captured {len(lines)-1} DB-stored web parts in legacy_webparts_scan_results.csv)"

    print(f"\n  Pages analysed   : {stats['totalPages']}")
    print(f"  Inline ASPX WPs  : {stats['totalWebParts']}{live_count_msg}")
    print(f"  Critical         : {stats['byComplexity']['Critical']}")
    print(f"  High             : {stats['byComplexity']['High']}")
    print(f"  Custom exception : {stats['byApproach']['custom-exception']}")
    print(f"  Connected WP pgs : {stats['connectedWebPartPages']}")
    print()


if __name__ == "__main__":
    main()
