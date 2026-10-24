# Acceptance Criteria: sharepoint-apply-provisioning-plan

- Skill slug: `sharepoint-apply-provisioning-plan`.
- Target plugin: `sharepoint-site-build-and-publish`.
- Purpose: The real PnP.PowerShell executors for sharepoint-site-build-and-publish's plan JSON, covering create, update and delete of lists, libraries, site columns and content types, content-type attach and detach, and the granular and site-level operations (views, items, pages, web parts, permissions, navigation, term sets, branding, hub sites, re-index). Use once a plan has been approved, to pick the right executor script. Dry-run by default; every write is gated behind -Execute and an operation-specific -ConfirmToken.

## Constraints honored

- Nothing is written to the tenant unless both `-Execute` and the script's exact `-ConfirmToken` are passed. Without `-Execute` every script prints a dry-run JSON summary, including the exact PnP cmdlet it would run.
- A real run is a live tenant write that the user runs. Never pass a token the user has not confirmed, and never reuse one script's token for another (each token is operation-specific; see the table).
- The plan's own `confirmation_token` field is not the `-ConfirmToken` value.
- Read the "Plan JSON shape" block in the chosen script's header and do not invent keys. When running an installed copy, pass `-ConfigPath` (or `-SiteUrl`, `-ClientId`, `-TenantId`).
- `Get-WorkbenchConnectionConfig.ps1` is a shared helper, not an executor.

## Verification passes

- The dry run names the intended PnP calls and targets; after a real run, check the outcome the script reports and confirm the object on the tenant. Deletions are not all re-checked by the scripts, so verify them.
- Focused plugin tests for this skill pass.
