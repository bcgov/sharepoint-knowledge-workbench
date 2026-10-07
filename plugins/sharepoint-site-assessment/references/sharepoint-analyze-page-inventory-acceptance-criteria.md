# Acceptance Criteria: sharepoint-analyze-page-inventory

- Skill slug: `sharepoint-analyze-page-inventory`.
- Target plugin: `sharepoint-site-assessment`.
- Purpose: Analyses an exported classic SharePoint page inventory, scoring per-page migration complexity, classifying web-part categories and emitting a disposition hint per page (migrate as-is, rebuild, retire), using a caller-supplied rules file. Use when planning a classic-to-modern migration and deciding which pages are cheap to move. Read-only; consumes an export you provide and never contacts a tenant.

## Constraints honored

- Read-only. The analysis makes no tenant writes and no network access; it reads the export path you name and writes to the output directory you name.
- Rules are data, not code. Complexity weights, category classifications and disposition thresholds all come from the caller-supplied rules JSON. No site-specific judgement is built in.
- A missing input file is `UNAVAILABLE` and creates no output directory; never fabricate defaults to look successful. An empty inventory is `EMPTY`, never a pass.
- Run from this skill's root with `scripts/` on `sys.path`.

## Verification passes

- Check `outcome.status` is `OBSERVED` and the output directory holds the report. Treat any other status as the honest outcome it is; see outcomes.
- Focused plugin tests for this skill pass.
