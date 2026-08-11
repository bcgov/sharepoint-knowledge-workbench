<#
.SYNOPSIS
Builds a tenant-safe SharePoint Online Site Page copy plan.

.DESCRIPTION
Parses a source SPO Site Page URL and target SPO Site Page URL into a JSON
page-to-page promotion plan. By default this script performs no SharePoint
tenant I/O; with -Execute and the confirmation token it runs the reviewed
PnP.PowerShell flow, treating the page as a file in the Site Pages library
rather than a special "page copy" operation (Copy-PnPPage's -SourceSite/
-DestinationSite parameter set does not exist in current PnP.PowerShell and
its cross-site-collection copy also requires SharePoint Administrator/admin-
center access that Copy-PnPFile does not):
  1. If the final target path already exists: fail unless -Overwrite; with
     -Overwrite, recycle the existing target file first.
  2. Copy-PnPFile -SourceUrl <source server-relative file path> -TargetUrl
     <target site's SitePages FOLDER, no filename -- Copy-PnPFile requires a
     folder path for cross-site-collection copies, confirmed via
     `Get-Help Copy-PnPFile -Full`> -Overwrite:<whether -Overwrite was passed>.
  3. Rename-PnPFile -ServerRelativeUrl <copied file, still under the source
     page name> -TargetFileName <target page name> when the target page name
     differs from the source -- confirmed via `Get-Help Rename-PnPFile -Full`
     that -ServerRelativeUrl (not -SiteRelativeUrl) and -OverwriteIfAlreadyExists
     (not -Force) are the real parameter names for this cmdlet.

.PARAMETER SourcePageUrl
Full source SPO Site Page URL under /SitePages/.

.PARAMETER TargetPageUrl
Full destination SPO Site Page URL under /SitePages/.

.PARAMETER Overwrite
Marks the generated plan as allowing overwrite at the target.

.PARAMETER ConfigPath
Path to config.psd1 containing ClientId/TenantId. Defaults to the repository
root config.psd1.

.PARAMETER ClientId
Overrides ConfigPath ClientId.

.PARAMETER TenantId
Overrides ConfigPath TenantId.

.PARAMETER TenantAdminUrl
Overrides ConfigPath Authentication.TenantAdminUrl. Not required by the
Copy-PnPFile/Rename-PnPFile flow this script now uses (kept as an optional
override only in case a future PnP cmdlet in this flow needs it).

.PARAMETER Execute
Runs the PnP.PowerShell copy/rename commands. Omit this to print the plan only.

.PARAMETER ConfirmToken
Required with -Execute. Must be COPY-SPO-PAGE.

.EXAMPLE
.\spo-page-copy-plan.ps1 -SourcePageUrl "https://tenant.sharepoint.com/sites/Test/SitePages/Page.aspx" -TargetPageUrl "https://tenant.sharepoint.com/sites/Prod/SitePages/Page-copy.aspx"
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$SourcePageUrl,

    [Parameter(Mandatory = $true)]
    [string]$TargetPageUrl,

    [switch]$Overwrite,

    [string]$ConfigPath = (Join-Path $PSScriptRoot "..\..\..\config.psd1"),

    [string]$ClientId,

    [string]$TenantId,

    [string]$TenantAdminUrl,

    [switch]$Execute,

    [string]$ConfirmToken,

    # Diagnostic-only: runs the copy step but skips Rename-PnPFile, to verify the copy
    # step's behavior in isolation. Not part of the normal flow -- remove once diagnosed.
    [switch]$SkipRename
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Resolve-SpoSitePageUrl {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$PageUrl,

        [Parameter(Mandatory = $true)]
        [string]$ParameterName
    )

    if ([string]::IsNullOrWhiteSpace($PageUrl)) {
        throw "$ParameterName is required."
    }

    $uri = [System.Uri]::new($PageUrl)
    if (-not $uri.IsAbsoluteUri) {
        throw "$ParameterName must be an absolute SharePoint page URL."
    }

    $pathParts = $uri.AbsolutePath.Split("/", [System.StringSplitOptions]::RemoveEmptyEntries) |
        ForEach-Object { [System.Uri]::UnescapeDataString($_) }
    $sitePagesIndex = [array]::FindIndex([string[]]$pathParts, [Predicate[string]]{ param($part) $part -ieq "SitePages" })

    if ($sitePagesIndex -lt 0 -or $sitePagesIndex -eq ($pathParts.Count - 1)) {
        throw "$ParameterName must point to a page under SitePages."
    }

    $pageName = $pathParts[-1]
    if (-not $pageName.EndsWith(".aspx", [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "$ParameterName must end with .aspx."
    }

    $sitePath = "/" + (($pathParts[0..($sitePagesIndex - 1)]) -join "/")
    [pscustomobject]@{
        SiteUrl = "$($uri.Scheme)://$($uri.Host)$sitePath"
        Library = "Site Pages"
        PageName = $pageName
        SiteRelativePageUrl = "SitePages/$pageName"
        ServerRelativeSitePath = $sitePath
        ServerRelativeFileUrl = "$sitePath/SitePages/$pageName"
    }
}

function Get-WorkbenchConnectionConfig {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    if (-not (Test-Path -LiteralPath $Path)) {
        return [pscustomobject]@{
            ClientId       = $null
            TenantId       = $null
            TenantAdminUrl = $null
        }
    }

    $rawConfig = Import-PowerShellDataFile -LiteralPath $Path
    $tenantAdminUrl = if ($rawConfig.Authentication) { $rawConfig.Authentication.TenantAdminUrl } else { $rawConfig.TenantAdminUrl }

    if ($rawConfig.Connection) {
        return [pscustomobject]@{
            ClientId       = $rawConfig.Connection.ClientId
            TenantId       = $rawConfig.Connection.TenantId
            TenantAdminUrl = $tenantAdminUrl
        }
    }

    [pscustomobject]@{
        ClientId       = $rawConfig.ClientId
        TenantId       = $rawConfig.TenantId
        TenantAdminUrl = $tenantAdminUrl
    }
}

function Format-ConnectPnPOnlineCommand {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)][string]$SiteUrl,
        [Parameter(Mandatory = $true)][string]$ClientId,
        [Parameter(Mandatory = $true)][string]$TenantId,
        [string]$TenantAdminUrl
    )

    $command = "Connect-PnPOnline -Url `"$SiteUrl`" -ClientId `"$ClientId`" -Tenant `"$TenantId`" -Interactive"
    if ($TenantAdminUrl) {
        $command += " -TenantAdminUrl `"$TenantAdminUrl`""
    }
    $command
}

$source = Resolve-SpoSitePageUrl -PageUrl $SourcePageUrl -ParameterName "SourcePageUrl"
$target = Resolve-SpoSitePageUrl -PageUrl $TargetPageUrl -ParameterName "TargetPageUrl"
$connectionConfig = Get-WorkbenchConnectionConfig -Path $ConfigPath
if (-not $ClientId) { $ClientId = $connectionConfig.ClientId }
if (-not $TenantId) { $TenantId = $connectionConfig.TenantId }
if (-not $TenantAdminUrl) { $TenantAdminUrl = $connectionConfig.TenantAdminUrl }

# Copy-PnPFile's -TargetUrl must be a FOLDER (no filename) for a cross-site-
# collection copy -- confirmed via `Get-Help Copy-PnPFile -Full`: "Notice that
# if copying between sites or to a subsite you cannot specify a target
# filename, only a folder name." The copy lands under the SOURCE page name; a
# separate Rename-PnPFile step (below) renames it to the target page name.
$targetSitePagesFolderUrl = "$($target.ServerRelativeSitePath)/SitePages"
$copiedFileServerRelativeUrl = "$targetSitePagesFolderUrl/$($source.PageName)"

$plan = [ordered]@{
    operation = "copy-spo-page"
    scope = "page-to-page"
    source = [ordered]@{
        site_url = $source.SiteUrl
        library = $source.Library
        page_name = $source.PageName
    }
    target = [ordered]@{
        site_url = $target.SiteUrl
        library = $target.Library
        page_name = $target.PageName
        site_relative_page_url_after_copy = $source.SiteRelativePageUrl
        site_relative_page_url_after_rename = $target.SiteRelativePageUrl
        overwrite = [bool]$Overwrite
    }
    page = [ordered]@{
        name = $source.PageName
        source_name = $source.PageName
        target_name = $target.PageName
        library = $source.Library
    }
    safety = [ordered]@{
        tenant_io = $(if ($Execute) { "pnp-write" } else { "none" })
        raw_aspx_upload = "avoid"
        execute_requires_confirm_token = "COPY-SPO-PAGE"
    }
    pnp_commands = [ordered]@{
        connect_target_for_precheck = Format-ConnectPnPOnlineCommand -SiteUrl $target.SiteUrl -ClientId $ClientId -TenantId $TenantId -TenantAdminUrl $TenantAdminUrl
        remove_existing_target_if_overwrite = "Remove-PnPFile -ServerRelativeUrl `"$($target.ServerRelativeFileUrl)`" -Recycle -Force   # only if the target already exists and -Overwrite was supplied"
        connect_source_for_copy = Format-ConnectPnPOnlineCommand -SiteUrl $source.SiteUrl -ClientId $ClientId -TenantId $TenantId -TenantAdminUrl $TenantAdminUrl
        copy_file = "Copy-PnPFile -SourceUrl `"$($source.ServerRelativeFileUrl)`" -TargetUrl `"$targetSitePagesFolderUrl`" -Force$(if ($Overwrite) { ' -Overwrite' })"
        connect_target_for_rename = $(if ($source.PageName -ne $target.PageName) { Format-ConnectPnPOnlineCommand -SiteUrl $target.SiteUrl -ClientId $ClientId -TenantId $TenantId -TenantAdminUrl $TenantAdminUrl } else { $null })
        rename_target_page = $(if ($source.PageName -ne $target.PageName) {
            "Rename-PnPFile -ServerRelativeUrl `"$copiedFileServerRelativeUrl`" -TargetFileName `"$($target.PageName)`" -Force$(if ($Overwrite) { ' -OverwriteIfAlreadyExists' })"
        } else { $null })
    }
    recommended_execution = "Treat the page as a Site Pages library file, not a special page-copy operation: pre-check/clear the final target path, Copy-PnPFile from the source server-relative path to the target site's SitePages FOLDER (no filename -- cross-site Copy-PnPFile requires a folder target; it lands under the source page name), then Rename-PnPFile (-ServerRelativeUrl, -OverwriteIfAlreadyExists) to the target page name if it differs. Do not use Copy-PnPPage (its -SourceSite/-DestinationSite parameter set does not exist in current PnP.PowerShell) and do not use raw Add-PnPFile .aspx upload."
}

if ($Execute) {
    if ($ConfirmToken -ne "COPY-SPO-PAGE") {
        throw "-Execute requires -ConfirmToken COPY-SPO-PAGE."
    }
    if (-not (Get-Command Copy-PnPFile -ErrorAction SilentlyContinue)) {
        throw "PnP.PowerShell with Copy-PnPFile is required. Install/import PnP.PowerShell before executing."
    }
    if (-not $ClientId -or -not $TenantId) {
        throw "ClientId/TenantId not resolved. Provide -ClientId/-TenantId or a valid -ConfigPath."
    }

    $connectParameters = @{
        Url         = $target.SiteUrl
        ClientId    = $ClientId
        Tenant      = $TenantId
        Interactive = $true
    }
    if ($TenantAdminUrl) { $connectParameters["TenantAdminUrl"] = $TenantAdminUrl }

    # 1. Pre-check the final target path on the target site.
    Connect-PnPOnline @connectParameters
    $existingTargetFile = Get-PnPFile -Url $target.ServerRelativeFileUrl -ErrorAction SilentlyContinue
    if ($existingTargetFile) {
        if (-not $Overwrite) {
            throw "Target page already exists at $($target.ServerRelativeFileUrl). Re-run with -Overwrite to replace it."
        }
        Remove-PnPFile -ServerRelativeUrl $target.ServerRelativeFileUrl -Recycle -Force
    }

    # 2. Copy the file from the source site to the target site's SitePages FOLDER
    #    (Copy-PnPFile requires a folder -- not a filename -- as -TargetUrl for a
    #    cross-site-collection copy; it lands under the source page name).
    $connectParameters["Url"] = $source.SiteUrl
    Connect-PnPOnline @connectParameters
    $copyParameters = @{
        SourceUrl = $source.ServerRelativeFileUrl
        TargetUrl = $targetSitePagesFolderUrl
        Force     = $true   # suppresses the interactive confirm prompt only -- does not overwrite (that's -Overwrite, set below)
    }
    if ($Overwrite) { $copyParameters["Overwrite"] = $true }
    Copy-PnPFile @copyParameters

    # 3. Rename to the target page name if it differs from the source page name.
    if ($SkipRename) {
        Write-Host "SkipRename set -- leaving copied file at $copiedFileServerRelativeUrl (not renamed)." -ForegroundColor Yellow
    }
    elseif ($source.PageName -ne $target.PageName) {
        $connectParameters["Url"] = $target.SiteUrl
        Connect-PnPOnline @connectParameters
        $renameParameters = @{
            ServerRelativeUrl = $copiedFileServerRelativeUrl
            TargetFileName = $target.PageName
            Force = $true   # suppresses the interactive confirm prompt only -- does not overwrite (that's -OverwriteIfAlreadyExists, set below)
        }
        if ($Overwrite) { $renameParameters["OverwriteIfAlreadyExists"] = $true }
        Rename-PnPFile @renameParameters
    }
}

$plan | ConvertTo-Json -Depth 8
