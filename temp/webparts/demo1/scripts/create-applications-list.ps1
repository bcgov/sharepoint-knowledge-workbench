<#
.SYNOPSIS
    Scratch script: creates the "Applications" and "ApplicationFavorites"
    SharePoint Online lists (plus sample data) needed by the demo1 SPFx
    line-of-business application launcher web part, using the isolated
    trial tenancy sandbox site (this repo's own SharePoint site cannot yet
    host SPFx web parts for testing).

.DESCRIPTION
    Creates two lists on the trial tenancy sandbox site configured in
    config.psd1 (a local copy of the sandbox settings, see -ConfigPath):
      1. "Applications" — Title, IconUrl (Text), Url (Text), Pinned (Yes/No).
         Seeded with sample line-of-business apps (a few marked Pinned).
         Also generates and uploads a generic placeholder icon PNG to
         SiteAssets/app-icons/ (via System.Drawing) and stores each sample
         item's IconUrl as the site-relative path to that file (not a
         domain-root-relative path, which would resolve incorrectly for a
         site under a /sites/<name> managed path).
      2. "ApplicationFavorites" — Title, ApplicationId (Number). Empty by
         default; the web part creates/deletes items here per user to track
         "hearted" favorites (Author = favoriting user).

    Idempotent: re-running skips list/field creation if they already exist,
    and skips sample items whose Title already exists.

    Pass -RemoveOnly to remove both lists created by this script.

.PARAMETER ConfigPath
    Path to config.psd1 for the isolated trial tenancy sandbox (NOT this
    repo's own root config.psd1 — that points at the BC Gov DEV site, which
    is not yet available for SPFx web part testing). Defaults to
    .\..\config\config.psd1 (a local copy of the same sandbox settings used
    by jag-csb-cmat-sharepoint-online's
    trial-tenancy-testing\config-trial.psd1 and its books-authors-spfx-poc).

.PARAMETER RemoveOnly
    If set, skips create/populate steps and only removes the two lists.

.EXAMPLE
    pwsh -File .\create-applications-list.ps1
    pwsh -File .\create-applications-list.ps1 -RemoveOnly
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [string]$ConfigPath = "$PSScriptRoot\..\config\config.psd1",

    [Parameter(Mandatory = $false)]
    [switch]$RemoveOnly
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# auth-helpers.ps1 lives in the sibling repo's sharepoint-migration plugin -
# reused as-is (Connect-Spo only needs ClientId/TenantId/SiteUrl from config-trial.psd1),
# matching the pattern used by trial-tenancy-testing\books-authors-spfx-poc\01_create-books-authors-poc.ps1.
. "C:\Users\RICHFREM\source\repos\jag-csb-cmat-sharepoint-online\plugins\sharepoint-migration\scripts\lib\auth-helpers.ps1"

$ApplicationsListName = "Applications"
$FavoritesListName     = "ApplicationFavorites"

# --- Result tracking (mirrors this repo's other scratch/pilot scripts) ---
$results = [System.Collections.Generic.List[pscustomobject]]::new()
function Add-Result {
    param([string]$Section, [string]$Step, [string]$Status, [string]$Detail = "")
    $results.Add([pscustomobject]@{ Section = $Section; Step = $Step; Status = $Status; Detail = $Detail })
    $color = switch ($Status) { "PASS" { "Green" }; "SKIPPED" { "Yellow" }; default { "Red" } }
    Write-Host "  [$Status] $Step" -ForegroundColor $color
    if ($Detail) { Write-Host "         $Detail" -ForegroundColor DarkGray }
}

# Force a clean connection at the start of every run (matches 01_create-books-authors-poc.ps1).
Disconnect-PnPOnline -ErrorAction SilentlyContinue

if (-not (Test-Path $ConfigPath)) { throw "config.psd1 not found at '$ConfigPath'." }
$preConnectCfg = Import-PowerShellDataFile $ConfigPath
$TrialSiteUrl = $preConnectCfg.SiteUrl

Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host " Applications list setup: $TrialSiteUrl" -ForegroundColor Yellow
Write-Host "==================================================================" -ForegroundColor Cyan

# --- 1. Connect ---
Write-Host ""
Write-Host "1. Connect" -ForegroundColor Cyan
try {
    $cfg = Connect-Spo -ConfigPath $ConfigPath -SiteUrlOverride $TrialSiteUrl
    $currentUser = $null
    try { $currentUser = (Get-PnPWeb -Includes CurrentUser).CurrentUser } catch {}
    Add-Result "Connect" "Connect to site" "PASS" "$TrialSiteUrl | User=$($currentUser.LoginName)"
} catch {
    Add-Result "Connect" "Connect to site" "FAIL" (Get-ErrorDetail $_)
    $results | Format-Table -AutoSize
    exit 1
}

if ($RemoveOnly) {
    Write-Host ""
    Write-Host "2. Remove lists" -ForegroundColor Cyan
    try { Remove-PnPList -Identity $FavoritesListName -Force -ErrorAction Stop; Add-Result "Cleanup" "Remove list" "PASS" $FavoritesListName } catch { Add-Result "Cleanup" "Remove list" "FAIL" $_.Exception.Message }
    try { Remove-PnPList -Identity $ApplicationsListName -Force -ErrorAction Stop; Add-Result "Cleanup" "Remove list" "PASS" $ApplicationsListName } catch { Add-Result "Cleanup" "Remove list" "FAIL" $_.Exception.Message }
    Write-Host ""
    $results | Format-Table -AutoSize
    exit 0
}

# --- 2. Create Applications list + fields ---
Write-Host ""
Write-Host "2. Ensure 'Applications' list and columns exist" -ForegroundColor Cyan
try {
    $appsList = Get-PnPList -Identity $ApplicationsListName -ErrorAction SilentlyContinue
    if (-not $appsList) {
        New-PnPList -Title $ApplicationsListName -Template GenericList -ErrorAction Stop | Out-Null
        $appsList = Get-PnPList -Identity $ApplicationsListName -ErrorAction Stop
        Add-Result "Lists" "Create Applications list" "PASS" "ListId=$($appsList.Id)"
    } else {
        Add-Result "Lists" "Applications list exists" "SKIPPED" "ListId=$($appsList.Id)"
    }

    if (-not (Get-PnPField -List $ApplicationsListName -Identity "IconUrl" -ErrorAction SilentlyContinue)) {
        Add-PnPField -List $ApplicationsListName -Type Text -DisplayName "IconUrl" -InternalName "IconUrl" -ErrorAction Stop | Out-Null
        Add-Result "Lists" "Add IconUrl column" "PASS" ""
    } else {
        Add-Result "Lists" "IconUrl column exists" "SKIPPED" ""
    }

    if (-not (Get-PnPField -List $ApplicationsListName -Identity "Url" -ErrorAction SilentlyContinue)) {
        Add-PnPField -List $ApplicationsListName -Type Text -DisplayName "Url" -InternalName "Url" -ErrorAction Stop | Out-Null
        Add-Result "Lists" "Add Url column" "PASS" ""
    } else {
        Add-Result "Lists" "Url column exists" "SKIPPED" ""
    }

    if (-not (Get-PnPField -List $ApplicationsListName -Identity "Pinned" -ErrorAction SilentlyContinue)) {
        Add-PnPField -List $ApplicationsListName -Type Boolean -DisplayName "Pinned" -InternalName "Pinned" -ErrorAction Stop | Out-Null
        Add-Result "Lists" "Add Pinned column" "PASS" ""
    } else {
        Add-Result "Lists" "Pinned column exists" "SKIPPED" ""
    }
} catch {
    Add-Result "Lists" "Ensure Applications list" "FAIL" $_.Exception.Message
    $results | Format-Table -AutoSize
    exit 1
}

# --- 3. Create ApplicationFavorites list + fields ---
Write-Host ""
Write-Host "3. Ensure 'ApplicationFavorites' list and columns exist" -ForegroundColor Cyan
try {
    $favList = Get-PnPList -Identity $FavoritesListName -ErrorAction SilentlyContinue
    if (-not $favList) {
        New-PnPList -Title $FavoritesListName -Template GenericList -ErrorAction Stop | Out-Null
        $favList = Get-PnPList -Identity $FavoritesListName -ErrorAction Stop
        Add-Result "Lists" "Create ApplicationFavorites list" "PASS" "ListId=$($favList.Id)"
    } else {
        Add-Result "Lists" "ApplicationFavorites list exists" "SKIPPED" "ListId=$($favList.Id)"
    }

    if (-not (Get-PnPField -List $FavoritesListName -Identity "ApplicationId" -ErrorAction SilentlyContinue)) {
        Add-PnPField -List $FavoritesListName -Type Number -DisplayName "ApplicationId" -InternalName "ApplicationId" -ErrorAction Stop | Out-Null
        Add-Result "Lists" "Add ApplicationId column" "PASS" ""
    } else {
        Add-Result "Lists" "ApplicationId column exists" "SKIPPED" ""
    }
} catch {
    Add-Result "Lists" "Ensure ApplicationFavorites list" "FAIL" $_.Exception.Message
}

# --- 4. Generic app icon (uploaded to SiteAssets/app-icons, site-relative path) ---
Write-Host ""
Write-Host "4. Ensure generic app icon file exists in SiteAssets/app-icons" -ForegroundColor Cyan
$web = Get-PnPWeb -Includes ServerRelativeUrl
$siteServerRelativeUrl = $web.ServerRelativeUrl.TrimEnd('/')
$iconFolderSiteRelative = "$siteServerRelativeUrl/SiteAssets/app-icons"
$iconFileName = "generic-app.png"
$genericIconUrl = "$iconFolderSiteRelative/$iconFileName"

try {
    $existingIconFile = Get-PnPFile -Url "$iconFolderSiteRelative/$iconFileName" -ErrorAction SilentlyContinue
    if ($existingIconFile) {
        Add-Result "Assets" "Generic app icon exists" "SKIPPED" $genericIconUrl
    } else {
        Add-Type -AssemblyName System.Drawing
        $bitmap = New-Object System.Drawing.Bitmap 48, 48
        $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
        $graphics.Clear([System.Drawing.Color]::FromArgb(255, 3, 120, 124))
        $font = New-Object System.Drawing.Font "Segoe UI", 20, ([System.Drawing.FontStyle]::Bold)
        $brush = [System.Drawing.Brushes]::White
        $stringFormat = New-Object System.Drawing.StringFormat
        $stringFormat.Alignment = [System.Drawing.StringAlignment]::Center
        $stringFormat.LineAlignment = [System.Drawing.StringAlignment]::Center
        $graphics.DrawString("A", $font, $brush, (New-Object System.Drawing.RectangleF 0, 0, 48, 48), $stringFormat)

        $tempIconPath = Join-Path ([System.IO.Path]::GetTempPath()) $iconFileName
        $bitmap.Save($tempIconPath, [System.Drawing.Imaging.ImageFormat]::Png)
        $graphics.Dispose()
        $bitmap.Dispose()

        Resolve-PnPFolder -SiteRelativePath "SiteAssets/app-icons" -ErrorAction Stop | Out-Null
        Add-PnPFile -Path $tempIconPath -Folder "SiteAssets/app-icons" -ErrorAction Stop | Out-Null
        Remove-Item $tempIconPath -ErrorAction SilentlyContinue

        Add-Result "Assets" "Upload generic app icon" "PASS" $genericIconUrl
    }
} catch {
    Add-Result "Assets" "Ensure generic app icon" "FAIL" $_.Exception.Message
}

# --- 5. Sample data (matches the reference intranet "Applications" list) ---
Write-Host ""
Write-Host "5. Ensure sample Applications" -ForegroundColor Cyan
$sampleApps = @(
    @{ Title = "ARC";                    IconUrl = $genericIconUrl; Url = "https://example.com/arc";        Pinned = $false },
    @{ Title = "BCSSS";                  IconUrl = $genericIconUrl; Url = "https://example.com/bcsss";      Pinned = $false },
    @{ Title = "CAS";                    IconUrl = $genericIconUrl; Url = "https://example.com/cas";        Pinned = $false },
    @{ Title = "CCD";                    IconUrl = $genericIconUrl; Url = "https://example.com/ccd";        Pinned = $false },
    @{ Title = "CDDS";                   IconUrl = $genericIconUrl; Url = "https://example.com/cdds";       Pinned = $false },
    @{ Title = "CEIS";                   IconUrl = $genericIconUrl; Url = "https://example.com/ceis";       Pinned = $true  },
    @{ Title = "CISA";                   IconUrl = $genericIconUrl; Url = "https://example.com/cisa";       Pinned = $false },
    @{ Title = "Contacts";               IconUrl = $genericIconUrl; Url = "https://example.com/contacts";   Pinned = $true  },
    @{ Title = "Court Administration";   IconUrl = $genericIconUrl; Url = "https://example.com/court-admin"; Pinned = $true  }
)

$existingApps = Get-PnPListItem -List $ApplicationsListName -Fields "Id", "Title", "IconUrl" -ErrorAction SilentlyContinue
foreach ($app in $sampleApps) {
    try {
        $existing = $existingApps | Where-Object { $_["Title"] -eq $app.Title }
        if ($existing) {
            if ($existing["IconUrl"] -ne $app.IconUrl) {
                Set-PnPListItem -List $ApplicationsListName -Identity $existing.Id -Values @{ IconUrl = $app.IconUrl } -ErrorAction Stop | Out-Null
                Add-Result "SampleData" "Application '$($app.Title)' exists" "PASS" "Item ID $($existing.Id) — IconUrl corrected to $($app.IconUrl)"
            } else {
                Add-Result "SampleData" "Application '$($app.Title)' exists" "SKIPPED" "Item ID $($existing.Id)"
            }
        } else {
            $item = Add-PnPListItem -List $ApplicationsListName -Values @{
                Title   = $app.Title
                IconUrl = $app.IconUrl
                Url     = $app.Url
                Pinned  = $app.Pinned
            } -ErrorAction Stop
            Add-Result "SampleData" "Add Application '$($app.Title)'" "PASS" "Item ID $($item.Id), Pinned=$($app.Pinned)"
        }
    } catch {
        Add-Result "SampleData" "Application '$($app.Title)'" "FAIL" $_.Exception.Message
    }
}

Write-Host ""
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host " SUMMARY" -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan
$results | Format-Table -AutoSize
Write-Host ""
Write-Host "Applications list: $TrialSiteUrl/Lists/$ApplicationsListName/AllItems.aspx" -ForegroundColor Yellow
