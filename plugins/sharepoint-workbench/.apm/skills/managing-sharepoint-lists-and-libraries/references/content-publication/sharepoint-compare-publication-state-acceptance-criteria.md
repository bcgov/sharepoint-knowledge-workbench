# Acceptance Criteria: sharepoint-compare-publication-state

- Skill slug: `sharepoint-compare-publication-state`.
- Target plugin: `sharepoint-site-build-and-publish`.
- Purpose: >-

## Constraints honored

- Read-only and zero tenant I/O; no tenant write of any kind.
- CSV export is the only confirmed evidence-capture mechanism; a Graph or PnP reader is left open.
- Comparison is scoped to the package's own entries.
- Run from this skill's root with `scripts/` on `sys.path`.

## Verification passes

- Check the report for `MISSING_IN_LIBRARY`, `DUPLICATE_IN_LIBRARY`, `FIELD_MISMATCH` and `UNEXPECTED_IN_LIBRARY` (an item present in the library but not in the package). No issues means the library matches the package for the compared fields.
- Focused plugin tests for this skill pass.
