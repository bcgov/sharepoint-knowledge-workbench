<#
.SYNOPSIS
    Find exact location of CEIS content to place agent correctly

.EXAMPLE
    .\find-ceis-location.ps1
#>

[CmdletBinding()]
param(
    [string]$ConfigFile = "tools/phase-4-native-sharepoint-skills/config.psd1"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $ConfigFile)) {
    Write-Error "Config file $ConfigFile not found."
    exit 1
}

$config = Import-PowerShellDataFile $ConfigFile
Import-Module PnP.PowerShell -ErrorAction Stop

Write-Host "Connecting..." -ForegroundColor Cyan
$hasValidAppReg = ($config.ClientId -and $config.TenantId -and `
    $config.ClientId -notlike "*test*" -and $config.TenantId -notlike "*test*")

if ($hasValidAppReg) {
    Connect-PnPOnline -Url $config.SiteUrl -ClientId $config.ClientId -Tenant $config.TenantId -Interactive -ForceAuthentication -ErrorAction Stop
} else {
    $phase3Config = Import-PowerShellDataFile "../../tools/phase-3-sharepoint-discovery/config.psd1"
    Connect-PnPOnline -Url $config.SiteUrl -ClientId $phase3Config.ClientId -Tenant $phase3Config.TenantId -Interactive -ForceAuthentication -ErrorAction Stop
}

Write-Host "Finding CEIS content location..." -ForegroundColor Cyan

# List all libraries
$lists = Get-PnPList -Includes BaseTemplate | Where-Object { $_.BaseTemplate -eq 101 -or $_.Title -like "*CEIS*" }

foreach ($list in $lists) {
    Write-Host "Library: $($list.Title)" -ForegroundColor Green
    Write-Host "  URL: $($list.RootFolder.ServerRelativeUrl)" -ForegroundColor Cyan

    # Try to find CEIS content
    try {
        $items = Get-PnPListItem -List $list.Id -PageSize 10 -ErrorAction SilentlyContinue
        if ($items) {
            Write-Host "  Items found: $($items.Count)" -ForegroundColor Cyan
            foreach ($item in $items | Select-Object -First 3) {
                Write-Host "    - $($item['FileLeafRef'])" -ForegroundColor Gray
            }
        }
    } catch {}
}

Write-Host ""
Write-Host "Check SharePoint directly:" -ForegroundColor Yellow
Write-Host "1. Navigate to: https://bcgov.sharepoint.com/sites/AG-CSB-INTRANET-DEV/" -ForegroundColor Yellow
Write-Host "2. Look for 'CEISPilotKnowledgePages' library" -ForegroundColor Yellow
Write-Host "3. Report the exact library name you see" -ForegroundColor Yellow

Disconnect-PnPOnline
