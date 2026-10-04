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
