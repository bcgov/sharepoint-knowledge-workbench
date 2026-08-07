"""
permissions_analysis.py

Purpose:
    Analyses an exported permissions/security snapshot and produces a group
    provisioning worksheet plus a "broken inheritance" exception report -- the
    lists/libraries whose permissions were changed from their parent's default.

    Read-only: reads a JSON export file from the local filesystem and writes report
    artifacts to a caller-specified output directory. No SharePoint tenant I/O.

Layer: plugins/sharepoint-discovery -- analysis

Key Input Dependencies:
    Accepts either of two export shapes:
      1. A flat JSON array of permission entries, one row per (principal, object)
         pair: webUrl, principalTitle, permissionLevels, objectTitle|listName.
      2. A structured JSON object:
         { siteUrl, groups: [{name, permission}],
           objects: [{title, hasUniqueRoleAssignments, roleAssignments: [{group, role}]}] }

Provenance:
    Extracted from the originating SharePoint migration repository's security and
    permissions analysis script at the pinned source commit. See
    docs/reports/phase-9-reusable-sharepoint-plugin-extraction/provenance.md.
"""

from __future__ import annotations

import json
from pathlib import Path

from discovery_inputs import DiscoveryOutcome, DiscoveryStatus, load_json_input, require_output_dir

DOMAIN = "permissions"


def _analyse_flat(entries: list[dict]) -> tuple[str, list[dict], list[dict]]:
    site_url = ""
    groups_by_name: dict[str, dict] = {}
    objects_by_title: dict[str, dict] = {}

    for entry in entries:
        if not isinstance(entry, dict):
            continue
        site_url = entry.get("webUrl", site_url)
        principal = entry.get("principalTitle", "")
        permission = entry.get("permissionLevels", "")
        obj_title = entry.get("objectTitle") or entry.get("listName") or "Site"

        if principal and principal not in groups_by_name:
            groups_by_name[principal] = {"name": principal, "permission": permission}

        obj = objects_by_title.setdefault(
            obj_title,
            {"title": obj_title, "hasUniqueRoleAssignments": permission != "Inherited", "roleAssignments": []},
        )
        if principal:
            obj["roleAssignments"].append({"group": principal, "role": permission})

    return site_url, list(groups_by_name.values()), list(objects_by_title.values())


def analyse(data) -> dict:
    """Produce structured group/object permission data from either accepted export shape."""
    if isinstance(data, list):
        site_url, groups, objects = _analyse_flat(data)
        unique_objects = objects
    else:
        site_url = data.get("siteUrl", "")
        groups = data.get("groups") or []
        objects = data.get("objects") or []
        unique_objects = [o for o in objects if o.get("hasUniqueRoleAssignments") is True]

    return {
        "siteUrl": site_url,
        "groups": groups,
        "objects": objects,
        "uniqueObjects": unique_objects,
        "stats": {
            "groupsCount": len(groups),
            "totalObjects": len(objects),
            "uniqueObjectsCount": len(unique_objects),
        },
    }


def generate_report(plan: dict) -> str:
    """Render the group provisioning worksheet and broken-inheritance exception report."""
    stats = plan["stats"]
    lines = [
        "# Permissions Analysis",
        "",
        f"**Source:** `{plan['siteUrl'] or '--'}`  ",
        f"**Groups:** {stats['groupsCount']} | **Objects evaluated:** {stats['totalObjects']} | "
        f"**Objects with broken inheritance:** {stats['uniqueObjectsCount']}",
        "",
        "---",
        "",
        "## Group Provisioning Worksheet",
        "",
        "| Group | Permission Level |",
        "|:---|:---|",
    ]
    for g in plan["groups"]:
        lines.append(f"| `{g.get('name', 'Unknown')}` | {g.get('permission', '') or '--'} |")
    if not plan["groups"]:
        lines.append("| -- | No groups detected |")

    lines += [
        "",
        "---",
        "",
        "## Broken Inheritance Exception Report",
        "",
        "> Objects whose permissions were changed from their parent's default -- each must be",
        "> explicitly re-provisioned rather than inherited during migration.",
        "",
        "| Object | Groups Assigned | Permission Levels |",
        "|:---|:---|:---|",
    ]
    for obj in plan["uniqueObjects"]:
        roles = obj.get("roleAssignments") or []
        assigned = ", ".join(sorted({r.get("group", "") for r in roles if r.get("group")}))
        levels = ", ".join(sorted({r.get("role", "") for r in roles if r.get("role")}))
        lines.append(f"| {obj.get('title', 'Untitled')} | {assigned or '--'} | {levels or '--'} |")
    if not plan["uniqueObjects"]:
        lines.append("| -- | -- | No broken-inheritance objects detected |")

    lines += ["", "---", "", "*Full structured data: `permissions-plan.json` in the same folder.*"]
    return "\n".join(lines)


def run(*, permissions_path: str | Path, output_dir: str | Path) -> DiscoveryOutcome:
    """
    Analyse a permissions export and write `permissions-plan.{json,md}`.

    Returns an honest `DiscoveryOutcome`: no artifacts are written when the
    permissions export is unavailable, unparseable, or not the expected shape.
    """
    loaded = load_json_input(permissions_path, domain=DOMAIN)
    if loaded.status in (DiscoveryStatus.FAILED, DiscoveryStatus.FORBIDDEN, DiscoveryStatus.UNAVAILABLE):
        return loaded
    if not isinstance(loaded.data, (list, dict)):
        return DiscoveryOutcome.failed(
            DOMAIN,
            f"Expected a JSON array or object in {permissions_path}, got {type(loaded.data).__name__}.",
        )

    out_dir = require_output_dir(output_dir)
    plan = analyse(loaded.data)

    json_path = out_dir / "permissions-plan.json"
    json_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")
    md_path = out_dir / "permissions-plan.md"
    md_path.write_text(generate_report(plan), encoding="utf-8")

    artifacts = (str(json_path), str(md_path))
    detail = (
        f"{plan['stats']['totalObjects']} object(s), {plan['stats']['groupsCount']} group(s) analysed."
    )
    if plan["stats"]["totalObjects"] == 0 and plan["stats"]["groupsCount"] == 0:
        return DiscoveryOutcome.empty(DOMAIN, "No groups or objects in the permissions export.", plan, artifacts)
    return DiscoveryOutcome.observed(DOMAIN, detail, plan, artifacts)
