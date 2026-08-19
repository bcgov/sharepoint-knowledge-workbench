<#
.SYNOPSIS
Real PnP executor for creating modern SharePoint Client-Side Pages and layout sections.

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
Must equal CREATE-SPO-MODERN-PAGE when -Execute is passed. Refused otherwise.

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
    if ($ConfirmToken -ne "CREATE-SPO-MODERN-PAGE") {
        throw "-Execute requires -ConfirmToken CREATE-SPO-MODERN-PAGE."
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
            $layout = if ($action.layout_type) { $action.layout_type } else { "Article" }
            Add-PnPPage -Name $action.page_name -LayoutType $layout -ErrorAction Stop | Out-Null
            if ($action.section_template) { Add-PnPPageSection -Page $action.page_name -SectionTemplate $action.section_template -ErrorAction Stop | Out-Null }
            $updated += [ordered]@{ page_name = $action.page_name }
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
        $displayName = if ($action.PSObject.Properties.Name -contains 'display_name') { $action.display_name } else { $null }
        $description = if ($action.PSObject.Properties.Name -contains 'description') { $action.description } else { $null }
        $required = if ($action.PSObject.Properties.Name -contains 'required') { [bool]$action.required } else { $false }
        [ordered]@{
            internal_name = $action.internal_name
            action        = "Set-PnPField -Identity `"$($action.internal_name)`" -Values @{Title=`"$displayName`"; Description=`"$description`"; Required=$required}"
        }
    }
    $summary = [ordered]@{
        operation           = "update-spo-site-columns"
        confirmation_token  = $plan.confirmation_token
        update_count        = $plan.actions.Count
        site_url            = $SiteUrl
        safety              = [ordered]@{
            tenant_io                      = "none"
            execute_requires_confirm_token = "CREATE-SPO-MODERN-PAGE"
        }
        planned_actions     = $actionPlans
    }
    $summaryJson = $summary | ConvertTo-Json -Depth 8
    $summaryJson
    if ($OutputPath) { Set-Content -LiteralPath $OutputPath -Value $summaryJson -Encoding UTF8 }
}

