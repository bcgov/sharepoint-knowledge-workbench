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
    [string]$ConfigPath = (Join-Path $PSScriptRoot "..\..\..\config.psd1"),

    [string]$OutputPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

. (Join-Path $PSScriptRoot "Get-WorkbenchConnectionConfig.ps1")

$config = Get-WorkbenchConnectionConfig -Path $ConfigPath
if (-not $SiteUrl) { $SiteUrl = $config.SiteUrl }
if (-not $ClientId) { $ClientId = $config.ClientId }
if (-not $TenantId) { $TenantId = $config.TenantId }
if (-not $TenantAdminUrl) { $TenantAdminUrl = $config.TenantAdminUrl }

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
        $displayName = if ($action.PSObject.Properties.Name -contains 'display_name') { $action.display_name } else { $null }
        $description = if ($action.PSObject.Properties.Name -contains 'description') { $action.description } else { $null }
        [ordered]@{ content_type_name = $action.content_type_name; action = "Set-PnPContentType -Identity `"$($action.content_type_name)`" -NewName `"$displayName`" -Description `"$description`"" }
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
