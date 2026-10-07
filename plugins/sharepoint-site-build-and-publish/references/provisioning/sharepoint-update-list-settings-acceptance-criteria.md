# Acceptance Criteria: sharepoint-update-list-settings

- Skill slug: `sharepoint-update-list-settings`.
- Target plugin: `sharepoint-site-build-and-publish`.
- Purpose: Updates SharePoint list or library title, description and versioning settings using Set-PnPList. Use to rename or reconfigure a list. Dry-run by default; real writes require -Execute and confirmation token UPDATE-SPO-LIST.

## Constraints honored

- Dry run by default: without `-Execute` it prints a structured JSON action summary and changes nothing.
- A real write needs `-Execute -ConfirmToken UPDATE-SPO-LIST`, exactly. The plan's own `confirmation_token` field is a different value. A real run is a live tenant write that the user runs.
- Title, description and versioning only. To recreate a list use sharepoint-remove-list then sharepoint-create-list; to tune approval and draft visibility use sharepoint-configure-library-settings.
- Read the "Plan JSON shape" block in `scripts/spo-update-list.ps1`'s header and do not invent plan keys. When running an installed copy, pass `-ConfigPath` (or `-SiteUrl`, `-ClientId`, `-TenantId`).

## Verification passes

- The dry-run summary shows each setting change; afterwards the list reports the new values.
- Focused plugin tests for this skill pass.
