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
    Write-Host "Running production test/build (npx heft test --clean --production)..." -ForegroundColor Cyan
    npx heft test --clean --production
    if ($LASTEXITCODE -ne 0) {
        throw "heft test --clean --production failed with exit code $LASTEXITCODE"
    }

    Write-Host "Running production package-solution (npx heft package-solution --production)..." -ForegroundColor Cyan
    npx heft package-solution --production
    if ($LASTEXITCODE -ne 0) {
        throw "heft package-solution --production failed with exit code $LASTEXITCODE"
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
