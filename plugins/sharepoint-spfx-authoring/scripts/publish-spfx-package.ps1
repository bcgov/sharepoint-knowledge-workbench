<#
.SYNOPSIS
    Publishes an SPFx .sppkg package to either a Site Collection App Catalog
    or Tenant App Catalog using config.psd1 (nested or flat schema).

.DESCRIPTION
    This script supports trial-tenancy style deployment where the operator can
    choose scope:
      - Site:   Connect to SiteUrl and publish with -Scope Site
      - Tenant: Connect to TenantAdminUrl and publish with -Scope Tenant

    It validates package existence, resolves connection settings from
    config.psd1, uploads/publishes with overwrite, and performs a basic
    verification readback via Get-PnPApp.

    Key Input Dependencies:
      - config.psd1 (nested Connection/Authentication schema or flat schema)
      - PnP.PowerShell module
      - Existing .sppkg package file

    Procedure Index:
      - Resolve-ConfigPath
      - Main publish execution flow (connect -> publish -> verify)

.PARAMETER PackagePath
    Path to the .sppkg package file.

.PARAMETER Scope
    Publish scope: Site or Tenant. Default: Site.

.PARAMETER ConfigPath
    Path to config.psd1. Defaults to repository root config.psd1 if found.

.PARAMETER SiteUrl
    Optional override for Site scope target URL.

.PARAMETER TenantAdminUrl
    Optional override for Tenant scope target URL.

.PARAMETER ClientId
    Optional override for ClientId.

.PARAMETER TenantId
    Optional override for TenantId.

.EXAMPLE
    pwsh -File scripts/publish-spfx-package.ps1 `
      -PackagePath "temp\bcps-webparts\Technical Documentation\crownnet-my-fav-apps\crownnet-my-fav-apps\sharepoint\solution\my-fav-apps-dev.sppkg" `
      -Scope Site

.EXAMPLE
    pwsh -File scripts/publish-spfx-package.ps1 `
      -PackagePath ".\sharepoint\solution\my-fav-apps-dev.sppkg" `
      -Scope Tenant
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$PackagePath,

    [Parameter(Mandatory = $false)]
    [ValidateSet("Site", "Tenant")]
    [string]$Scope = "Site",

    [Parameter(Mandatory = $false)]
    [string]$ConfigPath = "",

    [Parameter(Mandatory = $false)]
    [string]$SiteUrl = "",

    [Parameter(Mandatory = $false)]
    [string]$TenantAdminUrl = "",

    [Parameter(Mandatory = $false)]
    [string]$ClientId = "",

    [Parameter(Mandatory = $false)]
    [string]$TenantId = "",

    [Parameter(Mandatory = $false)]
    [switch]$Install,

    [Parameter(Mandatory = $false)]
    [switch]$EnsureSiteAppCatalog,

    [Parameter(Mandatory = $false)]
    [switch]$SkipFeatureDeployment
)

$ErrorActionPreference = "Stop"

function Resolve-ConfigPath {
    param([string]$ProvidedPath)

    if ($ProvidedPath -and (Test-Path -LiteralPath $ProvidedPath)) {
        return (Resolve-Path -LiteralPath $ProvidedPath).Path
    }

    $candidates = @(
        "$PWD\config.psd1",
        "$PSScriptRoot\..\..\..\config.psd1",
        "$PSScriptRoot\..\..\config.psd1",
        "$PSScriptRoot\..\config.psd1",
        "$PSScriptRoot\config.psd1"
    )

    foreach ($cand in $candidates) {
        if (Test-Path -LiteralPath $cand) {
            return (Resolve-Path -LiteralPath $cand).Path
        }
    }

    return $null
}

if (-not (Test-Path -LiteralPath $PackagePath)) {
    Write-Error "Package file not found: $PackagePath"
    exit 1
}

$resolvedPackagePath = (Resolve-Path -LiteralPath $PackagePath).Path
$resolvedConfigPath = Resolve-ConfigPath -ProvidedPath $ConfigPath

$cfgSiteUrl = $null
$cfgTenantAdminUrl = $null
$cfgClientId = $null
$cfgTenantId = $null

if ($resolvedConfigPath) {
    $rawConfig = Import-PowerShellDataFile -LiteralPath $resolvedConfigPath
    $connection = if ($rawConfig.Connection) { $rawConfig.Connection } else { $rawConfig }
    $authentication = if ($rawConfig.Authentication) { $rawConfig.Authentication } else { $rawConfig }

    $cfgSiteUrl = $connection.SiteUrl
    $cfgClientId = $connection.ClientId
    $cfgTenantId = $connection.TenantId
    $cfgTenantAdminUrl = $authentication.TenantAdminUrl
}

$finalSiteUrl = if ($SiteUrl) { $SiteUrl } else { $cfgSiteUrl }
$finalTenantAdminUrl = if ($TenantAdminUrl) { $TenantAdminUrl } else { $cfgTenantAdminUrl }
$finalClientId = if ($ClientId) { $ClientId } else { $cfgClientId }
$finalTenantId = if ($TenantId) { $TenantId } else { $cfgTenantId }

if (-not $finalClientId -or -not $finalTenantId) {
    Write-Error "ClientId and TenantId are required (from config or parameters)."
    exit 1
}

if ($Scope -eq "Site" -and -not $finalSiteUrl) {
    Write-Error "Scope=Site requires SiteUrl (from config or -SiteUrl)."
    exit 1
}

if ($Scope -eq "Tenant" -and -not $finalTenantAdminUrl) {
    Write-Error "Scope=Tenant requires TenantAdminUrl (from config or -TenantAdminUrl)."
    exit 1
}

$targetUrl = if ($Scope -eq "Site") { $finalSiteUrl } else { $finalTenantAdminUrl }

Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host " Publish SPFx Package" -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host "Scope      : $Scope" -ForegroundColor Gray
Write-Host "Target URL : $targetUrl" -ForegroundColor Gray
Write-Host "Package    : $resolvedPackagePath" -ForegroundColor Gray
if ($resolvedConfigPath) {
    Write-Host "Config     : $resolvedConfigPath" -ForegroundColor Gray
}
Write-Host "==================================================================" -ForegroundColor Cyan

try {
    Import-Module PnP.PowerShell -ErrorAction Stop

    Connect-PnPOnline -Url $targetUrl -ClientId $finalClientId -Tenant $finalTenantId -Interactive

    if ($EnsureSiteAppCatalog -and $Scope -eq "Site") {
        Write-Host "Ensuring Site Collection App Catalog exists..." -ForegroundColor Cyan
        Add-PnPSiteCollectionAppCatalog -ErrorAction SilentlyContinue | Out-Null
    }

    $addParams = @{
        Path      = $resolvedPackagePath
        Scope     = $Scope
        Publish   = $true
        Overwrite = $true
        ErrorAction = "Stop"
    }
    if ($SkipFeatureDeployment) {
        $addParams["SkipFeatureDeployment"] = $true
    }

    $app = Add-PnPApp @addParams
    Write-Host "Uploaded and published package." -ForegroundColor Green
    Write-Host "App Title  : $($app.Title)" -ForegroundColor Green
    Write-Host "App Id     : $($app.Id)" -ForegroundColor Green
    Write-Host "Deployed   : $($app.Deployed)" -ForegroundColor Green

    $verify = Get-PnPApp -Scope $Scope -Identity $app.Id -ErrorAction SilentlyContinue
    if ($verify) {
        Write-Host "Verification: PASS (app found in catalog)." -ForegroundColor Green
    } else {
        Write-Host "Verification: WARNING (app not returned by Get-PnPApp)." -ForegroundColor Yellow
    }

    if ($Install -and $Scope -eq "Site") {
        Write-Host "Installing app on the current site ($finalSiteUrl)..." -ForegroundColor Cyan
        try {
            Install-PnPApp -Identity $app.Id -Scope Site -ErrorAction Stop | Out-Null
            Write-Host "Installed app onto site successfully." -ForegroundColor Green
        } catch {
            Write-Host "App installation note: $($_.Exception.Message)" -ForegroundColor Yellow
        }
    }
}
catch {
    Write-Host "FAIL: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
finally {
    Disconnect-PnPOnline -ErrorAction SilentlyContinue
}
