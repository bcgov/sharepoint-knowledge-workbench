<#
.SYNOPSIS
Real PnP executor for removing web part instances from modern SharePoint pages.

.DESCRIPTION
Same dry-run-by-default / -Execute + -ConfirmToken / Get-WorkbenchConnectionConfig.ps1
pattern as every other spo-provision-*.ps1 script in this plugin -- see that
script's own docstring for the full safety-gate rationale, not repeated here.
Wraps PnP.PowerShell's Remove-PnPPageComponent, which removes one control by
its exact InstanceId (a page-scoped GUID visible via Get-PnPPageComponent or
Get-PnPClientSidePage). Never targets a web part by title/type -- the caller
must supply the specific InstanceId(s) to remove, since titles/types are not
unique on a page (e.g. multiple "List" web parts on the same list/view).

Plan JSON shape:

    {
      "confirmation_token": "REMOVE-2-abcdef0123456789",
      "actions": [
        {
          "page_name": "Example_Page.aspx",
          "instance_id": "d5e80003-c15c-406a-aa59-7f6dc9557a1a"
        }
      ]
    }

.PARAMETER PlanPath
Path to the plan JSON described above.

.PARAMETER Execute
Runs the real Remove-PnPPageComponent call. Omit this to print a dry-run
action summary and take no tenant action.

.PARAMETER ConfirmToken
Must equal REMOVE-SPO-PAGE-WEBPART when -Execute is passed. Refused otherwise.

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
    if ($ConfirmToken -ne "REMOVE-SPO-PAGE-WEBPART") {
        throw "-Execute requires -ConfirmToken REMOVE-SPO-PAGE-WEBPART."
    }
    if (-not $SiteUrl -or -not $ClientId -or -not $TenantId) {
        throw "SiteUrl/ClientId/TenantId not resolved. Provide -SiteUrl/-ClientId/-TenantId or a valid -ConfigPath."
    }
    if (-not (Get-Command Remove-PnPPageComponent -ErrorAction SilentlyContinue)) {
        throw "PnP.PowerShell with Remove-PnPPageComponent is required. Install/import PnP.PowerShell before executing."
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
            Remove-PnPPageComponent -Page $action.page_name -InstanceId $action.instance_id -Force -ErrorAction Stop
            $updated += [ordered]@{ page_name = $action.page_name; instance_id = $action.instance_id }
        }
        catch {
            $failed += [ordered]@{ page_name = $action.page_name; instance_id = $action.instance_id; error = $_.Exception.Message }
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
        $pageName = if ($action.PSObject.Properties.Name -contains 'page_name') { $action.page_name } else { $null }
        $instanceId = if ($action.PSObject.Properties.Name -contains 'instance_id') { $action.instance_id } else { $null }
        [ordered]@{
            page_name   = $pageName
            instance_id = $instanceId
            action      = "Remove-PnPPageComponent -Page `"$pageName`" -InstanceId `"$instanceId`""
        }
    }
    $summary = [ordered]@{
        operation           = "remove-spo-page-webpart"
        confirmation_token  = $plan.confirmation_token
        remove_count        = $plan.actions.Count
        site_url            = $SiteUrl
        safety              = [ordered]@{
            tenant_io                      = "none"
            execute_requires_confirm_token = "REMOVE-SPO-PAGE-WEBPART"
        }
        planned_actions     = $actionPlans
    }
    $summaryJson = $summary | ConvertTo-Json -Depth 8
    $summaryJson
    if ($OutputPath) { Set-Content -LiteralPath $OutputPath -Value $summaryJson -Encoding UTF8 }
}
