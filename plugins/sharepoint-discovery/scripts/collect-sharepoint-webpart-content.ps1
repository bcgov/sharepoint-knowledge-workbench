<#
.SYNOPSIS
Discovers and extracts classic Content Editor / Script Editor (and other)
web parts across a legacy on-premises SharePoint 2016 site, via REST +
Windows-credential auth.

.DESCRIPTION
On-prem SharePoint (unlike modern SPO) has no Entra app-registration path in
general use here, so this script authenticates via NTLM/Kerberos --
Invoke-RestMethod with -UseDefaultCredentials or an explicit -Credential --
not Connect-PnPOnline. This is a deliberate divergence from this repo's
standard PnP.PowerShell auth convention, required because the target is
on-prem SP2016.

Design note -- why one script with a -Mode switch instead of three:
the source material had two near-duplicate "scan" scripts (one that
recursively crawls every list/library/folder site-wide via GetFolderByUrl,
one that only enumerates the Pages library items) that both call the same
GetLimitedWebPartManager REST endpoint per page and differ only in *how
pages are discovered* and *how much per-web-part metadata is captured*.
Those are merged into a single Scan mode here, controlled by
-FullSiteCrawl: off (default) enumerates the Pages library only (fast,
covers the common case); on recursively crawls every list/library/folder
across all webs (thorough, finds pages living outside the Pages library --
list forms, root .aspx files -- at the cost of a much longer run). Content
extraction (the exportwp.aspx call that pulls the full HTML/JS payload) is
a genuinely separate concern -- it consumes Scan mode's own CSV output as
input -- so it stays a second mode rather than being folded into Scan.

Modes:
  Scan (default)  Enumerates pages (Pages library, or full site crawl with
                   -FullSiteCrawl) and queries GetLimitedWebPartManager for
                   every web part on every page, unfiltered by title/type
                   (title is author-editable and cannot reliably classify a
                   web part). Writes webpart-scan.csv and webpart-scan.json
                   -- one row per web part, with a best-effort Category
                   classification (ListView/CEWP/SEWP/ListForm/Other) plus
                   list binding for List View web parts.

  ExtractContent   Reads a webpart-scan.csv (this script's own Scan output,
                   or any CSV with PageUrl/WebPartId/WebPartTitle columns)
                   and calls the legacy _vti_bin/exportwp.aspx handler per
                   web part to pull its full, untruncated Content property
                   (the HTML/JS payload). The modern REST API does not
                   expose this at all -- ExportWebPart 404s regardless of
                   URL/verb/GUID formatting because the LimitedWebPartManager
                   REST wrapper never published that method; exportwp.aspx
                   (a plain-GET legacy handler) is the only working
                   mechanism on SP2016. Writes webpart-content.json in the
                   exact JSON-array shape consumed by this plugin's
                   webpart_code_analysis.py (analyze-webpart-code skill):
                   [{ PageUrl, WebPartId, WebPartTitle, Content }].

.PARAMETER SiteUrl
The on-prem SP2016 site to inspect. Required (no hardcoded default).

.PARAMETER OutputDir
Directory to write outputs to. Defaults to .\sharepoint-webpart-export
relative to the current working directory.

.PARAMETER Mode
Scan or ExtractContent. Defaults to Scan.

.PARAMETER FullSiteCrawl
Scan mode only. Recursively crawl every list/library/folder across all webs
instead of enumerating the Pages library only. Much slower; finds pages
living outside the Pages library.

.PARAMETER ScanCsvPath
ExtractContent mode only. Path to the webpart-scan.csv to read. Defaults to
webpart-scan.csv inside -OutputDir.

.PARAMETER UseDefaultCredentials
Use the current Windows session (Kerberos/NTLM pass-through). Requires VPN /
domain-joined. Without this switch, a credential prompt is shown.

.EXAMPLE
.\collect-sharepoint-webpart-content.ps1 -SiteUrl "https://sp2016.example.org/sites/Legacy" -UseDefaultCredentials

.EXAMPLE
.\collect-sharepoint-webpart-content.ps1 -SiteUrl "https://sp2016.example.org/sites/Legacy" -Mode Scan -FullSiteCrawl -UseDefaultCredentials

.EXAMPLE
.\collect-sharepoint-webpart-content.ps1 -SiteUrl "https://sp2016.example.org/sites/Legacy" -Mode ExtractContent -UseDefaultCredentials
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$SiteUrl,

    [string]$OutputDir = ".\sharepoint-webpart-export",

    [ValidateSet("Scan", "ExtractContent")]
    [string]$Mode = "Scan",

    [switch]$FullSiteCrawl,

    [string]$ScanCsvPath,

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
Write-Host "Mode   : $Mode" -ForegroundColor White

function Invoke-SP {
    param([string]$Url, [string]$Method = 'Get')
    $headers = @{ Accept = 'application/json;odata=verbose' }
    $bodyArg = if ($Method -eq 'Post') { @{ Body = '' } } else { @{} }
    try {
        if ($UseDefaultCredentials) {
            return Invoke-RestMethod -Uri $Url -Method $Method -Headers $headers -UseDefaultCredentials @bodyArg -ErrorAction Stop
        }
        return Invoke-RestMethod -Uri $Url -Method $Method -Headers $headers -Credential $Credential @bodyArg -ErrorAction Stop
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
        if ($r.d.results) { $r.d.results | ForEach-Object { $all.Add($_) } }
        $nextProp = $r.d.PSObject.Properties['__next']
        $nextUrl = if ($nextProp) { $nextProp.Value } else { $null }
    }
    return $all
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

function Get-WpCategory {
    param([string]$TypeName, [string]$Title)
    switch -Regex ("$TypeName|$Title") {
        "XsltListViewWebPart|ListViewWebPart" { return "ListView" }
        "ListFormWebPart"                      { return "ListForm" }
        "ContentEditorWebPart|Content Editor"  { return "CEWP" }
        "ScriptEditorWebPart|Script Editor"    { return "SEWP" }
        "PageViewerWebPart"                    { return "PageViewer" }
        "ImageWebPart"                         { return "Image" }
        "SummaryLinkWebPart"                   { return "SummaryLink" }
        default                                { return "Other" }
    }
}

# ============================================================
# MODE: Scan
# ============================================================
function Invoke-ScanMode {
    $allPages = [System.Collections.Generic.List[string]]::new()

    if ($FullSiteCrawl) {
        Write-Host "`nDiscovering all .aspx pages (full site crawl)..." -ForegroundColor Cyan
        $noDeepRecurseLibraries = @("Documents", "Images", "PublishingImages", "Drop Off Library", "Style Library", "SiteAssets")

        function Scan-FolderForPages {
            param([string]$FolderUrl, [string]$TargetWebUrl, [int]$Depth = 0)
            $pages = @()
            $leafName = ($FolderUrl -split '/')[-1]
            $encodedFolder = [Uri]::EscapeDataString($FolderUrl)

            $files = Get-All -Url "$TargetWebUrl/_api/web/GetFolderByServerRelativeUrl('$encodedFolder')/Files"
            foreach ($f in $files) {
                if ($f.Name -match '\.aspx$') { $pages += $f.ServerRelativeUrl }
            }

            if ($Depth -eq 1 -and $leafName -in $noDeepRecurseLibraries) { return $pages }

            $folders = Get-All -Url "$TargetWebUrl/_api/web/GetFolderByServerRelativeUrl('$encodedFolder')/Folders"
            foreach ($sub in $folders) {
                if ($sub.Name -match "^_") { continue }
                if ($sub.Name -in @("Forms", "Attachments")) { continue }
                $pages += Scan-FolderForPages -FolderUrl $sub.ServerRelativeUrl -TargetWebUrl $TargetWebUrl -Depth ($Depth + 1)
            }
            return $pages
        }

        $webInfo = Invoke-SP -Url "$SiteUrl/_api/web?`$select=ServerRelativeUrl,Title,Url"
        if (-not $webInfo) { throw "Could not connect to $SiteUrl" }
        $allWebs = @($webInfo.d)
        $allWebs += Get-SPSubWebs -WebUrl $SiteUrl
        Write-Host "  Discovered $($allWebs.Count) web(s)." -ForegroundColor Green

        foreach ($w in $allWebs) {
            $found = Scan-FolderForPages -FolderUrl $w.ServerRelativeUrl -TargetWebUrl $w.Url
            foreach ($p in $found) { $allPages.Add($p) }
        }
    } else {
        Write-Host "`nDiscovering pages (Pages library only)..." -ForegroundColor Cyan
        $pageItems = Get-All -Url "$SiteUrl/_api/web/Lists/GetByTitle('Pages')/Items?`$select=FileRef,FileLeafRef&`$orderby=FileLeafRef"
        foreach ($item in $pageItems) {
            if ($item.FileRef -match '\.aspx$') { $allPages.Add($item.FileRef) }
        }
    }

    $allPages = @($allPages | Select-Object -Unique)
    Write-Host "  Total pages to scan: $($allPages.Count)" -ForegroundColor Green

    Write-Host "`nQuerying Web Part Manager API per page..." -ForegroundColor Cyan
    $results = [System.Collections.Generic.List[object]]::new()
    $counter = 0
    foreach ($pageUrl in $allPages) {
        $counter++
        Write-Progress -Activity "Scanning pages" -Status $pageUrl -PercentComplete (($counter / [Math]::Max($allPages.Count, 1)) * 100)

        $encodedPageUrl = [Uri]::EscapeDataString($pageUrl)
        $wpApiUrl = "$SiteUrl/_api/web/GetFileByServerRelativeUrl('$encodedPageUrl')/GetLimitedWebPartManager(scope=1)/WebParts?`$expand=WebPart,WebPart/Properties"
        $wpResult = Invoke-SP -Url $wpApiUrl
        if (-not $wpResult -or -not $wpResult.d.results) { continue }

        foreach ($wp in $wpResult.d.results) {
            $title = ""; $typeName = ""; $listName = ""; $viewGuid = ""; $zone = ""; $zoneIdx = ""
            try { $title = $wp.WebPart.Title } catch { }
            try { $typeName = $wp.WebPart.TitleUrl } catch { }
            try { $zone = $wp.WebPart.ZoneId } catch { }
            try { $zoneIdx = $wp.WebPart.ZoneIndex } catch { }
            $props = $null
            try { $props = $wp.WebPart.Properties } catch { }
            if ($props) {
                try { $listName = $props.ListName } catch { }
                if (-not $listName) { try { $listName = $props.ListUrl } catch { } }
                try { $viewGuid = $props.ViewGuid } catch { }
            }

            $results.Add([PSCustomObject]@{
                PageUrl      = $pageUrl
                WebPartId    = $wp.Id
                WebPartTitle = $title
                TypeName     = $typeName
                Category     = Get-WpCategory -TypeName $typeName -Title $title
                ListName     = $listName
                ViewGuid     = $viewGuid
                Zone         = $zone
                ZoneIndex    = $zoneIdx
            })
        }
    }
    Write-Progress -Completed -Activity "Scanning pages"

    $csvPath = Join-Path $OutputDir "webpart-scan.csv"
    $jsonPath = Join-Path $OutputDir "webpart-scan.json"
    if ($results.Count -gt 0) {
        $results | Export-Csv -Path $csvPath -NoTypeInformation -Encoding UTF8
    } else {
        "PageUrl,WebPartId,WebPartTitle,TypeName,Category,ListName,ViewGuid,Zone,ZoneIndex" | Out-File -FilePath $csvPath -Encoding UTF8
    }
    $results | ConvertTo-Json -Depth 5 | Set-Content -Path $jsonPath -Encoding UTF8

    Write-Host "`nComplete." -ForegroundColor Green
    Write-Host "  Pages scanned    : $($allPages.Count)" -ForegroundColor Green
    Write-Host "  Web parts found  : $($results.Count)" -ForegroundColor Green
    Write-Host "  webpart-scan.csv : $csvPath" -ForegroundColor Green
    Write-Host "  webpart-scan.json: $jsonPath" -ForegroundColor Green
}

# ============================================================
# MODE: ExtractContent
# ============================================================
function Unwrap-XmlValue {
    param([string]$Raw)
    if ($Raw -match '(?s)^\s*<!\[CDATA\[(.*)\]\]>\s*$') { return $Matches[1] }
    return [System.Net.WebUtility]::HtmlDecode($Raw.Trim())
}

function Invoke-ExtractContentMode {
    if (-not $ScanCsvPath) { $ScanCsvPath = Join-Path $OutputDir "webpart-scan.csv" }
    if (-not [System.IO.Path]::IsPathRooted($ScanCsvPath)) { $ScanCsvPath = Join-Path (Get-Location) $ScanCsvPath }
    if (-not (Test-Path $ScanCsvPath)) { throw "Cannot find $ScanCsvPath. Run -Mode Scan first, or pass -ScanCsvPath." }

    $webparts = Import-Csv $ScanCsvPath
    Write-Host "`nLoaded $($webparts.Count) web part row(s) from $ScanCsvPath" -ForegroundColor Green

    $rawDir = Join-Path $OutputDir "raw-export"
    if (-not (Test-Path $rawDir)) { New-Item -ItemType Directory -Path $rawDir -Force | Out-Null }

    $rootUri = [Uri]$SiteUrl
    $results = [System.Collections.Generic.List[object]]::new()
    $counter = 0

    foreach ($row in $webparts) {
        $counter++
        $pageUrl = $row.PageUrl
        $wpId = $row.WebPartId
        Write-Progress -Activity "Extracting web part content" -Status "$pageUrl ($wpId)" -PercentComplete (($counter / [Math]::Max($webparts.Count, 1)) * 100)

        $absolutePageUrl = "$($rootUri.Scheme)://$($rootUri.Host)$pageUrl"
        $exportUrl = "$SiteUrl/_vti_bin/exportwp.aspx?pageurl=$([Uri]::EscapeDataString($absolutePageUrl))&guidstring=$wpId"
        $exportResp = Invoke-SP -Url $exportUrl -Method 'Get'

        $content = ""
        $xmlText = ""
        if ($exportResp) {
            $xmlText = if ($exportResp -is [xml]) { $exportResp.OuterXml } else { [string]$exportResp }

            $safePage = ($pageUrl -replace "[\\/:]", "_").TrimStart("_")
            $rawFile = Join-Path $rawDir "$safePage`_$wpId.xml"
            $xmlText | Out-File -FilePath $rawFile -Encoding UTF8

            # ContentEditorWebPart / ScriptEditorWebPart store their payload in a
            # dedicated <Content> element (not the generic v3 property bag).
            if ($xmlText -match '(?s)<(?:\w+:)?Content\b[^>]*>(.*?)</(?:\w+:)?Content>') {
                $content = Unwrap-XmlValue -Raw $Matches[1]
            }
            elseif ($xmlText -match '(?s)<property\b(?:(?!/>)[^>])*\bname\s*=\s*"ClientSideWebPartData"[^>]*>(.*?)</property>') {
                # Modern Script Editor / SPFx clones: double-encoded JSON payload.
                $jsonRaw = Unwrap-XmlValue -Raw $Matches[1]
                if ($jsonRaw -match '(?s)data-sp-webpartdata\s*=\s*"(.*?)"\s*(?:/?>|\s+\w)') {
                    $jsonRaw = [System.Net.WebUtility]::HtmlDecode($Matches[1])
                }
                try {
                    $parsedJson = $jsonRaw | ConvertFrom-Json
                    $content = if ($parsedJson.properties -and $parsedJson.properties.script) { $parsedJson.properties.script } else { $jsonRaw }
                } catch { $content = $jsonRaw }
            }
            elseif ($xmlText -match '(?s)<property\b(?:(?!/>)[^>])*\bname\s*=\s*"Content"[^>]*>(.*?)</property>') {
                $content = Unwrap-XmlValue -Raw $Matches[1]
            }
        }

        $results.Add([PSCustomObject]@{
            PageUrl      = $pageUrl
            WebPartId    = $wpId
            WebPartTitle = $row.WebPartTitle
            Content      = $content
        })

        if ([string]::IsNullOrWhiteSpace($content)) {
            Write-Host "  -> $($row.WebPartTitle) on $pageUrl : EMPTY" -ForegroundColor Yellow
        } else {
            Write-Host "  -> $($row.WebPartTitle) on $pageUrl : $($content.Length) chars" -ForegroundColor Green
        }
    }
    Write-Progress -Completed -Activity "Extracting web part content"

    # webpart-content.json -- consumed directly by webpart_code_analysis.py (analyze-webpart-code)
    $jsonPath = Join-Path $OutputDir "webpart-content.json"
    $results | ConvertTo-Json -Depth 5 | Set-Content -Path $jsonPath -Encoding UTF8

    Write-Host "`nComplete." -ForegroundColor Green
    Write-Host "  Web parts processed: $($results.Count)" -ForegroundColor Green
    Write-Host "  Empty content      : $(@($results | Where-Object { [string]::IsNullOrWhiteSpace($_.Content) }).Count)" -ForegroundColor Yellow
    Write-Host "  webpart-content.json: $jsonPath (feeds analyze-webpart-code)" -ForegroundColor Green
    Write-Host "  raw-export\          : $rawDir (untouched exportwp.aspx XML, one file per web part)" -ForegroundColor DarkGray
}

if ($Mode -eq "Scan") { Invoke-ScanMode } else { Invoke-ExtractContentMode }
