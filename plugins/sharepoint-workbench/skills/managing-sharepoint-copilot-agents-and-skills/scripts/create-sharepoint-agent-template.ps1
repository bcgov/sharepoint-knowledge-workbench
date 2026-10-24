<#
.SYNOPSIS
    Author a reusable SharePoint agent template locally (governance metadata + placeholder
    knowledge-source slots), distinct from a concrete .agent package.

.DESCRIPTION
    A template captures the *reusable shape* of an agent (purpose, instruction structure, answer
    boundaries, refusal behavior, citation expectations, conversation starters, native-skill
    references, output style, governance metadata, template version) with knowledge-source
    PLACEHOLDERS rather than concrete URLs. create-agent-package-from-template fills in the
    placeholders for a specific target and produces a real .agent package via
    create-agent-package. Template authoring is distinct from agent creation -- this script
    never produces a deployable .agent file itself.

.PARAMETER TemplateName
    The template's name.

.PARAMETER Purpose
    One-sentence statement of the template's intended use.

.PARAMETER InstructionsTemplatePath / InstructionsTemplate
    Instructions body, with {{KNOWLEDGE_SOURCE_PLACEHOLDER}}-style tokens where per-target
    content belongs (mutually exclusive parameters).

.PARAMETER AnswerBoundary
    Statement of what the agent should and shouldn't answer.

.PARAMETER RefusalBehavior
    Statement of how the agent should decline out-of-scope requests.

.PARAMETER CitationExpectations
    Statement of citation requirements.

.PARAMETER KnowledgeSourcePlaceholderCount
    How many knowledge-source slots this template expects create-agent-package-from-template to
    fill. Required, must be >= 1.

.PARAMETER TemplateVersion
    Version string for this template. Required.

.PARAMETER OutputPath
    Where to write the template JSON. Required.

.PARAMETER Overwrite
    Required to overwrite an existing file.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$TemplateName,

    [Parameter(Mandatory = $true)]
    [string]$Purpose,

    [string]$InstructionsTemplatePath,
    [string]$InstructionsTemplate,

    [string]$AnswerBoundary,
    [string]$RefusalBehavior,
    [string]$CitationExpectations,

    [Parameter(Mandatory = $true)]
    [ValidateRange(1, [int]::MaxValue)]
    [int]$KnowledgeSourcePlaceholderCount,

    [Parameter(Mandatory = $true)]
    [string]$TemplateVersion,

    [Parameter(Mandatory = $true)]
    [string]$OutputPath,

    [switch]$Overwrite
)

$ErrorActionPreference = "Stop"

if ($InstructionsTemplatePath -and $InstructionsTemplate) {
    Write-Error "Provide either -InstructionsTemplatePath or -InstructionsTemplate, not both."
    exit 1
}
if (-not $InstructionsTemplatePath -and -not $InstructionsTemplate) {
    Write-Error "One of -InstructionsTemplatePath or -InstructionsTemplate is required."
    exit 1
}

$instructionsTemplateBody = if ($InstructionsTemplatePath) {
    if (-not (Test-Path $InstructionsTemplatePath)) {
        Write-Error "InstructionsTemplatePath '$InstructionsTemplatePath' not found."
        exit 1
    }
    (Get-Content -Path $InstructionsTemplatePath -Raw).Trim()
} else {
    $InstructionsTemplate
}

if ((Test-Path $OutputPath) -and -not $Overwrite) {
    Write-Error "OutputPath '$OutputPath' already exists. Pass -Overwrite to replace it."
    exit 1
}

$template = [PSCustomObject]@{
    templateName                    = $TemplateName
    templateVersion                 = $TemplateVersion
    purpose                         = $Purpose
    instructionsTemplate            = $instructionsTemplateBody
    answerBoundary                  = $AnswerBoundary
    refusalBehavior                 = $RefusalBehavior
    citationExpectations            = $CitationExpectations
    knowledgeSourcePlaceholderCount = $KnowledgeSourcePlaceholderCount
}

$outDir = Split-Path -Path $OutputPath -Parent
if ($outDir -and -not (Test-Path $outDir)) {
    New-Item -ItemType Directory -Path $outDir -Force | Out-Null
}

$template | ConvertTo-Json -Depth 5 | Set-Content -Path $OutputPath -Encoding UTF8

Write-Host "Agent template written to: $OutputPath" -ForegroundColor Green
Write-Host "Use sharepoint-create-agent-package-from-template to produce a concrete .agent package from it." -ForegroundColor Yellow
