<#
.SYNOPSIS
    Audits and validates the Form Customizer association state of a SharePoint list content type.

.DESCRIPTION
    Read-only inspection script. Connects to SharePoint Online, queries the specified
    list content type, and outputs the client-side component IDs, properties, and
    matching status against an expected Component ID.

.PARAMETER ListName
    The Title or internal name of the target SharePoint list.

.PARAMETER ContentTypeName
    The name of the Content Type to inspect. Default: "Item".

.PARAMETER ExpectedComponentId
    Optional expected Form Customizer manifest GUID to validate against.

.PARAMETER OutputJson
    Switch to output result strictly as formatted JSON.

.PARAMETER ConfigPath
    Optional path to config.psd1.

.PARAMETER SiteUrl
    Optional override for SharePoint site collection URL.

.PARAMETER ClientId
    Optional override for Azure AD App Registration Client ID.

.PARAMETER TenantId
    Optional override for Azure AD Tenant ID.

.PARAMETER TenantAdminUrl
    Optional override for SharePoint Tenant Admin URL.

.EXAMPLE
    pwsh -File scripts/validate-form-customizer-association.ps1 `
      -ListName "Narratives" `
      -ContentTypeName "Item"

.EXAMPLE
    pwsh -File scripts/validate-form-customizer-association.ps1 `
      -ListName "Narratives" `
      -ContentTypeName "Item" `
      -ExpectedComponentId "e672956c-38d7-4c8d-b778-9e55b4fa3977" `
      -OutputJson
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ListName,

    [Parameter(Mandatory = $false)]
    [string]$ContentTypeName = "Item",

    [Parameter(Mandatory = $false)]
    [string]$ExpectedComponentId = "",

    [Parameter(Mandatory = $false)]
    [switch]$OutputJson,

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
    Write-Error "SiteUrl not resolved. Provide -SiteUrl or configure config.psd1."
    exit 1
}

# Connect to SharePoint Online
$connectParams = @{
    Url = $targetSiteUrl
    Interactive = $true
}
if ($targetClientId) { $connectParams["ClientId"] = $targetClientId }
if ($targetTenantId) { $connectParams["Tenant"] = $targetTenantId }
if ($targetTenantAdminUrl) { $connectParams["TenantAdminUrl"] = $targetTenantAdminUrl }

if (-not $OutputJson) {
    Write-Host "Connecting to SharePoint Online ($targetSiteUrl)..." -ForegroundColor Cyan
}
Connect-PnPOnline @connectParams

$ct = Get-PnPContentType -List $ListName -Identity $ContentTypeName -ErrorAction SilentlyContinue

if (-not $ct) {
    Write-Error "Content type '$ContentTypeName' not found on list '$ListName'."
    exit 1
}

$hasCustomNew = [bool]($ct.NewFormClientSideComponentId -and $ct.NewFormClientSideComponentId -ne [System.Guid]::Empty.ToString())
$hasCustomEdit = [bool]($ct.EditFormClientSideComponentId -and $ct.EditFormClientSideComponentId -ne [System.Guid]::Empty.ToString())
$hasCustomDisplay = [bool]($ct.DisplayFormClientSideComponentId -and $ct.DisplayFormClientSideComponentId -ne [System.Guid]::Empty.ToString())

$matchesExpected = $true
if ($ExpectedComponentId) {
    if ($hasCustomNew -and ($ct.NewFormClientSideComponentId -ne $ExpectedComponentId)) { $matchesExpected = $false }
    if ($hasCustomEdit -and ($ct.EditFormClientSideComponentId -ne $ExpectedComponentId)) { $matchesExpected = $false }
    if ($hasCustomDisplay -and ($ct.DisplayFormClientSideComponentId -ne $ExpectedComponentId)) { $matchesExpected = $false }
    if (-not ($hasCustomNew -or $hasCustomEdit -or $hasCustomDisplay)) { $matchesExpected = $false }
}

$auditResult = [ordered]@{
    SiteUrl                          = $targetSiteUrl
    ListName                         = $ListName
    ContentTypeName                  = $ContentTypeName
    ContentTypeId                    = $ct.StringId
    NewFormCustomizerActive          = $hasCustomNew
    NewFormComponentId               = $ct.NewFormClientSideComponentId
    NewFormComponentProperties       = $ct.NewFormClientSideComponentProperties
    EditFormCustomizerActive         = $hasCustomEdit
    EditFormComponentId              = $ct.EditFormClientSideComponentId
    EditFormComponentProperties      = $ct.EditFormClientSideComponentProperties
    DisplayFormCustomizerActive      = $hasCustomDisplay
    DisplayFormComponentId           = $ct.DisplayFormClientSideComponentId
    DisplayFormComponentProperties   = $ct.DisplayFormClientSideComponentProperties
    ExpectedComponentId              = $ExpectedComponentId
    MatchesExpectedComponentId       = if ($ExpectedComponentId) { $matchesExpected } else { $null }
}

if ($OutputJson) {
    $auditResult | ConvertTo-Json -Depth 5
} else {
    Write-Host "========================================================" -ForegroundColor Cyan
    Write-Host "SPFx Form Customizer Association Status" -ForegroundColor Cyan
    Write-Host "========================================================" -ForegroundColor Cyan
    $auditResult | Format-List | Out-String | Write-Host
    if ($ExpectedComponentId) {
        if ($matchesExpected) {
            Write-Host "VALIDATION PASS: Content type matches expected component ID." -ForegroundColor Green
        } else {
            Write-Host "VALIDATION FAIL: Content type does not match expected component ID." -ForegroundColor Red
        }
    }
}
