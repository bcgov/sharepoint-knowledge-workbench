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
.\spo-publish-modern-page.ps1 -PlanPath plan.json -SiteUrl "https://tenant.sharepoint.com/sites/Test" -Execute -ConfirmToken UPLOAD-SPO-PLAN
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

. (Join-Path $PSScriptRoot "Get-WorkbenchConnectionConfig.ps1")

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

# Contract guard: this executor injects each source_path file, unchanged, into an HTML text web part, so every
# action must point at a pre-rendered HTML fragment. A Markdown-source plan would publish raw Markdown as page text.
$planHasFormat = $plan.PSObject.Properties.Name -contains 'source_format'
if ($planHasFormat -and $plan.source_format -eq 'markdown') {
    throw "Plan at '$PlanPath' has source_format 'markdown'. spo-publish-modern-page.ps1 publishes pre-rendered HTML fragments only; build the plan from the renderer output with build_page_publish_plan_from_render (or publish Markdown files with spo-upload-file.ps1)."
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

    try {
        $results = foreach ($action in $plan.actions) {
            $basePageName = Get-PageNameFromFileName -FileName $action.target_filename
            $relativeFolder = ""
            if ($action.PSObject.Properties.Name -contains 'target_folder' -and $action.target_folder) {
                $folder = $action.target_folder.Replace('\', '/').Trim('/')
                if ($folder -match '^\.\.' -or $folder -match '/\.\.') {
                    throw "target_folder '$($action.target_folder)' contains invalid traversal characters."
                }
                if ($folder.ToLower().StartsWith('sitepages/')) {
                    $relativeFolder = $folder.Substring(10).Trim('/')
                }
                elseif ($folder.ToLower() -eq 'sitepages') {
                    $relativeFolder = ""
                }
                else {
                    $relativeFolder = $folder
                }
            }
            $pageIdentity = (@($relativeFolder, $basePageName) | Where-Object { $_ }) -join '/'

            try {
                if (-not (Test-Path -LiteralPath $action.source_path)) {
                    throw "source_path '$($action.source_path)' does not exist -- refusing to create an empty page."
                }

                $existingPage = Get-PnPPage -Identity $pageIdentity -ErrorAction SilentlyContinue
                if ($existingPage) {
                    if (-not $Overwrite) {
                        throw "Page '$pageIdentity' already exists. Re-run with -Overwrite to replace it."
                    }
                    Remove-PnPPage -Identity $pageIdentity -Force
                }

                $content = Get-Content -LiteralPath $action.source_path -Raw
                $pageTitle = if ($action.PSObject.Properties.Name -contains 'title' -and $action.title) { $action.title } else { $basePageName }
                Add-PnPPage -Name $pageIdentity -Title $pageTitle -LayoutType Article | Out-Null
                Add-PnPPageTextPart -Page $pageIdentity -Text $content | Out-Null
                Set-PnPPage -Identity $pageIdentity -Publish | Out-Null

                [pscustomobject]@{
                    source_path   = $action.source_path
                    page_name     = $basePageName
                    page_identity = $pageIdentity
                    success       = $true
                }
            }
            catch {
                [pscustomobject]@{
                    source_path   = $action.source_path
                    page_name     = $basePageName
                    page_identity = $pageIdentity
                    success       = $false
                    error         = $_.Exception.Message
                }
            }
        }

        $results | ConvertTo-Json -Depth 8
        $anyFailed = @($results | Where-Object { -not $_.success })
        if ($anyFailed.Count -gt 0) {
            exit 1
        }
    } finally {
        Disconnect-PnPOnline -ErrorAction SilentlyContinue
    }
}
else {
    $actionPlans = foreach ($action in $plan.actions) {
        $basePageName = Get-PageNameFromFileName -FileName $action.target_filename
        $relativeFolder = ""
        if ($action.PSObject.Properties.Name -contains 'target_folder' -and $action.target_folder) {
            $folder = $action.target_folder.Replace('\', '/').Trim('/')
            if ($folder.ToLower().StartsWith('sitepages/')) {
                $relativeFolder = $folder.Substring(10).Trim('/')
            }
            elseif ($folder.ToLower() -eq 'sitepages') {
                $relativeFolder = ""
            }
            else {
                $relativeFolder = $folder
            }
        }
        $pageIdentity = (@($relativeFolder, $basePageName) | Where-Object { $_ }) -join '/'
        # typed array assignment (not an if-expression) so a single reference is not unrolled to a scalar in the JSON
        [string[]]$mediaRefs = @()
        if ($action.PSObject.Properties.Name -contains 'media_refs') { $mediaRefs = [string[]]@($action.media_refs) }
        [ordered]@{
            source_path = $action.source_path
            target_library = $action.target_library
            target_folder = $action.target_folder
            page_name = $basePageName
            page_identity = $pageIdentity
            media_refs = $mediaRefs
            create_page = "Add-PnPPage -Name `"$pageIdentity`" -LayoutType Article"
            inject_content = "Add-PnPPageTextPart -Page `"$pageIdentity`" -Text (Get-Content -Raw `"$($action.source_path)`")"
            publish_page = "Set-PnPPage -Identity `"$pageIdentity`" -Publish"
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
