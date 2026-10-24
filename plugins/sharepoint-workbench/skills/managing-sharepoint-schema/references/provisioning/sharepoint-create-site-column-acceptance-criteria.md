# Acceptance Criteria: sharepoint-create-site-column

- Skill slug: `sharepoint-create-site-column`.
- Target plugin: `sharepoint-site-build-and-publish`.
- Purpose: Creates new SharePoint site columns across standard or complex types (Text, Choice, Lookup, User, Calculated via Field XML). Use to define a reusable site column. Dry-run by default; real writes require -Execute and confirmation token PROVISION-SPO-SITE-COLUMNS.

## Constraints honored

- Dry run by default: without `-Execute` it prints a structured JSON action summary and changes nothing.
- A real write needs `-Execute -ConfirmToken PROVISION-SPO-SITE-COLUMNS`, exactly. The plan's own `confirmation_token` field is a different value. A real run is a live tenant write that the user runs.
- Supports standard and complex types, including Calculated via Field XML; use Field XML as supplied and do not rewrite formulas.
- Read the "Plan JSON shape" block in `scripts/spo-provision-site-columns.ps1`'s header and do not invent plan keys. When running an installed copy, pass `-ConfigPath` (or `-SiteUrl`, `-ClientId`, `-TenantId`).

## Verification passes

- The dry-run summary lists each column and type; afterwards the site column exists.
- Focused plugin tests for this skill pass.
