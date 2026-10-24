<#
.SYNOPSIS
Batch extracts SP2016 web part content and scaffolds temp workspaces for all in-scope migration pages.

.DESCRIPTION
Prompts for on-premises credentials ONCE, then iterates through all 166 target pages
(or filtered subset) from inventory-page.json across all three subsites:
- Administration (https://source-tenant.example.com/Administration)
- Operations (https://source-tenant.example.com/Operations)
- Main (https://source-tenant.example.com)

For each page, scaffolds its temp/<slug> workspace, prepares metadata, writes webpart-scan.csv,
and extracts untruncated HTML/JS web part content and raw XML exports from SP2016.

.PARAMETER Wave
Optional wave filter (e.g. 'Wave-1', 'Wave-2', 'Wave-3', or 'All'). Default is 'All' (all 166 pages).

.PARAMETER SiteName
Optional subsite filter ('Administration', 'Main', 'Operations', or 'All'). Default is 'All'.

.PARAMETER PageTitles
Optional list of specific page titles or slugs to extract.

.PARAMETER InventoryPath
Path to inventory-page.json. Defaults to inventory/inventory-page.json.

.PARAMETER Credential
Optional PSCredential object. If omitted, prompts once via Get-Credential.

.EXAMPLE
pwsh -File plugins/sp-migration/scripts/migration/batch-extract-webpart-content.ps1
Extracts all 166 pages across all subsites with a single credential prompt.

.EXAMPLE
pwsh -File plugins/sp-migration/scripts/migration/batch-extract-webpart-content.ps1 -Wave Wave-2
#>

[CmdletBinding()]
param(
    [string]$Wave = "All",
    [string]$SiteName = "All",
    [string[]]$PageTitles,
    [string]$InventoryPath = "inventory/inventory-page.json",
    [System.Management.Automation.PSCredential]$Credential
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = $PSScriptRoot
while ($RepoRoot -and -not (Test-Path (Join-Path $RepoRoot ".agents"))) {
    $Parent = Split-Path $RepoRoot -Parent
    if ($Parent -eq $RepoRoot) { break }
    $RepoRoot = $Parent
}
if (-not $RepoRoot) { $RepoRoot = (Get-Location).Path }

$ResolvedInventory = Join-Path $RepoRoot $InventoryPath
if (-not (Test-Path $ResolvedInventory)) {
    throw "Inventory file not found: $ResolvedInventory"
}

$Inventory = Get-Content -LiteralPath $ResolvedInventory -Raw | ConvertFrom-Json
$ScanResultsCsv = Join-Path $RepoRoot "portal-workspace-prod/01_source_sharepoint/analysis/legacy_webparts_scan_results.csv"
$RawExportBaseDir = Join-Path $RepoRoot "portal-workspace-prod/01_source_sharepoint/analysis/webpart_raw_export"
$CollectorScript = Join-Path $RepoRoot ".agents/skills/sharepoint-analyze-webpart-behavior/scripts/collect-sharepoint-webpart-content.ps1"

# Load legacy scan results for fast web part ID lookups
$LegacyWpMap = @{}
if (Test-Path $ScanResultsCsv) {
    Import-Csv -LiteralPath $ScanResultsCsv -Header "PageUrl", "WebPartTitle", "WebPartId" | ForEach-Object {
        $pUrl = $_.PageUrl.Trim()
        if (-not $LegacyWpMap.ContainsKey($pUrl)) {
            $LegacyWpMap[$pUrl] = [System.Collections.Generic.List[PSObject]]::new()
        }
        $LegacyWpMap[$pUrl].Add($_)
    }
}

# Filter target pages
$Targets = $Inventory | Where-Object {
    $match = $true
    if ($Wave -and $Wave -ne "All" -and $_.'Migration Plan' -ne $Wave) { $match = $false }
    if ($SiteName -and $SiteName -ne "All" -and $_.SiteName -ne $SiteName) { $match = $false }
    if ($PageTitles -and $PageTitles.Count -gt 0) {
        $t = $_.Title
        $match = ($PageTitles -contains $t) -or ($PageTitles -contains ($t -replace '\.aspx$', ''))
    }
    $match
}

if (-not $Targets -or $Targets.Count -eq 0) {
    Write-Host "No matching pages found for extraction." -ForegroundColor Yellow
    return
}

Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host " Batch SP2016 Web Part Extractor (All-in-One)" -ForegroundColor Cyan
Write-Host " Target count: $($Targets.Count) pages" -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan

# Prompt for credentials once if not passed
if (-not $Credential) {
    $Credential = Get-Credential -Message "Enter credentials for on-prem SP2016 (https://source-tenant.example.com)"
    if (-not $Credential) { throw "No credentials provided." }
}

$SuccessCount = 0
$FailCount = 0
$TotalWebParts = 0

for ($i = 0; $i -lt $Targets.Count; $i++) {
    $item = $Targets[$i]
    $title = $item.Title
    $pageUrl = $item.ServerRelativeUrl
    $fullUrl = $item.Url
    $site = $item.SiteName
    $idx = $i + 1
    
    # Determine correct subsite URL
    $siteRootUrl = switch ($site) {
        "Administration" { "https://source-tenant.example.com/Administration" }
        "Operations"    { "https://source-tenant.example.com/Operations" }
        default      { "https://source-tenant.example.com" }
    }

    # Generate clean folder slug (e.g. 'administration-field-educators' or 'field-educators')
    $safeTitle = ($title.ToLower() -replace '[^a-z0-9]+', '-').Trim('-')
    $slug = if ($site -ne "Main" -and -not $safeTitle.StartsWith($site.ToLower())) {
        "$($site.ToLower())-$safeTitle"
    } else {
        $safeTitle
    }
    
    # Also support existing directory name without prefix if it exists
    if (-not (Test-Path (Join-Path $RepoRoot "temp\$slug")) -and (Test-Path (Join-Path $RepoRoot "temp\$safeTitle"))) {
        $slug = $safeTitle
    }

    Write-Host "`n[$idx/$($Targets.Count)] [$site] $title -> temp\$slug ..." -ForegroundColor White

    $baseDir = Join-Path $RepoRoot "temp\$slug"
    $wpDir = Join-Path $baseDir "wp"
    $rawDir = Join-Path $wpDir "raw-export"
    $assetsDir = Join-Path $baseDir "assets"
    
    New-Item -ItemType Directory -Force -Path $rawDir | Out-Null
    New-Item -ItemType Directory -Force -Path $assetsDir | Out-Null
    
    # 1. Scaffolding metadata JSON files
    $pageJsonPath = Join-Path $baseDir "page.json"
    $scopeJsonPath = Join-Path $baseDir "scope.json"
    $legacyScopeJsonPath = Join-Path $baseDir "legacy-scope.json"
    $imagesJsonPath = Join-Path $baseDir "images.json"
    
    $item | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $pageJsonPath -Encoding utf8
    
    @{
        SiteName = $item.SiteName
        ServerRelativeUrl = $item.ServerRelativeUrl
        TargetPageServerRelativeUrl = "/SitePages/$($item.SiteName)/$($title).aspx"
        Title = $item.Title
        Url = $item.Url
        Layout = $item.Layout
        TargetEnvironment = "dev"
        Wave = $item.'Migration Plan'
    } | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $scopeJsonPath -Encoding utf8

    @{
        Wave = $item.'Migration Plan'
        TargetEnvironment = "dev"
        SiteName = $item.SiteName
        TargetPageServerRelativeUrl = "/SitePages/$($item.SiteName)/$($title).aspx"
        Layout = $item.Layout
        ServerRelativeUrl = $item.ServerRelativeUrl
    } | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $legacyScopeJsonPath -Encoding utf8

    if (-not (Test-Path $imagesJsonPath)) {
        "[]" | Set-Content -LiteralPath $imagesJsonPath -Encoding utf8
    }

    # 2. Build webpart-scan.csv and copy raw-export XMLs
    $wpList = @()
    if ($LegacyWpMap.ContainsKey($pageUrl)) {
        $wpList = $LegacyWpMap[$pageUrl]
    }

    $scanCsvLines = [System.Collections.Generic.List[string]]::new()
    $scanCsvLines.Add("PageUrl,WebPartId,WebPartTitle,TypeName,Category,ListName,ViewGuid,Zone,ZoneIndex")

    $order = 0
    foreach ($w in $wpList) {
        $wId = $w.WebPartId
        $wTitle = $w.WebPartTitle
        $zone = if ($wTitle -match "Intro|Content Editor") { "HeaderZone" } else { "LeftZone" }
        $scanCsvLines.Add("`"$pageUrl`",`"$wId`",`"$wTitle`",,CEWP,,,`"$zone`",$order")
        $order++

        # Copy raw export XML if exists
        $srcXml = Join-Path $RawExportBaseDir "${site}_Pages_$($title).aspx_$wId.xml"
        if (-not (Test-Path $srcXml)) {
            $srcXml = Join-Path $RawExportBaseDir "Pages_$($title).aspx_$wId.xml"
        }
        if (-not (Test-Path $srcXml)) {
            $srcXml = Join-Path $RawExportBaseDir "Administration_Pages_$($title).aspx_$wId.xml"
        }
        if (Test-Path $srcXml) {
            Copy-Item -LiteralPath $srcXml -Destination $rawDir -Force
        }
    }

    $scanCsvPath = Join-Path $wpDir "webpart-scan.csv"
    $scanCsvLines | Set-Content -LiteralPath $scanCsvPath -Encoding utf8

    # 3. If no webparts found in mapping, create a dummy or skip content extraction
    if ($wpList.Count -eq 0) {
        Write-Host "  -> No classic web parts recorded on this page." -ForegroundColor Gray
        "[]" | Set-Content -LiteralPath (Join-Path $wpDir "webpart-content.json") -Encoding utf8
        $SuccessCount++
        continue
    }

    # 4. Extract content via legacy exportwp.aspx
    try {
        & $CollectorScript `
            -SiteUrl $siteRootUrl `
            -OutputDir $wpDir `
            -ScanCsvPath $scanCsvPath `
            -Mode ExtractContent `
            -Credential $Credential

        $SuccessCount++
        $TotalWebParts += $wpList.Count
    } catch {
        Write-Warning "Extraction failed for $title`: $_"
        $FailCount++
    }
}

Write-Host "`n==================================================================" -ForegroundColor Cyan
Write-Host " Batch Extraction Complete!" -ForegroundColor Green
Write-Host "   Pages processed  : $SuccessCount succeeded, $FailCount failed" -ForegroundColor Green
Write-Host "   Web parts pulled : $TotalWebParts" -ForegroundColor Green
Write-Host "==================================================================" -ForegroundColor Cyan
