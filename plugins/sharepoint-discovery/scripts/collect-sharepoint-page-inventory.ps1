<#
.SYNOPSIS
Collects a page inventory (Site Pages) from a live SharePoint Online site and
writes it as JSON in the shape page_inventory_analysis.py consumes.

.DESCRIPTION
Read-only. Connects interactively via PnP.PowerShell, enumerates the Site
Pages library, downloads each .aspx page's content, and detects legacy
Content Editor / Script Editor web parts by scanning the page markup.
Performs zero tenant writes.

.PARAMETER SiteUrl
Overrides config.psd1 Connection.SiteUrl.

.PARAMETER ConfigPath
Path to config.psd1. Defaults to the repository root config.psd1.

.PARAMETER ClientId
Overrides ConfigPath ClientId.

.PARAMETER TenantId
Overrides ConfigPath TenantId.

.PARAMETER TenantAdminUrl
Overrides ConfigPath Authentication.TenantAdminUrl. Not required for this
read-only, single-site operation -- present only so this script does not
silently diverge from the repo's standard PnP auth parameter set.

.PARAMETER IncludeListForms
When set, also scans each list's NewForm/EditForm/DispForm pages, not just
Site Pages library pages. Not yet implemented -- reserved for a follow-on
pass; currently a documented no-op.

.PARAMETER OutputPath
Where to write the resulting JSON array. Defaults to .\page-inventory.json.

.EXAMPLE
.\collect-sharepoint-page-inventory.ps1 -SiteUrl "https://tenant.sharepoint.com/sites/Test" -OutputPath ".\out\page-inventory.json"
#>

[CmdletBinding()]
param(
    [string]$SiteUrl,

    [string]$ConfigPath = (Join-Path $PSScriptRoot "..\..\..\config.psd1"),

    [string]$ClientId,

    [string]$TenantId,

    [string]$TenantAdminUrl,

    [switch]$IncludeListForms,

    [string]$OutputPath = ".\page-inventory.json"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

. (Join-Path $PSScriptRoot "Get-WorkbenchConnectionConfig.ps1")

function Get-PageWebParts {
    [CmdletBinding()]
    param([Parameter(Mandatory = $true)][string]$PageContent)

    $webParts = @()
    $hasCewp = $PageContent -match 'ContentEditorWebPart'
    $hasSewp = $PageContent -match 'ScriptEditorWebPart'

    if ($PageContent -match 'ContentEditorWebPart[^>]*Title="([^"]*)"') {
        $webParts += [pscustomobject]@{ Category = "CEWP"; TypeName = "ContentEditorWebPart"; Title = $matches[1]; ListName = "" }
    }
    if ($PageContent -match 'ScriptEditorWebPart[^>]*Title="([^"]*)"') {
        $webParts += [pscustomobject]@{ Category = "SEWP"; TypeName = "ScriptEditorWebPart"; Title = $matches[1]; ListName = "" }
    }

    [pscustomobject]@{
        HasCEWP  = $hasCewp
        HasSEWP  = $hasSewp
        WebParts = $webParts
    }
}

$connectionConfig = Get-WorkbenchConnectionConfig -Path $ConfigPath
if (-not $SiteUrl) { $SiteUrl = $connectionConfig.SiteUrl }
if (-not $ClientId) { $ClientId = $connectionConfig.ClientId }
if (-not $TenantId) { $TenantId = $connectionConfig.TenantId }
if (-not $TenantAdminUrl) { $TenantAdminUrl = $connectionConfig.TenantAdminUrl }

if (-not $SiteUrl -or -not $ClientId -or -not $TenantId) {
    throw "SiteUrl/ClientId/TenantId not resolved. Provide -SiteUrl/-ClientId/-TenantId or a valid -ConfigPath."
}

$connectParameters = @{
    Url         = $SiteUrl
    ClientId    = $ClientId
    Tenant      = $TenantId
    Interactive = $true
}
if ($TenantAdminUrl) { $connectParameters["TenantAdminUrl"] = $TenantAdminUrl }
Connect-PnPOnline @connectParameters

$pages = @()
$siteRelativeUrl = (Get-PnPWeb -Includes ServerRelativeUrl).ServerRelativeUrl
$pageFiles = Get-PnPFolderItem -FolderSiteRelativeUrl "SitePages" -ItemType File

foreach ($file in $pageFiles) {
    if ($file.Name -notmatch '\.aspx$') { continue }
    $serverRelativeUrl = "$siteRelativeUrl/SitePages/$($file.Name)"
    $content = (Get-PnPFile -Url $serverRelativeUrl -AsString)
    $detection = Get-PageWebParts -PageContent $content

    $pages += [pscustomobject]@{
        FileName         = $file.Name
        Category         = "SitePage"
        ListTitle        = ""
        ConnectedWPCount = 0
        HasCEWP          = $detection.HasCEWP
        HasSEWP          = $detection.HasSEWP
        WebParts         = $detection.WebParts
    }
}

if ($IncludeListForms) {
    Write-Warning "-IncludeListForms is not yet implemented -- list NewForm/EditForm/DispForm pages were not scanned."
}

$pages | ConvertTo-Json -Depth 8 | Set-Content -Path $OutputPath -Encoding UTF8
Write-Host "Wrote $($pages.Count) page record(s) to $OutputPath" -ForegroundColor Green
Disconnect-PnPOnline -ErrorAction SilentlyContinue
