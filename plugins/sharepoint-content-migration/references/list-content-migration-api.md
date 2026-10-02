# List content migration: API, outcomes and sequencing

## Contents

- [Two-pass sequencing](#two-pass-sequencing)
- [Write safety gates](#write-safety-gates)
- [Honest outcomes](#honest-outcomes)
- [Usage](#usage)
- [Scripts](#scripts)

## Two-pass sequencing

Lookup columns cannot be populated in the same pass that creates the items they target: a lookup field stores a
reference to a specific destination item ID, and that ID does not exist until the target item has been migrated.

1. **Content pass.** Migrate every list's non-lookup fields with `plan_item_migration` / `apply_item_migration`. As
   each item migrates, record its source ID to destination ID (and, for its own lookup fields, the raw source IDs they
   reference) with `record_id_mapping`.
2. **Backfill pass.** Once a target list's content pass is complete, use `resolve_lookup_ids` against the accumulated
   mapping to translate each recorded source ID into its destination ID, then write the resolved lookup values back.

Order: parent lists (lookup targets) complete their content pass before any list with a lookup pointing at them starts
its backfill pass. Self-referential lookups (a list whose lookup points at itself) backfill last, after every other item
in that list has been migrated and has a destination ID.

Unresolvable lookup values are quarantined, not dropped. If `resolve_lookup_ids` returns fewer IDs than were requested,
the missing source IDs had no mapping entry: report which ones, and never silently write a shorter list and call it
success.

## Write safety gates

The same three-gate contract as every write-capable module in the workbench:

1. Dry-run is the default. `apply_item_migration(plan)` with no further arguments changes nothing.
2. An executor must be injected. This module ships no tenant transport. Without an `executor(item) -> dest_id`
   callable, a real apply raises `ExecutorRequired`.
3. A confirmation token is required. `dry_run=False` also requires `confirm=plan.confirmation_token`, derived from
   the plan's own content (otherwise `ConfirmationRequired`).

## Honest outcomes

| Outcome | Meaning |
|---|---|
| `OBSERVED` | Every item in the plan migrated successfully |
| `PARTIAL` | Some items migrated, some failed after exhausting retries; both lists populated |
| `FAILED` | Every item failed after exhausting retries |
| `EMPTY` | Nothing to migrate |

## Usage

```python
import sys; sys.path.insert(0, "scripts")
from item_migration import MigrationItem, plan_item_migration, apply_item_migration
from id_mapping import record_id_mapping, resolve_lookup_ids

# Pass 1: content
items = [MigrationItem(source_id=sid, fields=fields) for sid, fields in source_rows]
plan = plan_item_migration(items, batch_size=100)
result = apply_item_migration(plan, executor=my_executor, dry_run=False, confirm=plan.confirmation_token)

mapping = {}
for source_id, dest_id in result.migrated:
    mapping = record_id_mapping(mapping, list_name="TargetList", source_id=source_id, dest_id=dest_id)

# Pass 2: backfill (once every target list's content pass is done)
dest_ids = resolve_lookup_ids(mapping, target_list="TargetList", source_ids=[10322, 14647])
```

## Scripts

- `scripts/id_mapping.py`: `record_id_mapping`, `resolve_lookup_ids`.
- `scripts/item_migration.py`: `MigrationItem`, `plan_item_migration`, `apply_item_migration`, `ExecutorRequired`,
  `ConfirmationRequired`.
- `scripts/provisioning_outcomes.py`: the shared `Outcome` vocabulary, reused from `sharepoint-provisioning`.
- `scripts/spo-migrate-list-items.ps1`: the real PnP executor; see `list-content-migration-executor.md`.
- `scripts/Get-WorkbenchConnectionConfig.ps1`: the shared `config.psd1` reader owned by `workbench-setup`.
