#!/usr/bin/env python3
"""
generate-deep-forms-analysis.py
================================

Parses custom list form extractions and generates deterministic
form inventory and modernization disposition reports:
  1. CUSTOM-FORMS-INVENTORY-REPORT.md

Purpose:
    Summarize collected classic-form evidence into a deep-analysis report.

Key Input Dependencies:
    - Caller-supplied custom-form discovery JSON and the bundled report template under assets/templates/.

Function index:
    - find_asset
    - analyze_forms_data
    - generate_forms_report
    - main
"""

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path


def find_asset(name: str) -> Path:
    """Locate a bundled template/rules file under assets/ (plugin source tree: <plugin>/assets; installed skill: <skill>/assets),
    trying assets/templates/<name>, assets/<name> and assets/<lowercase name>."""
    here = Path(__file__).resolve()
    for base in (here.parents[2] / "assets", here.parents[1] / "assets"):
        for candidate in (base / "templates" / name, base / name, base / name.lower()):
            if candidate.exists():
                return candidate
    return here.parents[2] / "assets" / "templates" / name


# Count custom, scripted, InfoPath, and out-of-the-box forms in the supplied inventory.
def analyze_forms_data(forms: list, site_url: str) -> dict:
    """Summarize form types and retain custom form records for reviewer follow-up."""
    custom_forms = []
    oob_count = 0
    script_count = 0
    infopath_count = 0

    for item in forms:
        is_custom = item.get("IsCustomized", False)
        name = item.get("ListName", "Unknown")

        if is_custom:
            custom_forms.append(item)
            if item.get("HasScript", False):
                script_count += 1
            else:
                infopath_count += 1
        else:
            oob_count += 1

    return {
        "site_url": site_url,
        "total_forms": len(forms),
        "oob_forms": oob_count,
        "custom_forms": len(custom_forms),
        "script_forms": script_count,
        "infopath_forms": infopath_count,
        "custom_items": custom_forms
    }


# Fill the bundled forms template with observed counts and custom-form rows.
def generate_forms_report(summary: dict, site_name: str) -> str:
    """Render a custom-forms inventory report from the supplied summary."""
    today_str = date.today().strftime("%Y-%m-%d")

    rows = []
    for idx, item in enumerate(summary["custom_items"], 1):
        list_name = item.get("ListName", "Unknown List")
        f_type = item.get("FormType", "Custom Form")
        code = "Custom JS/WebParts" if item.get("HasScript") else "Custom Layout"
        strategy = "Custom Power Apps / React Form"

        rows.append(f"| {idx} | `{list_name}` | `{f_type}` | {code} | {strategy} |")

    rows_txt = "\n".join(rows) if rows else "| 1 | `Standard Lists` | Standard Forms | None | 🟢 Standard SPO Modern List Form |"

    template_path = find_asset("CUSTOM-FORMS-INVENTORY-REPORT-template.md")
    if template_path.exists():
        content = template_path.read_text(encoding="utf-8")
        content = content.replace("{{SITE_NAME}}", site_name)
        content = content.replace("{{SITE_URL}}", summary["site_url"])
        content = content.replace("{{DATE}}", today_str)
        content = content.replace("{{TOTAL_FORMS}}", str(summary["total_forms"]))
        content = content.replace("{{OOB_FORMS}}", str(summary["oob_forms"]))
        content = content.replace("{{CUSTOM_FORMS}}", str(summary["custom_forms"]))
        content = content.replace("{{SCRIPT_FORMS}}", str(summary["script_forms"]))
        content = content.replace("{{INFOPATH_FORMS}}", str(summary["infopath_forms"]))
        content = content.replace("{{FORM_ROWS}}", rows_txt)
        return content
    else:
        return f"# Custom List Forms Inventory — {site_name}\n\nTotal Custom: {summary['custom_forms']}\n\n{rows_txt}"


# Parse the command-line options, run the selected workflow, and report its outputs.
def main() -> None:
    """Parse the command-line options, run the selected workflow, and report its outputs."""
    p = argparse.ArgumentParser(description="Generate deep custom forms analysis report.")
    p.add_argument("--input", help="Path to forms json file")
    p.add_argument("--output-dir", help="Directory for output markdown files")
    p.add_argument("--site-name", default="Source Site", help="Target site display name")
    p.add_argument("--site-url", default="", help="Source site URL for the report (default: StructureSourceUrl/SourceUrl from --config)")
    p.add_argument("--config", help="Path to config.psd1 file for dynamic ExportBase resolution")
    args = p.parse_args()

    project_root = Path(__file__).resolve().parents[4]
    export_base = "01_source_sharepoint"
    site_url = args.site_url

    if args.config and Path(args.config).exists():
        cfg_text = Path(args.config).read_text(encoding="utf-8")
        m = re.search(r'ExportBase\s*=\s*"([^"]+)"', cfg_text)
        if m:
            export_base = m.group(1).replace("\\", "/")
        m_url = re.search(r'StructureSourceUrl\s*=\s*"([^"]+)"', cfg_text) or re.search(r'SourceUrl\s*=\s*"([^"]+)"', cfg_text)
        if m_url:
            site_url = args.site_url or m_url.group(1)

    target_root = project_root / export_base

    out_dir_str = args.output_dir
    if out_dir_str:
        out_dir_str = out_dir_str.replace('\r', '').replace('\n', '').strip()
    else:
        out_dir_str = str(target_root / "analysis" / "forms")

    out_dir = Path(out_dir_str)
    out_dir.mkdir(parents=True, exist_ok=True)

    forms_data = []
    if args.input and Path(args.input).exists():
        forms_data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    else:
        forms_manifest = target_root / "forms" / "custom-forms-manifest.json"
        if forms_manifest.exists():
            forms_data = json.loads(forms_manifest.read_text(encoding="utf-8"))

    summary = analyze_forms_data(forms_data, site_url)
    report_content = generate_forms_report(summary, args.site_name)

    out_file = out_dir / "CUSTOM-FORMS-INVENTORY-REPORT.md"
    out_file.write_text(report_content, encoding="utf-8")
    print(f"  [OK] Saved Forms Inventory : {out_file}")


if __name__ == "__main__":
    main()
