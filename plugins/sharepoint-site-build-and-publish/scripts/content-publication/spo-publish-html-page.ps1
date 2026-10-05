<#
.SYNOPSIS
Publishes an HTML page (.html) to a SharePoint Online document library or Site Pages.

.DESCRIPTION
Uploads a local HTML file (.html / .htm) to a target SharePoint Online document
library or Site Pages library (SitePages/) using PnP.PowerShell (Add-PnPFile) with
checkout/checkin discipline (Set-PnPFileCheckedOut / Set-PnPFileCheckedIn -CheckinType MajorCheckIn)
around any overwrite of an existing file. Verifies presence post-upload and outputs
the clean in-browser URL. Aligns with native SharePoint HTML page rendering (M365
Roadmap ID 569208).
By default performs no tenant I/O (dry-run plan only); -Execute plus
-ConfirmToken PUBLISH-SPO-HTML runs the real upload.

.PARAMETER HtmlPath
Path to local .html or .htm file to publish.

.PARAMETER TargetLibrary
Target document library or "SitePages" (default is "SitePages").

.PARAMETER TargetFolder
Optional folder path inside the target library.

.PARAMETER TargetFileName
Optional filename override. Defaults to the local filename.

.PARAMETER CheckinComment
Comment used when checking in the updated file.

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
Executes the live Add-PnPFile / checkout-checkin calls. Omit this to print the plan only.

.PARAMETER ConfirmToken
Required with -Execute. Must be PUBLISH-SPO-HTML.

.EXAMPLE
.\spo-publish-html-page.ps1 -HtmlPath ".\dashboard.html" -TargetLibrary "SitePages" -Execute -ConfirmToken PUBLISH-SPO-HTML
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$HtmlPath,

    [string]$TargetLibrary = "SitePages",

    [string]$TargetFolder = "",

    [string]$TargetFileName,

    [string]$CheckinComment = "Published via sharepoint-publish-html-page",

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

$connectionConfig = Get-WorkbenchConnectionConfig -Path $ConfigPath
if (-not $SiteUrl) { $SiteUrl = $connectionConfig.SiteUrl }
if (-not $ClientId) { $ClientId = $connectionConfig.ClientId }
if (-not $TenantId) { $TenantId = $connectionConfig.TenantId }
if (-not $TenantAdminUrl) { $TenantAdminUrl = $connectionConfig.TenantAdminUrl }

if (-not $SiteUrl -or -not $ClientId -or -not $TenantId) {
    throw "SiteUrl/ClientId/TenantId not resolved. Provide -SiteUrl/-ClientId/-TenantId or a valid -ConfigPath."
}

if (-not (Test-Path -LiteralPath $HtmlPath)) {
    throw "Local HTML file '$HtmlPath' does not exist."
}

$ext = [System.IO.Path]::GetExtension($HtmlPath).ToLower()
if ($ext -ne ".html" -and $ext -ne ".htm") {
    throw "HtmlPath '$HtmlPath' must have a .html or .htm extension (was '$ext')."
}

$sourceLeaf = [System.IO.Path]::GetFileName($HtmlPath)
$finalFileName = if ($TargetFileName) { $TargetFileName } else { $sourceLeaf }

$folderUrl = if ($TargetFolder) {
    "$($TargetLibrary.Trim('/'))/$($TargetFolder.Trim('/'))"
} else {
    $TargetLibrary.Trim('/')
}

$targetServerRelativeUrl = "$folderUrl/$finalFileName"

if (-not $Execute) {
    Write-Host "`n[DRY RUN] Planned HTML publication action:" -ForegroundColor Yellow
    Write-Host "  Source File       : $HtmlPath"
    Write-Host "  Target Site       : $SiteUrl"
    Write-Host "  Target Library    : $TargetLibrary"
    Write-Host "  Target Folder     : $(if ($TargetFolder) { $TargetFolder } else { '<root>' })"
    Write-Host "  Target Filename   : $finalFileName"
    Write-Host "  Target Server URL : $targetServerRelativeUrl"
    Write-Host "`nTo execute live publication, re-run with: -Execute -ConfirmToken PUBLISH-SPO-HTML" -ForegroundColor Cyan
    return [PSCustomObject]@{
        DryRun                  = $true
        HtmlPath                = $HtmlPath
        SiteUrl                 = $SiteUrl
        TargetLibrary           = $TargetLibrary
        TargetFolder            = $TargetFolder
        TargetServerRelativeUrl = $targetServerRelativeUrl
        Status                  = "PLANNED"
    }
}

if ($ConfirmToken -ne "PUBLISH-SPO-HTML") {
    throw "-Execute requires -ConfirmToken PUBLISH-SPO-HTML."
}

if (-not (Get-Command Add-PnPFile -ErrorAction SilentlyContinue)) {
    throw "PnP.PowerShell with Add-PnPFile is required. Install/import PnP.PowerShell before executing."
}

$connectParameters = @{
    Url         = $SiteUrl
    ClientId    = $ClientId
    Tenant      = $TenantId
    Interactive = $true
}
if ($TenantAdminUrl) { $connectParameters["TenantAdminUrl"] = $TenantAdminUrl }

Write-Host "Connecting to $SiteUrl..." -ForegroundColor Cyan
Connect-PnPOnline @connectParameters

try {
    # Check if target file already exists
    $existingFile = Get-PnPFile -Url $targetServerRelativeUrl -ErrorAction SilentlyContinue
    if ($existingFile) {
        Write-Host "Target file already exists. Checking out '$targetServerRelativeUrl'..." -ForegroundColor Yellow
        try {
            Set-PnPFileCheckedOut -Url $targetServerRelativeUrl -ErrorAction SilentlyContinue
        } catch {
            Write-Host "Checkout note: $($_.Exception.Message)" -ForegroundColor Gray
        }
    }

    Write-Host "Uploading '$HtmlPath' -> '$targetServerRelativeUrl'..." -ForegroundColor Cyan
    $uploaded = Add-PnPFile -Path $HtmlPath -Folder $folderUrl -NewFileName $finalFileName -ErrorAction Stop

    if ($existingFile) {
        Write-Host "Checking in '$targetServerRelativeUrl'..." -ForegroundColor Cyan
        try {
            Set-PnPFileCheckedIn -Url $targetServerRelativeUrl -CheckinType MajorCheckIn -Comment $CheckinComment -ErrorAction SilentlyContinue
        } catch {
            Write-Host "Checkin note: $($_.Exception.Message)" -ForegroundColor Gray
        }
    }

    # Verify presence
    $verified = Get-PnPFile -Url $targetServerRelativeUrl -ErrorAction Stop
    $viewUrl = "$($SiteUrl.TrimEnd('/'))/$($targetServerRelativeUrl.TrimStart('/'))"

    Write-Host "HTML page published successfully!" -ForegroundColor Green
    Write-Host "Direct Browser URL: $viewUrl" -ForegroundColor Yellow

    return [PSCustomObject]@{
        DryRun                  = $false
        SiteUrl                 = $SiteUrl
        TargetServerRelativeUrl = $targetServerRelativeUrl
        BrowserUrl              = $viewUrl
        Status                  = "PUBLISHED"
    }
}
finally {
    Disconnect-PnPOnline -ErrorAction SilentlyContinue
}
