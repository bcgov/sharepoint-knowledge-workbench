<#
.SYNOPSIS
    Diagnostic script to inspect SharePoint libraries and their contents

.DESCRIPTION
    Read-only inspection tool for troubleshooting SharePoint library structure.
    Lists all libraries on the site, or inspects a specific library in detail.
    Useful for verifying library names, IDs, and content structure.

.PARAMETER ConfigFile
    Path to config.psd1 with SiteUrl, ClientId, TenantId

.PARAMETER LibraryName
    Specific library to inspect (optional). If omitted, lists all libraries.

.PARAMETER Detailed
    Include detailed item information (Title, FileRef, created date, modified date)

.EXAMPLE
    # List all libraries
    .\diagnose-sharepoint-library.ps1

.EXAMPLE
    # Inspect specific library in detail
    .\diagnose-sharepoint-library.ps1 -LibraryName "CEISPilotKnowledgePages" -Detailed

.EXAMPLE
    # Inspect AgentAssets library
    .\diagnose-sharepoint-library.ps1 -LibraryName "AgentAssets"
#>

[CmdletBinding()]
param(
    [string]$ConfigFile = "tools/phase-4-native-sharepoint-skills/config.psd1",
    [string]$LibraryName,
    [switch]$Detailed
)

$ErrorActionPreference = "Stop"

Write-Host "=== SHAREPOINT LIBRARY DIAGNOSTIC ===" -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Path $ConfigFile)) {
    Write-Error "Config file not found: $ConfigFile"
    exit 1
}

$config = Import-PowerShellDataFile $ConfigFile
Import-Module PnP.PowerShell -ErrorAction Stop

Write-Host "Connecting to: $($config.SiteUrl)" -ForegroundColor Cyan
try {
    $hasValidAppReg = ($config.ClientId -and $config.TenantId -and `
        $config.ClientId -notlike "*test*" -and $config.ClientId -notlike "*example*" -and `
        $config.TenantId -notlike "*test*" -and $config.TenantId -notlike "*example*")

    if ($hasValidAppReg) {
        Connect-PnPOnline -Url $config.SiteUrl -ClientId $config.ClientId -Tenant $config.TenantId -Interactive -ErrorAction Stop
    } else {
        $phase3ConfigPath = "../../tools/phase-3-sharepoint-discovery/config.psd1"
        if (Test-Path $phase3ConfigPath) {
            Write-Host "Using Phase 3 credentials..." -ForegroundColor Yellow
            $phase3Config = Import-PowerShellDataFile $phase3ConfigPath
            Connect-PnPOnline -Url $config.SiteUrl -ClientId $phase3Config.ClientId -Tenant $phase3Config.TenantId -Interactive -ErrorAction Stop
        } else {
            Write-Error "No valid authentication available."
            exit 1
        }
    }

    Write-Host "✓ Connected" -ForegroundColor Green
    Write-Host ""

    if ($LibraryName) {
        # Inspect specific library
        Write-Host "Inspecting library: '$LibraryName'" -ForegroundColor Cyan
        Write-Host ""

        $list = Get-PnPList -Identity $LibraryName -ErrorAction Stop

        Write-Host "Library Details:" -ForegroundColor Green
        Write-Host "  Title: $($list.Title)" -ForegroundColor White
        Write-Host "  URL: $($list.RootFolder.ServerRelativeUrl)" -ForegroundColor White
        Write-Host "  ID: $($list.Id)" -ForegroundColor Gray
        Write-Host "  BaseTemplate: $($list.BaseTemplate)" -ForegroundColor Gray
        Write-Host "  ItemCount: $($list.ItemCount)" -ForegroundColor Gray
        Write-Host ""

        if ($list.ItemCount -gt 0) {
            Write-Host "Items in library:" -ForegroundColor Green
            $items = Get-PnPListItem -List $list -PageSize 100

            if ($Detailed) {
                $items | ForEach-Object {
                    Write-Host "  ID: $($_.Id)" -ForegroundColor White
                    Write-Host "    Title: $($_.FieldValues.Title)" -ForegroundColor Gray
                    Write-Host "    FileRef: $($_.FieldValues.FileRef)" -ForegroundColor Gray
                    Write-Host "    Created: $($_.FieldValues.Created)" -ForegroundColor Gray
                    Write-Host "    Modified: $($_.FieldValues.Modified)" -ForegroundColor Gray
                    Write-Host ""
                }
            } else {
                $items | ForEach-Object {
                    $title = if ([string]::IsNullOrWhiteSpace($_.FieldValues.Title)) { "[NO TITLE]" } else { $_.FieldValues.Title }
                    Write-Host "  ID: $($_.Id) | Title: $title | FileRef: $($_.FieldValues.FileRef)" -ForegroundColor Gray
                }
            }
        } else {
            Write-Host "  [Library is empty]" -ForegroundColor Yellow
        }

        # Show available fields/columns
        Write-Host ""
        Write-Host "Available fields/columns:" -ForegroundColor Green
        $fields = Get-PnPField -List $list
        $fields | ForEach-Object {
            if (-not $_.Hidden -and -not $_.InternalName.StartsWith("_")) {
                Write-Host "  - $($_.InternalName) ($($_.TypeAsString))" -ForegroundColor Gray
            }
        }

    } else {
        # List all libraries
        Write-Host "All libraries on site:" -ForegroundColor Green
        Write-Host ""

        $allLists = Get-PnPList

        $allLists | ForEach-Object {
            Write-Host "Library: $($_.Title)" -ForegroundColor White
            Write-Host "  URL: $($_.RootFolder.ServerRelativeUrl)" -ForegroundColor Gray
            Write-Host "  ID: $($_.Id)" -ForegroundColor Gray
            Write-Host "  Type: $($_.BaseTemplate)" -ForegroundColor Gray
            Write-Host "  Items: $($_.ItemCount)" -ForegroundColor Gray
            Write-Host ""
        }
    }

    Write-Host "✓ Diagnostic complete" -ForegroundColor Green

} catch {
    Write-Error "Error: $_"
    exit 1
} finally {
    Disconnect-PnPOnline -ErrorAction SilentlyContinue
}
