# Schema diff: definition modes, usage and provenance

## Contents

- [Why a separate skill](#why-a-separate-skill)
- [The two modes](#the-two-modes)
- [Usage](#usage)
- [Honest outcomes](#honest-outcomes)
- [Scripts](#scripts)
- [Provenance](#provenance)

## Why a separate skill

This skill compares a declarative `SiteSchemaDefinition` (the shape from
`sharepoint-generate-schema-definition-from-export`), not a raw export. It is distinct from
`sharepoint-compare-schema-exports`'s `compare_schema_exports`, which compares two loaded exports directly.

## The two modes

1. Definition vs. definition: `compare_schema_definitions(left, right, left_label=..., right_label=...)`
   compares two `SiteSchemaDefinition` objects (two hand-authored targets, or one definition at two
   points in time).
2. Definition vs. export: `compare_definition_to_export(definition, export, definition_label=...,
   export_label=...)` answers "what would change if I applied this target definition against this
   current state". It converts the export to a definition via `generate_schema_definition` (a pure,
   existing transform) and reuses `compare_schema_definitions`, so one place owns the declarative
   diff logic.

Both modes are pure, read-only comparisons over local files and objects already in memory. Neither
contacts a tenant, and neither produces an apply or write plan; only a diff report.

## Usage

Definition vs. definition:

```bash
python3 -c "
import sys; sys.path.insert(0, 'scripts')
from schema_definition import SiteSchemaDefinition
from schema_diff import compare_schema_definitions, render_markdown
left = SiteSchemaDefinition.load('baseline-schema.json')
right = SiteSchemaDefinition.load('target-schema.json')
print(render_markdown(compare_schema_definitions(left, right, left_label='baseline', right_label='target')))"
```

Definition vs. export (target vs. current tenant state, already exported):

```bash
python3 -c "
import sys; sys.path.insert(0, 'scripts')
from schema_export import load_schema_export
from schema_definition import SiteSchemaDefinition
from schema_diff import compare_definition_to_export, render_markdown
target = SiteSchemaDefinition.load('target-schema.json')
current = load_schema_export('exports/current', label='current')
print(render_markdown(compare_definition_to_export(target, current, definition_label='target')))"
```

## Honest outcomes

Both modes reuse `SectionStatus` from `schema_export.py` and propagate it as `compare_schema_exports`
does: if either side's `SiteSchemaDefinition.status` is `UNAVAILABLE`, the report is `UNAVAILABLE`
(never a clean pass); if either side is short of `OBSERVED`, it is `PARTIAL`. This holds whether the
degraded side is hand-built or converted from a degraded export, because `generate_schema_definition`
carries the export's honest status through unchanged. The named-set semantics are the same as in the
exports comparison; see `schema-export-sources-and-outcomes.md`.

## Scripts

- `scripts/schema_diff.py`: `compare_schema_definitions`, `compare_definition_to_export` (new in this
  skill), plus the existing `compare_schema_exports`, `compare_named_sets`, `render_markdown`.
- `scripts/schema_definition.py`: `SiteSchemaDefinition`, `generate_schema_definition`.
- `scripts/schema_export.py`: `load_schema_export`, `SectionStatus`, `SchemaExport`.

## Provenance

New-build work for this repository, extending `schema_diff.py` (originally built for the export-vs-
export comparison) with two definition-aware modes. Not extracted from any prior source, and the
existing export-vs-export behavior is unchanged.
