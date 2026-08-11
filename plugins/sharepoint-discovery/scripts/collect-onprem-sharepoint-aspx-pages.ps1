<#
.SYNOPSIS
Bulk-downloads .aspx page source (site pages, list forms, custom list forms,
root pages) from a legacy on-premises SharePoint 2016 site collection, across
all webs, for offline web-part/customization analysis.

.DESCRIPTION
On-prem SharePoint (unlike modern SPO) has no Entra app-registration path in
general use here, so this script authenticates via NTLM/Kerberos --
Invoke-RestMethod/Invoke-WebRequest with -UseDefaultCredentials or an
explicit -Credential -- not Connect-PnPOnline. This is a deliberate
divergence from this repo's standard PnP.PowerShell auth convention,
required because the target is on-prem SP2016.

Runs four phases across the site collection and every sub-web:
  1. Site Pages library pages.
  2. Standard list forms (NewForm.aspx / EditForm.aspx / DispForm.aspx /
     AllItems.aspx / view.aspx) that exist on each list.
  3. Non-standard .aspx files sitting in a list's own root folder (custom
     forms).
  4. .aspx files in each web's root folder (e.g. default.aspx).

Each downloaded file is flattened to a single local filename and skipped if
already present (safe to re-run/resume). Writes an aspx-manifest.json
recording category, source URL, and local filename for every downloaded
page.

.PARAMETER SiteUrl
The on-prem SP2016 site to scan. Required (no hardcoded default).

.PARAMETER OutputDir
Directory to write downloaded pages + manifest to. Defaults to
.\sharepoint-aspx-pages-export relative to the current working directory.

.PARAMETER UseDefaultCredentials
Use the current Windows session (Kerberos/NTLM pass-through). Requires VPN /
domain-joined. Without this switch, a credential prompt is shown.

.EXAMPLE
.\collect-onprem-sharepoint-aspx-pages.ps1 -SiteUrl "https://sp2016.example.org/sites/Legacy" -UseDefaultCredentials

.EXAMPLE
.\collect-onprem-sharepoint-aspx-pages.ps1 -SiteUrl "https://sp2016.example.org/sites/Legacy" -OutputDir .\aspx-export
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$SiteUrl,

    [string]$OutputDir = ".\sharepoint-aspx-pages-export",

    [switch]$UseDefaultCredentials
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if (-not [System.IO.Path]::IsPathRooted($OutputDir)) {
    $OutputDir = Join-Path (Get-Location) $OutputDir
}
if (-not (Test-Path $OutputDir)) { New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null }

Write-Host "Site   : $SiteUrl" -ForegroundColor White
Write-Host "Output : $OutputDir" -ForegroundColor White

$headers = @{ "Accept" = "application/json;odata=verbose" }
$cred = $null
if (-not $UseDefaultCredentials) {
    $cred = Get-Credential -Message "Credentials for $SiteUrl"
    if (-not $cred) { throw "No credentials provided." }
}

function Invoke-SP {
    param([string]$Url)
    try {
        if ($UseDefaultCredentials) {
            return Invoke-RestMethod -Uri $Url -Headers $headers -UseDefaultCredentials -ErrorAction Stop
        }
        return Invoke-RestMethod -Uri $Url -Headers $headers -Credential $cred -ErrorAction Stop
    } catch {
        Write-Verbose "REST error on $Url : $($_.Exception.Message)"
        return $null
    }
}

function Get-All {
    param([string]$Url)
    $all = [System.Collections.Generic.List[object]]::new()
    $nextUrl = $Url
    while ($nextUrl) {
        $r = Invoke-SP -Url $nextUrl
        if (-not $r) { break }
        $r.d.results | ForEach-Object { $all.Add($_) }
        $nextProp = $r.d.PSObject.Properties['__next']
        $nextUrl = if ($nextProp) { $nextProp.Value } else { $null }
    }
    return $all
}

function Download-Aspx {
    param([string]$ServerRelativeUrl)
    $safe = $ServerRelativeUrl.TrimStart("/") -replace "[/\\]", "_"
    $outFile = Join-Path $OutputDir $safe

    if (Test-Path $outFile) {
        Write-Verbose "  SKIP (exists): $safe"
        return $safe
    }

    $escapedRelUrl = $ServerRelativeUrl.Replace("'", "''")
    $downloadUrl = "$SiteUrl/_api/web/GetFileByServerRelativeUrl('$([Uri]::EscapeUriString($escapedRelUrl))')/`$value"
    try {
        if ($UseDefaultCredentials) {
            Invoke-WebRequest -Uri $downloadUrl -UseDefaultCredentials -OutFile $outFile -ErrorAction Stop | Out-Null
        } else {
            Invoke-WebRequest -Uri $downloadUrl -Credential $cred -OutFile $outFile -ErrorAction Stop | Out-Null
        }
        Write-Host "  [OK] $safe" -ForegroundColor DarkGray
        return $safe
    } catch {
        Write-Host "  [SKIP] $safe — $($_.Exception.Message)" -ForegroundColor DarkYellow
        return $null
    }
}

function Get-SPSubWebs {
    param([string]$WebUrl)
    $subwebs = @()
    $res = Get-All -Url "$WebUrl/_api/web/webs?`$select=Title,Url,ServerRelativeUrl"
    foreach ($w in $res) {
        $subwebs += $w
        $subwebs += Get-SPSubWebs -WebUrl $w.Url
    }
    return $subwebs
}

$webInfo = Invoke-SP -Url "$SiteUrl/_api/web?`$select=ServerRelativeUrl,Title,Url"
if (-not $webInfo) { throw "Could not connect to $SiteUrl" }
$allWebs = @($webInfo.d)
$subWebs = Get-SPSubWebs -WebUrl $SiteUrl
if ($subWebs) { $allWebs += $subWebs }

Write-Host "Discovered $($allWebs.Count) web(s) across site collection." -ForegroundColor Cyan

$manifest = [System.Collections.Generic.List[hashtable]]::new()

# Phase 1: Site Pages library across all webs.
Write-Host "`nPhase 1 — Site Pages libraries..." -ForegroundColor Cyan
$sitePageCount = 0
foreach ($w in $allWebs) {
    $pagesItems = Get-All -Url "$($w.Url)/_api/web/Lists/GetByTitle('Pages')/Items?`$select=FileRef,FileLeafRef&`$filter=substringof('.aspx',FileLeafRef)"
    foreach ($item in $pagesItems) {
        if (-not $item.FileRef) { continue }
        $fn = Download-Aspx -ServerRelativeUrl $item.FileRef
        if ($fn) {
            $sitePageCount++
            $manifest.Add(@{ Category = "SitePage"; ServerRelativeUrl = $item.FileRef; LocalFile = $fn; WebUrl = $w.Url })
        }
    }
}
Write-Host "  $sitePageCount site page(s) downloaded." -ForegroundColor Green

# Phase 2: Standard list forms across all webs.
Write-Host "`nPhase 2 — List forms..." -ForegroundColor Cyan
$formCount = 0
foreach ($w in $allWebs) {
    $lists = Get-All -Url "$($w.Url)/_api/web/Lists?`$select=Title,RootFolder/ServerRelativeUrl&`$expand=RootFolder&`$filter=Hidden eq false"
    foreach ($list in $lists) {
        $rootUrl = $list.RootFolder.ServerRelativeUrl
        foreach ($formName in @("NewForm.aspx", "EditForm.aspx", "DispForm.aspx", "AllItems.aspx", "view.aspx")) {
            $formUrl = "$rootUrl/Forms/$formName"
            $check = Invoke-SP -Url "$SiteUrl/_api/web/GetFileByServerRelativeUrl('$([Uri]::EscapeDataString($formUrl))')?`$select=Exists,Name"
            if ($check -and $check.d.Exists -eq $true) {
                $fn = Download-Aspx -ServerRelativeUrl $formUrl
                if ($fn) {
                    $formCount++
                    $manifest.Add(@{ Category = "ListForm"; ListTitle = $list.Title; FormType = $formName; ServerRelativeUrl = $formUrl; LocalFile = $fn; WebUrl = $w.Url })
                }
            }
        }
    }
}
Write-Host "  $formCount list form(s) downloaded." -ForegroundColor Green

# Phase 3: Non-standard .aspx in list root folders (custom forms) across all webs.
Write-Host "`nPhase 3 — Custom list .aspx files..." -ForegroundColor Cyan
$customCount = 0
foreach ($w in $allWebs) {
    $lists = Get-All -Url "$($w.Url)/_api/web/Lists?`$select=Title,RootFolder/ServerRelativeUrl&`$expand=RootFolder&`$filter=Hidden eq false"
    foreach ($list in $lists) {
        $rootUrl = $list.RootFolder.ServerRelativeUrl
        $escapedRoot = $rootUrl.Replace("'", "''")
        $files = Get-All -Url "$($w.Url)/_api/web/GetFolderByServerRelativeUrl('$([Uri]::EscapeUriString($escapedRoot))')/Files?`$select=Name,ServerRelativeUrl"
        foreach ($f in $files) {
            if ($f.Name -match '\.aspx$' -and $f.Name -notmatch '^(NewForm|EditForm|DispForm|AllItems|view)\.aspx$') {
                $fn = Download-Aspx -ServerRelativeUrl $f.ServerRelativeUrl
                if ($fn) {
                    $customCount++
                    $manifest.Add(@{ Category = "CustomForm"; ListTitle = $list.Title; ServerRelativeUrl = $f.ServerRelativeUrl; LocalFile = $fn; WebUrl = $w.Url })
                }
            }
        }
    }
}
Write-Host "  $customCount custom list .aspx file(s) downloaded." -ForegroundColor Green

# Phase 4: Root folder .aspx (e.g. default.aspx) across all webs.
Write-Host "`nPhase 4 — Web root .aspx files..." -ForegroundColor Cyan
$rootCount = 0
foreach ($w in $allWebs) {
    $rootFiles = Get-All -Url "$SiteUrl/_api/web/GetFolderByServerRelativeUrl('$([Uri]::EscapeDataString($w.ServerRelativeUrl))')/Files?`$select=Name,ServerRelativeUrl"
    foreach ($f in $rootFiles) {
        if ($f.Name -match '\.aspx$') {
            $fn = Download-Aspx -ServerRelativeUrl $f.ServerRelativeUrl
            if ($fn) {
                $rootCount++
                $manifest.Add(@{ Category = "RootPage"; ServerRelativeUrl = $f.ServerRelativeUrl; LocalFile = $fn; WebUrl = $w.Url })
            }
        }
    }
}
Write-Host "  $rootCount root .aspx file(s) downloaded." -ForegroundColor Green

$manifestPath = Join-Path $OutputDir "aspx-manifest.json"
$manifest | ConvertTo-Json -Depth 5 | Set-Content -Path $manifestPath -Encoding UTF8

Write-Host "`nComplete. Total files downloaded: $($manifest.Count)" -ForegroundColor Green
Write-Host "Manifest: $manifestPath" -ForegroundColor Green
