<#
.SYNOPSIS
    Associates an SPFx Form Customizer component ID and properties with a SharePoint list content type.

.DESCRIPTION
    Binds an SPFx Form Customizer extension GUID to a list's content type properties
    (NewFormClientSideComponentId, EditFormClientSideComponentId, DisplayFormClientSideComponentId).
    
    Dry-run by default. Pass -Execute to apply changes to SharePoint Online.
    Captures pre-existing state for audit and rollback verification before modifying.

.PARAMETER ListName
    The Title or internal name of the target SharePoint list.

.PARAMETER ContentTypeName
    The name of the Content Type to update. Default: "Item".

.PARAMETER ComponentId
    The Form Customizer manifest GUID (e.g. "e672956c-38d7-4c8d-b778-9e55b4fa3977").

.PARAMETER ComponentProperties
    Optional JSON-formatted properties string passed to the customizer at runtime.

.PARAMETER Modes
    Which form modes to associate: "New", "Edit", "Display", or any combination. Default: @("New", "Edit", "Display").

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
    e.g. ag.csb.cmat.interactive). Overrides the value from -ConfigPath. Required (directly or
    via -ConfigPath) — Connect-PnPOnline -Interactive fails with "Specified method is not
    supported" if no ClientId is resolved.

.PARAMETER TenantId
    Optional override for the Azure AD Tenant ID. Overrides the value from -ConfigPath. Required
    (directly or via -ConfigPath).

.PARAMETER TenantAdminUrl
    Optional override for SharePoint Tenant Admin URL.

.EXAMPLE
    pwsh -File scripts/associate-form-customizer.ps1 `
      -ListName "PIO_Narratives" `
      -ContentTypeName "Item" `
      -ComponentId "e672956c-38d7-4c8d-b778-9e55b4fa3977" `
      -ConfigPath "plugins\sharepoint-migration\config\config-prod.psd1"

.EXAMPLE
    pwsh -File scripts/associate-form-customizer.ps1 `
      -ListName "PIO_Narratives" `
      -ContentTypeName "Item" `
      -ComponentId "e672956c-38d7-4c8d-b778-9e55b4fa3977" `
      -ConfigPath "plugins\sharepoint-migration\config\config-prod.psd1" `
      -Modes @("New") `
      -Execute
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ListName,

    [Parameter(Mandatory = $false)]
    [string]$ContentTypeName = "Item",

    [Parameter(Mandatory = $true)]
    [string]$ComponentId,

    [Parameter(Mandatory = $false)]
    [string]$ComponentProperties = "",

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

# Validate ComponentId format (GUID)
if (-not [System.Guid]::TryParse($ComponentId, [ref][System.Guid]::Empty)) {
    Write-Error "Invalid ComponentId GUID format: '$ComponentId'."
    exit 1
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
Write-Host "SPFx Form Customizer Association Plan" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "Target Site:         $targetSiteUrl"
Write-Host "Target List:         $ListName"
Write-Host "Content Type:        $ContentTypeName"
Write-Host "Component ID (GUID): $ComponentId"
Write-Host "Component Props:     $(if ($ComponentProperties) { $ComponentProperties } else { '<None>' })"
Write-Host "Target Modes:        $($targetModes -join ', ')"
Write-Host "Execution Mode:      $(if ($Execute) { 'EXECUTE (Live Write)' } else { 'DRY RUN (Analysis Only)' })"
Write-Host "--------------------------------------------------------"

if (-not $Execute) {
    Write-Host "`n[DRY RUN] No changes made to SharePoint content type." -ForegroundColor Yellow
    Write-Host "To apply these changes, re-run with -Execute." -ForegroundColor Yellow
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

# Fetch current Content Type state for backup
Write-Host "Reading existing content type '$ContentTypeName' on list '$ListName'..."
$currentCt = Get-PnPContentType -List $ListName -Identity $ContentTypeName -ErrorAction SilentlyContinue

if (-not $currentCt) {
    Write-Error "Content type '$ContentTypeName' not found on list '$ListName'."
    exit 1
}

$priorState = [ordered]@{
    Timestamp                        = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    ListName                         = $ListName
    ContentTypeName                  = $ContentTypeName
    ContentTypeId                    = $currentCt.StringId
    NewFormClientSideComponentId     = $currentCt.NewFormClientSideComponentId
    NewFormClientSideComponentProps  = $currentCt.NewFormClientSideComponentProperties
    EditFormClientSideComponentId    = $currentCt.EditFormClientSideComponentId
    EditFormClientSideComponentProps = $currentCt.EditFormClientSideComponentProperties
    DisplayFormClientSideComponentId = $currentCt.DisplayFormClientSideComponentId
    DisplayFormClientSideComponentProps = $currentCt.DisplayFormClientSideComponentProperties
}

Write-Host "Captured prior content type state:" -ForegroundColor Gray
$priorState | Format-List | Out-String | Write-Host -ForegroundColor Gray

# Build Set-PnPContentType parameters
$setCtParams = @{
    List     = $ListName
    Identity = $ContentTypeName
}

if ($targetModes.Contains("New")) {
    $setCtParams["NewFormClientSideComponentId"] = $ComponentId
    if ($ComponentProperties) { $setCtParams["NewFormClientSideComponentProperties"] = $ComponentProperties }
}
if ($targetModes.Contains("Edit")) {
    $setCtParams["EditFormClientSideComponentId"] = $ComponentId
    if ($ComponentProperties) { $setCtParams["EditFormClientSideComponentProperties"] = $ComponentProperties }
}
if ($targetModes.Contains("Display")) {
    $setCtParams["DisplayFormClientSideComponentId"] = $ComponentId
    if ($ComponentProperties) { $setCtParams["DisplayFormClientSideComponentProperties"] = $ComponentProperties }
}

Write-Host "Applying Form Customizer association via Set-PnPContentType..." -ForegroundColor Cyan
Set-PnPContentType @setCtParams

# Read back and verify
Write-Host "Verifying content type properties post-update..." -ForegroundColor Cyan
$verifiedCt = Get-PnPContentType -List $ListName -Identity $ContentTypeName

$verificationFailed = $false

if ($targetModes.Contains("New")) {
    if ($verifiedCt.NewFormClientSideComponentId -ne $ComponentId) {
        Write-Error "NewFormClientSideComponentId readback mismatch: expected '$ComponentId', found '$($verifiedCt.NewFormClientSideComponentId)'."
        $verificationFailed = $true
    }
}
if ($targetModes.Contains("Edit")) {
    if ($verifiedCt.EditFormClientSideComponentId -ne $ComponentId) {
        Write-Error "EditFormClientSideComponentId readback mismatch: expected '$ComponentId', found '$($verifiedCt.EditFormClientSideComponentId)'."
        $verificationFailed = $true
    }
}
if ($targetModes.Contains("Display")) {
    if ($verifiedCt.DisplayFormClientSideComponentId -ne $ComponentId) {
        Write-Error "DisplayFormClientSideComponentId readback mismatch: expected '$ComponentId', found '$($verifiedCt.DisplayFormClientSideComponentId)'."
        $verificationFailed = $true
    }
}

if ($verificationFailed) {
    Write-Error "Association verification failed."
    exit 1
}

Write-Host "========================================================" -ForegroundColor Green
Write-Host "PASS: Form Customizer successfully associated and verified." -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Green
