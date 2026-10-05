<#
.SYNOPSIS
Downloads a document, file, or page from SharePoint Online or SharePoint 2016 to local disk.

.DESCRIPTION
Downloads a remote file, document, or page from SharePoint Online (using PnP.PowerShell
Get-PnPFile -AsFile) or SharePoint 2016 on-prem (using Invoke-WebRequest with Windows
Integrated authentication). Verifies local file existence and reports byte size.
Supports both standard document library assets (.html, .docx, .pdf, images) and Site Pages.
By default performs no tenant I/O (dry-run plan only); -Execute plus
-ConfirmToken DOWNLOAD-SPO-FILE executes the live download.

.PARAMETER RemoteUrl
Remote file URL or server-relative URL.
Examples:
  SPO:    "/sites/MySite/Shared Documents/report.html" or "https://tenant.sharepoint.com/sites/Site/Shared Documents/file.pdf"
  SP2016: "https://csb.jag.gov.bc.ca/Criminal Documents/justinews/apr-7-22.aspx"

.PARAMETER ServerRelativeUrl
Alias for RemoteUrl for backward compatibility.

.PARAMETER DestinationDir
Local directory where the downloaded file will be saved. Defaults to current directory.

.PARAMETER FileName
Optional local filename override. If omitted, uses the filename from the remote URL.

.PARAMETER FromSource
Explicit switch to indicate the source is the SP2016 environment defined in config.psd1 Source.

.PARAMETER Overwrite
Switch to overwrite existing local file. Default is false (fails if local file exists).

.PARAMETER SiteUrl
Overrides config.psd1 Connection.SiteUrl (or Source.SiteUrl when -FromSource is used).

.PARAMETER ConfigPath
Path to config.psd1. Defaults to the repository root config.psd1.

.PARAMETER ClientId
Overrides ConfigPath ClientId.

.PARAMETER TenantId
Overrides ConfigPath TenantId.

.PARAMETER TenantAdminUrl
Overrides ConfigPath Authentication.TenantAdminUrl.

.PARAMETER Execute
Executes the live download. Omit this to print the planned action only.

.PARAMETER ConfirmToken
Required with -Execute. Must be DOWNLOAD-SPO-FILE.

.EXAMPLE
.\spo-download-file.ps1 -RemoteUrl "/sites/MySite/Shared Documents/test.html" -DestinationDir ".\temp" -Execute -ConfirmToken DOWNLOAD-SPO-FILE
#>

[CmdletBinding(DefaultParameterSetName = "Default")]
param(
    [Parameter(Mandatory = $true, Position = 0, ParameterSetName = "Default")]
    [string]$RemoteUrl,

    [Parameter(ParameterSetName = "Legacy")]
    [string]$ServerRelativeUrl,

    [string]$DestinationDir = ".",

    [string]$FileName,

    [switch]$FromSource,

    [switch]$Overwrite,

    [string]$SiteUrl,

    [System.Management.Automation.PSCredential]$Credential,

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

$targetUrl = if ($RemoteUrl) { $RemoteUrl } else { $ServerRelativeUrl }
if (-not $targetUrl) {
    throw "RemoteUrl or ServerRelativeUrl is required."
}

$connectionConfig = Get-WorkbenchConnectionConfig -Path $ConfigPath

# Detect if target is SP2016
$isSp2016 = $false
if ($FromSource) {
    $isSp2016 = $true
} elseif ($targetUrl -like "http*://*") {
    if ($targetUrl -match "csb\.jag\.gov\.bc\.ca" -or ($targetUrl -match "\.gov\.bc\.ca/" -and $targetUrl -notmatch "sharepoint\.com")) {
        $isSp2016 = $true
    }
}

if ($isSp2016) {
    $sourceSite = if ($SiteUrl) { $SiteUrl } else {
        if (Test-Path $ConfigPath) {
            $rawPsd1 = Import-PowerShellDataFile $ConfigPath
            if ($rawPsd1.ContainsKey('Source') -and $rawPsd1.Source.ContainsKey('SiteUrl')) {
                $rawPsd1.Source.SiteUrl
            } else { "https://csb.jag.gov.bc.ca/" }
        } else { "https://csb.jag.gov.bc.ca/" }
    }
    $platform = "SharePoint2016"
} else {
    if (-not $SiteUrl) { $SiteUrl = $connectionConfig.SiteUrl }
    if (-not $ClientId) { $ClientId = $connectionConfig.ClientId }
    if (-not $TenantId) { $TenantId = $connectionConfig.TenantId }
    if (-not $TenantAdminUrl) { $TenantAdminUrl = $connectionConfig.TenantAdminUrl }

    if (-not $SiteUrl -or -not $ClientId -or -not $TenantId) {
        throw "SiteUrl/ClientId/TenantId not resolved. Provide -SiteUrl/-ClientId/-TenantId or a valid -ConfigPath."
    }
    $platform = "SharePointOnline"
}

# Resolve target file name
$sourceLeaf = [System.IO.Path]::GetFileName($targetUrl)
if ($sourceLeaf -like "*?*") {
    $sourceLeaf = $sourceLeaf.Substring(0, $sourceLeaf.IndexOf('?'))
}
if (-not $sourceLeaf) {
    throw "RemoteUrl '$targetUrl' does not contain a recognizable file name."
}
$targetFileName = if ($FileName) { $FileName } else { $sourceLeaf }

# Resolve destination directory & full path
if (-not (Test-Path -LiteralPath $DestinationDir)) {
    if ($Execute) {
        New-Item -ItemType Directory -Path $DestinationDir -Force | Out-Null
    }
}
$resolvedDestDir = if (Test-Path -LiteralPath $DestinationDir) {
    (Resolve-Path -LiteralPath $DestinationDir).Path
} else {
    $DestinationDir
}
$destinationFilePath = Join-Path $resolvedDestDir $targetFileName

if (Test-Path -LiteralPath $destinationFilePath) {
    if (-not $Overwrite) {
        throw "Local file '$destinationFilePath' already exists. Use -Overwrite to replace it."
    }
}

if (-not $Execute) {
    Write-Host "`n[DRY RUN] Planned download action:" -ForegroundColor Yellow
    Write-Host "  Platform          : $platform"
    Write-Host "  Remote URL        : $targetUrl"
    Write-Host "  Destination Dir   : $resolvedDestDir"
    Write-Host "  Destination File  : $destinationFilePath"
    Write-Host "  Overwrite Allowed : $Overwrite"
    Write-Host "`nTo execute live download, re-run with: -Execute -ConfirmToken DOWNLOAD-SPO-FILE" -ForegroundColor Cyan
    return [PSCustomObject]@{
        DryRun              = $true
        Platform            = $platform
        RemoteUrl           = $targetUrl
        DestinationFilePath = $destinationFilePath
        Status              = "PLANNED"
    }
}

if ($ConfirmToken -ne "DOWNLOAD-SPO-FILE") {
    throw "-Execute requires -ConfirmToken DOWNLOAD-SPO-FILE."
}

if ($isSp2016) {
    Write-Host "Downloading from SharePoint 2016 (Integrated Auth): $targetUrl..." -ForegroundColor Cyan
    $fullUrl = if ($targetUrl -like "http*://*") { $targetUrl } else {
        "$($sourceSite.TrimEnd('/'))/$($targetUrl.TrimStart('/'))"
    }
    $reqArgs = @{
        Uri             = $fullUrl
        UseBasicParsing = $true
        OutFile         = $destinationFilePath
        ErrorAction     = "Stop"
    }
    if ($Credential) {
        $reqArgs["Credential"] = $Credential
    } else {
        $reqArgs["UseDefaultCredentials"] = $true
    }
    Invoke-WebRequest @reqArgs
} else {
    if (-not (Get-Command Get-PnPFile -ErrorAction SilentlyContinue)) {
        throw "PnP.PowerShell with Get-PnPFile is required. Install/import PnP.PowerShell before executing."
    }

    $connectParameters = @{
        Url         = $SiteUrl
        ClientId    = $ClientId
        Tenant      = $TenantId
        Interactive = $true
    }
    if ($TenantAdminUrl) { $connectParameters["TenantAdminUrl"] = $TenantAdminUrl }

    Write-Host "Connecting to SharePoint Online: $SiteUrl..." -ForegroundColor Cyan
    Connect-PnPOnline @connectParameters

    try {
        Write-Host "Downloading '$targetUrl' to '$destinationFilePath'..." -ForegroundColor Cyan
        Get-PnPFile -Url $targetUrl -Path $resolvedDestDir -FileName $targetFileName -AsFile -Force -ErrorAction Stop | Out-Null
    }
    finally {
        Disconnect-PnPOnline -ErrorAction SilentlyContinue
    }
}

if (-not (Test-Path -LiteralPath $destinationFilePath)) {
    throw "Download completed without error, but destination file was not found at '$destinationFilePath'."
}

$fileInfo = Get-Item -LiteralPath $destinationFilePath
Write-Host "Download successful! Size: $($fileInfo.Length) bytes." -ForegroundColor Green

return [PSCustomObject]@{
    DryRun              = $false
    Platform            = $platform
    RemoteUrl           = $targetUrl
    DestinationFilePath = $destinationFilePath
    SizeBytes           = $fileInfo.Length
    Status              = "SUCCESS"
}
