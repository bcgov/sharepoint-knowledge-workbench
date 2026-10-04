<#
.SYNOPSIS
Real PnP executor for whole-schema list/library provisioning -- creates and
(only when explicitly opted into recreate) deletes+recreates lists from a
plan JSON matching sharepoint-site-build-and-publish's list_provisioning.py
ProvisioningPlan shape.

.DESCRIPTION
list_provisioning.py's plan_provisioning is pure planning -- it aggregates
field_provisioning/content_type_provisioning sub-plans together with
list-level create/delete planning into one reviewable ProvisioningPlan, and
detect_duplicate_lists runs before any deletion step is even planned. This
script is the real tenant-facing counterpart for the plan's list-level
`list_creations`/`list_deletions` steps specifically -- see
spo-provision-site-columns.ps1 and spo-provision-content-types.ps1 for the
field-level and content-type-level executors this plan's other write items
(`field_actions`, `content_type_actions`) are submitted through.

Plan JSON shape (matches ProvisioningPlan.to_dict() field names exactly --
this script consumes the plan's `list_creations`/`list_deletions`/
`blocking_findings`/`confirmation_token` fields verbatim, no augmentation
needed since ListCreation/ListDeletion already carry every field a list
create/delete cmdlet needs):

    {
      "outcome": "OBSERVED",
      "confirmation_token": "APPLY-2-abcdef0123456789",
      "field_actions": [],
      "content_type_actions": [],
      "list_creations": [
        { "title": "Case Files", "detail": "create 'Case Files' (template 100)" }
      ],
      "list_deletions": [],
      "blocking_findings": []
    }

Duplicate-title safety gate (non-optional core safety contract, per
list_provisioning.py's own `_gate`/`DuplicateListsBlockProvisioning`): this
script checks `plan.blocking_findings` BEFORE processing ANY
`list_deletions` entry (which is where `recreate=True` lists are deleted
ahead of their recreation) and refuses the entire run outright if the array
is non-empty -- not a per-item skip, a whole-plan refusal, mirroring the
Python module's own unconditional gate exactly ("a plan carrying a
duplicate-title finding is FAILED -- it can never be executed, not even a
partial subset of it", per the plugin README). `list_creations` for
titles that have no matching `list_deletions` entry (plain create-if-
missing, no recreate involved) are still processed even if unrelated
blocking findings exist elsewhere in the plan, EXCEPT that this script
takes the stricter whole-plan reading the README uses ("never, not even a
partial subset") and refuses the entire plan if any blocking finding is
present, for any title.

Template resolution: `list_creations`/`list_deletions` entries carry only a
`title` and a human-readable `detail` string (ListCreation.to_dict() has no
`template` field of its own -- template is embedded in `detail`'s text,
e.g. "create 'X' (template 100)", and in the *separate* schema definition
the plan was built from, not on ListCreation itself). This script therefore
requires the caller's plan JSON to carry the template as an explicit
`template` field on each list_creations entry (this script's own contract,
same augmentation pattern as spo-provision-content-types.ps1's `field_name`)
-- if a list_creations entry has no `template`, this script defaults to 100
(Generic List), matching list_provisioning.ListDef's own default.

Cmdlet sequence, evidenced against the source repo's list-helpers.ps1
(New-ListSafe/New-LibrarySafe): New-PnPList -Title <title> -Template
<template> -Description <description>, followed by a post-create
Get-PnPList verification (this script's equivalent of
verify_deletion_complete's fail-loud discipline, applied symmetrically to
creation). Deletion uses Remove-PnPList -Identity <title> -Force, followed
by a Get-PnPList re-check; if the object is still observed to exist after
deletion this script calls out to `verify_deletion_complete`'s exact
Python-side contract by construction (fail loud, do not report success).

By default performs no SharePoint tenant I/O; -Execute plus -ConfirmToken
PROVISION-SPO-LIST runs the real writes.

.PARAMETER PlanPath
Path to the plan JSON file (see .DESCRIPTION for the required shape).

.PARAMETER OutputPath
If set, writes the result JSON to this path in addition to stdout.

.PARAMETER SiteUrl
Overrides config.psd1 Connection.SiteUrl.

.PARAMETER ConfigPath
Path to config.psd1. Defaults to the repository root config.psd1.

.PARAMETER ClientId
Overrides ConfigPath ClientId.

.PARAMETER TenantId
Overrides ConfigPath TenantId.

.PARAMETER TenantAdminUrl
Overrides ConfigPath Authentication.TenantAdminUrl.

.PARAMETER Execute
Runs the real New-PnPList/Remove-PnPList calls. Omit this to print a
per-list action plan only -- no tenant I/O.

.PARAMETER ConfirmToken
Required with -Execute. Must be PROVISION-SPO-LIST.

.EXAMPLE
.\spo-provision-list.ps1 -PlanPath plan.json -SiteUrl "https://tenant.sharepoint.com/sites/Test" -Execute -ConfirmToken PROVISION-SPO-LIST
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$PlanPath,

    [string]$OutputPath,

    [string]$SiteUrl,

    [string]$ConfigPath = (Join-Path $PSScriptRoot "..\..\..\config.psd1"),

    [string]$ClientId,

    [string]$TenantId,

    [string]$TenantAdminUrl,

    [switch]$Execute,

    [string]$ConfirmToken
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

. (Join-Path $PSScriptRoot "Get-WorkbenchConnectionConfig.ps1")

$connectionConfig = Get-WorkbenchConnectionConfig -Path $ConfigPath
if (-not $SiteUrl) { $SiteUrl = $connectionConfig.SiteUrl }
if (-not $ClientId) { $ClientId = $connectionConfig.ClientId }
if (-not $TenantId) { $TenantId = $connectionConfig.TenantId }
if (-not $TenantAdminUrl) { $TenantAdminUrl = $connectionConfig.TenantAdminUrl }

if (-not (Test-Path -LiteralPath $PlanPath)) {
    throw "PlanPath '$PlanPath' does not exist."
}
$plan = Get-Content -LiteralPath $PlanPath -Raw | ConvertFrom-Json

# Non-optional core safety contract: a plan carrying ANY blocking finding
# (duplicate-titled lists) can never be executed, not even a partial subset
# of it -- checked BEFORE any list_deletions/list_creations processing,
# matching list_provisioning.py's own unconditional _gate check exactly.
$blockingFindings = @($plan.blocking_findings)
if ($blockingFindings.Count -gt 0) {
    $refusal = [ordered]@{
        outcome           = "FAILED"
        dry_run           = -not $Execute
        refused           = $true
        blocking_findings = $blockingFindings
        message           = "REFUSED: plan carries blocking findings (duplicate-titled lists) and cannot be executed, even in dry-run preview, until resolved -- see list_provisioning.py's DuplicateListsBlockProvisioning."
    }
    $refusalJson = $refusal | ConvertTo-Json -Depth 8
    $refusalJson
    if ($OutputPath) { Set-Content -LiteralPath $OutputPath -Value $refusalJson -Encoding UTF8 }
    throw "Plan at '$PlanPath' carries blocking findings and cannot be executed: $($blockingFindings -join '; ')"
}

$creations = @($plan.list_creations)
$deletions = @($plan.list_deletions)

if ($creations.Count -eq 0 -and $deletions.Count -eq 0) {
    $emptyResult = [ordered]@{
        outcome  = "EMPTY"
        dry_run  = -not $Execute
        created  = @()
        deleted  = @()
        failed   = @()
    }
    $emptyJson = $emptyResult | ConvertTo-Json -Depth 8
    $emptyJson
    if ($OutputPath) { Set-Content -LiteralPath $OutputPath -Value $emptyJson -Encoding UTF8 }
    return
}

if ($Execute) {
    if ($ConfirmToken -ne "PROVISION-SPO-LIST") {
        throw "-Execute requires -ConfirmToken PROVISION-SPO-LIST."
    }
    if (-not $SiteUrl -or -not $ClientId -or -not $TenantId) {
        throw "SiteUrl/ClientId/TenantId not resolved. Provide -SiteUrl/-ClientId/-TenantId or a valid -ConfigPath."
    }
    if (-not (Get-Command New-PnPList -ErrorAction SilentlyContinue) -or
        -not (Get-Command Get-PnPList -ErrorAction SilentlyContinue)) {
        throw "PnP.PowerShell with New-PnPList/Get-PnPList is required. Install/import PnP.PowerShell before executing."
    }

    $connectParameters = @{
        Url         = $SiteUrl
        ClientId    = $ClientId
        Tenant      = $TenantId
        Interactive = $true
    }
    if ($TenantAdminUrl) { $connectParameters["TenantAdminUrl"] = $TenantAdminUrl }
    Connect-PnPOnline @connectParameters

    $deleted = @()
    $created = @()
    $failed = @()

    # Deletions first -- a recreate=True list's plan always pairs a deletion
    # with a following creation of the same title.
    foreach ($deletion in $deletions) {
        try {
            Remove-PnPList -Identity $deletion.title -Force -ErrorAction Stop
            $stillExists = $null -ne (Get-PnPList -Identity $deletion.title -ErrorAction SilentlyContinue)
            if ($stillExists) {
                throw "'$($deletion.title)' still exists after deletion -- fail loud, do not assume success (see verify_deletion_complete)."
            }
            $deleted += [ordered]@{ title = $deletion.title; reason = $deletion.reason }
        }
        catch {
            $failed += [ordered]@{ title = $deletion.title; step = "delete"; error = $_.Exception.Message }
        }
    }

    foreach ($creation in $creations) {
        try {
            $template = if (Get-Member -InputObject $creation -Name "template" -ErrorAction SilentlyContinue) { [int]$creation.template } else { 100 }
            $description = if (Get-Member -InputObject $creation -Name "description" -ErrorAction SilentlyContinue) { $creation.description } else { "" }
            New-PnPList -Title $creation.title -Template $template -ErrorAction Stop | Out-Null
            if ($description) {
                Set-PnPList -Identity $creation.title -Description $description -ErrorAction Stop | Out-Null
            }
            $check = Get-PnPList -Identity $creation.title -ErrorAction SilentlyContinue
            if (-not $check) {
                throw "list creation verification failed: '$($creation.title)' not found after create"
            }
            $created += [ordered]@{ title = $creation.title; detail = $creation.detail }
        }
        catch {
            $failed += [ordered]@{ title = $creation.title; step = "create"; error = $_.Exception.Message }
        }
    }

    if (($created.Count -eq 0 -and $deleted.Count -eq 0) -and $failed.Count -gt 0) {
        $outcome = "FAILED"
    }
    elseif ($failed.Count -gt 0) {
        $outcome = "PARTIAL"
    }
    else {
        $outcome = "OBSERVED"
    }

    $result = [ordered]@{
        outcome = $outcome
        dry_run = $false
        created = $created
        deleted = $deleted
        failed  = $failed
    }

    $resultJson = $result | ConvertTo-Json -Depth 8
    $resultJson
    if ($OutputPath) { Set-Content -LiteralPath $OutputPath -Value $resultJson -Encoding UTF8 }
}
else {
    $deletionPlans = foreach ($deletion in $deletions) {
        [ordered]@{ title = $deletion.title; reason = $deletion.reason; action = "Remove-PnPList -Identity `"$($deletion.title)`" -Force" }
    }
    $creationPlans = foreach ($creation in $creations) {
        $template = if (Get-Member -InputObject $creation -Name "template" -ErrorAction SilentlyContinue) { [int]$creation.template } else { 100 }
        [ordered]@{ title = $creation.title; detail = $creation.detail; action = "New-PnPList -Title `"$($creation.title)`" -Template $template" }
    }

    $summary = [ordered]@{
        operation = "provision-spo-list"
        confirmation_token = $plan.confirmation_token
        deletion_count = $deletions.Count
        creation_count = $creations.Count
        site_url = $SiteUrl
        safety = [ordered]@{
            tenant_io = "none"
            execute_requires_confirm_token = "PROVISION-SPO-LIST"
            duplicate_title_gate = "plan.blocking_findings checked before any deletion/creation processing -- whole-plan refusal if non-empty"
        }
        deletions = $deletionPlans
        creations = $creationPlans
    }

    $summaryJson = $summary | ConvertTo-Json -Depth 8
    $summaryJson
    if ($OutputPath) { Set-Content -LiteralPath $OutputPath -Value $summaryJson -Encoding UTF8 }
}
