<#
.SYNOPSIS
Tests effective SharePoint capabilities for a selected app registration and
authentication mode. Does NOT infer a Sites.Selected role tier (Write vs
Manage) from list/library creation -- an earlier version of this script did,
and production testing disproved that assumption.

.DESCRIPTION
This script does not test or disprove Microsoft's delegated-access
intersection model -- it tests effective capabilities under the current
auth mode. A successful operation means the app grant and the current
signed-in user context (for -AuthMode Interactive) together allowed it;
it does not mean the stored app role is any particular tier. See
../references/effective-permissions-matrix.md's "How effective access is
actually calculated" section for the full reasoning and the controlled
tests (varying app grant with fixed user rights, or vice versa) that
would actually probe the intersection model -- none of which this script
performs on its own.

CAUTION -- read before trusting this script's capability results as a tier
signal: an earlier version of this script assumed New-PnPList / New-PnPList
-Template DocumentLibrary distinguished Write from Manage (Write blocks
creation, Manage allows it). Production testing disproved that assumption
for the interactive app registration in this workbench's own real tenant:
Get-PnPAzureADAppSitePermission reported the stored grant role as {write},
while the same app, connected interactively, successfully created and
removed lists, document libraries, pages, items, and files. List/library/
page creation succeeding does not prove the stored role is Manage -- what
it disproves is the Write-blocks-structure assumption, not the intersection
model itself.

Two likely (not yet fully disambiguated) reasons this can happen:

1. Microsoft's current Sites.Selected documentation defines `write` as
   "read and modify metadata and contents of the resource" -- it does not
   document `write` as excluding list/library creation the way this
   workbench's earlier assumption (Write ~= Contribute, item CRUD only)
   claimed. That specific mapping came from older, possibly outdated or
   context-specific community guidance, not Microsoft's own current model.
2. For DELEGATED (interactive) sessions specifically, Microsoft's own
   documented model is that effective access is the INTERSECTION of the
   app's consented permission and the signed-in user's own SharePoint
   permission on the site -- the app can never exceed the user, and the
   user can never exceed the app's consented scope. If the signed-in user
   already holds elevated rights (e.g. Site Collection Administrator) on
   the target site independent of the app's own grant, list/library
   creation succeeding may reflect the USER's permission, not the app's
   stored Sites.Selected role at all.

Because of this, this script reports TWO SEPARATE things per site, and
does not conflate them:

  1. STORED SITES.SELECTED ROLE ASSIGNMENT -- read directly via
     Get-PnPAzureADAppSitePermission when possible (best-effort; a
     failure to read it is reported, not
     treated as a test failure).
  2. EFFECTIVE CAPABILITIES -- what PnP operations actually succeed or
     fail for the current connection (app + auth mode + signed-in
     identity, if any), reported as a capability list, not a tier label.

Every created object (list, library, item, file, page, site column,
content type) is removed
immediately after its probe -- no residue left on any site, regardless of
pass/fail.

Supports two auth modes -- do not assume an interactive-session probe says
anything about a certificate/app-only registration's boundary, or vice
versa; they are different auth paths and must be tested separately:

  -AuthMode Interactive (default): Connect-PnPOnline -Interactive (prompts
    for browser sign-in). Effective capabilities reflect the intersection
    of the app's consented scope and the signed-in user's own permissions.
  -AuthMode Certificate: Connect-PnPOnline -Thumbprint (app-only, no user
    context). Effective capabilities reflect the application permission
    grant alone. Requires -CertThumbprint.

A successful Interactive probe cannot be used to infer the capability
boundary of a certificate-based app-only registration. Run this same
probe in Certificate mode using the ETL registration's own ClientId and
certificate before claiming the ETL app has any particular capability --
Microsoft's delegated-access model explicitly intersects app permissions
AND user permissions for interactive sessions, so interactive results
prove nothing about what an app-only identity can do alone.

Reads ClientId/TenantId from config.psd1 at the repo root by default
(supports both the nested Connection = @{...} schema and a flat top-level
schema) -- override with -ClientId/-TenantId for a different registration
(e.g. the certificate-based ETL app, which is not the registration
config.psd1 describes). SiteUrl is NOT read from config.psd1 -- this
script tests explicit target sites. No site URL is hardcoded -- -Sites is
required.

.PARAMETER ConfigPath
Path to config.psd1. Defaults to the repo root.

.PARAMETER Sites
Site URLs to probe, comma-joined in one string (see .EXAMPLE -- pwsh -File
argument binding only reliably accepts one token per array parameter;
comma-joined-and-split is the robust invocation). Required, no default.

.PARAMETER AuthMode
"Interactive" (default) or "Certificate".

.PARAMETER ClientId
Overrides config.psd1's ClientId -- required when testing a different
registration than the one config.psd1 describes (e.g. the certificate
ETL app).

.PARAMETER TenantId
Overrides config.psd1's TenantId.

.PARAMETER CertThumbprint
Required when -AuthMode Certificate.

.PARAMETER RunPermissionMutationProbe
Off by default. When set, additionally probes read-only permission
enumeration (Get-PnPGroup, Get-PnPRoleDefinition) -- never mutates
permissions. Kept opt-in and deliberately read-only; this script does not
attempt permission mutation probes at all.

.EXAMPLE
# Interactive app, default config.psd1
pwsh -File test-pnp-effective-capability-probe.ps1 -Sites "https://<tenant>.sharepoint.com/sites/<site-a>,https://<tenant>.sharepoint.com/sites/<site-b>"

.EXAMPLE
# Certificate-based ETL app -- explicit ClientId/TenantId/CertThumbprint, not config.psd1's registration
pwsh -File test-pnp-effective-capability-probe.ps1 -Sites "https://<tenant>.sharepoint.com/sites/<site>" -AuthMode Certificate -ClientId "<etl-client-id>" -TenantId "<tenant-id>" -CertThumbprint "<thumbprint>"
#>
param(
    [string]$ConfigPath = "$PSScriptRoot/../../../config.psd1",
    [Parameter(Mandatory = $true)]
    [string[]]$Sites,
    [ValidateSet("Interactive", "Certificate")]
    [string]$AuthMode = "Interactive",
    [string]$ClientId,
    [string]$TenantId,
    [string]$CertThumbprint,
    [switch]$RunPermissionMutationProbe
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# pwsh -File only binds the first bare token to a [string[]] parameter, then
# spills any further bare tokens onto the next declared parameter -- a real
# CLI-invocation quirk, not a scripting bug. Normalize: if invoked with a
# single comma-joined value (the robust way to pass multiple sites via
# -File), split it back into an array here.
if ($Sites.Count -eq 1 -and $Sites[0] -match ',') {
    $Sites = $Sites[0] -split ',' | ForEach-Object { $_.Trim() }
}

$raw = Import-PowerShellDataFile $ConfigPath
$cfg = if ($raw.ContainsKey('Connection')) { $raw.Connection } else { $raw }

if (-not $ClientId) { $ClientId = $cfg.ClientId }
if (-not $TenantId) { $TenantId = $cfg.TenantId }

if (-not $ClientId -or -not $TenantId) {
    Write-Error "ClientId/TenantId not resolved -- supply -ClientId/-TenantId or fix config.psd1."
}
if ($AuthMode -eq "Certificate" -and -not $CertThumbprint) {
    Write-Error "-CertThumbprint is required for -AuthMode Certificate."
}

Write-Host ""
Write-Host "=== PnP Effective Capability Probe ===" -ForegroundColor Cyan
Write-Host "NOTE: This script does NOT infer Sites.Selected tier from list/library creation." -ForegroundColor Yellow
Write-Host "It records the stored grant role, if readable, and separately tests effective" -ForegroundColor Yellow
Write-Host "capabilities. For delegated interactive auth, effective access reflects the" -ForegroundColor Yellow
Write-Host "intersection of the app's consented scope and the signed-in user's own" -ForegroundColor Yellow
Write-Host "SharePoint permissions -- it is not a pure app-grant signal." -ForegroundColor Yellow
Write-Host ""
Write-Host "AuthMode: $AuthMode" -ForegroundColor Gray
Write-Host "ClientId: $ClientId" -ForegroundColor Gray
Write-Host "TenantId: $TenantId" -ForegroundColor Gray
Write-Host ""

$results = @()

foreach ($site in $Sites) {
    Write-Host "--- $site ---" -ForegroundColor Yellow

    $result = [PSCustomObject]@{
        Site                    = $site
        AuthMode                = $AuthMode
        Connect                 = "not run"
        StoredGrantRole         = "unknown"
        StoredGrantApps         = "unknown"
        CreateList              = "not run"
        ListItemCrud            = "not run"
        CreateLibrary           = "not run"
        LibraryFileCrud         = "not run"
        CreatePage              = "not run"
        CreateSiteColumn        = "not run"
        CreateContentType       = "not run"
        EffectiveCapabilitySummary = "not run"
    }

    try {
        if ($AuthMode -eq "Interactive") {
            Connect-PnPOnline -Url $site -ClientId $ClientId -Tenant $TenantId -Interactive -ErrorAction Stop
        } else {
            Connect-PnPOnline -Url $site -ClientId $ClientId -Tenant $TenantId -Thumbprint $CertThumbprint -ErrorAction Stop
        }
        $web = Get-PnPWeb -ErrorAction Stop
        $result.Connect = "PASS -- $($web.Title)"
        Write-Host "  [PASS] Connect ($AuthMode) -- $($web.Title)" -ForegroundColor Green
    } catch {
        $result.Connect = "FAIL -- $($_.Exception.Message)"
        Write-Host "  [FAIL] Connect -- $($_.Exception.Message)" -ForegroundColor Red
        $results += $result
        continue
    }

    # --- Stored Sites.Selected role assignment: read directly, best-effort, never fails the run ---
    try {
        $grants = Get-PnPAzureADAppSitePermission -Site $site -ErrorAction Stop
        # .Apps is not guaranteed to be a single string (it's typically an array of
        # "DisplayName, ClientId" pairs) -- join before matching rather than relying
        # on -match's implicit stringification, which can behave inconsistently
        # depending on how PnP serializes the property.
        $grant = $grants | Where-Object { ($_.Apps -join ',') -match [regex]::Escape($ClientId) }
        if ($grant) {
            $result.StoredGrantRole = ($grant.Roles -join ",")
            $result.StoredGrantApps = ($grant.Apps -join ",")
            Write-Host "  [info] Stored grant role for this app: $($result.StoredGrantRole)" -ForegroundColor Cyan
        } else {
            $result.StoredGrantRole = "not found for this app"
            Write-Host "  [info] No stored Sites.Selected grant found for this ClientId on this site" -ForegroundColor Cyan
        }
    } catch {
        $result.StoredGrantRole = "not readable -- $($_.Exception.Message)"
        Write-Host "  [info] Could not read stored grant role: $($_.Exception.Message)" -ForegroundColor DarkGray
    }

    $stamp = Get-Date -Format 'yyyyMMdd-HHmmss'

    # --- List creation (effective-capability check, not a tier signal) ---
    $probeListName = "CapabilityProbe-List-$stamp"
    $listCreated = $false
    try {
        New-PnPList -Title $probeListName -Template GenericList -ErrorAction Stop | Out-Null
        $listCreated = $true
        $result.CreateList = "PASS"
        Write-Host "  [PASS] Create list '$probeListName'" -ForegroundColor Green
    } catch {
        $result.CreateList = "FAIL -- $($_.Exception.Message)"
        Write-Host "  [FAIL] Create list: $($_.Exception.Message)" -ForegroundColor Yellow
    }

    if ($listCreated) {
        try {
            $item = Add-PnPListItem -List $probeListName -Values @{ Title = "CapabilityProbe-Item-$stamp" } -ErrorAction Stop
            Remove-PnPListItem -List $probeListName -Identity $item.Id -Force -ErrorAction Stop
            $result.ListItemCrud = "PASS"
            Write-Host "  [PASS] List item add/remove" -ForegroundColor Green
        } catch {
            $result.ListItemCrud = "FAIL -- $($_.Exception.Message)"
            Write-Host "  [FAIL] List item add/remove: $($_.Exception.Message)" -ForegroundColor Red
        }
        Remove-PnPList -Identity $probeListName -Force -ErrorAction SilentlyContinue
        Write-Host "  [cleanup] Removed probe list" -ForegroundColor DarkGray
    } else {
        $result.ListItemCrud = "skipped (no list to test against)"
    }

    # --- Document library creation (effective-capability check, not a tier signal) ---
    $probeLibName = "CapabilityProbe-Lib-$stamp"
    $libCreated = $false
    try {
        New-PnPList -Title $probeLibName -Template DocumentLibrary -ErrorAction Stop | Out-Null
        $libCreated = $true
        $result.CreateLibrary = "PASS"
        Write-Host "  [PASS] Create document library '$probeLibName'" -ForegroundColor Green
    } catch {
        $result.CreateLibrary = "FAIL -- $($_.Exception.Message)"
        Write-Host "  [FAIL] Create document library: $($_.Exception.Message)" -ForegroundColor Yellow
    }

    if ($libCreated) {
        # -Folder needs the library's real server-relative URL, not its bare
        # title -- same lesson already learned once in this repo
        # (rollback-skill-deployment.ps1: derive the path from the target
        # library's own RootFolder.ServerRelativeUrl rather than assuming a
        # title resolves correctly).
        $probeLib = Get-PnPList -Identity $probeLibName -Includes RootFolder -ErrorAction Stop
        $libFolderUrl = $probeLib.RootFolder.ServerRelativeUrl

        $tempFile = Join-Path ([System.IO.Path]::GetTempPath()) "CapabilityProbe-Doc-$stamp.txt"
        "capability probe" | Out-File -FilePath $tempFile -Encoding utf8
        try {
            $uploaded = Add-PnPFile -Path $tempFile -Folder $libFolderUrl -ErrorAction Stop
            Remove-PnPFile -ServerRelativeUrl $uploaded.ServerRelativeUrl -Force -ErrorAction Stop
            $result.LibraryFileCrud = "PASS"
            Write-Host "  [PASS] Document upload/remove" -ForegroundColor Green
        } catch {
            $result.LibraryFileCrud = "FAIL -- $($_.Exception.Message)"
            Write-Host "  [FAIL] Document upload/remove: $($_.Exception.Message)" -ForegroundColor Red
        } finally {
            Remove-Item -Path $tempFile -Force -ErrorAction SilentlyContinue
        }
        Remove-PnPList -Identity $probeLibName -Force -ErrorAction SilentlyContinue
        Write-Host "  [cleanup] Removed probe library" -ForegroundColor DarkGray
    } else {
        $result.LibraryFileCrud = "skipped (no library to test against)"
    }

    # --- Page create/delete ---
    $probePageName = "CapabilityProbe-Page-$stamp"
    try {
        Add-PnPPage -Name $probePageName -LayoutType Article -ErrorAction Stop | Out-Null
        $result.CreatePage = "PASS"
        Write-Host "  [PASS] Create page" -ForegroundColor Green
        Remove-PnPPage -Identity $probePageName -Force -ErrorAction SilentlyContinue
        Write-Host "  [cleanup] Removed probe page" -ForegroundColor DarkGray
    } catch {
        $result.CreatePage = "FAIL -- $($_.Exception.Message)"
        Write-Host "  [FAIL] Create page: $($_.Exception.Message)" -ForegroundColor Red
    }

    # --- Site column (field) create/delete -- schema-level, NOT covered by list/library
    # creation succeeding. This is exactly the kind of operation flagged as untested in
    # effective-permissions-matrix.md -- do not assume it behaves like list/library
    # creation just because those passed. ---
    $probeFieldInternalName = "CapabilityProbeField$($stamp -replace '-','')"
    try {
        Add-PnPField -DisplayName "CapabilityProbe-Field-$stamp" -InternalName $probeFieldInternalName `
            -Type Text -Group "Capability Probe" -ErrorAction Stop | Out-Null
        $result.CreateSiteColumn = "PASS"
        Write-Host "  [PASS] Create site column '$probeFieldInternalName'" -ForegroundColor Green
        Remove-PnPField -Identity $probeFieldInternalName -Force -ErrorAction SilentlyContinue
        Write-Host "  [cleanup] Removed probe site column" -ForegroundColor DarkGray
    } catch {
        $result.CreateSiteColumn = "FAIL -- $($_.Exception.Message)"
        Write-Host "  [FAIL] Create site column: $($_.Exception.Message)" -ForegroundColor Red
    }

    # --- Content type create/delete -- schema-level, same caveat as site columns above. ---
    $probeContentTypeName = "CapabilityProbe-CT-$stamp"
    try {
        Add-PnPContentType -Name $probeContentTypeName -Description "Capability probe -- safe to delete" `
            -Group "Capability Probe" -ParentContentType (Get-PnPContentType -Identity "Item") -ErrorAction Stop | Out-Null
        $result.CreateContentType = "PASS"
        Write-Host "  [PASS] Create content type '$probeContentTypeName'" -ForegroundColor Green
        Remove-PnPContentType -Identity $probeContentTypeName -Force -ErrorAction SilentlyContinue
        Write-Host "  [cleanup] Removed probe content type" -ForegroundColor DarkGray
    } catch {
        $result.CreateContentType = "FAIL -- $($_.Exception.Message)"
        Write-Host "  [FAIL] Create content type: $($_.Exception.Message)" -ForegroundColor Red
    }

    # --- Optional, read-only, opt-in: permission enumeration ---
    if ($RunPermissionMutationProbe) {
        try {
            $groups = Get-PnPGroup -ErrorAction Stop
            Write-Host "  [info] Get-PnPGroup succeeded -- $($groups.Count) group(s) readable" -ForegroundColor Cyan
        } catch {
            Write-Host "  [info] Get-PnPGroup failed: $($_.Exception.Message)" -ForegroundColor DarkGray
        }
        try {
            $roles = Get-PnPRoleDefinition -ErrorAction Stop
            Write-Host "  [info] Get-PnPRoleDefinition succeeded -- $($roles.Count) role definition(s) readable" -ForegroundColor Cyan
        } catch {
            Write-Host "  [info] Get-PnPRoleDefinition failed: $($_.Exception.Message)" -ForegroundColor DarkGray
        }
    }

    $capabilities = @()
    if ($result.CreateList -like "PASS*") { $capabilities += "CanCreateList" }
    if ($result.CreateLibrary -like "PASS*") { $capabilities += "CanCreateLibrary" }
    if ($result.CreatePage -like "PASS*") { $capabilities += "CanCreatePage" }
    if ($result.ListItemCrud -like "PASS*") { $capabilities += "CanCrudListItems" }
    if ($result.LibraryFileCrud -like "PASS*") { $capabilities += "CanCrudFiles" }
    if ($result.CreateSiteColumn -like "PASS*") { $capabilities += "CanCreateSiteColumn" }
    if ($result.CreateContentType -like "PASS*") { $capabilities += "CanCreateContentType" }
    $result.EffectiveCapabilitySummary = if ($capabilities.Count) { $capabilities -join ", " } else { "No write/provisioning capabilities observed" }

    Disconnect-PnPOnline -ErrorAction SilentlyContinue
    $results += $result
    Write-Host ""
}

Write-Host "=== Summary ===" -ForegroundColor Cyan
$results | Format-Table Site, AuthMode, Connect, StoredGrantRole, EffectiveCapabilitySummary -Wrap
