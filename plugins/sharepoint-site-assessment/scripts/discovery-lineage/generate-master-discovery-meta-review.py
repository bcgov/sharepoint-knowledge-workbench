#!/usr/bin/env python3
"""
generate-master-discovery-meta-review.py
=========================================

Reads all discovery outputs across the 13 discovery domains and generates
the consolidated Master Discovery Meta-Review Catalog using:
  assets/templates/MASTER-DISCOVERY-META-REVIEW-template.md
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


UNAVAILABLE = "unavailable"


def fmt(value) -> str:
    return UNAVAILABLE if value is None else str(value)


def analyze_meta_data(metrics: dict, site_url: str) -> dict:
    """Summarize observed metrics. A metric that could not be observed is None and is reported as unavailable, never estimated."""
    total_wps = metrics.get("total_wps")
    unique_groups = metrics.get("unique_wp_groups")
    flagged = metrics.get("flagged_links")

    complexity = "Unknown"
    if total_wps is not None or unique_groups is not None:
        complexity = "Low"
        if (total_wps or 0) > 100 or (unique_groups or 0) > 50:
            complexity = "Medium"
        if (total_wps or 0) > 500 or (flagged or 0) > 1000:
            complexity = "High"

    summary = {"site_url": site_url, "complexity_rating": complexity}
    for key in ("total_pages", "total_wps", "unique_wp_groups", "flagged_links", "total_groups", "custom_forms",
                "total_nav_nodes", "oob_pages", "custom_pages", "spfx_candidates"):
        summary[key] = metrics.get(key)
    return summary


def generate_meta_report(summary: dict, site_name: str, problems=()) -> str:
    today_str = date.today().strftime("%Y-%m-%d")
    missing = sorted(k for k, v in summary.items() if v is None)
    quality = ["", "## Data quality", ""]
    if missing:
        quality.append("These metrics could not be observed from the available inputs and are reported as unavailable (nothing is estimated): "
                       + ", ".join(f"`{m}`" for m in missing) + ".")
    else:
        quality.append("Every metric was observed from the discovery outputs.")
    quality += [f"- Input problem: {p}" for p in problems]
    quality_txt = "\n".join(quality) + "\n"

    template_path = find_asset("MASTER-DISCOVERY-META-REVIEW-template.md")
    if template_path.exists():
        content = template_path.read_text(encoding="utf-8")
        content = content.replace("{{SITE_NAME}}", site_name)
        content = content.replace("{{SITE_URL}}", summary["site_url"])
        content = content.replace("{{DATE}}", today_str)
        for placeholder, key in (("TOTAL_PAGES", "total_pages"), ("TOTAL_WPS", "total_wps"), ("UNIQUE_WP_GROUPS", "unique_wp_groups"),
                                 ("FLAGGED_LINKS", "flagged_links"), ("TOTAL_GROUPS", "total_groups"), ("CUSTOM_FORMS", "custom_forms"),
                                 ("TOTAL_NAV_NODES", "total_nav_nodes"), ("OOB_PAGES", "oob_pages"), ("CUSTOM_PAGES", "custom_pages"),
                                 ("SPFX_CANDIDATES", "spfx_candidates")):
            content = content.replace("{{" + placeholder + "}}", fmt(summary[key]))
        content = content.replace("{{COMPLEXITY_RATING}}", summary["complexity_rating"])
        return content + quality_txt
    rows = "\n".join(f"- {k}: {fmt(v)}" for k, v in summary.items() if k != "site_url")
    return f"# Master Discovery Meta-Review — {site_name}\n\n{rows}\n" + quality_txt


def read_json(path: Path, problems: list):
    """Parsed JSON, or None when the file is absent; an unreadable/invalid file is recorded as a problem."""
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        problems.append(f"{path}: {exc}")
        return None


def collect_metrics(target_root: Path, problems: list) -> dict:
    """Derive every metric from the discovery outputs; anything that cannot be derived stays None."""
    m = {k: None for k in ("total_pages", "total_wps", "unique_wp_groups", "flagged_links", "total_groups", "custom_forms",
                           "total_nav_nodes", "oob_pages", "custom_pages", "spfx_candidates")}
    manifest_path = target_root / "all_aspx_pages" / "aspx-manifest.json"
    manifest = read_json(manifest_path, problems)
    if isinstance(manifest, (list, dict)):
        m["total_pages"] = len(manifest)
    elif not manifest_path.exists() and (target_root / "all_aspx_pages").is_dir():
        # No manifest at all: count the downloaded pages (every sub-folder), and say so. An unreadable manifest is NOT replaced by a count.
        m["total_pages"] = len(list((target_root / "all_aspx_pages").rglob("*.aspx")))
        problems.append(f"{manifest_path} is absent; total_pages was counted from the downloaded .aspx files")
    inventory = read_json(target_root / "analysis" / "aspx-webpart-inventory.json", problems)
    if isinstance(inventory, list):
        m["total_wps"] = sum(len(p.get("WebParts") or []) for p in inventory if isinstance(p, dict))
    groups = read_json(target_root / "analysis" / "webpart-code-groups.json", problems)
    if isinstance(groups, dict) and isinstance(groups.get("groups"), list):
        m["unique_wp_groups"] = len(groups["groups"])
    links = read_json(target_root / "analysis" / "links" / "link-summary.json", problems)
    if isinstance(links, dict):
        m["flagged_links"] = links.get("flagged_links")
    perms = read_json(target_root / "analysis" / "security" / "permissions_inventory.json", problems)
    if isinstance(perms, dict) and isinstance(perms.get("Groups"), list):
        m["total_groups"] = len(perms["Groups"])
    forms = read_json(target_root / "forms" / "custom-forms-manifest.json", problems)
    if isinstance(forms, list):
        m["custom_forms"] = len(forms)
    top = read_json(target_root / "analysis" / "navigation" / "top-nav.json", problems)
    quick = read_json(target_root / "analysis" / "navigation" / "quick-launch-nav.json", problems)
    if isinstance(top, list) or isinstance(quick, list):
        m["total_nav_nodes"] = len(top or []) + len(quick or [])
    return m


def main() -> None:
    p = argparse.ArgumentParser(description="Generate Master Discovery Meta-Review Report.")
    p.add_argument("--output-dir", help="Directory for output markdown files")
    p.add_argument("--site-name", default="Source Site", help="Target site display name")
    p.add_argument("--site-url", default="", help="Source site URL for the report (default: StructureSourceUrl/SourceUrl from --config)")
    p.add_argument("--metrics-file", help="JSON file whose values override or supply metrics that cannot be derived from the discovery outputs")
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
        out_dir_str = str(target_root / "analysis")

    out_dir = Path(out_dir_str)
    out_dir.mkdir(parents=True, exist_ok=True)

    problems = []
    metrics = collect_metrics(target_root, problems)
    if args.metrics_file:
        override = read_json(Path(args.metrics_file), problems)
        if isinstance(override, dict):
            metrics.update({k: v for k, v in override.items() if k in metrics})
    for problem in problems:
        print(f"  [WARN] {problem}", file=sys.stderr)
    if all(v is None for v in metrics.values()):
        print(f"  [ERROR] No discovery outputs found under {target_root}; nothing to review. "
              "Run the discovery steps first or pass --metrics-file.", file=sys.stderr)
        sys.exit(2)

    summary = analyze_meta_data(metrics, site_url)
    report_content = generate_meta_report(summary, args.site_name, problems)

    out_file = out_dir / "MASTER-DISCOVERY-META-REVIEW-CATALOG.md"
    out_file.write_text(report_content, encoding="utf-8")
    print(f"  [OK] Saved Master Meta-Review Catalog : {out_file}")


if __name__ == "__main__":
    main()
