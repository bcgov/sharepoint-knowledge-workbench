# Acceptance Criteria: sharepoint-detach-content-type

- Skill slug: `sharepoint-detach-content-type`.
- Target plugin: `sharepoint-site-build-and-publish`.
- Purpose: Detaches and unlinks a content type from a specific SharePoint list or library. Use to stop a list using a content type without deleting it. Dry-run by default; real writes require -Execute and confirmation token DETACH-SPO-CONTENT-TYPE.

## Constraints honored

- Dry run by default: without `-Execute` it prints a structured JSON action summary and changes nothing.
- A real write needs `-Execute -ConfirmToken DETACH-SPO-CONTENT-TYPE`, exactly. The plan's own `confirmation_token` field is a different value. A real run is a live tenant write that the user runs.
- Detaches from one list only; the site content type stays. Use sharepoint-remove-content-type to delete it from the site collection.
- Read the "Plan JSON shape" block in `scripts/spo-detach-content-type-from-list.ps1`'s header and do not invent plan keys. When running an installed copy, pass `-ConfigPath` (or `-SiteUrl`, `-ClientId`, `-TenantId`).

## Verification passes

- The dry-run summary names the list and content type; afterwards the list no longer offers the content type.
- Focused plugin tests for this skill pass.
