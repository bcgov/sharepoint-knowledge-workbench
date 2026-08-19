# SharePoint Provisioning/Migration-Planning/Page-Modernization Alignment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the confirmed PnP `.ps1` CRUD gaps in `sharepoint-migration-planning` (update/delete
site columns, update/delete content types, detach content type from list) and make the honest
plan-only/execute split between `sharepoint-provisioning`, `sharepoint-migration-planning`, and
`sharepoint-page-modernization` discoverable from each plugin's own `SKILL.md` files, without
renaming any plugin/skill directory.

**Architecture:** `sharepoint-provisioning`'s Python modules (`list_provisioning.py`,
`field_provisioning.py`, `content_type_provisioning.py`) already produce plan JSON shaped exactly
for `sharepoint-migration-planning`'s `spo-provision-*.ps1` real PnP executors (confirmed field-name
match in `spo-provision-list.ps1`'s own docstring). That design is sound but two things are missing:
(1) five PnP verbs (site-column update/delete, content-type update/delete, content-type-to-list
detach) have no executor at all, and (2) no skill anywhere symlinks the existing or new executor
scripts, so a caller has no discoverable "run this against my plan" entry point. This plan adds the
missing executors, gathers all provisioning-plan executors (existing + new) into one new skill
(`apply-sharepoint-provisioning-plan`) in `sharepoint-migration-planning` via file-level symlinks
per the hub-and-spoke policy, then updates the three plugins' `SKILL.md`/README files to
cross-reference each other honestly.

**Tech Stack:** PowerShell 7 (`pwsh`) + PnP.PowerShell cmdlets, Markdown (`SKILL.md`), existing
`Get-WorkbenchConnectionConfig.ps1` connection helper, plugin hub-and-spoke symlink convention.

**Spec:** No standalone spec doc exists for this; this plan's requirements are the audit findings
from this conversation (2026-08-18), cross-checked directly against
`plugins/sharepoint-provisioning/skills/*/SKILL.md`,
`plugins/sharepoint-migration-planning/scripts/spo-provision-*.ps1`, and
`plugins/sharepoint-page-modernization/skills/convert-aspx-pages/SKILL.md`.

## Global Constraints

- No plugin/skill directory renames (confirmed decision — see conversation). Only new files and
  `SKILL.md`/README content edits.
- Every new `.ps1` must follow the exact existing pattern in
  `plugins/sharepoint-migration-planning/scripts/spo-provision-site-columns.ps1`: dry-run by
  default, `-Execute` + `-ConfirmToken <OPERATION-TOKEN>` gate, `Get-WorkbenchConnectionConfig.ps1`
  for connection resolution, `Connect-PnPOnline -Interactive`, JSON `outcome` result
  (`OBSERVED`/`EMPTY`/`PARTIAL`/`FAILED`), verb-specific confirmation token string.
- New symlinks must be created as file-level symlinks only (`ln -s ../../../scripts/<file>
  <file>` from the skill's `scripts/` dir), per `.agent/rules/plugin-architecture-policy.md` §2,
  and recorded in the repo-root `symlinks.json` manifest matching existing entries' shape.
- No deletions of existing files without explicit permission (`.agent/rules/self-evolution-policy.md`)
  — this plan only adds files and edits `SKILL.md`/README prose.
- Per `.agent/rules/sharepoint-ps1-authentication-convention.md`, every live-tenant script uses the
  `Connect-PnPOnline` interactive + `TenantAdminUrl` pattern exactly as the existing scripts do —
  copy their `$connectParameters` block verbatim.

---

## Task 1: Add site-column update/delete executors

**Files:**
- Create: `plugins/sharepoint-migration-planning/scripts/spo-update-site-column.ps1`
- Create: `plugins/sharepoint-migration-planning/scripts/spo-remove-site-column.ps1`

**Interfaces:**
- Consumes: a plan JSON with shape `{ "actions": [ { "internal_name": "...", "display_name": "...",
  "description": "...", "required": true|false, "choices": [...] } ], "confirmation_token": "..." }`
  for the update script, and `{ "actions": [ { "internal_name": "..." } ], "confirmation_token":
  "..." }` for the remove script — same `-PlanPath`/`-Execute`/`-ConfirmToken`/`-SiteUrl`/
  `-ClientId`/`-TenantId`/`-ConfigPath`/`-TenantAdminUrl`/`-OutputPath` parameter set as
  `spo-provision-site-columns.ps1`.
- Produces: JSON result on stdout (and `-OutputPath` if given) with `outcome`/`dry_run`/`updated`
  (or `removed`)/`skipped`/`failed` arrays — same shape family as the existing scripts' `created`/
  `skipped`/`failed`.

- [ ] **Step 1: Write `spo-update-site-column.ps1`**

```powershell
<#
.SYNOPSIS
Real PnP executor for site-column updates -- Set-PnPField against a plan JSON's
`actions` array. Companion to spo-provision-site-columns.ps1 (create-only) and
spo-remove-site-column.ps1 (delete) -- this repo's site-column CRUD was
create-only before this script; DisplayName/Description/Required/Choices
changes to an already-created site column had no PnP executor anywhere.

.DESCRIPTION
Same dry-run-by-default / -Execute + -ConfirmToken / Get-WorkbenchConnectionConfig.ps1
pattern as every other spo-provision-*.ps1 script in this plugin -- see that
script's own docstring for the full safety-gate rationale, not repeated here.

Plan JSON shape:

    {
      "confirmation_token": "UPDATE-2-abcdef0123456789",
      "actions": [
        {
          "internal_name": "ClientMatterNumber",
          "display_name": "Client Matter Number",
          "description": "Updated per 2026-08-18 schema review",
          "required": false,
          "choices": []
        }
      ]
    }

.PARAMETER PlanPath
Path to the plan JSON described above.

.PARAMETER Execute
Runs the real Set-PnPField call. Omit this to print a dry-run action summary
and take no tenant action.

.PARAMETER ConfirmToken
Must equal UPDATE-SPO-SITE-COLUMNS when -Execute is passed. Refused otherwise.

.PARAMETER SiteUrl
.PARAMETER ClientId
.PARAMETER TenantId
.PARAMETER TenantAdminUrl
.PARAMETER ConfigPath
Connection parameters -- resolved via Get-WorkbenchConnectionConfig.ps1 when
-ConfigPath is given and the explicit parameters are omitted.

.PARAMETER OutputPath
Optional path to also write the JSON result to.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$PlanPath,

    [switch]$Execute,

    [string]$ConfirmToken,

    [string]$SiteUrl,
    [string]$ClientId,
    [string]$TenantId,
    [string]$TenantAdminUrl,
    [string]$ConfigPath,

    [string]$OutputPath
)

$ErrorActionPreference = "Stop"

if ($ConfigPath) {
    $helperPath = Join-Path $PSScriptRoot "Get-WorkbenchConnectionConfig.ps1"
    $config = & $helperPath -ConfigPath $ConfigPath
    if (-not $SiteUrl) { $SiteUrl = $config.SiteUrl }
    if (-not $ClientId) { $ClientId = $config.ClientId }
    if (-not $TenantId) { $TenantId = $config.TenantId }
    if (-not $TenantAdminUrl) { $TenantAdminUrl = $config.TenantAdminUrl }
}

if (-not (Test-Path -LiteralPath $PlanPath)) {
    throw "Plan file not found at '$PlanPath'."
}
$plan = Get-Content -LiteralPath $PlanPath -Raw | ConvertFrom-Json

if (-not $plan.actions -or $plan.actions.Count -eq 0) {
    $emptyResult = [ordered]@{
        outcome = "EMPTY"
        dry_run = -not $Execute
        updated = @()
        skipped = @()
        failed  = @()
    }
    $emptyJson = $emptyResult | ConvertTo-Json -Depth 8
    $emptyJson
    if ($OutputPath) { Set-Content -LiteralPath $OutputPath -Value $emptyJson -Encoding UTF8 }
    return
}

if ($Execute) {
    if ($ConfirmToken -ne "UPDATE-SPO-SITE-COLUMNS") {
        throw "-Execute requires -ConfirmToken UPDATE-SPO-SITE-COLUMNS."
    }
    if (-not $SiteUrl -or -not $ClientId -or -not $TenantId) {
        throw "SiteUrl/ClientId/TenantId not resolved. Provide -SiteUrl/-ClientId/-TenantId or a valid -ConfigPath."
    }
    if (-not (Get-Command Set-PnPField -ErrorAction SilentlyContinue)) {
        throw "PnP.PowerShell with Set-PnPField is required. Install/import PnP.PowerShell before executing."
    }

    $connectParameters = @{
        Url         = $SiteUrl
        ClientId    = $ClientId
        Tenant      = $TenantId
        Interactive = $true
    }
    if ($TenantAdminUrl) { $connectParameters["TenantAdminUrl"] = $TenantAdminUrl }
    Connect-PnPOnline @connectParameters

    $updated = @()
    $failed = @()

    foreach ($action in $plan.actions) {
        try {
            $setParameters = @{
                Identity    = $action.internal_name
                ErrorAction = "Stop"
            }
            if ($action.display_name) { $setParameters["Values"] = @{ Title = $action.display_name } }
            if ($null -ne $action.description) {
                if (-not $setParameters.ContainsKey("Values")) { $setParameters["Values"] = @{} }
                $setParameters["Values"]["Description"] = $action.description
            }
            if ($null -ne $action.required) {
                if (-not $setParameters.ContainsKey("Values")) { $setParameters["Values"] = @{} }
                $setParameters["Values"]["Required"] = [bool]$action.required
            }
            if ($action.choices -and $action.choices.Count -gt 0) {
                if (-not $setParameters.ContainsKey("Values")) { $setParameters["Values"] = @{} }
                $setParameters["Values"]["Choices"] = $action.choices
            }
            Set-PnPField @setParameters | Out-Null
            $updated += [ordered]@{ internal_name = $action.internal_name }
        }
        catch {
            $failed += [ordered]@{ internal_name = $action.internal_name; error = $_.Exception.Message }
        }
    }

    $outcome = if ($updated.Count -eq 0 -and $failed.Count -gt 0) { "FAILED" }
        elseif ($failed.Count -gt 0) { "PARTIAL" }
        else { "OBSERVED" }

    $result = [ordered]@{
        outcome = $outcome
        dry_run = $false
        updated = $updated
        skipped = @()
        failed  = $failed
    }
    $resultJson = $result | ConvertTo-Json -Depth 8
    $resultJson
    if ($OutputPath) { Set-Content -LiteralPath $OutputPath -Value $resultJson -Encoding UTF8 }
}
else {
    $actionPlans = foreach ($action in $plan.actions) {
        [ordered]@{
            internal_name = $action.internal_name
            action        = "Set-PnPField -Identity `"$($action.internal_name)`" -Values @{Title=`"$($action.display_name)`"; Description=`"$($action.description)`"; Required=$([bool]$action.required)}"
        }
    }
    $summary = [ordered]@{
        operation           = "update-spo-site-columns"
        confirmation_token  = $plan.confirmation_token
        update_count        = $plan.actions.Count
        site_url            = $SiteUrl
        safety              = [ordered]@{
            tenant_io                      = "none"
            execute_requires_confirm_token = "UPDATE-SPO-SITE-COLUMNS"
        }
        planned_actions     = $actionPlans
    }
    $summaryJson = $summary | ConvertTo-Json -Depth 8
    $summaryJson
    if ($OutputPath) { Set-Content -LiteralPath $OutputPath -Value $summaryJson -Encoding UTF8 }
}
```

- [ ] **Step 2: Write `spo-remove-site-column.ps1`**

```powershell
<#
.SYNOPSIS
Real PnP executor for site-column deletion -- Remove-PnPField against a plan
JSON's `actions` array. Companion to spo-provision-site-columns.ps1
(create-only) and spo-update-site-column.ps1 (update).

.DESCRIPTION
Same dry-run-by-default / -Execute + -ConfirmToken / Get-WorkbenchConnectionConfig.ps1
pattern as every other spo-provision-*.ps1 script in this plugin.

Plan JSON shape:

    {
      "confirmation_token": "REMOVE-2-abcdef0123456789",
      "actions": [ { "internal_name": "DeprecatedField" } ]
    }

.PARAMETER PlanPath
Path to the plan JSON described above.

.PARAMETER Execute
Runs the real Remove-PnPField call. Omit this to print a dry-run action
summary and take no tenant action.

.PARAMETER ConfirmToken
Must equal REMOVE-SPO-SITE-COLUMNS when -Execute is passed. Refused otherwise.

.PARAMETER SiteUrl
.PARAMETER ClientId
.PARAMETER TenantId
.PARAMETER TenantAdminUrl
.PARAMETER ConfigPath
.PARAMETER OutputPath
Same meaning as spo-update-site-column.ps1.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$PlanPath,

    [switch]$Execute,

    [string]$ConfirmToken,

    [string]$SiteUrl,
    [string]$ClientId,
    [string]$TenantId,
    [string]$TenantAdminUrl,
    [string]$ConfigPath,

    [string]$OutputPath
)

$ErrorActionPreference = "Stop"

if ($ConfigPath) {
    $helperPath = Join-Path $PSScriptRoot "Get-WorkbenchConnectionConfig.ps1"
    $config = & $helperPath -ConfigPath $ConfigPath
    if (-not $SiteUrl) { $SiteUrl = $config.SiteUrl }
    if (-not $ClientId) { $ClientId = $config.ClientId }
    if (-not $TenantId) { $TenantId = $config.TenantId }
    if (-not $TenantAdminUrl) { $TenantAdminUrl = $config.TenantAdminUrl }
}

if (-not (Test-Path -LiteralPath $PlanPath)) {
    throw "Plan file not found at '$PlanPath'."
}
$plan = Get-Content -LiteralPath $PlanPath -Raw | ConvertFrom-Json

if (-not $plan.actions -or $plan.actions.Count -eq 0) {
    $emptyResult = [ordered]@{ outcome = "EMPTY"; dry_run = -not $Execute; removed = @(); failed = @() }
    $emptyJson = $emptyResult | ConvertTo-Json -Depth 8
    $emptyJson
    if ($OutputPath) { Set-Content -LiteralPath $OutputPath -Value $emptyJson -Encoding UTF8 }
    return
}

if ($Execute) {
    if ($ConfirmToken -ne "REMOVE-SPO-SITE-COLUMNS") {
        throw "-Execute requires -ConfirmToken REMOVE-SPO-SITE-COLUMNS."
    }
    if (-not $SiteUrl -or -not $ClientId -or -not $TenantId) {
        throw "SiteUrl/ClientId/TenantId not resolved. Provide -SiteUrl/-ClientId/-TenantId or a valid -ConfigPath."
    }
    if (-not (Get-Command Remove-PnPField -ErrorAction SilentlyContinue)) {
        throw "PnP.PowerShell with Remove-PnPField is required. Install/import PnP.PowerShell before executing."
    }

    $connectParameters = @{
        Url         = $SiteUrl
        ClientId    = $ClientId
        Tenant      = $TenantId
        Interactive = $true
    }
    if ($TenantAdminUrl) { $connectParameters["TenantAdminUrl"] = $TenantAdminUrl }
    Connect-PnPOnline @connectParameters

    $removed = @()
    $failed = @()
    foreach ($action in $plan.actions) {
        try {
            Remove-PnPField -Identity $action.internal_name -Force -ErrorAction Stop
            $removed += [ordered]@{ internal_name = $action.internal_name }
        }
        catch {
            $failed += [ordered]@{ internal_name = $action.internal_name; error = $_.Exception.Message }
        }
    }

    $outcome = if ($removed.Count -eq 0 -and $failed.Count -gt 0) { "FAILED" }
        elseif ($failed.Count -gt 0) { "PARTIAL" }
        else { "OBSERVED" }

    $result = [ordered]@{ outcome = $outcome; dry_run = $false; removed = $removed; failed = $failed }
    $resultJson = $result | ConvertTo-Json -Depth 8
    $resultJson
    if ($OutputPath) { Set-Content -LiteralPath $OutputPath -Value $resultJson -Encoding UTF8 }
}
else {
    $actionPlans = foreach ($action in $plan.actions) {
        [ordered]@{ internal_name = $action.internal_name; action = "Remove-PnPField -Identity `"$($action.internal_name)`" -Force" }
    }
    $summary = [ordered]@{
        operation          = "remove-spo-site-columns"
        confirmation_token = $plan.confirmation_token
        remove_count       = $plan.actions.Count
        site_url           = $SiteUrl
        safety             = [ordered]@{ tenant_io = "none"; execute_requires_confirm_token = "REMOVE-SPO-SITE-COLUMNS" }
        planned_actions    = $actionPlans
    }
    $summaryJson = $summary | ConvertTo-Json -Depth 8
    $summaryJson
    if ($OutputPath) { Set-Content -LiteralPath $OutputPath -Value $summaryJson -Encoding UTF8 }
}
```

- [ ] **Step 3: Syntax-check both scripts**

Run: `pwsh -NoProfile -Command "Get-Command -Syntax { . 'plugins/sharepoint-migration-planning/scripts/spo-update-site-column.ps1' }" ` is not applicable to dot-sourcing a param'd script directly; instead parse-check:

```bash
pwsh -NoProfile -Command "[System.Management.Automation.Language.Parser]::ParseFile('plugins/sharepoint-migration-planning/scripts/spo-update-site-column.ps1', [ref]$null, [ref]$null) | Out-Null; Write-Output 'OK'"
pwsh -NoProfile -Command "[System.Management.Automation.Language.Parser]::ParseFile('plugins/sharepoint-migration-planning/scripts/spo-remove-site-column.ps1', [ref]$null, [ref]$null) | Out-Null; Write-Output 'OK'"
```
Expected: both print `OK` with no parser errors.

- [ ] **Step 4: Commit**

```bash
git add plugins/sharepoint-migration-planning/scripts/spo-update-site-column.ps1 plugins/sharepoint-migration-planning/scripts/spo-remove-site-column.ps1
git commit -m "feat(sharepoint-migration-planning): add site-column update/delete PnP executors"
```

---

## Task 2: Add content-type update/delete and content-type-to-list detach executors

**Files:**
- Create: `plugins/sharepoint-migration-planning/scripts/spo-update-content-type.ps1`
- Create: `plugins/sharepoint-migration-planning/scripts/spo-remove-content-type.ps1`
- Create: `plugins/sharepoint-migration-planning/scripts/spo-detach-content-type-from-list.ps1`

**Interfaces:**
- Consumes: plan JSON `{ "confirmation_token": "...", "actions": [ { "content_type_name": "...",
  "display_name": "...", "description": "..." } ] }` for update; `{ "confirmation_token": "...",
  "actions": [ { "content_type_name": "..." } ] }` for remove and for detach (detach additionally
  needs `"list_title"` per action).
- Produces: same `outcome`/`dry_run`/`updated|removed|detached`/`failed` JSON shape family as
  Task 1's scripts.

- [ ] **Step 1: Write `spo-update-content-type.ps1`**

```powershell
<#
.SYNOPSIS
Real PnP executor for content-type updates -- Set-PnPContentType against a
plan JSON's `actions` array. Companion to spo-provision-content-types.ps1
(create/link/unlink/attach only) -- renaming or re-describing an
already-created content type had no PnP executor anywhere before this script.

.DESCRIPTION
Same dry-run-by-default / -Execute + -ConfirmToken / Get-WorkbenchConnectionConfig.ps1
pattern as every other spo-provision-*.ps1 script in this plugin.

Plan JSON shape:

    {
      "confirmation_token": "UPDATE-CT-abcdef0123456789",
      "actions": [
        { "content_type_name": "Case File", "display_name": "Case File v2", "description": "Renamed 2026-08-18" }
      ]
    }

.PARAMETER PlanPath
.PARAMETER Execute
Runs the real Set-PnPContentType call. Omit for dry-run.
.PARAMETER ConfirmToken
Must equal UPDATE-SPO-CONTENT-TYPES when -Execute is passed.
.PARAMETER SiteUrl
.PARAMETER ClientId
.PARAMETER TenantId
.PARAMETER TenantAdminUrl
.PARAMETER ConfigPath
.PARAMETER OutputPath
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$PlanPath,

    [switch]$Execute,
    [string]$ConfirmToken,

    [string]$SiteUrl,
    [string]$ClientId,
    [string]$TenantId,
    [string]$TenantAdminUrl,
    [string]$ConfigPath,

    [string]$OutputPath
)

$ErrorActionPreference = "Stop"

if ($ConfigPath) {
    $helperPath = Join-Path $PSScriptRoot "Get-WorkbenchConnectionConfig.ps1"
    $config = & $helperPath -ConfigPath $ConfigPath
    if (-not $SiteUrl) { $SiteUrl = $config.SiteUrl }
    if (-not $ClientId) { $ClientId = $config.ClientId }
    if (-not $TenantId) { $TenantId = $config.TenantId }
    if (-not $TenantAdminUrl) { $TenantAdminUrl = $config.TenantAdminUrl }
}

if (-not (Test-Path -LiteralPath $PlanPath)) { throw "Plan file not found at '$PlanPath'." }
$plan = Get-Content -LiteralPath $PlanPath -Raw | ConvertFrom-Json

if (-not $plan.actions -or $plan.actions.Count -eq 0) {
    $emptyResult = [ordered]@{ outcome = "EMPTY"; dry_run = -not $Execute; updated = @(); failed = @() }
    $emptyJson = $emptyResult | ConvertTo-Json -Depth 8
    $emptyJson
    if ($OutputPath) { Set-Content -LiteralPath $OutputPath -Value $emptyJson -Encoding UTF8 }
    return
}

if ($Execute) {
    if ($ConfirmToken -ne "UPDATE-SPO-CONTENT-TYPES") {
        throw "-Execute requires -ConfirmToken UPDATE-SPO-CONTENT-TYPES."
    }
    if (-not $SiteUrl -or -not $ClientId -or -not $TenantId) {
        throw "SiteUrl/ClientId/TenantId not resolved. Provide -SiteUrl/-ClientId/-TenantId or a valid -ConfigPath."
    }
    if (-not (Get-Command Set-PnPContentType -ErrorAction SilentlyContinue)) {
        throw "PnP.PowerShell with Set-PnPContentType is required. Install/import PnP.PowerShell before executing."
    }

    $connectParameters = @{ Url = $SiteUrl; ClientId = $ClientId; Tenant = $TenantId; Interactive = $true }
    if ($TenantAdminUrl) { $connectParameters["TenantAdminUrl"] = $TenantAdminUrl }
    Connect-PnPOnline @connectParameters

    $updated = @()
    $failed = @()
    foreach ($action in $plan.actions) {
        try {
            $setParameters = @{ Identity = $action.content_type_name; ErrorAction = "Stop" }
            if ($action.display_name) { $setParameters["NewName"] = $action.display_name }
            if ($null -ne $action.description) { $setParameters["Description"] = $action.description }
            Set-PnPContentType @setParameters | Out-Null
            $updated += [ordered]@{ content_type_name = $action.content_type_name }
        }
        catch {
            $failed += [ordered]@{ content_type_name = $action.content_type_name; error = $_.Exception.Message }
        }
    }

    $outcome = if ($updated.Count -eq 0 -and $failed.Count -gt 0) { "FAILED" } elseif ($failed.Count -gt 0) { "PARTIAL" } else { "OBSERVED" }
    $result = [ordered]@{ outcome = $outcome; dry_run = $false; updated = $updated; failed = $failed }
    $resultJson = $result | ConvertTo-Json -Depth 8
    $resultJson
    if ($OutputPath) { Set-Content -LiteralPath $OutputPath -Value $resultJson -Encoding UTF8 }
}
else {
    $actionPlans = foreach ($action in $plan.actions) {
        [ordered]@{ content_type_name = $action.content_type_name; action = "Set-PnPContentType -Identity `"$($action.content_type_name)`" -NewName `"$($action.display_name)`" -Description `"$($action.description)`"" }
    }
    $summary = [ordered]@{
        operation           = "update-spo-content-types"
        confirmation_token  = $plan.confirmation_token
        update_count        = $plan.actions.Count
        site_url            = $SiteUrl
        safety              = [ordered]@{ tenant_io = "none"; execute_requires_confirm_token = "UPDATE-SPO-CONTENT-TYPES" }
        planned_actions     = $actionPlans
    }
    $summaryJson = $summary | ConvertTo-Json -Depth 8
    $summaryJson
    if ($OutputPath) { Set-Content -LiteralPath $OutputPath -Value $summaryJson -Encoding UTF8 }
}
```

- [ ] **Step 2: Write `spo-remove-content-type.ps1`**

```powershell
<#
.SYNOPSIS
Real PnP executor for content-type deletion -- Remove-PnPContentType against
a plan JSON's `actions` array. Companion to spo-provision-content-types.ps1
(create only).

.DESCRIPTION
Same dry-run-by-default / -Execute + -ConfirmToken pattern as the rest of
this plugin's executors.

Plan JSON shape:

    { "confirmation_token": "REMOVE-CT-abc", "actions": [ { "content_type_name": "Obsolete Type" } ] }

.PARAMETER PlanPath
.PARAMETER Execute
.PARAMETER ConfirmToken
Must equal REMOVE-SPO-CONTENT-TYPES when -Execute is passed.
.PARAMETER SiteUrl
.PARAMETER ClientId
.PARAMETER TenantId
.PARAMETER TenantAdminUrl
.PARAMETER ConfigPath
.PARAMETER OutputPath
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$PlanPath,

    [switch]$Execute,
    [string]$ConfirmToken,

    [string]$SiteUrl,
    [string]$ClientId,
    [string]$TenantId,
    [string]$TenantAdminUrl,
    [string]$ConfigPath,

    [string]$OutputPath
)

$ErrorActionPreference = "Stop"

if ($ConfigPath) {
    $helperPath = Join-Path $PSScriptRoot "Get-WorkbenchConnectionConfig.ps1"
    $config = & $helperPath -ConfigPath $ConfigPath
    if (-not $SiteUrl) { $SiteUrl = $config.SiteUrl }
    if (-not $ClientId) { $ClientId = $config.ClientId }
    if (-not $TenantId) { $TenantId = $config.TenantId }
    if (-not $TenantAdminUrl) { $TenantAdminUrl = $config.TenantAdminUrl }
}

if (-not (Test-Path -LiteralPath $PlanPath)) { throw "Plan file not found at '$PlanPath'." }
$plan = Get-Content -LiteralPath $PlanPath -Raw | ConvertFrom-Json

if (-not $plan.actions -or $plan.actions.Count -eq 0) {
    $emptyResult = [ordered]@{ outcome = "EMPTY"; dry_run = -not $Execute; removed = @(); failed = @() }
    $emptyJson = $emptyResult | ConvertTo-Json -Depth 8
    $emptyJson
    if ($OutputPath) { Set-Content -LiteralPath $OutputPath -Value $emptyJson -Encoding UTF8 }
    return
}

if ($Execute) {
    if ($ConfirmToken -ne "REMOVE-SPO-CONTENT-TYPES") {
        throw "-Execute requires -ConfirmToken REMOVE-SPO-CONTENT-TYPES."
    }
    if (-not $SiteUrl -or -not $ClientId -or -not $TenantId) {
        throw "SiteUrl/ClientId/TenantId not resolved. Provide -SiteUrl/-ClientId/-TenantId or a valid -ConfigPath."
    }
    if (-not (Get-Command Remove-PnPContentType -ErrorAction SilentlyContinue)) {
        throw "PnP.PowerShell with Remove-PnPContentType is required. Install/import PnP.PowerShell before executing."
    }

    $connectParameters = @{ Url = $SiteUrl; ClientId = $ClientId; Tenant = $TenantId; Interactive = $true }
    if ($TenantAdminUrl) { $connectParameters["TenantAdminUrl"] = $TenantAdminUrl }
    Connect-PnPOnline @connectParameters

    $removed = @()
    $failed = @()
    foreach ($action in $plan.actions) {
        try {
            Remove-PnPContentType -Identity $action.content_type_name -Force -ErrorAction Stop
            $removed += [ordered]@{ content_type_name = $action.content_type_name }
        }
        catch {
            $failed += [ordered]@{ content_type_name = $action.content_type_name; error = $_.Exception.Message }
        }
    }

    $outcome = if ($removed.Count -eq 0 -and $failed.Count -gt 0) { "FAILED" } elseif ($failed.Count -gt 0) { "PARTIAL" } else { "OBSERVED" }
    $result = [ordered]@{ outcome = $outcome; dry_run = $false; removed = $removed; failed = $failed }
    $resultJson = $result | ConvertTo-Json -Depth 8
    $resultJson
    if ($OutputPath) { Set-Content -LiteralPath $OutputPath -Value $resultJson -Encoding UTF8 }
}
else {
    $actionPlans = foreach ($action in $plan.actions) {
        [ordered]@{ content_type_name = $action.content_type_name; action = "Remove-PnPContentType -Identity `"$($action.content_type_name)`" -Force" }
    }
    $summary = [ordered]@{
        operation          = "remove-spo-content-types"
        confirmation_token = $plan.confirmation_token
        remove_count       = $plan.actions.Count
        site_url           = $SiteUrl
        safety             = [ordered]@{ tenant_io = "none"; execute_requires_confirm_token = "REMOVE-SPO-CONTENT-TYPES" }
        planned_actions    = $actionPlans
    }
    $summaryJson = $summary | ConvertTo-Json -Depth 8
    $summaryJson
    if ($OutputPath) { Set-Content -LiteralPath $OutputPath -Value $summaryJson -Encoding UTF8 }
}
```

- [ ] **Step 3: Write `spo-detach-content-type-from-list.ps1`**

```powershell
<#
.SYNOPSIS
Real PnP executor for removing a content type from a list --
Remove-PnPContentTypeFromList against a plan JSON's `actions` array.
Companion to spo-provision-content-types.ps1's attach_content_type step
(Add-PnPContentTypeToList) -- attach existed, detach did not.

.DESCRIPTION
Same dry-run-by-default / -Execute + -ConfirmToken pattern as the rest of
this plugin's executors.

Plan JSON shape:

    {
      "confirmation_token": "DETACH-CT-abc",
      "actions": [ { "content_type_name": "Case File", "list_title": "Case Files" } ]
    }

.PARAMETER PlanPath
.PARAMETER Execute
.PARAMETER ConfirmToken
Must equal DETACH-SPO-CONTENT-TYPE when -Execute is passed.
.PARAMETER SiteUrl
.PARAMETER ClientId
.PARAMETER TenantId
.PARAMETER TenantAdminUrl
.PARAMETER ConfigPath
.PARAMETER OutputPath
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$PlanPath,

    [switch]$Execute,
    [string]$ConfirmToken,

    [string]$SiteUrl,
    [string]$ClientId,
    [string]$TenantId,
    [string]$TenantAdminUrl,
    [string]$ConfigPath,

    [string]$OutputPath
)

$ErrorActionPreference = "Stop"

if ($ConfigPath) {
    $helperPath = Join-Path $PSScriptRoot "Get-WorkbenchConnectionConfig.ps1"
    $config = & $helperPath -ConfigPath $ConfigPath
    if (-not $SiteUrl) { $SiteUrl = $config.SiteUrl }
    if (-not $ClientId) { $ClientId = $config.ClientId }
    if (-not $TenantId) { $TenantId = $config.TenantId }
    if (-not $TenantAdminUrl) { $TenantAdminUrl = $config.TenantAdminUrl }
}

if (-not (Test-Path -LiteralPath $PlanPath)) { throw "Plan file not found at '$PlanPath'." }
$plan = Get-Content -LiteralPath $PlanPath -Raw | ConvertFrom-Json

if (-not $plan.actions -or $plan.actions.Count -eq 0) {
    $emptyResult = [ordered]@{ outcome = "EMPTY"; dry_run = -not $Execute; detached = @(); failed = @() }
    $emptyJson = $emptyResult | ConvertTo-Json -Depth 8
    $emptyJson
    if ($OutputPath) { Set-Content -LiteralPath $OutputPath -Value $emptyJson -Encoding UTF8 }
    return
}

if ($Execute) {
    if ($ConfirmToken -ne "DETACH-SPO-CONTENT-TYPE") {
        throw "-Execute requires -ConfirmToken DETACH-SPO-CONTENT-TYPE."
    }
    if (-not $SiteUrl -or -not $ClientId -or -not $TenantId) {
        throw "SiteUrl/ClientId/TenantId not resolved. Provide -SiteUrl/-ClientId/-TenantId or a valid -ConfigPath."
    }
    if (-not (Get-Command Remove-PnPContentTypeFromList -ErrorAction SilentlyContinue)) {
        throw "PnP.PowerShell with Remove-PnPContentTypeFromList is required. Install/import PnP.PowerShell before executing."
    }

    $connectParameters = @{ Url = $SiteUrl; ClientId = $ClientId; Tenant = $TenantId; Interactive = $true }
    if ($TenantAdminUrl) { $connectParameters["TenantAdminUrl"] = $TenantAdminUrl }
    Connect-PnPOnline @connectParameters

    $detached = @()
    $failed = @()
    foreach ($action in $plan.actions) {
        try {
            Remove-PnPContentTypeFromList -List $action.list_title -ContentType $action.content_type_name -ErrorAction Stop
            $detached += [ordered]@{ content_type_name = $action.content_type_name; list_title = $action.list_title }
        }
        catch {
            $failed += [ordered]@{ content_type_name = $action.content_type_name; list_title = $action.list_title; error = $_.Exception.Message }
        }
    }

    $outcome = if ($detached.Count -eq 0 -and $failed.Count -gt 0) { "FAILED" } elseif ($failed.Count -gt 0) { "PARTIAL" } else { "OBSERVED" }
    $result = [ordered]@{ outcome = $outcome; dry_run = $false; detached = $detached; failed = $failed }
    $resultJson = $result | ConvertTo-Json -Depth 8
    $resultJson
    if ($OutputPath) { Set-Content -LiteralPath $OutputPath -Value $resultJson -Encoding UTF8 }
}
else {
    $actionPlans = foreach ($action in $plan.actions) {
        [ordered]@{ content_type_name = $action.content_type_name; list_title = $action.list_title; action = "Remove-PnPContentTypeFromList -List `"$($action.list_title)`" -ContentType `"$($action.content_type_name)`"" }
    }
    $summary = [ordered]@{
        operation           = "detach-spo-content-type-from-list"
        confirmation_token  = $plan.confirmation_token
        detach_count        = $plan.actions.Count
        site_url            = $SiteUrl
        safety              = [ordered]@{ tenant_io = "none"; execute_requires_confirm_token = "DETACH-SPO-CONTENT-TYPE" }
        planned_actions     = $actionPlans
    }
    $summaryJson = $summary | ConvertTo-Json -Depth 8
    $summaryJson
    if ($OutputPath) { Set-Content -LiteralPath $OutputPath -Value $summaryJson -Encoding UTF8 }
}
```

- [ ] **Step 4: Syntax-check all three scripts**

```bash
for f in spo-update-content-type.ps1 spo-remove-content-type.ps1 spo-detach-content-type-from-list.ps1; do
  pwsh -NoProfile -Command "[System.Management.Automation.Language.Parser]::ParseFile('plugins/sharepoint-migration-planning/scripts/$f', [ref]\$null, [ref]\$null) | Out-Null; Write-Output '$f OK'"
done
```
Expected: three `OK` lines, no parser errors.

- [ ] **Step 5: Commit**

```bash
git add plugins/sharepoint-migration-planning/scripts/spo-update-content-type.ps1 plugins/sharepoint-migration-planning/scripts/spo-remove-content-type.ps1 plugins/sharepoint-migration-planning/scripts/spo-detach-content-type-from-list.ps1
git commit -m "feat(sharepoint-migration-planning): add content-type update/delete and list-detach PnP executors"
```

---

## Task 3: Create the `apply-sharepoint-provisioning-plan` skill and symlink every provisioning executor into it

**Files:**
- Create: `plugins/sharepoint-migration-planning/skills/apply-sharepoint-provisioning-plan/SKILL.md`
- Create (symlinks): `plugins/sharepoint-migration-planning/skills/apply-sharepoint-provisioning-plan/scripts/{Get-WorkbenchConnectionConfig.ps1,spo-provision-list.ps1,spo-provision-content-types.ps1,spo-provision-site-columns.ps1,spo-update-site-column.ps1,spo-remove-site-column.ps1,spo-update-content-type.ps1,spo-remove-content-type.ps1,spo-detach-content-type-from-list.ps1}`
- Modify: `symlinks.json` (append 9 new entries matching the existing entries' shape)

**Interfaces:**
- Consumes: nothing new — this task only exposes Task 1/2's scripts plus the three pre-existing
  create/attach scripts through one discoverable skill.
- Produces: a single skill entry point (`apply-sharepoint-provisioning-plan`) that
  `sharepoint-provisioning`'s Task 4 `SKILL.md` edits will point to as "your injected executor."

- [ ] **Step 1: Create the symlinks**

Run from repo root (Git Bash / WSL — real symlinks, matching the existing ones `find -type l`
already confirmed in this plugin tree):

```bash
cd plugins/sharepoint-migration-planning/skills/apply-sharepoint-provisioning-plan
mkdir -p scripts
cd scripts
for f in Get-WorkbenchConnectionConfig.ps1 spo-provision-list.ps1 spo-provision-content-types.ps1 spo-provision-site-columns.ps1 spo-update-site-column.ps1 spo-remove-site-column.ps1 spo-update-content-type.ps1 spo-remove-content-type.ps1 spo-detach-content-type-from-list.ps1; do
  ln -s "../../../scripts/$f" "$f"
done
cd ../../../../..
```

- [ ] **Step 2: Verify the symlinks resolve**

```bash
for f in plugins/sharepoint-migration-planning/skills/apply-sharepoint-provisioning-plan/scripts/*.ps1; do
  test -L "$f" && test -e "$f" && echo "OK: $f" || echo "BROKEN: $f"
done
```
Expected: nine `OK:` lines, zero `BROKEN:` lines.

- [ ] **Step 3: Append entries to `symlinks.json`**

Open `symlinks.json` at repo root and add nine entries to the `links` array (matching the file's
existing entry shape exactly), one per symlink from Step 1, e.g.:

```json
{
  "src": "plugins/sharepoint-migration-planning/scripts/spo-update-site-column.ps1",
  "dst": "plugins/sharepoint-migration-planning/skills/apply-sharepoint-provisioning-plan/scripts/spo-update-site-column.ps1",
  "strategy": "symlink",
  "description": "apply-sharepoint-provisioning-plan skill's bundled copy of spo-update-site-column.ps1"
}
```

Repeat for `Get-WorkbenchConnectionConfig.ps1`, `spo-provision-list.ps1`,
`spo-provision-content-types.ps1`, `spo-provision-site-columns.ps1`, `spo-remove-site-column.ps1`,
`spo-update-content-type.ps1`, `spo-remove-content-type.ps1`, and
`spo-detach-content-type-from-list.ps1`.

- [ ] **Step 4: Write `SKILL.md`**

```markdown
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

The four scripts marked "new" have no `sharepoint-provisioning` Python planner
producing their plan JSON yet -- author the plan JSON by hand (see each
script's own docstring for the exact shape) until a planner is added. This is
an honest gap, not a hidden one: `sharepoint-provisioning`'s reconciliation
modules currently only plan create/delete for lists and create/link/unlink/
attach for content types and fields, never update or detach.

## Every script shares the same safety contract

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
```

- [ ] **Step 5: Verify the skill's `SKILL.md` references only in-skill-relative paths**

```bash
grep -n "scripts/" plugins/sharepoint-migration-planning/skills/apply-sharepoint-provisioning-plan/SKILL.md
```
Expected: both `examples:` lines and the table reference bare `scripts/<file>.ps1` filenames only
(no `../` or absolute paths), per `.agent/rules/plugin-architecture-policy.md` §3.

- [ ] **Step 6: Commit**

```bash
git add plugins/sharepoint-migration-planning/skills/apply-sharepoint-provisioning-plan symlinks.json
git commit -m "feat(sharepoint-migration-planning): add apply-sharepoint-provisioning-plan skill exposing all provisioning PnP executors"
```

---

## Task 4: Align `sharepoint-provisioning`'s four `SKILL.md` files

**Files:**
- Modify: `plugins/sharepoint-provisioning/skills/provision-list/SKILL.md`
- Modify: `plugins/sharepoint-provisioning/skills/provision-content-types/SKILL.md`
- Modify: `plugins/sharepoint-provisioning/skills/provision-fields/SKILL.md`
- Modify: `plugins/sharepoint-provisioning/skills/provision-modern-calendar-list/SKILL.md`
- Modify: `plugins/sharepoint-provisioning/README.md` (the "executes" wording flagged in this
  conversation)

**Interfaces:**
- Consumes: `apply-sharepoint-provisioning-plan` skill name and script table from Task 3.
- Produces: nothing new — prose-only edits.

- [ ] **Step 1: Add an "Executor" section to `provision-list/SKILL.md`**

Insert immediately after the existing `## Write safety` section (found via `grep -n "^## " plugins/sharepoint-provisioning/skills/provision-list/SKILL.md` to get the exact insertion line):

```markdown
## Where the "injected executor" actually lives

This skill's Python `apply_provisioning(plan, executor=...)` ships no tenant
transport of its own -- by design (see Write safety above). The real,
tested PnP.PowerShell executor that plan JSON is meant to be submitted to is
`sharepoint-migration-planning`'s `apply-sharepoint-provisioning-plan` skill
(`spo-provision-list.ps1` specifically, which consumes this module's
`ProvisioningPlan.to_dict()` output verbatim -- see that script's own
docstring for the exact field-name match). This skill produces the plan;
that skill is the executor you inject.
```

- [ ] **Step 2: Add the same section (adapted per-object) to the other three `SKILL.md` files**

For `provision-content-types/SKILL.md`, point to `spo-provision-content-types.ps1`,
`spo-update-content-type.ps1`, `spo-remove-content-type.ps1`, and
`spo-detach-content-type-from-list.ps1`. For `provision-fields/SKILL.md`, point to
`spo-provision-site-columns.ps1`, `spo-update-site-column.ps1`, and
`spo-remove-site-column.ps1`. For `provision-modern-calendar-list/SKILL.md`, point to
`spo-provision-calendar.ps1` (already in `sharepoint-migration-planning/scripts/`, not yet
symlinked into any skill — note in this section that it is not currently part of
`apply-sharepoint-provisioning-plan` and should be treated as a follow-up, not silently included).

- [ ] **Step 3: Fix the "executes" claim in `sharepoint-provisioning/README.md`**

Find the line (via `grep -n "executes" plugins/sharepoint-provisioning/README.md`) reading:
`sharepoint-provisioning executes a single-pass reconcile of one target schema (three-gate write safety)`

Replace with:
```markdown
`sharepoint-provisioning` **plans** a single-pass reconcile of one target schema (three-gate write
safety) and, once approved, submits that plan to `sharepoint-migration-planning`'s
`apply-sharepoint-provisioning-plan` skill for real execution
```

- [ ] **Step 4: Verify all four `SKILL.md` files and the README mention `apply-sharepoint-provisioning-plan`**

```bash
grep -rl "apply-sharepoint-provisioning-plan" plugins/sharepoint-provisioning/skills/*/SKILL.md plugins/sharepoint-provisioning/README.md
```
Expected: five file paths printed (four `SKILL.md` + `README.md`).

- [ ] **Step 5: Commit**

```bash
git add plugins/sharepoint-provisioning/skills/*/SKILL.md plugins/sharepoint-provisioning/README.md
git commit -m "docs(sharepoint-provisioning): cross-reference the real PnP executor skill in sharepoint-migration-planning"
```

---

## Task 5: Cross-reference the real deployment owner from `sharepoint-page-modernization`

**Files:**
- Modify: `plugins/sharepoint-page-modernization/skills/convert-aspx-pages/SKILL.md`
- Modify: `plugins/sharepoint-page-modernization/README.md`

**Interfaces:**
- Consumes: `sharepoint-content-publication`'s `convert-page-to-modern` skill name (confirmed to
  exist, real `ConvertTo-PnPPage` executor, dry-run/`-Execute`/confirm-token gated).
- Produces: nothing new — prose-only edits.

- [ ] **Step 1: Replace the vague "owned elsewhere" line**

In `plugins/sharepoint-page-modernization/skills/convert-aspx-pages/SKILL.md`, find (via
`grep -n "owned elsewhere" plugins/sharepoint-page-modernization/skills/convert-aspx-pages/SKILL.md`):

```markdown
## No tenant writes

This skill produces a manifest describing the intended modern page. It does not
create, publish, or modify anything in SharePoint. Deployment is a separate,
explicitly-authorized concern owned elsewhere in the workbench.
```

Replace with:

```markdown
## No tenant writes

This skill produces a manifest describing the intended modern page. It does not
create, publish, or modify anything in SharePoint. Deployment is a separate,
explicitly-authorized concern: once you have a reviewed conversion manifest,
hand the source page name/library/target metadata to
`sharepoint-content-publication`'s `convert-page-to-modern` skill
(`spo-convert-page-to-modern.ps1`, real `ConvertTo-PnPPage` executor,
dry-run by default, gated behind `-Execute -ConfirmToken`). That skill does
not read this plugin's manifest format directly -- you supply its
`-PageName`/`-SourceLibrary`/field-mapping parameters yourself from the
manifest's contents.
```

- [ ] **Step 2: Add the same pointer to `README.md`**

Find the matching "does not create, publish, or modify" sentence in
`plugins/sharepoint-page-modernization/README.md` and append one sentence naming
`sharepoint-content-publication`'s `convert-page-to-modern` skill as the deployment owner, matching
Step 1's wording.

- [ ] **Step 3: Verify**

```bash
grep -rl "convert-page-to-modern" plugins/sharepoint-page-modernization/skills/convert-aspx-pages/SKILL.md plugins/sharepoint-page-modernization/README.md
```
Expected: both file paths printed.

- [ ] **Step 4: Commit**

```bash
git add plugins/sharepoint-page-modernization/skills/convert-aspx-pages/SKILL.md plugins/sharepoint-page-modernization/README.md
git commit -m "docs(sharepoint-page-modernization): name sharepoint-content-publication as the deployment owner"
```

---

## Task 6: Final cross-plugin verification

**Files:** none (verification only)

- [ ] **Step 1: Confirm no plugin/skill directories were renamed**

```bash
git status --short plugins/sharepoint-provisioning plugins/sharepoint-migration-planning plugins/sharepoint-page-modernization plugins/sharepoint-content-publication
```
Expected: only new files and modified `SKILL.md`/`README.md`/`symlinks.json` — no `R ` (rename)
lines, no deletions.

- [ ] **Step 2: Confirm every new `.ps1` parses**

```bash
for f in plugins/sharepoint-migration-planning/scripts/spo-update-site-column.ps1 \
         plugins/sharepoint-migration-planning/scripts/spo-remove-site-column.ps1 \
         plugins/sharepoint-migration-planning/scripts/spo-update-content-type.ps1 \
         plugins/sharepoint-migration-planning/scripts/spo-remove-content-type.ps1 \
         plugins/sharepoint-migration-planning/scripts/spo-detach-content-type-from-list.ps1; do
  pwsh -NoProfile -Command "[System.Management.Automation.Language.Parser]::ParseFile('$f', [ref]\$null, [ref]\$null) | Out-Null; Write-Output '$f OK'"
done
```
Expected: five `OK` lines.

- [ ] **Step 3: Confirm the new skill's symlinks are all real and resolvable**

```bash
find plugins/sharepoint-migration-planning/skills/apply-sharepoint-provisioning-plan -type l | while read -r f; do test -e "$f" && echo "OK: $f" || echo "BROKEN: $f"; done
```
Expected: nine `OK:` lines, zero `BROKEN:`.

- [ ] **Step 4: Confirm existing Python test suites still pass (nothing here touches Python, this is a regression guard)**

```bash
cd plugins/sharepoint-provisioning && python -m pytest -q
cd ../sharepoint-migration-planning && python -m pytest -q
```
Expected: all existing tests still pass (this plan added no Python changes, so this should be a
no-op confirmation).

- [ ] **Step 5: Commit any final fixups only if Steps 1-4 found something to fix; otherwise no commit needed for this task**

---

## Task 7: Cross-reference `sharepoint-discovery`'s schema-export producer from `sharepoint-schema`

**Context:** `sharepoint-discovery/scripts/collect-sharepoint-schema-export.ps1`'s own docstring
confirms it exists specifically to produce the directory-tree shape
`sharepoint-schema/scripts/schema_export.py`'s `load_schema_export`/`ExportLayout` expects
(`<OutputDir>/summary/lists.json`, `<OutputDir>/lists/<listname>/fields.json`, etc.) — a real,
already-working producer/consumer pair. Confirmed by grep: none of `sharepoint-schema`'s five
`SKILL.md` files (`audit-schema`, `diff-sharepoint-schema`, `extract-calculated-columns`,
`extract-choice-fields`, `generate-sharepoint-schema-from-export`) name `sharepoint-discovery` or
`collect-sharepoint-schema-export.ps1` anywhere, despite each one consuming "an exported schema" as
input. Same undiscoverable-handoff pattern as Tasks 4/5, different plugin pair. (For contrast,
`sharepoint-content-publication`'s skills already do this correctly — `publish-markdown-to-sharepoint`,
`rollback-sharepoint-publication`, and `validate-sharepoint-publication` all name their real executor
script explicitly; only this producer/consumer pair across `sharepoint-discovery`/`sharepoint-schema`
was found undocumented. `reconcile-sharepoint-publication` and `publish-aspx-to-sharepoint` were
checked and are correctly package-only/already cross-referenced — no action needed there.)

**Files:**
- Modify: `plugins/sharepoint-schema/skills/audit-schema/SKILL.md`
- Modify: `plugins/sharepoint-schema/skills/diff-sharepoint-schema/SKILL.md`
- Modify: `plugins/sharepoint-schema/skills/extract-calculated-columns/SKILL.md`
- Modify: `plugins/sharepoint-schema/skills/extract-choice-fields/SKILL.md`
- Modify: `plugins/sharepoint-schema/skills/generate-sharepoint-schema-from-export/SKILL.md`

**Interfaces:**
- Consumes: `sharepoint-discovery`'s `collect-sharepoint-inventory` skill name and
  `collect-sharepoint-schema-export.ps1` script name (both already exist, unmodified by this task).
- Produces: nothing new — prose-only edits.

- [ ] **Step 1: Add an "Input source" note to each of the five `SKILL.md` files**

Insert immediately under each file's `## Trigger and Purpose` (or equivalent opening) section:

```markdown
## Where the exported schema comes from

This skill consumes an already-exported schema directory tree
(`<dir>/summary/lists.json`, `<dir>/lists/<listname>/fields.json`, etc. — see
`schema_export.py`'s `ExportLayout`). That tree is produced by
`sharepoint-discovery`'s `collect-sharepoint-inventory` skill running
`collect-sharepoint-schema-export.ps1` against a live tenant — this plugin
never connects to a tenant itself. Run that script first if you don't
already have an export directory.
```

- [ ] **Step 2: Verify all five files reference `sharepoint-discovery`**

```bash
grep -rl "sharepoint-discovery" plugins/sharepoint-schema/skills/*/SKILL.md
```
Expected: five file paths printed.

- [ ] **Step 3: Commit**

```bash
git add plugins/sharepoint-schema/skills/*/SKILL.md
git commit -m "docs(sharepoint-schema): cross-reference sharepoint-discovery as the schema-export producer"
```
