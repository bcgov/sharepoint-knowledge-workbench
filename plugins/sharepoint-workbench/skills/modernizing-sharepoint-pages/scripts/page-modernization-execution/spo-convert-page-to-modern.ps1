<#
.SYNOPSIS
Converts a single classic SharePoint page to a modern Site Page and stamps
caller-supplied metadata onto the converted page.

.DESCRIPTION
By default performs no SharePoint tenant I/O; with -Execute and the
confirmation token it runs the reviewed PnP.PowerShell flow:
  1. Look up the source page in -SourceLibrary by filename.
  2. ConvertTo-PnPPage -Overwrite -KeepPageCreationModificationInformation
     -CopyPageMetadata, converting within the same site.
  3. Find the converted page in -TargetLibrary.
  4. Set-PnPListItem, stamping fields per -FieldMapping (a JSON object mapping
     source field internal names to target field internal names) plus any
     literal values supplied via -LiteralFieldValues.

ConvertTo-PnPPage's -UrlMappingFile/-SkipUrlRewriting parameters only apply
to cross-site transformations; converting within one site (this script's
scope) does not rewrite embedded links in the page body. Run a separate link
remediation pass afterward if the source content contains embedded links.

.PARAMETER PageName
Filename of the page to convert (matched against FileLeafRef), e.g.
"article.aspx". Required.

.PARAMETER SourceLibrary
Library containing the classic source page. Required.

.PARAMETER TargetLibrary
Library the converted modern page lands in. Defaults to "Site Pages".

.PARAMETER FieldMapping
Path to a JSON file mapping source field internal names to target field
internal names, e.g. {"MediaCategory": "PageCategory"}. Optional -- omit for
no field mapping.

.PARAMETER LiteralFieldValues
Path to a JSON file of target-field-internal-name -> literal value pairs
stamped onto every converted page regardless of source content (e.g. a
migration tag or a PromotedState flag). Optional.

.PARAMETER SiteUrl
Overrides config.psd1 Connection.SiteUrl.

.PARAMETER ConfigPath
Path to config.psd1. Defaults to the repository root config.psd1.

.PARAMETER ClientId
Overrides ConfigPath ClientId.

.PARAMETER TenantId
Overrides ConfigPath TenantId.

.PARAMETER TenantAdminUrl
Overrides ConfigPath Authentication.TenantAdminUrl.

.PARAMETER Execute
Runs the real PnP.PowerShell conversion/metadata-stamp calls. Omit this to
print the plan only.

.PARAMETER ConfirmToken
Required with -Execute. Must be CONVERT-SPO-PAGE.

.EXAMPLE
.\spo-convert-page-to-modern.ps1 -PageName "article.aspx" -SourceLibrary "ClassicPages" -Execute -ConfirmToken CONVERT-SPO-PAGE
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$PageName,

    [Parameter(Mandatory = $true)]
    [string]$SourceLibrary,

    [string]$TargetLibrary = "Site Pages",

    [string]$FieldMapping,

    [string]$LiteralFieldValues,

    [string]$SiteUrl,

    [string]$ConfigPath = (Join-Path $PSScriptRoot "..\..\..\config.psd1"),

    [string]$ClientId,

    [string]$TenantId,

    [string]$TenantAdminUrl,

    [switch]$Execute,

    [string]$ConfirmToken
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

. (Join-Path $PSScriptRoot "Get-WorkbenchConnectionConfig.ps1")

function Get-JsonFileOrEmpty {
    [CmdletBinding()]
    param([string]$Path)
    if (-not $Path) { return [ordered]@{} }
    if (-not (Test-Path -LiteralPath $Path)) { throw "File not found: $Path" }
    $parsed = Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
    $result = [ordered]@{}
    foreach ($property in $parsed.PSObject.Properties) { $result[$property.Name] = $property.Value }
    return $result
}

$connectionConfig = Get-WorkbenchConnectionConfig -Path $ConfigPath
if (-not $SiteUrl) { $SiteUrl = $connectionConfig.SiteUrl }
if (-not $ClientId) { $ClientId = $connectionConfig.ClientId }
if (-not $TenantId) { $TenantId = $connectionConfig.TenantId }
if (-not $TenantAdminUrl) { $TenantAdminUrl = $connectionConfig.TenantAdminUrl }

if (-not $SiteUrl -or -not $ClientId -or -not $TenantId) {
    throw "SiteUrl/ClientId/TenantId not resolved. Provide -SiteUrl/-ClientId/-TenantId or a valid -ConfigPath."
}

$fieldMappingTable = Get-JsonFileOrEmpty -Path $FieldMapping
$literalFieldValuesTable = Get-JsonFileOrEmpty -Path $LiteralFieldValues

$plan = [ordered]@{
    operation = "convert-page-to-modern"
    site_url = $SiteUrl
    source = [ordered]@{ library = $SourceLibrary; page_name = $PageName }
    target = [ordered]@{ library = $TargetLibrary }
    field_mapping = $fieldMappingTable
    literal_field_values = $literalFieldValuesTable
    safety = [ordered]@{
        tenant_io = $(if ($Execute) { "pnp-write" } else { "none" })
        execute_requires_confirm_token = "CONVERT-SPO-PAGE"
        note = "ConvertTo-PnPPage does not rewrite embedded links for same-site conversions -- run link remediation separately if needed."
    }
}

if ($Execute) {
    if ($ConfirmToken -ne "CONVERT-SPO-PAGE") {
        throw "-Execute requires -ConfirmToken CONVERT-SPO-PAGE."
    }
    if (-not (Get-Command ConvertTo-PnPPage -ErrorAction SilentlyContinue)) {
        throw "PnP.PowerShell with ConvertTo-PnPPage is required. Install/import PnP.PowerShell before executing."
    }

    $connectParameters = @{
        Url         = $SiteUrl
        ClientId    = $ClientId
        Tenant      = $TenantId
        Interactive = $true
    }
    if ($TenantAdminUrl) { $connectParameters["TenantAdminUrl"] = $TenantAdminUrl }
    Connect-PnPOnline @connectParameters

    $escapedName = [System.Security.SecurityElement]::Escape($PageName)
    $viewFieldsList = @("FileRef", "FileLeafRef") + [string[]]$fieldMappingTable.Keys
    $viewFieldsXml = ($viewFieldsList | ForEach-Object { "<FieldRef Name='$_'/>" }) -join ""
    $camlQuery = "<View><ViewFields>$viewFieldsXml</ViewFields><Query><Where><Eq><FieldRef Name='FileLeafRef'/><Value Type='File'>$escapedName</Value></Eq></Where></Query></View>"
    $sourceItems = @(Get-PnPListItem -List $SourceLibrary -Query $camlQuery)
    if ($sourceItems.Count -eq 0) {
        throw "No page named '$PageName' found in '$SourceLibrary'."
    }
    $sourceItem = $sourceItems[0]

    ConvertTo-PnPPage -Identity $sourceItem.FieldValues["FileRef"] -TargetWebUrl $SiteUrl `
        -Overwrite -KeepPageCreationModificationInformation -CopyPageMetadata

    $modernQuery = "<View><ViewFields><FieldRef Name='FileRef'/><FieldRef Name='FileLeafRef'/></ViewFields><Query><Where><Eq><FieldRef Name='FileLeafRef'/><Value Type='File'>$escapedName</Value></Eq></Where></Query></View>"
    $modernItems = @(Get-PnPListItem -List $TargetLibrary -Query $modernQuery)
    if ($modernItems.Count -eq 0) {
        throw "Modern page not found in '$TargetLibrary' after conversion of '$PageName'."
    }
    $modernItem = $modernItems[0]

    $stampValues = [ordered]@{}
    foreach ($sourceFieldName in $fieldMappingTable.Keys) {
        $targetFieldName = $fieldMappingTable[$sourceFieldName]
        $stampValues[$targetFieldName] = $sourceItem.FieldValues[$sourceFieldName]
    }
    foreach ($targetFieldName in $literalFieldValuesTable.Keys) {
        $stampValues[$targetFieldName] = $literalFieldValuesTable[$targetFieldName]
    }
    if ($stampValues.Count -gt 0) {
        Set-PnPListItem -List $TargetLibrary -Identity $modernItem.Id -Values $stampValues | Out-Null
    }

    [pscustomobject]@{
        page_name       = $PageName
        modern_item_id  = $modernItem.Id
        fields_stamped  = @($stampValues.Keys)
        success         = $true
    } | ConvertTo-Json -Depth 8
}
else {
    $plan | ConvertTo-Json -Depth 8
}
