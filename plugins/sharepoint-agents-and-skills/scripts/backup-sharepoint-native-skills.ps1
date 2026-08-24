<#
.SYNOPSIS
    Read-only backup: downloads named AgentAssets skill/template files from a SharePoint tenant
    to a local directory, as a precaution before any tenant cleanup is considered. Makes no
    changes to the tenant.

.DESCRIPTION
    Idempotent and deterministic: always writes to the same fixed OutputDir (no timestamp in
    the default path) and overwrites each file's content on every run.

.PARAMETER Items
    Explicit list of hashtables with Url (server-relative or AgentAssets-relative source path)
    and Dest (relative destination path under OutputDir) keys. No hardcoded default — the
    caller (or a phase-specific thin wrapper) supplies the real target list.
#>
[CmdletBinding()]
param(
    [string]$ConfigFile = (Join-Path $PSScriptRoot '../../../config.psd1'),
    [Parameter(Mandatory = $true)]
    [hashtable[]]$Items,
    [string]$OutputDir = "plugins/sharepoint-agents-and-skills/backups/native-skills"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $ConfigFile)) {
    Write-Error "Config file not found: $ConfigFile. Copy config.psd1.example to config.psd1 and fill in ClientId/TenantId/SiteUrl."
    exit 1
}

$rawConfig = Import-PowerShellDataFile -Path $ConfigFile
$config = if ($rawConfig.ContainsKey('Connection')) { $rawConfig.Connection } else { $rawConfig }
Connect-PnPOnline -Url $config.SiteUrl -ClientId $config.ClientId -Tenant $config.TenantId -Interactive -ForceAuthentication -ErrorAction Stop
Write-Host "Connected successfully!" -ForegroundColor Green

foreach ($item in $Items) {
    $destPath = Join-Path $OutputDir $item.Dest
    $destDir = Split-Path -Path $destPath -Parent
    if ($destDir -and -not (Test-Path $destDir)) {
        New-Item -ItemType Directory -Path $destDir -Force | Out-Null
    }
    try {
        $content = Get-PnPFile -Url $item.Url -AsString
        Set-Content -Path $destPath -Value $content -Encoding UTF8
        Write-Host "  Backed up: $($item.Url)" -ForegroundColor Green
    } catch {
        Write-Warning "Could not back up $($item.Url): $_"
    }
}

Write-Host "`nDone. Backups written to: $OutputDir" -ForegroundColor Green
