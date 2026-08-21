<#
.SYNOPSIS
    Builds and packages an SPFx solution into a production .sppkg file, then
    verifies the output artifact.

.DESCRIPTION
    Runs the Heft test/build and package-solution commands in production mode
    against a target SPFx solution directory, then confirms the resulting
    .sppkg file exists under sharepoint/solution/ and is non-empty.

.PARAMETER SolutionPath
    Path to the SPFx solution root (the folder containing package.json).
    Defaults to the current directory.

.EXAMPLE
    pwsh -File ./package-spfx-solution.ps1 -SolutionPath "../../../temp/webparts/demo1"
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [string]$SolutionPath = "."
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path (Join-Path $SolutionPath "package.json"))) {
    Write-Host " FAIL: No package.json found at '$SolutionPath'. Is this an SPFx solution root?" -ForegroundColor Red
    exit 1
}

$resolvedPath = (Resolve-Path $SolutionPath).Path
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host " Package SPFx Solution: $resolvedPath" -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan

Push-Location $resolvedPath
try {
    if (-not (Test-Path "node_modules")) {
        Write-Host "node_modules not found. Running npm install..." -ForegroundColor Yellow
        npm install
        if ($LASTEXITCODE -ne 0) {
            throw "npm install failed with exit code $LASTEXITCODE"
        }
    }

    Write-Host "Running production test & packaging (npm run build)..." -ForegroundColor Cyan
    npm run build
    if ($LASTEXITCODE -ne 0) {
        throw "SPFx build failed with exit code $LASTEXITCODE"
    }

    $sppkgFiles = Get-ChildItem -Path "sharepoint/solution" -Filter "*.sppkg" -ErrorAction SilentlyContinue
    if (-not $sppkgFiles -or $sppkgFiles.Count -eq 0) {
        throw "No .sppkg file found under sharepoint/solution/ after packaging."
    }

    foreach ($file in $sppkgFiles) {
        if ($file.Length -le 0) {
            throw "Package '$($file.Name)' is 0 bytes."
        }
        Write-Host " PASS: $($file.FullName) ($([math]::Round($file.Length / 1KB, 1)) KB)" -ForegroundColor Green
    }

    Write-Host "==================================================================" -ForegroundColor Cyan
    Write-Host " Packaging complete." -ForegroundColor Green
} catch {
    Write-Host " FAIL: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
} finally {
    Pop-Location
}
