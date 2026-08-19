<#
.SYNOPSIS
    Creates a new SharePoint agent grounded on the rendered-Markdown CEIS content
    (CEIS-Pilot-Knowledge/pages/), mirroring the chosen .aspx baseline agent's instructions
    so the Phase 5 comparison isolates content format, not instruction wording.
#>

[CmdletBinding()]
param(
    [string]$ConfigPath = (Join-Path $PSScriptRoot "config.psd1")
)

$ErrorActionPreference = "Stop"

$config = Import-PowerShellDataFile -Path $ConfigPath
Connect-PnPOnline -Url $config.SiteUrl -ClientId $config.ClientId -Tenant $config.TenantId -Interactive -ForceAuthentication -ErrorAction Stop

$library = Get-PnPList -Identity "CEIS-Pilot-Knowledge" -ErrorAction Stop
$web = Get-PnPWeb -Includes Id, ServerRelativeUrl
$site = Get-PnPSite -Includes Id
$webRelativeLibraryUrl = $library.RootFolder.ServerRelativeUrl.Substring($web.ServerRelativeUrl.TrimEnd("/").Length).TrimStart("/")
$pagesFolderWebRelativeUrl = "$webRelativeLibraryUrl/pages"

# AUTHORITATIVE_LIVE_BASELINE (re-verified 2026-08-02, see results/task6-baseline-verification.md
# and results/task6-instruction-diff.md) with ONLY the 4 source-related phrase substitutions
# applied — everything else word-for-word identical to the live CEIS-ASPX-Only-Test.agent text.
$baselineInstructions = "You are the CEIS Procedures Agent. Search and answer ONLY using the CEIS-Pilot-Knowledge Markdown procedure pages. Search strategy: (1) Search the CEISPilotKnowledge/pages folder for .md pages matching the user's question, (2) Extract detailed step-by-step procedures from the .md pages found, (3) Always cite the specific .md page name, (4) If the answer is not found in the .md pages, state clearly that the procedure is not documented. Do NOT search images or other sources. Reply in a formal, professional tone."

$agentDefinition = @{
    schemaVersion = "0.2.0"
    customCopilotConfig = @{
        conversationStarters = @{
            conversationStarterList = @(@{ text = "Summarize recent items" }, @{ text = "Tell me more about..." }, @{ text = "How can you help me?" })
            welcomeMessage = @{ text = "Ask a question or get started with one of these prompts:" }
        }
        gptDefinition = @{
            name = "CEIS-Markdown-Comparison-Agent"
            description = "Phase 5 comparison agent grounded on rendered-Markdown CEIS content, for evaluating grounding/citation quality against the existing .aspx-grounded agents."
            instructions = $baselineInstructions
            capabilities = @(@{
                name = "OneDriveAndSharePoint"
                items_by_sharepoint_ids = @()
                items_by_url = @(@{
                    url = "$($config.SiteUrl)/$pagesFolderWebRelativeUrl"
                    name = "pages"
                    site_id = $site.Id.ToString()
                    web_id = $web.Id.ToString()
                    list_id = $library.Id.ToString()
                    unique_id = "00000000-0000-0000-0000-000000000000"
                    type = "Folder"
                })
            })
        }
    }
}

$tempPath = Join-Path $env:TMPDIR "CEIS-Markdown-Comparison-Agent.agent"
$agentDefinition | ConvertTo-Json -Depth 20 | Set-Content -Path $tempPath -Encoding UTF8

Add-PnPFile -Path $tempPath -Folder "SitePages/CEISPilotKnowledgePages" -NewFileName "CEIS-Markdown-Comparison-Agent.agent"
Write-Host "Created CEIS-Markdown-Comparison-Agent.agent" -ForegroundColor Green
