<#
.SYNOPSIS
    Human-authorized rollback procedure for removing deployed skill assets from SharePoint Site Assets / AgentAssets.
.DESCRIPTION
    By default runs in dry-run preflight mode. Requires explicit -Execute switch to attempt action.
    Displays exact target URL / path. Requires explicit -ConfirmExactTarget "CONFIRM-REMOVE" parameter for write path.
    Recycles target file to SharePoint Recycle Bin (Move-PnPFileToRecycleBin) rather than permanent deletion (Remove-PnPFile),
    and performs post-action verification that item no longer exists in active site assets.
.PARAMETER ConfigFile
    Path to PSD1 configuration file.
.PARAMETER ManifestFile
    Path to deployment manifest JSON.
.PARAMETER Execute
    Switch to authorize tenant connection and removal. Default is false (dry-run preflight mode).
.PARAMETER ConfirmExactTarget
    Mandatory exact confirmation string required when -Execute is specified. Must match "CONFIRM-REMOVE" exactly.
.PARAMETER JsonOutputPath
    Optional path for writing structured JSON execution report.
#>
[CmdletBinding(ConfirmImpact="High", SupportsShouldProcess=$true)]
param (
    [string]$ConfigFile = "tools/phase-4-native-sharepoint-skills/config.psd1",
    [string]$ManifestFile = "tools/phase-4-native-sharepoint-skills/deployment/deployment-manifest.example.json",
    [switch]$Execute,
    [string]$ConfirmExactTarget,
    [string]$JsonOutputPath
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $ConfigFile)) {
    Write-Error "Configuration file '$ConfigFile' not found."
    exit 1
}

$config = Import-PowerShellDataFile -Path $ConfigFile

$targetLibraryTitle = "Site Assets"
$targetRelativeFolder = "Skills/review-manual-topics"
$targetFilename = "SKILL.md"

if (Test-Path $ManifestFile) {
    try {
        $manifest = Get-Content -Path $ManifestFile -Raw | ConvertFrom-Json
        if ($manifest.target_library) { $targetLibraryTitle = $manifest.target_library }
        if ($manifest.target_relative_folder) { $targetRelativeFolder = $manifest.target_relative_folder }
        if ($manifest.target_filename) { $targetFilename = $manifest.target_filename }
    } catch {
        Write-Warning "Failed to parse manifest $ManifestFile; using defaults."
    }
}

$targetServerRelativeUrl = "$targetLibraryTitle/$targetRelativeFolder/$targetFilename"
$siteUrl = $config.SiteUrl

Write-Host "=== Rollback Preflight Check ===" -ForegroundColor Cyan
Write-Host "  Target Site URL:             $siteUrl"
Write-Host "  Target Server Relative URL:  $targetServerRelativeUrl"
Write-Host "  Target Asset:                $targetLibraryTitle/$targetRelativeFolder/$targetFilename"

if (-not $Execute) {
    Write-Host "`n[DRY-RUN PREFLIGHT MODE] Zero tenant modifications performed because -Execute switch was not specified." -ForegroundColor Yellow
    Write-Host "  Would recycle asset: $targetServerRelativeUrl from $siteUrl"
    
    if ($JsonOutputPath) {
        $resultObj = [PSCustomObject]@{
            status = "NOT_EXECUTED"
            mode = "DRY_RUN_PREFLIGHT"
            execute = $false
            target_site_url = $siteUrl
            target_server_relative_url = $targetServerRelativeUrl
            action = "RECYCLE_TO_BIN"
            verification_result = "NOT_EXECUTED"
        }
        $resultObj | ConvertTo-Json -Depth 5 | Set-Content -Path $JsonOutputPath
    }
    exit 0
}

# Require explicit -ConfirmExactTarget "CONFIRM-REMOVE" when -Execute is specified
if ($ConfirmExactTarget -cne "CONFIRM-REMOVE") {
    Write-Error "Execution denied: -Execute requires explicit -ConfirmExactTarget 'CONFIRM-REMOVE'. Provided: '$ConfirmExactTarget'"
    if ($JsonOutputPath) {
        $resultObj = [PSCustomObject]@{
            status = "CANCELLED"
            mode = "EXECUTE"
            execute = $true
            target_server_relative_url = $targetServerRelativeUrl
            verification_result = "FAILED_AUTHORIZATION_CONFIRMATION"
        }
        $resultObj | ConvertTo-Json -Depth 5 | Set-Content -Path $JsonOutputPath
    }
    exit 1
}

Write-Host "`n[EXECUTION MODE] Connecting to SharePoint tenant to recycle skill artifact..." -ForegroundColor Green
Import-Module PnP.PowerShell -ErrorAction Stop

if ($config.ClientId -and $config.TenantId) {
    Connect-PnPOnline -Url $siteUrl -ClientId $config.ClientId -Tenant $config.TenantId -Interactive
} else {
    Connect-PnPOnline -Url $siteUrl -Interactive
}

try {
    Write-Host "Recycling file '$targetServerRelativeUrl' to SharePoint Recycle Bin..." -ForegroundColor Yellow
    Move-PnPFileToRecycleBin -ServerRelativeUrl $targetServerRelativeUrl -Force

    Write-Host "Performing post-action verification..." -ForegroundColor Cyan
    $remainingFile = Get-PnPFile -Url $targetServerRelativeUrl -ErrorAction SilentlyContinue
    if ($remainingFile) {
        Write-Error "FAILURE: Target item '$targetServerRelativeUrl' still exists in active site assets!"
        exit 1
    } else {
        Write-Host "SUCCESS: Verified target item '$targetServerRelativeUrl' no longer exists in active site assets." -ForegroundColor Green
        if ($JsonOutputPath) {
            $resultObj = [PSCustomObject]@{
                status = "SUCCESS"
                mode = "EXECUTE"
                execute = $true
                target_server_relative_url = $targetServerRelativeUrl
                recycled = $true
                verification_result = "PASS"
            }
            $resultObj | ConvertTo-Json -Depth 5 | Set-Content -Path $JsonOutputPath
        }
        exit 0
    }
} finally {
    Disconnect-PnPOnline
}
