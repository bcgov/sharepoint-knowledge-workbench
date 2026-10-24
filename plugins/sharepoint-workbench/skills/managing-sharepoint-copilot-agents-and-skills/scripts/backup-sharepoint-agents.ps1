<#
.SYNOPSIS
    Read-only backup: downloads named .agent files from a SharePoint Site Pages folder to a
    local directory, so they exist as a reference before any tenant cleanup/recreation is
    considered. Makes no changes to the tenant.

.DESCRIPTION
    Idempotent and deterministic: always writes to the same fixed OutputDir (no timestamp in
    the default path) and overwrites each file's content on every run — rerunning refreshes
    the backup in place rather than accumulating dated folders.

.PARAMETER SitePath
    Site-relative path to the folder containing the .agent files (e.g.
    "SitePages/KnowledgePages").

.PARAMETER AgentFileNames
    Explicit list of .agent file names to back up. No hardcoded default — the caller (or a
    phase-specific thin wrapper) supplies the real target list.

.PARAMETER All
    Discovery mode: instead of a named list, scan the Site Pages, AgentAssets and KnowledgePublications
    libraries of the connected site and back up every .agent file found. Also used when no
    -AgentFileNames are given.
#>
[CmdletBinding()]
param(
    [string]$ConfigFile = (Join-Path $PSScriptRoot '../../../config.psd1'),
    [string]$SitePath,
    [string[]]$AgentFileNames,
    [switch]$All,
    [string]$OutputDir = "plugins/sharepoint-copilot-agents-and-skills/backups/agents"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $ConfigFile)) {
    Write-Error "Config file not found: $ConfigFile. Copy config.psd1.example to config.psd1 and fill in ClientId/TenantId/SiteUrl."
    exit 1
}

$rawConfig = Import-PowerShellDataFile -Path $ConfigFile
$config = if ($rawConfig.ContainsKey('Connection')) { $rawConfig.Connection } else { $rawConfig }
Connect-PnPOnline -Url $config.SiteUrl -ClientId $config.ClientId -Tenant $config.TenantId -Interactive -ForceAuthentication -ErrorAction Stop
Write-Host "Connected successfully!" -ForegroundColor Green

New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null

if ($All -or (-not $AgentFileNames -or $AgentFileNames.Count -eq 0)) {
    $librariesToScan = @("Site Pages", "AgentAssets", "KnowledgePublications")
    $discoveredAgents = @()

    foreach ($libName in $librariesToScan) {
        Write-Host "Discovering .agent files in '$libName'..." -ForegroundColor Cyan
        try {
            $found = Get-PnPListItem -List $libName -PageSize 500 -Fields "FileLeafRef", "FileRef" -ErrorAction Stop |
                Where-Object { $_.FieldValues.FileLeafRef -like "*.agent" }
            
            foreach ($f in $found) {
                $discoveredAgents += [PSCustomObject]@{
                    FileName = $f.FieldValues.FileLeafRef
                    FileRef  = $f.FieldValues.FileRef
                }
            }
        } catch {
            Write-Warning "Could not query $($libName): $_"
        }
    }

    if ($discoveredAgents.Count -gt 0) {
        Write-Host "Found $($discoveredAgents.Count) .agent file(s) to back up." -ForegroundColor Cyan
        foreach ($a in $discoveredAgents) {
            $destPath = Join-Path $OutputDir $a.FileName
            try {
                $content = Get-PnPFile -Url $a.FileRef -AsString
                Set-Content -Path $destPath -Value $content -Encoding UTF8
                Write-Host "  Backed up: $($a.FileName) -> $destPath" -ForegroundColor Green
            } catch {
                Write-Warning "Could not back up $($a.FileName): $_"
            }
        }
    } else {
        Write-Host "No .agent files found in '$sitePagesLib'." -ForegroundColor Yellow
    }
} else {
    foreach ($fileName in $AgentFileNames) {
        $sourceUrl = "$SitePath/$fileName"
        $destPath = Join-Path $OutputDir $fileName
        try {
            $content = Get-PnPFile -Url $sourceUrl -AsString
            Set-Content -Path $destPath -Value $content -Encoding UTF8
            Write-Host "  Backed up: $fileName -> $destPath" -ForegroundColor Green
        } catch {
            Write-Warning "Could not back up $fileName : $_"
        }
    }
}

Write-Host "`nDone. Backups written to: $OutputDir" -ForegroundColor Green
