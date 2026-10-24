# Acceptance Criteria: sharepoint-create-content-type

- Skill slug: `sharepoint-create-content-type`.
- Target plugin: `sharepoint-site-build-and-publish`.
- Purpose: Creates new SharePoint content types, binds field links and attaches content types to target lists. Use to define a reusable content type. Dry-run by default; real writes require -Execute and confirmation token PROVISION-SPO-CONTENT-TYPES.

## Constraints honored

- Dry run by default: without `-Execute` it prints a structured JSON action summary and changes nothing.
- A real write needs `-Execute -ConfirmToken PROVISION-SPO-CONTENT-TYPES`, exactly. The plan's own `confirmation_token` field is a different value. A real run is a live tenant write that the user runs.
- Check that the site columns the plan references exist before a real run (create them with sharepoint-create-site-column first).
- Read the "Plan JSON shape" block in `scripts/spo-provision-content-types.ps1`'s header and do not invent plan keys. When running an installed copy, pass `-ConfigPath` (or `-SiteUrl`, `-ClientId`, `-TenantId`).

## Verification passes

- The dry-run summary lists the content types, field links and target lists; afterwards the content type exists and is attached.
- Focused plugin tests for this skill pass.
