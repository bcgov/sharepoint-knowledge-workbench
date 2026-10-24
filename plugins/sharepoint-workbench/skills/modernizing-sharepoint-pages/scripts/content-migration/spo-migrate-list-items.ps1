<#
.SYNOPSIS
Real PnP executor for item-level SharePoint list content migration --
creates (content pass) or updates (backfill pass) list items from a plan
JSON produced by item_migration.py's MigrationItem/MigrationPlan shapes.

.DESCRIPTION
item_migration.py's plan_item_migration/apply_item_migration are pure
planning + a gated apply that requires an injected executor(item) -> int
callable; this script is that executor's real tenant-facing counterpart,
invoked directly against a plan JSON file (Python cannot inject a
PowerShell callback across the process boundary).

Plan JSON shape (this script's own contract -- see "Design seam" below for
why this isn't simply MigrationItem.to_dict(), which doesn't exist):

    {
      "target_list": "TargetListName",
      "confirmation_token": "APPLY-3-1-abcdef0123456789",
      "batches": [
        [
          { "source_id": 101, "fields": { "Title": "Row 1" } },
          { "source_id": 102, "fields": { "Title": "Row 2" }, "dest_id": 55 }
        ]
      ]
    }

Each item has a `source_id` and a `fields` dict of already destination-
shaped field values (this script performs no field renaming or type
coercion beyond what -Values requires -- see item_migration.py's own
docstring: "this module has no schema knowledge and performs no field
renaming"). An item's presence/absence of `dest_id` selects the operation:

  - No `dest_id` (or null)  -> CREATE.  Non-batched
    `Add-PnPListItem -List $TargetList -Values $fields -ErrorAction Stop`
    is used (not `-Batch`) because `Add-PnPListItem -Batch` does not
    reliably return a usable lazy item reference in the installed
    PnP.PowerShell version -- confirmed against a source-repository
    migration library's own comment and non-batched fallback for exactly
    this reason. The real created item's `Id` becomes the result's
    `dest_id`, ready for `id_mapping.record_id_mapping`.
  - Present `dest_id`         -> BACKFILL (update). Calls
    `Set-PnPListItem -List $TargetList -Identity <dest_id> -Values $fields
    -ErrorAction Stop` -- used for pass 2, writing an already-resolved
    lookup field onto an item this same two-pass technique already
    created in an earlier content pass.

.DESCRIPTION (design seam -- read before assuming this maps 1:1 onto item_migration.py)
`item_migration.py`'s `MigrationItem` dataclass carries only `source_id`
and `fields` -- it has no `dest_id`/"is this a backfill" field, and
neither `MigrationItem` nor `ItemMigrationPlan` defines a `to_dict()`/
`from_dict()` serialization method (only `ItemMigrationResult` does). That
means this script's plan JSON is NOT a literal serialization of a Python
`ItemMigrationPlan` -- it is this script's own contract, shaped to carry
the one extra bit (`dest_id` presence) the Python module's own dataclass
doesn't represent. A caller producing this plan JSON from Python code
augments each item dict with `dest_id` itself (analogous to how
`spo-remediate-document-content-links.ps1` augments its plan with
`remediated_content` that `RemediationPlan.to_dict()` doesn't carry). This
was flagged rather than silently assumed away; changing `MigrationItem`
to natively carry an optional `dest_id` is a real, undone follow-up if a
caller wants the Python plan object itself to represent both passes.

Retry: each item gets at least one write attempt, always -- passing
-RetryAttempts 0 does NOT skip the item (that exact silent-drop bug was
already fixed on the Python side in `apply_item_migration`, which now
raises ValueError for retry_attempts < 1; this script instead clamps to a
minimum of 1 attempt so a 0 value can never silently drop an item here
either).

Result JSON matches `ItemMigrationResult.to_dict()`'s field names exactly
so a Python caller can feed `result.migrated` straight into
`record_id_mapping` without reshaping:

    {
      "outcome": "OBSERVED" | "PARTIAL" | "FAILED" | "EMPTY",
      "dry_run": false,
      "migrated": [ { "source_id": 101, "dest_id": 9001 }, ... ],
      "failed":   [ { "source_id": 102, "error": "..." }, ... ]
    }

By default performs no SharePoint tenant I/O; -Execute plus -ConfirmToken
MIGRATE-SPO-LIST-ITEMS runs the real writes.

.PARAMETER PlanPath
Path to the plan JSON file (see .DESCRIPTION for the required shape).

.PARAMETER TargetList
Overrides the plan's own `target_list`. Optional if the plan JSON already
carries `target_list`.

.PARAMETER RetryAttempts
Attempts per item before recording it as failed. Defaults to 1 (matching
`apply_item_migration`'s own default). A value below 1 is clamped to 1 --
every item always gets at least one real write attempt, never zero.

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
Runs the real Add-PnPListItem/Set-PnPListItem calls. Omit this to print a
per-item action plan only -- no tenant I/O.

.PARAMETER ConfirmToken
Required with -Execute. Must be MIGRATE-SPO-LIST-ITEMS.

.EXAMPLE
.\spo-migrate-list-items.ps1 -PlanPath plan.json -SiteUrl "https://tenant.sharepoint.com/sites/Test" -Execute -ConfirmToken MIGRATE-SPO-LIST-ITEMS
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$PlanPath,

    [string]$TargetList,

    [int]$RetryAttempts = 1,

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

if (-not $TargetList) { $TargetList = $plan.target_list }
if (-not $TargetList) {
    throw "TargetList not resolved. Provide -TargetList or a plan JSON with a top-level 'target_list'."
}

if (-not $plan.batches) {
    throw "Plan at '$PlanPath' has no batches -- nothing to migrate."
}

# Every item always gets at least one real write attempt -- a 0/negative
# value is clamped, never allowed to silently drop items (see .DESCRIPTION).
$effectiveRetryAttempts = [Math]::Max(1, $RetryAttempts)

$allItems = @()
foreach ($batch in $plan.batches) {
    foreach ($item in $batch) {
        $allItems += $item
    }
}

if ($allItems.Count -eq 0) {
    $emptyResult = [ordered]@{
        outcome  = "EMPTY"
        dry_run  = -not $Execute
        migrated = @()
        failed   = @()
    }
    $emptyJson = $emptyResult | ConvertTo-Json -Depth 8
    $emptyJson
    if ($OutputPath) { Set-Content -LiteralPath $OutputPath -Value $emptyJson -Encoding UTF8 }
    return
}

if ($Execute) {
    if ($ConfirmToken -ne "MIGRATE-SPO-LIST-ITEMS") {
        throw "-Execute requires -ConfirmToken MIGRATE-SPO-LIST-ITEMS."
    }
    if (-not $SiteUrl -or -not $ClientId -or -not $TenantId) {
        throw "SiteUrl/ClientId/TenantId not resolved. Provide -SiteUrl/-ClientId/-TenantId or a valid -ConfigPath."
    }
    if (-not (Get-Command Add-PnPListItem -ErrorAction SilentlyContinue) -or
        -not (Get-Command Set-PnPListItem -ErrorAction SilentlyContinue)) {
        throw "PnP.PowerShell with Add-PnPListItem/Set-PnPListItem is required. Install/import PnP.PowerShell before executing."
    }

    $connectParameters = @{
        Url         = $SiteUrl
        ClientId    = $ClientId
        Tenant      = $TenantId
        Interactive = $true
    }
    if ($TenantAdminUrl) { $connectParameters["TenantAdminUrl"] = $TenantAdminUrl }
    Connect-PnPOnline @connectParameters

    $migrated = @()
    $failed = @()

    foreach ($item in $allItems) {
        $sourceId = [int]$item.source_id
        $fields = @{}
        if ($item.fields) {
            foreach ($property in $item.fields.PSObject.Properties) {
                $fields[$property.Name] = $property.Value
            }
        }
        $isBackfill = ($null -ne (Get-Member -InputObject $item -Name "dest_id" -ErrorAction SilentlyContinue)) -and $null -ne $item.dest_id

        $lastError = $null
        $destId = $null

        for ($attempt = 1; $attempt -le $effectiveRetryAttempts; $attempt++) {
            try {
                if ($isBackfill) {
                    Set-PnPListItem -List $TargetList -Identity ([int]$item.dest_id) -Values $fields -ErrorAction Stop | Out-Null
                    $destId = [int]$item.dest_id
                }
                else {
                    $created = Add-PnPListItem -List $TargetList -Values $fields -ErrorAction Stop
                    $destId = [int]$created.Id
                }
                $lastError = $null
                break
            }
            catch {
                $lastError = $_.Exception.Message
            }
        }

        if ($null -eq $lastError) {
            $migrated += [ordered]@{ source_id = $sourceId; dest_id = $destId }
        }
        else {
            $failed += [ordered]@{ source_id = $sourceId; error = $lastError }
        }
    }

    if ($migrated.Count -eq 0 -and $failed.Count -gt 0) {
        $outcome = "FAILED"
    }
    elseif ($failed.Count -gt 0) {
        $outcome = "PARTIAL"
    }
    else {
        $outcome = "OBSERVED"
    }

    $result = [ordered]@{
        outcome  = $outcome
        dry_run  = $false
        migrated = $migrated
        failed   = $failed
    }

    $resultJson = $result | ConvertTo-Json -Depth 8
    $resultJson
    if ($OutputPath) { Set-Content -LiteralPath $OutputPath -Value $resultJson -Encoding UTF8 }
}
else {
    $actionPlans = foreach ($item in $allItems) {
        $isBackfill = ($null -ne (Get-Member -InputObject $item -Name "dest_id" -ErrorAction SilentlyContinue)) -and $null -ne $item.dest_id
        [ordered]@{
            source_id = $item.source_id
            operation = if ($isBackfill) { "backfill (update)" } else { "create" }
            action    = if ($isBackfill) {
                "Set-PnPListItem -List `"$TargetList`" -Identity $($item.dest_id) -Values <fields>"
            }
            else {
                "Add-PnPListItem -List `"$TargetList`" -Values <fields>"
            }
        }
    }

    $summary = [ordered]@{
        operation = "migrate-spo-list-items"
        target_list = $TargetList
        confirmation_token = $plan.confirmation_token
        item_count = $allItems.Count
        retry_attempts = $effectiveRetryAttempts
        site_url = $SiteUrl
        safety = [ordered]@{
            tenant_io = "none"
            execute_requires_confirm_token = "MIGRATE-SPO-LIST-ITEMS"
        }
        actions = $actionPlans
    }

    $summaryJson = $summary | ConvertTo-Json -Depth 8
    $summaryJson
    if ($OutputPath) { Set-Content -LiteralPath $OutputPath -Value $summaryJson -Encoding UTF8 }
}
