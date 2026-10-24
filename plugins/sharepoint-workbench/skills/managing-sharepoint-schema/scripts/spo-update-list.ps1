<#
.SYNOPSIS
Real PnP executor for list/library settings updates -- Set-PnPList against a
plan JSON's `actions` array. Companion to spo-provision-list.ps1 (create/
delete only) -- renaming a list or changing its versioning settings had no
PnP executor anywhere before this script (spo-provision-list.ps1 only sets
Description at create time).

.DESCRIPTION
Same dry-run-by-default / -Execute + -ConfirmToken / Get-WorkbenchConnectionConfig.ps1
pattern as every other spo-provision-*.ps1 script in this plugin.

Plan JSON shape:

    {
      "confirmation_token": "UPDATE-LIST-abc",
      "actions": [
        {
          "title": "Case Files",
          "new_title": "Case Files Archive",
          "description": "Renamed 2026-08-18",
          "enable_versioning": true
        }
      ]
    }

`new_title`, `description`, and `enable_versioning` are all optional per
action -- only the fields present are changed.

.PARAMETER PlanPath
Path to the plan JSON described above.

.PARAMETER Execute
Runs the real Set-PnPList call. Omit this to print a dry-run action summary
and take no tenant action.

.PARAMETER ConfirmToken
Must equal UPDATE-SPO-LIST when -Execute is passed. Refused otherwise.

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
    [string]$ConfigPath = (Join-Path $PSScriptRoot "..\..\..\config.psd1"),

    [string]$OutputPath
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
    throw "Plan file not found at '$PlanPath'."
}
$plan = Get-Content -LiteralPath $PlanPath -Raw | ConvertFrom-Json

if (-not $plan.actions -or $plan.actions.Count -eq 0) {
    $emptyResult = [ordered]@{
        outcome = "EMPTY"
        dry_run = -not $Execute
        updated = @()
        failed  = @()
    }
    $emptyJson = $emptyResult | ConvertTo-Json -Depth 8
    $emptyJson
    if ($OutputPath) { Set-Content -LiteralPath $OutputPath -Value $emptyJson -Encoding UTF8 }
    return
}

if ($Execute) {
    if ($ConfirmToken -ne "UPDATE-SPO-LIST") {
        throw "-Execute requires -ConfirmToken UPDATE-SPO-LIST."
    }
    if (-not $SiteUrl -or -not $ClientId -or -not $TenantId) {
        throw "SiteUrl/ClientId/TenantId not resolved. Provide -SiteUrl/-ClientId/-TenantId or a valid -ConfigPath."
    }
    if (-not (Get-Command Set-PnPList -ErrorAction SilentlyContinue)) {
        throw "PnP.PowerShell with Set-PnPList is required. Install/import PnP.PowerShell before executing."
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
            $setParameters = @{ Identity = $action.title; ErrorAction = "Stop" }
            if ($action.PSObject.Properties.Name -contains "new_title") { $setParameters["Title"] = $action.new_title }
            if ($action.PSObject.Properties.Name -contains "description") { $setParameters["Description"] = $action.description }
            if ($action.PSObject.Properties.Name -contains "enable_versioning") { $setParameters["EnableVersioning"] = [bool]$action.enable_versioning }
            Set-PnPList @setParameters | Out-Null
            $updated += [ordered]@{ title = $action.title }
        }
        catch {
            $failed += [ordered]@{ title = $action.title; error = $_.Exception.Message }
        }
    }

    $outcome = if ($updated.Count -eq 0 -and $failed.Count -gt 0) { "FAILED" }
        elseif ($failed.Count -gt 0) { "PARTIAL" }
        else { "OBSERVED" }

    $result = [ordered]@{ outcome = $outcome; dry_run = $false; updated = $updated; failed = $failed }
    $resultJson = $result | ConvertTo-Json -Depth 8
    $resultJson
    if ($OutputPath) { Set-Content -LiteralPath $OutputPath -Value $resultJson -Encoding UTF8 }
}
else {
    $newTitle = if ($null -ne $plan.actions -and $plan.actions.Count -gt 0) { $null } else { $null }
    $actionPlans = foreach ($action in $plan.actions) {
        $nt = if ($action.PSObject.Properties.Name -contains "new_title") { $action.new_title } else { $action.title }
        $desc = if ($action.PSObject.Properties.Name -contains "description") { $action.description } else { "" }
        $ver = if ($action.PSObject.Properties.Name -contains "enable_versioning") { [bool]$action.enable_versioning } else { $null }
        [ordered]@{
            title  = $action.title
            action = "Set-PnPList -Identity `"$($action.title)`" -Title `"$nt`" -Description `"$desc`" -EnableVersioning:$ver"
        }
    }
    $summary = [ordered]@{
        operation           = "update-spo-list"
        confirmation_token  = $plan.confirmation_token
        update_count        = $plan.actions.Count
        site_url            = $SiteUrl
        safety              = [ordered]@{ tenant_io = "none"; execute_requires_confirm_token = "UPDATE-SPO-LIST" }
        planned_actions     = $actionPlans
    }
    $summaryJson = $summary | ConvertTo-Json -Depth 8
    $summaryJson
    if ($OutputPath) { Set-Content -LiteralPath $OutputPath -Value $summaryJson -Encoding UTF8 }
}
