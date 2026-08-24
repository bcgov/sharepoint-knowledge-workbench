<#
.SYNOPSIS
    Read-only backup: downloads named .agent files from a SharePoint Site Pages folder to a
    local directory, so they exist as a reference before any tenant cleanup/recreation is
    considered. Makes no changes to the tenant.

.DESCRIPTION
    Idempotent and deterministic: always writes to the same fixed OutputDir (no timestamp in
    the default path) and overwrites each file's content on every run — rerunning refreshes
    the backup in place rather than accumulating dated folders.

.PARAMETER SitePath
    Site-relative path to the folder containing the .agent files (e.g.
    "SitePages/KnowledgePages").

.PARAMETER AgentFileNames
    Explicit list of .agent file names to back up. No hardcoded default — the caller (or a
    phase-specific thin wrapper) supplies the real target list.
#>
[CmdletBinding()]
param(
    [string]$ConfigFile = (Join-Path $PSScriptRoot '../../../config.psd1'),
    [Parameter(Mandatory = $true)]
    [string]$SitePath,
    [Parameter(Mandatory = $true)]
    [string[]]$AgentFileNames,
    [string]$OutputDir = "plugins/sharepoint-agents-and-skills/backups/agents"
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

New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null

foreach ($fileName in $AgentFileNames) {
    $sourceUrl = "$SitePath/$fileName"
    $destPath = Join-Path $OutputDir $fileName
    try {
        $content = Get-PnPFile -Url $sourceUrl -AsString
        Set-Content -Path $destPath -Value $content -Encoding UTF8
        Write-Host "  Backed up: $fileName" -ForegroundColor Green
    } catch {
        Write-Warning "Could not back up $fileName : $_"
    }
}

Write-Host "`nDone. Backups written to: $OutputDir" -ForegroundColor Green
