<#
.SYNOPSIS
    Uploads ONLY the rendered-Markdown pages (runs/ceis-manual-v2/render/rendered-output/pages/
    and index.md) into a "pages" subfolder inside the EXISTING CEIS-Pilot-Knowledge library, so
    they ground a comparison agent against the .aspx pages (Phase 5 CEIS grounding-only
    prototype) without duplicating the 319 images already uploaded there.

    Corrected 2026-08-02: the original version of this script copied the ENTIRE
    rendered-output tree (pages/ + media/) into a brand-new library, duplicating the images.
    The rendered pages' image links are relative one level up (../media/imageNN.png) — placing
    the pages in a "pages/" subfolder INSIDE CEIS-Pilot-Knowledge (which already has media/ at
    its root) makes those links resolve correctly against the existing images, with zero
    duplication. This target (CEIS-Pilot-Knowledge/pages/) is a different library from the
    .aspx publication (Site Pages/CEISPilotKnowledgePages), so it cannot collide with or
    overwrite that publication.
#>

[CmdletBinding()]
param(
    [string]$ConfigPath = (Join-Path $PSScriptRoot "config.psd1"),
    [string]$SourcePagesPath = (Join-Path $PSScriptRoot "../../runs/ceis-manual-v2/render/rendered-output/pages"),
    [string]$SourceIndexPath = (Join-Path $PSScriptRoot "../../runs/ceis-manual-v2/render/rendered-output/index.md"),
    [string]$TargetLibrary = "CEIS-Pilot-Knowledge",
    [string]$TargetSubFolder = "pages"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $ConfigPath)) {
    Write-Error "Config file not found: $ConfigPath. Copy config.psd1.example to config.psd1 and fill in ClientId/TenantId/SiteUrl."
    exit 1
}
if (-not (Test-Path $SourcePagesPath)) {
    Write-Error "Rendered pages not found at $SourcePagesPath. Confirm runs/ceis-manual-v2/render/rendered-output/pages exists."
    exit 1
}
if (-not (Test-Path $SourceIndexPath)) {
    Write-Error "Rendered index.md not found at $SourceIndexPath."
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
    Write-Error "Library '$TargetLibrary' does not exist. This script deliberately reuses the existing CEIS-Pilot-Knowledge library (with its already-uploaded media/) — it does not create a new one. Confirm the library name."
    exit 1
}
Write-Host "Reusing existing library '$TargetLibrary' (id: $($existingLib.Id)) — its existing media/ is NOT touched by this script." -ForegroundColor Yellow

$targetFolder = "$TargetLibrary/$TargetSubFolder"
Resolve-PnPFolder -SiteRelativePath $targetFolder | Out-Null

$pageFiles = Get-ChildItem -Path $SourcePagesPath -File
$allFiles = @($pageFiles) + @(Get-Item $SourceIndexPath)
Write-Host "Uploading $($allFiles.Count) Markdown files ($($pageFiles.Count) pages + index.md) to '$targetFolder'..." -ForegroundColor Cyan

$uploadedCount = 0
foreach ($file in $allFiles) {
    $destinationFolder = if ($file.FullName -eq (Resolve-Path $SourceIndexPath).Path) { $TargetLibrary } else { $targetFolder }
    Add-PnPFile -Path $file.FullName -Folder $destinationFolder -ErrorAction Stop | Out-Null
    Write-Host "  Uploaded: $($file.Name) -> $destinationFolder"
    $uploadedCount++
}

Write-Host "`nDone. Uploaded $uploadedCount Markdown files to '$targetFolder' (index.md at library root)." -ForegroundColor Green
Write-Host "Reused existing media/ in '$TargetLibrary' — 0 images duplicated." -ForegroundColor Green
Write-Host "Exact target: $($config.SiteUrl)/$targetFolder" -ForegroundColor Green
