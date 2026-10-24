<#
.SYNOPSIS
    Read-only: retrieve the exact site_id/web_id/list_id/unique_id a SharePoint agent's
    knowledge-source entry needs for a given site/folder.

.DESCRIPTION
    Extracted from a previously manual-only method (see docs/research/phase-4-agent-format-
    learning-journal.md and PHASE-4-SHAREPOINT-AGENTS-CRITICAL-LEARNINGS.md): the confirmed
    working approach for fixing site-isolation bugs was to extract these IDs from a working
    reference agent by hand, every time. This script does the same PnP queries the manual
    process used, as a real, reusable, read-only capability.

.PARAMETER ConfigFile
    Connection/authentication context only.

.PARAMETER FolderSiteRelativePath
    The site-relative folder path to resolve (e.g. "SitePages/MyFolder" or a document library
    name). Required.

.PARAMETER JsonOutputPath
    Optional path to write the resolved identifiers as JSON, ready to paste into a
    -KnowledgeSourcePaths-adjacent knowledge-source block.
#>
[CmdletBinding()]
param(
    [string]$ConfigFile = (Join-Path $PSScriptRoot '../../../config.psd1'),
    [Parameter(Mandatory = $true)]
    [string]$FolderSiteRelativePath,
    [string]$JsonOutputPath
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $ConfigFile)) {
    Write-Error "Config file not found: $ConfigFile."
    exit 1
}

$rawConfig = Import-PowerShellDataFile -Path $ConfigFile
$config = if ($rawConfig.ContainsKey('Connection')) { $rawConfig.Connection } else { $rawConfig }
Import-Module PnP.PowerShell -ErrorAction Stop
Connect-PnPOnline -Url $config.SiteUrl -ClientId $config.ClientId -Tenant $config.TenantId -Interactive -ErrorAction Stop
Write-Host "Connected to: $($config.SiteUrl)" -ForegroundColor Green

try {
    $site = Get-PnPSite -ErrorAction Stop
    $web = Get-PnPWeb -ErrorAction Stop
    $siteId = $site.Id.Guid
    $webId = $web.Id.Guid

    Write-Host "  site_id: $siteId" -ForegroundColor Cyan
    Write-Host "  web_id:  $webId" -ForegroundColor Cyan

    $listId = $null
    $uniqueId = "00000000-0000-0000-0000-000000000000"
    $type = "Folder"

    # Check if target is a Custom List
    if ($FolderSiteRelativePath -match "^Lists/([^/]+)") {
        $listName = $matches[1]
        $type = "List"
        try {
            $list = Get-PnPList -Identity $listName -ErrorAction Stop
            $listId = $list.Id.Guid
            Write-Host "  list_id (List): $listId" -ForegroundColor Cyan
        } catch {
            Write-Warning "Could not resolve list_id for List '$listName': $_"
        }
    } else {
        # Target is a Document Library or subfolder
        $type = "Folder"
        $libraryName = ($FolderSiteRelativePath -split '/')[0]
        try {
            $list = Get-PnPList -Identity $libraryName -ErrorAction Stop
            $listId = $list.Id.Guid
            Write-Host "  list_id:   $listId" -ForegroundColor Cyan
        } catch {
            Write-Warning "Could not resolve list_id for Library '$libraryName': $_"
        }

        try {
            $folder = Get-PnPFolder -Url $FolderSiteRelativePath -ErrorAction Stop -Includes ListItemAllFields, UniqueId
            if ($folder.UniqueId) {
                $uniqueId = $folder.UniqueId.Guid
                Write-Host "  unique_id: $uniqueId" -ForegroundColor Cyan
            }
        } catch {
            Write-Warning "Could not resolve unique_id for folder '$FolderSiteRelativePath' (defaulting to zero GUID): $_"
        }
    }

    $result = [PSCustomObject]@{
        url         = "$($config.SiteUrl)/$FolderSiteRelativePath"
        name        = Split-Path -Path $FolderSiteRelativePath -Leaf
        site_id     = $siteId
        web_id      = $webId
        list_id     = $(if ($listId) { $listId } else { "00000000-0000-0000-0000-000000000000" })
        unique_id   = $uniqueId
        type        = $type
    }

    if ($JsonOutputPath) {
        $result | ConvertTo-Json -Depth 5 | Set-Content -Path $JsonOutputPath
        Write-Host "Written to: $JsonOutputPath" -ForegroundColor Green
    }

    $result
} finally {
    Disconnect-PnPOnline -ErrorAction SilentlyContinue
}
