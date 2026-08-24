<#
.SYNOPSIS
    READ-ONLY inventory of SKILL.md assets and knowledge pages on the pilot site using proven PnP authentication. Does NOT delete or modify any file.
#>
[CmdletBinding()]
param (
    [string]$ConfigFile = (Join-Path $PSScriptRoot '../../../config.psd1'),
    [string]$SitePagesLibraryName = "Site Pages",
    [string[]]$ExcludedSitePagesFiles = @("Home.aspx", "TopicHome.aspx", "Site-Links.aspx", "Chief-Sheriff-Messages.aspx", "ADM-Messages.aspx"),
    [string[]]$MediaFileExtensions = @("*.png", "*.jpeg", "*.jpg", "*.gif"),
    [string]$JsonOutputPath = ""
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $ConfigFile)) {
    Write-Error "Config file $ConfigFile not found. Copy config.psd1.example to config.psd1 and fill in tenant details."
    exit 1
}

$rawConfig = Import-PowerShellDataFile $ConfigFile
$config = if ($rawConfig.ContainsKey('Connection')) { $rawConfig.Connection } else { $rawConfig }
Import-Module PnP.PowerShell -ErrorAction Stop

# Proven PnP Connection Pattern
if ($config.ClientId -and $config.TenantId) {
    Connect-PnPOnline -Url $config.SiteUrl -ClientId $config.ClientId -Tenant $config.TenantId -Interactive
} else {
    Connect-PnPOnline -Url $config.SiteUrl -Interactive
}

Write-Host "Connected to $($config.SiteUrl). READ-ONLY inventorying of $($config.TargetLibrary)..." -ForegroundColor Green

$inventoryResult = [PSCustomObject]@{
    SiteUrl               = $config.SiteUrl
    TargetLibrary         = $config.TargetLibrary
    PilotKnowledgeLibrary = $config.PilotKnowledgeLibrary
    SkillAssetsFound      = @()
    KnowledgePagesFound   = @()
    MediaAssetsCount      = 0
    LibraryStatuses       = @{}
}

$targetLibraryName = if ($config.TargetLibrary) { 
    $config.TargetLibrary 
} elseif ($rawConfig.Defaults -and $rawConfig.Defaults.DefaultAgentAssetsLibrary) { 
    $rawConfig.Defaults.DefaultAgentAssetsLibrary 
} else { 
    "AgentAssets" 
}

# 1. Target Library (e.g. AgentAssets / Site Assets)
try {
    $targetList = Get-PnPList -Identity $targetLibraryName -ErrorAction SilentlyContinue
    if ($targetList) {
        $targetItems = Get-PnPListItem -List $targetList -PageSize 500
        $inventoryResult.LibraryStatuses[$targetLibraryName] = "EXISTS"
        Write-Host "Found $($targetItems.Count) item(s) in $targetLibraryName library."
        foreach ($item in $targetItems) {
            $fileName = $item["FileLeafRef"]
            if ($fileName -like "*SKILL*.md" -or $fileName -like "*.md" -or $fileName -like "*.agent") {
                Write-Host "  Found asset: $fileName (ID: $($item.Id), Path: $($item['FileRef']))" -ForegroundColor Green
                $inventoryResult.SkillAssetsFound += [PSCustomObject]@{
                    Id          = $item.Id
                    FileLeafRef = $fileName
                    FileRef     = $item["FileRef"]
                }
            }
        }
    } else {
        Write-Host "Target library '$targetLibraryName' does not exist on site." -ForegroundColor Yellow
        $inventoryResult.LibraryStatuses[$targetLibraryName] = "NOT_FOUND"
    }
} catch {
    Write-Host "Could not query '$targetLibraryName': $_" -ForegroundColor Yellow
    $inventoryResult.LibraryStatuses[$targetLibraryName] = "ERROR"
}

# Also check Site Assets if different
if ($targetLibraryName -ne "Site Assets") {
    try {
        $siteAssetsList = Get-PnPList -Identity "Site Assets" -ErrorAction SilentlyContinue
        if ($siteAssetsList) {
            $saItems = Get-PnPListItem -List $siteAssetsList -PageSize 500
            foreach ($item in $saItems) {
                $fileName = $item["FileLeafRef"]
                if ($fileName -like "*SKILL*.md" -or $fileName -like "*.md" -or $fileName -like "*.agent") {
                    Write-Host "  Found asset in Site Assets: $fileName (Path: $($item['FileRef']))" -ForegroundColor Green
                    $inventoryResult.SkillAssetsFound += [PSCustomObject]@{
                        Id          = $item.Id
                        FileLeafRef = $fileName
                        FileRef     = $item["FileRef"]
                    }
                }
            }
        }
    } catch {
        # ignore optional scan
    }
}

# 2. Pilot Knowledge / Site Pages
try {
    $sitePages = Get-PnPListItem -List $SitePagesLibraryName -PageSize 500
    $topicPages = $sitePages | Where-Object { $_["FileLeafRef"] -like "*.aspx" -and $ExcludedSitePagesFiles -notcontains $_["FileLeafRef"] }
    foreach ($tp in $topicPages) {
        $inventoryResult.KnowledgePagesFound += [PSCustomObject]@{
            Id          = $tp.Id
            FileLeafRef = $tp["FileLeafRef"]
            FileRef     = $tp["FileRef"]
        }
    }
    $inventoryResult.LibraryStatuses[$SitePagesLibraryName] = "EXISTS"
    Write-Host "Found $($topicPages.Count) ASPX topic pages in Site Pages."
} catch {
    $inventoryResult.LibraryStatuses[$SitePagesLibraryName] = "ERROR"
}

# 3. Media Assets
$mediaLibrary = if ($config.PilotKnowledgeLibrary) {
    $config.PilotKnowledgeLibrary
} elseif ($rawConfig.Defaults -and $rawConfig.Defaults.DefaultHumanPublicationLibrary) {
    $rawConfig.Defaults.DefaultHumanPublicationLibrary
} else {
    $null
}

if ($mediaLibrary) {
    try {
        $mediaItems = Get-PnPListItem -List $mediaLibrary -PageSize 500 -ErrorAction Stop
        $images = $mediaItems | Where-Object { $ext = $_["FileLeafRef"]; $MediaFileExtensions | Where-Object { $ext -like $_ } }
        $inventoryResult.MediaAssetsCount = $images.Count
        $inventoryResult.LibraryStatuses[$mediaLibrary] = "EXISTS"
        Write-Host "Found $($images.Count) media assets in $mediaLibrary."
    } catch {
        $inventoryResult.LibraryStatuses[$mediaLibrary] = "NOT_FOUND"
    }
}

if ($JsonOutputPath) {
    # Ensure directory exists
    $outDir = Split-Path -Path $JsonOutputPath -Parent
    if ($outDir -and -not (Test-Path $outDir)) {
        New-Item -ItemType Directory -Path $outDir -Force | Out-Null
    }
    $inventoryResult | ConvertTo-Json -Depth 5 | Out-File -FilePath $JsonOutputPath -Encoding utf8
    Write-Host "Raw inventory saved to $JsonOutputPath"
}

Disconnect-PnPOnline
