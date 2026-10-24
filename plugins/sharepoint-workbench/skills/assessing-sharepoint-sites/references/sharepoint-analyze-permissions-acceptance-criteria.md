# Acceptance Criteria: sharepoint-analyze-permissions

- Skill slug: `sharepoint-analyze-permissions`.
- Target plugin: `sharepoint-site-assessment`.
- Purpose: Analyses an exported classic SharePoint permissions snapshot, deriving groups, evaluated objects and the subset with broken permission inheritance, to produce a group provisioning worksheet and a broken-inheritance exception report. Use when planning a classic-to-modern migration and you need to know which groups exist and which lists or libraries must be explicitly re-provisioned. Read-only; consumes an export you provide and never contacts a tenant.

## Constraints honored

- Read-only. The analysis makes no tenant writes and no network access; it reads the export path you name and writes to the output directory you name.
- Never fabricate a placeholder group or object list to look successful. A missing export is `UNAVAILABLE` and creates no output directory. No groups or objects is `EMPTY`, never a pass. An input that is neither a JSON array nor object is `FAILED`.
- Accepts two export shapes (flat array, or structured object). The flat shape carries no inheritance flag, so do not claim inheritance state it cannot show.
- Run from this skill's root with `scripts/` on `sys.path`.

## Verification passes

- Check `outcome.status` is `OBSERVED` and the output directory holds the group provisioning worksheet and exception report. Treat any other status as the honest outcome it is; see outcomes.
- Focused plugin tests for this skill pass.
