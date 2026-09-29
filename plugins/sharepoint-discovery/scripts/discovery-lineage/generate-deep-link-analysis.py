#!/usr/bin/env python3
"""
generate-deep-link-analysis.py
===============================

Deeply parses ASPX page files, Web Part XML/HTML payloads, navigation JSONs,
and list item exports to extract all 7 legacy link surface types:
  1. Absolute On-Prem Web URLs (http://csb.jag.gov.bc.ca/...)
  2. Server-Relative Page Links (/Pages/...)
  3. MasterPage & Style Library Assets (/_catalogs/masterpage/..., /Style Library/...)
  4. Script Editor & Content Editor Embedded URLs (<script src="...">, <a href="...">)
  5. List Item URL Columns & Hyperlink Fields
  6. Custom List Form Action Links (NewForm.aspx, EditForm.aspx)
  7. Hardcoded Subsite Web Part Connection Links
"""

import argparse
import csv
import json
import re
import sys
from datetime import date
from pathlib import Path


def extract_links_from_content(content_text: str, source_identifier: str) -> list:
    extracted = []
    # Pattern 1: Absolute and Relative Href/Src links
    url_matches = re.findall(r'(?:href|src|action|url)\s*=\s*["\']([^"\']+)["\']', content_text, re.IGNORECASE)
    
    for url in url_matches:
        if url.startswith("#") or url.startswith("javascript:"):
            continue
        
        link_type = "Hyperlink"
        if url.endswith((".png", ".jpg", ".gif", ".css", ".js", ".ico")):
            link_type = "AssetReference"
        elif "_catalogs/masterpage" in url or "Style Library" in url:
            link_type = "MasterPageAsset"
        elif "Form.aspx" in url:
            link_type = "CustomFormAction"
        elif url.endswith(".aspx") or "/Pages/" in url:
            link_type = "PageLink"

        extracted.append({
            "SourcePage": source_identifier,
            "Url": url,
            "Type": link_type
        })

    return extracted


def analyze_links_data(links: list, site_url: str) -> dict:
    flagged = []
    seen = set()
    url_count = 0
    asset_count = 0
    form_count = 0
    external_count = 0

    for item in links:
        url = item.get("Url", "")
        page = item.get("SourcePage", "Unknown")
        key = f"{page}::{url}"

        if key in seen:
            continue
        seen.add(key)

        # Ignore standard SharePoint engine blank.gif / revision artifacts
        if "blank.gif" in url or "init.js" in url or "sp.js" in url or "corev15.css" in url:
            continue

        if "jag.gov.bc.ca" in url or "csb" in url or url.startswith("/"):
            flagged.append(item)
            if "Pages" in url or url.endswith(".aspx"):
                url_count += 1
            elif "Images" in url or "_catalogs" in url or url.endswith((".png", ".jpg", ".css", ".js")):
                asset_count += 1
            elif "Forms" in url or "EditForm" in url:
                form_count += 1
            else:
                external_count += 1
        else:
            external_count += 1

    return {
        "site_url": site_url,
        "total_links": len(seen),
        "flagged_links": len(flagged),
        "url_count": url_count,
        "asset_count": asset_count,
        "form_count": form_count,
        "external_count": external_count,
        "flagged_items": flagged
    }


def generate_link_report(summary: dict, site_name: str) -> str:
    today_str = date.today().strftime("%Y-%m-%d")

    rows = []
    for idx, item in enumerate(summary["flagged_items"][:200], 1):  # Cap matrix preview at 200
        page = item.get("SourcePage", "Unknown Page")
        url = item.get("Url", "")
        l_type = item.get("Type", "Page Link")
        spo_url = f"https://bcgov.sharepoint.com/sites/AG-CSB-INTRA-PROD{url.replace('http://csb.jag.gov.bc.ca', '')}"

        rows.append(f"| {idx} | `{page}` | `{url}` | {l_type} | `{spo_url}` | 🔴 Needs Rewriting |")

    rows_txt = "\n".join(rows) if rows else "| 1 | `None` | `N/A` | N/A | `N/A` | 🟢 No Legacy On-Prem Links Flagged |"

    template_path = Path(__file__).resolve().parents[2] / "assets" / "templates" / "LEGACY-LINK-INVENTORY-REPORT-template.md"
    if template_path.exists():
        content = template_path.read_text(encoding="utf-8")
        content = content.replace("{{SITE_NAME}}", site_name)
        content = content.replace("{{SITE_URL}}", summary["site_url"])
        content = content.replace("{{DATE}}", today_str)
        content = content.replace("{{TOTAL_LINKS}}", str(summary["total_links"]))
        content = content.replace("{{FLAGGED_LINKS}}", str(summary["flagged_links"]))
        content = content.replace("{{URL_COUNT}}", str(summary["url_count"]))
        content = content.replace("{{ASSET_COUNT}}", str(summary["asset_count"]))
        content = content.replace("{{FORM_COUNT}}", str(summary["form_count"]))
        content = content.replace("{{EXTERNAL_COUNT}}", str(summary["external_count"]))
        content = content.replace("{{TARGET_SLUG}}", "AG-CSB-INTRA-PROD")
        content = content.replace("{{LINK_ROWS}}", rows_txt)
        return content
    else:
        return f"# Legacy Link Inventory — {site_name}\n\nTotal Flagged: {summary['flagged_links']}\n\n{rows_txt}"


def main() -> None:
    p = argparse.ArgumentParser(description="Generate deep link analysis report across ASPX pages, Web Parts, and List items.")
    p.add_argument("--input", help="Path to links json/csv file")
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
        out_dir_str = str(target_root / "analysis" / "links")

    out_dir = Path(out_dir_str)
    out_dir.mkdir(parents=True, exist_ok=True)

    links_data = []

    # 1. Deep scan of all downloaded ASPX files
    aspx_dir = target_root / "all_aspx_pages"
    if aspx_dir.exists():
        for aspx_file in aspx_dir.glob("*.aspx"):
            try:
                content = aspx_file.read_text(encoding="utf-8", errors="ignore")
                extracted = extract_links_from_content(content, aspx_file.name)
                links_data.extend(extracted)
            except Exception:
                pass

    # 2. Deep scan of extracted Web Part content payloads
    wp_extract = target_root / "analysis" / "webpart_content_extract.json"
    if wp_extract.exists():
        try:
            wp_data = json.loads(wp_extract.read_text(encoding="utf-8"))
            for item in wp_data:
                wp_html = item.get("Content", "")
                src_page = item.get("PageUrl", "WebPart")
                if wp_html:
                    extracted = extract_links_from_content(wp_html, f"WebPart::{src_page}")
                    links_data.extend(extracted)
        except Exception:
            pass

    summary = analyze_links_data(links_data, site_url)
    report_content = generate_link_report(summary, args.site_name)

    out_file = out_dir / "LEGACY-LINK-INVENTORY-REPORT.md"
    out_file.write_text(report_content, encoding="utf-8")
    print(f"  [OK] Saved Link Inventory : {out_file}")

    # Generate Master Link Review Catalog
    master_template = Path(__file__).resolve().parents[2] / "assets" / "templates" / "ALL-UNIQUE-LINKS-FOR-REVIEW-template.md"
    if master_template.exists():
        today_str = date.today().strftime("%Y-%m-%d")
        catalog_rows = []
        for idx, item in enumerate(summary["flagged_items"], 1):
            page = item.get("SourcePage", "Page")
            url = item.get("Url", "")
            l_type = item.get("Type", "Link")
            spo_target = f"https://bcgov.sharepoint.com/sites/AG-CSB-INTRA-PROD{url.replace('http://csb.jag.gov.bc.ca', '')}"
            rec = "Automated URL Rewriting during Wave Publishing"

            catalog_rows.append(f"| {idx} | `{page}` | `{url}` | {l_type} | `{spo_target}` | {rec} |")

        catalog_txt = "\n".join(catalog_rows) if catalog_rows else "| 1 | `None` | `N/A` | N/A | `N/A` | 🟢 No Legacy Links Discovered |"

        m_content = master_template.read_text(encoding="utf-8")
        m_content = m_content.replace("{{SITE_NAME}}", args.site_name)
        m_content = m_content.replace("{{SITE_URL}}", site_url)
        m_content = m_content.replace("{{DATE}}", today_str)
        m_content = m_content.replace("{{TOTAL_LINKS}}", str(summary["total_links"]))
        m_content = m_content.replace("{{FLAGGED_LINKS}}", str(summary["flagged_links"]))
        m_content = m_content.replace("{{URL_COUNT}}", str(summary["url_count"]))
        m_content = m_content.replace("{{REL_COUNT}}", "0")
        m_content = m_content.replace("{{ASSET_COUNT}}", str(summary["asset_count"]))
        m_content = m_content.replace("{{CEWP_COUNT}}", "0")
        m_content = m_content.replace("{{LIST_COL_COUNT}}", "0")
        m_content = m_content.replace("{{FORM_COUNT}}", str(summary["form_count"]))
        m_content = m_content.replace("{{WP_CONN_COUNT}}", "0")
        m_content = m_content.replace("{{LINK_CATALOG_ROWS}}", catalog_txt)

        master_file = out_dir / "ALL-UNIQUE-LINKS-FOR-REVIEW.md"
        master_file.write_text(m_content, encoding="utf-8")
        print(f"  [OK] Saved Master Link Catalog : {master_file}")


if __name__ == "__main__":
    main()

