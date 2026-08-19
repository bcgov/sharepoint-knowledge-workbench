<#
.SYNOPSIS
    Task 8 (Phase 4 historical entry point): Deploy review-manual-topics SKILL.md to AgentAssets/Skills/.

.DESCRIPTION
    Thin wrapper preserving the Phase 4 task entry point and its evidence-recorded default
    parameters. All tenant-write logic (manifest validation, hash verification, upload,
    readback verification) is owned by the canonical implementation at
    plugins/sharepoint-agents-and-skills/scripts/deploy-and-verify-skill.ps1 — this wrapper
    does not retain independent tenant logic. See docs/reports/phase-4-native-sharepoint-skills/
    EVID-PHASE4-TASK8-DEPLOYMENT.md for the original Phase 4 execution evidence (recorded
    against the pre-migration script; this wrapper reproduces the same deployment via the
    canonical implementation, not a re-run).
#>
[CmdletBinding()]
param(
    [string]$ConfigFile = "tools/phase-4-native-sharepoint-skills/config.psd1",
    [string]$ManifestFile = "plugins/sharepoint-agents-and-skills/deployment-manifest.example.json",
    [switch]$Execute,
    [string]$JsonOutputPath
)

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "../../../..")).Path
$canonicalScript = Join-Path $repoRoot "plugins/sharepoint-agents-and-skills/scripts/deploy-and-verify-skill.ps1"
& $canonicalScript -ConfigFile $ConfigFile -ManifestFile $ManifestFile -Execute:$Execute -JsonOutputPath $JsonOutputPath
