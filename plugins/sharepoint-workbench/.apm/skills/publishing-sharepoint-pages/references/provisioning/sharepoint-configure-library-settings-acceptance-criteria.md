# Acceptance Criteria: sharepoint-configure-library-settings

- Skill slug: `sharepoint-configure-library-settings`.
- Target plugin: `sharepoint-site-build-and-publish`.
- Purpose: Configures advanced SharePoint document library version limits, content approval and draft visibility settings. Use to tune versioning and approval on a library. Dry-run by default; real writes require -Execute and confirmation token CONFIGURE-SPO-LIBRARY-SETTINGS.

## Constraints honored

- Dry run by default: without `-Execute` it prints a structured JSON action summary and changes nothing.
- A real write needs `-Execute -ConfirmToken CONFIGURE-SPO-LIBRARY-SETTINGS`, exactly. The plan's own `confirmation_token` field is a different value. A real run is a live tenant write that the user runs.
- Limited to version limits, content approval and draft visibility; use sharepoint-update-list-settings for a list's title, description or general versioning.
- Read the "Plan JSON shape" block in `scripts/spo-configure-library-settings.ps1`'s header and do not invent plan keys. When running an installed copy, pass `-ConfigPath` (or `-SiteUrl`, `-ClientId`, `-TenantId`).

## Verification passes

- The dry-run summary lists the settings; afterwards the library reports them.
- Focused plugin tests for this skill pass.
