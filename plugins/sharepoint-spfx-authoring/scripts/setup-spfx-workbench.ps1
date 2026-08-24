<#
.SYNOPSIS
    Prepares an SPFx project for hosted SharePoint Online workbench debugging.

.DESCRIPTION
    Validates the SPFx project shape, optionally runs the existing toolchain check,
    optionally trusts the local SPFx dev certificate, and prints canonical local and
    hosted workbench URLs including the hosted debug URL for localhost manifests.

.PARAMETER ProjectPath
    Path to the SPFx project root containing package.json.

.PARAMETER SiteUrl
    Target SharePoint Online site URL used to compose hosted workbench URLs.

.PARAMETER DebugPort
    Local SPFx debug port. Defaults to 4321.

.PARAMETER SkipToolchainCheck
    Skips calling check-spfx-toolchain.ps1.

.PARAMETER SkipCertInstall
    Skips running `npx gulp trust-dev-cert`.

.EXAMPLE
    pwsh -File .\setup-spfx-workbench.ps1 `
      -ProjectPath "..\..\temp\my-webpart" `
      -SiteUrl "https://contoso.sharepoint.com/sites/dev-site"
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [string]$ProjectPath = ".",

    [Parameter(Mandatory = $true)]
    [string]$SiteUrl,

    [Parameter(Mandatory = $false)]
    [ValidateRange(1, 65535)]
    [int]$DebugPort = 4321,

    [switch]$SkipToolchainCheck,
    [switch]$SkipCertInstall
)

$ErrorActionPreference = "Stop"

function Write-FailAndExit {
    param([string]$Message)
    Write-Host " FAIL: $Message" -ForegroundColor Red
    exit 1
}

if ($SiteUrl -notmatch '^https://') {
    Write-FailAndExit "SiteUrl must start with https:// (received '$SiteUrl')."
}

$normalizedSiteUrl = $SiteUrl.TrimEnd("/")
$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$toolchainScript = Join-Path $scriptRoot "check-spfx-toolchain.ps1"

$resolvedProjectPath = (Resolve-Path $ProjectPath -ErrorAction SilentlyContinue)
if (-not $resolvedProjectPath) {
    Write-FailAndExit "ProjectPath not found: '$ProjectPath'."
}

$projectRoot = $resolvedProjectPath.Path
if (-not (Test-Path (Join-Path $projectRoot "package.json"))) {
    Write-FailAndExit "No package.json found in '$projectRoot'. Use the SPFx solution root."
}

Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host " Setup SPFx Hosted Workbench" -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host "Project: $projectRoot" -ForegroundColor Cyan
Write-Host "Site   : $normalizedSiteUrl" -ForegroundColor Cyan

if (-not $SkipToolchainCheck) {
    if (-not (Test-Path $toolchainScript)) {
        Write-FailAndExit "Required helper missing: '$toolchainScript'."
    }
    Write-Host "Running SPFx toolchain validation..." -ForegroundColor Cyan
    & $toolchainScript
    if ($LASTEXITCODE -ne 0) {
        Write-FailAndExit "Toolchain validation failed."
    }
}

Push-Location $projectRoot
try {
    if (-not $SkipCertInstall) {
        Write-Host "Trusting SPFx dev certificate..." -ForegroundColor Cyan
        npx gulp trust-dev-cert
        if ($LASTEXITCODE -ne 0) {
            Write-FailAndExit "Failed to trust SPFx dev certificate."
        }
    }
} finally {
    Pop-Location
}

$localWorkbenchUrl = "https://localhost:5432/workbench"
$hostedWorkbenchUrl = "$normalizedSiteUrl/_layouts/15/workbench.aspx"
$debugManifestsUrl = "https://localhost:$DebugPort/temp/manifests.js"
$encodedDebugManifests = [System.Uri]::EscapeDataString($debugManifestsUrl)
$hostedDebugUrl = "$hostedWorkbenchUrl?loadSPFX=true&debugManifestsFile=$encodedDebugManifests"

Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host " PASS: Setup checks completed." -ForegroundColor Green
Write-Host "" 
Write-Host "Next commands:" -ForegroundColor Yellow
Write-Host "  cd `"$projectRoot`"" -ForegroundColor Gray
Write-Host "  npx gulp serve --nobrowser" -ForegroundColor Gray
Write-Host ""
Write-Host "Workbench URLs:" -ForegroundColor Yellow
Write-Host "  Local Workbench : $localWorkbenchUrl" -ForegroundColor Gray
Write-Host "  Hosted Workbench: $hostedWorkbenchUrl" -ForegroundColor Gray
Write-Host "  Hosted Debug URL: $hostedDebugUrl" -ForegroundColor Gray
Write-Host ""
Write-Host "Before tenant operations, validate connection with:" -ForegroundColor Yellow
Write-Host "  pwsh -File plugins/workbench-setup/skills/workbench-validate-workbench-environment/scripts/test-spo-connection.ps1" -ForegroundColor Gray
