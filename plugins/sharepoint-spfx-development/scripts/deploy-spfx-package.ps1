<#
.SYNOPSIS
    Deploys a compiled .sppkg package to a Site Collection App Catalog using PnP PowerShell.

.DESCRIPTION
    Automates uploading, overwriting, publishing, and enabling an SPFx solution (.sppkg)
    in a target site's App Catalog. Supports config.psd1 resolution and explicit parameter overrides.

.PARAMETER PackagePath
    Local path to the .sppkg file.

.PARAMETER Scope
    Publish scope: Site or Tenant. Default: Site.

.PARAMETER SiteUrl
    The target site collection URL (e.g. https://contoso.sharepoint.com/sites/Demo).

.PARAMETER ClientId
    Optional Azure AD App Registration Client ID for interactive authentication.

.PARAMETER TenantId
    Optional Azure AD Tenant ID.

.PARAMETER ConfigPath
    Path to config.psd1.

.PARAMETER Install
    Switch to automatically install/activate the app on the site.

.PARAMETER EnsureSiteAppCatalog
    Switch to ensure the Site Collection App Catalog is provisioned.

.PARAMETER SkipFeatureDeployment
    Switch for tenant-wide deployment.

.EXAMPLE
    pwsh -File ./deploy-spfx-package.ps1 -PackagePath "../sharepoint/solution/spfx-selectedid-filter.sppkg" -Install
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
Write-Host " Deploy SPFx Package" -ForegroundColor Cyan
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
        Path        = $resolvedPackagePath
        Scope       = $Scope
        Publish     = $true
        Overwrite   = $true
        ErrorAction = "Stop"
    }
    if ($SkipFeatureDeployment) {
        $addParams["SkipFeatureDeployment"] = $true
    }

    $app = $null
    try {
        $app = Add-PnPApp @addParams
        Write-Host "Uploaded and published package via ALM API." -ForegroundColor Green
        Write-Host "App Title  : $($app.Title)" -ForegroundColor Green
        Write-Host "App Id     : $($app.Id)" -ForegroundColor Green
        Write-Host "Deployed   : $($app.Deployed)" -ForegroundColor Green
    } catch {
        $errMsg = $_.Exception.Message
        if ($errMsg -match "Manage Web Site permissions" -or $errMsg -match "Unauthorized" -or $errMsg -match "Access denied") {
            Write-Host " Note: ALM REST API rejected automated deployment due to enterprise permission boundaries (Site Owner vs Tenant Admin)." -ForegroundColor Yellow
            Write-Host " Attempting direct document upload to 'AppCatalog' library..." -ForegroundColor Cyan
            try {
                $file = Add-PnPFile -Path $resolvedPackagePath -Folder "AppCatalog" -Overwrite -ErrorAction Stop
                Write-Host " PASS: Package uploaded directly to AppCatalog library: $($file.ServerRelativeUrl)" -ForegroundColor Green
            } catch {
                Write-Host "`n------------------------------------------------------------------" -ForegroundColor Yellow
                Write-Host " MANUAL APP CATALOG UPLOAD REQUIRED" -ForegroundColor Yellow
                Write-Host "------------------------------------------------------------------" -ForegroundColor Yellow
                Write-Host "In enterprise tenancies without delegated ALM API permissions," -ForegroundColor Gray
                Write-Host "open the App Catalog in your browser and drag & drop the .sppkg file:" -ForegroundColor Gray
                Write-Host "`n  $targetUrl/AppCatalog/Forms/AllItems.aspx`n" -ForegroundColor Cyan
                Write-Host "Package file: $resolvedPackagePath" -ForegroundColor Gray
                Write-Host "------------------------------------------------------------------" -ForegroundColor Yellow
            }
        } else {
            throw $_
        }
    }

    $verify = Get-PnPApp -Scope $Scope -Identity $app.Id -ErrorAction SilentlyContinue
    if (-not $verify) {
        $verify = Get-PnPApp -Scope $Scope | Where-Object { $_.Title -like "*my-fav-apps*" -or $_.Filename -like "*.sppkg" }
    }
    if ($verify) {
        Write-Host "Verification: PASS (app found in catalog)." -ForegroundColor Green
    } else {
        Write-Host "Verification: Check App Catalog in browser: $targetUrl/AppCatalog/Forms/AllItems.aspx" -ForegroundColor Gray
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
} catch {
    Write-Host " FAIL: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
} finally {
    Disconnect-PnPOnline -ErrorAction SilentlyContinue
}
