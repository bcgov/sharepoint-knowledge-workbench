# Acceptance Criteria: sharepoint-publish-spfx-package

- Skill slug: `sharepoint-publish-spfx-package`.
- Target plugin: `sharepoint-spfx-development`.
- Purpose: Publishes an SPFx .sppkg package to a Site Collection App Catalog or Tenant App Catalog using config.psd1-driven connection settings, then performs basic catalog verification. Use to publish (and optionally install) a built package without manual browser upload.

## Constraints honored

- `scripts/publish-spfx-package.ps1` has no dry-run or confirmation gate: it publishes (and with `-Install` installs) as soon as it runs. Confirm the package, scope and target with the user first; the user runs it.
- Requires PowerShell 7, `PnP.PowerShell` and a built `.sppkg`. Connection comes from `config.psd1` (`Connection.SiteUrl`, `ClientId`, `TenantId`; `Authentication.TenantAdminUrl` for tenant scope) or explicit `-SiteUrl`, `-ClientId`, `-TenantId`. When running an installed copy, pass `-ConfigPath` or the explicit parameters.
- A Site Catalog app with "Added to all sites" = No must also be installed into the site (`-Install`) before its web parts appear in the toolbox.

## Verification passes

- The script exits non-zero with explicit errors on failure. On success, confirm `Deployed` and that the app appears in the page `+` toolbox. To change the toolbox name, edit `preconfiguredEntries[0].title.default` and repackage.
- Focused plugin tests for this skill pass.
