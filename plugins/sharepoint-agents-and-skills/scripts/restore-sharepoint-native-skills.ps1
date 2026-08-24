<#
.SYNOPSIS
    Restore native-skill/template files from a local backup (produced by
    backup-sharepoint-native-skills.ps1) back to their AgentAssets tenant locations.

.DESCRIPTION
    Dry-run by default -- displays exactly what would be restored with zero tenant writes.
    Requires -Execute plus -ConfirmExactTarget "CONFIRM-RESTORE" (exact match) before uploading
    anything. Mirrors backup-sharepoint-native-skills.ps1's Items shape and
    rollback-skill-deployment.ps1's safety-gate pattern.

.PARAMETER Items
    Explicit list of hashtables with LocalPath (backup file to restore from) and Url
    (AgentAssets-relative or server-relative target path to restore to) keys. No hardcoded
    default -- the caller supplies the real target list.
#>
[CmdletBinding(ConfirmImpact = "High", SupportsShouldProcess = $true)]
param(
    [string]$ConfigFile = (Join-Path $PSScriptRoot '../../../config.psd1'),
    [Parameter(Mandatory = $true)]
    [hashtable[]]$Items,
    [switch]$Execute,
    [string]$ConfirmExactTarget,
    [string]$JsonOutputPath
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $ConfigFile)) {
    Write-Error "Config file not found: $ConfigFile. Copy config.psd1.example to config.psd1 and fill in ClientId/TenantId/SiteUrl."
    exit 1
}

foreach ($item in $Items) {
    if (-not (Test-Path $item.LocalPath)) {
        Write-Error "Backup file not found: $($item.LocalPath). Cannot restore from a missing source."
        exit 1
    }
}

Write-Host "=== Restore Preflight Check ===" -ForegroundColor Cyan
foreach ($item in $Items) {
    Write-Host "  Would restore: $($item.LocalPath) -> $($item.Url)"
}

if (-not $Execute) {
    Write-Host "`n[DRY-RUN PREFLIGHT MODE] Zero tenant writes performed because -Execute switch was not specified." -ForegroundColor Yellow
    if ($JsonOutputPath) {
        $resultObj = [PSCustomObject]@{
            status  = "NOT_EXECUTED"
            mode    = "DRY_RUN_PREFLIGHT"
            execute = $false
            items   = $Items
        }
        $resultObj | ConvertTo-Json -Depth 5 | Set-Content -Path $JsonOutputPath
    }
    exit 0
}

if ($ConfirmExactTarget -cne "CONFIRM-RESTORE") {
    # Write evidence BEFORE Write-Error: under $ErrorActionPreference = "Stop", Write-Error is a
    # terminating error -- any code after it in this script never executes. (Confirmed by direct
    # test; this same ordering bug was found and fixed here after discovering it also exists,
    # unfixed, in rollback-skill-deployment.ps1 -- see that script's own fix in this same commit.)
    if ($JsonOutputPath) {
        $resultObj = [PSCustomObject]@{
            status              = "CANCELLED"
            mode                = "EXECUTE"
            execute             = $true
            verification_result = "FAILED_AUTHORIZATION_CONFIRMATION"
        }
        $resultObj | ConvertTo-Json -Depth 5 | Set-Content -Path $JsonOutputPath
    }
    Write-Error "Execution denied: -Execute requires explicit -ConfirmExactTarget 'CONFIRM-RESTORE'. Provided: '$ConfirmExactTarget'"
    exit 1
}

$rawConfig = Import-PowerShellDataFile -Path $ConfigFile
$config = if ($rawConfig.ContainsKey('Connection')) { $rawConfig.Connection } else { $rawConfig }
Connect-PnPOnline -Url $config.SiteUrl -ClientId $config.ClientId -Tenant $config.TenantId -Interactive -ForceAuthentication -ErrorAction Stop
Write-Host "Connected successfully!" -ForegroundColor Green

$results = @()
foreach ($item in $Items) {
    try {
        $folder = Split-Path -Path $item.Url -Parent
        $filename = Split-Path -Path $item.Url -Leaf
        Add-PnPFile -Path $item.LocalPath -Folder $folder -NewFileName $filename -ErrorAction Stop | Out-Null
        Write-Host "  Restored: $($item.Url)" -ForegroundColor Green
        $results += [PSCustomObject]@{ Url = $item.Url; Status = "RESTORED" }
    } catch {
        Write-Warning "Could not restore $($item.Url): $_"
        $results += [PSCustomObject]@{ Url = $item.Url; Status = "FAILED"; Error = "$_" }
    }
}

if ($JsonOutputPath) {
    $resultObj = [PSCustomObject]@{
        status  = "EXECUTED"
        mode    = "EXECUTE"
        execute = $true
        results = $results
    }
    $resultObj | ConvertTo-Json -Depth 5 | Set-Content -Path $JsonOutputPath
}

Write-Host "`nDone." -ForegroundColor Green
Disconnect-PnPOnline
