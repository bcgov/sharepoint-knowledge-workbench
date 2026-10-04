<#
.SYNOPSIS
    Removes an SPFx Form Customizer association from a SharePoint list content type.

.DESCRIPTION
    Restores the standard SharePoint Online out-of-the-box form experience by clearing
    the client-side component IDs and properties (setting them to empty strings) on
    the specified content type.

    Dry-run by default. Pass -Execute to apply changes to SharePoint Online.

.PARAMETER ListName
    The Title or internal name of the target SharePoint list.

.PARAMETER ContentTypeName
    The name of the Content Type to update. Default: "Item".

.PARAMETER Modes
    Which form modes to detach: "New", "Edit", "Display", or "All". Default: @("New", "Edit", "Display").

.PARAMETER Execute
    Switch to execute the live content type update. Omit for dry-run analysis.

.PARAMETER ConfigPath
    Path to a project config.psd1 supplying ClientId/TenantId/SiteUrl (same file format used by
    Connect-Spo in this repo's other SPO-connecting scripts, e.g.
    plugins\sharepoint-migration\config\config-prod.psd1). Required unless -ClientId/-TenantId/
    -SiteUrl are all supplied explicitly.

.PARAMETER SiteUrl
    Optional override for SharePoint site collection URL. Overrides the value from -ConfigPath.

.PARAMETER ClientId
    Optional override for the Azure AD App Registration Client ID (delegated/interactive app,
    e.g. <org>.<project>.interactive). Overrides the value from -ConfigPath. Required (directly or
    via -ConfigPath) — Connect-PnPOnline -Interactive fails with "Specified method is not
    supported" if no ClientId is resolved.

.PARAMETER TenantId
    Optional override for the Azure AD Tenant ID. Overrides the value from -ConfigPath. Required
    (directly or via -ConfigPath).

.PARAMETER TenantAdminUrl
    Optional override for SharePoint Tenant Admin URL.

.EXAMPLE
    pwsh -File scripts/remove-form-customizer-association.ps1 `
      -ListName "Example_Items" `
      -ContentTypeName "Item" `
      -ConfigPath "plugins\sharepoint-migration\config\config-prod.psd1"

.EXAMPLE
    pwsh -File scripts/remove-form-customizer-association.ps1 `
      -ListName "Example_Items" `
      -ContentTypeName "Item" `
      -ConfigPath "plugins\sharepoint-migration\config\config-prod.psd1" `
      -Execute
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ListName,

    [Parameter(Mandatory = $false)]
    [string]$ContentTypeName = "Item",

    [Parameter(Mandatory = $false)]
    [ValidateSet("New", "Edit", "Display", "All")]
    [string[]]$Modes = @("New", "Edit", "Display"),

    [Parameter(Mandatory = $false)]
    [switch]$Execute,

    [Parameter(Mandatory = $false)]
    [string]$ConfigPath = "",

    [Parameter(Mandatory = $false)]
    [string]$SiteUrl = "",

    [Parameter(Mandatory = $false)]
    [string]$ClientId = "",

    [Parameter(Mandatory = $false)]
    [string]$TenantId = "",

    [Parameter(Mandatory = $false)]
    [string]$TenantAdminUrl = ""
)

Set-StrictMode -Version Latest
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

# Normalize modes
$targetModes = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
foreach ($m in $Modes) {
    if ($m -eq "All") {
        $targetModes.Add("New") | Out-Null
        $targetModes.Add("Edit") | Out-Null
        $targetModes.Add("Display") | Out-Null
    } else {
        $targetModes.Add($m) | Out-Null
    }
}

$resolvedConfigPath = Resolve-ConfigPath -ProvidedPath $ConfigPath
$cfgSiteUrl = $null
$cfgClientId = $null
$cfgTenantId = $null
$cfgTenantAdminUrl = $null

if ($resolvedConfigPath) {
    $rawConfig = Import-PowerShellDataFile -LiteralPath $resolvedConfigPath
    $connection = if ($rawConfig.ContainsKey('Connection')) { $rawConfig.Connection } else { $rawConfig }
    $authentication = if ($rawConfig.ContainsKey('Authentication')) { $rawConfig.Authentication } else { $rawConfig }

    $cfgSiteUrl = $connection.SiteUrl
    $cfgClientId = $connection.ClientId
    $cfgTenantId = $connection.TenantId
    if ($authentication -and $authentication.ContainsKey('TenantAdminUrl')) {
        $cfgTenantAdminUrl = $authentication.TenantAdminUrl
    }
}

$targetSiteUrl = if ($SiteUrl) { $SiteUrl } else { $cfgSiteUrl }
$targetClientId = if ($ClientId) { $ClientId } else { $cfgClientId }
$targetTenantId = if ($TenantId) { $TenantId } else { $cfgTenantId }
$targetTenantAdminUrl = if ($TenantAdminUrl) { $TenantAdminUrl } else { $cfgTenantAdminUrl }

if (-not $targetSiteUrl) {
    Write-Error "SiteUrl not resolved. Provide -SiteUrl or -ConfigPath pointing to a config.psd1 with a SiteUrl entry."
    exit 1
}
if (-not $targetClientId) {
    Write-Error "ClientId not resolved. Provide -ClientId or -ConfigPath pointing to a config.psd1 with a ClientId entry (e.g. plugins\sharepoint-migration\config\config-prod.psd1). Connect-PnPOnline -Interactive requires a ClientId — omitting it causes 'Specified method is not supported.'"
    exit 1
}
if (-not $targetTenantId) {
    Write-Error "TenantId not resolved. Provide -TenantId or -ConfigPath pointing to a config.psd1 with a TenantId entry."
    exit 1
}

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "SPFx Form Customizer Removal / Rollback Plan" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "Target Site:    $targetSiteUrl"
Write-Host "Target List:    $ListName"
Write-Host "Content Type:   $ContentTypeName"
Write-Host "Modes to Reset: $($targetModes -join ', ')"
Write-Host "Execution Mode: $(if ($Execute) { 'EXECUTE (Live Write)' } else { 'DRY RUN (Analysis Only)' })"
Write-Host "--------------------------------------------------------"

if (-not $Execute) {
    Write-Host "`n[DRY RUN] No changes made to SharePoint content type." -ForegroundColor Yellow
    Write-Host "To execute the removal and restore default forms, re-run with -Execute." -ForegroundColor Yellow
    exit 0
}

# Connect to SharePoint Online
$connectParams = @{
    Url = $targetSiteUrl
    Interactive = $true
}
if ($targetClientId) { $connectParams["ClientId"] = $targetClientId }
if ($targetTenantId) { $connectParams["Tenant"] = $targetTenantId }
if ($targetTenantAdminUrl) { $connectParams["TenantAdminUrl"] = $targetTenantAdminUrl }

Write-Host "Connecting to SharePoint Online ($targetSiteUrl)..." -ForegroundColor Cyan
Connect-PnPOnline @connectParams

# Fetch current Content Type state
Write-Host "Reading existing content type '$ContentTypeName' on list '$ListName'..."
$currentCt = Get-PnPContentType -List $ListName -Identity $ContentTypeName -ErrorAction SilentlyContinue

if (-not $currentCt) {
    Write-Error "Content type '$ContentTypeName' not found on list '$ListName'."
    exit 1
}

Write-Host "Current Customizer IDs before removal:" -ForegroundColor Gray
Write-Host "  NewFormClientSideComponentId:     $($currentCt.NewFormClientSideComponentId)" -ForegroundColor Gray
Write-Host "  EditFormClientSideComponentId:    $($currentCt.EditFormClientSideComponentId)" -ForegroundColor Gray
Write-Host "  DisplayFormClientSideComponentId: $($currentCt.DisplayFormClientSideComponentId)" -ForegroundColor Gray

# Build Set-PnPContentType parameters resetting IDs and props to empty strings
$setCtParams = @{
    List     = $ListName
    Identity = $ContentTypeName
}

if ($targetModes.Contains("New")) {
    $setCtParams["NewFormClientSideComponentId"] = ""
    $setCtParams["NewFormClientSideComponentProperties"] = ""
}
if ($targetModes.Contains("Edit")) {
    $setCtParams["EditFormClientSideComponentId"] = ""
    $setCtParams["EditFormClientSideComponentProperties"] = ""
}
if ($targetModes.Contains("Display")) {
    $setCtParams["DisplayFormClientSideComponentId"] = ""
    $setCtParams["DisplayFormClientSideComponentProperties"] = ""
}

Write-Host "Clearing Form Customizer associations via Set-PnPContentType..." -ForegroundColor Cyan
Set-PnPContentType @setCtParams

# Verify readback
Write-Host "Verifying content type properties post-removal..." -ForegroundColor Cyan
$verifiedCt = Get-PnPContentType -List $ListName -Identity $ContentTypeName

$failed = $false

if ($targetModes.Contains("New") -and $verifiedCt.NewFormClientSideComponentId -and $verifiedCt.NewFormClientSideComponentId -ne [System.Guid]::Empty.ToString()) {
    Write-Error "NewFormClientSideComponentId was not cleared: found '$($verifiedCt.NewFormClientSideComponentId)'."
    $failed = $true
}
if ($targetModes.Contains("Edit") -and $verifiedCt.EditFormClientSideComponentId -and $verifiedCt.EditFormClientSideComponentId -ne [System.Guid]::Empty.ToString()) {
    Write-Error "EditFormClientSideComponentId was not cleared: found '$($verifiedCt.EditFormClientSideComponentId)'."
    $failed = $true
}
if ($targetModes.Contains("Display") -and $verifiedCt.DisplayFormClientSideComponentId -and $verifiedCt.DisplayFormClientSideComponentId -ne [System.Guid]::Empty.ToString()) {
    Write-Error "DisplayFormClientSideComponentId was not cleared: found '$($verifiedCt.DisplayFormClientSideComponentId)'."
    $failed = $true
}

if ($failed) {
    Write-Error "Removal verification failed."
    exit 1
}

Write-Host "========================================================" -ForegroundColor Green
Write-Host "PASS: Form Customizer association successfully removed." -ForegroundColor Green
Write-Host "Standard out-of-the-box SharePoint forms restored." -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Green
