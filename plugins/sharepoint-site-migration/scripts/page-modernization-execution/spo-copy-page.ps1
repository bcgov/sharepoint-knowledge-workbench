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
center access that Copy-PnPFile does not). Two distinct flows depending on
whether source and target resolve to the same site:

SAME-SITE (source.SiteUrl -eq target.SiteUrl), e.g. duplicating a page under
a new name for safe iteration without touching the original:
  1. If the final target path already exists: fail unless -Overwrite; with
     -Overwrite, recycle the existing target file first.
  2. Copy-PnPFile -SourceUrl <source server-relative file path> -TargetUrl
     <target server-relative file path, INCLUDING filename> in one step --
     confirmed via `Get-Help Copy-PnPFile -Full` Example 5: a same-site/
     same-library copy accepts a full destination file path directly. No
     Rename-PnPFile step is needed or run.
     CONFIRMED REAL BUG (2026-09-08): an earlier version of this script
     always used the cross-site two-step flow (copy under source name, then
     rename) even for same-site copies. For a same-site copy this fails
     immediately with "A file or folder with the name '<source page>.aspx'
     already exists at the destination" -- the intermediate "land under the
     source name" step collides with the source file itself, since source
     and target are the same folder. Do not reintroduce the two-step flow
     for the same-site case.

CROSS-SITE (source.SiteUrl -ne target.SiteUrl), e.g. TEST-to-PROD promotion:
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
.\spo-copy-page.ps1 -SourcePageUrl "https://tenant.sharepoint.com/sites/Test/SitePages/Page.aspx" -TargetPageUrl "https://tenant.sharepoint.com/sites/Prod/SitePages/Page-copy.aspx"
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

    $relativeSegments = if ($sitePagesIndex -lt ($pathParts.Count - 1)) {
        $pathParts[($sitePagesIndex + 1)..($pathParts.Count - 1)]
    } else {
        @($pageName)
    }
    $relativePagePath = $relativeSegments -join "/"
    $sitePath = if ($sitePagesIndex -gt 0) {
        "/" + (($pathParts[0..($sitePagesIndex - 1)]) -join "/")
    } else {
        ""
    }
    $serverRelativeFileUrl = if ($sitePath) { "$sitePath/SitePages/$relativePagePath" } else { "/SitePages/$relativePagePath" }
    $relativeFolder = if ($relativeSegments.Count -gt 1) {
        ($relativeSegments[0..($relativeSegments.Count - 2)]) -join "/"
    } else {
        ""
    }

    [pscustomobject]@{
        SiteUrl                = "$($uri.Scheme)://$($uri.Host)$sitePath"
        Library                = "Site Pages"
        PageName               = $pageName
        RelativeFolder         = $relativeFolder
        SiteRelativePageUrl    = "SitePages/$relativePagePath"
        ServerRelativeSitePath = $sitePath
        ServerRelativeFileUrl  = $serverRelativeFileUrl
    }
}

. (Join-Path $PSScriptRoot "Get-WorkbenchConnectionConfig.ps1")

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

if ($source.SiteUrl -ieq $target.SiteUrl -and $source.ServerRelativeFileUrl -ieq $target.ServerRelativeFileUrl) {
    throw "Source and target resolve to the same page: '$($source.ServerRelativeFileUrl)'."
}

$connectionConfig = Get-WorkbenchConnectionConfig -Path $ConfigPath
if (-not $ClientId) { $ClientId = $connectionConfig.ClientId }
if (-not $TenantId) { $TenantId = $connectionConfig.TenantId }
if (-not $TenantAdminUrl) { $TenantAdminUrl = $connectionConfig.TenantAdminUrl }

$isSameSite = $source.SiteUrl -ieq $target.SiteUrl

# Copy-PnPFile's -TargetUrl must be a FOLDER (no filename) for a cross-site-
# collection copy -- confirmed via `Get-Help Copy-PnPFile -Full`: "Notice that
# if copying between sites or to a subsite you cannot specify a target
# filename, only a folder name." The copy lands under the SOURCE page name; a
# separate Rename-PnPFile step (below) renames it to the target page name.
# Same-site copies do not have this restriction (Example 5 in the same help
# topic copies directly to a full target file path) -- and MUST use the
# direct form, since landing under the source name in the SAME folder would
# collide with the source file itself.
$targetSitePagesFolderUrl = if ($target.RelativeFolder) {
    "$($target.ServerRelativeSitePath)/SitePages/$($target.RelativeFolder)"
} else {
    "$($target.ServerRelativeSitePath)/SitePages"
}
$copiedFileServerRelativeUrl = if ($isSameSite) { $target.ServerRelativeFileUrl } else { "$targetSitePagesFolderUrl/$($source.PageName)" }

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
    pnp_commands = if ($isSameSite) {
        [ordered]@{
            connect_for_precheck_and_copy = Format-ConnectPnPOnlineCommand -SiteUrl $target.SiteUrl -ClientId $ClientId -TenantId $TenantId -TenantAdminUrl $TenantAdminUrl
            remove_existing_target_if_overwrite = "Remove-PnPFile -ServerRelativeUrl `"$($target.ServerRelativeFileUrl)`" -Recycle -Force   # only if the target already exists and -Overwrite was supplied"
            copy_file = "Copy-PnPFile -SourceUrl `"$($source.ServerRelativeFileUrl)`" -TargetUrl `"$($target.ServerRelativeFileUrl)`" -Force$(if ($Overwrite) { ' -Overwrite' })"
            rename_target_page = $null
        }
    } else {
        [ordered]@{
            connect_target_for_precheck = Format-ConnectPnPOnlineCommand -SiteUrl $target.SiteUrl -ClientId $ClientId -TenantId $TenantId -TenantAdminUrl $TenantAdminUrl
            remove_existing_target_if_overwrite = "Remove-PnPFile -ServerRelativeUrl `"$($target.ServerRelativeFileUrl)`" -Recycle -Force   # only if the target already exists and -Overwrite was supplied"
            connect_source_for_copy = Format-ConnectPnPOnlineCommand -SiteUrl $source.SiteUrl -ClientId $ClientId -TenantId $TenantId -TenantAdminUrl $TenantAdminUrl
            copy_file = "Copy-PnPFile -SourceUrl `"$($source.ServerRelativeFileUrl)`" -TargetUrl `"$targetSitePagesFolderUrl`" -Force$(if ($Overwrite) { ' -Overwrite' })"
            connect_target_for_rename = $(if ($source.PageName -ne $target.PageName) { Format-ConnectPnPOnlineCommand -SiteUrl $target.SiteUrl -ClientId $ClientId -TenantId $TenantId -TenantAdminUrl $TenantAdminUrl } else { $null })
            rename_target_page = $(if ($source.PageName -ne $target.PageName) {
                "Rename-PnPFile -ServerRelativeUrl `"$copiedFileServerRelativeUrl`" -TargetFileName `"$($target.PageName)`" -Force$(if ($Overwrite) { ' -OverwriteIfAlreadyExists' })"
            } else { $null })
        }
    }
    recommended_execution = if ($isSameSite) {
        "Same-site copy: pre-check/clear the final target path, then Copy-PnPFile directly from the source server-relative path to the target's full server-relative file path (same-site/same-library copies accept a full destination file path -- no folder-only restriction, no rename step). Do not use the cross-site folder+rename flow here -- it collides with the source file since both live in the same folder."
    } else {
        "Cross-site copy: treat the page as a Site Pages library file, not a special page-copy operation: pre-check/clear the final target path, Copy-PnPFile from the source server-relative path to the target site's SitePages FOLDER (no filename -- cross-site Copy-PnPFile requires a folder target; it lands under the source page name), then Rename-PnPFile (-ServerRelativeUrl, -OverwriteIfAlreadyExists) to the target page name if it differs. Do not use Copy-PnPPage (its -SourceSite/-DestinationSite parameter set does not exist in current PnP.PowerShell) and do not use raw Add-PnPFile .aspx upload."
    }
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

    if ($isSameSite) {
        # 2. Same-site: Copy-PnPFile directly to the full target file path.
        #    No folder-only restriction, no rename step -- see .DESCRIPTION.
        $copyParameters = @{
            SourceUrl = $source.ServerRelativeFileUrl
            TargetUrl = $target.ServerRelativeFileUrl
            Force     = $true   # suppresses the interactive confirm prompt only -- does not overwrite (that's -Overwrite, set below)
        }
        if ($Overwrite) { $copyParameters["Overwrite"] = $true }
        Copy-PnPFile @copyParameters
    }
    else {
        # 2. Cross-site: copy the file from the source site to the target site's
        #    SitePages FOLDER (Copy-PnPFile requires a folder -- not a filename --
        #    as -TargetUrl for a cross-site-collection copy; it lands under the
        #    source page name).
        if ($source.PageName -ne $target.PageName) {
            $existingIntermediate = Get-PnPFile -Url $copiedFileServerRelativeUrl -ErrorAction SilentlyContinue
            if ($existingIntermediate) {
                throw "Intermediate landing file already exists at '$copiedFileServerRelativeUrl' on the target site. Refusing to overwrite unrelated page during cross-site copy staging."
            }
        }

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
}

$plan | ConvertTo-Json -Depth 8
