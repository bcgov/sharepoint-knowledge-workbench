<#
.SYNOPSIS
    Create CEIS agent with CORRECTED configuration from manual agent analysis

.DESCRIPTION
    Configuration corrected based on manual agent that successfully retrieves ASPX content:
    - URL: SitePages/CEISPilotKnowledgePages (NOT document library)
    - list_id: 1a4a1eda-a2fe-4c43-8d48-4a841f07b253 (actual SitePages subfolder ID)
    - unique_id: d260117a-79d8-4586-b9cf-9a0211634556 (actual folder ID)

.EXAMPLE
    .\create-corrected-agent.ps1
#>

[CmdletBinding()]
param(
    [string]$ConfigFile = "/Users/richardfremmerlid/Projects/sharepoint-knowledge-workbench/tools/phase-3-sharepoint-discovery/config.psd1"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $ConfigFile)) {
    Write-Error "Config file not found: $ConfigFile"
    exit 1
}

$config = Import-PowerShellDataFile $ConfigFile
Import-Module PnP.PowerShell -ErrorAction Stop

Write-Host "Connecting to AG-CSB-INTRANET-DEV..." -ForegroundColor Cyan
Connect-PnPOnline -Url "https://bcgov.sharepoint.com/sites/AG-CSB-INTRANET-DEV" -ClientId $config.ClientId -Tenant $config.TenantId -Interactive -ForceAuthentication -ErrorAction Stop

$web = Get-PnPWeb

# VERIFIED from working manual agent
$siteId = "19801e68-6fba-44c7-89c7-923b85baf943"
$webId = "fbff48d7-76dd-4f69-8b03-9f8ed45f07cf"
$ceisPagesFolderListId = "1a4a1eda-a2fe-4c43-8d48-4a841f07b253"   # SitePages/CEISPilotKnowledgePages
$ceisPagesFolderUniqueId = "d260117a-79d8-4586-b9cf-9a0211634556" # Actual folder unique_id

Write-Host "Using CORRECTED IDs from working manual agent:" -ForegroundColor Green
Write-Host "  Site ID: $siteId" -ForegroundColor Cyan
Write-Host "  Web ID: $webId" -ForegroundColor Cyan
Write-Host "  list_id: $ceisPagesFolderListId (SitePages/CEISPilotKnowledgePages)" -ForegroundColor Cyan
Write-Host "  unique_id: $ceisPagesFolderUniqueId (actual folder ID)" -ForegroundColor Cyan

$agentJson = @"
{
  "schemaVersion": "0.2.0",
  "customCopilotConfig": {
    "conversationStarters": {
      "conversationStarterList": [
        {
          "text": "Summarize recent items"
        },
        {
          "text": "Tell me more about..."
        },
        {
          "text": "How can you help me?"
        }
      ],
      "welcomeMessage": {
        "text": "Ask a question or get started with one of these prompts:"
      }
    },
    "gptDefinition": {
      "name": "CEIS Pilot Knowledge Agent",
      "description": "This is an agent curated based on the content from the selected sources.",
      "instructions": "You are the CEIS Pilot Knowledge Agent. Answer questions using the available knowledge sources. Search strategy: (1) First search the CEISPilotKnowledgePages .aspx topic pages for matching content, (2) Extract detailed information from found .aspx pages and cite them, (3) Always prioritize .aspx page content. Reply in a formal, professional tone suitable for CEIS operational documentation.",
      "capabilities": [
        {
          "name": "OneDriveAndSharePoint",
          "items_by_sharepoint_ids": [],
          "items_by_url": [
            {
              "url": "$($web.Url)/SitePages/CEISPilotKnowledgePages",
              "name": "CEISPilotKnowledgePages",
              "site_id": "$siteId",
              "web_id": "$webId",
              "list_id": "$ceisPagesFolderListId",
              "unique_id": "$ceisPagesFolderUniqueId",
              "type": "Folder"
            }
          ]
        }
      ],
      "behavior_overrides": {
        "special_instructions": {
          "discourage_model_knowledge": true
        }
      }
    },
    "icon": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGAAAABgCAYAAADimHc4AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAL6SURBVHhe7ZrNkaMwEIUnmjltMhyIhQOp2LcJgbN9IAQH4CEDMugpzHpX3YBpYaMHnqeq70LxU9Wf9CQBH1+ff4Tg+LAHSFooAAwFgKEAMBQAhgLAUAAYCgBDAWAoAAwFgKEAMBQAhgLAUAAYCgBDAWAoAAwFgKEAMBQAhgLAUAAYCgBDAWAoAAwFgKEAMBQAhgLAUAAYCgBDAWAoAAwFgKEAMBQAhgLAUAAYCgBDAWAoAAwFgMELKM4StqYYOecpcqkPR2mu39Je1aNEpDt2luZQSpXZ69IAF1CfTE1O5eCcRWTlregxrT0dpbL3WRmsgOwora2CnKW250XR9fiZwk+KefbZ8UAFVEGh2qAo7SEfnOsjl8sgZvqeXWfj96yyUi6n+7N/lYCwWN9yKYLRcF0SBcPi94W3502RS92dPzi+LjgBYfzcCm6EuAvXE46mri0fRWmBCVDx87dYY8dc2LnkVRN5AkACSmn+VSvIXVVIfx6rldSi+MKBERCu/VVv1Tnu2hOY3u+6ZkNABIQ91hZMZbkjSnT2+0fNVgAImIifO1ExZFY+DmFbI7mA+R6ui/p4Mg5lDkfTHkgswJfxStKjSVWNlvil6xZIK8AdL2HPflBYCohjPn7+E07UkzFEATFE5rV6TT0xWiggAk9BFQ5hO98DdCQTMHjvH9tGI0tLmoyqDZNIgC7UsjY2argP8GE+O3bv/r2o60Z6uN4J728eSCAgZmM1ZPZF247fhHasL+DZlYoaPePX2/llT5Px6gLcu9pJHCPIjoIJUVtkZQGO4jlwSTTzTCehKSKed/s2/G6fJB3x4cK53refJW/t2osYlfaZS1Uc3/ej/OwE6sa/3KyKs4kj00Z/0Lq3txLw2k1S1IcX9auJt0VG1otYT8Cr4ueOM4Y0wW+JwbV96/cZzWH6n6EUrCeAuKAAMBQAhgLAUAAYCgBDAWAoAAwFgKEAMBQAhgLAUAAYCgBDAWAoAAwFgKEAMBQAhgLAUAAYCgBDAWAoAAwFgKEAMBQAhgLAUAAYCgBDAWAoAAwFgKEAMBQAhgLAUAAYCgBDAWAoAMwPx31tJdyior4AAAAASUVORK5CYII="
  }
}
"@

Write-Host ""
Write-Host "Creating corrected agent for SitePages/CEISPilotKnowledgePages..." -ForegroundColor Cyan
$tempFile = New-TemporaryFile
Set-Content -Path $tempFile -Value $agentJson -Encoding UTF8

# Ensure target folder exists
Resolve-PnPFolder -SiteRelativePath "SitePages/CEISPilotKnowledgePages" | Out-Null

Add-PnPFile -Path $tempFile -Folder "SitePages/CEISPilotKnowledgePages" -NewFileName "CEIS-Pilot-Knowledge-Agent-Corrected.agent" -ErrorAction Stop

Write-Host "✓ CORRECTED agent created: SitePages/CEISPilotKnowledgePages/CEIS-Pilot-Knowledge-Agent-Corrected.agent" -ForegroundColor Green
Write-Host ""
Write-Host "Key correction: list_id and unique_id now match working manual agent" -ForegroundColor Yellow

Remove-Item $tempFile -Force
Disconnect-PnPOnline
