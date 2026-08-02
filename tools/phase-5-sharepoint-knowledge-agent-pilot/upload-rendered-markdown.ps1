<#
.SYNOPSIS
    Uploads the Task 18 rendered-Markdown CEIS output to a new SharePoint library on
    AG-CSB-INTRANET-DEV, so it can be compared against the existing .aspx pages as a
    grounding source (Phase 5 CEIS grounding-only prototype).
#>

[CmdletBinding()]
param(
    [string]$ConfigPath = (Join-Path $PSScriptRoot "config.psd1"),
    [string]$SourcePath = (Join-Path $PSScriptRoot "../../runs/ceis-manual-v2/render/rendered-output"),
    [string]$TargetLibrary = "CEISPilotKnowledgeMarkdown"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $ConfigPath)) {
    Write-Error "Config file not found: $ConfigPath. Copy config.psd1.example to config.psd1 and fill in ClientId/TenantId/SiteUrl."
    exit 1
}
if (-not (Test-Path $SourcePath)) {
    Write-Error "Rendered output not found at $SourcePath. Confirm runs/ceis-manual-v2/render/rendered-output exists."
    exit 1
}

$config = Import-PowerShellDataFile -Path $ConfigPath
foreach ($required in @("ClientId", "TenantId", "SiteUrl")) {
    if (-not $config.ContainsKey($required) -or [string]::IsNullOrWhiteSpace($config[$required])) {
        Write-Error "config.psd1 is missing a value for '$required'."
        exit 1
    }
}

Write-Host "Connecting to SPO at $($config.SiteUrl)..." -ForegroundColor Cyan
Connect-PnPOnline -Url $config.SiteUrl -ClientId $config.ClientId -Tenant $config.TenantId -Interactive -ForceAuthentication -ErrorAction Stop
Write-Host "Connected successfully!" -ForegroundColor Green

$existingLib = Get-PnPList -Identity $TargetLibrary -ErrorAction SilentlyContinue
if (-not $existingLib) {
    Write-Host "Creating library '$TargetLibrary'..." -ForegroundColor Cyan
    New-PnPList -Title $TargetLibrary -Template DocumentLibrary | Out-Null
} else {
    Write-Host "Library '$TargetLibrary' already exists — reusing it." -ForegroundColor Yellow
}

$files = Get-ChildItem -Path $SourcePath -Recurse -File
Write-Host "Uploading $($files.Count) files from $SourcePath..." -ForegroundColor Cyan

foreach ($file in $files) {
    $relativePath = $file.FullName.Substring((Resolve-Path $SourcePath).Path.Length + 1) -replace '\\', '/'
    $relativeFolder = Split-Path $relativePath -Parent
    $targetFolder = if ($relativeFolder) { "$TargetLibrary/$relativeFolder" } else { $TargetLibrary }

    if ($relativeFolder) {
        Resolve-PnPFolder -SiteRelativePath $targetFolder | Out-Null
    }
    Add-PnPFile -Path $file.FullName -Folder $targetFolder -ErrorAction Stop | Out-Null
    Write-Host "  Uploaded: $relativePath"
}

Write-Host "`nDone. Uploaded $($files.Count) files to '$TargetLibrary'." -ForegroundColor Green
