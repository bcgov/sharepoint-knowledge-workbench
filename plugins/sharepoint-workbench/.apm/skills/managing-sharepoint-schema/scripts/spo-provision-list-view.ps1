<#
.SYNOPSIS
Real PnP executor for custom SharePoint list view provisioning.

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
Must equal PROVISION-SPO-LIST-VIEW when -Execute is passed. Refused otherwise.

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
        skipped = @()
        failed  = @()
    }
    $emptyJson = $emptyResult | ConvertTo-Json -Depth 8
    $emptyJson
    if ($OutputPath) { Set-Content -LiteralPath $OutputPath -Value $emptyJson -Encoding UTF8 }
    return
}

if ($Execute) {
    if ($ConfirmToken -ne "PROVISION-SPO-LIST-VIEW") {
        throw "-Execute requires -ConfirmToken PROVISION-SPO-LIST-VIEW."
    }
    if (-not $SiteUrl -or -not $ClientId -or -not $TenantId) {
        throw "SiteUrl/ClientId/TenantId not resolved. Provide -SiteUrl/-ClientId/-TenantId or a valid -ConfigPath."
    }
    if (-not (Get-Command Add-PnPView -ErrorAction SilentlyContinue)) {
        throw "PnP.PowerShell with Add-PnPView is required. Install/import PnP.PowerShell before executing."
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

    try {
        foreach ($action in $plan.actions) {
            try {
                $existingView = Get-PnPView -List $action.list_title -Identity $action.view_title -ErrorAction SilentlyContinue
                if ($existingView) {
                    if ($action.fields) {
                        Set-PnPView -List $action.list_title -Identity $action.view_title -Fields $action.fields -ErrorAction Stop | Out-Null
                    }
                    if ($action.query) {
                        $existingView.ViewQuery = $action.query
                        $existingView.Update()
                        Invoke-PnPQuery
                    }
                    if ($action.set_as_default) {
                        Set-PnPView -List $action.list_title -Identity $action.view_title -SetAsDefault -ErrorAction Stop | Out-Null
                    }
                    $updated += [ordered]@{ view_title = $action.view_title; action = "updated" }
                } else {
                    $viewParams = @{ List = $action.list_title; Title = $action.view_title; SetAsDefault = [bool]$action.set_as_default; ErrorAction = "Stop" }
                    if ($action.fields) { $viewParams["Fields"] = $action.fields }
                    if ($action.query) { $viewParams["Query"] = $action.query }
                    if ($action.row_limit) { $viewParams["RowLimit"] = [uint32]$action.row_limit }
                    Add-PnPView @viewParams | Out-Null
                    $updated += [ordered]@{ view_title = $action.view_title; action = "created" }
                }
            }
            catch {
                $failed += [ordered]@{ list_title = $action.list_title; view_title = $action.view_title; error = $_.Exception.Message }
            }
        }
    } finally {
        Disconnect-PnPOnline -ErrorAction SilentlyContinue
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
        $listTitle = if ($action.PSObject.Properties.Name -contains 'list_title') { $action.list_title } else { $null }
        $viewTitle = if ($action.PSObject.Properties.Name -contains 'view_title') { $action.view_title } else { $null }
        [ordered]@{
            list_title = $listTitle
            view_title = $viewTitle
            action     = "Add-PnPView -List `"$listTitle`" -Title `"$viewTitle`""
        }
    }
    $summary = [ordered]@{
        operation           = "provision-spo-list-views"
        confirmation_token  = $plan.confirmation_token
        provision_count     = $plan.actions.Count
        site_url            = $SiteUrl
        safety              = [ordered]@{
            tenant_io                      = "none"
            execute_requires_confirm_token = "PROVISION-SPO-LIST-VIEW"
        }
        planned_actions     = $actionPlans
    }
    $summaryJson = $summary | ConvertTo-Json -Depth 8
    $summaryJson
    if ($OutputPath) { Set-Content -LiteralPath $OutputPath -Value $summaryJson -Encoding UTF8 }
}
