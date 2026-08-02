<#
.SYNOPSIS
    Read-only backup: downloads the Phase 4 AgentAssets skills/template (ceis-test-skill,
    review-manual-topics, ceis-procedure-review-template.md) from AG-CSB-INTRANET-DEV to a
    local directory, as a precaution — these are real Phase 4 deliverables and are explicitly
    NOT in scope for any deletion. Makes no changes to the tenant.

    Idempotent and deterministic: always writes to the same fixed OutputDir (no timestamp in
    the default path) and overwrites each file's content on every run.
#>

[CmdletBinding()]
param(
    [string]$ConfigPath = (Join-Path $PSScriptRoot "config.psd1"),
    [string]$OutputDir = (Join-Path $PSScriptRoot "backups/skills")
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $ConfigPath)) {
    Write-Error "Config file not found: $ConfigPath. Copy config.psd1.example to config.psd1 and fill in ClientId/TenantId/SiteUrl."
    exit 1
}

$config = Import-PowerShellDataFile -Path $ConfigPath
Connect-PnPOnline -Url $config.SiteUrl -ClientId $config.ClientId -Tenant $config.TenantId -Interactive -ForceAuthentication -ErrorAction Stop
Write-Host "Connected successfully!" -ForegroundColor Green

New-Item -ItemType Directory -Path "$OutputDir/ceis-test-skill" -Force | Out-Null
New-Item -ItemType Directory -Path "$OutputDir/review-manual-topics" -Force | Out-Null

$items = @(
    @{ Url = "/AgentAssets/Skills/ceis-test-skill/SKILL.md"; Dest = "$OutputDir/ceis-test-skill/SKILL.md" },
    @{ Url = "/AgentAssets/Skills/review-manual-topics/SKILL.md"; Dest = "$OutputDir/review-manual-topics/SKILL.md" },
    @{ Url = "/AgentAssets/ceis-procedure-review-template.md"; Dest = "$OutputDir/ceis-procedure-review-template.md" }
)

foreach ($item in $items) {
    try {
        $content = Get-PnPFile -Url $item.Url -AsString
        Set-Content -Path $item.Dest -Value $content -Encoding UTF8
        Write-Host "  Backed up: $($item.Url)" -ForegroundColor Green
    } catch {
        Write-Warning "Could not back up $($item.Url): $_"
    }
}

Write-Host "`nDone. Backups written to: $OutputDir" -ForegroundColor Green
