# Acceptance Criteria: sharepoint-update-site-column

- Skill slug: `sharepoint-update-site-column`.
- Target plugin: `sharepoint-site-build-and-publish`.
- Purpose: Updates existing SharePoint site column properties (display name, description, required, choices) using Set-PnPField. Use to change a reusable site column. Dry-run by default; real writes require -Execute and confirmation token UPDATE-SPO-SITE-COLUMNS.

## Constraints honored

- Dry run by default: without `-Execute` it prints a structured JSON action summary and changes nothing.
- A real write needs `-Execute -ConfirmToken UPDATE-SPO-SITE-COLUMNS`, exactly. The plan's own `confirmation_token` field is a different value. A real run is a live tenant write that the user runs.
- Changes the site column everywhere it is used. Removing a choice can affect items that already use it; confirm with the user.
- Read the "Plan JSON shape" block in `scripts/spo-update-site-column.ps1`'s header and do not invent plan keys. When running an installed copy, pass `-ConfigPath` (or `-SiteUrl`, `-ClientId`, `-TenantId`).

## Verification passes

- The dry-run summary shows each property change; afterwards the site column carries the new values.
- Focused plugin tests for this skill pass.
