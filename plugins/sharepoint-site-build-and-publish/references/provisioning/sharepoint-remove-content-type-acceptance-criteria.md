# Acceptance Criteria: sharepoint-remove-content-type

- Skill slug: `sharepoint-remove-content-type`.
- Target plugin: `sharepoint-site-build-and-publish`.
- Purpose: Deletes a SharePoint content type from the site collection. Use to remove an obsolete content type. Dry-run by default; real writes require -Execute and confirmation token REMOVE-SPO-CONTENT-TYPES.

## Constraints honored

- Dry run by default: without `-Execute` it prints a structured JSON action summary and changes nothing.
- A real write needs `-Execute -ConfirmToken REMOVE-SPO-CONTENT-TYPES`, exactly. The plan's own `confirmation_token` field is a different value. A real run is a live tenant write that the user runs.
- Destructive. The script does not check whether the content type is still in use; detach it from lists first (sharepoint-detach-content-type) and confirm there are no dependents.
- Read the "Plan JSON shape" block in `scripts/spo-remove-content-type.ps1`'s header and do not invent plan keys. When running an installed copy, pass `-ConfigPath` (or `-SiteUrl`, `-ClientId`, `-TenantId`).

## Verification passes

- The dry-run summary names the content type; afterwards it no longer exists in the site collection.
- Focused plugin tests for this skill pass.
