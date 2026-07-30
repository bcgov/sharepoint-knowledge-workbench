# ==============================================================================
# Script Name: phase-3-0-tenant-discovery.ps1
# Description: Phase 3.0 (SharePoint Tenant-Capability Discovery) read-only probe
#              script for the manual-conversion-poc initiative's Phase 3 pilot
#              (Governed SharePoint Knowledge Pilot). Answers, with observed
#              evidence rather than assumption, the specific questions Phase 3's
#              provisional metadata schema (spec Section 7) needs answered before
#              it stops being provisional:
#
#                1. Site/web/library inventory (master plan Stage 3.0.1.2) — what
#                   surfaces actually exist on the target site.
#                2. Existing field/column type inventory (Stage 3.0.2.5) — what
#                   column types (Choice, Person, Date, Lookup, single-line text,
#                   etc.) are actually already in use on this tenant, as a concrete
#                   basis for confirming Section 7's proposed column types.
#                3. Content type inventory — supporting Stage 3.0.2.5 and giving a
#                   real basis for any content-type-based schema decisions.
#                4. Library versioning configuration (evidence-consumption
#                   matrix's proposed addition #1) — whether native version
#                   history is enabled, informing the PublishedVersion-column
#                   decision (spec Section 14 / unresolved-decisions #5).
#                5. Site groups / role assignments (evidence-consumption matrix's
#                   proposed addition #2) — candidate distinct identities for the
#                   Stage 3.4.2 oversharing/permission test (does NOT itself
#                   perform that test; only inventories what identities exist).
#
#              This script is strictly READ-ONLY — it creates, modifies, and
#              deletes nothing in the tenant, per the master plan's Subphase
#              3.0.2 staged protocol ("read-only first"). Native-Markdown-
#              rendering (Stage 3.0.2.4) is NOT covered here — that requires an
#              actual file upload/render observation and is called out below as
#              a separate manual verification step, not automatable read-only.
#
#              Modeled on the login/config pattern from the sibling
#              check-appearance-city-to-be-verified.ps1 example script (CMAT SPO
#              Replatform Team), adapted for this initiative's own tenant/site
#              and discovery questions. Config is loaded from a sibling
#              config.psd1 in the SAME directory (not a parent directory, unlike
#              the CMAT example, since both files live side-by-side here).
#
# Output:      A single JSON report at $OutputPath. This file is tenant evidence
#              — do NOT commit it to the manual-conversion-poc Git repository.
#              Per Phase 3 spec Section 16's evidence-storage split, only a
#              hand-written SANITIZED SUMMARY (no raw URLs/identities/site
#              structure) belongs in docs/reports/; this raw JSON is a
#              controlled-original and stays out of Git, in this temp/ directory
#              or another approved non-Git location.
#
# Usage:       pwsh ./phase-3-0-tenant-discovery.ps1
#              (Requires the PnP.PowerShell module and interactive login via the
#              delegated app registration in config.psd1 — a browser window will
#              open for you to authenticate. No credentials are stored by this
#              script or passed on the command line.)
# ==============================================================================

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [string]$ConfigPath = (Join-Path $PSScriptRoot "config.psd1"),

    [Parameter(Mandatory = $false)]
    [string]$OutputPath = (Join-Path $PSScriptRoot "phase-3-0-discovery-report.json"),

    # Hidden/system lists (e.g. "Web Part Gallery", "Master Page Gallery") are
    # excluded by default — they add noise and aren't candidate pilot libraries.
    # Pass -IncludeHiddenLists to include them if you need the full picture.
    [Parameter(Mandatory = $false)]
    [switch]$IncludeHiddenLists
)

if (-not (Test-Path $ConfigPath)) {
    Write-Error "Config file not found: $ConfigPath. Copy config.psd1.example (in this same folder) to config.psd1 and fill in ClientId/TenantId/SiteUrl before running this script."
    exit 1
}

Write-Host "Loading configuration from $ConfigPath..." -ForegroundColor Cyan
$config = Import-PowerShellDataFile -Path $ConfigPath

foreach ($required in @("ClientId", "TenantId", "SiteUrl")) {
    if (-not $config.ContainsKey($required) -or [string]::IsNullOrWhiteSpace($config[$required])) {
        Write-Error "config.psd1 is missing a value for '$required'. This script cannot connect without it."
        exit 1
    }
}

Write-Host "Connecting to SPO at $($config.SiteUrl) (interactive delegated login — a browser window will open)..." -ForegroundColor Cyan
Connect-PnPOnline -Url $config.SiteUrl -ClientId $config.ClientId -Tenant $config.TenantId -Interactive -ForceAuthentication -ErrorAction Stop

Write-Host "Connected successfully!" -ForegroundColor Green

$report = @{
    ExportDate       = (Get-Date).ToString("o")
    SiteUrl          = $config.SiteUrl
    Purpose          = "Phase 3.0 tenant-capability discovery (read-only) for manual-conversion-poc Phase 3 pilot"
    Web              = @{}
    Lists            = @()
    SiteFields       = @()
    ContentTypes     = @()
    SiteGroups       = @()
    ManualStepsNeeded = @(
        ("Stage 3.0.2.4 (native Markdown rendering): this script cannot observe rendered output. " +
         "Manually upload one sample rendered CEIS topic (from runs/ceis-manual-v2/render/) to a " +
         "designated non-production test library, view it in the browser, and record whether it " +
         "renders usably (headings/lists/tables/images) or requires a different representation " +
         "(e.g. a Site Page). Remove the test upload afterward per the staged-write protocol."),
        ("Stage 3.0.2.1-3.0.2.3 (AgentAssets / native SKILL.md authoring / agent-creation approval): " +
         "these require tenant-admin-level confirmation, not a site-level PnP probe. Follow up with " +
         "your tenant admin per the master plan's staged protocol.")
    )
}

# --- 1. Site/web inventory (Stage 3.0.1.2) ---
Write-Host "Inspecting web/site properties..." -ForegroundColor Yellow
$web = Get-PnPWeb -Includes WebTemplate, Configuration, Language, RegionalSettings
$report.Web = [PSCustomObject]@{
    Title         = $web.Title
    Url           = $web.Url
    WebTemplate   = $web.WebTemplate
    Configuration = $web.Configuration
    Language      = $web.Language
}
Write-Host "  Web template: $($web.WebTemplate) (configuration $($web.Configuration))" -ForegroundColor Green

# --- 2. Lists/libraries inventory, including versioning config (Stage 3.0.1.2 + proposed addition #1) ---
Write-Host "Inspecting lists/libraries (incl. versioning settings)..." -ForegroundColor Yellow
$listParams = @{ Includes = @("EnableVersioning", "EnableMinorVersions", "MajorVersionLimit", "MajorWithMinorVersionsLimit", "BaseTemplate", "ItemCount", "Hidden") }
$lists = Get-PnPList @listParams
foreach ($list in $lists) {
    if (-not $IncludeHiddenLists -and $list.Hidden) { continue }
    $report.Lists += [PSCustomObject]@{
        Title                       = $list.Title
        BaseTemplate                = $list.BaseTemplate.ToString()
        ItemCount                   = $list.ItemCount
        Hidden                      = $list.Hidden
        EnableVersioning            = $list.EnableVersioning
        EnableMinorVersions         = $list.EnableMinorVersions
        MajorVersionLimit           = $list.MajorVersionLimit
        MajorWithMinorVersionsLimit = $list.MajorWithMinorVersionsLimit
    }
}
Write-Host "  Found $($report.Lists.Count) list(s)/librar(ies) (hidden $(if ($IncludeHiddenLists) {'included'} else {'excluded'}))" -ForegroundColor Green

# --- 3. Site (web-scoped) field/column type inventory (Stage 3.0.2.5) ---
Write-Host "Inspecting site columns (field types actually in use on this tenant)..." -ForegroundColor Yellow
$fields = Get-PnPField -InSiteHierarchy
foreach ($f in $fields) {
    if ($f.Hidden -and -not $IncludeHiddenLists) { continue }
    $choices = $null
    if ($f.TypeAsString -eq "Choice" -or $f.TypeAsString -eq "MultiChoice") {
        try { $choices = (Get-PnPProperty -ClientObject $f -Property "Choices").Choices } catch { $choices = $null }
    }
    $report.SiteFields += [PSCustomObject]@{
        InternalName = $f.InternalName
        Title        = $f.Title
        TypeAsString = $f.TypeAsString
        Required     = $f.Required
        Group        = $f.Group
        Choices      = $choices
    }
}
Write-Host "  Found $($report.SiteFields.Count) site column(s)" -ForegroundColor Green

# --- 4. Content type inventory ---
Write-Host "Inspecting site content types..." -ForegroundColor Yellow
$contentTypes = Get-PnPContentType
foreach ($ct in $contentTypes) {
    $report.ContentTypes += [PSCustomObject]@{
        Name        = $ct.Name
        Id          = $ct.Id.ToString()
        Group       = $ct.Group
        Description = $ct.Description
    }
}
Write-Host "  Found $($report.ContentTypes.Count) content type(s)" -ForegroundColor Green

# --- 5. Site groups / role assignments (candidate identities for Stage 3.4.2, proposed addition #2) ---
Write-Host "Inspecting site groups (candidate identities for the future oversharing/permission test)..." -ForegroundColor Yellow
try {
    $groups = Get-PnPGroup
    foreach ($g in $groups) {
        $report.SiteGroups += [PSCustomObject]@{
            Title      = $g.Title
            Id         = $g.Id
            OwnerTitle = $g.OwnerTitle
            OnlyAllowMembersViewMembership = $g.OnlyAllowMembersViewMembership
        }
    }
    Write-Host "  Found $($report.SiteGroups.Count) site group(s)" -ForegroundColor Green
}
catch {
    Write-Warning "  Could not retrieve site groups: $($_.Exception.Message)"
}

# --- Save JSON output ---
$jsonContent = $report | ConvertTo-Json -Depth 6
[System.IO.File]::WriteAllText($OutputPath, $jsonContent)

Write-Host "========================================================================" -ForegroundColor Green
Write-Host "Phase 3.0 discovery report exported to: $OutputPath" -ForegroundColor Green
Write-Host "This file contains tenant-specific evidence (site URLs, structure, field" -ForegroundColor Yellow
Write-Host "names). Do NOT commit it to the manual-conversion-poc Git repository." -ForegroundColor Yellow
Write-Host "Write a sanitized summary into docs/reports/phase-3-sharepoint-pilot/" -ForegroundColor Yellow
Write-Host "referencing this file's controlled (non-Git) location instead, per spec" -ForegroundColor Yellow
Write-Host "Section 16's evidence-storage split." -ForegroundColor Yellow
Write-Host "========================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Manual verification still needed (not automatable read-only):" -ForegroundColor Cyan
foreach ($step in $report.ManualStepsNeeded) {
    Write-Host "  - $step" -ForegroundColor Cyan
}
