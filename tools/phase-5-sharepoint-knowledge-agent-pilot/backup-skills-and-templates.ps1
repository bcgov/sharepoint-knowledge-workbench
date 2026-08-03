<#
.SYNOPSIS
    Phase 5 historical entry point: back up the Phase 4 AgentAssets skills/template
    (ceis-test-skill, review-manual-topics, ceis-procedure-review-template.md) — real Phase 4
    deliverables, explicitly NOT in scope for any deletion.

.DESCRIPTION
    Thin wrapper supplying Phase 5's real target list to the canonical
    backup-sharepoint-native-skills capability
    (plugins/sharepoint-agents-and-skills/scripts/backup-sharepoint-native-skills.ps1). No
    independent tenant logic remains here.
#>
[CmdletBinding()]
param(
    [string]$ConfigPath = (Join-Path $PSScriptRoot "config.psd1"),
    [string]$OutputDir = (Join-Path $PSScriptRoot "backups/skills")
)

$items = @(
    @{ Url = "/AgentAssets/Skills/ceis-test-skill/SKILL.md"; Dest = "ceis-test-skill/SKILL.md" },
    @{ Url = "/AgentAssets/Skills/review-manual-topics/SKILL.md"; Dest = "review-manual-topics/SKILL.md" },
    @{ Url = "/AgentAssets/ceis-procedure-review-template.md"; Dest = "ceis-procedure-review-template.md" }
)

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "../..")).Path
$canonicalScript = Join-Path $repoRoot "plugins/sharepoint-agents-and-skills/scripts/backup-sharepoint-native-skills.ps1"
& $canonicalScript -ConfigFile $ConfigPath -Items $items -OutputDir $OutputDir
