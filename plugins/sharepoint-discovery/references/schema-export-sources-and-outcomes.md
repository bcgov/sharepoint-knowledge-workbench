# Schema exports: where they come from and how absence is reported

## Contents

- [Where the exported schema comes from](#where-the-exported-schema-comes-from)
- [Section statuses](#section-statuses)
- [Comparison semantics](#comparison-semantics)

## Where the exported schema comes from

The schema skills consume an already-exported schema directory tree (`<dir>/summary/lists.json`,
`<dir>/lists/<listname>/fields.json`, and so on; see `ExportLayout` in `schema_export.py`). That tree
is produced by the `sharepoint-collect-sharepoint-inventory` skill running
`collect-sharepoint-schema-export.ps1` against a live tenant. The analysis code in the schema skills
never connects to a tenant itself. Run that collector first if you have no export directory.

## Section statuses

`SectionStatus` distinguishes states a naive tool conflates:

| Status | Meaning |
|---|---|
| `OBSERVED` | Section read, content present |
| `EMPTY` | Read successfully, genuinely nothing there |
| `PARTIAL` | Some sub-items unreadable; recorded, not hidden |
| `UNAVAILABLE` | Export or section missing entirely |

A missing export makes the report `UNAVAILABLE`, never a clean pass. If either side of a comparison is
`UNAVAILABLE`, the report is `UNAVAILABLE`; if either side is anything short of `OBSERVED`, it is
`PARTIAL`.

## Comparison semantics

- Additions, removals and changes are reported per section.
- A list present on only one side is reported, never silently dropped.
- Duplicate keys are surfaced as an ambiguity rather than resolved by guessing.
- Items missing the comparison key are recorded rather than skipped silently.
- `render_markdown` output is deterministic and carries no timestamp or host identifier, so two runs
  over the same inputs diff cleanly.
