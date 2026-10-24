# Library upload orchestration contract

## Ledger columns (`library_migration_ledger.py`)

`FileUrl` (key), `SourceRelativePath`, `Extension`, `SizeBytes`, `Route`, `TargetLibrary`,
`TargetFolder`, `TargetFilename`, `LocalPath`, `Sha256`, `Status`, `Message`.

- Routes: `static-html` (html/htm/aspx; target extension becomes `.html`), `upload`, `skip`
  (extensions passed with `--skip-extensions`).
- Statuses: `PLANNED`, `DOWNLOADED`, `CONVERTED`, `UPLOADED`, `VERIFIED`, `FAILED`, `BLOCKED`,
  `SKIPPED`. Re-running `plan` keeps recorded status, local path, hash and message.
- `BLOCKED` means two files map to one target path (for example `a.aspx` and `a.html`); a human
  decides which wins before any write.

## Path mapping

Target folder = `--target-root` + source path relative to the library, with `\` normalized to `/`.
Library name and root must match the existing target; verify actual casing and title first.

## Responsibilities by callee

| Step | Skill / script | Notes |
| --- | --- | --- |
| Inventory | `sharepoint-collect-site-inventory` | metadata only; user-run |
| Library | `sharepoint-create-document-library` | verify before the first batch |
| Folders | built into `spo-upload-file.ps1` | checks library, creates missing folders parent-first, confirms, per file; no separate step for plain uploads |
| Download | `sharepoint-download-file` bulk wrapper | keep `downloads.csv` |
| Plain upload | `spo-upload-file.ps1` | overwrite is broken upstream; see below |
| html/aspx | `sp-static-aspx-file-migration` | one file per call |

## Known upstream issues

- `spo-provision-list.ps1` may print FAILED after creating a library; re-check with `Get-PnPList`.
- `spo-upload-file.ps1` cannot overwrite (`Set-PnPFileCheckedOut` fails). On DEV only, after
  asserting the config URL is DEV, use a one-off `Add-PnPFile` and record each use.
- Plan paths may mix `\` and `/` on Windows; the ledger plan normalizes them.

## Limits

Per-file downloader reconnects each time; sample first and run large libraries in batches.
Inventory covers files only, not list item metadata or permissions. Relative links inside
migrated pages are not rewritten here; use `sharepoint-extract-links` for disposition.

## Overall tracker

`migration_status_tracker.py` keeps `inventory/portal-workspace-documents/migration-status.csv`: one row per `files.csv` file with DEV/TEST/PROD Status/Updated/Message columns. Ledger commands write through it with `--tracker` (whole ledger synced, idempotent); ledger rows absent from the inventory are appended and reported as `not in inventory`. `observations` emits one `documentLibrary` observation per library for `reconcile-register-recorders.ps1`, the only writer of register recorders.
