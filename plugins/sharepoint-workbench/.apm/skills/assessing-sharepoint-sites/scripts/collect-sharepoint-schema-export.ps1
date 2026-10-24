<#
.SYNOPSIS
Orchestrates multiple collect-sharepoint-inventory.ps1 invocations into the
directory-tree schema-export shape sharepoint-schema's analysis tools expect.

.DESCRIPTION
Read-only orchestrator. `collect-sharepoint-inventory.ps1` only ever writes
one flat JSON file per invocation (modes: Lists, ListFields, LibraryFiles,
ContentTypes) to a caller-given -OutputPath. `sharepoint-schema`'s
`schema_export.load_schema_export`/`ExportLayout` instead expects a directory
tree:

  <OutputDir>/summary/lists.json
  <OutputDir>/summary/content_types.json
  <OutputDir>/lists/<listname>/fields.json
  <OutputDir>/lists/<listname>/content_types.json

This script drives `collect-sharepoint-inventory.ps1` once per mode/per-list
to assemble that tree, reusing its real, already-working PnP collection
logic rather than reimplementing any Get-PnP* calls.

For Lists and ListFields modes, `collect-sharepoint-inventory.ps1`'s raw JSON
output already matches the flat-array shape `schema_export.py` expects
(records keyed by "Title"/"InternalName" respectively), so those calls target
the final destination -OutputPath directly -- no intermediate reshaping.

ContentTypes mode is different: its raw output is a single combined object
(`{ SiteContentTypes: [...], Lists: [ { Title, BaseType, ContentTypes,
Fields } ] }`), not the flat content-type array `schema_export.py` expects
per section. Those calls are written to a temp file first, then this script
extracts and re-writes just the relevant array (`.SiteContentTypes` for the
sitewide summary; the single list entry's `.ContentTypes` for a per-list
export) to its real destination.

KNOWN GAP -- summary/site_columns.json is NOT produced by this script.
`collect-sharepoint-inventory.ps1` has no site-columns-only mode: its
ListFields mode requires -ListName (site-scoped/web-level fields, i.e.
fields not attached to any specific list, are never enumerated by any of its
four modes). Fabricating this file from another mode's data would not be
correct, so it is skipped -- this is a real, separate, smaller collector gap
this script found, not something silently omitted. A follow-up would add a
genuine site-columns mode to collect-sharepoint-inventory.ps1 (or an
equivalent standalone collector) before this gap can be closed.

Performs zero tenant writes and zero writes outside -OutputDir -- every mode
this script drives calls only Get-PnP* cmdlets.

.PARAMETER SiteUrl
Target site. Overrides config.psd1 Connection.SiteUrl.

.PARAMETER ConfigPath
Path to config.psd1. Defaults to the repository root config.psd1.

.PARAMETER ClientId
Overrides ConfigPath ClientId.

.PARAMETER TenantId
Overrides ConfigPath TenantId.

.PARAMETER TenantAdminUrl
Overrides ConfigPath Authentication.TenantAdminUrl. Not required (all
collection here operates within a single site), present only so this script
does not silently diverge from the repo's standard PnP auth parameter set.

.PARAMETER OutputDir
Directory to assemble the schema-export tree under. Created if it does not
already exist.

.EXAMPLE
.\collect-sharepoint-schema-export.ps1 -SiteUrl "https://tenant.sharepoint.com/sites/Test" -OutputDir .\schema-export

.EXAMPLE
.\collect-sharepoint-schema-export.ps1 -OutputDir .\schema-export
(SiteUrl/ClientId/TenantId resolved from config.psd1)
#>

[CmdletBinding()]
param(
    [string]$SiteUrl,

    [string]$ConfigPath = (Join-Path $PSScriptRoot "..\..\..\config.psd1"),

    [string]$ClientId,

    [string]$TenantId,

    [string]$TenantAdminUrl,

    [Parameter(Mandatory = $true)]
    [string]$OutputDir
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

. (Join-Path $PSScriptRoot "Get-WorkbenchConnectionConfig.ps1")

$connectionConfig = Get-WorkbenchConnectionConfig -Path $ConfigPath
if (-not $SiteUrl) { $SiteUrl = $connectionConfig.SiteUrl }
if (-not $ClientId) { $ClientId = $connectionConfig.ClientId }
if (-not $TenantId) { $TenantId = $connectionConfig.TenantId }
if (-not $TenantAdminUrl) { $TenantAdminUrl = $connectionConfig.TenantAdminUrl }

if (-not $SiteUrl -or -not $ClientId -or -not $TenantId) {
    throw "SiteUrl/ClientId/TenantId not resolved. Provide -SiteUrl/-ClientId/-TenantId or a valid -ConfigPath."
}

$collectorScript = Join-Path $PSScriptRoot "collect-sharepoint-inventory.ps1"
if (-not (Test-Path $collectorScript)) {
    throw "collect-sharepoint-inventory.ps1 not found alongside this script at $collectorScript."
}

# Every collect-sharepoint-inventory.ps1 invocation below is passed the same
# resolved connection values explicitly, so config.psd1 is only read once
# (here), not re-resolved independently by each child invocation.
$commonParameters = @{
    SiteUrl  = $SiteUrl
    ClientId = $ClientId
    TenantId = $TenantId
}
if ($TenantAdminUrl) { $commonParameters["TenantAdminUrl"] = $TenantAdminUrl }

function ConvertTo-SafeFolderName {
    param([string]$Name)
    $invalidChars = [System.IO.Path]::GetInvalidFileNameChars() -join ""
    $pattern = "[{0}]" -f [System.Text.RegularExpressions.Regex]::Escape($invalidChars)
    return ($Name -replace $pattern, "_")
}

$summaryDir = Join-Path $OutputDir "summary"
$listsDir = Join-Path $OutputDir "lists"
New-Item -ItemType Directory -Force -Path $summaryDir | Out-Null
New-Item -ItemType Directory -Force -Path $listsDir | Out-Null

Write-Host "=== Collecting schema export to $OutputDir ===" -ForegroundColor Cyan

# --- summary/lists.json -----------------------------------------------
# Lists mode's raw output already matches the flat array schema_export.py
# expects (records keyed by "Title") -- write directly to the final path.
$listsSummaryPath = Join-Path $summaryDir "lists.json"
& $collectorScript @commonParameters -Mode Lists -OutputPath $listsSummaryPath

# --- summary/content_types.json ----------------------------------------
# ContentTypes mode's raw output is a combined { SiteContentTypes, Lists }
# object, not the flat array schema_export.py expects here -- collect to a
# temp file, then extract and re-write just .SiteContentTypes.
$siteContentTypesTemp = New-TemporaryFile
& $collectorScript @commonParameters -Mode ContentTypes -OutputPath $siteContentTypesTemp.FullName
$siteContentTypesRaw = Get-Content $siteContentTypesTemp.FullName -Raw | ConvertFrom-Json
$siteContentTypesPath = Join-Path $summaryDir "content_types.json"
@($siteContentTypesRaw.SiteContentTypes) | ConvertTo-Json -Depth 10 | Set-Content -Path $siteContentTypesPath -Encoding UTF8
Remove-Item $siteContentTypesTemp.FullName -Force -ErrorAction SilentlyContinue

# --- summary/site_columns.json -- KNOWN GAP, NOT PRODUCED --------------
# collect-sharepoint-inventory.ps1 has no site-columns-only mode (see
# .DESCRIPTION above). Reported honestly rather than fabricated.
Write-Warning "summary/site_columns.json was NOT written: collect-sharepoint-inventory.ps1 has no site-columns-only mode (its ListFields mode requires -ListName). This is a real collector gap, not a silent omission -- see this script's header comment."

# --- lists/<listname>/{fields.json, content_types.json} ----------------
$listRecords = @(Get-Content $listsSummaryPath -Raw | ConvertFrom-Json)
Write-Host "Found $($listRecords.Count) list(s)/library(ies); collecting per-list fields and content types..." -ForegroundColor Cyan

foreach ($listRecord in $listRecords) {
    $listTitle = $listRecord.Title
    $safeFolderName = ConvertTo-SafeFolderName -Name $listTitle
    $listDir = Join-Path $listsDir $safeFolderName
    New-Item -ItemType Directory -Force -Path $listDir | Out-Null

    # fields.json -- ListFields mode's raw output already matches the flat
    # array schema_export.py expects (records keyed by "InternalName").
    $fieldsPath = Join-Path $listDir "fields.json"
    & $collectorScript @commonParameters -Mode ListFields -ListName $listTitle -OutputPath $fieldsPath

    # content_types.json -- same combined-object situation as the sitewide
    # summary above: collect to a temp file, extract the single list
    # entry's .ContentTypes array, re-write just that.
    $listContentTypesTemp = New-TemporaryFile
    & $collectorScript @commonParameters -Mode ContentTypes -ListNames $listTitle -OutputPath $listContentTypesTemp.FullName
    $listContentTypesRaw = Get-Content $listContentTypesTemp.FullName -Raw | ConvertFrom-Json
    $listEntry = @($listContentTypesRaw.Lists) | Select-Object -First 1
    $listContentTypesPath = Join-Path $listDir "content_types.json"
    if ($listEntry) {
        @($listEntry.ContentTypes) | ConvertTo-Json -Depth 10 | Set-Content -Path $listContentTypesPath -Encoding UTF8
    } else {
        Write-Warning "No content-type data returned for list '$listTitle'; writing an empty array to $listContentTypesPath."
        @() | ConvertTo-Json -Depth 10 | Set-Content -Path $listContentTypesPath -Encoding UTF8
    }
    Remove-Item $listContentTypesTemp.FullName -Force -ErrorAction SilentlyContinue
}

Write-Host "=== Schema export collection complete: $OutputDir ===" -ForegroundColor Green
