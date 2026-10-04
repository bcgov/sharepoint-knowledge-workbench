<#
.SYNOPSIS
Validates converted modern SharePoint pages against a run manifest: page
existence, mapped-field population, and literal field values.

.DESCRIPTION
Read-only. Reads a run manifest CSV (PageName, Status, ...), re-queries the
target library for each Succeeded (and optionally Skipped) row, and checks:
  - The modern page exists in -TargetLibrary.
  - Every target field named in -FieldMapping's values is non-empty.
  - Every field named in -LiteralFieldValues equals its expected value.
Writes a test-report.csv (PageName, Result, PageFound, MissingFields,
ValidatedAt, Notes) and exits 1 if any row fails, for use in a pipeline.

.PARAMETER ManifestPath
Path to the run manifest CSV. Required.

.PARAMETER TargetLibrary
Library containing the converted modern pages. Defaults to "Site Pages".

.PARAMETER FieldMapping
Path to the same JSON field-mapping file passed to
spo-convert-page-to-modern.ps1 -- only the mapped-to (target) field names are
checked for non-empty population. Optional.

.PARAMETER LiteralFieldValues
Path to the same JSON literal-field-values file passed to
spo-convert-page-to-modern.ps1 -- each field is checked to equal its expected
value exactly. Optional.

.PARAMETER ReportPath
Path to write the test report CSV. Required.

.PARAMETER IncludeSkipped
Also validates manifest rows with Status = Skipped, not just Succeeded.

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

.EXAMPLE
.\spo-validate-page-conversion.ps1 -ManifestPath run-manifest.csv -FieldMapping field-mapping.json -ReportPath test-report.csv
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ManifestPath,

    [string]$TargetLibrary = "Site Pages",

    [string]$FieldMapping,

    [string]$LiteralFieldValues,

    [Parameter(Mandatory = $true)]
    [string]$ReportPath,

    [switch]$IncludeSkipped,

    [string]$SiteUrl,

    [string]$ConfigPath = (Join-Path $PSScriptRoot "..\..\..\config.psd1"),

    [string]$ClientId,

    [string]$TenantId,

    [string]$TenantAdminUrl
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

if (-not (Test-Path -LiteralPath $ManifestPath)) {
    throw "Run manifest not found at '$ManifestPath'."
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
$targetFieldNames = @($fieldMappingTable.Values) + @($literalFieldValuesTable.Keys) | Select-Object -Unique

$manifest = Import-Csv -LiteralPath $ManifestPath
$statusFilter = @("Succeeded")
if ($IncludeSkipped) { $statusFilter += "Skipped" }
$rowsToCheck = $manifest | Where-Object { $statusFilter -contains $_.Status }

if ($rowsToCheck.Count -eq 0) {
    Write-Warning "No manifest rows to validate (looked for status: $($statusFilter -join ', '))."
    "PageName,Result,PageFound,MissingFields,ValidatedAt,Notes" | Out-File -FilePath $ReportPath -Encoding utf8
    exit 0
}

$connectParameters = @{
    Url         = $SiteUrl
    ClientId    = $ClientId
    Tenant      = $TenantId
    Interactive = $true
}
if ($TenantAdminUrl) { $connectParameters["TenantAdminUrl"] = $TenantAdminUrl }
Connect-PnPOnline @connectParameters

"PageName,Result,PageFound,MissingFields,ValidatedAt,Notes" | Out-File -FilePath $ReportPath -Encoding utf8

$passCount = 0
$failCount = 0

foreach ($row in $rowsToCheck) {
    $pageName = $row.PageName
    $validatedAt = (Get-Date).ToString("o")
    $pageFound = $false
    $missingFields = @()
    $notes = @()

    $escapedName = [System.Security.SecurityElement]::Escape($pageName)
    $viewFieldsList = @("FileLeafRef") + [string[]]$targetFieldNames
    $viewFieldsXml = ($viewFieldsList | ForEach-Object { "<FieldRef Name='$_'/>" }) -join ""
    $camlQuery = "<View><ViewFields>$viewFieldsXml</ViewFields><Query><Where><Eq><FieldRef Name='FileLeafRef'/><Value Type='File'>$escapedName</Value></Eq></Where></Query></View>"
    $modernItems = @(Get-PnPListItem -List $TargetLibrary -Query $camlQuery -ErrorAction SilentlyContinue)
    $modernItem = if ($modernItems.Count -gt 0) { $modernItems[0] } else { $null }

    if (-not $modernItem) {
        $notes += "Page not found in target library '$TargetLibrary'"
    } else {
        $pageFound = $true
        foreach ($targetFieldName in $fieldMappingTable.Values) {
            if ([string]::IsNullOrWhiteSpace($modernItem.FieldValues[$targetFieldName])) {
                $missingFields += $targetFieldName
                $notes += "$targetFieldName is empty"
            }
        }
        foreach ($targetFieldName in $literalFieldValuesTable.Keys) {
            $expected = $literalFieldValuesTable[$targetFieldName]
            $actual = $modernItem.FieldValues[$targetFieldName]
            if ($actual -ne $expected) {
                $missingFields += $targetFieldName
                $notes += "$targetFieldName expected '$expected', got '$actual'"
            }
        }
    }

    $result = if ($pageFound -and $missingFields.Count -eq 0) { "Pass" } else { "Fail" }
    if ($result -eq "Pass") { $passCount++ } else { $failCount++ }

    $missingText = ($missingFields -join "|") -replace '"', "'"
    $notesText = ($notes -join "; ") -replace '"', "'" -replace "`r`n|`n", " "
    "$pageName,$result,$pageFound,`"$missingText`",$validatedAt,`"$notesText`"" | Out-File -FilePath $ReportPath -Append -Encoding utf8
}

Disconnect-PnPOnline -ErrorAction SilentlyContinue

Write-Host "Pass: $passCount  Fail: $failCount  Report: $ReportPath"
if ($failCount -gt 0) { exit 1 }
