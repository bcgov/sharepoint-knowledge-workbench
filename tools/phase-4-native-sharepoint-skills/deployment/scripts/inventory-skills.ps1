<#
.SYNOPSIS
    READ-ONLY inventory of SKILL.md assets and knowledge pages on the pilot site using proven PnP authentication. Does NOT delete or modify any file.
#>
[CmdletBinding()]
param (
    [string]$ConfigFile = "tools/phase-4-native-sharepoint-skills/config.psd1",
    [string]$JsonOutputPath = ""
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $ConfigFile)) {
    Write-Error "Config file $ConfigFile not found. Copy config.psd1.example to config.psd1 and fill in tenant details."
    exit 1
}

$config = Import-PowerShellDataFile $ConfigFile
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

# 1. Target Library (AgentAssets)
try {
    $targetItems = Get-PnPListItem -List $config.TargetLibrary -PageSize 500
    $inventoryResult.LibraryStatuses[$config.TargetLibrary] = "EXISTS"
    Write-Host "Found $($targetItems.Count) items in $($config.TargetLibrary)."
    foreach ($item in $targetItems) {
        $fileName = $item["FileLeafRef"]
        if ($fileName -like "*SKILL*.md" -or $fileName -like "TEST-DO-NOT-USE-*" -or $fileName -like "*.md") {
            Write-Host "Skill asset: $fileName (ID: $($item.Id), Path: $($item['FileRef']))"
            $inventoryResult.SkillAssetsFound += [PSCustomObject]@{
                Id          = $item.Id
                FileLeafRef = $fileName
                FileRef     = $item["FileRef"]
            }
        }
    }
} catch {
    Write-Host "Target library '$($config.TargetLibrary)' does not exist on site yet." -ForegroundColor Yellow
    $inventoryResult.LibraryStatuses[$config.TargetLibrary] = "NOT_FOUND"
}

# 2. Pilot Knowledge / Site Pages
try {
    $sitePages = Get-PnPListItem -List "Site Pages" -PageSize 500
    $topicPages = $sitePages | Where-Object { $_["FileLeafRef"] -like "*.aspx" -and $_["FileLeafRef"] -ne "Home.aspx" -and $_["FileLeafRef"] -ne "TopicHome.aspx" -and $_["FileLeafRef"] -ne "Site-Links.aspx" -and $_["FileLeafRef"] -ne "Chief-Sheriff-Messages.aspx" -and $_["FileLeafRef"] -ne "ADM-Messages.aspx" }
    foreach ($tp in $topicPages) {
        $inventoryResult.KnowledgePagesFound += [PSCustomObject]@{
            Id          = $tp.Id
            FileLeafRef = $tp["FileLeafRef"]
            FileRef     = $tp["FileRef"]
        }
    }
    $inventoryResult.LibraryStatuses["SitePages"] = "EXISTS"
    Write-Host "Found $($topicPages.Count) ASPX topic pages in Site Pages."
} catch {
    $inventoryResult.LibraryStatuses["SitePages"] = "ERROR"
}

# 3. Media Assets
try {
    $mediaItems = Get-PnPListItem -List "CEIS-Pilot-Knowledge" -PageSize 500
    $images = $mediaItems | Where-Object { $_["FileLeafRef"] -like "*.png" -or $_["FileLeafRef"] -like "*.jpeg" -or $_["FileLeafRef"] -like "*.jpg" -or $_["FileLeafRef"] -like "*.gif" }
    $inventoryResult.MediaAssetsCount = $images.Count
    $inventoryResult.LibraryStatuses["CEIS-Pilot-Knowledge"] = "EXISTS"
    Write-Host "Found $($images.Count) media assets in CEIS-Pilot-Knowledge."
} catch {
    $inventoryResult.LibraryStatuses["CEIS-Pilot-Knowledge"] = "NOT_FOUND"
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
