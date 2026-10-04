<#
.SYNOPSIS
Collects site chrome and navigation (top nav, quick launch, breadcrumb
ancestors, master page, logo) from a legacy on-premises SharePoint 2016 site
via REST + Windows-credential auth.

.DESCRIPTION
On-prem SharePoint (unlike modern SPO) has no Entra app-registration path in
general use here, so this script authenticates via NTLM/Kerberos --
Invoke-RestMethod/Invoke-WebRequest with -UseDefaultCredentials or an
explicit -Credential -- not Connect-PnPOnline. This is a deliberate
divergence from this repo's standard PnP.PowerShell auth convention,
required because the target is on-prem SP2016. REST-only, no CSOM/PnP
module required.

Captures everything the master page provides that is shared across all pages
of the site:
  - Site title, logo URL, master page path, locale/time zone
  - Top navigation bar (with nested children)
  - Quick launch / left navigation (with nested children)
  - Breadcrumb ancestor chain (site hierarchy, walked from the URL path)

Writes navigation.json in the exact {topNav, quickLaunch} shape consumed by
this plugin's navigation_analysis.py (analyze-site-navigation skill), plus a
site-chrome.json with the fuller chrome record (title, logo, master page,
ancestors) for reference/reporting. Never fabricates data on partial
failure -- a REST call that fails leaves the corresponding section empty and
emits Write-Warning, it does not invent placeholder nodes.

.PARAMETER SiteUrl
The on-prem SP2016 site to inspect. Required (no hardcoded default).

.PARAMETER OutputDir
Directory to write navigation.json and site-chrome.json to. Defaults to
.\sharepoint-site-navigation-export relative to the current working
directory.

.PARAMETER UseDefaultCredentials
Use the current Windows session (Kerberos/NTLM pass-through). Requires VPN /
domain-joined. Without this switch, a credential prompt is shown.

.EXAMPLE
.\collect-sharepoint-site-navigation.ps1 -SiteUrl "https://sp2016.example.org/sites/Legacy" -UseDefaultCredentials

.EXAMPLE
.\collect-sharepoint-site-navigation.ps1 -SiteUrl "https://sp2016.example.org/sites/Legacy" -OutputDir .\nav-export -Credential (Get-Credential)
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$SiteUrl,

    [string]$OutputDir = ".\sharepoint-site-navigation-export",

    [switch]$UseDefaultCredentials,

    [System.Management.Automation.PSCredential]$Credential
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if (-not [System.IO.Path]::IsPathRooted($OutputDir)) {
    $OutputDir = Join-Path (Get-Location) $OutputDir
}
if (-not (Test-Path $OutputDir)) { New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null }

if (-not $UseDefaultCredentials -and -not $Credential) {
    $Credential = Get-Credential -Message "Credentials for $SiteUrl"
    if (-not $Credential) { throw "No credentials provided." }
}

Write-Host "Site   : $SiteUrl" -ForegroundColor White
Write-Host "Output : $OutputDir" -ForegroundColor White

function Invoke-SpRest {
    param([string]$Url)
    $params = @{ Uri = $Url; Headers = @{ Accept = 'application/json;odata=verbose' }; ErrorAction = 'Stop' }
    if ($UseDefaultCredentials) { $params.UseDefaultCredentials = $true } else { $params.Credential = $Credential }
    try {
        $response = Invoke-WebRequest @params
        return ($response.Content | ConvertFrom-Json)
    } catch {
        Write-Warning "REST call failed for $Url : $($_.Exception.Message)"
        return $null
    }
}

function Get-SafeProperty {
    param($Object, $PropertyName)
    if ($null -eq $Object) { return $null }
    $prop = $Object.PSObject.Properties[$PropertyName]
    if ($prop) { return $prop.Value }
    return $null
}

function Get-NavNodes {
    # Normalizes SP REST verbose OData navigation node trees (top nav / quick
    # launch) into a plain {title, url, children} shape, recursing into
    # Children at any depth.
    param([object]$Nodes)
    if (-not $Nodes) { return @() }

    $working = $Nodes
    $members = ($working | Get-Member -MemberType NoteProperty -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Name)
    if ($members -contains 'd')       { $working = $working.d; $members = ($working | Get-Member -MemberType NoteProperty -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Name) }
    if ($members -contains 'results') { $items = $working.results }
    elseif ($members -contains 'value') { $items = $working.value }
    elseif ($working -is [array])     { $items = $working }
    else                              { $items = @($working) }

    $result = @()
    foreach ($n in $items) {
        $node = [ordered]@{
            title    = Get-SafeProperty -Object $n -PropertyName 'Title'
            url      = Get-SafeProperty -Object $n -PropertyName 'Url'
            children = @()
        }
        $childrenProp = Get-SafeProperty -Object $n -PropertyName 'Children'
        if ($childrenProp) {
            try { $node.children = @(Get-NavNodes -Nodes $childrenProp) } catch { }
        }
        $result += $node
    }
    return $result
}

function Get-SiteAncestors {
    # Builds a breadcrumb chain by walking up the URL path one segment at a
    # time, calling _api/web at each level. Any unreachable ancestor is
    # skipped (with a warning), never fabricated.
    param([string]$SiteUrl)
    $uri = [Uri]$SiteUrl
    $segments = $uri.AbsolutePath.Trim('/') -split '/'
    $ancestors = @()
    $accumulated = ''
    foreach ($seg in $segments) {
        if ([string]::IsNullOrWhiteSpace($seg)) { continue }
        $accumulated += "/$seg"
        $ancestorUrl = "$($uri.Scheme)://$($uri.Host)$accumulated"
        $webInfo = Invoke-SpRest -Url "$ancestorUrl/_api/web?`$select=Title,Url,ServerRelativeUrl"
        if ($webInfo -and $webInfo.d) {
            $ancestors += [ordered]@{
                title             = $webInfo.d.Title
                url               = $webInfo.d.Url
                serverRelativeUrl = $webInfo.d.ServerRelativeUrl
            }
        }
    }
    return $ancestors
}

$baseUrl = $SiteUrl.TrimEnd('/')

Write-Host "`nFetching web properties (title, logo, master page)..." -ForegroundColor Cyan
$webProps = Invoke-SpRest -Url "$baseUrl/_api/web?`$select=Title,Url,ServerRelativeUrl,MasterUrl,CustomMasterUrl,SiteLogoUrl,QuickLaunchEnabled,Language,RegionalSettings/LocaleId,RegionalSettings/TimeZone/Description&`$expand=RegionalSettings/TimeZone"

$webData = [ordered]@{
    title               = if ($webProps) { $webProps.d.Title } else { $null }
    url                 = if ($webProps) { $webProps.d.Url } else { $null }
    serverRelativeUrl   = if ($webProps) { $webProps.d.ServerRelativeUrl } else { $null }
    masterPageUrl       = if ($webProps) { $webProps.d.MasterUrl } else { $null }
    customMasterPageUrl = if ($webProps) { $webProps.d.CustomMasterUrl } else { $null }
    siteLogoUrl         = if ($webProps) { $webProps.d.SiteLogoUrl } else { $null }
    language            = if ($webProps) { $webProps.d.Language } else { $null }
}
if ($webProps -and $webProps.d.RegionalSettings) {
    $webData.localeId  = $webProps.d.RegionalSettings.LocaleId
    $webData.timeZone  = $webProps.d.RegionalSettings.TimeZone.Description
}
Write-Host "  Site title  : $($webData.title)" -ForegroundColor DarkGray
Write-Host "  Master page : $($webData.masterPageUrl)" -ForegroundColor DarkGray

Write-Host "`nFetching top navigation..." -ForegroundColor Cyan
$topNavRaw = Invoke-SpRest -Url "$baseUrl/_api/web/navigation/topnavigationbar?`$expand=Children"
$topNav = @(Get-NavNodes -Nodes $topNavRaw)
Write-Host "  Top nav nodes    : $($topNav.Count)" -ForegroundColor Green

Write-Host "Fetching quick launch navigation..." -ForegroundColor Cyan
$quickLaunchRaw = Invoke-SpRest -Url "$baseUrl/_api/web/navigation/quicklaunch?`$expand=Children"
$quickLaunch = @(Get-NavNodes -Nodes $quickLaunchRaw)
Write-Host "  Quick launch nodes: $($quickLaunch.Count)" -ForegroundColor Green

Write-Host "Building breadcrumb ancestor chain..." -ForegroundColor Cyan
$ancestors = @(Get-SiteAncestors -SiteUrl $SiteUrl)
Write-Host "  Ancestors        : $($ancestors.Count)" -ForegroundColor Green

# navigation.json -- consumed directly by navigation_analysis.py (analyze-site-navigation)
$navigation = [ordered]@{
    topNav      = $topNav
    quickLaunch = $quickLaunch
}
$navPath = Join-Path $OutputDir "navigation.json"
$navigation | ConvertTo-Json -Depth 12 | Set-Content -Path $navPath -Encoding UTF8

# site-chrome.json -- fuller record (title, logo, master page, ancestors) for reference
$chrome = [ordered]@{
    collectedAt = (Get-Date).ToString('s')
    siteUrl     = $SiteUrl
    web         = $webData
    ancestors   = $ancestors
    topNav      = $topNav
    quickLaunch = $quickLaunch
}
$chromePath = Join-Path $OutputDir "site-chrome.json"
$chrome | ConvertTo-Json -Depth 12 | Set-Content -Path $chromePath -Encoding UTF8

Write-Host "`nComplete." -ForegroundColor Green
Write-Host "  navigation.json  : $navPath (feeds analyze-site-navigation)" -ForegroundColor Green
Write-Host "  site-chrome.json : $chromePath (title/logo/master page/ancestors)" -ForegroundColor Green
