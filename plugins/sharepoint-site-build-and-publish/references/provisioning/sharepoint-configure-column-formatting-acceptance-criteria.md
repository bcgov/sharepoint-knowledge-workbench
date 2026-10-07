# Acceptance Criteria: sharepoint-configure-column-formatting

- Skill slug: `sharepoint-configure-column-formatting`.
- Target plugin: `sharepoint-site-build-and-publish`.
- Purpose: Applies JSON custom column formatting and custom renderers to SharePoint fields. Use to change how a column displays. Dry-run by default; real writes require -Execute and confirmation token CONFIGURE-SPO-COLUMN-FORMATTING.

## Constraints honored

- Dry run by default: without `-Execute` it prints a structured JSON action summary and changes nothing.
- A real write needs `-Execute -ConfirmToken CONFIGURE-SPO-COLUMN-FORMATTING`, exactly. The plan's own `confirmation_token` field is a different value. A real run is a live tenant write that the user runs.
- Apply the formatting JSON the plan supplies; do not author or alter it.
- Read the "Plan JSON shape" block in `scripts/spo-configure-column-formatting.ps1`'s header and do not invent plan keys. When running an installed copy, pass `-ConfigPath` (or `-SiteUrl`, `-ClientId`, `-TenantId`).

## Verification passes

- The dry-run summary names the fields; afterwards each column renders with its formatter.
- Focused plugin tests for this skill pass.
