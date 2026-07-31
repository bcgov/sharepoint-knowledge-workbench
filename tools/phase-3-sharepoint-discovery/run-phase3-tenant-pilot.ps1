<#
.SYNOPSIS
    Phase 3 Governed SharePoint Tenant Pilot Execution Script.

.DESCRIPTION
    Automates Task 5 of Phase 3:
    1. Connects to SPO via PnPOnline using config.psd1 credentials.
    2. Ensures custom library fields exist on Site Pages:
       - CEISTopicID (Text)
       - CEISSourceVersion (Text)
       - CEISCanonicalHash (Text)
       - CEISRenderedHash (Text)
    3. Reads upload package manifest (upload-package.json / entries).
    4. Uploads referenced media files to SiteAssets/CEIS-manual-v2/.
    5. Converts HTML content to modern PnP pages, attaching custom metadata fields.
    6. Exports tenant library state to CSV (actual-state.csv) for sharepoint_cli.py reconcile.

.EXAMPLE
    .\run-phase3-tenant-pilot.ps1 -PackageDir "/path/to/upload-package" -ConfigPath "config.psd1" -OutputFile "actual-state.csv"
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$PackageDir,

    [string]$ConfigPath = (Join-Path $PSScriptRoot "config.psd1"),

    [string]$OutputFile = (Join-Path $PSScriptRoot "actual-state.csv")
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $ConfigPath)) {
    Write-Error "Config file not found: $ConfigPath. Copy config.psd1.example to config.psd1 and fill in your tenant settings."
    exit 1
}

$manifestPath = Join-Path $PackageDir "upload-package.json"
if (-not (Test-Path $manifestPath)) {
    Write-Error "Manifest file not found: $manifestPath."
    exit 1
}

Write-Host "Loading configuration from $ConfigPath..." -ForegroundColor Cyan
$config = Import-PowerShellDataFile -Path $ConfigPath

Write-Host "Connecting to SharePoint Online at $($config.SiteUrl)..." -ForegroundColor Cyan
Connect-PnPOnline -Url $config.SiteUrl -ClientId $config.ClientId -Tenant $config.TenantId -Interactive -ForceAuthentication -ErrorAction Stop
Write-Host "Connected successfully!" -ForegroundColor Green

# 1. Ensure custom columns exist on Site Pages
$customFields = @(
    @{ InternalName = "CEISTopicID"; DisplayName = "CEIS Topic ID"; Type = "Text" },
    @{ InternalName = "CEISSourceVersion"; DisplayName = "CEIS Source Version"; Type = "Text" },
    @{ InternalName = "CEISCanonicalHash"; DisplayName = "CEIS Canonical Hash"; Type = "Text" },
    @{ InternalName = "CEISRenderedHash"; DisplayName = "CEIS Rendered Hash"; Type = "Text" }
)

Write-Host "Ensuring custom metadata columns on 'Site Pages' library..." -ForegroundColor Cyan
$list = Get-PnPList -Identity "Site Pages"
foreach ($field in $customFields) {
    $existing = Get-PnPField -List $list -Identity $field.InternalName -ErrorAction SilentlyContinue
    if (-not $existing) {
        Write-Host "  Adding field $($field.DisplayName) ($($field.InternalName))..." -ForegroundColor Yellow
        Add-PnPField -List $list -DisplayName $field.DisplayName -InternalName $field.InternalName -Type $field.Type | Out-Null
    } else {
        Write-Host "  Field $($field.InternalName) already exists." -ForegroundColor Gray
    }
}

# 2. Upload Media Assets
$mediaFolder = Join-Path $PackageDir "media"
$siteAssetsTarget = "SiteAssets/CEIS-manual-v2"
if (Test-Path $mediaFolder) {
    Write-Host "Uploading media assets to $siteAssetsTarget..." -ForegroundColor Cyan
    Resolve-PnPFolder -SiteRelativePath $siteAssetsTarget | Out-Null
    $mediaFiles = Get-ChildItem -Path $mediaFolder -File
    foreach ($file in $mediaFiles) {
        Add-PnPFile -Path $file.FullName -Folder $siteAssetsTarget | Out-Null
        Write-Host "  Uploaded $($file.Name)" -ForegroundColor Gray
    }
}

# 3. Read Manifest and Publish Pages
Write-Host "Reading package manifest..." -ForegroundColor Cyan
$manifestJson = Get-Content -Path $manifestPath -Raw | ConvertFrom-Json

$web = Get-PnPWeb
$siteAssetsUrl = "$($web.Url)/$siteAssetsTarget"

Write-Host "Publishing $($manifestJson.entries.Count) topic pages..." -ForegroundColor Cyan
foreach ($entry in $manifestJson.entries) {
    $htmlFile = Join-Path $PackageDir $entry.rendered_relative_path
    $rawHtml = Get-Content -Path $htmlFile -Raw

    # Rewrite media paths if present
    $rewrittenHtml = $rawHtml -replace '\.\./media/', "$siteAssetsUrl/"

    $pageName = "$($entry.topic_id).aspx"
    Write-Host "  Creating modern page $pageName..." -ForegroundColor Cyan

    $page = Add-PnPPage -Name $pageName -LayoutType Article -Publish:$false
    Add-PnPPageTextPart -Page $page -Text $rewrittenHtml

    # Set custom metadata
    Set-PnPPage -Identity $page -Values @{
        "CEISTopicID"        = $entry.topic_id;
        "CEISSourceVersion"   = $entry.source_version;
        "CEISCanonicalHash"   = $entry.canonical_hash;
        "CEISRenderedHash"    = $entry.rendered_hash;
    } | Out-Null

    # Publish page
    Set-PnPPage -Identity $page -Publish | Out-Null
    Write-Host "  Published $pageName" -ForegroundColor Green
}

# 4. Export actual library state to CSV for reconciliation
Write-Host "Exporting tenant state to CSV at $OutputFile..." -ForegroundColor Cyan
$items = Get-PnPListItem -List "Site Pages" -Fields "FileLeafRef", "CEISTopicID", "CEISSourceVersion", "CEISCanonicalHash", "CEISRenderedHash"
$results = @()

foreach ($item in $items) {
    if ($item["CEISTopicID"]) {
        $results += [PSCustomObject]@{
            "FileLeafRef"        = $item["FileLeafRef"]
            "CEISTopicID"        = $item["CEISTopicID"]
            "CEISSourceVersion"   = $item["CEISSourceVersion"]
            "CEISCanonicalHash"   = $item["CEISCanonicalHash"]
            "CEISRenderedHash"    = $item["CEISRenderedHash"]
        }
    }
}

$results | Export-Csv -Path $OutputFile -NoTypeInformation -Encoding UTF8
Write-Host "Task 5 execution complete! Exported $($results.Count) items to $OutputFile." -ForegroundColor Green
