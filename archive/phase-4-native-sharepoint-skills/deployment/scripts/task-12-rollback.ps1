<#
.SYNOPSIS
    Task 12 (Phase 4 historical entry point): rollback review-manual-topics SKILL.md deployment.

.DESCRIPTION
    Thin wrapper preserving the Phase 4 task entry point. All tenant-write logic is owned by
    the canonical guarded implementation at
    plugins/sharepoint-agents-and-skills/scripts/rollback-skill-deployment.ps1 (dry-run by
    default, requires -Execute plus -ConfirmExactTarget "CONFIRM-REMOVE", recycles rather than
    permanently deletes, verifies removal). The pre-migration version of this script performed
    an unguarded permanent Remove-PnPListItem with no dry-run or confirmation gate — that
    independent tenant logic has been retired in favor of the canonical guarded path. See
    docs/reports/phase-4-native-sharepoint-skills/EVID-PHASE4-TASK12-ROLLBACK-COMPLETION.md for
    the original Phase 4 rollback evidence.
#>
[CmdletBinding(ConfirmImpact = "High", SupportsShouldProcess = $true)]
param(
    [string]$ConfigFile = "tools/phase-4-native-sharepoint-skills/config.psd1",
    [string]$ManifestFile = "plugins/sharepoint-agents-and-skills/deployment-manifest.example.json",
    [switch]$Execute,
    [string]$ConfirmExactTarget,
    [string]$JsonOutputPath
)

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "../../../..")).Path
$canonicalScript = Join-Path $repoRoot "plugins/sharepoint-agents-and-skills/scripts/rollback-skill-deployment.ps1"
& $canonicalScript -ConfigFile $ConfigFile -ManifestFile $ManifestFile -Execute:$Execute -ConfirmExactTarget $ConfirmExactTarget -JsonOutputPath $JsonOutputPath
