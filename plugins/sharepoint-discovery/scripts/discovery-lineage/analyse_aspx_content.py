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
"""

import argparse
import json
import re
from collections import defaultdict
from datetime import date
from pathlib import Path


# ── Rule helpers ───────────────────────────────────────────────────────────────

def load_rules(rules_path: Path) -> dict:
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


def disposition_hint(page: dict, rules: dict) -> str:
    hints = rules.get("dispositionHints", {})
    return hints.get(page.get("Category", ""), "Review — apply Keep/Merge/Archive/Delete manually")


# ── Core analysis ──────────────────────────────────────────────────────────────

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
    pages_out = []
    wp_category_counts: dict[str, int] = defaultdict(int)

    for page in inventory:
        wps = page.get("WebParts", [])
        score, complexity_label = compute_complexity(page, rules)

        # Classify each web part on this page
        classified_wps = []
        for wp in wps:
            cat = wp.get("Category", "Other")
            rule = classify_wp_category(cat, rules)
            wp_category_counts[cat] += 1
            classified_wps.append({
                "category": cat,
                "typeName": wp.get("TypeName", ""),
                "title": wp.get("Title", ""),
                "listName": wp.get("ListName", ""),
                "approach": rule["approach"],
                "modernEquivalent": rule["modernEquivalent"],
            })

        # Unique web part categories on this page
        unique_cats = sorted(set(wp["category"] for wp in classified_wps))
        has_custom_exception = any(wp["approach"] == "custom-exception" for wp in classified_wps)

        pages_out.append({
            "fileName": page.get("FileName", ""),
            "category": page.get("Category", ""),
            "listTitle": page.get("ListTitle", ""),
            "webPartCount": len(wps),
            "webPartCategories": unique_cats,
            "hasConnectedWebParts": page.get("ConnectedWPCount", 0) > 0,
            "connectedWebPartCount": page.get("ConnectedWPCount", 0),
            "hasCEWP": page.get("HasCEWP", False),
            "hasSEWP": page.get("HasSEWP", False),
            "complexityScore": score,
            "complexityLabel": complexity_label,
            "hasCustomException": has_custom_exception,
            "dispositionHint": disposition_hint(page, rules),
            "disposition": "",  # filled in by human reviewer
            "webParts": classified_wps,
        })

    # Web part summary across all pages
    wp_summary = []
    for rule in rules["webPartRules"]:
        cat = rule["category"]
        count = wp_category_counts.get(cat, 0)
        if count > 0 or cat != "Other":
            wp_summary.append({
                "category": cat,
                "totalInstances": count,
                "approach": rule["approach"],
                "modernEquivalent": rule["modernEquivalent"],
                "notes": rule["notes"],
            })

    # Dependency matrix: one row per page, sorted by complexity desc
    matrix = sorted(pages_out, key=lambda p: p["complexityScore"], reverse=True)

    stats = {
        "totalPages": len(pages_out),
        "totalWebParts": sum(p["webPartCount"] for p in pages_out),
        "byComplexity": {
            "Critical": sum(1 for p in pages_out if p["complexityLabel"] == "Critical"),
            "High": sum(1 for p in pages_out if p["complexityLabel"] == "High"),
            "Medium": sum(1 for p in pages_out if p["complexityLabel"] == "Medium"),
            "Low": sum(1 for p in pages_out if p["complexityLabel"] == "Low"),
        },
        "byApproach": {
            "directly-convertible": sum(
                1 for p in pages_out
                if all(wp["approach"] == "directly-convertible" for wp in p["webParts"])
                and p["webParts"]
            ),
            "replace-ootb": sum(
                1 for p in pages_out
                if p["webParts"] and not p["hasCustomException"]
                and any(wp["approach"] == "replace-ootb" for wp in p["webParts"])
            ),
            "custom-exception": sum(1 for p in pages_out if p["hasCustomException"]),
            "no-web-parts": sum(1 for p in pages_out if not p["webParts"]),
        },
        "connectedWebPartPages": sum(1 for p in pages_out if p["hasConnectedWebParts"]),
        "sewpPages": sum(1 for p in pages_out if p["hasSEWP"]),
    }

    return {
        "generated": str(date.today()),
        "pages": pages_out,
        "webPartSummary": wp_summary,
        "dependencyMatrix": matrix,
        "stats": stats,
    }


# ── Report generation ──────────────────────────────────────────────────────────

def generate_report(plan: dict) -> str:
    stats = plan["stats"]
    pages = plan["pages"]
    wp_summary = plan["webPartSummary"]
    matrix = plan["dependencyMatrix"]

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
    for label in ("Critical", "High", "Medium", "Low"):
        lines.append(f"| {label} | {stats['byComplexity'][label]} |")

    lines += [
        "",
        "### Migration approach distribution",
        "",
        "| Approach | Pages |",
        "|:---|---:|",
        f"| Directly convertible (all WPs) | {stats['byApproach']['directly-convertible']} |",
        f"| Replace OOTB (at least one) | {stats['byApproach']['replace-ootb']} |",
        f"| Custom exception required | {stats['byApproach']['custom-exception']} |",
        f"| No web parts detected | {stats['byApproach']['no-web-parts']} |",
        "",
        f"**Pages with connected web parts:** {stats['connectedWebPartPages']} (no OOTB SPO equivalent — design detail-page separately)  ",
        f"**Pages with Script Editor WPs:** {stats['sewpPages']} (SEWP blocked in modern SPO — requires SPFx justification)",
        "",
        "---",
        "",
        "## 2. Web Part Classification",
        "",
        "| Category | Total Instances | Migration Approach | Modern Equivalent |",
        "|:---|---:|:---|:---|",
    ]
    for wp in wp_summary:
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
        "> **Instructions:** Review the `Disposition Hint` column. Set `Disposition` for each page to one of:",
        "> `Keep` | `Merge` | `Archive` | `Delete`",
        "> Pages marked Keep or Merge proceed to `sp-converting-aspx-pages` pipeline.",
        "",
        "| Page | Category | List | Complexity | WP Count | Custom Exception? | Connected WPs? | Disposition Hint | **Disposition** |",
        "|:---|:---|:---|:---|---:|:---|:---|:---|:---|",
    ]
    for p in sorted(pages, key=lambda x: (x["category"], x["fileName"])):
        exc = "Yes" if p["hasCustomException"] else "No"
        conn = f"Yes ({p['connectedWebPartCount']})" if p["hasConnectedWebParts"] else "No"
        hint = p["dispositionHint"].replace("|", "∣")
        lines.append(
            f"| {p['fileName']} | {p['category']} | {p['listTitle'] or '—'} "
            f"| {p['complexityLabel']} ({p['complexityScore']}) | {p['webPartCount']} "
            f"| {exc} | {conn} | {hint} |  |"
        )

    lines += [
        "",
        "---",
        "",
        "## 4. Page Dependency Matrix",
        "",
        "> Pages sorted by complexity score descending. Use this to identify high-risk combinations",
        "> and select representative test pages (aim to cover each unique WP combination at least once).",
        "",
        "| Page | Complexity | Score | Web Part Categories | Connected? | CEWP? | SEWP? |",
        "|:---|:---|---:|:---|:---|:---|:---|",
    ]
    for p in matrix:
        cats = ", ".join(p["webPartCategories"]) if p["webPartCategories"] else "—"
        conn = "Yes" if p["hasConnectedWebParts"] else "No"
        cewp = "Yes" if p["hasCEWP"] else "No"
        sewp = "Yes" if p["hasSEWP"] else "No"
        lines.append(
            f"| {p['fileName']} | {p['complexityLabel']} | {p['complexityScore']} "
            f"| {cats} | {conn} | {cewp} | {sewp} |"
        )

    lines += [
        "",
        "---",
        "",
        "## 5. Custom Exception Pages",
        "",
        "> These pages contain web parts requiring SPFx or Power Apps solutions.",
        "> Each must be explicitly justified (business function, cost, support plan, named approver) before proceeding.",
        "",
        "| Page | Web Part | Type | Notes |",
        "|:---|:---|:---|:---|",
    ]
    custom_found = False
    for p in pages:
        for wp in p["webParts"]:
            if wp["approach"] == "custom-exception":
                rule = next(
                    (r for r in [] if r.get("category") == wp["category"]), {}
                )
                lines.append(
                    f"| {p['fileName']} | {wp['category']} | {wp['typeName'] or '—'} "
                    f"| {wp.get('modernEquivalent', '—')} |"
                )
                custom_found = True
    if not custom_found:
        lines.append("| — | — | — | No custom exceptions detected |")

    lines += [
        "",
        "---",
        "",
        "## 6. Connected Web Part Pages",
        "",
        "> These pages use the SP2016 web part connection mechanism (parent list filters child web parts on row select).",
        "> There is no OOTB equivalent in modern SPO. Each must be redesigned as a detail-page or navigation pattern.",
        "",
        "| Page | Connection Count |",
        "|:---|---:|",
    ]
    conn_found = False
    for p in pages:
        if p["hasConnectedWebParts"]:
            lines.append(f"| {p['fileName']} | {p['connectedWebPartCount']} |")
            conn_found = True
    if not conn_found:
        lines.append("| — | No connected web part pages detected |")

    lines += [
        "",
        "---",
        "",
        "*Full data: `aspx-content-plan.json` in the same folder.*",
        "*Next step: set Disposition for all rows in Section 3, then feed Keep/Merge pages into `sp-converting-aspx-pages` pipeline.*",
    ]

    return "\n".join(lines)


# ── Entry point ────────────────────────────────────────────────────────────────

def main() -> None:
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
        rules_input = str(Path(__file__).resolve().parents[2] / "assets" / "templates" / "webpart-migration-rules.json")

    inventory_str = args.inventory
    if inventory_str:
        inventory_str = re.sub(r'csb-intranet-\s+prod', 'csb-intranet-prod', inventory_str).replace('\r', '').replace('\n', '').strip()
    else:
        inventory_str = str(target_root / "analysis" / "aspx-webpart-inventory.json")

    out_dir_str = args.output_dir
    if out_dir_str:
        out_dir_str = re.sub(r'csb-intranet-\s+prod', 'csb-intranet-prod', out_dir_str).replace('\r', '').replace('\n', '').strip()
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
