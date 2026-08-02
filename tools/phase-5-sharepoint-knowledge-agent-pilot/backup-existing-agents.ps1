<#
.SYNOPSIS
    Read-only backup: downloads the 5 existing .agent files from
    SitePages/CEISPilotKnowledgePages on AG-CSB-INTRANET-DEV to a local directory, so they
    exist as a reference before any tenant cleanup/recreation is considered. Makes no changes
    to the tenant.

    Idempotent and deterministic: always writes to the same fixed OutputDir (no timestamp in
    the default path) and overwrites each file's content on every run — rerunning refreshes
    the backup in place rather than accumulating dated folders.
#>

[CmdletBinding()]
param(
    [string]$ConfigPath = (Join-Path $PSScriptRoot "config.psd1"),
    [string]$OutputDir = (Join-Path $PSScriptRoot "backups/agents")
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $ConfigPath)) {
    Write-Error "Config file not found: $ConfigPath. Copy config.psd1.example to config.psd1 and fill in ClientId/TenantId/SiteUrl."
    exit 1
}

$config = Import-PowerShellDataFile -Path $ConfigPath
Connect-PnPOnline -Url $config.SiteUrl -ClientId $config.ClientId -Tenant $config.TenantId -Interactive -ForceAuthentication -ErrorAction Stop
Write-Host "Connected successfully!" -ForegroundColor Green

New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null

$agentFiles = @(
    "CEIS-Pilot-Knowledge-Agent.agent",
    "CEIS-Pilot-Knowledge-Agent-Corrected.agent",
    "CEIS-ASPX-Only-Test.agent",
    "CEIS-Topic-Reviewer-with-Skills.agent",
    "CEISPilotKnowledgePages-manuallycreated.agent"
)

foreach ($fileName in $agentFiles) {
    $sourceUrl = "/sites/AG-CSB-INTRANET-DEV/SitePages/CEISPilotKnowledgePages/$fileName"
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
