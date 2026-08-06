<#
.SYNOPSIS
    Phase 4 pre-Task-8 verification: confirm AgentAssets library and Skills folder exist and are accessible.

.DESCRIPTION
    READ-ONLY verification that AgentAssets provisioning was successful:
    1. Confirms AgentAssets library exists on target site.
    2. Confirms AgentAssets/Skills/ subfolder is accessible.
    3. Inventories any existing SKILL.md files.
    4. Exports JSON report for Task 8 entry gate validation.

.EXAMPLE
    .\verify-agentassets-ready.ps1
#>

[CmdletBinding()]
param(
    [string]$ConfigFile = "plugins/sharepoint-agents-and-skills/config.psd1",
    [string]$FallbackConfigFile = "tools/phase-3-sharepoint-discovery/config.psd1",
    [string]$JsonOutputPath = ""
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $ConfigFile)) {
    Write-Error "Config file $ConfigFile not found. Copy config.psd1.example to config.psd1 and fill in tenant details."
    exit 1
}

$config = Import-PowerShellDataFile $ConfigFile
Import-Module PnP.PowerShell -ErrorAction Stop

Write-Host "Connecting to $($config.SiteUrl)..." -ForegroundColor Cyan

# Check if ClientId/TenantId are real values (not placeholders)
$hasValidAppReg = ($config.ClientId -and $config.TenantId -and `
    $config.ClientId -notlike "*test*" -and $config.ClientId -notlike "*example*" -and `
    $config.TenantId -notlike "*test*" -and $config.TenantId -notlike "*example*")

if ($hasValidAppReg) {
    Connect-PnPOnline -Url $config.SiteUrl -ClientId $config.ClientId -Tenant $config.TenantId -Interactive -ForceAuthentication -ErrorAction Stop
} else {
    # Fall back to Phase 3 config if Phase 4 has placeholder values
    $phase3ConfigPath = $FallbackConfigFile
    if (Test-Path $phase3ConfigPath) {
        Write-Host "Phase 4 config has placeholder values. Using Phase 3 config for authentication..." -ForegroundColor Yellow
        $phase3Config = Import-PowerShellDataFile $phase3ConfigPath
        Connect-PnPOnline -Url $config.SiteUrl -ClientId $phase3Config.ClientId -Tenant $phase3Config.TenantId -Interactive -ForceAuthentication -ErrorAction Stop
    } else {
        Write-Error "No valid app registration found in config.psd1. Please use the Phase 3 config or update with real ClientId/TenantId."
        exit 1
    }
}

Write-Host "Connected successfully!" -ForegroundColor Green

# Verification result envelope
$verificationResult = [PSCustomObject]@{
    SiteUrl               = $config.SiteUrl
    Timestamp             = (Get-Date -Format "o")
    AgentAssetsExists     = $false
    SkillsFolderExists    = $false
    ExistingSkills        = @()
    Task8ReadinessStatus  = "BLOCKED"
    ErrorDetails          = $null
}

# 1. Check AgentAssets library
Write-Host "Verifying AgentAssets library..." -ForegroundColor Cyan
try {
    $agentAssets = Get-PnPList -Identity "AgentAssets" -ErrorAction Stop
    $verificationResult.AgentAssetsExists = $true
    Write-Host "  ✓ AgentAssets exists (ItemCount: $($agentAssets.ItemCount))" -ForegroundColor Green
} catch {
    Write-Host "  ✗ AgentAssets not found or inaccessible" -ForegroundColor Red
    $verificationResult.ErrorDetails = $_.Exception.Message
    if ($JsonOutputPath) {
        $verificationResult | ConvertTo-Json -Depth 5 | Out-File -FilePath $JsonOutputPath -Encoding utf8
    }
    Disconnect-PnPOnline
    exit 1
}

# 2. Check Skills subfolder
Write-Host "Verifying AgentAssets/Skills/ subfolder..." -ForegroundColor Cyan
try {
    $skillsFolder = Get-PnPFolder -Url "AgentAssets/Skills" -ErrorAction Stop
    $verificationResult.SkillsFolderExists = $true
    Write-Host "  ✓ Skills folder exists and is accessible" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Skills folder not found or inaccessible" -ForegroundColor Yellow
    $verificationResult.ErrorDetails = "Skills folder missing: $($_.Exception.Message)"
}

# 3. Inventory SKILL.md files
Write-Host "Inventorying SKILL.md files in AgentAssets..." -ForegroundColor Cyan
try {
    $skillItems = Get-PnPListItem -List $agentAssets -PageSize 500 | Where-Object { $_["FileLeafRef"] -like "*.md" }
    foreach ($skill in $skillItems) {
        $verificationResult.ExistingSkills += [PSCustomObject]@{
            FileName = $skill["FileLeafRef"]
            FilePath = $skill["FileRef"]
            Size     = $skill["File_x0020_Size"]
        }
    }
    Write-Host "  ✓ Found $($verificationResult.ExistingSkills.Count) existing SKILL.md file(s)" -ForegroundColor Green
    foreach ($existingSkill in $verificationResult.ExistingSkills) {
        Write-Host "      - $($existingSkill.FilePath)" -ForegroundColor DarkGray
    }
} catch {
    Write-Host "  ⚠ Could not inventory SKILL.md files: $($_.Exception.Message)" -ForegroundColor Yellow
}

# 4. Set Task 8 readiness
if ($verificationResult.AgentAssetsExists -and $verificationResult.SkillsFolderExists) {
    $verificationResult.Task8ReadinessStatus = "READY"
    Write-Host "Task 8 Entry Gate: ✓ READY" -ForegroundColor Green
} else {
    $verificationResult.Task8ReadinessStatus = "BLOCKED"
    Write-Host "Task 8 Entry Gate: ✗ BLOCKED" -ForegroundColor Red
}

# Export verification
if ($JsonOutputPath) {
    $outDir = Split-Path -Path $JsonOutputPath -Parent
    if (-not (Test-Path $outDir)) {
        New-Item -ItemType Directory -Path $outDir -Force | Out-Null
    }
    $verificationResult | ConvertTo-Json -Depth 5 | Out-File -FilePath $JsonOutputPath -Encoding utf8
    Write-Host "Verification report saved to: $JsonOutputPath" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "========================================================================" -ForegroundColor Green
Write-Host "Task 8 Readiness Report" -ForegroundColor Green
Write-Host "========================================================================" -ForegroundColor Green
Write-Host "Site: $($config.SiteUrl)" -ForegroundColor Cyan
Write-Host "AgentAssets: $($verificationResult.AgentAssetsExists)" -ForegroundColor Cyan
Write-Host "Skills Folder: $($verificationResult.SkillsFolderExists)" -ForegroundColor Cyan
Write-Host "Existing Skills: $($verificationResult.ExistingSkills.Count)" -ForegroundColor Cyan
Write-Host "Task 8 Status: $($verificationResult.Task8ReadinessStatus)" -ForegroundColor Cyan

Disconnect-PnPOnline

# Exit with appropriate code
if ($verificationResult.Task8ReadinessStatus -eq "READY") {
    exit 0
} else {
    exit 1
}
