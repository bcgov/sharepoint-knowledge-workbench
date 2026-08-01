<#
.SYNOPSIS
    Deploys review-manual-topics/SKILL.md to SharePoint and performs exact readback SHA-256 hash verification.
.DESCRIPTION
    Validates manifest and configuration, calculates local SHA-256, and unless -Execute is passed,
    runs in preflight mode with zero tenant writes. When -Execute is passed, uploads the skill file,
    downloads it back to a temporary file location, and verifies a 100% byte-for-byte SHA-256 match.
.PARAMETER ConfigFile
    Path to the PSD1 configuration file (defaults to tools/phase-4-native-sharepoint-skills/config.psd1).
.PARAMETER ManifestFile
    Path to the JSON deployment manifest (defaults to tools/phase-4-native-sharepoint-skills/deployment/deployment-manifest.example.json).
.PARAMETER Execute
    Switch to authorize actual tenant writes and PnP online execution. Default is false (preflight mode).
.PARAMETER JsonOutputPath
    Optional output path for writing structured JSON verification results.
#>
[CmdletBinding()]
param (
    [string]$ConfigFile = "tools/phase-4-native-sharepoint-skills/config.psd1",
    [string]$ManifestFile = "tools/phase-4-native-sharepoint-skills/deployment/deployment-manifest.example.json",
    [switch]$Execute,
    [string]$JsonOutputPath
)

$ErrorActionPreference = "Stop"

# 1. Validate input manifest and configuration files
if (-not (Test-Path $ConfigFile)) {
    Write-Error "Configuration file '$ConfigFile' not found. Copy config.psd1.example to config.psd1 before running."
    exit 1
}

if (-not (Test-Path $ManifestFile)) {
    Write-Error "Deployment manifest file '$ManifestFile' not found."
    exit 1
}

try {
    $manifest = Get-Content -Path $ManifestFile -Raw | ConvertFrom-Json
} catch {
    Write-Error "Failed to parse deployment manifest JSON from '$ManifestFile': $_"
    exit 1
}

$sourcePath = $manifest.repository_path
if (-not (Test-Path $sourcePath)) {
    Write-Error "Source skill file '$sourcePath' referenced in manifest does not exist."
    exit 1
}

$config = Import-PowerShellDataFile -Path $ConfigFile

# 2. Calculate local SHA-256 file hash before any network operations
$hasher = [System.Security.Cryptography.SHA256]::Create()
try {
    $localBytes = [System.IO.File]::ReadAllBytes((Resolve-Path $sourcePath))
    $localHash = [System.BitConverter]::ToString($hasher.ComputeHash($localBytes)).Replace("-", "").ToLower()
} finally {
    $hasher.Dispose()
}

$targetLibraryTitle = $manifest.target_library
$targetRelativeFolder = $manifest.target_relative_folder
$targetFilename = $manifest.target_filename
$exactTargetPath = "<$targetLibraryTitle root>/$targetRelativeFolder/$targetFilename"

Write-Host "=== Deployment Preflight Check ===" -ForegroundColor Cyan
Write-Host "  Source File:        $sourcePath"
Write-Host "  Local SHA-256:      $localHash"
Write-Host "  Target Library:     $targetLibraryTitle"
Write-Host "  Target Folder:      $targetRelativeFolder"
Write-Host "  Target Filename:    $targetFilename"
Write-Host "  Exact Target Path:  $exactTargetPath"

# 3. Default to non-writing preflight mode unless -Execute is explicitly specified
if (-not $Execute) {
    Write-Host "`n[PREFLIGHT MODE] Zero tenant writes performed because -Execute switch was not specified." -ForegroundColor Yellow
    Write-Host "  To perform actual deployment and readback verification, run with -Execute switch."

    if ($JsonOutputPath) {
        $resultObj = [PSCustomObject]@{
            status = "NOT_EXECUTED"
            mode = "PREFLIGHT_ONLY"
            execute = $false
            source_path = $sourcePath
            local_sha256 = $localHash
            target_library = $targetLibraryTitle
            target_exact_path = $exactTargetPath
            verification_result = "NOT_EXECUTED"
        }
        $resultObj | ConvertTo-Json -Depth 5 | Set-Content -Path $JsonOutputPath
    }
    exit 0
}

# 4. Execution Mode (-Execute switch supplied)
Write-Host "`n[EXECUTION MODE] Connecting to SharePoint tenant and uploading skill artifact..." -ForegroundColor Green

Import-Module PnP.PowerShell -ErrorAction Stop

if ($config.ClientId -and $config.TenantId) {
    Connect-PnPOnline -Url $config.SiteUrl -ClientId $config.ClientId -Tenant $config.TenantId -Interactive
} else {
    Connect-PnPOnline -Url $config.SiteUrl -Interactive
}

try {
    # 5. Fail closed if target library does not exist on site (do NOT include library creation logic)
    $libraryList = Get-PnPList -Identity $targetLibraryTitle -ErrorAction SilentlyContinue
    if (-not $libraryList) {
        Write-Error "Target library '$targetLibraryTitle' does not exist on SharePoint site '$($config.SiteUrl)'. Failing closed (library creation is prohibited)."
        exit 1
    }

    $targetFolderUrl = "$targetLibraryTitle/$targetRelativeFolder"

    # Ensure subfolder path inside library exists
    try {
        $folder = Get-PnPFolder -Url $targetFolderUrl -ErrorAction Stop
    } catch {
        Write-Host "Target folder '$targetFolderUrl' missing. Resolving parent path and creating subfolder..." -ForegroundColor Yellow
        $folder = Add-PnPFolder -Name (Split-Path $targetRelativeFolder -Leaf) -Folder "$targetLibraryTitle/$(Split-Path $targetRelativeFolder -Parent)"
    }

    # 6. Upload source file to exact target path
    $uploadedFile = Add-PnPFile -Path $sourcePath -Folder $targetFolderUrl -FileName $targetFilename -Values @{ Title = $manifest.skill_name }
    $serverRelativeUrl = $uploadedFile.ServerRelativeUrl

    Write-Host "Uploaded artifact to server-relative URL: $serverRelativeUrl" -ForegroundColor Green
    Write-Host "Performing readback verification..." -ForegroundColor Cyan

    # 7. Download uploaded file to temp path and perform byte-for-byte SHA-256 verification
    $tempFile = [System.IO.Path]::GetTempFileName()
    try {
        $tempDir = [System.IO.Path]::GetDirectoryName($tempFile)
        $tempName = [System.IO.Path]::GetFileName($tempFile)

        Get-PnPFile -Url $serverRelativeUrl -Path $tempDir -Filename $tempName -AsFile -Force

        $downloadedBytes = [System.IO.File]::ReadAllBytes($tempFile)
        $hasherReadback = [System.Security.Cryptography.SHA256]::Create()
        try {
            $downloadedHash = [System.BitConverter]::ToString($hasherReadback.ComputeHash($downloadedBytes)).Replace("-", "").ToLower()
        } finally {
            $hasherReadback.Dispose()
        }

        Write-Host "Downloaded SKILL.md SHA-256: $downloadedHash" -ForegroundColor Cyan

        if ($localHash -eq $downloadedHash) {
            Write-Host "SUCCESS: Pre- and Post-deployment SHA-256 hashes MATCH 100%." -ForegroundColor Green

            if ($JsonOutputPath) {
                $resultObj = [PSCustomObject]@{
                    status = "SUCCESS"
                    mode = "EXECUTE"
                    execute = $true
                    source_path = $sourcePath
                    local_sha256 = $localHash
                    downloaded_sha256 = $downloadedHash
                    target_library = $targetLibraryTitle
                    server_relative_url = $serverRelativeUrl
                    verification_result = "PASS"
                }
                $resultObj | ConvertTo-Json -Depth 5 | Set-Content -Path $JsonOutputPath
            }
            exit 0
        } else {
            Write-Error "FAILURE: SHA-256 mismatch! Local ($localHash) vs Downloaded ($downloadedHash)."
            exit 1
        }
    } finally {
        if (Test-Path $tempFile) {
            Remove-Item $tempFile -Force -ErrorAction SilentlyContinue
        }
    }
} finally {
    Disconnect-PnPOnline
}
