<#
.SYNOPSIS
    Author a validated SharePoint Copilot agent (.agent JSON) source file locally. Does not
    upload/deploy it.

.DESCRIPTION
    Parameterized per docs/superpowers/specs/2026-08-02-sharepoint-agents-and-skills-plugin-
    design.md Section 4's script parameter matrix -- not extracted verbatim from any of the 4
    Phase 4/5 research scripts (create-test-agent.ps1, create-corrected-agent.ps1,
    create-aspx-only-agent-test.ps1, create-updated-agent-sitepages.ps1), none of which is
    reusable as-is (hard-coded agent name/description/instructions/knowledge sources). Those
    scripts remain in tools/ as research/evidence of the .agent schema pattern this script
    implements generically.

    Creation is deliberately separate from deployment: writes a local .agent JSON file to
    -OutputPath only; a future create-sharepoint-agent deployment step (not built yet, out of
    Task 0's scope) would upload it.

.PARAMETER AgentName
    The agent's display name.

.PARAMETER AgentDescription
    One-sentence description.

.PARAMETER AgentInstructionsPath
    Path to a file containing the agent's instructions. Mutually exclusive with
    -AgentInstructions; preferred to avoid shell-escaping long instruction text.

.PARAMETER AgentInstructions
    Inline instructions text.

.PARAMETER KnowledgeSourcePaths
    Explicit array of knowledge-source URLs (SharePoint site/library/folder URLs). No default --
    replaces the research scripts' hard-coded items_by_url blocks.

.PARAMETER AgentTemplatePath
    Optional: an existing .agent JSON file to clone structure from (e.g. a confirmed-working
    agent). When supplied, its capabilities/behavior_overrides are used as a starting point,
    overridden by this invocation's own -KnowledgeSourcePaths.

.PARAMETER OutputPath
    Where to write the generated .agent file. Required.

.PARAMETER Overwrite
    Required to overwrite an existing file at -OutputPath.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$AgentName,

    [Parameter(Mandatory = $true)]
    [string]$AgentDescription,

    [string]$AgentInstructionsPath,
    [string]$AgentInstructions,

    [Parameter(Mandatory = $true)]
    [string[]]$KnowledgeSourcePaths,

    [string]$AgentTemplatePath,

    [Parameter(Mandatory = $true)]
    [string]$OutputPath,

    [switch]$Overwrite
)

$ErrorActionPreference = "Stop"

if ($AgentInstructionsPath -and $AgentInstructions) {
    Write-Error "Provide either -AgentInstructionsPath or -AgentInstructions, not both."
    exit 1
}
if (-not $AgentInstructionsPath -and -not $AgentInstructions) {
    Write-Error "One of -AgentInstructionsPath or -AgentInstructions is required -- no default instruction content is provided."
    exit 1
}
if ($KnowledgeSourcePaths.Count -eq 0) {
    Write-Error "-KnowledgeSourcePaths must contain at least one URL. No default knowledge source is provided."
    exit 1
}

$instructions = if ($AgentInstructionsPath) {
    if (-not (Test-Path $AgentInstructionsPath)) {
        Write-Error "AgentInstructionsPath '$AgentInstructionsPath' not found."
        exit 1
    }
    (Get-Content -Path $AgentInstructionsPath -Raw).Trim()
} else {
    $AgentInstructions
}

if ((Test-Path $OutputPath) -and -not $Overwrite) {
    Write-Error "OutputPath '$OutputPath' already exists. Pass -Overwrite to replace it."
    exit 1
}

$itemsByUrl = $KnowledgeSourcePaths | ForEach-Object { [PSCustomObject]@{ url = $_ } }

$conversationStarters = @(
    [PSCustomObject]@{ text = "What can you help me with?" },
    [PSCustomObject]@{ text = "Summarize the key information here." },
    [PSCustomObject]@{ text = "What topics are covered?" }
)

if ($AgentTemplatePath) {
    if (-not (Test-Path $AgentTemplatePath)) {
        Write-Error "AgentTemplatePath '$AgentTemplatePath' not found."
        exit 1
    }
    $template = Get-Content -Path $AgentTemplatePath -Raw | ConvertFrom-Json
    Write-Host "Cloning structure from template: $AgentTemplatePath (knowledge sources overridden by -KnowledgeSourcePaths)" -ForegroundColor Cyan
}

$agentObject = [PSCustomObject]@{
    schemaVersion       = "0.2.0"
    customCopilotConfig = [PSCustomObject]@{
        conversationStarters = [PSCustomObject]@{
            conversationStarterList = $conversationStarters
            welcomeMessage          = [PSCustomObject]@{ text = "Hi! Ask me anything about the content I'm grounded on." }
        }
        gptDefinition = [PSCustomObject]@{
            name           = $AgentName
            description    = $AgentDescription
            instructions   = $instructions
            capabilities   = @(
                [PSCustomObject]@{
                    name                   = "OneDriveAndSharePoint"
                    items_by_sharepoint_ids = @()
                    # [System.Object[]] cast forces array serialization even with exactly 1
                    # item -- ConvertTo-Json otherwise silently unwraps single-element PowerShell
                    # arrays into a bare object (confirmed via direct test; a real, non-obvious
                    # quirk, not a hypothetical edge case -- the unary-comma trick alone did not
                    # fix it, only this explicit type cast did).
                    items_by_url           = [System.Object[]]$itemsByUrl
                }
            )
            behavior_overrides = [PSCustomObject]@{
                special_instructions = [PSCustomObject]@{ discourage_model_knowledge = $true }
            }
        }
    }
}

$outDir = Split-Path -Path $OutputPath -Parent
if ($outDir -and -not (Test-Path $outDir)) {
    New-Item -ItemType Directory -Path $outDir -Force | Out-Null
}

$agentObject | ConvertTo-Json -Depth 10 | Set-Content -Path $OutputPath -Encoding UTF8

Write-Host "Validated agent source package written to: $OutputPath" -ForegroundColor Green
Write-Host "Not deployed. Agent upload is a separate, not-yet-built capability." -ForegroundColor Yellow
