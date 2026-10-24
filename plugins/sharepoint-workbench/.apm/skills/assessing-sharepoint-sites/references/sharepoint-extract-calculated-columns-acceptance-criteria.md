# Acceptance Criteria: sharepoint-extract-calculated-columns

- Skill slug: `sharepoint-extract-calculated-columns`.
- Target plugin: `sharepoint-site-assessment`.
- Purpose: Finds calculated-type fields across an exported SharePoint schema and reports each one's Formula and any [FieldName]-referenced field names, distinguishing "formula captured" from "formula not present in this export" rather than fabricating one. Use for migration planning, or for dependency analysis before renaming or removing a referenced field. Read-only; consumes an export, never contacts a tenant.

## Constraints honored

- Read-only by construction. Never connect to a tenant and never remove, rename or mutate a field. A test asserts the absence of any remediation or write capability.
- Never fabricate a formula. A calculated field without a `Formula` in the export is still reported, with `formula=None` and an entry in `ambiguities`.
- A missing export is `UNAVAILABLE`, never a clean pass.
- Run from this skill's root with `scripts/` on `sys.path`.

## Verification passes

- Check the report status, and that every column reported without a formula has a matching entry in `ambiguities`. `EMPTY` means no calculated fields were found, not that the export was unreadable.
- Focused plugin tests for this skill pass.
