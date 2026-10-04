"""
navigation_analysis.py

Purpose:
    Analyses an exported site navigation tree (top navigation bar and quick launch)
    and produces a flattened, depth-annotated navigation architecture summary.

    Read-only: reads a JSON export file from the local filesystem and writes report
    artifacts to a caller-specified output directory. No SharePoint tenant I/O.

Layer: plugins/sharepoint-site-assessment -- analysis

Key Input Dependencies:
    - A navigation export JSON object:
        { "topNav": [ {title, url, children: [...]} , ... ],
          "quickLaunch": [ {title, url, children: [...]} , ... ] }
      `children` is optional and recurses to arbitrary depth.

Provenance:
    Extracted from the originating SharePoint migration repository's navigation
    architecture analysis script at the pinned source commit. See
    docs/reports/phase-9-reusable-sharepoint-plugin-extraction/provenance.md.
"""

from __future__ import annotations

import json
from pathlib import Path

from discovery_inputs import DiscoveryOutcome, DiscoveryStatus, load_json_input, require_output_dir

DOMAIN = "navigation"


def _flatten(nodes: list[dict], depth: int = 0) -> list[dict]:
    """Recursively flatten a navigation tree into a depth-annotated list."""
    flat: list[dict] = []
    for node in nodes:
        children = node.get("children") or []
        flat.append(
            {
                "title": node.get("title", "Untitled"),
                "url": node.get("url", ""),
                "depth": depth,
                "childCount": len(children),
            }
        )
        flat.extend(_flatten(children, depth + 1))
    return flat


def _max_depth(nodes: list[dict], depth: int = 0) -> int:
    if not nodes:
        return depth - 1 if depth > 0 else 0
    deepest = depth
    for node in nodes:
        children = node.get("children") or []
        if children:
            deepest = max(deepest, _max_depth(children, depth + 1))
    return deepest


def analyse(nav_data: dict) -> dict:
    """Produce structured navigation architecture data from a navigation export."""
    top_nav = nav_data.get("topNav") or []
    quick_launch = nav_data.get("quickLaunch") or []

    flat_top_nav = _flatten(top_nav)
    flat_quick_launch = _flatten(quick_launch)

    return {
        "topNav": flat_top_nav,
        "quickLaunch": flat_quick_launch,
        "stats": {
            "topNavCount": len(top_nav),
            "quickLaunchCount": len(quick_launch),
            "topNavTotalNodes": len(flat_top_nav),
            "quickLaunchTotalNodes": len(flat_quick_launch),
            "topNavMaxDepth": _max_depth(top_nav),
            "quickLaunchMaxDepth": _max_depth(quick_launch),
        },
    }


def generate_report(plan: dict) -> str:
    """Render the navigation architecture summary as Markdown."""
    stats = plan["stats"]
    lines = [
        "# Site Navigation Architecture Summary",
        "",
        f"**Top navigation nodes:** {stats['topNavCount']} top-level "
        f"({stats['topNavTotalNodes']} total, max depth {stats['topNavMaxDepth']})  ",
        f"**Quick launch nodes:** {stats['quickLaunchCount']} top-level "
        f"({stats['quickLaunchTotalNodes']} total, max depth {stats['quickLaunchMaxDepth']})",
        "",
        "---",
        "",
        "## Top Navigation",
        "",
        "| Depth | Title | Url | Children |",
        "|---:|:---|:---|---:|",
    ]
    for node in plan["topNav"]:
        lines.append(f"| {node['depth']} | `{node['title']}` | `{node['url']}` | {node['childCount']} |")
    if not plan["topNav"]:
        lines.append("| -- | -- | -- | No top navigation nodes detected |")

    lines += [
        "",
        "## Quick Launch",
        "",
        "| Depth | Title | Url | Children |",
        "|---:|:---|:---|---:|",
    ]
    for node in plan["quickLaunch"]:
        lines.append(f"| {node['depth']} | `{node['title']}` | `{node['url']}` | {node['childCount']} |")
    if not plan["quickLaunch"]:
        lines.append("| -- | -- | -- | No quick launch nodes detected |")

    lines += ["", "---", "", "*Full structured data: `navigation-plan.json` in the same folder.*"]
    return "\n".join(lines)


def run(*, navigation_path: str | Path, output_dir: str | Path) -> DiscoveryOutcome:
    """
    Analyse a navigation export and write `navigation-plan.{json,md}`.

    Returns an honest `DiscoveryOutcome`: no artifacts are written when the
    navigation export is unavailable, unparseable, or not a JSON object.
    """
    loaded = load_json_input(navigation_path, domain=DOMAIN)
    if loaded.status is DiscoveryStatus.FAILED or loaded.status is DiscoveryStatus.FORBIDDEN:
        return loaded
    if loaded.status is DiscoveryStatus.UNAVAILABLE:
        return loaded
    if not isinstance(loaded.data, dict):
        return DiscoveryOutcome.failed(
            DOMAIN,
            f"Expected a JSON object with 'topNav'/'quickLaunch' in {navigation_path}, "
            f"got {type(loaded.data).__name__}.",
        )

    nav_data = loaded.data
    out_dir = require_output_dir(output_dir)
    plan = analyse(nav_data)

    json_path = out_dir / "navigation-plan.json"
    json_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")
    md_path = out_dir / "navigation-plan.md"
    md_path.write_text(generate_report(plan), encoding="utf-8")

    artifacts = (str(json_path), str(md_path))
    stats = plan["stats"]
    detail = (
        f"{stats['topNavTotalNodes']} top-nav node(s), "
        f"{stats['quickLaunchTotalNodes']} quick-launch node(s) analysed."
    )
    if stats["topNavTotalNodes"] == 0 and stats["quickLaunchTotalNodes"] == 0:
        return DiscoveryOutcome.empty(DOMAIN, "No navigation nodes in the export.", plan, artifacts)
    return DiscoveryOutcome.observed(DOMAIN, detail, plan, artifacts)
