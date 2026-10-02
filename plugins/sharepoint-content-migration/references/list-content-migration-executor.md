# List content migration: the real PowerShell executor

## Contents

- [What it does](#what-it-does)
- [Create vs. backfill](#create-vs-backfill)
- [Retry and result shape](#retry-and-result-shape)
- [Design seam: the plan JSON](#design-seam-the-plan-json)
- [Provenance](#provenance)

## What it does

`scripts/spo-migrate-list-items.ps1` is the real tenant-facing counterpart to `apply_item_migration`'s injected
`executor(item) -> dest_id`. Python cannot inject a PowerShell callback across the process boundary, so the script
reads a plan JSON file directly and performs the real writes itself. By default it performs no tenant I/O;
`-Execute` plus `-ConfirmToken MIGRATE-SPO-LIST-ITEMS` runs the real writes.

## Create vs. backfill

Per item it chooses one of two real PnP cmdlets, depending on whether the plan entry carries a `dest_id`:

- **No `dest_id`: create.** Non-batched `Add-PnPListItem -List $TargetList -Values $fields -ErrorAction Stop`. It is
  not `-Batch`: `Add-PnPListItem -Batch` does not reliably return a usable lazy item reference in the installed
  PnP.PowerShell version (confirmed against the source migration library's own comment), so the source falls back to
  non-batched per-item creates whenever the real created ID is needed immediately, which this workflow always needs
  for `record_id_mapping`. The created item's `Id` becomes the result's `dest_id`.
- **Present `dest_id`: backfill (update).** `Set-PnPListItem -List $TargetList -Identity <dest_id> -Values $fields
  -ErrorAction Stop`, which is pass 2: writing an already-resolved lookup value onto an item the content pass created.

## Retry and result shape

Every item always gets at least one real write attempt. `-RetryAttempts 0` is clamped to 1, never allowed to silently
skip an item. This mirrors the Python side, where `apply_item_migration` raises `ValueError` for `retry_attempts < 1`.

The result JSON matches `ItemMigrationResult.to_dict()`'s field names exactly (`outcome`, `dry_run`,
`migrated: [{source_id, dest_id}]`, `failed: [{source_id, error}]`), so a Python caller can feed `result.migrated`
straight into `record_id_mapping` without reshaping.

## Design seam: the plan JSON

The plan JSON is not a literal `MigrationItem` / `ItemMigrationPlan` serialization. Neither class defines a
`to_dict()` / `from_dict()` (only `ItemMigrationResult` does), and `MigrationItem` has no `dest_id` field; it carries
only `source_id` and `fields`. The create-vs-backfill distinction therefore has no native representation in the Python
dataclass today. The plan JSON is this script's own contract: a caller producing it from Python augments each item
dict with `dest_id` itself for a backfill entry (the same division of labor `spo-remediate-document-content-links.ps1`
uses for its `remediated_content` augmentation). Giving `MigrationItem` a native optional `dest_id` is undone
follow-up work if a caller wants the Python plan object to represent both passes without manual augmentation.

## Provenance

Generalized from a source-repository content-migration library's `Read-IdMappings`, `Write-IdMappingBatch` and
`Resolve-LookupIdsFromMap` functions and `Invoke-ListMigration`'s batched-migration-with-retry shape, identified in the
Phase 9 exhaustive source audit (`temp/phase9-source-audit/file-tracking.json`, source repository only). The source's
field-catalog-driven, matrix-driven, calendar-aware per-schema logic was deliberately not ported; only the two reusable
mechanisms were.
