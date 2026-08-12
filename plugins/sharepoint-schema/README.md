# sharepoint-schema

Read-only SharePoint schema auditing: compares two exported schema snapshots
for list/content-type/site-column/field variance, audits a single export for
duplicate display names, inventories Choice field option sets, finds
calculated-column formulas and their referenced fields, and generates a
schema definition from an export.

**Zero SharePoint tenant I/O.** No environment names are built in —
`compare_schema_exports` takes caller-supplied labels, not a hardcoded
"prod"/"test" pair.

```
plugins/sharepoint-schema/
├── scripts/
│   ├── schema_export.py         # SectionStatus, ExportLayout, load_schema_export
│   ├── schema_diff.py           # compare_schema_exports, render_markdown
│   ├── schema_definition.py     # schema definition generation from an export
│   ├── choice_fields.py         # inventory_choice_fields, to_overrides_mapping
│   ├── duplicate_fields.py      # find_duplicate_fields
│   └── calculated_columns.py    # find_calculated_columns
├── skills/
│   ├── audit-schema/
│   ├── diff-sharepoint-schema/
│   ├── extract-choice-fields/
│   ├── extract-calculated-columns/
│   └── generate-sharepoint-schema-from-export/
└── tests/
```

## Honest outcomes

`SectionStatus`: `OBSERVED`/`EMPTY`/`PARTIAL`/`UNAVAILABLE`. A missing export
is `UNAVAILABLE`, never a clean pass. A list present on only one side of a
comparison is reported, never silently dropped.

## Deliberate capability removal

The source script this plugin's duplicate-field auditing was adapted from
carried a `-Cleanup` switch that called `Remove-PnPField` — a destructive
tenant write. **That capability was not extracted.**
`test_module_exposes_no_remediation_or_write_capability` enforces its
absence.

## Coverage

`sp-auditing-schema` and `sp-extracting-choices` are extracted as
`audit-schema`/`diff-sharepoint-schema` and `extract-choice-fields`
respectively. `extract-calculated-columns` generalizes
`discover-calculated-columns.ps1` from a sibling migration repository (see
the skill's own provenance note for its hardcoded-default removal). See
`docs/reports/phase-9-reusable-sharepoint-plugin-extraction/
remaining-capability-roadmap.md` for the disposition of every other source
capability, and `provenance.md` for what was extracted and how.

## Install

```bash
pip install -e plugins/sharepoint-schema
python3 -m pytest plugins/sharepoint-schema/tests/ -q
```
