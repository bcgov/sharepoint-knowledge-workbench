<#
.SYNOPSIS
    READ-ONLY artifact verification: identify existing SKILL.md and compare with repository source.

.DESCRIPTION
    1. Connect to SharePoint
    2. List all items in AgentAssets/Skills/
    3. For each SKILL.md found, download and calculate SHA-256
    4. Compare with repository source (review-manual-topics/SKILL.md)
    5. Report exact artifact details
    6. Output disposition recommendation for Task 8

.EXAMPLE
    .\verify-agentassets-artifact.ps1
#>

[CmdletBinding()]
param(
    [string]$ConfigFile = "tools/phase-4-native-sharepoint-skills/config.psd1",
    [string]$RepoSkillPath = "tools/phase-4-native-sharepoint-skills/skills/review-manual-topics/SKILL.md",
    [string]$TempDownloadDir = "temp/artifact-verification"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $ConfigFile)) {
    Write-Error "Config file $ConfigFile not found."
    exit 1
}

$config = Import-PowerShellDataFile $ConfigFile
Import-Module PnP.PowerShell -ErrorAction Stop

Write-Host "Connecting to $($config.SiteUrl)..." -ForegroundColor Cyan
$hasValidAppReg = ($config.ClientId -and $config.TenantId -and `
    $config.ClientId -notlike "*test*" -and $config.TenantId -notlike "*test*")

if ($hasValidAppReg) {
    Connect-PnPOnline -Url $config.SiteUrl -ClientId $config.ClientId -Tenant $config.TenantId -Interactive -ForceAuthentication -ErrorAction Stop
} else {
    $phase3ConfigPath = "../../tools/phase-3-sharepoint-discovery/config.psd1"
    if (Test-Path $phase3ConfigPath) {
        $phase3Config = Import-PowerShellDataFile $phase3ConfigPath
        Connect-PnPOnline -Url $config.SiteUrl -ClientId $phase3Config.ClientId -Tenant $phase3Config.TenantId -Interactive -ForceAuthentication -ErrorAction Stop
    } else {
        Write-Error "No valid config found."
        exit 1
    }
}

Write-Host "Connected successfully!" -ForegroundColor Green

# Create temp directory for downloads
if (-not (Test-Path $TempDownloadDir)) {
    New-Item -ItemType Directory -Path $TempDownloadDir -Force | Out-Null
}

$artifacts = @()

# 1. Get AgentAssets library
Write-Host "Retrieving AgentAssets library info..." -ForegroundColor Cyan
try {
    $agentAssets = Get-PnPList -Identity "AgentAssets" -ErrorAction Stop
    Write-Host "  ✓ AgentAssets Title: $($agentAssets.Title)" -ForegroundColor Green
    Write-Host "  ✓ AgentAssets ID: $($agentAssets.Id)" -ForegroundColor Green
    Write-Host "  ✓ AgentAssets RootFolder: $($agentAssets.RootFolder.ServerRelativeUrl)" -ForegroundColor Green
} catch {
    Write-Error "Failed to get AgentAssets: $($_.Exception.Message)"
    exit 1
}

# 2. List all folders/items in AgentAssets/Skills/
Write-Host "Listing items in AgentAssets/Skills/..." -ForegroundColor Cyan
try {
    $skillsFolder = Get-PnPFolder -Url "AgentAssets/Skills" -ErrorAction Stop
    $skillItems = Get-PnPFolderItem -FolderSiteRelativeUrl "AgentAssets/Skills" -ErrorAction Stop

    Write-Host "  Found $($skillItems.Count) item(s)" -ForegroundColor Green

    foreach ($item in $skillItems) {
        Write-Host "    - $($item.Name) (Type: $($item.FileSystemObjectType))" -ForegroundColor Gray

        # If it's a folder, list its contents
        if ($item.FileSystemObjectType -eq "Folder") {
            $folderName = $item.Name
            $folderPath = "AgentAssets/Skills/$folderName"
            Write-Host "      Folder contents:" -ForegroundColor Gray

            try {
                $folderContents = Get-PnPFolderItem -FolderSiteRelativeUrl $folderPath -ErrorAction SilentlyContinue
                foreach ($file in $folderContents) {
                    Write-Host "        - $($file.Name)" -ForegroundColor Gray

                    # If it's a SKILL.md file, download and hash it
                    if ($file.Name -eq "SKILL.md") {
                        Write-Host "        → Downloading $folderName/SKILL.md..." -ForegroundColor Cyan

                        $downloadPath = Join-Path $TempDownloadDir "$folderName-SKILL.md"
                        try {
                            Get-PnPFile -Url "$folderPath/SKILL.md" -Path $TempDownloadDir -Filename "$folderName-SKILL.md" -AsFile -Force -ErrorAction Stop

                            # Calculate SHA-256
                            $fileBytes = [System.IO.File]::ReadAllBytes($downloadPath)
                            $sha256 = [System.Security.Cryptography.SHA256]::Create()
                            $hash = [System.BitConverter]::ToString($sha256.ComputeHash($fileBytes)).Replace("-","").ToLower()
                            $sha256.Dispose()

                            # Extract frontmatter
                            $content = Get-Content $downloadPath -Raw
                            $nameMatch = $content | Select-String -Pattern '^\s*name:\s*(.+?)$' -AllMatches
                            $descMatch = $content | Select-String -Pattern '^\s*description:\s*(.+?)$' -AllMatches

                            $artifacts += [PSCustomObject]@{
                                FolderName       = $folderName
                                FileName         = $file.Name
                                FilePath         = "$folderPath/$($file.Name)"
                                DeployedSHA256   = $hash
                                FrontmatterName  = if ($nameMatch.Matches) { $nameMatch.Matches[0].Groups[1].Value.Trim() } else { "NOT_FOUND" }
                                FrontmatterDesc  = if ($descMatch.Matches) { $descMatch.Matches[0].Groups[1].Value.Trim() } else { "NOT_FOUND" }
                                Downloaded       = $true
                                DownloadPath     = $downloadPath
                            }

                            Write-Host "          SHA-256: $hash" -ForegroundColor Green
                            Write-Host "          Name: $($artifacts[-1].FrontmatterName)" -ForegroundColor Green
                        } catch {
                            Write-Host "          ✗ Failed to download: $($_.Exception.Message)" -ForegroundColor Red
                        }
                    }
                }
            } catch {
                Write-Host "      (Could not list folder contents)" -ForegroundColor Yellow
            }
        }
    }
} catch {
    Write-Error "Failed to list Skills folder: $($_.Exception.Message)"
    exit 1
}

# 3. Compare with repository source
Write-Host "Comparing with repository source..." -ForegroundColor Cyan
if (Test-Path $RepoSkillPath) {
    $repoBytes = [System.IO.File]::ReadAllBytes($RepoSkillPath)
    $repoSha256 = [System.Security.Cryptography.SHA256]::Create()
    $repoHash = [System.BitConverter]::ToString($repoSha256.ComputeHash($repoBytes)).Replace("-","").ToLower()
    $repoSha256.Dispose()

    Write-Host "  Repository review-manual-topics/SKILL.md SHA-256: $repoHash" -ForegroundColor Cyan

    foreach ($artifact in $artifacts) {
        Write-Host "  Comparing with deployed $($artifact.FolderName)..." -ForegroundColor Cyan
        if ($artifact.DeployedSHA256 -eq $repoHash) {
            Write-Host "    ✓ HASH MATCH - Deployed artifact matches repository source" -ForegroundColor Green
            $artifact | Add-Member -NotePropertyName HashMatch -NotePropertyValue $true
        } else {
            Write-Host "    ✗ HASH MISMATCH - Deployed artifact differs from repository" -ForegroundColor Red
            $artifact | Add-Member -NotePropertyName HashMatch -NotePropertyValue $false
        }
    }
} else {
    Write-Host "  ⚠ Repository source not found: $RepoSkillPath" -ForegroundColor Yellow
}

# 4. Determine Task 8 disposition
Write-Host ""
Write-Host "========================================================================" -ForegroundColor Green
Write-Host "ARTIFACT VERIFICATION SUMMARY" -ForegroundColor Green
Write-Host "========================================================================" -ForegroundColor Green

if ($artifacts.Count -eq 0) {
    Write-Host "No SKILL.md artifacts found in AgentAssets/Skills/" -ForegroundColor Yellow
    Write-Host "Task 8 Disposition: DEPLOYMENT_CANDIDATE_NOT_YET_PRESENT" -ForegroundColor Yellow
} else {
    foreach ($artifact in $artifacts) {
        Write-Host ""
        Write-Host "Artifact: $($artifact.FolderName)/SKILL.md" -ForegroundColor Cyan
        Write-Host "  Deployed Path: $($artifact.FilePath)" -ForegroundColor Cyan
        Write-Host "  Deployed SHA-256: $($artifact.DeployedSHA256)" -ForegroundColor Cyan
        Write-Host "  Frontmatter Name: $($artifact.FrontmatterName)" -ForegroundColor Cyan
        Write-Host "  Hash Match Repository: $($artifact.HashMatch)" -ForegroundColor Cyan

        if ($artifact.FolderName -eq "review-manual-topics") {
            Write-Host ""
            if ($artifact.HashMatch) {
                Write-Host "Task 8 Disposition: ARTIFACT_ALREADY_PRESENT (review-manual-topics matches repository)" -ForegroundColor Yellow
                Write-Host "  → Task 8 deployment is SUPERSEDED" -ForegroundColor Yellow
                Write-Host "  → Revise Task 8 to hash reconciliation only" -ForegroundColor Yellow
            } else {
                Write-Host "Task 8 Disposition: DEPLOYED_ARTIFACT_DRIFT_DETECTED" -ForegroundColor Red
                Write-Host "  → Hash mismatch detected (deployment ≠ repository)" -ForegroundColor Red
                Write-Host "  → Task 8 BLOCKED pending disposition" -ForegroundColor Red
            }
        } else {
            Write-Host ""
            Write-Host "Task 8 Disposition: DEPLOYMENT_CANDIDATE_NOT_YET_PRESENT (existing skill is $($artifact.FolderName), not review-manual-topics)" -ForegroundColor Yellow
            Write-Host "  → Existing skill identified: $($artifact.FrontmatterName)" -ForegroundColor Yellow
            Write-Host "  → No collision detected with review-manual-topics" -ForegroundColor Green
            Write-Host "  → Task 8 deployment can proceed" -ForegroundColor Green
        }
    }
}

Write-Host ""
Write-Host "Temporary downloads preserved in: $TempDownloadDir" -ForegroundColor Gray
Write-Host "(for manual review if needed — will not be committed)" -ForegroundColor Gray

Disconnect-PnPOnline
