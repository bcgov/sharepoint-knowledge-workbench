<#
.SYNOPSIS
    Deploys a compiled .sppkg package to a Site Collection App Catalog using PnP PowerShell.

.DESCRIPTION
    Automates uploading, overwriting, publishing, and enabling an SPFx solution (.sppkg)
    in a target site's App Catalog.

.PARAMETER SiteUrl
    The target site collection URL (e.g. https://<tenant>.sharepoint.com/sites/<SiteName>).

.PARAMETER PackagePath
    Local path to the .sppkg file.

.PARAMETER ClientId
    Optional Azure AD App Registration Client ID for interactive authentication.

.EXAMPLE
    pwsh -File ./deploy-spfx-package.ps1 -SiteUrl "https://contoso.sharepoint.com/sites/TargetSite" -PackagePath "../sharepoint/solution/spfx-selectedid-filter.sppkg"
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$SiteUrl,

    [Parameter(Mandatory = $true)]
    [string]$PackagePath,

    [Parameter(Mandatory = $false)]
    [string]$ClientId
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $PackagePath)) {
    Write-Host "Error: Package file not found at: $PackagePath" -ForegroundColor Red
    exit 1
}

$resolvedPackagePath = (Resolve-Path $PackagePath).Path
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host " Deploy SPFx Package: $resolvedPackagePath" -ForegroundColor Cyan
Write-Host " Target Site:         $SiteUrl" -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan

try {
    Write-Host "Connecting to target site..." -ForegroundColor Cyan
    if ($ClientId) {
        Connect-PnPOnline -Url $SiteUrl -ClientId $ClientId -Interactive
    } else {
        Connect-PnPOnline -Url $SiteUrl -Interactive
    }

    Write-Host "Uploading and publishing .sppkg package to Site App Catalog..." -ForegroundColor Cyan
    $app = Add-PnPApp -Path $resolvedPackagePath -Scope Site -Publish -Overwrite -ErrorAction Stop

    Write-Host "Package deployed successfully!" -ForegroundColor Green
    Write-Host " App Title:  $($app.Title)" -ForegroundColor Green
    Write-Host " App ID:     $($app.Id)" -ForegroundColor Green
    Write-Host " Deployed:   $($app.Deployed)" -ForegroundColor Green
    Write-Host " Enabled:    $($app.AppCatalogVersion)" -ForegroundColor Green

} catch {
    Write-Host " FAIL: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
