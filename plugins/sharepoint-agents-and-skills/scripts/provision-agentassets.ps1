<#
.SYNOPSIS
    Provision AgentAssets library and sample native SKILL.md on AG-CSB-INTRANET-DEV.

.DESCRIPTION
    1. Checks if AgentAssets library exists.
    2. If not found, creates AgentAssets as a Document Library.
    3. Creates AgentAssets/Skills/ subfolder.
    4. Uploads a sample review-manual-topics SKILL.md.
    5. Exports updated tenant inventory JSON.

.EXAMPLE
    .\provision-agentassets.ps1
#>

[CmdletBinding()]
param(
    [string]$ConfigPath = (Join-Path $PSScriptRoot '../../../config.psd1'),
    [string]$SkillName = "",
    [string]$SkillSourcePath = "",
    [string]$JsonOutputPath = ""
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $ConfigPath)) {
    Write-Error "Config file $ConfigPath not found. Copy config.psd1.example to config.psd1 and fill in tenant details."
    exit 1
}

$config = Import-PowerShellDataFile $ConfigPath
Import-Module PnP.PowerShell -ErrorAction Stop

Write-Host "Connecting to $($config.SiteUrl)..." -ForegroundColor Cyan

# Check if ClientId/TenantId are real values (not placeholders)
$hasValidAppReg = ($config.ClientId -and $config.TenantId -and `
    $config.ClientId -notlike "*test*" -and $config.ClientId -notlike "*example*" -and `
    $config.TenantId -notlike "*test*" -and $config.TenantId -notlike "*example*")

if (-not $hasValidAppReg) {
    Write-Error "Config file '$ConfigPath' has placeholder ClientId/TenantId values. Provide a -ConfigPath with real tenant credentials -- this script fails closed rather than silently falling back to a different phase's config file."
    exit 1
}

Connect-PnPOnline -Url $config.SiteUrl -ClientId $config.ClientId -Tenant $config.TenantId -Interactive -ForceAuthentication -ErrorAction Stop

Write-Host "Connected successfully!" -ForegroundColor Green

# 1. Check if AgentAssets exists
Write-Host "Checking for AgentAssets library..." -ForegroundColor Cyan
$agentAssets = $null
try {
    $agentAssets = Get-PnPList -Identity "AgentAssets" -ErrorAction SilentlyContinue
    if ($agentAssets) {
        Write-Host "  ✓ AgentAssets already exists (Title: $($agentAssets.Title), ItemCount: $($agentAssets.ItemCount))" -ForegroundColor Green
    }
} catch {
    Write-Host "  AgentAssets not found." -ForegroundColor Yellow
}

# 2. If not found, create it
if (-not $agentAssets) {
    Write-Host "Creating AgentAssets Document Library..." -ForegroundColor Yellow
    try {
        $agentAssets = New-PnPList -Title "AgentAssets" -Url "AgentAssets" -Template DocumentLibrary -ErrorAction Stop
        Write-Host "  ✓ AgentAssets created successfully" -ForegroundColor Green
    } catch {
        Write-Error "Failed to create AgentAssets: $($_.Exception.Message)"
        exit 1
    }
}

# 3. Ensure Skills folder exists
Write-Host "Ensuring AgentAssets/Skills/ subfolder exists..." -ForegroundColor Cyan
try {
    Resolve-PnPFolder -SiteRelativePath "AgentAssets/Skills" | Out-Null
    Write-Host "  ✓ AgentAssets/Skills/ folder ready" -ForegroundColor Green
} catch {
    Write-Error "Failed to create Skills folder: $($_.Exception.Message)"
    exit 1
}

# 4. Optionally upload a sample SKILL.md, only when explicitly requested via both parameters.
if ($SkillName -and $SkillSourcePath) {
    if (Test-Path $SkillSourcePath) {
        Write-Host "Uploading sample skill: $SkillName/SKILL.md..." -ForegroundColor Cyan
        try {
            $uploadedFile = Add-PnPFile -Path $SkillSourcePath -Folder "AgentAssets/Skills/$SkillName" -NewFileName "SKILL.md" -ErrorAction Stop
            Write-Host "  ✓ SKILL.md uploaded to AgentAssets/Skills/$SkillName/" -ForegroundColor Green
        } catch {
            Write-Host "  ⚠ Warning: Could not upload SKILL.md - $($_.Exception.Message)" -ForegroundColor Yellow
        }
    } else {
        Write-Host "  ⚠ Skill source file not found: $SkillSourcePath" -ForegroundColor Yellow
    }
} else {
    Write-Host "No -SkillName/-SkillSourcePath supplied -- skipping sample skill upload (provisioning AgentAssets structure only)." -ForegroundColor Gray
}

# 5. Verify with read-only inventory
Write-Host "Running verification inventory..." -ForegroundColor Cyan
$inventoryResult = [PSCustomObject]@{
    Timestamp        = (Get-Date -Format "O")
    SiteUrl          = $config.SiteUrl
    AgentAssets      = @{
        Exists   = $false
        ItemCount = 0
        Skills   = @()
    }
}

try {
    $agentAssetsList = Get-PnPList -Identity "AgentAssets" -ErrorAction SilentlyContinue
    if ($agentAssetsList) {
        $inventoryResult.AgentAssets.Exists = $true
        $inventoryResult.AgentAssets.ItemCount = $agentAssetsList.ItemCount

        Write-Host "  ✓ AgentAssets exists with $($agentAssetsList.ItemCount) item(s)" -ForegroundColor Green

        # Check for SKILL.md files
        try {
            $skillItems = Get-PnPListItem -List $agentAssetsList -PageSize 500 | Where-Object { $_["FileLeafRef"] -like "*.md" }
            foreach ($skill in $skillItems) {
                $inventoryResult.AgentAssets.Skills += [PSCustomObject]@{
                    FileName = $skill["FileLeafRef"]
                    FilePath = $skill["FileRef"]
                    Id       = $skill.Id
                }
            }
            Write-Host "  ✓ Found $($inventoryResult.AgentAssets.Skills.Count) SKILL.md file(s)" -ForegroundColor Green
        } catch {
            Write-Host "  ⚠ Could not inventory skills: $($_.Exception.Message)" -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host "  ✗ Failed to verify AgentAssets: $($_.Exception.Message)" -ForegroundColor Red
}

# Export results
if ($JsonOutputPath) {
    $outDir = Split-Path -Path $JsonOutputPath -Parent
    if (-not (Test-Path $outDir)) {
        New-Item -ItemType Directory -Path $outDir -Force | Out-Null
    }
    $inventoryResult | ConvertTo-Json -Depth 5 | Out-File -FilePath $JsonOutputPath -Encoding utf8
    Write-Host "Verification saved to: $JsonOutputPath" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "========================================================================" -ForegroundColor Green
Write-Host "Provisioning complete!" -ForegroundColor Green
Write-Host "========================================================================" -ForegroundColor Green
Write-Host "AgentAssets Status:" -ForegroundColor Cyan
Write-Host "  Exists: $($inventoryResult.AgentAssets.Exists)" -ForegroundColor Cyan
Write-Host "  Item Count: $($inventoryResult.AgentAssets.ItemCount)" -ForegroundColor Cyan
Write-Host "  Skills: $($inventoryResult.AgentAssets.Skills.Count)" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next: Run verify-agentassets-ready.ps1 to confirm Task 8 readiness." -ForegroundColor Yellow

Disconnect-PnPOnline
