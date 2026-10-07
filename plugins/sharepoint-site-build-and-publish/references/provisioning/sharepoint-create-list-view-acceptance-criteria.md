# Acceptance Criteria: sharepoint-create-list-view

- Skill slug: `sharepoint-create-list-view`.
- Target plugin: `sharepoint-site-build-and-publish`.
- Purpose: Creates and configures custom views for SharePoint lists and document libraries. Use to add a filtered or sorted view. Dry-run by default; real writes require -Execute and confirmation token PROVISION-SPO-LIST-VIEW.

## Constraints honored

- Dry run by default: without `-Execute` it prints a structured JSON action summary and changes nothing.
- A real write needs `-Execute -ConfirmToken PROVISION-SPO-LIST-VIEW`, exactly. The plan's own `confirmation_token` field is a different value. A real run is a live tenant write that the user runs.
- A view references columns; confirm they exist on the list before a real run.
- Read the "Plan JSON shape" block in `scripts/spo-provision-list-view.ps1`'s header and do not invent plan keys. When running an installed copy, pass `-ConfigPath` (or `-SiteUrl`, `-ClientId`, `-TenantId`).

## Verification passes

- The dry-run summary lists the view and its columns; afterwards the view exists on the list.
- Focused plugin tests for this skill pass.
