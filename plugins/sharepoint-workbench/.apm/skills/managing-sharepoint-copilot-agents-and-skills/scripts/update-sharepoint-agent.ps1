<#
.SYNOPSIS
    Update an existing local .agent source package's fields in place, without recreating it.

.DESCRIPTION
    Previously missing entirely -- there was no way to change an agent's instructions or
    grounding sources without running create-agent-package again from scratch. Operates on
    the same local .agent JSON package create-agent-package produces; does not connect to a
    tenant (deployment of the updated package is a separate, not-yet-built capability, same as
    for creation).

.PARAMETER AgentPath
    Path to the existing .agent JSON file to update. Required; fails if not found.

.PARAMETER AgentDescription
    New description. Optional -- unchanged if not supplied.

.PARAMETER AgentInstructionsPath / AgentInstructions
    New instructions (mutually exclusive). Optional -- unchanged if neither supplied.

.PARAMETER KnowledgeSourcePaths
    New knowledge-source URL array, replacing the existing one entirely. Optional -- unchanged
    if not supplied. Pass an empty array explicitly (@()) if you intend to clear all sources --
    this script will reject that as likely accidental; use -AllowEmptyKnowledgeSources to confirm.

.PARAMETER AllowEmptyKnowledgeSources
    Required alongside an empty -KnowledgeSourcePaths array, to distinguish "not supplied" from
    "intentionally clear".
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$AgentPath,

    [string]$AgentDescription,
    [string]$AgentInstructionsPath,
    [string]$AgentInstructions,
    [object[]]$KnowledgeSourcePaths,
    [switch]$AllowEmptyKnowledgeSources
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $AgentPath)) {
    Write-Error "AgentPath '$AgentPath' not found. update-sharepoint-agent only updates an existing package -- use sharepoint-create-agent-package to author a new one."
    exit 1
}

if ($AgentInstructionsPath -and $AgentInstructions) {
    Write-Error "Provide either -AgentInstructionsPath or -AgentInstructions, not both."
    exit 1
}

$noChangeRequested = -not $AgentDescription -and -not $AgentInstructionsPath -and -not $AgentInstructions -and -not $PSBoundParameters.ContainsKey('KnowledgeSourcePaths')
if ($noChangeRequested) {
    Write-Error "No update parameters supplied -- nothing to change. Pass at least one of -AgentDescription, -AgentInstructionsPath/-AgentInstructions, -KnowledgeSourcePaths."
    exit 1
}

if ($PSBoundParameters.ContainsKey('KnowledgeSourcePaths') -and $KnowledgeSourcePaths.Count -eq 0 -and -not $AllowEmptyKnowledgeSources) {
    Write-Error "Empty -KnowledgeSourcePaths supplied without -AllowEmptyKnowledgeSources -- refusing to silently clear all grounding sources."
    exit 1
}

$agent = Get-Content -Path $AgentPath -Raw | ConvertFrom-Json

$changed = @()

if ($AgentDescription) {
    $agent.customCopilotConfig.gptDefinition.description = $AgentDescription
    $changed += "description"
}

if ($AgentInstructionsPath -or $AgentInstructions) {
    $newInstructions = if ($AgentInstructionsPath) {
        if (-not (Test-Path $AgentInstructionsPath)) {
            Write-Error "AgentInstructionsPath '$AgentInstructionsPath' not found."
            exit 1
        }
        (Get-Content -Path $AgentInstructionsPath -Raw).Trim()
    } else {
        $AgentInstructions
    }
    $agent.customCopilotConfig.gptDefinition.instructions = $newInstructions
    $changed += "instructions"
}

if ($PSBoundParameters.ContainsKey('KnowledgeSourcePaths')) {
    $capability = @($agent.customCopilotConfig.gptDefinition.capabilities | Where-Object { $_.name -eq 'OneDriveAndSharePoint' })
    if ($capability.Count -eq 0) {
        if ($agent.customCopilotConfig.gptDefinition.capabilities.Count -gt 0) {
            $targetCap = $agent.customCopilotConfig.gptDefinition.capabilities[0]
        } else {
            $targetCap = [PSCustomObject]@{ name = 'OneDriveAndSharePoint'; items_by_url = @() }
            $agent.customCopilotConfig.gptDefinition.capabilities = @($targetCap)
        }
    } else {
        $targetCap = $capability[0]
    }

    # Map existing items by URL to preserve resolved identifiers
    $existingMap = @{}
    if ($targetCap.items_by_url) {
        foreach ($item in $targetCap.items_by_url) {
            if ($item.url) {
                $existingMap[$item.url] = $item
            }
        }
    }

    $newItems = @()
    foreach ($ks in $KnowledgeSourcePaths) {
        if ($ks -is [PSCustomObject] -or $ks -is [System.Collections.IDictionary]) {
            $newItems += $ks
        } else {
            $urlStr = "$ks".Trim()
            if (-not $urlStr) { continue }
            if ($existingMap.ContainsKey($urlStr)) {
                $newItems += $existingMap[$urlStr]
            } else {
                $leafName = Split-Path -Path $urlStr -Leaf
                if (-not $leafName) { $leafName = ($urlStr -split '/')[-1] }
                $isList = $urlStr -match "/Lists/"
                $typeStr = if ($isList) { "List" } else { "Folder" }
                $newItems += [PSCustomObject]@{
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

    $targetCap.items_by_url = [System.Object[]]$newItems
    $changed += "knowledge sources ($($newItems.Count) item(s))"
}

$agent | ConvertTo-Json -Depth 10 | Set-Content -Path $AgentPath -Encoding UTF8

Write-Host "Updated: $($changed -join ', ')" -ForegroundColor Green
Write-Host "Package updated in place at: $AgentPath" -ForegroundColor Green
Write-Host "Not deployed. Deployment of the updated package is a separate, not-yet-built capability." -ForegroundColor Yellow
