# SPFx publish details

## Contents

- [Scope, prerequisites and what the script prints](#scope-prerequisites-and-what-the-script-prints)
- [Examples](#examples)
- [Toolbox visibility and site activation](#toolbox-visibility-and-site-activation)

## Scope, prerequisites and what the script prints

`scripts/publish-spfx-package.ps1` publishes a built `.sppkg` without manual browser upload. It supports Site scope (a site collection App Catalog) and Tenant scope (the tenant App Catalog), and resolves a nested or
flat `config.psd1` schema. Prerequisites: PowerShell 7, `PnP.PowerShell`, an existing `.sppkg`, and a valid `config.psd1` with `Connection.SiteUrl`, `Connection.ClientId`, `Connection.TenantId`, and
`Authentication.TenantAdminUrl` (required for tenant scope). It has no dry-run gate.

It prints upload and publish status, app metadata (`Title`, `Id`, `Deployed`), catalog readback verification via `Get-PnPApp`, and site installation verification when `-Install` is given. If publish fails it exits
non-zero with explicit error output.

## Examples

```powershell
# Site Collection App Catalog, publish and auto-install (recommended)
pwsh -File scripts/publish-spfx-package.ps1 -PackagePath "path/to/solution.sppkg" -Scope Site -Install

# First-time site setup: ensure the App Catalog, publish and install
pwsh -File scripts/publish-spfx-package.ps1 -PackagePath "path/to/solution.sppkg" -Scope Site -EnsureSiteAppCatalog -Install

# Tenant App Catalog with tenant-wide deployment skipped
pwsh -File scripts/publish-spfx-package.ps1 -PackagePath "path/to/solution.sppkg" -Scope Tenant -SkipFeatureDeployment

# Explicit connection overrides (no config.psd1 dependency)
pwsh -File scripts/publish-spfx-package.ps1 -PackagePath "path/to/solution.sppkg" -Scope Site -SiteUrl "https://contoso.sharepoint.com/sites/my-site" -ClientId "<client-id>" -TenantId "<tenant-id>" -Install
```

`-Install` runs `Install-PnPApp` after publication so the app is immediately available in the modern page `+` toolbox without manual Site Contents steps.

## Toolbox visibility and site activation

Deploying to a Site Collection App Catalog (`-Scope Site`) makes the app available to that site collection, but when "Added to all sites" is `No` (the default for site catalogs) the app must also be activated or
installed into the site before its web parts appear in the page editor toolbox:

- PowerShell: `Install-PnPApp -Identity <AppId> -Scope Site`.
- UI: Site Contents > `+ New` > `App` > select the app.
