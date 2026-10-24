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
    -OutputPath only; a future create-agent-package deployment step (not built yet, out of
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
    [string]$AgentName,
    [string]$AgentDescription,

    [string]$AgentInstructionsPath,
    [string]$AgentInstructions,

    [object[]]$KnowledgeSourcePaths,

    [string]$AgentTemplatePath = (Join-Path $PSScriptRoot '../assets/templates/sharepoint-agent.template.json'),
    [string]$AgentMarkdownTemplatePath,
    [string]$ConfigFile,

    [Parameter(Mandatory = $true)]
    [string]$OutputPath,

    [switch]$Overwrite
)

$ErrorActionPreference = "Stop"

# Support direct Markdown template as input
if ($AgentMarkdownTemplatePath -and (Test-Path $AgentMarkdownTemplatePath)) {
    $mdContent = Get-Content -Path $AgentMarkdownTemplatePath -Raw
    if (-not $AgentInstructions -and -not $AgentInstructionsPath) {
        $AgentInstructions = $mdContent.Trim()
    }
    if (-not $AgentName -and ($mdContent -match "^#\s+(.+)")) {
        $AgentName = $matches[1].Trim()
    }
    if (-not $AgentDescription -and ($mdContent -match "(?ms)## Purpose\s*\r?\n([^\r\n#]+)")) {
        $AgentDescription = $matches[1].Trim()
    }
}

if (-not $AgentName) {
    Write-Error "-AgentName is required or must be defined in # Title of -AgentMarkdownTemplatePath."
    exit 1
}
if (-not $AgentDescription) {
    Write-Error "-AgentDescription is required or must be defined in ## Purpose of -AgentMarkdownTemplatePath."
    exit 1
}

if ($AgentInstructionsPath -and $AgentInstructions -and -not $AgentMarkdownTemplatePath) {
    Write-Error "Provide either -AgentInstructionsPath or -AgentInstructions, not both."
    exit 1
}
if (-not $AgentInstructionsPath -and -not $AgentInstructions) {
    Write-Error "One of -AgentInstructionsPath, -AgentInstructions, or -AgentMarkdownTemplatePath is required."
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

if ((-not $KnowledgeSourcePaths -or $KnowledgeSourcePaths.Count -eq 0) -and $AgentMarkdownTemplatePath) {
    $mdContent = Get-Content -Path $AgentMarkdownTemplatePath -Raw
    $extractedUrls = @()
    foreach ($line in ($mdContent -split "\r?\n")) {
        if ($line -match "https://[^\s""'\)]+") {
            $extractedUrl = $matches[0].Trim().TrimEnd('`', '"', "'", '.', ',')
            $extractedUrls += $extractedUrl
        }
    }
    if ($extractedUrls.Count -gt 0) {
        $KnowledgeSourcePaths = $extractedUrls | Select-Object -Unique
    }
}

if (-not $KnowledgeSourcePaths -or $KnowledgeSourcePaths.Count -eq 0) {
    Write-Error "-KnowledgeSourcePaths must contain at least one URL (or be present in -AgentMarkdownTemplatePath)."
    exit 1
}

$itemsByUrl = @()
$resolverScript = Join-Path $PSScriptRoot "get-agent-resource-identifiers.ps1"

foreach ($ks in $KnowledgeSourcePaths) {
    if ($ks -is [PSCustomObject] -or $ks -is [System.Collections.IDictionary]) {
        $itemsByUrl += $ks
    } else {
        $urlStr = "$ks".Trim()
        $leafName = Split-Path -Path $urlStr -Leaf
        if (-not $leafName) { $leafName = ($urlStr -split '/')[-1] }
        
        $resolvedObject = $null
        if ($ConfigFile -and (Test-Path $ConfigFile) -and (Test-Path $resolverScript)) {
            try {
                $rawCfg = Import-PowerShellDataFile -Path $ConfigFile
                $cfg = if ($rawCfg.ContainsKey('Connection')) { $rawCfg.Connection } else { $rawCfg }
                if ($urlStr.StartsWith($cfg.SiteUrl, [System.StringComparison]::OrdinalIgnoreCase)) {
                    $rel = $urlStr.Substring($cfg.SiteUrl.Length).TrimStart('/')
                    if ($rel) {
                        Write-Host "Dynamically resolving GUIDs for '$rel'..." -ForegroundColor Cyan
                        $resolved = & $resolverScript -ConfigFile $ConfigFile -FolderSiteRelativePath $rel
                        if ($resolved -and $resolved.site_id) {
                            $resolvedObject = $resolved
                        }
                    }
                }
            } catch {
                Write-Warning "Could not dynamically resolve identifiers for $urlStr : $_"
            }
        }

        if ($resolvedObject) {
            $itemsByUrl += $resolvedObject
        } else {
            $isList = $urlStr -match "/Lists/"
            $typeStr = if ($isList) { "List" } else { "Folder" }
            
            $itemsByUrl += [PSCustomObject]@{
                url       = $urlStr
                name      = [System.Uri]::UnescapeDataString($leafName)
                site_id   = "00000000-0000-0000-0000-000000000000"
                web_id    = "00000000-0000-0000-0000-000000000000"
                list_id   = "00000000-0000-0000-0000-000000000000"
                unique_id = "00000000-0000-0000-0000-000000000000"
                type      = $typeStr
            }
        }
    }
}

$conversationStarters = @(
    [PSCustomObject]@{ text = "Summarize recent items" },
    [PSCustomObject]@{ text = "Tell me more about..." },
    [PSCustomObject]@{ text = "How can you help me?" }
)

$icon = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGAAAABgCAYAAADimHc4AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAANgSURBVHhe7dq9jeMwFATgq8sFuYYrQ2WoAoWuQhkzh8oUOeRBvttdkkNJjxQ5Bg5D4EsGkr3mz6N+9tev37OXD4JAuCAQLgiECwLhgkC4IBAuCIQLAuGCQLggEC4IhAsC4YJAuCAQLgiECwLhgkC4IBAuCIQLAuGCQLggEC4IhAsC4YJAuCAQLgiECwLhgkC4IBAuCIQLAuGCQLggEC4IhAsClnH1YZvGzDHVnL+Ni5/ml3dL9DXv5paXnx6Lvw/peR8AAcl9TnplfsIx5Zy/z6/kg0/asn52ICBgGBbv0o7wq7+nx5XIfmbQluOBcQ+Hn8kAAcHt8dMZWzm43AlJOXu3ZfXD6PwtPXb7/uHph8xKcU1WYSEIunN++K7LLz+MwcxdlmyHHYKZ//LTaBzIbSCSPaJ6EtSCoLeww94dngxIUT1++um762rO34TfX/sZF0DQWVR+/s22XGYRnre1+iupZCBrVmItCLoKf2iw6UZlxLoZJ512tX5H+whxFUDQU/gjow6Ly4BpJjfvsMYDagVBR+G1f9rJUTkx/PjoPqJRyejxmacg6Gan/HwpKkPxiinZNw5Fq+rsb2gEgk7OZ3hJp8blIl1N1aJJ0KKsGUDQha3GR4N0VAK6dVSngT0CQQ/m8hJ2wEHHagDKnJefH+FGuFuGNAAlCn+UZSPUABSwdGjE0AnJ85/sMTW6DewBCBqD5/6lLVuy4kHaLVWliidLAxA0lT4sq2m5jkgeoGUHqdz/dyOWPKffnv1bRedlZnj8IK5Fuei0qs5A0EzJjRU6nY3pe4Crq6D5syUjCFq5uqEZOiTeX/LH2HzoQdwGgkbMd7W7LCso3WNqXrCnL2Rye05HEDRh6bxzpkGE98Hba07j9w1PPyWvJJtd0lpB0IKhfJgYr/fTN2Nbc+9/N8kPxO5L+cqJcgkEDZxuoGb2y83buCYv5+OWXlnFreBFfmsQXNb2ci6e3Sf1eWdmHzU3f/g/5CC4qlX5+WIsQzHn74/VT9s9RXDu37bdZ6x+eDwvrMyGIBAuCIQLAuGCQLggEC4IhAsC4YJAuCAQLgiECwLhgkC4IBAuCIQLAuGCQLggEC4IhAsC4YJAuCAQLgiECwLhgkC4IBAuCIQLAuGCQLggEC4IhAsC4YJAqP4AV3GK2i9B/WUAAAAASUVORK5CYII="

if ($AgentTemplatePath -and (Test-Path $AgentTemplatePath)) {
    $template = Get-Content -Path $AgentTemplatePath -Raw | ConvertFrom-Json
    if ($template.customCopilotConfig.conversationStarters) {
        $conversationStarters = $template.customCopilotConfig.conversationStarters.conversationStarterList
    }
    if ($template.customCopilotConfig.icon) {
        $icon = $template.customCopilotConfig.icon
    }
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
                    # arrays into a bare object
                    items_by_url           = [System.Object[]]$itemsByUrl
                }
            )
            behavior_overrides = [PSCustomObject]@{
                special_instructions = [PSCustomObject]@{ discourage_model_knowledge = $true }
            }
        }
        icon = $icon
    }
}

$outDir = Split-Path -Path $OutputPath -Parent
if ($outDir -and -not (Test-Path $outDir)) {
    New-Item -ItemType Directory -Path $outDir -Force | Out-Null
}

$agentObject | ConvertTo-Json -Depth 10 | Set-Content -Path $OutputPath -Encoding UTF8

Write-Host "Validated agent source package written to: $OutputPath" -ForegroundColor Green
Write-Host "Not deployed. Agent upload is a separate, not-yet-built capability." -ForegroundColor Yellow
