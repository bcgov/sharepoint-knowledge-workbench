# Acceptance Criteria: sharepoint-create-list

- Skill slug: `sharepoint-create-list`.
- Target plugin: `sharepoint-site-build-and-publish`.
- Purpose: Creates a new SharePoint custom list (Template 100) using PnP.PowerShell. Use to add a custom list to a site. Dry-run by default; real writes require -Execute and confirmation token PROVISION-SPO-LIST.

## Constraints honored

- Dry run by default: without `-Execute` it prints a structured JSON action summary and changes nothing.
- A real write needs `-Execute -ConfirmToken PROVISION-SPO-LIST`, exactly. The plan's own `confirmation_token` field is a different value. A real run is a live tenant write that the user runs.
- Shares spo-provision-list.ps1 with sharepoint-create-document-library and sharepoint-remove-list, which applies a duplicate-title gate on the plan's blocking_findings. A generic list gets a default Title column with Required set to true (see the contract reference).
- Read the "Plan JSON shape" block in `scripts/spo-provision-list.ps1`'s header and do not invent plan keys. When running an installed copy, pass `-ConfigPath` (or `-SiteUrl`, `-ClientId`, `-TenantId`).

## Verification passes

- The dry-run summary lists the list; afterwards a Get-PnPList re-check finds it.
- Focused plugin tests for this skill pass.
