<#
.SYNOPSIS
Creates a SharePoint document-library folder path (nested, parent first)
after verifying the library exists. Dry-run by default.

.DESCRIPTION
Verifies the target library with Get-PnPList, then creates each missing
folder segment one parent at a time with Resolve-PnPFolder and confirms each
with Get-PnPFolder. A folder is treated as missing only after Get-PnPFolder
reports not found; any other error (permissions, throttling) stops the run.
Without -Execute no tenant I/O occurs and a JSON plan is printed.

Key Input Dependencies:
  - config.psd1 (Connection.SiteUrl/ClientId/TenantId) or -SiteUrl/-ClientId/-TenantId
  - Get-WorkbenchConnectionConfig.ps1 (same folder)
  - PnP.PowerShell (only with -Execute)

Function Index:
  Test-FolderPath, Get-FolderSegments

.PARAMETER LibraryName
Document library title or URL name that must already exist.

.PARAMETER FolderPath
Folder path inside the library, "/" separated (for example "administrative documents/awards").

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
Performs the real library check and folder creation.

.PARAMETER ConfirmToken
Required with -Execute. Must be CREATE-SPO-FOLDER.

.EXAMPLE
.\spo-create-folder.ps1 -LibraryName sheriff -FolderPath "administrative documents/awards"
.\spo-create-folder.ps1 -LibraryName sheriff -FolderPath "administrative documents/awards" -Execute -ConfirmToken CREATE-SPO-FOLDER
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$LibraryName,

    [Parameter(Mandatory = $true)]
    [string]$FolderPath,

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

# Split a folder path into trimmed segments, rejecting empty, traversal and illegal-character segments.
function Get-FolderSegments {
    param([string]$Path)
    $segments = @($Path -split "[/\\]" | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne "" })
    if ($segments.Count -eq 0) { throw "Invalid folder path '$Path': no segments." }
    foreach ($segment in $segments) {
        if ($segment -eq "." -or $segment -eq ".." -or $segment -match '[\x00-\x1f"*:<>?|#%]') {
            throw "Invalid folder path '$Path': segment '$segment' is not allowed."
        }
    }
    return $segments
}

$segments = Get-FolderSegments -Path $FolderPath
if ([string]::IsNullOrWhiteSpace($LibraryName)) { throw "LibraryName is required." }

. (Join-Path $PSScriptRoot "Get-WorkbenchConnectionConfig.ps1")
$connectionConfig = Get-WorkbenchConnectionConfig -Path $ConfigPath
if (-not $SiteUrl) { $SiteUrl = $connectionConfig.SiteUrl }
if (-not $ClientId) { $ClientId = $connectionConfig.ClientId }
if (-not $TenantId) { $TenantId = $connectionConfig.TenantId }
if (-not $TenantAdminUrl) { $TenantAdminUrl = $connectionConfig.TenantAdminUrl }

if (-not $SiteUrl -or -not $ClientId -or -not $TenantId) {
    throw "SiteUrl/ClientId/TenantId not resolved. Provide -SiteUrl/-ClientId/-TenantId or a valid -ConfigPath."
}

$folderPlan = @()
$current = $LibraryName
foreach ($segment in $segments) {
    $current = "$current/$segment"
    $folderPlan += [ordered]@{ folder = $current }
}

if (-not $Execute) {
    [ordered]@{
        dry_run        = $true
        site_url       = $SiteUrl
        library        = $LibraryName
        verify_library = "Get-PnPList -Identity `"$LibraryName`""
        folders        = $folderPlan
        note           = "No SharePoint calls made. Rerun with -Execute -ConfirmToken CREATE-SPO-FOLDER to create."
    } | ConvertTo-Json -Depth 5
    return
}

if ($ConfirmToken -ne "CREATE-SPO-FOLDER") {
    throw "-Execute requires -ConfirmToken CREATE-SPO-FOLDER."
}
$missingCommands = @(@("Get-PnPList", "Resolve-PnPFolder", "Get-PnPFolder") | Where-Object {
    -not (Get-Command $_ -ErrorAction SilentlyContinue)
})
if ($missingCommands.Count -gt 0) {
    throw "PnP.PowerShell commands are required before execution: $($missingCommands -join ', ')."
}

$connectParameters = @{ Url = $SiteUrl; ClientId = $ClientId; Tenant = $TenantId; Interactive = $true }
if ($TenantAdminUrl) { $connectParameters["TenantAdminUrl"] = $TenantAdminUrl }
Connect-PnPOnline @connectParameters

try {
    $library = Get-PnPList -Identity $LibraryName -ErrorAction Stop
}
catch {
    throw "Unable to verify library '$LibraryName'; no folder was created. If missing, create it with the SharePoint document-library skill. Details: $($_.Exception.Message)"
}
if (-not $library) { throw "Library '$LibraryName' could not be confirmed; no folder was created." }

$results = foreach ($step in $folderPlan) {
    $existed = $true
    try {
        $found = Get-PnPFolder -Url $step.folder -ErrorAction Stop
        if (-not $found) { $existed = $false }
    }
    catch {
        if ($_.Exception.Message -match "not found|does not exist|File Not Found|404") { $existed = $false }
        else { throw "Unable to query folder '$($step.folder)': $($_.Exception.Message)" }
    }
    if (-not $existed) {
        Resolve-PnPFolder -SiteRelativePath $step.folder -ErrorAction Stop | Out-Null
        $confirmed = Get-PnPFolder -Url $step.folder -ErrorAction Stop
        if (-not $confirmed) { throw "Folder '$($step.folder)' could not be confirmed after creation." }
    }
    [ordered]@{ folder = $step.folder; status = $(if ($existed) { "existed" } else { "created" }) }
}

[ordered]@{ dry_run = $false; site_url = $SiteUrl; library = $LibraryName; folders = @($results) } | ConvertTo-Json -Depth 5
