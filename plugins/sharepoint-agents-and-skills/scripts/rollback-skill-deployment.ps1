<#
.SYNOPSIS
    Human-authorized rollback procedure for removing deployed skill assets from SharePoint Site Assets / AgentAssets.
.DESCRIPTION
    By default runs in dry-run preflight mode. Requires explicit -Execute switch to attempt action.
    Displays exact target URL / path. Requires explicit -ConfirmExactTarget "CONFIRM-REMOVE" parameter for write path.
    Recycles target file to SharePoint Recycle Bin (Remove-PnPFile -Recycle) rather than permanent deletion,
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
    [string]$ConfigFile = "plugins/sharepoint-agents-and-skills/config.psd1",
    [string]$ManifestFile = "plugins/sharepoint-agents-and-skills/deployment-manifest.example.json",
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
    # Write evidence BEFORE Write-Error: under $ErrorActionPreference = "Stop", Write-Error is a
    # terminating error and the JSON-write below never ran until this fix (found via a real
    # pwsh-executed test on the sibling restore-sharepoint-native-skills.ps1, which copied this
    # same ordering bug).
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
    Write-Error "Execution denied: -Execute requires explicit -ConfirmExactTarget 'CONFIRM-REMOVE'. Provided: '$ConfirmExactTarget'"
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
    # $targetServerRelativeUrl built earlier is a library-title-relative path (e.g.
    # "AgentAssets/Skills/review-manual-topics/SKILL.md"), not a real server-relative path —
    # Remove-PnPFile/Get-PnPFile require the full site-relative path (e.g.
    # "/sites/AG-CSB-INTRANET-DEV/AgentAssets/Skills/review-manual-topics/SKILL.md"). Derive it
    # from the library's own RootFolder, same pattern reconcile-deployed-skill.ps1 uses.
    $targetLibrary = Get-PnPList -Identity $targetLibraryTitle -Includes RootFolder -ErrorAction Stop
    $realServerRelativeUrl = "$($targetLibrary.RootFolder.ServerRelativeUrl)/$targetRelativeFolder/$targetFilename"

    Write-Host "Recycling file '$realServerRelativeUrl' to SharePoint Recycle Bin..." -ForegroundColor Yellow
    Remove-PnPFile -ServerRelativeUrl $realServerRelativeUrl -Recycle -Force

    Write-Host "Performing post-action verification..." -ForegroundColor Cyan
    $remainingFile = Get-PnPFile -Url $realServerRelativeUrl -ErrorAction SilentlyContinue
    if ($remainingFile) {
        Write-Error "FAILURE: Target item '$realServerRelativeUrl' still exists in active site assets!"
        exit 1
    } else {
        Write-Host "SUCCESS: Verified target item '$realServerRelativeUrl' no longer exists in active site assets." -ForegroundColor Green
        if ($JsonOutputPath) {
            $resultObj = [PSCustomObject]@{
                status = "SUCCESS"
                mode = "EXECUTE"
                execute = $true
                target_server_relative_url = $realServerRelativeUrl
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
