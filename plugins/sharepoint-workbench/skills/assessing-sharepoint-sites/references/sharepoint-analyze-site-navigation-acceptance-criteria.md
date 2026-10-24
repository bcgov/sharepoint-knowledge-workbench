# Acceptance Criteria: sharepoint-analyze-site-navigation

- Skill slug: `sharepoint-analyze-site-navigation`.
- Target plugin: `sharepoint-site-assessment`.
- Purpose: Analyses an exported classic SharePoint site navigation tree (top nav and quick launch), flattening it with per-node depth and child counts and computing max-depth statistics, to produce a navigation architecture summary. Use when planning a classic-to-modern migration and sizing navigation before mapping it to hub or global navigation. Read-only; consumes an export you provide and never contacts a tenant.

## Constraints honored

- Read-only. No tenant writes, no network access: it reads the export path you name and writes analysis artifacts to the output directory you name.
- A missing input file is `UNAVAILABLE` and creates no output directory. An export with no navigation nodes is `EMPTY`, never a pass. An input that isn't a JSON object is `FAILED` (the expected shape is `{topNav, quickLaunch}`).
- Run from this skill's root with `scripts/` on `sys.path`. Python is standard library only.

## Verification passes

- Check `outcome.status` is `OBSERVED` and the output directory holds the report. Treat any other status as the honest outcome it is; see outcomes.
- Focused plugin tests for this skill pass.
