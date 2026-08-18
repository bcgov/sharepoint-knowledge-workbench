<#
.SYNOPSIS
    Verifies the Site Collection App Catalog on a target SharePoint Online site.

.DESCRIPTION
    Connects to SharePoint Online and verifies whether a Site Collection App Catalog
    is provisioned and ready for .sppkg package deployment.

.PARAMETER SiteUrl
    The target site collection URL (e.g. https://<tenant>.sharepoint.com/sites/<SiteName>).

.PARAMETER AdminUrl
    Optional SharePoint tenant admin endpoint (e.g. https://<tenant>-admin.sharepoint.com).
    When provided, queries Get-PnPSiteCollectionAppCatalog at the tenant level.

.PARAMETER ClientId
    Optional Azure AD App Registration Client ID for interactive authentication.

.EXAMPLE
    pwsh -File ./verify-app-catalog.ps1 -SiteUrl "https://bcgov.sharepoint.com/sites/AG-CSB-ITAU-CMAT-TEST"
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$SiteUrl,

    [Parameter(Mandatory = $false)]
    [string]$AdminUrl,

    [Parameter(Mandatory = $false)]
    [string]$ClientId
)

$ErrorActionPreference = "Stop"

Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host " Verify Site Collection App Catalog: $SiteUrl" -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan

try {
    # 1. If AdminUrl provided, query tenant catalog list
    if ($AdminUrl) {
        Write-Host "Connecting to Tenant Admin endpoint: $AdminUrl..." -ForegroundColor Cyan
        if ($ClientId) {
            Connect-PnPOnline -Url $AdminUrl -ClientId $ClientId -Interactive
        } else {
            Connect-PnPOnline -Url $AdminUrl -Interactive
        }

        $catalogs = Get-PnPSiteCollectionAppCatalog
        if ($catalogs) {
            $match = $catalogs | Where-Object { $_.AbsoluteUrl -like "*$($SiteUrl.TrimEnd('/'))*" }
            if ($match) {
                Write-Host " PASS: Site Collection App Catalog confirmed via Tenant Admin query on $SiteUrl" -ForegroundColor Green
                exit 0
            }
        }
    }

    # 2. Connect directly to target site and inspect AppCatalog subweb / library
    Write-Host "Connecting directly to target site: $SiteUrl..." -ForegroundColor Cyan
    if ($ClientId) {
        Connect-PnPOnline -Url $SiteUrl -ClientId $ClientId -Interactive
    } else {
        Connect-PnPOnline -Url $SiteUrl -Interactive
    }

    $appCatalogSubweb = "$($SiteUrl.TrimEnd('/'))/AppCatalog"
    Write-Host "Checking direct AppCatalog library accessibility at: $appCatalogSubweb..." -ForegroundColor Cyan

    try {
        Connect-PnPOnline -Url $appCatalogSubweb -Interactive -ErrorAction Stop
        $appsList = Get-PnPList -Identity "AppCatalog" -ErrorAction SilentlyContinue
        if (-not $appsList) {
            $appsList = Get-PnPList -Identity "Apps for SharePoint" -ErrorAction SilentlyContinue
        }

        if ($appsList) {
            Write-Host " PASS: App Catalog library verified ('$($appsList.Title)', ItemCount=$($appsList.ItemCount))" -ForegroundColor Green
            Write-Host " Direct Upload URL: $appCatalogSubweb/AppCatalog" -ForegroundColor Yellow
        } else {
            Write-Host " WARNING: AppCatalog subweb exists but 'Apps for SharePoint' library was not found." -ForegroundColor Yellow
        }
    } catch {
        Write-Host " NOTICE: Could not connect to $appCatalogSubweb directly ($($_.Exception.Message))." -ForegroundColor Yellow
        Write-Host " Please verify tenant admin has run Add-PnPSiteCollectionAppCatalog." -ForegroundColor Yellow
    }

} catch {
    Write-Host " FAIL: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
