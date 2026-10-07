# Acceptance Criteria: sharepoint-add-list-column

- Skill slug: `sharepoint-add-list-column`.
- Target plugin: `sharepoint-site-build-and-publish`.
- Purpose: Adds a column directly to an existing SharePoint list or library. Use when a column belongs to one list only. Dry-run by default; real writes require -Execute and confirmation token ADD-SPO-LIST-COLUMN.

## Constraints honored

- Dry run by default: without `-Execute` it prints a structured JSON action summary and changes nothing.
- A real write needs `-Execute -ConfirmToken ADD-SPO-LIST-COLUMN`, exactly. The plan's own `confirmation_token` field is a different value. A real run is a live tenant write that the user runs.
- The target list or library must already exist; this adds a column, not a list.
- Read the "Plan JSON shape" block in `scripts/spo-add-list-column.ps1`'s header and do not invent plan keys. When running an installed copy, pass `-ConfigPath` (or `-SiteUrl`, `-ClientId`, `-TenantId`).

## Verification passes

- The dry-run summary lists the column(s) and the target list; afterwards the column exists on that list.
- Focused plugin tests for this skill pass.
