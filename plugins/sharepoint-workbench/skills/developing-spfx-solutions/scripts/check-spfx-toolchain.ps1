<#
.SYNOPSIS
    Verifies the local toolchain required to scaffold a new SPFx web part.

.DESCRIPTION
    Checks for Node.js (LTS major version 18 or 22), npm, the Yeoman CLI (`yo`),
    and the `@microsoft/generator-sharepoint` package (global install). Reports
    PASS/WARN/FAIL per dependency and exits non-zero if any required dependency
    is missing, so it can gate scaffolding before `yo @microsoft/sharepoint` runs.

.EXAMPLE
    pwsh -File ./check-spfx-toolchain.ps1
#>

[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$failures = 0

function Test-Command {
    param([string]$Name, [string]$Command, [string]$InstallHint)

    try {
        $output = Invoke-Expression "$Command 2>`$null"
        if ($LASTEXITCODE -ne 0 -and -not $output) {
            throw "no output"
        }
        Write-Host " PASS: $Name -> $output" -ForegroundColor Green
        return $true
    } catch {
        Write-Host " FAIL: $Name not found. $InstallHint" -ForegroundColor Red
        return $false
    }
}

Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host " SPFx Scaffolding Toolchain Check" -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan

if (-not (Test-Command -Name "Node.js" -Command "node --version" -InstallHint "Install Node.js 18 or 22 LTS.")) {
    $failures++
} else {
    $nodeVersion = (node --version) -replace 'v', ''
    $majorVersion = [int]($nodeVersion.Split('.')[0])
    if ($majorVersion -ne 18 -and $majorVersion -ne 22) {
        Write-Host " WARN: Node.js v$nodeVersion is not v18.x or v22.x (SPFx-supported LTS). Consider 'nvm use 22'." -ForegroundColor Yellow
    }
}

if (-not (Test-Command -Name "npm" -Command "npm --version" -InstallHint "Comes bundled with Node.js.")) {
    $failures++
}

if (-not (Test-Command -Name "Yeoman (yo)" -Command "yo --version" -InstallHint "Install with: npm install -g yo")) {
    $failures++
}

try {
    $generatorList = (npm ls -g "@microsoft/generator-sharepoint" --depth=0 2>$null) -join "`n"
    if ($generatorList -match "@microsoft/generator-sharepoint@[\d.]+") {
        Write-Host " PASS: @microsoft/generator-sharepoint -> $($Matches[0])" -ForegroundColor Green
    } else {
        throw "not installed"
    }
} catch {
    Write-Host " FAIL: @microsoft/generator-sharepoint not found. Install with: npm install -g @microsoft/generator-sharepoint" -ForegroundColor Red
    $failures++
}

Write-Host "==================================================================" -ForegroundColor Cyan
if ($failures -gt 0) {
    Write-Host " Toolchain check FAILED ($failures issue(s)). Resolve before scaffolding." -ForegroundColor Red
    exit 1
} else {
    Write-Host " Toolchain check PASSED. Ready to run 'yo @microsoft/sharepoint'." -ForegroundColor Green
    exit 0
}
