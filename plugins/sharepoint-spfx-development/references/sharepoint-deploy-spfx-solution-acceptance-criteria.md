# Acceptance Criteria: sharepoint-deploy-spfx-solution

- Skill slug: `sharepoint-deploy-spfx-solution`.
- Target plugin: `sharepoint-spfx-development`.
- Purpose: Provides PnP PowerShell runbooks and scripts to upload, deploy and verify .sppkg packages in Site Collection or Tenant App Catalogs. Use after packaging an SPFx solution, to get it into an App Catalog and confirm it is valid and enabled.

## Constraints honored

- `scripts/deploy-spfx-package.ps1` has no dry-run or confirmation gate: it uploads and publishes (`Add-PnPApp`), and with `-Install` installs the app, as soon as it runs. Confirm the target site and package with the user first; the user runs it. `scripts/verify-app-catalog.ps1` is read-only.
- A Site Collection App Catalog must exist on the target site before a site-scope deploy; add it with `-EnsureSiteAppCatalog` or follow `sharepoint-request-site-collection-app-catalog`.
- Requires PowerShell 7 (`pwsh`) and `PnP.PowerShell`. When running an installed copy, pass `-ConfigPath` or explicit `-SiteUrl`, `-ClientId`, `-TenantId`.

## Verification passes

- The App Catalog list shows Enabled = Yes, Valid App Package = Yes and App Package Error Message = No errors, and the SPFx component renders updated data on the page without being re-added.
- Focused plugin tests for this skill pass.
