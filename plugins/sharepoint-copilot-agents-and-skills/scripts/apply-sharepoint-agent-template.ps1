<#
.SYNOPSIS
    Apply an existing agent template (from create-agent-template) to a specific
    target, producing a concrete .agent package via create-agent-package.

.DESCRIPTION
    Reads a template JSON, requires exactly the number of knowledge-source URLs the template
    declares it needs (KnowledgeSourcePlaceholderCount), assembles the final instructions from
    the template's instructionsTemplate plus its answer-boundary/refusal-behavior/citation-
    expectations sections, and delegates to create-sharepoint-agent.ps1 to write the resulting
    .agent package. Does not deploy it -- same separation as create-agent-package.

.PARAMETER TemplatePath
    Path to the template JSON produced by create-agent-template.

.PARAMETER AgentName / AgentDescription
    The concrete agent's name/description (the template has no fixed name of its own).

.PARAMETER KnowledgeSourcePaths
    Must contain exactly TemplatePath's KnowledgeSourcePlaceholderCount URLs.

.PARAMETER OutputPath
    Where to write the resulting .agent file.

.PARAMETER Overwrite
    Passed through to create-sharepoint-agent.ps1.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$TemplatePath,

    [Parameter(Mandatory = $true)]
    [string]$AgentName,

    [Parameter(Mandatory = $true)]
    [string]$AgentDescription,

    [Parameter(Mandatory = $true)]
    [string[]]$KnowledgeSourcePaths,

    [Parameter(Mandatory = $true)]
    [string]$OutputPath,

    [switch]$Overwrite
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $TemplatePath)) {
    Write-Error "TemplatePath '$TemplatePath' not found."
    exit 1
}

$template = Get-Content -Path $TemplatePath -Raw | ConvertFrom-Json

if ($KnowledgeSourcePaths.Count -ne $template.knowledgeSourcePlaceholderCount) {
    Write-Error "Template '$($template.templateName)' requires exactly $($template.knowledgeSourcePlaceholderCount) knowledge source(s); got $($KnowledgeSourcePaths.Count)."
    exit 1
}

$instructionSections = New-Object System.Collections.Generic.List[string]
$instructionSections.Add($template.instructionsTemplate.TrimEnd())
if ($template.answerBoundary) { $instructionSections.Add("`n## Answer Boundary`n`n$($template.answerBoundary)") }
if ($template.refusalBehavior) { $instructionSections.Add("`n## Refusal Behavior`n`n$($template.refusalBehavior)") }
if ($template.citationExpectations) { $instructionSections.Add("`n## Citation Expectations`n`n$($template.citationExpectations)") }

$finalInstructions = $instructionSections -join "`n"

$scriptDir = Split-Path -Path $PSCommandPath -Parent
$createScript = Join-Path $scriptDir "create-sharepoint-agent.ps1"

$createArgs = @{
    AgentName            = $AgentName
    AgentDescription     = $AgentDescription
    AgentInstructions    = $finalInstructions
    KnowledgeSourcePaths = $KnowledgeSourcePaths
    OutputPath           = $OutputPath
}
if ($Overwrite) { $createArgs["Overwrite"] = $true }

& $createScript @createArgs
