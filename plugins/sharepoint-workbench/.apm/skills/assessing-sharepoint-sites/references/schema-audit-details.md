# Schema audit: environment labels, duplicate fields, scripts

## Contents

- [No environment names built in](#no-environment-names-built-in)
- [Duplicate-field audit](#duplicate-field-audit)
- [Scripts](#scripts)
- [Provenance](#provenance)

## No environment names built in

`compare_schema_exports(left, right, left_label=..., right_label=...)` takes caller-supplied labels.
There is no built-in notion of "prod", "test" or any environment; the source implementation hardcoded
its own pair and that is removed. Which properties are compared is likewise a caller parameter.

## Duplicate-field audit

`find_duplicate_fields` flags two internal names sharing one display name, a common cause of
ambiguous column references. The builtin-column exclusion list is caller-configurable; read-only
columns are excluded; fields without a display name are surfaced rather than guessed.

Read-only by construction. The source script carried a `-Cleanup` switch that deleted fields. No
remediation or write capability exists here, and a test asserts its absence.

## Scripts

- `scripts/schema_export.py`: `load_schema_export`, `SectionStatus`, `ExportLayout`, `SchemaExport`.
- `scripts/schema_diff.py`: `compare_schema_exports`, `compare_named_sets`, `render_markdown`.
- `scripts/duplicate_fields.py`: `find_duplicate_fields`, `DEFAULT_BUILTIN_INTERNAL_NAMES`.

## Provenance

Adapted from `sp-auditing-schema` in the originating SharePoint migration repository. One of that
skill's seven symlinks was broken at the pinned source commit and was not extracted. Source repository
only: `docs/reports/phase-9-reusable-sharepoint-plugin-extraction/provenance.md`.
