<#
.SYNOPSIS
Real PnP executor for adding a layout section to an EXISTING modern SharePoint page.

.DESCRIPTION
Same dry-run-by-default / -Execute + -ConfirmToken / Get-WorkbenchConnectionConfig.ps1
pattern as every other spo-provision-*.ps1 script in this plugin -- see that
script's own docstring for the full safety-gate rationale, not repeated here.
Wraps PnP.PowerShell's Add-PnPPageSection only -- unlike spo-create-modern-
page.ps1 (which always calls Add-PnPPage first and is for brand-new pages),
this script never creates or touches page existence, it only appends a
section to a page that already exists.

Verified accepted -SectionTemplate values (PnP.PowerShell docs, 2026-09-08):
OneColumn, OneColumnFullWidth, TwoColumn, ThreeColumn, TwoColumnLeft,
TwoColumnRight, OneColumnVerticalSection, TwoColumnVerticalSection,
ThreeColumnVerticalSection, TwoColumnLeftVerticalSection,
TwoColumnRightVerticalSection, FlexibleLayoutSection,
FlexibleLayoutVerticalSection. Only one vertical section is allowed per page.

Plan JSON shape:

    {
      "confirmation_token": "ADD-2-abcdef0123456789",
      "actions": [
        {
          "page_name": "Example_Page.aspx",
          "section_template": "TwoColumnLeftVerticalSection"
        }
      ]
    }

.PARAMETER PlanPath
Path to the plan JSON described above.

.PARAMETER Execute
Runs the real Add-PnPPageSection call. Omit this to print a dry-run action
summary and take no tenant action.

.PARAMETER ConfirmToken
Must equal ADD-SPO-PAGE-SECTION when -Execute is passed. Refused otherwise.

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
    if ($ConfirmToken -ne "ADD-SPO-PAGE-SECTION") {
        throw "-Execute requires -ConfirmToken ADD-SPO-PAGE-SECTION."
    }
    if (-not $SiteUrl -or -not $ClientId -or -not $TenantId) {
        throw "SiteUrl/ClientId/TenantId not resolved. Provide -SiteUrl/-ClientId/-TenantId or a valid -ConfigPath."
    }
    if (-not (Get-Command Add-PnPPageSection -ErrorAction SilentlyContinue)) {
        throw "PnP.PowerShell with Add-PnPPageSection is required. Install/import PnP.PowerShell before executing."
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
            Add-PnPPageSection -Page $action.page_name -SectionTemplate $action.section_template -ErrorAction Stop | Out-Null
            $updated += [ordered]@{ page_name = $action.page_name; section_template = $action.section_template }
        }
        catch {
            $failed += [ordered]@{ page_name = $action.page_name; section_template = $action.section_template; error = $_.Exception.Message }
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
        $sectionTemplate = if ($action.PSObject.Properties.Name -contains 'section_template') { $action.section_template } else { $null }
        [ordered]@{
            page_name        = $pageName
            section_template = $sectionTemplate
            action           = "Add-PnPPageSection -Page `"$pageName`" -SectionTemplate `"$sectionTemplate`""
        }
    }
    $summary = [ordered]@{
        operation           = "add-spo-page-section"
        confirmation_token  = $plan.confirmation_token
        add_count           = $plan.actions.Count
        site_url            = $SiteUrl
        safety              = [ordered]@{
            tenant_io                      = "none"
            execute_requires_confirm_token = "ADD-SPO-PAGE-SECTION"
        }
        planned_actions     = $actionPlans
    }
    $summaryJson = $summary | ConvertTo-Json -Depth 8
    $summaryJson
    if ($OutputPath) { Set-Content -LiteralPath $OutputPath -Value $summaryJson -Encoding UTF8 }
}
