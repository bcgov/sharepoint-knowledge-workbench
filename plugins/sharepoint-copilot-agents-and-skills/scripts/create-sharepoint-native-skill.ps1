<#
.SYNOPSIS
    Author a validated native SharePoint skill (SKILL.md) source package. Does not deploy it.

.DESCRIPTION
    Produces a local SKILL.md file with valid frontmatter (name, description) and a body built
    from explicit instruction/boundary parameters -- no hardcoded
    skill content. Creation is deliberately separate from deployment: this script writes to
    -OutputPath only; use deploy-native-skill to push the result to a tenant.

.PARAMETER SkillName
    The skill's name (used as the AgentAssets/Skills/<SkillName>/ folder name on deployment).

.PARAMETER SkillDescription
    One-paragraph description, used verbatim in the SKILL.md frontmatter.

.PARAMETER InstructionsPath
    Path to a file containing the skill's body instructions (Markdown). Mutually exclusive with
    -Instructions; preferred for anything beyond a short inline string, to avoid shell-escaping
    long instruction text.

.PARAMETER Instructions
    Inline instructions text. Use -InstructionsPath instead for anything non-trivial.

.PARAMETER InputBoundary
    Optional explicit statement of the skill's input scope/boundary (e.g. "review exactly one
    topic page per invocation"). Appended as its own section if supplied.

.PARAMETER ProhibitedScope
    Optional explicit list of prohibited actions (e.g. "no write actions", "no full-library
    scan"). Appended as its own section if supplied.

.PARAMETER OutputPath
    Where to write the generated SKILL.md. Required.

.PARAMETER Overwrite
    Required to overwrite an existing file at -OutputPath. Fails closed otherwise.

.EXAMPLE
    .\create-sharepoint-native-skill.ps1 -SkillName "example-skill" `
        -SkillDescription "Does one clearly bounded thing." `
        -InstructionsPath ./instructions.md `
        -InputBoundary "One target per invocation." `
        -ProhibitedScope "Read-only; no write actions." `
        -OutputPath ./out/example-skill/SKILL.md
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$SkillName,

    [Parameter(Mandatory = $true)]
    [string]$SkillDescription,

    [string]$InstructionsPath,
    [string]$Instructions,
    [string]$InputBoundary,
    [string]$ProhibitedScope,

    [Parameter(Mandatory = $true)]
    [string]$OutputPath,

    [switch]$Overwrite
)

$ErrorActionPreference = "Stop"

if (-not $SkillName -or $SkillName -notmatch '^[a-z0-9][a-z0-9-]*$') {
    Write-Error "SkillName must be lowercase, alphanumeric-and-hyphens, matching the AgentAssets/Skills/<name>/ folder convention. Got: '$SkillName'"
    exit 1
}

if ($InstructionsPath -and $Instructions) {
    Write-Error "Provide either -InstructionsPath or -Instructions, not both."
    exit 1
}
if (-not $InstructionsPath -and -not $Instructions) {
    Write-Error "One of -InstructionsPath or -Instructions is required -- no default instruction content is provided."
    exit 1
}

$body = if ($InstructionsPath) {
    if (-not (Test-Path $InstructionsPath)) {
        Write-Error "InstructionsPath '$InstructionsPath' not found."
        exit 1
    }
    Get-Content -Path $InstructionsPath -Raw
} else {
    $Instructions
}

if (Test-Path $OutputPath) {
    if (-not $Overwrite) {
        Write-Error "OutputPath '$OutputPath' already exists. Pass -Overwrite to replace it."
        exit 1
    }
}

$sections = New-Object System.Collections.Generic.List[string]
$sections.Add($body.TrimEnd())

if ($InputBoundary) {
    $sections.Add("`n## Input Boundary`n`n$InputBoundary")
}
if ($ProhibitedScope) {
    $sections.Add("`n## Prohibited Scope`n`n$ProhibitedScope")
}

$skillContent = @"
---
name: $SkillName
description: $SkillDescription
---

$($sections -join "`n")
"@

$outDir = Split-Path -Path $OutputPath -Parent
if ($outDir -and -not (Test-Path $outDir)) {
    New-Item -ItemType Directory -Path $outDir -Force | Out-Null
}

Set-Content -Path $OutputPath -Value $skillContent -Encoding UTF8

Write-Host "Validated native-skill source package written to: $OutputPath" -ForegroundColor Green
Write-Host "Not deployed. Use sharepoint-deploy-native-skill to push it to a tenant." -ForegroundColor Yellow
