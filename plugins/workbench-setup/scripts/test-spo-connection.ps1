<#
.SYNOPSIS
Minimal SharePoint Online connection test — interactive (delegated) auth
only, no network pre-flight. For the fuller check (network reachability +
this same auth test), use test-network-connectivity.ps1 instead.

.PARAMETER ConfigPath
Path to config.psd1. Defaults to this repository's root config.psd1.
Supports both setup-sharepoint-connection's nested `Connection = @{...}`
schema and a flat top-level ClientId/TenantId/SiteUrl schema.
#>
param(
    [string]$ConfigPath = ""
)

if (-not $ConfigPath -or -not (Test-Path $ConfigPath)) {
    $candidates = @(
        "$PWD\config.psd1",
        "$PSScriptRoot\config.psd1",
        "$PSScriptRoot\..\config.psd1",
        "$PSScriptRoot\..\..\config.psd1",
        "$PSScriptRoot\..\..\..\config.psd1",
        "$PSScriptRoot\..\..\..\..\config.psd1"
    )
    foreach ($cand in $candidates) {
        if (Test-Path $cand) {
            $ConfigPath = (Resolve-Path $cand).Path
            break
        }
    }
}

if (-not (Test-Path $ConfigPath)) {
    Write-Error "Could not locate config.psd1. Please specify -ConfigPath <path> or run from a directory containing config.psd1."
    exit 1
}

$raw = Import-PowerShellDataFile $ConfigPath
$cfg = if ($raw.ContainsKey('Connection')) { $raw.Connection } else { $raw }

Write-Host ""
Write-Host "=== SPO Connection Test — Interactive (Delegated) ===" -ForegroundColor Cyan
Write-Host "Site     : $($cfg.SiteUrl)" -ForegroundColor Gray
Write-Host "ClientId : $($cfg.ClientId)" -ForegroundColor Gray
Write-Host ""
Write-Host "A browser window will open — sign in with your account." -ForegroundColor Yellow
Write-Host ""

try {
    Connect-PnPOnline -Url $cfg.SiteUrl -ClientId $cfg.ClientId -Tenant $cfg.TenantId -Interactive
    $web = Get-PnPWeb
    Write-Host "CONNECTED — Site title: $($web.Title)" -ForegroundColor Green
    Disconnect-PnPOnline -ErrorAction SilentlyContinue
}
catch {
    Write-Host "FAILED: $_" -ForegroundColor Red
    exit 1
}
