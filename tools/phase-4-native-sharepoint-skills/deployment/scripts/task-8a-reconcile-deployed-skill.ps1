<#
.SYNOPSIS
    Task 8A: Read-only reconciliation of deployed review-manual-topics SKILL.md

.DESCRIPTION
    Inspects AgentAssets/Skills/ folder for any deployed SKILL.md files.
    Records identity, path, frontmatter, timestamp, and calculated SHA-256.
    Compares against repository artifact hash.

    READ-ONLY: No upload, overwrite, delete, or tenant modification.

.EXAMPLE
    .\task-8a-reconcile-deployed-skill.ps1
#>

[CmdletBinding()]
param(
    [string]$ConfigFile = "tools/phase-4-native-sharepoint-skills/config.psd1",
    [string]$RepositorySHA = "9586379f777d2064004e747b2d73e49a3d16680efd0dc3e2c67d5d3c5e71ce2c"
)

$ErrorActionPreference = "Stop"

Write-Host "=== TASK 8A: SKILL.md DEPLOYMENT RECONCILIATION ===" -ForegroundColor Cyan
Write-Host "Repository SHA-256: $RepositorySHA" -ForegroundColor Yellow
Write-Host ""

if (-not (Test-Path $ConfigFile)) {
    Write-Error "Config file $ConfigFile not found."
    exit 1
}

$config = Import-PowerShellDataFile $ConfigFile
Import-Module PnP.PowerShell -ErrorAction Stop

# Authentication
$hasValidAppReg = ($config.ClientId -and $config.TenantId -and `
    $config.ClientId -notlike "*test*" -and $config.ClientId -notlike "*example*" -and `
    $config.TenantId -notlike "*test*" -and $config.TenantId -notlike "*example*")

if ($hasValidAppReg) {
    Connect-PnPOnline -Url $config.SiteUrl -ClientId $config.ClientId -Tenant $config.TenantId -Interactive -ErrorAction Stop
} else {
    $phase3ConfigPath = "../../tools/phase-3-sharepoint-discovery/config.psd1"
    if (Test-Path $phase3ConfigPath) {
        Write-Host "Using Phase 3 credentials for authentication..." -ForegroundColor Yellow
        $phase3Config = Import-PowerShellDataFile $phase3ConfigPath
        Connect-PnPOnline -Url $config.SiteUrl -ClientId $phase3Config.ClientId -Tenant $phase3Config.TenantId -Interactive -ErrorAction Stop
    } else {
        Write-Error "No valid authentication available."
        exit 1
    }
}

Write-Host "Connected to: $($config.SiteUrl)" -ForegroundColor Green
Write-Host ""

# Find AgentAssets library
Write-Host "Searching for AgentAssets library..." -ForegroundColor Cyan
try {
    $agentAssetsLib = Get-PnPList | Where-Object { $_.Title -eq "AgentAssets" }

    if (-not $agentAssetsLib) {
        Write-Host "AgentAssets library NOT FOUND on tenant." -ForegroundColor Red
        Write-Host "DISPOSITION: TASK_8_AGENTASSETS_LIBRARY_NOT_FOUND"
        exit 0
    }

    Write-Host "✓ AgentAssets library found" -ForegroundColor Green
    Write-Host "  Title: $($agentAssetsLib.Title)" -ForegroundColor Gray
    Write-Host "  ID: $($agentAssetsLib.Id)" -ForegroundColor Gray
    Write-Host "  RootFolder: $($agentAssetsLib.RootFolder.ServerRelativeUrl)" -ForegroundColor Gray
    Write-Host ""

    # Check Skills folder
    Write-Host "Checking for Skills subfolder..." -ForegroundColor Cyan
    $skillsFolderPath = "$($agentAssetsLib.RootFolder.ServerRelativeUrl)/Skills"

    try {
        $skillsFolder = Get-PnPFolder -Url $skillsFolderPath -ErrorAction Stop
        Write-Host "✓ Skills folder found" -ForegroundColor Green
        Write-Host "  Path: $($skillsFolder.ServerRelativeUrl)" -ForegroundColor Gray
        Write-Host ""
    } catch {
        Write-Host "✗ Skills folder NOT accessible at $skillsFolderPath" -ForegroundColor Red
        Write-Host "DISPOSITION: TASK_8_SKILLS_FOLDER_NOT_FOUND"
        exit 0
    }

    # Enumerate all skill subfolders
    Write-Host "Enumerating skill subfolders..." -ForegroundColor Cyan
    $skillFolders = Get-PnPFolderInFolder -FolderSiteRelativeUrl $skillsFolderPath -ErrorAction Stop

    if ($skillFolders.Count -eq 0) {
        Write-Host "No skill folders found in Skills/." -ForegroundColor Yellow
        Write-Host "DISPOSITION: TASK_8_NO_SKILLS_DEPLOYED"
        exit 0
    }

    Write-Host "Found $($skillFolders.Count) skill folder(s):" -ForegroundColor Green
    Write-Host ""

    $deployedSkills = @()

    foreach ($folder in $skillFolders) {
        $folderName = $folder.Name
        Write-Host "Skill: $folderName" -ForegroundColor Yellow
        Write-Host "  Path: $($folder.ServerRelativeUrl)" -ForegroundColor Gray

        # Look for SKILL.md in this folder
        $skillMdPath = "$($folder.ServerRelativeUrl)/SKILL.md"

        try {
            $file = Get-PnPFile -Url $skillMdPath -AsFile -ErrorAction Stop

            Write-Host "  ✓ SKILL.md found" -ForegroundColor Green
            Write-Host "    Size: $($file.Length) bytes" -ForegroundColor Gray
            Write-Host "    Modified: $($file.TimeLastModified)" -ForegroundColor Gray

            # Read file content for SHA-256 and frontmatter extraction
            $tempPath = [System.IO.Path]::GetTempFileName()
            Get-PnPFile -Url $skillMdPath -Path $tempPath -AsFile -Force -ErrorAction Stop | Out-Null

            $fileContent = Get-Content -Path $tempPath -Raw
            $fileHash = (Get-FileHash -Path $tempPath -Algorithm SHA256).Hash.ToLower()

            Write-Host "    SHA-256: $fileHash" -ForegroundColor Gray

            # Extract frontmatter
            if ($fileContent -match '---\s*([\s\S]*?)\s*---') {
                $frontmatter = $matches[1]
                if ($frontmatter -match 'name:\s*(.+)') {
                    $skillName = $matches[1].Trim()
                    Write-Host "    Frontmatter name: $skillName" -ForegroundColor Gray
                }
                if ($frontmatter -match 'description:\s*(.+)') {
                    $skillDesc = $matches[1].Trim()
                    Write-Host "    Description: $skillDesc" -ForegroundColor Gray
                }
            }

            # Check if this matches review-manual-topics
            $isReviewManualTopics = ($folderName -eq "review-manual-topics" -or $skillName -eq "review-manual-topics")
            $hashMatch = ($fileHash -eq $RepositorySHA)

            $deployedSkills += [PSCustomObject]@{
                FolderName = $folderName
                Path = $folder.ServerRelativeUrl
                FileName = "SKILL.md"
                FrontmatterName = $skillName
                Description = $skillDesc
                FileSize = $file.Length
                Modified = $file.TimeLastModified
                SHA256 = $fileHash
                IsReviewManualTopics = $isReviewManualTopics
                HashMatchesRepository = $hashMatch
            }

            if ($isReviewManualTopics) {
                Write-Host "  ⚠ This is review-manual-topics" -ForegroundColor Magenta
                if ($hashMatch) {
                    Write-Host "  ✓ HASH MATCHES REPOSITORY" -ForegroundColor Green
                } else {
                    Write-Host "  ✗ HASH DIFFERS FROM REPOSITORY" -ForegroundColor Red
                }
            }

            Remove-Item -Path $tempPath -Force -ErrorAction SilentlyContinue

        } catch {
            Write-Host "  ✗ No SKILL.md found in this folder" -ForegroundColor Yellow
        }

        Write-Host ""
    }

    # Reconciliation summary
    Write-Host "=== RECONCILIATION SUMMARY ===" -ForegroundColor Cyan
    Write-Host ""

    $reviewManualTopicsDeployed = $deployedSkills | Where-Object { $_.IsReviewManualTopics }

    if ($reviewManualTopicsDeployed) {
        $skill = $reviewManualTopicsDeployed[0]
        Write-Host "review-manual-topics deployment status: DEPLOYED" -ForegroundColor Green
        Write-Host "  Path: $($skill.Path)" -ForegroundColor Gray
        Write-Host "  Deployed SHA-256: $($skill.SHA256)" -ForegroundColor Gray
        Write-Host "  Repository SHA-256: $RepositorySHA" -ForegroundColor Gray
        Write-Host "  Modified: $($skill.Modified)" -ForegroundColor Gray

        if ($skill.HashMatchesRepository) {
            Write-Host "  ✓ HASH MATCH - artifact reconciled" -ForegroundColor Green
            Write-Host ""
            Write-Host "DISPOSITION: TASK_8_ARTIFACT_ALREADY_PRESENT_AND_RECONCILED" -ForegroundColor Green
        } else {
            Write-Host "  ✗ HASH MISMATCH - artifact differs" -ForegroundColor Red
            Write-Host ""
            Write-Host "DISPOSITION: DEPLOYED_ARTIFACT_DRIFT_DETECTED" -ForegroundColor Red
        }
    } else {
        Write-Host "review-manual-topics deployment status: NOT FOUND" -ForegroundColor Yellow
        Write-Host ""
        if ($deployedSkills.Count -gt 0) {
            Write-Host "Other skills deployed:" -ForegroundColor Gray
            $deployedSkills | ForEach-Object {
                Write-Host "  - $($_.FolderName) ($($_.FrontmatterName))" -ForegroundColor Gray
            }
            Write-Host ""
            Write-Host "DISPOSITION: TASK_8_DEPLOYMENT_CANDIDATE_NOT_PRESENT" -ForegroundColor Yellow
        } else {
            Write-Host "No skills deployed yet." -ForegroundColor Gray
            Write-Host "DISPOSITION: TASK_8_NO_SKILLS_DEPLOYED" -ForegroundColor Yellow
        }
    }

    Write-Host ""
    Write-Host "End of reconciliation." -ForegroundColor Cyan

} catch {
    Write-Error "Error during reconciliation: $_"
    exit 1
}

Disconnect-PnPOnline
