# Register Reconciliation Contract

## Contents

- [Supported scope](#supported-scope)
- [Input shape](#input-shape)
- [Report actions](#report-actions)
- [Approval and write gates](#approval-and-write-gates)
- [Page authority](#page-authority)
- [Related skills](#related-skills)

## Supported scope

This skill reconciles `documentLibrary`, `list`, and `webPartMapping` observations against a caller-supplied program register. The canonical script returns a deterministic report with one entry per observation, per-environment and per-action counts, and a SHA-256 fingerprint over the register and observations.

It is intended for batch reconciliation, evidence-freshness review, and a separately requested local register apply. It does not discover tenant content, publish content, export Excel, make exclusion decisions for owners, or create GitHub issues. Credentials and configuration secrets must not be included in reports.

## Input shape

The register JSON exposes `recorders.documentLibraries`, `recorders.lists`, and `recorders.webPartMappings`. A caller may use the project register or a compatible file. The observations input is a JSON array. Each observation includes:

- Required identity and evidence: `objectType`, `recordKey`, `environment`, `status`, `evidenceTimestamp`, and `sourceContentHash`.
- Optional target identity: `packageVersion`, `targetObjectId`, and `targetUrl`.
- Optional attributable evidence: `approvedBy`, `approvedAt`, and `evidenceRefs`.

The caller may pre-filter the observations file by selected task/object IDs (MIG-xxx); the evaluator receives the resulting observations array.

The tuple `(objectType, recordKey, environment)` must be unique in a batch. A blank `recordKey`, duplicate tuple, or blanket/batch approval marker rejects the run rather than merging or guessing.

## Report actions

| Action | Meaning |
|---|---|
| `CREATE` | No matching register record exists for the observation. |
| `UPDATE` | Evidence differs and does not supersede existing accepted evidence. |
| `NOCHANGE` | Evidence matches, or the register already represents the same or a more advanced state. |
| `INVALIDATE` | A source hash, package version, target object ID, or target URL changed and prior evidence needs renewal. The superseded state and evidence are preserved in history. |
| `HELD` | The observation cannot be applied under the approval or page-write boundary. Review `Reasons`. |

`Summary` reports counts by action and environment, including `BlockedPageCount`. These counts are not a percent-complete metric.

## Approval and write gates

- `ACCEPTED` is held with `APPROVAL_REQUIRED` unless `approvedBy` contains an attributable, nonblank human identity. Do not infer approval from publication or verification receipts.
- Any blanket/batch approval flag or `"BLANKET-APPROVE-ALL"`-style sentinel rejects the entire batch.
- Planning mode returns the proposed `Entries`, `Summary`, and `Fingerprint` without writing.
- `-Apply` writes the local register atomically only if the caller supplies the exact `-ExpectedFingerprint` returned by the reviewed plan and the current register and observation contents still match it.
- A mismatch rejects apply. Rerun planning against current inputs; never retry apply with a stale fingerprint.
- Repeated apply with unchanged inputs is idempotent. Evidence invalidation preserves previous target state, receipts, verification, and acceptance in history and requires renewed evidence where applicable.

## Page authority

Every observation with `objectType = "page"` is returned as `HELD` with `G03_BLOCKS_PAGE_WRITES`, counted in `Summary.BlockedPageCount`, and never written, including under `-Apply`. This is a permanent ownership boundary, not a pending integration.

The owners decided against C6/C8 page-store consolidation: `inventory-page.json` remains canonical for page identity and verified destination URLs; `page-migration-tracker.xlsx` is the planning workbook (written only by `page_migration_tracker.py`; the old generated `inventory-page.xlsx` is archived); the program register is canonical only for supported non-page recorders. `scripts/inventory/sync-register-pages.ps1` remains the sole page-record writer. Do not add another page write path here.

## Related skills

- Use `sp-page-inventory` for one independently verified destination URL.
- Use `sp-page-inventory` (`page_migration_tracker.py sync`) for the page tracker workbook.
- Use the page discovery or publication skills for tenant content discovery or publication; this skill only processes local register and observation files.
