# sharepoint-content-migration

## Purpose

Item-level SharePoint content (list-item data) migration mechanism:
batched migration with retry, and the two-pass lookup-ID re-link technique
that lookup columns require (a lookup field cannot be populated until the
item it targets already exists at the destination with a real ID — so a
first pass migrates content and records source-to-destination ID mappings,
and a second pass resolves lookup fields against that mapping once all
target lists have been fully migrated).

## Non-responsibilities

- **Schema/list/field structure** — owned by `sharepoint-provisioning`.
  This plugin migrates row data into lists that already exist with the
  right shape; it does not create or modify lists, fields, or content
  types.
- **Page/link content** — owned by `sharepoint-page-modernization` and
  `sharepoint-link-remediation` respectively.
- **Any specific source schema's field catalog, skip-type list, or
  matrix/manifest format** — this plugin's `MigrationItem.fields` is
  already caller-shaped (destination field names, ready to write); shaping
  a source record into that dict is the caller's job, not this plugin's.

## Why this plugin exists

Found during the Phase 9 exhaustive source audit
(`temp/phase9-source-audit/file-tracking.json`): a real, generic two-pass
lookup-ID re-link technique and a generic item-level batched-migration-
with-retry mechanism, with no home in any existing plugin — every plugin
built so far provisions schema, converts pages, or repairs links, and none
of them touch list-item content. Name and scope come from
`docs/architecture/complete-plugin-skill-catalog-after-phase-9.md`'s
pre-existing `sharepoint-content-migration` candidate entry, not invented
fresh, per this repository's Rule 0 (check the vision before naming/
placing new capability).

## Write safety

Same three-gate contract as every other write-capable module in this
workbench (`sharepoint-provisioning`'s `list_provisioning.py`,
`sharepoint-link-remediation`'s `link_remediation.py`): planning is pure,
apply is dry-run by default, and a real apply requires both an explicitly
injected `executor` callable and the plan's own confirmation token.

## Scripts

- `scripts/id_mapping.py` — `record_id_mapping`, `resolve_lookup_ids`: pure
  functions over a caller-supplied mapping dict, no file/tenant I/O.
- `scripts/item_migration.py` — `MigrationItem`, `plan_item_migration`,
  `apply_item_migration`: batched migration with per-item retry, gated.

## Skills

- `migrate-sharepoint-list-content` — wraps both modules; documents the
  two-pass sequencing rule (content pass, then lookup-backfill pass,
  self-referential lookups last) as the skill's core contract.

## Installation

```bash
pip install -e plugins/sharepoint-content-migration
```

## Provenance

Generalized from a source-repository content-migration library's
`Read-IdMappings` / `Write-IdMappingBatch` / `Resolve-LookupIdsFromMap`
functions (the ID-mapping mechanism) and `Invoke-ListMigration`'s batched-
migration-with-retry shape (the item-migration mechanism) — see
`temp/phase9-source-audit/file-tracking.json` for the full audit record.
The source's field-catalog-driven, matrix-driven, calendar-aware
per-schema logic was deliberately not ported; only the two reusable
mechanisms were.
