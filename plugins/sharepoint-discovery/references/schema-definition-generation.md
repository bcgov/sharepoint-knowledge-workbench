# Schema definition generation: statuses, round trip and provenance

## Contents

- [What a definition is](#what-a-definition-is)
- [A degraded export never yields a clean-looking definition](#a-degraded-export-never-yields-a-clean-looking-definition)
- [Round trip](#round-trip)
- [Scripts](#scripts)
- [Provenance](#provenance)

## What a definition is

One JSON-serializable shape describing site columns, content types and lists (each with its own
fields), suitable for later comparison or, in a future separate step, provisioning-input translation.
This skill does not compare two exports (see `sharepoint-audit-schema`) and does not provision or write
anything to a tenant. It transforms one export it is given into a declarative description of that export.

## A degraded export never yields a clean-looking definition

`generate_schema_definition` reuses `schema_export.SectionStatus` rather than inventing a second status
vocabulary. The resulting `SiteSchemaDefinition` carries the source export's overall `status` unchanged:
an `UNAVAILABLE`, `FORBIDDEN`, `FAILED` or `PARTIAL` export produces a definition with that same status
and only the sections that were actually `OBSERVED` populated, never a silently empty-but-`OBSERVED`
definition assembled from a broken export. The same discipline applies per list: a list whose own
`fields.json` could not be read cleanly keeps that list's `fields_status` honest and its `fields` tuple
empty, rather than guessing.

## Round trip

```bash
python3 -c "
import sys; sys.path.insert(0, 'scripts')
from schema_definition import SiteSchemaDefinition
d = SiteSchemaDefinition.load('baseline-schema.json')
print(len(d.site_columns), len(d.content_types), len(d.lists))"
```

## Scripts

- `scripts/schema_export.py`: `load_schema_export`, `SectionStatus`, `SchemaExport` (input to this skill).
- `scripts/schema_definition.py`: `generate_schema_definition`, `FieldDefinition`,
  `ContentTypeDefinition`, `ListDefinition`, `SiteSchemaDefinition`.

## Provenance

New-build work for this repository, not extracted or adapted from any prior source. No provenance
record is needed in the Phase 9 provenance ledger.
