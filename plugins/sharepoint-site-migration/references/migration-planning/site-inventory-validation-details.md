# Site inventory validation details

## Contents

- [Blocked half vs. implemented half](#blocked-half-vs-implemented-half)
- [Public interface](#public-interface)
- [Expected export shape](#expected-export-shape)
- [Honest outcomes](#honest-outcomes)
- [Provenance](#provenance)

## Blocked half vs. implemented half

- **Real live-tenant discovery**: connecting to the source site and pulling the inventory directly is `sharepoint-collection`'s (Part A's) job. It is
  design-only, `REQUIRES_HUMAN_DECISION`, and not authorized to build (see the source repository's
  `docs/superpowers/specs/2026-08-07-sharepoint-collection-and-orchestration-design.md`).
- **Implemented**: accepting an export directory a human already produced (by hand, or with an existing script run outside this workbench), and
  validating and normalizing its shape for stage 3a. For a collector that does read a live site, see the `sharepoint-collect-site-inventory` skill in
  `sharepoint-site-assessment`.

## Public interface

```python
from inventory_validation import validate_export_directory

result = validate_export_directory(export_dir)
# result.outcome: Outcome.OBSERVED | Outcome.EMPTY | Outcome.UNAVAILABLE | Outcome.FAILED
# result.issues: exact problems found (missing file, malformed JSON, missing fields,
#                a Lookup field with no lookupList target, duplicate list names)
# result.matrix_objects: only on OBSERVED/EMPTY; pass straight to dependency_graph.load_matrix_objects
```

## Expected export shape

A single `site-inventory.json` inside the export directory:
`{"lists": [{"name": ..., "fields": [{"name": ..., "type": ..., "lookupList": "..."}]}]}`, with `lookupList` required only on `type: "Lookup"` fields. The
full JSON Schema is `assets/migration-planning/site-inventory-export-schema.json`.

## Honest outcomes

A missing `site-inventory.json` is `UNAVAILABLE`. Malformed JSON, a missing `lists` or `fields` array, a duplicate list name, or a `Lookup` field with no
`lookupList` target is `FAILED` with the exact issue named. `EMPTY` is returned only when `lists` is present and legitimately empty. The skill never proceeds
silently on an incomplete export and never fabricates a lookup target.

## Provenance

New design work. The source repository's equivalent (`export-sharepoint-inventory-custom.ps1`) is a live-tenant collector, out of scope for this plugin's
zero-tenant-I/O design, so it was not ported.
