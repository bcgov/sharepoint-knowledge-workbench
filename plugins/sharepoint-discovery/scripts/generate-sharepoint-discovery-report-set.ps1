<#
.SYNOPSIS
    Assembles a set of Markdown discovery reports from previously-collected SharePoint
    export files (JSON/CSV) into an analysis output folder.

.DESCRIPTION
    This is a pure local report assembler -- it performs no tenant I/O. It reads whatever
    raw export files are present under the target folder tree and renders them into
    Markdown reports. Every conclusion in the generated reports is derived from the actual
    counts/values found in the input files. If an input file is missing, the affected
    report says so explicitly (`Unavailable` / `No data provided`) instead of asserting a
    fixed conclusion -- this script never prints a finding it did not compute.

    Reads from (relative to the target root, i.e. the parent of -AnalysisDir):
      - navigation/site-chrome.json                         (master page / nav counts)
      - <AnalysisDir>/webpart_content_extract.json           (web part inventory)
      - <AnalysisDir>/webpart-code-groups.json               (deduplicated code review groups)
      - raw_exports/summary/lists_with_custom_forms.csv, or  (custom list forms)
        summary/lists_with_custom_forms.csv
      - -PermissionsJson (explicit optional parameter; no default path is guessed)

    Generates, in -AnalysisDir:
      1. master_page_summary.md              -- master page, theme, chrome & nav counts
      2. SCRIPT-EDITOR-CODE-EXTRACTION.md     -- Script Editor / custom inline JS analysis,
                                                  with an SPFx-needed verdict computed from
                                                  actual Script Editor web part counts
      3. PROBLEMATIC-WEBPARTS-SUMMARY.md      -- complex-logic / custom-HTML web part rollup
      4. ALL-UNIQUE-WEBPART-CODE-FOR-REVIEW.md -- per-group code review catalog
      5. security-analysis-summary.md         -- only generated if -PermissionsJson is
                                                  supplied and readable; otherwise this
                                                  report is skipped and a warning is emitted
                                                  (no boilerplate security narrative is ever
                                                  printed without real permissions data)
      6. custom_forms_summary.md              -- custom list form count, with a form-override
                                                  verdict computed from the actual CSV rows

.PARAMETER AnalysisDir
    Directory containing raw extraction files and where reports will be written
    (e.g. <site-root>/analysis).

.PARAMETER SiteName
    Human-readable site name used in report headings (e.g. "Contoso Intranet").

.PARAMETER PermissionsJson
    Optional path to a permissions/security export (groups, role assignments, inheritance
    breaks). If omitted, security-analysis-summary.md is not generated -- there is no
    fallback narrative for this report because the source data determines every claim it
    would make.

.EXAMPLE
    pwsh -File .\generate-sharepoint-discovery-report-set.ps1 -AnalysisDir ".\contoso\analysis" -SiteName "Contoso Intranet"

.EXAMPLE
    pwsh -File .\generate-sharepoint-discovery-report-set.ps1 -AnalysisDir ".\contoso\analysis" -SiteName "Contoso Intranet" -PermissionsJson ".\contoso\security\permissions.json"
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$AnalysisDir,

    [Parameter(Mandatory = $false)]
    [string]$SiteName = "SharePoint Target Site",

    [Parameter(Mandatory = $false)]
    [string]$PermissionsJson
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if (-not (Test-Path $AnalysisDir)) {
    throw "Analysis directory '$AnalysisDir' does not exist."
}

$analysisPath = Resolve-Path $AnalysisDir | Select-Object -ExpandProperty Path
$targetRoot   = Split-Path $analysisPath -Parent
$navDir       = Join-Path $targetRoot "navigation"

Write-Host "============================================================" -ForegroundColor DarkCyan
Write-Host "Generating Discovery Report Set for: $SiteName" -ForegroundColor Cyan
Write-Host "Target Folder: $analysisPath" -ForegroundColor White
Write-Host "============================================================" -ForegroundColor DarkCyan

# -----------------------------------------------------------------------------
# 1. Master Page & Chrome Summary (master_page_summary.md)
# -----------------------------------------------------------------------------
$chromeJson = Join-Path $navDir "site-chrome.json"
$masterPageName = "Unknown (no site-chrome.json input found)"
$topNavCount = $null
$quickLaunchCount = $null
if (Test-Path $chromeJson) {
    $chrome = Get-Content $chromeJson -Raw | ConvertFrom-Json
    if ($chrome.PSObject.Properties['MasterPageUrl']) { $masterPageName = Split-Path $chrome.MasterPageUrl -Leaf }
    if ($chrome.PSObject.Properties['TopNavigation']) { $topNavCount = $chrome.TopNavigation.Count }
    if ($chrome.PSObject.Properties['QuickLaunch'])   { $quickLaunchCount = $chrome.QuickLaunch.Count }
}
$topNavDisplay = if ($null -ne $topNavCount) { $topNavCount } else { "Unavailable (no site-chrome.json input found)" }
$quickLaunchDisplay = if ($null -ne $quickLaunchCount) { $quickLaunchCount } else { "Unavailable (no site-chrome.json input found)" }

$masterMd = @"
# Master Page & Chrome Customization Summary — $SiteName

> **Generated:** $(Get-Date -Format 'yyyy-MM-dd')
> **Target Site:** $SiteName

---

## 1. Master Page Breakdown

| Attribute | Detail |
|:---|:---|
| **Master Page In Use** | ``$masterPageName`` |
| **Top Navigation Items** | $topNavDisplay |
| **Quick Launch Items** | $quickLaunchDisplay |

## 2. Modern SPO Notes

- Classic master pages (``.master``) are deprecated in SharePoint Online.
- Modern SPO pages use the OOB modern page canvas without custom master pages.
- Header logos and navigation links carry over to Modern Site Header settings and Mega Menu / Hub Navigation.
"@
Set-Content -Path (Join-Path $analysisPath "master_page_summary.md") -Value $masterMd -Encoding UTF8
Write-Host "  [OK] Created master_page_summary.md" -ForegroundColor Green

# -----------------------------------------------------------------------------
# 2. Script Editor & Custom Code Web Part Analysis (SCRIPT-EDITOR-CODE-EXTRACTION.md)
# -----------------------------------------------------------------------------
$wpExtractJson = Join-Path $analysisPath "webpart_content_extract.json"
$sewpEntries = @()
$cewpEntries = @()
$accordionWps = @()
$allWpsCount = 0
$hasWpData = Test-Path $wpExtractJson

if ($hasWpData) {
    $allWps = Get-Content $wpExtractJson -Raw | ConvertFrom-Json
    $allWpsCount = $allWps.Count
    $sewpEntries = @($allWps | Where-Object {
        ($_.PSObject.Properties['TypeName'] -and $_.TypeName -like '*ScriptEditor*') -or
        ($_.PSObject.Properties['Content'] -and $_.Content -like '*<script*')
    })
    $cewpEntries = @($allWps | Where-Object {
        ($_.PSObject.Properties['TypeName'] -and $_.TypeName -like '*ContentEditor*') -or
        ($_.PSObject.Properties['WebPartTitle'] -and $_.WebPartTitle -like '*Content Editor*') -or
        ($_.PSObject.Properties['Content'] -and $_.Content -and $_.Content.Length -gt 0)
    })
    $accordionWps = @($allWps | Where-Object {
        $_.PSObject.Properties['Content'] -and ($_.Content -like '*panel-group*' -or $_.Content -like '*accordion*')
    })
}

$sewpMd = [System.Text.StringBuilder]::new()
[void]$sewpMd.AppendLine("# Custom Code & Script Editor Web Part Analysis — $SiteName")
[void]$sewpMd.AppendLine("")
[void]$sewpMd.AppendLine("> **Generated:** $(Get-Date -Format 'yyyy-MM-dd')  ")
if (-not $hasWpData) {
    [void]$sewpMd.AppendLine("> **Status:** Unavailable -- no `webpart_content_extract.json` input was found at `$wpExtractJson`.  ")
    [void]$sewpMd.AppendLine("")
    [void]$sewpMd.AppendLine("---")
    [void]$sewpMd.AppendLine("")
    [void]$sewpMd.AppendLine("No web part extraction data was provided for this site. This report cannot assess Script Editor usage, Content Editor usage, or SPFx need without that input. Re-run once `webpart_content_extract.json` has been collected.")
} else {
    [void]$sewpMd.AppendLine("> **Total Web Parts Analyzed:** $allWpsCount  ")
    [void]$sewpMd.AppendLine("> **Script Editor / Literal JS Web Parts Found:** $($sewpEntries.Count)  ")
    [void]$sewpMd.AppendLine("> **Content Editor / Custom HTML Web Parts Found:** $($cewpEntries.Count)  ")
    [void]$sewpMd.AppendLine("> **Bootstrap Accordion / Collapsible Web Parts Found:** $($accordionWps.Count)  ")
    [void]$sewpMd.AppendLine("")
    [void]$sewpMd.AppendLine("---")
    [void]$sewpMd.AppendLine("")
    [void]$sewpMd.AppendLine("## 1. Web Part Inventory & Customization Breakdown")
    [void]$sewpMd.AppendLine("")
    [void]$sewpMd.AppendLine("| Category | Count | Primary Features & HTML Components | Modern SPO Replacement Strategy |")
    [void]$sewpMd.AppendLine("|:---|---:|:---|:---|")
    [void]$sewpMd.AppendLine("| **Literal Script Editor (``<script>``)** | $($sewpEntries.Count) | Client-side DOM scripts & helpers | Review for JSON Column Formatting vs Power Apps / SPFx |")
    [void]$sewpMd.AppendLine("| **Bootstrap Accordions (``panel-group``)** | $($accordionWps.Count) | Collapsible FAQ/help panels | Native Modern Canvas Collapsible Sections |")
    [void]$sewpMd.AppendLine("| **Custom Content Editors (CEWP)** | $($cewpEntries.Count) | HTML tables, staff bios, link matrices | OOB Modern Text & Quick Links Web Parts |")
    [void]$sewpMd.AppendLine("")
    [void]$sewpMd.AppendLine("## 2. Identified Custom Script Web Parts")
    [void]$sewpMd.AppendLine("")

    if ($sewpEntries.Count -eq 0) {
        [void]$sewpMd.AppendLine("No literal Script Editor (``<script>``) web parts executing client-side JavaScript were detected on this site.")
        [void]$sewpMd.AppendLine("The $($cewpEntries.Count) other custom web part(s) found are Content Editor Web Parts (CEWP) containing static HTML markup, of which $($accordionWps.Count) use Bootstrap accordion patterns.")
    } else {
        [void]$sewpMd.AppendLine("| Page URL | WebPartId | Character Length | Summary / Intent |")
        [void]$sewpMd.AppendLine("|:---|:---|---:|:---|")
        foreach ($se in $sewpEntries) {
            $page = $se.PageUrl
            $guid = $se.WebPartId
            $len  = if ($se.Content) { $se.Content.Length } else { 0 }
            [void]$sewpMd.AppendLine("| ``$page`` | ``$guid`` | $len | Custom inline JavaScript |")
        }
    }

    [void]$sewpMd.AppendLine("")
    [void]$sewpMd.AppendLine("## 3. Modern Script Editor (PnP SPFx) Evaluation & Policy")
    [void]$sewpMd.AppendLine("")

    # INTEGRITY FIX: the source script hardcoded this verdict to "No." regardless of the
    # actual Script Editor count. Here the verdict is computed from $sewpEntries.Count.
    if ($sewpEntries.Count -eq 0) {
        [void]$sewpMd.AppendLine("- **Are Modern Script Editor Web Parts (PnP SPFx) needed for this site?**: **No.**")
        [void]$sewpMd.AppendLine("- **Reasoning**: No literal Script Editor web parts were found ($($sewpEntries.Count) of $allWpsCount total web parts). All $($cewpEntries.Count) remaining custom web part(s), including $($accordionWps.Count) Bootstrap accordion panel(s), can be re-architected using OOB Modern SPO Canvas Collapsible Sections, Quick Links, and Modern Text web parts.")
        [void]$sewpMd.AppendLine("- **Governance Advantage**: Eliminates the need to enable NoScript exceptions or deploy open-source PnP Modern Script Editor SPFx packages to the Tenant App Catalog.")
    } else {
        [void]$sewpMd.AppendLine("- **Are Modern Script Editor Web Parts (PnP SPFx) needed for this site?**: **Conditional -- requires manual review.**")
        [void]$sewpMd.AppendLine("- **Reasoning**: $($sewpEntries.Count) of $allWpsCount total web parts contain literal Script Editor / inline ``<script>`` content (see the table above). Each must be reviewed individually to determine whether its business logic can be replaced with JSON Column/View Formatting or Power Apps, or genuinely requires a PnP Modern Script Editor SPFx web part.")
        [void]$sewpMd.AppendLine("- **Governance Note**: Any Script Editor web part that cannot be eliminated requires enabling NoScript exceptions or deploying the PnP Modern Script Editor SPFx package to the Tenant App Catalog -- confirm this is acceptable under this tenant's governance policy before proceeding.")
    }
}

Set-Content -Path (Join-Path $analysisPath "SCRIPT-EDITOR-CODE-EXTRACTION.md") -Value $sewpMd.ToString() -Encoding UTF8
Write-Host "  [OK] Created SCRIPT-EDITOR-CODE-EXTRACTION.md" -ForegroundColor Green

# -----------------------------------------------------------------------------
# 3. Problematic Web Parts Summary (PROBLEMATIC-WEBPARTS-SUMMARY.md)
# -----------------------------------------------------------------------------
if (-not $hasWpData) {
    $probMd = @"
# Problematic Web Parts & Complex Logic Summary — $SiteName

> **Generated:** $(Get-Date -Format 'yyyy-MM-dd')
> **Status:** Unavailable -- no ``webpart_content_extract.json`` input was found at ``$wpExtractJson``.

---

No web part extraction data was provided for this site. This report cannot identify problematic web parts without that input. Re-run once ``webpart_content_extract.json`` has been collected.
"@
} else {
    $spfxNeededLabel = if ($sewpEntries.Count -eq 0) { "**No** (Native SPO feature)" } else { "**Conditional** -- see SCRIPT-EDITOR-CODE-EXTRACTION.md" }
    $probMd = @"
# Problematic Web Parts & Complex Logic Summary — $SiteName

> **Generated:** $(Get-Date -Format 'yyyy-MM-dd')
> **Total Web Parts Analyzed:** $allWpsCount

---

## 1. Complex Script & Custom HTML Breakdown

This document identifies web parts containing custom JavaScript logic, Bootstrap UI components (accordions), or custom HTML layout tables, based on the counts in ``webpart_content_extract.json``.

| Category | Instances | SPO Modernization Equivalent | Modern Script Editor Needed? |
|:---|---:|:---|:---|
| **Custom Inline Logic (``<script>``)** | $($sewpEntries.Count) | JSON Column Formatting / Power Apps / SPFx | $spfxNeededLabel |
| **Bootstrap Accordions (``panel-group``)** | $($accordionWps.Count) | Native SPO Canvas Collapsible Sections | **No** (Native SPO feature) |
| **Custom Content Editors (CEWP)** | $($cewpEntries.Count) | OOB Modern Text & Quick Links | **No** (Native SPO feature) |

## 2. Recommendation Matrix

- **Bootstrap Accordions ($($accordionWps.Count) instances)**: Re-architect using Native SPO Canvas Collapsible Sections (Section Background -> Collapsible).
- **Static Rich Text & HTML Tables ($($cewpEntries.Count) instances)**: Migrate directly to OOB Modern Text or Quick Links Web Parts.
- **Script Editor Web Parts ($($sewpEntries.Count) instances)**: Re-evaluate business intent to replace with JSON Column/View Formatting or Power Apps before considering PnP Modern Script Editor SPFx.
"@
}
Set-Content -Path (Join-Path $analysisPath "PROBLEMATIC-WEBPARTS-SUMMARY.md") -Value $probMd -Encoding UTF8
Write-Host "  [OK] Created PROBLEMATIC-WEBPARTS-SUMMARY.md" -ForegroundColor Green

# -----------------------------------------------------------------------------
# 4. Master Review Catalog (ALL-UNIQUE-WEBPART-CODE-FOR-REVIEW.md)
# -----------------------------------------------------------------------------
$groupsJson = Join-Path $analysisPath "webpart-code-groups.json"
$sb = [System.Text.StringBuilder]::new()
[void]$sb.AppendLine("# Master Web Part Code Review Catalog — $SiteName")
[void]$sb.AppendLine("")
[void]$sb.AppendLine("> **Generated:** $(Get-Date -Format 'yyyy-MM-dd')")
[void]$sb.AppendLine("")

if (-not (Test-Path $groupsJson)) {
    [void]$sb.AppendLine("> **Status:** Unavailable -- no ``webpart-code-groups.json`` input was found at ``$groupsJson``.")
    [void]$sb.AppendLine("")
    [void]$sb.AppendLine("No deduplicated web part code groups were provided for this site. This catalog cannot be assembled without that input. Re-run once ``webpart-code-groups.json`` has been collected.")
} else {
    $groupsData = Get-Content $groupsJson -Raw | ConvertFrom-Json
    $groups = $groupsData.groups
    [void]$sb.AppendLine("## Summary of Unique Functional Groups ($($groups.Count) Groups Total)")
    [void]$sb.AppendLine("")
    $i = 1
    foreach ($g in $groups) {
        $pairsProp = $g.PSObject.Properties['pagePartPairs']
        $repPage = "Unknown"
        $repId   = "Unknown"
        if ($pairsProp -and $pairsProp.Value -and $pairsProp.Value.Count -gt 0) {
            $first = $pairsProp.Value[0]
            $repPage = $first[0]
            $repId   = $first[1]
        }

        $sampleProp = $g.PSObject.Properties['sampleContent']
        $snippet = if ($sampleProp -and $sampleProp.Value) { $sampleProp.Value.ToString().Trim() } else { "" }

        $catProp = $g.PSObject.Properties['category']
        $cat = if ($catProp) { $catProp.Value } else { "Unknown" }

        $instProp = $g.PSObject.Properties['instanceCount']
        $instCount = if ($instProp) { $instProp.Value } else { 0 }

        $sumProp = $g.PSObject.Properties['summary']
        $summary = if ($sumProp) { $sumProp.Value } else { "Not provided in webpart-code-groups.json" }

        $spoProp = $g.PSObject.Properties['spoEquivalent']
        $spoEquiv = if ($spoProp) { $spoProp.Value } else { "Not provided in webpart-code-groups.json" }

        $effProp = $g.PSObject.Properties['effort']
        $effort = if ($effProp) { $effProp.Value } else { "Not provided in webpart-code-groups.json" }

        # INTEGRITY NOTE: source-provided category drives these narrative lines directly --
        # they are not asserted independent of $cat/$spoEquiv.
        $userEffect = if ($cat -eq 'TextOnly') { "Renders rich text content / banner to page visitors." } else { "Custom script execution or placeholder (category: $cat)." }
        $busIntent  = if ($cat -eq 'TextOnly') { "Provide information, guidance, or links to site users." } else { "Custom business logic or layout placeholder (category: $cat)." }
        $spfxVal    = if ($cat -in @('TextOnly', 'Empty')) { "Not required -- category '$cat' is a native modern OOB feature." } else { "Conditional -- category '$cat' requires manual review." }

        [void]$sb.AppendLine("---")
        [void]$sb.AppendLine("## Group $i — $cat ($instCount instances)")
        [void]$sb.AppendLine('')
        $repStr = '**Representative Page:** `' + $repPage + '` (WebPartId `' + $repId + '`)'
        [void]$sb.AppendLine($repStr)
        [void]$sb.AppendLine('')
        [void]$sb.AppendLine('### Code / Content Snippet')
        [void]$sb.AppendLine('```html')
        [void]$sb.AppendLine($snippet)
        [void]$sb.AppendLine('```')
        [void]$sb.AppendLine('')
        [void]$sb.AppendLine('### Modernization Assessment')
        [void]$sb.AppendLine("- **Business behavior:** $summary")
        [void]$sb.AppendLine("- **Recommended modern replacement:** $spoEquiv")
        [void]$sb.AppendLine("- **Estimated effort:** $effort")
        [void]$sb.AppendLine('')
        [void]$sb.AppendLine('### Modernization Behaviour Analysis')
        [void]$sb.AppendLine('**User-visible effect:**')
        [void]$sb.AppendLine($userEffect)
        [void]$sb.AppendLine('')
        [void]$sb.AppendLine('**Business intent:**')
        [void]$sb.AppendLine($busIntent)
        [void]$sb.AppendLine('')
        [void]$sb.AppendLine('**Modern SPO approach:**')
        [void]$sb.AppendLine($spoEquiv)
        [void]$sb.AppendLine('')
        [void]$sb.AppendLine('**SPFx assessment:**')
        [void]$sb.AppendLine($spfxVal)
        [void]$sb.AppendLine('')
        $i++
    }
}

Set-Content -Path (Join-Path $analysisPath "ALL-UNIQUE-WEBPART-CODE-FOR-REVIEW.md") -Value $sb.ToString() -Encoding UTF8
Write-Host "  [OK] Created ALL-UNIQUE-WEBPART-CODE-FOR-REVIEW.md" -ForegroundColor Green

# -----------------------------------------------------------------------------
# 5. Security Analysis Summary (security-analysis-summary.md)
#
# INTEGRITY FIX: the source script generated this report from zero data inputs --
# it was 100% static boilerplate. This version only generates the report when the
# caller explicitly supplies -PermissionsJson; otherwise the report is skipped
# entirely and a warning is emitted, rather than printing an unearned narrative.
# -----------------------------------------------------------------------------
if ([string]::IsNullOrWhiteSpace($PermissionsJson)) {
    Write-Warning "security-analysis-summary.md was NOT generated: no -PermissionsJson input was supplied. There is no default path guessed for this file, because a security report must never be produced without real permissions data."
} elseif (-not (Test-Path $PermissionsJson)) {
    Write-Warning "security-analysis-summary.md was NOT generated: -PermissionsJson path '$PermissionsJson' does not exist."
} else {
    $permsData = Get-Content $PermissionsJson -Raw | ConvertFrom-Json
    $groupCount = if ($permsData.PSObject.Properties['Groups']) { @($permsData.Groups).Count } else { 0 }
    $brokenInheritanceCount = if ($permsData.PSObject.Properties['BrokenInheritance']) { @($permsData.BrokenInheritance).Count } else { 0 }

    $secMd = @"
# Security & Permissions Analysis Summary — $SiteName

> **Generated:** $(Get-Date -Format 'yyyy-MM-dd')
> **Source:** ``$PermissionsJson``

---

## 1. Groups & Inheritance (from source data)

| Attribute | Detail |
|:---|:---|
| **SharePoint Groups Found** | $groupCount |
| **Lists/Libraries with Broken Inheritance** | $brokenInheritanceCount |

## 2. Modernization Notes

- SharePoint Online site security maps classic SP groups (Owners, Members, Visitors) into modern M365 / Entra ID group roles.
- The $brokenInheritanceCount broken-inheritance item(s)/list(s) identified above require individual review prior to content migration to confirm the correct modern group mapping.
"@
    Set-Content -Path (Join-Path $analysisPath "security-analysis-summary.md") -Value $secMd -Encoding UTF8
    Write-Host "  [OK] Created security-analysis-summary.md" -ForegroundColor Green
}

# -----------------------------------------------------------------------------
# 6. Custom Forms Summary (custom_forms_summary.md)
# -----------------------------------------------------------------------------
$formsCsv = Join-Path $targetRoot "raw_exports\summary\lists_with_custom_forms.csv"
if (-not (Test-Path $formsCsv)) {
    $formsCsv = Join-Path $targetRoot "summary\lists_with_custom_forms.csv"
}
$hasFormsData = Test-Path $formsCsv
$formCount = 0
if ($hasFormsData) {
    $formsData = @(Import-Csv $formsCsv)
    $formCount = $formsData.Count
}

if (-not $hasFormsData) {
    $formsMd = @"
# Custom List Forms Summary — $SiteName

> **Generated:** $(Get-Date -Format 'yyyy-MM-dd')
> **Status:** Unavailable -- no ``lists_with_custom_forms.csv`` input was found under ``$targetRoot``.

---

No custom-forms export was provided for this site. This report cannot assess custom list form usage without that input. Re-run once ``lists_with_custom_forms.csv`` has been collected.
"@
} else {
    # INTEGRITY FIX: the source script hardcoded "Genuine Custom Script Overrides
    # Downloaded: 0 (all standard OOB forms)" and "All list forms ... use standard OOB
    # forms" regardless of $formCount. This version only states what the CSV row count
    # actually supports: a raw count of lists whose custom-form URL was flagged, with an
    # explicit note that overriding-script detection was not performed by this input.
    $formsMd = @"
# Custom List Forms Summary — $SiteName

> **Generated:** $(Get-Date -Format 'yyyy-MM-dd')
> **Source:** ``$formsCsv``

---

## 1. Custom Form Inventory

- **Lists with Custom Form URLs Identified:** $formCount
- **Genuine Custom Script Overrides Downloaded:** Not determined by this input -- ``lists_with_custom_forms.csv`` records only which lists have a custom form URL, not whether that form contains a genuine script override versus a standard OOB form. A separate script-content check is required to make that determination.

## 2. Modernization Notes

$(if ($formCount -eq 0) { "No lists with custom form URLs were identified in the source data. If this matches expectations, all list forms on this site are likely using standard OOB SharePoint forms, which render as modern SharePoint forms in SPO automatically." } else { "$formCount list(s) were flagged with a custom form URL. Each must be reviewed individually to confirm whether it is a genuine script override (requiring a Power Apps or SPFx replacement) or a cosmetic customization of the standard OOB form (which still renders as a modern SharePoint form in SPO)." })
"@
}
Set-Content -Path (Join-Path $analysisPath "custom_forms_summary.md") -Value $formsMd -Encoding UTF8
Write-Host "  [OK] Created custom_forms_summary.md" -ForegroundColor Green

Write-Host ""
Write-Host "============================================================" -ForegroundColor DarkCyan
Write-Host "Discovery report set generated in: $analysisPath" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor DarkCyan
