# Discovery report set: integrity fixes and provenance

## Contents

- [Why this is not a literal port](#why-this-is-not-a-literal-port)
- [Generalization from the source](#generalization-from-the-source)
- [Scripts and related assets](#scripts-and-related-assets)
- [Provenance](#provenance)

## Why this is not a literal port

The script was ported from an originating migration repository's `generate-discovery-reports.ps1`,
which had a real data-integrity problem: several report sections asserted fixed, hardcoded conclusions
regardless of the scan data. This version fixes each one.

1. **Modern Script Editor (PnP SPFx) verdict.** The source always printed
   `**Are Modern Script Editor Web Parts (PnP SPFx) needed for this site?**: **No.**` even though it had
   computed `$sewpEntries.Count` just above. This version computes the verdict: `No.` only when
   `$sewpEntries.Count -eq 0` (with the reasoning shown using the real numbers), otherwise
   `Conditional -- requires manual review.` with an explanation that each detected Script Editor web
   part must be reviewed individually. The same fix applies to the corresponding cell in
   `PROBLEMATIC-WEBPARTS-SUMMARY.md`.
2. **Custom forms summary.** The source always printed
   `**Genuine Custom Script Overrides Downloaded:** 0 (all standard OOB forms)` and
   `All list forms on this site use standard OOB SharePoint forms`, though `$formCount` (read from a real
   CSV) could be nonzero. This version reports the real `$formCount`, states plainly that
   override-vs-OOB cannot be determined from `lists_with_custom_forms.csv` (it only flags which lists
   have a custom form URL), and asks for manual review of each flagged list.
3. **Security and permissions summary.** The source generated `security-analysis-summary.md` from zero
   data inputs: 100% static boilerplate. This version does not generate that report unless the caller
   supplies an explicit `-PermissionsJson` path. If omitted or unreadable, the report is skipped and a
   `Write-Warning` explains why. When supplied, it states real `Groups`/`BrokenInheritance` counts from
   that file.
4. **Missing-input sections in general.** Every section checks whether its input exists before writing a
   conclusion. If a required input (`webpart_content_extract.json`, `webpart-code-groups.json`,
   `site-chrome.json`, `lists_with_custom_forms.csv`) is absent, the report says
   `Unavailable -- no <file> input was found at <path>` instead of falling back to a hardcoded default
   or narrative.

## Generalization from the source

The source hardcoded a project-specific path-fixup regex (matching one tenant's URL naming quirk) and
assumed one project's report-file layout. This version drops the regex entirely: `-AnalysisDir` is used
as given, and `-AnalysisDir` and `-SiteName` have no project-specific defaults.

## Scripts and related assets

- `scripts/generate-sharepoint-discovery-report-set.ps1`: assembles the six reports from local JSON/CSV
  inputs. It performs local filesystem reads (`Get-Content`, `Import-Csv`) and writes `.md` reports into
  `-AnalysisDir`. It never contacts a tenant.
- `scripts/generate-master-discovery-meta-review.py`: also bundled.
- `master-discovery-meta-review-template.md` (a plugin-level asset, if present) is a separate roll-up template used by
  another skill for a strategic review across a full discovery run. It is not duplicated here.

## Provenance

Ported and corrected from `plugins/sharepoint-migration/scripts/page-migration/generate-discovery-reports.ps1`
in the originating SharePoint migration repository. All hardcoded conclusions not backed by the input
data were removed or made conditional on real computed values, and project-specific path and naming
assumptions were generalized.
