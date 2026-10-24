# SPO Page Publication Contract

This is the authoritative detailed contract for `sp-page-publish`. Its
skill-local entry point links here; preserve the dry-run, confirmation,
duplicate-page, backup, and inventory handoff gates.

## Contents

- [Package and execution scope](#package-and-execution-scope)
- [Single-page and wave workflows](#single-page-and-wave-workflows)
- [Duplicate-page decisions](#duplicate-page-decisions)
- [Backup before overwrite](#backup-before-overwrite)
- [Environment and commands](#environment-and-commands)
- [Page layout and asset behavior](#page-layout-and-asset-behavior)
- [Recovery and completion boundary](#recovery-and-completion-boundary)

## Package and execution scope

Use this skill only after `sp-dynamic-aspx-page-migration` has produced and
validated a complete package set for the requested wave ID. The migration
agent must check that exact wave-scoped package set first; never substitute
another wave's packages. If the set is unavailable or incomplete, finish the
SP2016 read-only package-recovery path before invoking this publisher.

The package is the sole page and asset definition. The publisher uploads
page-scoped image assets, creates the modern page with `Add-PnPPage`, creates
the mapped section layout, adds source-ordered text web parts with extracted
images kept inline, disables page comments, and publishes the page with
`Set-PnPPage -Publish`. After writing, it verifies the page and each uploaded
asset through PnP read operations.

Dry-run is the default and performs no tenant I/O. Real writes require both
`-Execute` and the exact `PUBLISH-SPO-PAGE` confirmation token, plus an
explicit target configuration. Execution also requires ClientId, TenantId,
and a durable `-OutputPath` for the publication receipt.

## Single-page and wave workflows

- For one page, invoke the managed `scripts/publish-spo-page.ps1` spoke with
  one validated package and the explicitly selected `-ConfigPath`.
- For a wave, invoke the managed `scripts/publish-spo-wave.ps1` spoke with
  `-PackageDirectory`. It validates every package before connecting,
  authenticates once, processes the pages in one PnP session, and writes one
  consolidated receipt. Do not invoke the single-page script in a loop for a
  wave.
- During execution, the wave publisher streams authentication start/success,
  duplicate-preflight progress, each page's `Publishing` status, each
  `PUBLISHED` or `FAILED` result, and final totals. The receipt remains the
  authoritative machine-readable result; a silent console while a page is
  being processed is unexpected.

## Duplicate-page decisions

Before any page write, the wave publisher checks every target page in SPO and
lists all duplicates. It stops with `DUPLICATE_ACTION_REQUIRED` until the
user chooses exactly one action through `-DuplicatePageAction`:

- `Reject`: stop the entire batch; publish nothing.
- `Approve`: publish all pages, including duplicates.
- `Skip`: publish only pages that are not duplicates.

Site Assets are excluded from this duplicate-page gate and may be overwritten.
When run interactively without `-NonInteractive` and without a supplied
decision, the script prompts directly for Reject, Approve, or Skip (full word
or first-letter shorthand). In unattended runs, pass `-NonInteractive`; a
missing decision still blocks with `DUPLICATE_ACTION_REQUIRED` rather than
prompting or guessing.

For an executable run, list and review all duplicate pages before supplying
the user's choice. A wave with duplicates must not proceed merely because
`-Execute` and the token are present.

## Backup before overwrite

Both publisher scripts accept `-ExistingPageBackupAction Backup|NoBackup`;
`Backup` is the default. For an existing page with
`PageMode = OverwriteExisting` (except explicit partial-page recovery),
`Backup-SpoExistingPage` runs before the page is removed. It captures the raw
`.aspx` file, page component/layout JSON, Site Pages list-item metadata,
unique permission role assignments (if any), and already-published
referenced assets into a timestamped directory under
`temp/page-migration-backups/<page>-<timestamp>/` (override with
`-BackupRoot`) and writes a `manifest.json`.

Backup is fail-closed: if a capture step fails, the function throws and the
page is never deleted. The plan/execution summary reports
`Safety.ExistingPageBackup` as `BackupBeforeOverwrite`,
`OverwriteWithoutBackup`, or `NotApplicable`, and reports backup validation.
Use `-ExistingPageBackupAction NoBackup` only when the owner has explicitly
declined a backup for that run.

If `Approve` is selected for existing wave pages and no backup action was
specified, an interactive run asks whether to create a full-recovery backup
(default Yes). With `-NonInteractive`, the safe default is `Backup`.

When `Skip` is selected, existing pages count as wave-complete presence
evidence only; skip is never owner acceptance and never sets the page's
register state to `ACCEPTED`. Only newly published pages are eligible for a
later optional Edit -> Publish cycle. The package page mode still governs the
page-level operation after the decision.

## Environment and commands

Resolve one target environment before publication and pass its configuration
file as `-ConfigPath`:

| Environment | Configuration file (passed explicitly; default location is repository root) |
|---|---|
| `dev` | `config-spo-dev.psd1` (SPO DEV + SP2016 TEST source) |
| `test` | `config-spo-test.psd1` (SPO TEST + SP2016 TEST source) |
| `prod` | `config-spo-prod.psd1` (SPO PROD + SP2016 PROD source) |

Every sp-migration script reads the site, ClientId, TenantId, environment,
and SP2016 source from the selected config. Scripts do not assume a config
location or accept these values as separate arguments. Do not use the
repository-root `config.psd1`, environment variables, or a site URL inferred
from the package. Stop if the selected file is missing or any required
connection value is empty.

Single-page dry run:

```powershell
pwsh -File scripts/publish-spo-page.ps1 `
  -PackagePath "<validated-package-path>" `
  -ConfigPath "<selected-config-spo-environment.psd1>"
```

Wave execution, after package review and the user's explicit duplicate
decision:

```powershell
pwsh -File scripts/publish-spo-wave.ps1 `
  -PackageDirectory "<exact-wave-package-directory>" `
  -ConfigPath "<selected-config-spo-environment.psd1>" `
  -WaveId "<exact-wave-id>" `
  -OutputPath "<durable-publication-receipt-path>" `
  -Execute `
  -ConfirmToken "PUBLISH-SPO-PAGE" `
  -DuplicatePageAction "<Reject|Approve|Skip>"
```

Do not supply `-DuplicatePageAction` until the duplicate-page list has been
reviewed and the user has chosen Reject, Approve, or Skip.

## Page layout and asset behavior

Nested Site Pages targets use the supported slash-delimited PnP page name
format. For `/SitePages/Operations/AuditUnit.aspx`, the publisher calls
`Add-PnPPage -Name "Operations/AuditUnit"`; it does not substitute a root page.

Inline image references receive a server-relative URL including the site
collection path, built from the configured site URL and package-validated
asset path. Legacy image web parts remain supported for older packages but
are not produced by the current Wave 1 planner.

Inventory layouts `Two-Third-Left` and `One-Third-Right` map to the PnP
`TwoColumnLeft` section template. `LeftZone` maps to column 1 and `RightZone`
maps to column 2. For legacy `One-Third-Right` pages whose extracted source
zone is blank, the planner assigns the component to `LeftZone`. Two-column
packages without recognized source-zone metadata are rejected rather than
silently placing content in column 1. Source web-part order and image
position inside each Content Editor HTML payload are preserved.

## Recovery and completion boundary

For the currently observed partial DEV page only, recovery requires the
additional `-RecoverPartialPage` switch. Recovery refuses unless the existing
page has exactly one component; it then adds the remaining package components
in order before publishing and validating.

This capability does not update inventory. After independent publication
validation, hand the verified destination URL to `sp-page-inventory-agent`.
This skill does not update inventory or sync the tracker.
