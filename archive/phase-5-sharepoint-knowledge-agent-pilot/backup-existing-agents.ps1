<#
.SYNOPSIS
    Phase 5 historical entry point: back up the 5 CEIS pilot .agent files.

.DESCRIPTION
    Thin wrapper supplying Phase 5's real target list to the canonical
    backup-sharepoint-agents capability
    (plugins/sharepoint-agents-and-skills/scripts/backup-sharepoint-agents.ps1). No independent
    tenant logic remains here.
#>
[CmdletBinding()]
param(
    [string]$ConfigPath = (Join-Path $PSScriptRoot "config.psd1"),
    [string]$OutputDir = (Join-Path $PSScriptRoot "backups/agents")
)

$agentFiles = @(
    "CEIS-Pilot-Knowledge-Agent.agent",
    "CEIS-Pilot-Knowledge-Agent-Corrected.agent",
    "CEIS-ASPX-Only-Test.agent",
    "CEIS-Topic-Reviewer-with-Skills.agent",
    "CEISPilotKnowledgePages-manuallycreated.agent"
)

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "../..")).Path
$canonicalScript = Join-Path $repoRoot "plugins/sharepoint-agents-and-skills/scripts/backup-sharepoint-agents.ps1"
& $canonicalScript -ConfigFile $ConfigPath -SitePath "/sites/AG-CSB-INTRANET-DEV/SitePages/CEISPilotKnowledgePages" -AgentFileNames $agentFiles -OutputDir $OutputDir
