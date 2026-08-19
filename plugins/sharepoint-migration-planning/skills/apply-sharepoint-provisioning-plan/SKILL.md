---
name: apply-sharepoint-provisioning-plan
plugin: sharepoint-migration-planning
description: The real PnP.PowerShell executor for sharepoint-provisioning's plan JSON output -- create/update/delete for lists, libraries, site columns, and content types, plus content-type-to-list attach/detach. Dry-run by default; every write gated behind -Execute and an operation-specific -ConfirmToken. This is the "injected executor" sharepoint-provisioning's SKILL.md files reference but do not themselves ship.
allowed-tools: Bash, Read
examples:
  - "pwsh -File scripts/spo-provision-list.ps1 -PlanPath plan.json -SiteUrl https://contoso.sharepoint.com/sites/pilot -ClientId <id> -TenantId <tenant>"
  - "pwsh -File scripts/spo-update-site-column.ps1 -PlanPath update-plan.json -Execute -ConfirmToken UPDATE-SPO-SITE-COLUMNS -ConfigPath config.psd1"
---

# Apply SharePoint Provisioning Plan

## Trigger and Purpose

Use this skill once `sharepoint-provisioning`'s Python planning modules
(`list_provisioning.py`, `field_provisioning.py`, `content_type_provisioning.py`)
have produced an approved plan with a `confirmation_token`. Each script below
is the real tenant-facing counterpart for one plan JSON shape:

| Script | Plan input from | PnP verb |
|---|---|---|
| `spo-provision-list.ps1` | `list_provisioning.plan_provisioning` | `New-PnPList` / `Remove-PnPList` |
| `spo-provision-content-types.ps1` | `content_type_provisioning` | `Add-PnPContentType` / `Add-PnPFieldToContentType` / `Remove-PnPFieldFromContentType` / `Add-PnPContentTypeToList` |
| `spo-provision-site-columns.ps1` | `field_provisioning` | `Add-PnPField` / `Add-PnPFieldFromXml` |
| `spo-update-site-column.ps1` | *(new -- no Python planner yet emits this shape)* | `Set-PnPField` |
| `spo-remove-site-column.ps1` | *(new -- no Python planner yet emits this shape)* | `Remove-PnPField` |
| `spo-update-content-type.ps1` | *(new -- no Python planner yet emits this shape)* | `Set-PnPContentType` |
| `spo-remove-content-type.ps1` | *(new -- no Python planner yet emits this shape)* | `Remove-PnPContentType` |
| `spo-detach-content-type-from-list.ps1` | *(new -- no Python planner yet emits this shape)* | `Remove-PnPContentTypeFromList` |

The five scripts marked "new" have no `sharepoint-provisioning` Python planner
producing their plan JSON yet -- author the plan JSON by hand (see each
script's own docstring for the exact shape) until a planner is added. This is
an honest gap, not a hidden one: `sharepoint-provisioning`'s reconciliation
modules currently only plan create/delete for lists and create/link/unlink/
attach for content types and fields, never update or detach.

## Every script shares the same safety contract

`Get-WorkbenchConnectionConfig.ps1` is a shared dot-sourced connection-resolution
helper used by all the scripts in the table above -- it is not a standalone
executor and has no plan JSON shape of its own, which is why it does not
appear as a table row.

Dry-run by default, `-Execute` plus an operation-specific `-ConfirmToken`
required for any real write, connection resolved via
`Get-WorkbenchConnectionConfig.ps1` or explicit `-SiteUrl`/`-ClientId`/
`-TenantId`/`-TenantAdminUrl` parameters, `Connect-PnPOnline -Interactive`
per `.agent/rules/sharepoint-ps1-authentication-convention.md`. See each
script's own `.SYNOPSIS`/`.DESCRIPTION` for its exact plan JSON shape and
confirmation token string.

## No tenant writes without -Execute

Every script here prints a dry-run JSON action summary (including the exact
PnP cmdlet call it would run) when `-Execute` is omitted. Nothing is written
to the tenant until you pass both `-Execute` and the correct
`-ConfirmToken`.
