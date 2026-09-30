<#
.SYNOPSIS
    Parses every downloaded .aspx file and produces a structured web part inventory
    including connected web part relationships (linked list view web parts).

.DESCRIPTION
    Reads all .aspx files from:
      01_source_sharepoint/raw_exports_prod/all_aspx_pages/  (default, from config.psd1 ExportBase)

    For each file, extracts:
      - All web part zones and the web parts in each zone
      - Web part type (XsltListViewWebPart, ContentEditorWebPart, ListFormWebPart, etc.)
      - List bindings (which SP list each web part points to)
      - Connected web part relationships (provider/consumer pairs via ConnectionData)
      - View names and filter expressions
      - CEWP/SEWP content (inline HTML/JS)

    Produces:
      01_source_sharepoint/analysis/aspx-webpart-inventory.json   — full structured data
      01_source_sharepoint/analysis/aspx-webpart-inventory.csv    — flat CSV for quick filtering
      01_source_sharepoint/analysis/aspx-page-summary.md          — human-readable findings

.PARAMETER InputDir
    Directory containing downloaded .aspx files. Defaults to repo-relative path.

.PARAMETER SiteUrl
    Used only to resolve relative URLs in output. Not used for HTTP calls.

.EXAMPLE
    pwsh -File .\analyze-aspx-webparts.ps1
    pwsh -File .\analyze-aspx-webparts.ps1 -InputDir "C:\my\aspx\files"
#>

[CmdletBinding()]
param(
    [string]$ConfigPath = (Join-Path $PSScriptRoot '..\..\config\config.psd1'),
    [string]$InputDir   = "",
    [string]$OutputDir  = "",
    [string]$SiteUrl    = ""
)


Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptDir   = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = (Resolve-Path (Join-Path $scriptDir "..\..\..\..")).Path

$cfg = if (Test-Path $ConfigPath) { Import-PowerShellDataFile $ConfigPath } else { @{} }
if (-not $SiteUrl)  { $SiteUrl  = if ($cfg.StructureSourceUrl) { $cfg.StructureSourceUrl } else { "https://itau.jag.gov.bc.ca/cmat" } }
$targetRoot = Join-Path $projectRoot "csb-intranet-prod\01_source_sharepoint"
if (-not (Test-Path $targetRoot)) { $targetRoot = Join-Path $projectRoot "01_source_sharepoint" }

if ($InputDir) {
    $InputDir = [regex]::Replace($InputDir, "csb-intranet-\s+prod", "csb-intranet-prod").Replace("`r", "").Replace("`n", "").Trim()
    if (-not [System.IO.Path]::IsPathRooted($InputDir)) {
        $InputDir = Join-Path $projectRoot $InputDir
    }
} else {
    $InputDir = Join-Path $targetRoot "all_aspx_pages"
}

if ($OutputDir) {
    $OutputDir = [regex]::Replace($OutputDir, "csb-intranet-\s+prod", "csb-intranet-prod").Replace("`r", "").Replace("`n", "").Trim()
    if (-not [System.IO.Path]::IsPathRooted($OutputDir)) {
        $analysisDir = Join-Path $projectRoot $OutputDir
    } else {
        $analysisDir = $OutputDir
    }
} else {
    $analysisDir = Join-Path $targetRoot "analysis"
}
if (-not (Test-Path $analysisDir)) { New-Item -ItemType Directory -Path $analysisDir -Force | Out-Null }


Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  analyze-aspx-webparts.ps1                              ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host "  Input  : $InputDir" -ForegroundColor White
Write-Host "  Output : $analysisDir" -ForegroundColor White
Write-Host ""

# ── Load manifest ──────────────────────────────────────────────────────────────
$manifestPath = Join-Path $InputDir "aspx-manifest.json"
$manifest     = @{}
if (Test-Path $manifestPath) {
    $entries = Get-Content $manifestPath -Raw | ConvertFrom-Json
    foreach ($e in $entries) {
        $manifest[$e.LocalFile] = $e
    }
}

$aspxFiles = Get-ChildItem -Path $InputDir -Filter "*.aspx" -File
Write-Host "  Found $($aspxFiles.Count) .aspx files to analyze." -ForegroundColor Green
Write-Host ""

# ── Web part type classifier ───────────────────────────────────────────────────
function Get-WpCategory {
    param([string]$TypeName)
    switch -Regex ($TypeName) {
        "XsltListViewWebPart|ListViewWebPart" { return "ListView" }
        "ListFormWebPart"                      { return "ListForm" }
        "ContentEditorWebPart"                 { return "CEWP" }
        "ScriptEditorWebPart"                  { return "SEWP" }
        "PageViewerWebPart"                    { return "PageViewer" }
        "ImageWebPart"                         { return "Image" }
        "SummaryLinkWebPart"                   { return "SummaryLink" }
        "TableOfContentsWebPart"               { return "TOC" }
        "UserTasksWebPart"                     { return "UserTasks" }
        "SPUserCodeWebPart"                    { return "Sandbox" }
        "MediaWebPart"                         { return "Media" }
        default                                { return "Other" }
    }
}

# ── Parse a single .aspx ──────────────────────────────────────────────────────
function Parse-AspxFile {
    param([string]$FilePath, [string]$FileName)

    $content = Get-Content $FilePath -Raw -ErrorAction SilentlyContinue
    if (-not $content) { return $null }

    $manifestEntry = if ($manifest.ContainsKey($FileName)) { $manifest[$FileName] } else { $null }
    $catVal   = "Unknown"
    $titleVal = ""
    if ($manifestEntry -and $manifestEntry.PSObject.Properties['Category'])  { $catVal   = $manifestEntry.Category }
    if ($manifestEntry -and $manifestEntry.PSObject.Properties['ListTitle']) { $titleVal = $manifestEntry.ListTitle }

    $pageResult = [ordered]@{
        FileName    = $FileName
        Category    = $catVal
        ListTitle   = $titleVal
        WebParts    = [System.Collections.Generic.List[object]]::new()
        Connections = [System.Collections.Generic.List[object]]::new()
        HasCEWP     = $false
        HasSEWP     = $false
        HasListView = $false
        HasListForm = $false
        ConnectedWPCount = 0
    }



    # ── Extract web part definitions ─────────────────────────────────────────
    # SP serialises web parts as XML inside <WebPart> tags within the .aspx
    $wpMatches = [regex]::Matches($content, '(?s)<WebPart[^>]*>(.*?)</WebPart\s*>', [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)

    foreach ($m in $wpMatches) {
        $xml = $m.Value
        $wp  = [ordered]@{
            TypeName    = ""
            Category    = ""
            Title       = ""
            ListName    = ""
            ViewName    = ""
            ZoneID      = ""
            ZoneIndex   = ""
            WebPartId   = ""
            IsProvider  = $false
            IsConsumer  = $false
            CEWPContent = ""
        }

        # Type
        if ($xml -match '<type\s+name="([^"]+)"') { $wp.TypeName = $Matches[1] }
        elseif ($xml -match 'TypeName="([^"]+)"')  { $wp.TypeName = $Matches[1] }

        $wp.Category = Get-WpCategory -TypeName $wp.TypeName

        # Title
        if ($xml -match '<title>(.*?)</title>')           { $wp.Title = $Matches[1] }
        elseif ($xml -match '<property name="Title"[^>]*>(.*?)</property>') { $wp.Title = $Matches[1] }

        # List name
        if ($xml -match '<ListName>(.*?)</ListName>')     { $wp.ListName = $Matches[1] }
        elseif ($xml -match 'ListName="([^"]+)"')         { $wp.ListName = $Matches[1] }
        elseif ($xml -match '<property name="ListName"[^>]*>(\{[^}]+\})</property>') { $wp.ListName = $Matches[1] }

        # View name
        if ($xml -match '<ViewFlag[^>]*>.*?<ViewId>(.*?)</ViewId>') { $wp.ViewName = $Matches[1] }
        elseif ($xml -match 'ViewName="([^"]+)"')         { $wp.ViewName = $Matches[1] }
        elseif ($xml -match '<property name="ViewName"[^>]*>(.*?)</property>') { $wp.ViewName = $Matches[1] }

        # Zone
        if ($xml -match 'ZoneID="([^"]+)"')               { $wp.ZoneID = $Matches[1] }
        if ($xml -match 'FrameState="([^"]+)"')            { } # not needed

        # Web part ID (for connection mapping)
        if ($xml -match 'ID="([^"]+)"')                   { $wp.WebPartId = $Matches[1] }
        elseif ($xml -match '<id>(.*?)</id>')              { $wp.WebPartId = $Matches[1] }

        # CEWP content
        if ($wp.Category -eq "CEWP") {
            if ($xml -match '(?s)<Content[^>]*>(.*?)</Content>') {
                $wp.CEWPContent = $Matches[1].Trim() -replace '\s+', ' '
                if ($wp.CEWPContent.Length -gt 300) { $wp.CEWPContent = $wp.CEWPContent.Substring(0,300) + "…" }
            }
            $pageResult.HasCEWP = $true
        }
        if ($wp.Category -eq "SEWP") { $pageResult.HasSEWP = $true }
        if ($wp.Category -eq "ListView") { $pageResult.HasListView = $true }
        if ($wp.Category -eq "ListForm") { $pageResult.HasListForm = $true }

        $pageResult.WebParts.Add($wp)
    }

    # ── Extract connected web part relationships ───────────────────────────────
    # SP stores connections in <WebPartConnection> elements or in ConnectionData XML
    $connMatches = [regex]::Matches($content, '(?s)<WebPartConnection[^>]*/?>|(?s)<WebPartConnection[^>]*>.*?</WebPartConnection>', [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)

    foreach ($m in $connMatches) {
        $cx = $m.Value
        $conn = [ordered]@{
            ConsumerID           = ""
            ConsumerConnectionID = ""
            ProviderID           = ""
            ProviderConnectionID = ""
        }
        if ($cx -match 'ConsumerID="([^"]+)"')           { $conn.ConsumerID = $Matches[1] }
        if ($cx -match 'ConsumerConnectionPointID="([^"]+)"') { $conn.ConsumerConnectionID = $Matches[1] }
        if ($cx -match 'ProviderID="([^"]+)"')           { $conn.ProviderID = $Matches[1] }
        if ($cx -match 'ProviderConnectionPointID="([^"]+)"') { $conn.ProviderConnectionID = $Matches[1] }

        if ($conn.ConsumerID -or $conn.ProviderID) {
            $pageResult.Connections.Add($conn)
        }
    }

    # Also check for ConnectionData blocks (older SP serialisation)
    if ($content -match '(?s)<ConnectionData>(.*?)</ConnectionData>') {
        $cdBlock = $Matches[1]
        $cdConns = [regex]::Matches($cdBlock, '(?s)<Connection[^>]*/>')
        foreach ($c in $cdConns) {
            $cXml = $c.Value
            $conn = [ordered]@{
                ConsumerID           = ""
                ConsumerConnectionID = ""
                ProviderID           = ""
                ProviderConnectionID = ""
            }
            if ($cXml -match 'ConsumerWebPartID="([^"]+)"')           { $conn.ConsumerID = $Matches[1] }
            if ($cXml -match 'ConsumerConnectionPointID="([^"]+)"')   { $conn.ConsumerConnectionID = $Matches[1] }
            if ($cXml -match 'ProviderWebPartID="([^"]+)"')           { $conn.ProviderID = $Matches[1] }
            if ($cXml -match 'ProviderConnectionPointID="([^"]+)"')   { $conn.ProviderConnectionID = $Matches[1] }
            if ($conn.ConsumerID -or $conn.ProviderID) {
                $pageResult.Connections.Add($conn)
            }
        }
    }

    $pageResult.ConnectedWPCount = $pageResult.Connections.Count

    return $pageResult
}

# ── Analyze all files ─────────────────────────────────────────────────────────
$allPages  = [System.Collections.Generic.List[object]]::new()
$counter   = 0
$total     = $aspxFiles.Count

foreach ($f in $aspxFiles) {
    $counter++
    Write-Progress -Activity "Analyzing .aspx files" -Status $f.Name -PercentComplete (($counter / $total) * 100)
    $result = Parse-AspxFile -FilePath $f.FullName -FileName $f.Name
    if ($result) { $allPages.Add($result) }
}

Write-Progress -Completed -Activity "Analyzing .aspx files"

# ── Save JSON ─────────────────────────────────────────────────────────────────
$jsonPath = Join-Path $analysisDir "aspx-webpart-inventory.json"
$allPages | ConvertTo-Json -Depth 8 | Set-Content -Path $jsonPath -Encoding UTF8
Write-Host "  Saved JSON: $jsonPath" -ForegroundColor DarkGray

# ── Save CSV (flat — one row per web part) ────────────────────────────────────
$csvRows = [System.Collections.Generic.List[object]]::new()
foreach ($page in $allPages) {
    foreach ($wp in $page.WebParts) {
        $csvRows.Add([PSCustomObject]@{
            FileName    = $page.FileName
            Category    = $page.Category
            ListTitle   = $page.ListTitle
            WPCategory  = $wp.Category
            WPType      = $wp.TypeName
            WPTitle     = $wp.Title
            ListName    = $wp.ListName
            ViewName    = $wp.ViewName
            ZoneID      = $wp.ZoneID
            WebPartId   = $wp.WebPartId
            CEWPSnippet = $wp.CEWPContent
            HasConnections = ($page.ConnectedWPCount -gt 0)
        })
    }
}
$csvPath = Join-Path $analysisDir "aspx-webpart-inventory.csv"
$csvRows | Export-Csv -Path $csvPath -NoTypeInformation -Encoding UTF8
Write-Host "  Saved CSV : $csvPath" -ForegroundColor DarkGray

# ── Build Markdown summary ────────────────────────────────────────────────────
$totalWPs        = ($allPages | ForEach-Object { $_.WebParts.Count } | Measure-Object -Sum).Sum
$cewpPages       = @($allPages | Where-Object { $_.HasCEWP })
$sewpPages       = @($allPages | Where-Object { $_.HasSEWP })
$connectedPages  = @($allPages | Where-Object { $_.ConnectedWPCount -gt 0 })
$listViewPages   = @($allPages | Where-Object { $_.HasListView })
$listFormPages   = @($allPages | Where-Object { $_.HasListForm })

$sb = [System.Text.StringBuilder]::new()

$sb.AppendLine("# ASPX Page Web Part Inventory") | Out-Null
$sb.AppendLine("") | Out-Null
$sb.AppendLine("> **Source:** ``$InputDir``") | Out-Null
$sb.AppendLine("> **Generated:** $(Get-Date -Format 'yyyy-MM-dd')") | Out-Null
$sb.AppendLine("> **Site:** ``$SiteUrl``") | Out-Null
$sb.AppendLine("") | Out-Null
$sb.AppendLine("---") | Out-Null
$sb.AppendLine("") | Out-Null
$sb.AppendLine("## Summary") | Out-Null
$sb.AppendLine("") | Out-Null
$sb.AppendLine("| Metric | Count |") | Out-Null
$sb.AppendLine("|:---|---:|") | Out-Null
$sb.AppendLine("| Total .aspx pages analyzed | $($allPages.Count) |") | Out-Null
$sb.AppendLine("| Total web parts found | $totalWPs |") | Out-Null
$sb.AppendLine("| Pages with List View Web Parts (LVWP) | $($listViewPages.Count) |") | Out-Null
$sb.AppendLine("| Pages with List Form Web Parts | $($listFormPages.Count) |") | Out-Null
$sb.AppendLine("| Pages with Content Editor Web Parts (CEWP) | $($cewpPages.Count) |") | Out-Null
$sb.AppendLine("| Pages with Script Editor Web Parts (SEWP) | $($sewpPages.Count) |") | Out-Null
$sb.AppendLine("| Pages with connected web parts | $($connectedPages.Count) |") | Out-Null
$sb.AppendLine("") | Out-Null

# Connected web part pages — the key question
$sb.AppendLine("---") | Out-Null
$sb.AppendLine("") | Out-Null
$sb.AppendLine("## Section 1 — Pages with Connected Web Parts") | Out-Null
$sb.AppendLine("") | Out-Null
$sb.AppendLine("These pages use the SP2016 web part connection mechanism — a parent List View Web Part") | Out-Null
$sb.AppendLine("filters one or more child web parts when a row is selected. In the replatform this") | Out-Null
$sb.AppendLine('becomes a detail-page with filtered API calls (`GET /api/cases/{id}/approval-requests` etc.).') | Out-Null
$sb.AppendLine("") | Out-Null

if ($connectedPages.Count -eq 0) {
    $sb.AppendLine("_No connected web part relationships detected in downloaded .aspx files._") | Out-Null
    $sb.AppendLine("") | Out-Null
    $sb.AppendLine("> **Note:** SP2016 stores connection data in the content database, not always in the .aspx source.") | Out-Null
    $sb.AppendLine('> Run `scan-webparts.ps1 -UseDefaultCredentials` to query the live WPM API for connection data.') | Out-Null
} else {
    $sb.AppendLine("| Page | Connections | Provider WP | Consumer WP |") | Out-Null
    $sb.AppendLine("|:---|:---|:---|:---|") | Out-Null
    foreach ($page in $connectedPages) {
        foreach ($conn in $page.Connections) {
            $sb.AppendLine("| $($page.FileName) | $($page.ConnectedWPCount) | $($conn.ProviderID) ($($conn.ProviderConnectionID)) | $($conn.ConsumerID) ($($conn.ConsumerConnectionID)) |") | Out-Null
        }
    }
}
$sb.AppendLine("") | Out-Null

# CEWP pages
$sb.AppendLine("---") | Out-Null
$sb.AppendLine("") | Out-Null
$sb.AppendLine("## Section 2 — Content Editor Web Part Pages") | Out-Null
$sb.AppendLine("") | Out-Null
$sb.AppendLine("| Page | List | CEWP Content (first 200 chars) |") | Out-Null
$sb.AppendLine("|:---|:---|:---|") | Out-Null
foreach ($page in $cewpPages) {
    foreach ($wp in ($page.WebParts | Where-Object { $_.Category -eq "CEWP" })) {
        $snippet = ($wp.CEWPContent -replace '\|','∣' -replace '\n',' ').Trim()
        if ($snippet.Length -gt 200) { $snippet = $snippet.Substring(0,200) + "…" }
        $sb.AppendLine("| $($page.FileName) | $($page.ListTitle) | $snippet |") | Out-Null
    }
}
$sb.AppendLine("") | Out-Null

# List view web parts — what lists appear on which pages
$sb.AppendLine("---") | Out-Null
$sb.AppendLine("") | Out-Null
$sb.AppendLine("## Section 3 — List View Web Parts (what list appears on which page)") | Out-Null
$sb.AppendLine("") | Out-Null
$sb.AppendLine("| Page | Category | List Name | View | Zone |") | Out-Null
$sb.AppendLine("|:---|:---|:---|:---|:---|") | Out-Null
foreach ($page in ($allPages | Sort-Object FileName)) {
    foreach ($wp in ($page.WebParts | Where-Object { $_.Category -eq "ListView" })) {
        $sb.AppendLine("| $($page.FileName) | $($page.Category) | $($wp.ListName) | $($wp.ViewName) | $($wp.ZoneID) |") | Out-Null
    }
}
$sb.AppendLine("") | Out-Null

# All web parts by type frequency
$sb.AppendLine("---") | Out-Null
$sb.AppendLine("") | Out-Null
$sb.AppendLine("## Section 4 — Web Part Type Frequency") | Out-Null
$sb.AppendLine("") | Out-Null
$sb.AppendLine("| Category | Count |") | Out-Null
$sb.AppendLine("|:---|---:|") | Out-Null
$allPages |
    ForEach-Object { $_.WebParts } |
    Group-Object { $_.Category } |
    Sort-Object Count -Descending |
    ForEach-Object { $sb.AppendLine("| $($_.Name) | $($_.Count) |") | Out-Null }
$sb.AppendLine("") | Out-Null

# Missing pages note
$sb.AppendLine("---") | Out-Null
$sb.AppendLine("") | Out-Null
$sb.AppendLine("## Section 5 — Known Gaps") | Out-Null
$sb.AppendLine("") | Out-Null
$sb.AppendLine("SP2016 stores web part configuration in the **content database**, not in the .aspx file itself") | Out-Null
$sb.AppendLine("when web parts are added through the browser UI. If this report shows zero web parts on a page") | Out-Null
$sb.AppendLine("you know has web parts, that page's configuration lives in the DB only.") | Out-Null
$sb.AppendLine("") | Out-Null
$sb.AppendLine("Use the live API scanner to confirm:") | Out-Null
$sb.AppendLine('```powershell') | Out-Null
$sb.AppendLine('pwsh -File .\scan-webparts.ps1 -UseDefaultCredentials') | Out-Null
$sb.AppendLine('```') | Out-Null
$sb.AppendLine("") | Out-Null
$sb.AppendLine('Pages confirmed to have web parts via live API (from prior `scan-webparts.ps1` run):') | Out-Null
$sb.AppendLine('- `My_ICM_Cases.aspx` — 4 CEWPs (text banners/instructions)') | Out-Null
$sb.AppendLine('- `My_PIO_Cases.aspx` — CEWPs (same pattern)') | Out-Null
$sb.AppendLine('- `My_ITAU_Cases.aspx` — **not yet extracted** (missing from download — add to extract run)') | Out-Null
$sb.AppendLine("") | Out-Null
$sb.AppendLine("---") | Out-Null
$sb.AppendLine("") | Out-Null
$sb.AppendLine('*Full data: `aspx-webpart-inventory.json` and `aspx-webpart-inventory.csv` in same folder.*') | Out-Null

$mdPath = Join-Path $analysisDir "aspx-page-summary.md"
$sb.ToString() | Set-Content -Path $mdPath -Encoding UTF8

# ── Final summary ─────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  Analysis Complete                                       ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host "  Pages analyzed      : $($allPages.Count)" -ForegroundColor Green
Write-Host "  Total web parts     : $totalWPs" -ForegroundColor Green
Write-Host "  CEWP pages          : $($cewpPages.Count)" -ForegroundColor $(if ($cewpPages.Count -gt 0) {"Yellow"} else {"Green"})
Write-Host "  SEWP pages          : $($sewpPages.Count)" -ForegroundColor $(if ($sewpPages.Count -gt 0) {"Yellow"} else {"Green"})
Write-Host "  Connected WP pages  : $($connectedPages.Count)" -ForegroundColor $(if ($connectedPages.Count -gt 0) {"Yellow"} else {"Green"})
Write-Host ""
Write-Host "  Outputs:" -ForegroundColor White
Write-Host "    $mdPath" -ForegroundColor DarkGray
Write-Host "    $jsonPath" -ForegroundColor DarkGray
Write-Host "    $csvPath" -ForegroundColor DarkGray
Write-Host ""

if ($connectedPages.Count -eq 0) {
    Write-Host "  NOTE: No connections found in .aspx source." -ForegroundColor Yellow
    Write-Host "  SP2016 stores connection data in the content DB when web parts are" -ForegroundColor Yellow
    Write-Host "  added via browser. Run scan-webparts.ps1 against the live site" -ForegroundColor Yellow
    Write-Host "  to query the Web Part Manager API directly." -ForegroundColor Yellow
    Write-Host ""
}
