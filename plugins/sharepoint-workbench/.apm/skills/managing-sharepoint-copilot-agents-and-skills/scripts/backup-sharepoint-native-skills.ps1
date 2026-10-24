<#
.SYNOPSIS
    Read-only backup: downloads named AgentAssets skill/template files from a SharePoint tenant
    to a local directory, as a precaution before any tenant cleanup is considered. Makes no
    changes to the tenant.

.DESCRIPTION
    Idempotent and deterministic: always writes to the same fixed OutputDir (no timestamp in
    the default path) and overwrites each file's content on every run.

.PARAMETER Items
    Explicit list of hashtables with Url (server-relative or AgentAssets-relative source path)
    and Dest (relative destination path under OutputDir) keys. No hardcoded default — the
    caller (or a phase-specific thin wrapper) supplies the real target list.
#>
[CmdletBinding()]
param(
    [string]$ConfigFile = (Join-Path $PSScriptRoot '../../../config.psd1'),
    [object[]]$Items,
    [switch]$All,
    [string]$OutputDir = "plugins/sharepoint-copilot-agents-and-skills/backups/native-skills"
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

if ($All -or (-not $Items -or $Items.Count -eq 0)) {
    $agentAssetsLib = if ($rawConfig.Defaults -and $rawConfig.Defaults.DefaultAgentAssetsLibrary) {
        $rawConfig.Defaults.DefaultAgentAssetsLibrary
    } else {
        "AgentAssets"
    }
    
    Write-Host "Discovering all skill and template files in '$agentAssetsLib'..." -ForegroundColor Cyan
    $discoveredItems = @()
    try {
        $found = Get-PnPListItem -List $agentAssetsLib -PageSize 500 -Fields "FileLeafRef", "FileRef" -ErrorAction Stop |
            Where-Object { $_.FieldValues.FileLeafRef -like "*.md" }
        
        foreach ($f in $found) {
            $ref = $f.FieldValues.FileRef
            # Calculate destination relative path under AgentAssets
            $match = [regex]::Match($ref, "(?i)/$agentAssetsLib/(.+)$")
            $relPath = if ($match.Success) { $match.Groups[1].Value } else { $f.FieldValues.FileLeafRef }
            $discoveredItems += [PSCustomObject]@{
                Url  = $ref
                Dest = $relPath
            }
        }
    } catch {
        Write-Warning "Could not query $($agentAssetsLib): $_"
    }

    $Items = $discoveredItems
    Write-Host "Found $($Items.Count) skill/template file(s) to back up." -ForegroundColor Cyan
}

if (-not $Items -or $Items.Count -eq 0) {
    Write-Host "No items found or specified to back up." -ForegroundColor Yellow
    exit 0
}

foreach ($item in $Items) {
    $url = if ($item -is [hashtable]) { $item.Url } elseif ($item.Url) { $item.Url } else { "$item" }
    $dest = if ($item -is [hashtable]) { $item.Dest } elseif ($item.Dest) { $item.Dest } else { (Split-Path $url -Leaf) }

    $destPath = Join-Path $OutputDir $dest
    $destDir = Split-Path -Path $destPath -Parent
    if ($destDir -and -not (Test-Path $destDir)) {
        New-Item -ItemType Directory -Path $destDir -Force | Out-Null
    }
    try {
        $content = Get-PnPFile -Url $url -AsString
        Set-Content -Path $destPath -Value $content -Encoding UTF8
        Write-Host "  Backed up: $url -> $destPath" -ForegroundColor Green
    } catch {
        Write-Warning "Could not back up $url : $_"
    }
}

Write-Host "`nDone. Backups written to: $OutputDir" -ForegroundColor Green
