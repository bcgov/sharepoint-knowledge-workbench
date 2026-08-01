<#
.SYNOPSIS
    Task 8: Deploy review-manual-topics SKILL.md to AgentAssets/Skills/

.DESCRIPTION
    Deploys the reviewed, repository-authored review-manual-topics SKILL.md
    to the AgentAssets/Skills/ folder for evaluation.

    Scope:
    - ONE file deployment only
    - Single target: AgentAssets/Skills/review-manual-topics/SKILL.md
    - Verify deployment via hash readback
    - Record evidence (path, timestamp, SHA-256, deployment actor)

.EXAMPLE
    .\task-8-deploy-review-manual-topics.ps1
#>

[CmdletBinding()]
param(
    [string]$ConfigFile = "tools/phase-4-native-sharepoint-skills/config.psd1",
    [string]$RepositorySHA = "9586379f777d2064004e747b2d73e49a3d16680efd0dc3e2c67d5d3c5e71ce2c",
    [string]$SkillSource = "tools/phase-4-native-sharepoint-skills/skills/review-manual-topics/SKILL.md"
)

$ErrorActionPreference = "Stop"

Write-Host "=== TASK 8: DEPLOY review-manual-topics SKILL.md ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Repository SHA-256: $RepositorySHA" -ForegroundColor Yellow
Write-Host "Source file: $SkillSource" -ForegroundColor Yellow
Write-Host ""

# Verify source file exists
if (-not (Test-Path $SkillSource)) {
    Write-Error "Source SKILL.md not found at: $SkillSource"
    exit 1
}

# Verify source hash
$sourceHash = (Get-FileHash -Path $SkillSource -Algorithm SHA256).Hash.ToLower()
if ($sourceHash -ne $RepositorySHA) {
    Write-Error "Source file hash mismatch! Expected $RepositorySHA, got $sourceHash"
    exit 1
}

Write-Host "✓ Source file verified" -ForegroundColor Green
Write-Host "  Hash: $sourceHash" -ForegroundColor Gray
Write-Host ""

# Authentication
if (-not (Test-Path $ConfigFile)) {
    Write-Error "Config file $ConfigFile not found."
    exit 1
}

$config = Import-PowerShellDataFile $ConfigFile
Import-Module PnP.PowerShell -ErrorAction Stop

Write-Host "Connecting to tenant..." -ForegroundColor Cyan
$hasValidAppReg = ($config.ClientId -and $config.TenantId -and `
    $config.ClientId -notlike "*test*" -and $config.ClientId -notlike "*example*" -and `
    $config.TenantId -notlike "*test*" -and $config.TenantId -notlike "*example*")

if ($hasValidAppReg) {
    Connect-PnPOnline -Url $config.SiteUrl -ClientId $config.ClientId -Tenant $config.TenantId -Interactive -ErrorAction Stop
} else {
    $phase3ConfigPath = "../../tools/phase-3-sharepoint-discovery/config.psd1"
    if (Test-Path $phase3ConfigPath) {
        Write-Host "Using Phase 3 credentials..." -ForegroundColor Yellow
        $phase3Config = Import-PowerShellDataFile $phase3ConfigPath
        Connect-PnPOnline -Url $config.SiteUrl -ClientId $phase3Config.ClientId -Tenant $phase3Config.TenantId -Interactive -ErrorAction Stop
    } else {
        Write-Error "No valid authentication available."
        exit 1
    }
}

Write-Host "✓ Connected to: $($config.SiteUrl)" -ForegroundColor Green
Write-Host ""

# Ensure target folder exists
Write-Host "Ensuring AgentAssets/Skills/review-manual-topics folder exists..." -ForegroundColor Cyan
try {
    $targetFolder = Resolve-PnPFolder -SiteRelativePath "AgentAssets/Skills/review-manual-topics" -ErrorAction Stop
    Write-Host "✓ Target folder exists: $($targetFolder.ServerRelativeUrl)" -ForegroundColor Green
} catch {
    Write-Host "Creating target folder..." -ForegroundColor Yellow
    $skillsFolder = Resolve-PnPFolder -SiteRelativePath "AgentAssets/Skills" -ErrorAction Stop
    $targetFolder = Add-PnPFolder -Name "review-manual-topics" -Folder "AgentAssets/Skills" -ErrorAction Stop
    Write-Host "✓ Target folder created: $($targetFolder.ServerRelativeUrl)" -ForegroundColor Green
}

Write-Host ""

# Deploy file (using same pattern as working agent deployment scripts)
Write-Host "Deploying SKILL.md..." -ForegroundColor Cyan
try {
    $tempPath = [System.IO.Path]::GetTempFileName()
    Copy-Item -Path $SkillSource -Destination $tempPath -Force

    $deployedFile = Add-PnPFile -Path $tempPath -Folder "AgentAssets/Skills/review-manual-topics" -NewFileName "SKILL.md" -ErrorAction Stop

    Write-Host "✓ SKILL.md deployed successfully" -ForegroundColor Green
    Write-Host "  File: $($deployedFile.Name)" -ForegroundColor Gray
    Write-Host "  URL: $($deployedFile.ServerRelativeUrl)" -ForegroundColor Gray
    Write-Host "  Size: $($deployedFile.Length) bytes" -ForegroundColor Gray
    Write-Host "  Modified: $($deployedFile.TimeLastModified)" -ForegroundColor Gray

    Remove-Item $tempPath -Force
} catch {
    Write-Error "Deployment failed: $_"
    exit 1
}

Write-Host ""

# Verify deployment via readback
Write-Host "Verifying deployment via hash readback..." -ForegroundColor Cyan
try {
    $deploymentPath = "$($targetFolder.ServerRelativeUrl)/SKILL.md"
    $tempPath = [System.IO.Path]::GetTempFileName()

    Get-PnPFile -AsFile -Filename $tempPath -Url $deploymentPath -Force -ErrorAction Stop | Out-Null

    $deployedHash = (Get-FileHash -Path $tempPath -Algorithm SHA256).Hash.ToLower()

    Write-Host "Deployed SHA-256: $deployedHash" -ForegroundColor Gray
    Write-Host "Repository SHA-256: $RepositorySHA" -ForegroundColor Gray

    if ($deployedHash -eq $RepositorySHA) {
        Write-Host "✓ HASH MATCH - Deployment verified" -ForegroundColor Green
        $hashMatch = $true
    } else {
        Write-Host "✗ HASH MISMATCH - Deployment may be corrupted" -ForegroundColor Red
        $hashMatch = $false
    }

    Remove-Item -Path $tempPath -Force -ErrorAction SilentlyContinue

} catch {
    Write-Warning "Hash verification failed: $_"
    $hashMatch = $false
}

Write-Host ""

# Final status
Write-Host "=== DEPLOYMENT COMPLETE ===" -ForegroundColor Cyan
Write-Host "File: AgentAssets/Skills/review-manual-topics/SKILL.md" -ForegroundColor Green
Write-Host "Status: DEPLOYED" -ForegroundColor Green
Write-Host "Hash verification: $(if ($hashMatch) { 'PASSED' } else { 'FAILED' })" -ForegroundColor $(if ($hashMatch) { 'Green' } else { 'Red' })
Write-Host ""
Write-Host "Next step: Execute Task 8 evaluation (normal, negative, permission, safety cases)" -ForegroundColor Yellow

Disconnect-PnPOnline
