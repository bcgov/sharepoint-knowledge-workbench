# Calculated columns: formula presence, scripts and provenance

## Contents

- [Formula presence is not guaranteed](#formula-presence-is-not-guaranteed)
- [Scripts](#scripts)
- [Provenance](#provenance)

## Formula presence is not guaranteed

Some SharePoint REST exports omit the `Formula` property for calculated fields entirely. The skill
never fabricates a formula to fill that gap. A calculated field found without a `Formula` is still
reported (so the field is not silently dropped), with `formula=None` and an entry in `ambiguities`
explaining that the export did not carry it. Only when a `Formula` string is present does the skill
extract referenced field names, using SharePoint's `[FieldName]` bracket reference syntax. A formula
with no bracketed references (for example one that only calls built-in functions like `TODAY()`)
legitimately yields an empty reference tuple, not an error.

`EMPTY` means the export was read and no calculated fields were found. See
`schema-export-sources-and-outcomes.md` for the status vocabulary.

## Scripts

- `scripts/calculated_columns.py`: `find_calculated_columns`, `CalculatedColumn`,
  `CalculatedColumnsReport`.
- `scripts/schema_export.py`: export loading and the shared status vocabulary.

## Provenance

Generalized from `discover-calculated-columns.ps1` in a sibling SharePoint migration repository,
which scanned a hardcoded, project-specific export path and left `Formula` and referenced fields as
manual-fill placeholders (the REST export it targeted did not capture formulas). This skill
generalizes the scan to any caller-supplied export root via `ExportLayout`/`load_schema_export`, and
extracts referenced fields automatically when the export does carry a `Formula`.
