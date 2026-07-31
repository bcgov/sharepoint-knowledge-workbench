<#
.SYNOPSIS
    Human-authorized rollback procedure for review-manual-topics SKILL.md (Alias wrapper for rollback-skill-deployment.ps1).
#>
param (
    [string]$ConfigFile = "tools/phase-4-native-sharepoint-skills/config.psd1",
    [string]$ManifestFile = "tools/phase-4-native-sharepoint-skills/deployment/deployment-manifest.example.json",
    [switch]$Execute,
    [switch]$Force,
    [string]$JsonOutputPath
)

$scriptPath = Join-Path $PSScriptRoot "rollback-skill-deployment.ps1"
& $scriptPath -ConfigFile $ConfigFile -ManifestFile $ManifestFile -Execute:$Execute -Force:$Force -JsonOutputPath $JsonOutputPath
