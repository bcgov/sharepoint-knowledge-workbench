<#
.SYNOPSIS
Creates and publishes modern SharePoint Online pages from a publish plan.

.DESCRIPTION
Reads a PublishPlan JSON file (document_id, actions[]: source_path,
target_library, target_folder, target_filename) and, for each action,
creates a modern page via Add-PnPPage, injects the source_path file's
content into a text web part via Add-PnPPageTextPart, and publishes it via
Publish-PnPPage. By default performs no SharePoint tenant I/O; -Execute plus
-ConfirmToken UPLOAD-SPO-PLAN runs the real writes.

.PARAMETER PlanPath
Path to a PublishPlan JSON file matching PublishPlan.to_dict()'s shape.

.PARAMETER SiteUrl
Overrides config.psd1 Connection.SiteUrl. The site pages are created on.

.PARAMETER ConfigPath
Path to config.psd1. Defaults to the repository root config.psd1.

.PARAMETER ClientId
Overrides ConfigPath ClientId.

.PARAMETER TenantId
Overrides ConfigPath TenantId.

.PARAMETER TenantAdminUrl
Overrides ConfigPath Authentication.TenantAdminUrl.

.PARAMETER Overwrite
Removes an existing page at the target name before creating the new one.
Without this, an existing page at the target name causes the run to fail.

.PARAMETER Execute
Runs the real Add-PnPPage/Add-PnPPageTextPart/Publish-PnPPage calls. Omit
this to print the per-action plan only.

.PARAMETER ConfirmToken
Required with -Execute. Must be UPLOAD-SPO-PLAN.

.EXAMPLE
.\spo-upload-plan.ps1 -PlanPath plan.json -SiteUrl "https://tenant.sharepoint.com/sites/Test" -Execute -ConfirmToken UPLOAD-SPO-PLAN
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$PlanPath,

    [string]$SiteUrl,

    [string]$ConfigPath = (Join-Path $PSScriptRoot "..\..\..\config.psd1"),

    [string]$ClientId,

    [string]$TenantId,

    [string]$TenantAdminUrl,

    [switch]$Overwrite,

    [switch]$Execute,

    [string]$ConfirmToken
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-WorkbenchConnectionConfig {
    [CmdletBinding()]
    param([Parameter(Mandatory = $true)][string]$Path)

    if (-not (Test-Path -LiteralPath $Path)) {
        return [pscustomobject]@{ SiteUrl = $null; ClientId = $null; TenantId = $null; TenantAdminUrl = $null }
    }

    $rawConfig = Import-PowerShellDataFile -LiteralPath $Path
    $cfg = if ($rawConfig.Connection) { $rawConfig.Connection } else { $rawConfig }
    $tenantAdminUrl = if ($rawConfig.Authentication) { $rawConfig.Authentication.TenantAdminUrl } else { $rawConfig.TenantAdminUrl }

    [pscustomobject]@{
        SiteUrl        = $cfg.SiteUrl
        ClientId       = $cfg.ClientId
        TenantId       = $cfg.TenantId
        TenantAdminUrl = $tenantAdminUrl
    }
}

function Get-PageNameFromFileName {
    [CmdletBinding()]
    param([Parameter(Mandatory = $true)][string]$FileName)
    [System.IO.Path]::GetFileNameWithoutExtension($FileName)
}

$connectionConfig = Get-WorkbenchConnectionConfig -Path $ConfigPath
if (-not $SiteUrl) { $SiteUrl = $connectionConfig.SiteUrl }
if (-not $ClientId) { $ClientId = $connectionConfig.ClientId }
if (-not $TenantId) { $TenantId = $connectionConfig.TenantId }
if (-not $TenantAdminUrl) { $TenantAdminUrl = $connectionConfig.TenantAdminUrl }

if (-not $SiteUrl -or -not $ClientId -or -not $TenantId) {
    throw "SiteUrl/ClientId/TenantId not resolved. Provide -SiteUrl/-ClientId/-TenantId or a valid -ConfigPath."
}

if (-not (Test-Path -LiteralPath $PlanPath)) {
    throw "PlanPath '$PlanPath' does not exist."
}
$plan = Get-Content -LiteralPath $PlanPath -Raw | ConvertFrom-Json
if (-not $plan.actions -or $plan.actions.Count -eq 0) {
    throw "Plan at '$PlanPath' has no actions -- nothing to upload."
}

if ($Execute) {
    if ($ConfirmToken -ne "UPLOAD-SPO-PLAN") {
        throw "-Execute requires -ConfirmToken UPLOAD-SPO-PLAN."
    }
    if (-not (Get-Command Add-PnPPage -ErrorAction SilentlyContinue)) {
        throw "PnP.PowerShell with Add-PnPPage is required. Install/import PnP.PowerShell before executing."
    }

    $connectParameters = @{
        Url         = $SiteUrl
        ClientId    = $ClientId
        Tenant      = $TenantId
        Interactive = $true
    }
    if ($TenantAdminUrl) { $connectParameters["TenantAdminUrl"] = $TenantAdminUrl }
    Connect-PnPOnline @connectParameters

    $results = foreach ($action in $plan.actions) {
        $pageName = Get-PageNameFromFileName -FileName $action.target_filename
        if (-not (Test-Path -LiteralPath $action.source_path)) {
            throw "source_path '$($action.source_path)' does not exist -- refusing to create an empty page."
        }

        $existingPage = Get-PnPPage -Identity $pageName -ErrorAction SilentlyContinue
        if ($existingPage) {
            if (-not $Overwrite) {
                throw "Page '$pageName' already exists. Re-run with -Overwrite to replace it."
            }
            Remove-PnPPage -Identity $pageName -Force
        }

        $content = Get-Content -LiteralPath $action.source_path -Raw
        Add-PnPPage -Name $pageName -LayoutType Article | Out-Null
        Add-PnPPageTextPart -Page $pageName -Text $content | Out-Null
        Publish-PnPPage -Identity $pageName | Out-Null

        [pscustomobject]@{
            source_path = $action.source_path
            page_name   = $pageName
            success     = $true
        }
    }

    $results | ConvertTo-Json -Depth 8
}
else {
    $actionPlans = foreach ($action in $plan.actions) {
        $pageName = Get-PageNameFromFileName -FileName $action.target_filename
        [ordered]@{
            source_path = $action.source_path
            target_library = $action.target_library
            target_folder = $action.target_folder
            page_name = $pageName
            create_page = "Add-PnPPage -Name `"$pageName`" -LayoutType Article"
            inject_content = "Add-PnPPageTextPart -Page `"$pageName`" -Text (Get-Content -Raw `"$($action.source_path)`")"
            publish_page = "Publish-PnPPage -Identity `"$pageName`""
        }
    }

    $summary = [ordered]@{
        operation = "upload-spo-plan"
        document_id = $plan.document_id
        action_count = $plan.actions.Count
        site_url = $SiteUrl
        safety = [ordered]@{
            tenant_io = "none"
            execute_requires_confirm_token = "UPLOAD-SPO-PLAN"
        }
        actions = $actionPlans
    }

    $summary | ConvertTo-Json -Depth 8
}
