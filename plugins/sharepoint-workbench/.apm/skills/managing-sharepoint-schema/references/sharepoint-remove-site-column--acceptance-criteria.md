# Acceptance Criteria: sharepoint-remove-site-column

- Skill slug: `sharepoint-remove-site-column`.
- Target plugin: `sharepoint-site-build-and-publish`.
- Purpose: Deletes a SharePoint site column and reports each column as removed or failed. Use to remove an obsolete site column. Dry-run by default; real writes require -Execute and confirmation token REMOVE-SPO-SITE-COLUMNS.

## Constraints honored

- Dry run by default: without `-Execute` it prints a structured JSON action summary and changes nothing.
- A real write needs `-Execute -ConfirmToken REMOVE-SPO-SITE-COLUMNS`, exactly. The plan's own `confirmation_token` field is a different value. A real run is a live tenant write that the user runs.
- Destructive and site-wide. The script does not check dependents and does not re-check afterwards (it records each column as removed or failed); confirm no content types or lists use the column and verify it is gone.
- Read the "Plan JSON shape" block in `scripts/spo-remove-site-column.ps1`'s header and do not invent plan keys. When running an installed copy, pass `-ConfigPath` (or `-SiteUrl`, `-ClientId`, `-TenantId`).

## Verification passes

- The result lists each column under removed or failed with an outcome of OBSERVED, PARTIAL or FAILED.
- Focused plugin tests for this skill pass.
