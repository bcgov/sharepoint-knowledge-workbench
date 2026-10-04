<#
.SYNOPSIS
    Restore .agent files from a local backup (produced by backup-sharepoint-agents.ps1) back to
    their tenant locations.

.DESCRIPTION
    Dry-run by default. Requires -Execute plus -ConfirmExactTarget "CONFIRM-RESTORE" before
    uploading anything. Mirrors restore-sharepoint-native-skills.ps1's pattern exactly (same
    safety gate, same Items shape) -- new build, no prior implementation in this repository.

.PARAMETER Items
    Explicit list of hashtables with LocalPath (backup file) and Url (target site-relative path,
    e.g. "SitePages/MyFolder/agent-name.agent") keys. No hardcoded default.
#>
[CmdletBinding(ConfirmImpact = "High", SupportsShouldProcess = $true)]
param(
    [string]$ConfigFile = (Join-Path $PSScriptRoot '../../../config.psd1'),
    [object[]]$Items,
    [string]$LocalPath,
    [string]$Url,
    [switch]$Execute,
    [string]$ConfirmExactTarget,
    [string]$JsonOutputPath
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $ConfigFile)) {
    Write-Error "Config file not found: $ConfigFile. Copy config.psd1.example to config.psd1 and fill in ClientId/TenantId/SiteUrl."
    exit 1
}

# Allow passing single file via -LocalPath and -Url directly
if ($LocalPath -and $Url) {
    $Items = @( [PSCustomObject]@{ LocalPath = $LocalPath; Url = $Url } )
}

if (-not $Items -or $Items.Count -eq 0) {
    Write-Error "Either -Items @( @{ LocalPath='...'; Url='...' } ) or both -LocalPath and -Url are required."
    exit 1
}

$normalizedItems = @()
foreach ($item in $Items) {
    $loc = $null
    $targetUrl = $null

    if ($null -ne $item) {
        if ($item -is [System.Collections.IDictionary] -or $item -is [hashtable]) {
            $loc = if ($item.ContainsKey('LocalPath')) { $item['LocalPath'] } else { $item.LocalPath }
            $targetUrl = if ($item.ContainsKey('Url')) { $item['Url'] } else { $item.Url }
        } elseif ($item -is [PSCustomObject]) {
            $loc = $item.LocalPath
            $targetUrl = $item.Url
        } else {
            # Try reflection/properties first
            try {
                $loc = $item.LocalPath
                $targetUrl = $item.Url
            } catch {}
            
            # String fallback
            if (-not $loc) {
                $itemStr = "$item"
                if ($itemStr -match "LocalPath=['""]?([^;'""}]+)['""]?") { $loc = $matches[1].Trim() }
                if ($itemStr -match "Url=['""]?([^;'""}]+)['""]?") { $targetUrl = $matches[1].Trim() }
                if (-not $loc -and (Test-Path $itemStr)) { $loc = $itemStr }
            }
        }
    }

    if (-not $loc -or -not (Test-Path $loc)) {
        Write-Error "Backup file not found: '$loc'. Cannot restore from a missing source."
        exit 1
    }
    $normalizedItems += [PSCustomObject]@{
        LocalPath = $loc
        Url       = $targetUrl
    }
}
$Items = $normalizedItems

Write-Host "=== Restore Preflight Check ===" -ForegroundColor Cyan
foreach ($item in $Items) {
    Write-Host "  Would restore: $($item.LocalPath) -> $($item.Url)"
}

if (-not $Execute) {
    Write-Host "`n[DRY-RUN PREFLIGHT MODE] Zero tenant writes performed because -Execute switch was not specified." -ForegroundColor Yellow
    if ($JsonOutputPath) {
        $resultObj = [PSCustomObject]@{ status = "NOT_EXECUTED"; mode = "DRY_RUN_PREFLIGHT"; execute = $false; items = $Items }
        $resultObj | ConvertTo-Json -Depth 5 | Set-Content -Path $JsonOutputPath
    }
    exit 0
}

if ($ConfirmExactTarget -cne "CONFIRM-RESTORE") {
    if ($JsonOutputPath) {
        $resultObj = [PSCustomObject]@{ status = "CANCELLED"; mode = "EXECUTE"; execute = $true; verification_result = "FAILED_AUTHORIZATION_CONFIRMATION" }
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
    $resultObj = [PSCustomObject]@{ status = "EXECUTED"; mode = "EXECUTE"; execute = $true; results = $results }
    $resultObj | ConvertTo-Json -Depth 5 | Set-Content -Path $JsonOutputPath
}

Write-Host "`nDone." -ForegroundColor Green
Disconnect-PnPOnline
