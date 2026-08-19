<#
.SYNOPSIS
    Human-authorized rollback procedure for review-manual-topics SKILL.md (Alias wrapper for rollback-skill-deployment.ps1).
#>
param (
    [string]$ConfigFile = "tools/phase-4-native-sharepoint-skills/config.psd1",
    [string]$ManifestFile = "plugins/sharepoint-agents-and-skills/deployment-manifest.example.json",
    [switch]$Execute,
    [string]$ConfirmExactTarget,
    [string]$JsonOutputPath
)

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "../../../..")).Path
$scriptPath = Join-Path $repoRoot "plugins/sharepoint-agents-and-skills/scripts/rollback-skill-deployment.ps1"
& $scriptPath -ConfigFile $ConfigFile -ManifestFile $ManifestFile -Execute:$Execute -ConfirmExactTarget $ConfirmExactTarget -JsonOutputPath $JsonOutputPath
