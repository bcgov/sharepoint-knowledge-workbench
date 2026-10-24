# Acceptance Criteria: sharepoint-update-content-type

- Skill slug: `sharepoint-update-content-type`.
- Target plugin: `sharepoint-site-build-and-publish`.
- Purpose: Updates SharePoint content type name, description, group or hidden properties. Use to rename or reclassify a content type. Dry-run by default; real writes require -Execute and confirmation token UPDATE-SPO-CONTENT-TYPES.

## Constraints honored

- Dry run by default: without `-Execute` it prints a structured JSON action summary and changes nothing.
- A real write needs `-Execute -ConfirmToken UPDATE-SPO-CONTENT-TYPES`, exactly. The plan's own `confirmation_token` field is a different value. A real run is a live tenant write that the user runs.
- Changes name, description, group and hidden only; adding or removing field links is sharepoint-create-content-type's job.
- Read the "Plan JSON shape" block in `scripts/spo-update-content-type.ps1`'s header and do not invent plan keys. When running an installed copy, pass `-ConfigPath` (or `-SiteUrl`, `-ClientId`, `-TenantId`).

## Verification passes

- The dry-run summary shows each property change; afterwards the content type carries the new values.
- Focused plugin tests for this skill pass.
