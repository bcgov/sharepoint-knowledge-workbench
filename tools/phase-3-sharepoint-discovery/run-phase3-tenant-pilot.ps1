<#
.SYNOPSIS
    Phase 3 Governed SharePoint Tenant Pilot Execution Script.

.DESCRIPTION
    1. Connects to SPO via PnPOnline using config.psd1 credentials.
    2. Ensures dedicated Page Library 'CEISPilotKnowledgePages' and Asset Library 'CEISPilotKnowledge' exist.
    3. Ensures custom library fields exist on both libraries:
       - TopicId (Text)
       - PackageIdentity (Text)
       - PublicationOrder (Number)
       - TopicContentSHA256 (Text)
       - SourceDocumentSHA256 (Text)
    4. Uploads media files directly to CEISPilotKnowledge/media/.
    5. Publishes modern web pages directly to dedicated Page Library CEISPilotKnowledgePages/.
    6. Exports actual tenant state to CSV (actual-state.csv) for reconciliation.

.EXAMPLE
    .\run-phase3-tenant-pilot.ps1 -PackageDir "temp/upload-packages/ceis-manual-v2" -ConfigPath "config.psd1" -OutputFile "actual-state.csv"
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$PackageDir,

    [string]$ConfigPath = (Join-Path $PSScriptRoot "config.psd1"),

    [string]$OutputFile = (Join-Path $PSScriptRoot "actual-state.csv")
)

$ErrorActionPreference = "Stop"

# Single-source-of-truth library target configuration
[string]$PageLibraryUrl   = "CEISPilotKnowledgePages"
[string]$PageLibraryTitle = "CEIS Pilot Knowledge Pages"
[string]$AssetLibraryUrl  = "CEISPilotKnowledge"
[string]$AssetLibraryTitle = "CEIS-Pilot-Knowledge"

if (-not (Test-Path $ConfigPath)) {
    Write-Error "Config file not found: $ConfigPath. Copy config.psd1.example to config.psd1 and fill in your tenant settings."
    exit 1
}

$manifestPath = Join-Path $PackageDir "upload-manifest.json"
if (-not (Test-Path $manifestPath)) {
    $manifestPath = Join-Path $PackageDir "upload-package.json"
}
if (-not (Test-Path $manifestPath)) {
    Write-Error "Manifest file not found in $PackageDir."
    exit 1
}

Write-Host "Loading configuration from $ConfigPath..." -ForegroundColor Cyan
$config = Import-PowerShellDataFile -Path $ConfigPath

Write-Host "Connecting to SharePoint Online at $($config.SiteUrl)..." -ForegroundColor Cyan
Connect-PnPOnline -Url $config.SiteUrl -ClientId $config.ClientId -Tenant $config.TenantId -Interactive -ForceAuthentication -ErrorAction Stop
Write-Host "Connected successfully!" -ForegroundColor Green

# 1. Ensure custom Page Library & Asset Library exist for Governance Pilot
Write-Host "Checking for Page Library '$PageLibraryUrl'..." -ForegroundColor Cyan
$pageList = Get-PnPList -Identity $PageLibraryUrl -ErrorAction SilentlyContinue
if (-not $pageList) {
    $pageList = Get-PnPList -Identity $PageLibraryTitle -ErrorAction SilentlyContinue
}
if (-not $pageList) {
    Write-Host "Creating dedicated Page Library '$PageLibraryTitle' at $PageLibraryUrl..." -ForegroundColor Yellow
    $pageList = New-PnPList -Title $PageLibraryTitle -Url $PageLibraryUrl -Template WebPageLibrary
}

Write-Host "Checking for Asset Library '$AssetLibraryUrl'..." -ForegroundColor Cyan
$assetList = Get-PnPList -Identity $AssetLibraryUrl -ErrorAction SilentlyContinue
if (-not $assetList) {
    $assetList = Get-PnPList -Identity $AssetLibraryTitle -ErrorAction SilentlyContinue
}
if (-not $assetList) {
    Write-Host "Creating dedicated Asset Library '$AssetLibraryTitle' at $AssetLibraryUrl..." -ForegroundColor Yellow
    $assetList = New-PnPList -Title $AssetLibraryTitle -Url $AssetLibraryUrl -Template DocumentLibrary
}

# 2. Ensure custom columns exist on Page Library and Asset Library
$customFields = @(
    @{ InternalName = "TopicId"; DisplayName = "Topic ID"; Type = "Text" },
    @{ InternalName = "PackageIdentity"; DisplayName = "Package Identity"; Type = "Text" },
    @{ InternalName = "PublicationOrder"; DisplayName = "Publication Order"; Type = "Number" },
    @{ InternalName = "TopicContentSHA256"; DisplayName = "Topic Content SHA256"; Type = "Text" },
    @{ InternalName = "SourceDocumentSHA256"; DisplayName = "Source Document SHA256"; Type = "Text" }
)

foreach ($targetListId in @($PageLibraryUrl, $AssetLibraryUrl)) {
    Write-Host "Ensuring custom metadata columns on '$targetListId' library..." -ForegroundColor Cyan
    $list = Get-PnPList -Identity $targetListId -ErrorAction SilentlyContinue
    if ($list) {
        foreach ($field in $customFields) {
            $existing = Get-PnPField -List $list -Identity $field.InternalName -ErrorAction SilentlyContinue
            if (-not $existing) {
                Write-Host "  Adding field $($field.DisplayName) ($($field.InternalName)) to $targetListId..." -ForegroundColor Yellow
                Add-PnPField -List $list -DisplayName $field.DisplayName -InternalName $field.InternalName -Type $field.Type | Out-Null
            } else {
                Write-Host "  Field $($field.InternalName) already exists on $targetListId." -ForegroundColor Gray
            }
        }
    }
}

# 3. Upload Media Assets to dedicated library CEISPilotKnowledge/media
$mediaFolder = Join-Path $PackageDir "media"
$targetMediaFolder = "$AssetLibraryUrl/media"
if (Test-Path $mediaFolder) {
    Write-Host "Checking media assets in $targetMediaFolder..." -ForegroundColor Cyan
    try {
        Add-PnPFolder -Name "media" -Folder $AssetLibraryUrl -ErrorAction SilentlyContinue | Out-Null
    } catch { }
    
    $existingFolderFiles = Get-PnPFolderItem -ItemType File -FolderSiteRelativeUrl $targetMediaFolder -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Name
    
    $mediaFiles = Get-ChildItem -Path $mediaFolder -File
    foreach ($file in $mediaFiles) {
        if ($existingFolderFiles -and ($existingFolderFiles -contains $file.Name)) {
            Write-Host "  Skipping existing $($file.Name)" -ForegroundColor Gray
            continue
        }
        
        try {
            Add-PnPFile -Path $file.FullName -Folder $targetMediaFolder -ErrorAction Stop | Out-Null
            Write-Host "  Uploaded $($file.Name)" -ForegroundColor Green
        } catch {
            Write-Host "  Warning: Failed to upload $($file.Name) - $($_.Exception.Message)" -ForegroundColor Yellow
        }
    }
}

# 4. Read Manifest and Publish Modern Pages directly into Page Library CEISPilotKnowledgePages
Write-Host "Reading package manifest..." -ForegroundColor Cyan
$manifestJson = Get-Content -Path $manifestPath -Raw | ConvertFrom-Json

$web = Get-PnPWeb
$serverRelativeWebUrl = $web.ServerRelativeUrl.TrimEnd('/')
$mediaUrl = "$($web.Url)/$targetMediaFolder"

Write-Host "Publishing $($manifestJson.entries.Count) formatted modern pages to dedicated Page Library '$PageLibraryUrl'..." -ForegroundColor Cyan
foreach ($entry in $manifestJson.entries) {
    $pageName = "$($entry.topic_id).aspx"
    $pagePath = "CEISPilotKnowledgePages/$pageName"

    # Convert Markdown to HTML via pandoc fragment conversion (joined as a single string)
    $htmlContent = (& pandoc -f markdown -t html $mdFile) -join "`n"
    $rewrittenHtml = $htmlContent -replace '\.\./media/', "$mediaUrl/"

    # Clean up existing page if present in Site Pages subfolder
    $existingTargetPage = Get-PnPPage -Identity $pagePath -ErrorAction SilentlyContinue
    if ($existingTargetPage) {
        Remove-PnPPage -Identity $pagePath -Force -ErrorAction SilentlyContinue
    }

    # Step 1: Create and publish Modern Page directly in Site Pages/CEISPilotKnowledgePages subfolder
    Write-Host "  Creating modern page $pageName in Site Pages/CEISPilotKnowledgePages..." -ForegroundColor Cyan
    $page = Add-PnPPage -Name $pagePath -Title $entry.title -LayoutType Article -Publish:$false
    Add-PnPPageTextPart -Page $page -Text $rewrittenHtml
    Set-PnPPage -Identity $page -Publish | Out-Null

    # Step 2: Set custom governance metadata on the published page item in Site Pages
    $item = Get-PnPListItem -List "Site Pages" -Query "<View Scope='RecursiveAll'><Query><Where><Eq><FieldRef Name='FileLeafRef'/><Value Type='Text'>$pageName</Value></Eq></Where></Query></View>" -ErrorAction SilentlyContinue
    if (-not $item) {
        $item = Get-PnPListItem -List "Site Pages" -ErrorAction SilentlyContinue | Where-Object { $_["FileLeafRef"] -eq $pageName }
    }
    $targetItem = if ($item -is [array]) { $item[0] } else { $item }

    if ($targetItem) {
        $itemValues = @{
            "TopicId"              = $entry.topic_id;
            "PackageIdentity"      = $entry.package_identity;
            "PublicationOrder"     = $entry.order;
            "TopicContentSHA256"   = $entry.topic_content_sha256;
            "SourceDocumentSHA256" = $entry.source_document_sha256;
        }
        $hasTitleField = Get-PnPField -List "Site Pages" -Identity "Title" -ErrorAction SilentlyContinue
        if ($hasTitleField) {
            $itemValues["Title"] = $entry.title
        }

        Set-PnPListItem -List "Site Pages" -Identity $targetItem.Id -Values $itemValues | Out-Null
    }

    Write-Host "  Published $pageName to Site Pages/CEISPilotKnowledgePages" -ForegroundColor Green
}

# 5. Export actual library state from Site Pages to CSV for reconciliation
Write-Host "Exporting tenant state from Site Pages to CSV at $OutputFile..." -ForegroundColor Cyan
$items = Get-PnPListItem -List "Site Pages" -Query "<View Scope='RecursiveAll'><Query><Where><IsNotNull><FieldRef Name='TopicId'/></Where></Query></View>" -Fields "FileLeafRef", "Title", "TopicId", "PackageIdentity", "PublicationOrder", "TopicContentSHA256", "SourceDocumentSHA256" -ErrorAction SilentlyContinue
if (-not $items -or $items.Count -eq 0) {
    $items = Get-PnPListItem -List "Site Pages" -Fields "FileLeafRef", "Title", "TopicId", "PackageIdentity", "PublicationOrder", "TopicContentSHA256", "SourceDocumentSHA256" -ErrorAction SilentlyContinue
}

$results = @()
foreach ($item in $items) {
    if ($item["TopicId"]) {
        $results += [PSCustomObject]@{
            "TopicId"              = $item["TopicId"]
            "Title"                = $item["Title"]
            "PackageIdentity"      = $item["PackageIdentity"]
            "PublicationOrder"     = $item["PublicationOrder"]
            "TopicContentSHA256"   = $item["TopicContentSHA256"]
            "SourceDocumentSHA256" = $item["SourceDocumentSHA256"]
        }
    }
}

$results | Export-Csv -Path $OutputFile -NoTypeInformation -Encoding UTF8
Write-Host "Task 5 execution complete! Exported $($results.Count) items to $OutputFile." -ForegroundColor Green
