# Acceptance Criteria: sharepoint-update-list-column

- Skill slug: `sharepoint-update-list-column`.
- Target plugin: `sharepoint-site-build-and-publish`.
- Purpose: Updates a list-scoped column's properties on a specific SharePoint list. Use to change one list's column. Dry-run by default; real writes require -Execute and confirmation token UPDATE-SPO-LIST-COLUMN.

## Constraints honored

- Dry run by default: without `-Execute` it prints a structured JSON action summary and changes nothing.
- A real write needs `-Execute -ConfirmToken UPDATE-SPO-LIST-COLUMN`, exactly. The plan's own `confirmation_token` field is a different value. A real run is a live tenant write that the user runs.
- List-scoped: changes one list's column only. Treat a column type change as risky and confirm it with the user.
- Read the "Plan JSON shape" block in `scripts/spo-update-list-column.ps1`'s header and do not invent plan keys. When running an installed copy, pass `-ConfigPath` (or `-SiteUrl`, `-ClientId`, `-TenantId`).

## Verification passes

- The dry-run summary shows each property change; afterwards that list's column carries the new values.
- Focused plugin tests for this skill pass.
