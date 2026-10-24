# Acceptance Criteria: sharepoint-add-list-item

- Skill slug: `sharepoint-add-list-item`.
- Target plugin: `sharepoint-site-build-and-publish`.
- Purpose: Creates new list items in a SharePoint list with given field values. Use to seed or load items into an existing list. Dry-run by default; real writes require -Execute and confirmation token ADD-SPO-LIST-ITEM.

## Constraints honored

- Dry run by default: without `-Execute` it prints a structured JSON action summary and changes nothing.
- A real write needs `-Execute -ConfirmToken ADD-SPO-LIST-ITEM`, exactly. The plan's own `confirmation_token` field is a different value. A real run is a live tenant write that the user runs.
- Creates items only; it does not create the list or its columns. Use only field values the plan supplies.
- Read the "Plan JSON shape" block in `scripts/spo-add-list-item.ps1`'s header and do not invent plan keys. When running an installed copy, pass `-ConfigPath` (or `-SiteUrl`, `-ClientId`, `-TenantId`).

## Verification passes

- The dry-run summary lists the items; afterwards the items exist with the supplied values.
- Focused plugin tests for this skill pass.
