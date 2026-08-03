<#
.SYNOPSIS
    Read-only: report a deployed SharePoint agent's current knowledge-source bindings.

.DESCRIPTION
    Distinct from update-sharepoint-agent (which edits a LOCAL .agent package's knowledge
    sources): this reads the DEPLOYED .agent file from a tenant and reports what it's actually
    grounded on right now, without downloading a full local copy to edit.

    CORRECTION (2026-08-03): the Phase 6 plan's Task 0.6 named task-9-retrieve-topic-
    metadata.ps1 as this capability's source. Direct reading of that script found it is a
    CEIS-hardcoded diagnostic that inspects topic ITEM metadata field values (TopicID,
    PublicationOrder, TopicContentSHA256, Status, ReviewDate, TransitionAction,
    TransitionTarget) -- it has nothing to do with an agent's knowledge-source bindings. That
    script's capability is unrelated and was not extracted from here; it remains research-only
    in tools/. This script is a new build addressing the actual "configure agent knowledge"
    need: inspecting what an already-deployed agent is currently grounded on.

.PARAMETER ConfigFile
    Connection/authentication context only.

.PARAMETER AgentPath
    Site-relative path to the deployed .agent file to inspect.

.PARAMETER JsonOutputPath
    Optional path to write the resolved knowledge-source list as JSON.
#>
[CmdletBinding()]
param(
    [string]$ConfigFile = "plugins/sharepoint-agents-and-skills/config.psd1",
    [Parameter(Mandatory = $true)]
    [string]$AgentPath,
    [string]$JsonOutputPath
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $ConfigFile)) {
    Write-Error "Config file not found: $ConfigFile."
    exit 1
}

$config = Import-PowerShellDataFile -Path $ConfigFile
Import-Module PnP.PowerShell -ErrorAction Stop
Connect-PnPOnline -Url $config.SiteUrl -ClientId $config.ClientId -Tenant $config.TenantId -Interactive -ErrorAction Stop
Write-Host "Connected to: $($config.SiteUrl)" -ForegroundColor Green

try {
    $tempFile = [System.IO.Path]::GetTempFileName()
    Get-PnPFile -Url $AgentPath -Path (Split-Path $tempFile -Parent) -Filename (Split-Path $tempFile -Leaf) -AsFile -Force -ErrorAction Stop

    $agent = Get-Content -Path $tempFile -Raw | ConvertFrom-Json
    $gpt = $agent.customCopilotConfig.gptDefinition

    Write-Host "Agent: $($gpt.name)" -ForegroundColor Cyan
    Write-Host "Description: $($gpt.description)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Current knowledge sources:" -ForegroundColor Cyan

    $sources = @()
    foreach ($capability in $gpt.capabilities) {
        foreach ($item in $capability.items_by_url) {
            Write-Host "  - $($item.url)" -ForegroundColor Gray
            $sources += $item.url
        }
    }

    if ($sources.Count -eq 0) {
        Write-Host "  [No knowledge sources configured]" -ForegroundColor Yellow
    }

    $result = [PSCustomObject]@{
        agentPath       = $AgentPath
        agentName       = $gpt.name
        knowledgeSources = $sources
    }

    if ($JsonOutputPath) {
        $result | ConvertTo-Json -Depth 5 | Set-Content -Path $JsonOutputPath
        Write-Host "Written to: $JsonOutputPath" -ForegroundColor Green
    }

    $result
} finally {
    if (Test-Path $tempFile) { Remove-Item $tempFile -Force -ErrorAction SilentlyContinue }
    Disconnect-PnPOnline -ErrorAction SilentlyContinue
}
