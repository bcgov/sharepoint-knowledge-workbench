# Bulk page migration details

## Contents

- [Per-page subprocess, manifest, resume, throttle](#per-page-subprocess-manifest-resume-throttle)
- [Validates itself when done](#validates-itself-when-done)
- [Not included: link remediation](#not-included-link-remediation)
- [Usage](#usage)
- [Scripts](#scripts)
- [Provenance](#provenance)

## Per-page subprocess, manifest, resume, throttle

Each page is converted by its own `spo-convert-page-to-modern.ps1` subprocess. A failure on one page is recorded and the run continues; it never aborts the batch. Every page's result
(Succeeded, Failed or Skipped, timing, error) is appended to `-ManifestPath` (default `.\run-manifest.csv`) as the run proceeds, so an interruption preserves everything completed so far. Rerun with
`-ResumeFromManifest` to skip pages already recorded as Succeeded. `-ThrottleDelaySeconds` (default 2) runs between pages to avoid SharePoint Online rate limiting. `-PageName` limits a run to one page.

## Validates itself when done

Unless `-SkipValidation` is set, the script calls the validation script against the manifest automatically when the bulk run completes, and exits non-zero if any page fails validation.

## Not included: link remediation

The skill does not rewrite embedded links in converted page bodies, because `ConvertTo-PnPPage` does not do that for same-site conversions. Run the `sharepoint-site-migration` skills separately afterward if the
converted content contains links that need fixing.

## Usage

```bash
# Dry run
pwsh -File scripts/page-modernization-execution/spo-convert-pages-bulk.ps1 -SourceLibrary "ClassicPages"

# Test with a single page first
pwsh -File scripts/page-modernization-execution/spo-convert-pages-bulk.ps1 -SourceLibrary "ClassicPages" -PageName "article.aspx" -Execute -ConfirmToken CONVERT-SPO-PAGES-BULK

# Full bulk run
pwsh -File scripts/page-modernization-execution/spo-convert-pages-bulk.ps1 -SourceLibrary "ClassicPages" -FieldMapping field-mapping.json -Execute -ConfirmToken CONVERT-SPO-PAGES-BULK

# Resume an interrupted run
pwsh -File scripts/page-modernization-execution/spo-convert-pages-bulk.ps1 -SourceLibrary "ClassicPages" -ResumeFromManifest -Execute -ConfirmToken CONVERT-SPO-PAGES-BULK
```

## Scripts

- `scripts/page-modernization-execution/spo-convert-pages-bulk.ps1`: the orchestrator (subprocess per page, manifest, resume, throttle).
- `scripts/page-modernization-execution/spo-convert-page-to-modern.ps1`: the per-page worker (shared with `sharepoint-convert-page-to-modern`).
- `scripts/page-modernization-execution/spo-validate-page-conversion.ps1`: the post-run validator (shared with `sharepoint-validate-page-modernization`).

## Provenance

Generalized from the originating SharePoint migration repository's `link-conversion/Invoke-LinkConversionBulk.ps1`: hardcoded project naming was removed; the subprocess-per-page, manifest, resume and
throttle pattern was kept (it was already generic). The source's own link-repair step was dropped here because that capability belongs to `sharepoint-site-migration`. Source repository only.
