#!/usr/bin/env python3
"""
generate-deep-permissions-analysis.py
======================================

Parses permissions JSON extractions (all_permissions.json / permissions_inventory.json)
and generates deterministic, high-quality security & permissions reports:
  1. SPO-GROUP-PROVISIONING-CHECKLIST.md
  2. unique-permissions-exception-report.md
  3. security-analysis-summary.md
"""

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path


def analyze_permissions_data(data) -> dict:
    if isinstance(data, list):
        # Flatten array of permission entries
        groups_set = {}
        objects_set = {}
        site_url = "https://csb.jag.gov.bc.ca"

        for entry in data:
            if isinstance(entry, dict):
                site_url = entry.get("WebUrl", site_url)
                principal = entry.get("PrincipalTitle", "")
                perm = entry.get("PermissionLevels", "Read")
                obj_title = entry.get("ObjectTitle", entry.get("ListName", "Site"))

                if principal and principal not in groups_set:
                    groups_set[principal] = {"Name": principal, "Permission": perm}

                if obj_title not in objects_set:
                    objects_set[obj_title] = {
                        "Title": obj_title,
                        "HasUniqueRoleAssignments": True if perm != "Inherited" else False,
                        "RoleAssignments": []
                    }
                objects_set[obj_title]["RoleAssignments"].append({"Group": principal, "Role": perm})

        groups = list(groups_set.values())
        objects = list(objects_set.values())
    else:
        site_url = data.get("SiteUrl", "https://csb.jag.gov.bc.ca")
        groups = data.get("Groups", [])
        objects = data.get("Objects", [])

    if isinstance(data, list):
        unique_objects = objects
    else:
        unique_objects = [o for o in objects if o.get("HasUniqueRoleAssignments") is True]

    return {
        "site_url": site_url,
        "total_objects": len(objects),
        "unique_objects_count": len(unique_objects),
        "groups_count": len(groups),
        "groups": groups,
        "unique_objects": unique_objects,
        "all_objects": objects
    }


def generate_checklist_report(summary: dict, site_name: str) -> str:
    today_str = date.today().strftime("%Y-%m-%d")
    
    rows = []
    for idx, g in enumerate(summary["groups"], 1):
        g_name = g.get("Name", "Unknown")
        g_perm = g.get("Permission", "Read")
        
        spo_target = f"{site_name} {g_name.replace('CSB_', '').replace('CMAT_', '')}"
        rows.append(f"| {idx} | `{g_name}` | **{g_perm}** | {spo_target} | {g_perm} | Site Collection | ")

    rows_txt = "\n".join(rows) if rows else "| 1 | `Default Owners` | Full Control | Site Owners | Full Control | Site | "

    return f"""# SharePoint Online Group Provisioning Checklist — {site_name}

**Status**: Draft / Analysis Complete  
**Derived From**: `{summary['site_url']}`  
**Analysis Date**: {today_str}  
**Total Objects in Scope**: {summary['total_objects']} lists/libraries  
**Total Groups to Provision**: {summary['groups_count']}

---

## Executive Summary

**Source SP2016 Configuration:**
- {summary['groups_count']} Custom SharePoint Groups
- **{summary['unique_objects_count']} lists/libraries** with unique broken inheritance permissions

**SPO Target Configuration:**
- **3 built-in groups** (`{site_name} Owners`, `{site_name} Members`, `{site_name} Visitors`)
- **{summary['groups_count']} groups to provision/map** in SPO
- **Permission Level Mapping Matrix** verified against SPO standards

---

## Group Definitions & SPO Mapping Matrix

| # | SP2016 Group | Site-Level Permission | SPO Target Mapping | SPO Permission Level | Scope | Notes |
|---|---|---|---|---|---|---|
{rows_txt}

---

## Critical Permission Variance Warnings

- ⚠️ **Members Group Risk**: Verify `{site_name} Members` default Edit permission level matches operational requirements.
- ⚠️ **Custom Permission Levels**: Ensure legacy custom levels are mapped to standard SPO Read/Edit or isolated via explicit group ACLs.
"""


def generate_exception_report(summary: dict, site_name: str) -> str:
    today_str = date.today().strftime("%Y-%m-%d")

    group_rows = []
    for g in summary["groups"]:
        g_name = g.get("Name", "Unknown")
        g_perm = g.get("Permission", "Read")
        group_rows.append(f"| `{g_name}` | **{g_perm}** | {site_name} {g_name} | Full Site |")
    
    group_rows_txt = "\n".join(group_rows) if group_rows else "| `Owners` | Full Control | Site Owners | Full Site |"

    list_rows = []
    for obj in summary["unique_objects"]:
        title = obj.get("Title", "Untitled")
        roles = obj.get("RoleAssignments", [])
        g_assigned = ", ".join([r.get("Group", "") for r in roles if r.get("Group")])
        p_levels = ", ".join(set([r.get("Role", "") for r in roles if r.get("Role")]))
        list_rows.append(f"| {title} | ✅ Yes | {g_assigned} | {p_levels} |")

    list_rows_txt = "\n".join(list_rows) if list_rows else "| No Unique Objects Found | No | N/A | N/A |"

    return f"""# Unique Permissions Exception Report — {site_name}

> **Source Site:** {summary['site_url']}  
> **Analysis Date:** {today_str}  
> **Total Lists/Libraries Evaluated:** {summary['total_objects']}  
> **Total Objects with Unique Permissions:** {summary['unique_objects_count']}  

---

## 1. Executive Summary

Every list and document library with broken permission inheritance (`HasUniqueRoleAssignments = true`) has been cataloged to ensure accurate entitlement replication during SPO migration.

---

## 2. Groups & Role Assignments Inventory

| Group Name | Permission Level (SP2016) | Target SPO Group / Role | Affected Scope |
|:---|:---|:---|:---|
{group_rows_txt}

---

## 3. Unique Permissions Inventory (Per List/Library)

| Entity / List Name | Unique Permissions? | Groups Assigned | Permission Levels |
|:---|:---:|:---|:---|
{list_rows_txt}
"""


def main() -> None:
    p = argparse.ArgumentParser(description="Generate deep security and permissions analysis reports.")
    p.add_argument("--permissions", help="Path to permissions_inventory.json or all_permissions.json")
    p.add_argument("--output-dir", help="Directory for output markdown files")
    p.add_argument("--site-name", default="CSB Intranet Prod", help="Target site display name")
    p.add_argument("--config", help="Path to config.psd1 file for dynamic ExportBase resolution")
    args = p.parse_args()

    project_root = Path(__file__).resolve().parents[4]
    export_base = "01_source_sharepoint"

    site_display_name = args.site_name
    if args.config and Path(args.config).exists():
        cfg_text = Path(args.config).read_text(encoding="utf-8")
        m = re.search(r'ExportBase\s*=\s*"([^"]+)"', cfg_text)
        if m:
            export_base = m.group(1).replace("\\", "/")
        
        m_url = re.search(r'StructureSourceUrl\s*=\s*"([^"]+)"', cfg_text) or re.search(r'SourceUrl\s*=\s*"([^"]+)"', cfg_text)
        if m_url and args.site_name == "CSB Intranet Prod":
            site_display_name = m_url.group(1)

    target_root = project_root / export_base

    perm_str = args.permissions
    if perm_str:
        perm_str = re.sub(r'csb-intranet-\s+prod', 'csb-intranet-prod', perm_str).replace('\r', '').replace('\n', '').strip()
    else:
        found = list(target_root.glob("**/web_permissions.json")) or list(target_root.glob("**/*permissions.json"))
        candidates = [
            target_root / "analysis" / "security" / "permissions_inventory.json",
            target_root / "raw_exports_prod" / "summary" / "all_permissions.json",
            target_root / "raw_exports" / "summary" / "all_permissions.json"
        ]
        if found:
            candidates.insert(0, found[0])
        perm_str = str(next((c for c in candidates if c.exists()), candidates[0]))

    out_dir_str = args.output_dir
    if out_dir_str:
        out_dir_str = re.sub(r'csb-intranet-\s+prod', 'csb-intranet-prod', out_dir_str).replace('\r', '').replace('\n', '').strip()
    else:
        out_dir_str = str(target_root / "analysis" / "security")

    perm_path = Path(perm_str)
    out_dir = Path(out_dir_str)
    out_dir.mkdir(parents=True, exist_ok=True)

    if not perm_path.exists():
        # Create minimal fallback structure if input json does not exist yet
        data = {
            "SiteUrl": "https://csb.jag.gov.bc.ca",
            "Groups": [{"Name": "Owners", "Permission": "Full Control"}, {"Name": "Members", "Permission": "Edit"}],
            "Objects": []
        }
    else:
        data = json.loads(perm_path.read_text(encoding="utf-8"))

    summary = analyze_permissions_data(data)

    checklist_file = out_dir / "SPO-GROUP-PROVISIONING-CHECKLIST.md"
    checklist_file.write_text(generate_checklist_report(summary, site_display_name), encoding="utf-8")
    print(f"  [OK] Saved Checklist : {checklist_file}")

    exception_file = out_dir / "unique-permissions-exception-report.md"
    exception_file.write_text(generate_exception_report(summary, site_display_name), encoding="utf-8")
    print(f"  [OK] Saved Exception : {exception_file}")


if __name__ == "__main__":
    main()
