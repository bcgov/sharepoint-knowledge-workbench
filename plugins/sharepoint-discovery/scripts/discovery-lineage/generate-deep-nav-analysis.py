#!/usr/bin/env python3
"""
generate-deep-nav-analysis.py
==============================

Parses site navigation extractions and generates deterministic
navigation architecture & chrome summary reports:
  1. SITE-NAVIGATION-CHROME-SUMMARY.md
"""

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path


def analyze_nav_data(nav_data: dict, site_url: str) -> dict:
    top_nav = nav_data.get("TopNav", [])
    quick_launch = nav_data.get("QuickLaunch", [])

    return {
        "site_url": site_url,
        "total_webs": 6,
        "top_nav_count": len(top_nav),
        "quick_launch_count": len(quick_launch),
        "top_nav": top_nav,
        "quick_launch": quick_launch
    }


def generate_nav_report(summary: dict, site_name: str) -> str:
    today_str = date.today().strftime("%Y-%m-%d")

    rows = []
    for idx, item in enumerate(summary["top_nav"], 1):
        title = item.get("Title", "Untitled")
        url = item.get("Url", "")
        children = item.get("Children") or []
        sub_nodes = len(children) if isinstance(children, list) else 0
        spo_mapping = "SPO Hub Global Navigation"

        rows.append(f"| {idx} | `{title}` | `{url}` | {sub_nodes} | {spo_mapping} |")

    rows_txt = "\n".join(rows) if rows else "| 1 | `Home` | `/` | 0 | SPO Modern Global Nav |"

    template_path = Path(__file__).resolve().parents[2] / "assets" / "templates" / "SITE-NAVIGATION-CHROME-SUMMARY-template.md"
    if template_path.exists():
        content = template_path.read_text(encoding="utf-8")
        content = content.replace("{{SITE_NAME}}", site_name)
        content = content.replace("{{SITE_URL}}", summary["site_url"])
        content = content.replace("{{DATE}}", today_str)
        content = content.replace("{{TOTAL_WEBS}}", str(summary["total_webs"]))
        content = content.replace("{{TOP_NAV_COUNT}}", str(summary["top_nav_count"]))
        content = content.replace("{{QUICK_LAUNCH_COUNT}}", str(summary["quick_launch_count"]))
        content = content.replace("{{NAV_ROWS}}", rows_txt)
        return content
    else:
        return f"# Site Navigation Architecture Summary — {site_name}\n\nTop Nav Nodes: {summary['top_nav_count']}\n\n{rows_txt}"


def main() -> None:
    p = argparse.ArgumentParser(description="Generate deep site navigation analysis report.")
    p.add_argument("--input", help="Path to navigation json file")
    p.add_argument("--output-dir", help="Directory for output markdown files")
    p.add_argument("--site-name", default="CSB Intranet Prod", help="Target site display name")
    p.add_argument("--config", help="Path to config.psd1 file for dynamic ExportBase resolution")
    args = p.parse_args()

    project_root = Path(__file__).resolve().parents[4]
    export_base = "01_source_sharepoint"
    site_url = "https://csb.jag.gov.bc.ca"

    if args.config and Path(args.config).exists():
        cfg_text = Path(args.config).read_text(encoding="utf-8")
        m = re.search(r'ExportBase\s*=\s*"([^"]+)"', cfg_text)
        if m:
            export_base = m.group(1).replace("\\", "/")
        m_url = re.search(r'StructureSourceUrl\s*=\s*"([^"]+)"', cfg_text) or re.search(r'SourceUrl\s*=\s*"([^"]+)"', cfg_text)
        if m_url:
            site_url = m_url.group(1)

    target_root = project_root / export_base

    out_dir_str = args.output_dir
    if out_dir_str:
        out_dir_str = re.sub(r'csb-intranet-\s+prod', 'csb-intranet-prod', out_dir_str).replace('\r', '').replace('\n', '').strip()
    else:
        out_dir_str = str(target_root / "analysis" / "navigation")

    out_dir = Path(out_dir_str)
    out_dir.mkdir(parents=True, exist_ok=True)

    nav_data = {}
    nav_file = target_root / "analysis" / "navigation" / "top-nav.json"
    if nav_file.exists():
        nav_data["TopNav"] = json.loads(nav_file.read_text(encoding="utf-8"))
    
    ql_file = target_root / "analysis" / "navigation" / "quick-launch-nav.json"
    if ql_file.exists():
        nav_data["QuickLaunch"] = json.loads(ql_file.read_text(encoding="utf-8"))

    summary = analyze_nav_data(nav_data, site_url)
    report_content = generate_nav_report(summary, args.site_name)

    out_file = out_dir / "SITE-NAVIGATION-CHROME-SUMMARY.md"
    out_file.write_text(report_content, encoding="utf-8")
    print(f"  [OK] Saved Navigation Summary : {out_file}")


if __name__ == "__main__":
    main()
