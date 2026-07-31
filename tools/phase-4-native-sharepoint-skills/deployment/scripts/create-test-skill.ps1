<#
.SYNOPSIS
    Create test SKILL.md for Phase 4.7.5 testing in AgentAssets/Skills/ceis-test-skill/

.EXAMPLE
    .\create-test-skill.ps1
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

$skillContent = @"
---
name: ceis-test-skill
description: |-
  Test skill for reviewing CEIS pilot knowledge pages.
  Use when the user asks: "review this CEIS topic" / "analyze this procedure"
---

# CEIS Topic Reviewer

## When to use
The user wants to review a specific CEIS topic page for completeness, clarity, or procedural accuracy.

## Inputs
- Topic name or filename (required)
- Specific section to focus on (optional)

## Steps
1. Locate the requested CEIS topic in the knowledge base
2. Read the full topic content
3. Check for: clear title, purpose statement, procedural steps, warnings, expected results
4. Flag missing sections or unclear instructions
5. Note any cross-reference issues

## Output format
Provide a structured review with: topic reviewed, sections found, completeness assessment, recommendations for editors.
"@

Write-Host "Creating folder AgentAssets/Skills/ceis-test-skill/..." -ForegroundColor Cyan
Resolve-PnPFolder -SiteRelativePath "AgentAssets/Skills/ceis-test-skill" | Out-Null

Write-Host "Uploading SKILL.md..." -ForegroundColor Cyan
$tempFile = New-TemporaryFile
Set-Content -Path $tempFile -Value $skillContent -Encoding UTF8

Add-PnPFile -Path $tempFile -Folder "AgentAssets/Skills/ceis-test-skill" -NewFileName "SKILL.md" -ErrorAction Stop

Write-Host "✓ Test SKILL.md created at: AgentAssets/Skills/ceis-test-skill/SKILL.md" -ForegroundColor Green

Remove-Item $tempFile -Force

Disconnect-PnPOnline
