# Acceptance Criteria: sharepoint-remove-list-column

- Skill slug: `sharepoint-remove-list-column`.
- Target plugin: `sharepoint-site-build-and-publish`.
- Purpose: Removes a list-scoped column from a SharePoint list or library. Use to drop a column from one list only. Dry-run by default; real writes require -Execute and confirmation token REMOVE-SPO-LIST-COLUMN.

## Constraints honored

- Dry run by default: without `-Execute` it prints a structured JSON action summary and changes nothing.
- A real write needs `-Execute -ConfirmToken REMOVE-SPO-LIST-COLUMN`, exactly. The plan's own `confirmation_token` field is a different value. A real run is a live tenant write that the user runs.
- Destructive for that column's data on that list only; remove a site column with sharepoint-remove-site-column instead. The script does not check whether the column is in use.
- Read the "Plan JSON shape" block in `scripts/spo-remove-list-column.ps1`'s header and do not invent plan keys. When running an installed copy, pass `-ConfigPath` (or `-SiteUrl`, `-ClientId`, `-TenantId`).

## Verification passes

- The dry-run summary names the list and column; afterwards the column is gone from that list.
- Focused plugin tests for this skill pass.
