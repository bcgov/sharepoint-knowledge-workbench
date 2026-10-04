# SPFx deploy runbook

## Contents

- [Overview and toolchain](#overview-and-toolchain)
- [Verify the Site Collection App Catalog](#verify-the-site-collection-app-catalog)
- [Upload and deploy through the browser](#upload-and-deploy-through-the-browser)
- [Upload and deploy through PnP PowerShell](#upload-and-deploy-through-pnp-powershell)
- [Verification](#verification)

## Overview and toolchain

Deploys and verifies compiled SPFx solution packages (`.sppkg`) into a SharePoint Online App Catalog (Site Collection App Catalog or Tenant App Catalog). Requires PowerShell 7 (`pwsh`) and the `PnP.PowerShell` module.
The bundled scripts are `scripts/deploy-spfx-package.ps1` and `scripts/verify-app-catalog.ps1`; neither has a dry-run gate (see `spfx-live-write-scripts.md`).

## Verify the Site Collection App Catalog

```powershell
Connect-PnPOnline -Url "https://contoso.sharepoint.com/sites/Demo" -Interactive
Add-PnPSiteCollectionAppCatalog
```

Or use `pwsh -File scripts/verify-app-catalog.ps1 -SiteUrl "<site url>" -AdminUrl "<tenant admin url>"` to confirm it read-only.

## Upload and deploy through the browser

1. Open the App Catalog library: `https://contoso.sharepoint.com/sites/Demo/AppCatalog/AppCatalog`.
2. Drag and drop the `.sppkg` file.
3. Confirm Replace / Overwrite.
4. In the trust panel, select Enable app / Deploy.

## Upload and deploy through PnP PowerShell

```powershell
Connect-PnPOnline -Url "https://contoso.sharepoint.com/sites/Demo" -Interactive
Add-PnPApp -Path "path/to/solution.sppkg" -Publish -Overwrite
```

Or `pwsh -File scripts/deploy-spfx-package.ps1 -PackagePath "path/to/solution.sppkg" -Scope Site -Install`.

## Verification

1. The App Catalog list shows Enabled = Yes, Valid App Package = Yes, and App Package Error Message = No errors.
2. Refresh the target modern page (`.../SitePages/<page>.aspx?SelectedID=1`).
3. Confirm the SPFx component renders updated data without needing to be re-added to the page.
