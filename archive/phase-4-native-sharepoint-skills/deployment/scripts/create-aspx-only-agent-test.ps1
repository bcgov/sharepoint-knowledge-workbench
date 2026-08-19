<#
.SYNOPSIS
    Diagnostic test: ASPX-only agent with CORRECTED IDs

.DESCRIPTION
    Test agent with VERIFIED list_id and unique_id from manual agent:
    - ONLY knowledge source: CEISPilotKnowledgePages .aspx pages
    - Correct list_id: 1a4a1eda-a2fe-4c43-8d48-4a841f07b253
    - Correct unique_id: d260117a-79d8-4586-b9cf-9a0211634556

.EXAMPLE
    .\create-aspx-only-agent-test.ps1
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

Write-Host "Test configuration (ASPX-ONLY, CORRECTED):" -ForegroundColor Yellow
Write-Host "  Knowledge source: CEISPilotKnowledgePages .aspx pages ONLY" -ForegroundColor Cyan
Write-Host "  list_id: $ceisPagesFolderListId" -ForegroundColor Green
Write-Host "  unique_id: $ceisPagesFolderUniqueId" -ForegroundColor Green

$agentJson = @"
{
  "schemaVersion": "0.2.0",
  "customCopilotConfig": {
    "conversationStarters": {
      "conversationStarterList": [
        {
          "text": "What procedures are documented in CEIS?"
        },
        {
          "text": "Tell me about a specific CEIS process"
        },
        {
          "text": "How do I complete this task in CEIS?"
        }
      ],
      "welcomeMessage": {
        "text": "I can answer questions about CEIS procedures and processes from the available knowledge pages."
      }
    },
    "gptDefinition": {
      "name": "CEIS Procedures Agent (ASPX Pages Only)",
      "description": "Search CEIS procedure pages for answers to operational questions",
      "instructions": "You are the CEIS Procedures Agent. Search and answer ONLY using the CEISPilotKnowledgePages .aspx procedure pages. Search strategy: (1) Search the CEISPilotKnowledgePages folder for .aspx pages matching the user's question, (2) Extract detailed step-by-step procedures from the .aspx pages found, (3) Always cite the specific .aspx page name, (4) If the answer is not found in the .aspx pages, state clearly that the procedure is not documented. Do NOT search images or other sources. Reply in a formal, professional tone.",
      "capabilities": [
        {
          "name": "OneDriveAndSharePoint",
          "items_by_sharepoint_ids": [],
          "items_by_url": [
            {
              "url": "$($web.Url)/SitePages/CEISPilotKnowledgePages",
              "name": "CEISPilotKnowledgePages (.aspx pages)",
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
Write-Host "Creating ASPX-only test agent..." -ForegroundColor Cyan
$tempFile = New-TemporaryFile
Set-Content -Path $tempFile -Value $agentJson -Encoding UTF8

# Create in SitePages subfolder for testing
Resolve-PnPFolder -SiteRelativePath "SitePages/CEISPilotKnowledgePages" | Out-Null

Add-PnPFile -Path $tempFile -Folder "SitePages/CEISPilotKnowledgePages" -NewFileName "CEIS-ASPX-Only-Test.agent" -ErrorAction Stop

Write-Host "✓ Test agent created: SitePages/CEISPilotKnowledgePages/CEIS-ASPX-Only-Test.agent" -ForegroundColor Green
Write-Host ""
Write-Host "This agent:" -ForegroundColor Cyan
Write-Host "  - ONLY searches CEISPilotKnowledgePages .aspx pages" -ForegroundColor Green
Write-Host "  - Uses VERIFIED IDs from working manual agent" -ForegroundColor Green

Remove-Item $tempFile -Force
Disconnect-PnPOnline
