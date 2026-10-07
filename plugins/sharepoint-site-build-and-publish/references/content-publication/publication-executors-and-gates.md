# Publication executors, safety gates and platform constraints

## Contents

- [Package-only planning, real executors](#package-only-planning-real-executors)
- [Executor and token table](#executor-and-token-table)
- [Connection and config](#connection-and-config)
- [Raw .aspx upload is blocked](#raw-aspx-upload-is-blocked)
- [Stage 3.4.3 is not a blocker](#stage-343-is-not-a-blocker)
- [Corrections history](#corrections-history)
- [Tests and provenance (source repository only)](#tests-and-provenance-source-repository-only)

## Package-only planning, real executors

The Python modules in this plugin do **planning and validation only** and perform zero tenant I/O: they build a
`PublishPlan`, `RollbackPlan` or `UploadPackage` report that a human or an executor then acts on. The PowerShell
executors are the only scripts that touch a tenant, and every write is gated.

## Executor and token table

| Executor (`scripts/content-publication/`) | Consumes | Does | Write gate |
|---|---|---|---|
| `spo-upload-plan.ps1` | `PublishPlan.to_dict()` JSON | `Add-PnPPage`, `Add-PnPPageTextPart`, `Publish-PnPPage` per action (page creation from pre-rendered HTML fragments); has `-Overwrite` | dry run by default; `-Execute -ConfirmToken UPLOAD-SPO-PLAN` |
| `spo-publish-markdown-plan.ps1` | `PublishPlan` JSON | Verifies the target document library, resolves/creates and confirms the target folder, then calls `Add-PnPFile`; wraps an overwrite in `Set-PnPFileCheckedOut` / `Set-PnPFileCheckedIn -CheckinType MajorCheckIn` | dry run by default; `-Execute -ConfirmToken PUBLISH-SPO-MARKDOWN` |
| `spo-rollback-publication.ps1` | `RollbackPlan` JSON | `Remove-PnPPage` for a `SitePages` target, `Remove-PnPFile` for a document-library target; verifies absence after each removal and throws if a target is still present | dry run by default; `-Execute -ConfirmToken ROLLBACK-SPO-PLAN` |
| `spo-validate-publication-deployment.ps1` | `PublishPlan` JSON | read-only presence check: `Get-PnPPage` for `SitePages`, `Get-PnPFile` for a library target; `OBSERVED`/`EMPTY` per target, overall `PASS`/`FAIL` | none (read-only, always live) |

A wrong or missing token makes an `-Execute` run throw (`-Execute requires -ConfirmToken <TOKEN>.`).

## Connection and config

All four dot-source `Get-WorkbenchConnectionConfig.ps1` and accept `-PlanPath`, `-SiteUrl`, `-ConfigPath`, `-ClientId`,
`-TenantId`, `-TenantAdminUrl`. They use the interactive `Connect-PnPOnline` convention (see the repository's
`sharepoint-ps1-authentication-convention.md` rule).

`-ConfigPath` defaults to three directories above the script (the repository root `config.psd1`). That default does not
resolve from an installed skill, so when running from an installed copy pass `-ConfigPath` explicitly, or pass `-SiteUrl`,
`-ClientId` and `-TenantId` directly.

## Raw .aspx upload is blocked

The Phase 3.0 tenant experiment confirmed that raw `.aspx` file upload to Site Pages is `Access denied` (a platform
boundary, not a permissions gap). The only confirmed-working mechanism is the modern-page API:
`Add-PnPPage` / `Add-PnPPageTextPart` / `Publish-PnPPage`. Plans record source content and target page names, not an upload
mechanism, and any real uploader must follow the page-API pattern (or the equivalent REST calls). Source-repository
evidence: `docs/research/research-experimentation/tenant-discovery/field-note-sharepoint-write-capability-discovery.md`
section 15.

## Stage 3.4.3 is not a blocker

Stage 3.4.3 concerns a separate, not-yet-approved write identity. This plugin's real executors already run today under the
same interactive `Connect-PnPOnline` convention every plugin in the workbench uses, with no Stage 3.4.3 dependency.

## Corrections history

On 2026-08-17 four skills were corrected (kept here so the reasoning is not lost):

- `plan-page-publication` previously said the page-creation API "remains a future, separately-authorized capability once
  Stage 3.4.3 is approved." That was stale: a real executor already existed in `apply-page-publication-plan` and was never a Stage 3.4.3
  write-path question.
- `publish-markdown-files` and `remove-publication` previously said real writes were gated behind Stage
  3.4.3's approved-write-identity decision. That blocker was incorrect; the real gap was that no `Add-PnPFile` or removal
  executor had been built yet, now fixed.

## Tests and provenance (source repository only)

Tests live in the plugin's `tests/content-publication/unit/`, not in an installed skill: `test_sharepoint_publish_plan.py` (publish and rollback
plans, including the cross-document-mismatch rejection), `test_sharepoint_upload.py`, `test_sharepoint_reconcile.py`,
`test_sharepoint_dry_run.py`, `test_sharepoint_package.py`, `test_sharepoint_cli.py`.

`apply-page-publication-plan` derives from the authoritative publication and upload skill (`scripts/upload/upload-modern-page.ps1` and
`upload-modern-page-rest.ps1`); full record in
`docs/reports/phase-9-reusable-sharepoint-plugin-extraction/provenance.md`.
