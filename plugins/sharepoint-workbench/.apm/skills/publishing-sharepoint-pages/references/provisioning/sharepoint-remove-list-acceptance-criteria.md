# Acceptance Criteria: sharepoint-remove-list

- Skill slug: `sharepoint-remove-list`.
- Target plugin: `sharepoint-site-build-and-publish`.
- Purpose: Deletes a SharePoint list or document library and re-checks that it is gone, failing loud if it still exists. Use to remove an obsolete list or library. Dry-run by default; real writes require -Execute and confirmation token PROVISION-SPO-LIST.

## Constraints honored

- Dry run by default: without `-Execute` it prints a structured JSON action summary and changes nothing.
- A real write needs `-Execute -ConfirmToken PROVISION-SPO-LIST`, exactly. The plan's own `confirmation_token` field is a different value. A real run is a live tenant write that the user runs.
- Destructive. After deleting, the script re-checks with Get-PnPList and fails loud if the list still exists; never report an unverified delete as success. The duplicate-title gate on the plan's blocking_findings applies.
- Read the "Plan JSON shape" block in `scripts/spo-provision-list.ps1`'s header and do not invent plan keys. When running an installed copy, pass `-ConfigPath` (or `-SiteUrl`, `-ClientId`, `-TenantId`).

## Verification passes

- The dry-run summary names the list; after a real run the re-check finds it gone.
- Focused plugin tests for this skill pass.
