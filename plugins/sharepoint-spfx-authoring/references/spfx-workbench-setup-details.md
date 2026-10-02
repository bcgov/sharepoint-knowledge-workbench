# Hosted workbench setup details

## Contents

- [Purpose](#purpose)
- [Steps](#steps)
- [Common failures](#common-failures)

## Purpose

Prepare an SPFx project for local development and test it in the hosted SharePoint Online workbench (`/_layouts/15/workbench.aspx`) with debug manifests served from localhost.

## Steps

1. **Confirm tenant profile and connectivity.** Confirm `config.psd1` points at the intended tenant profile, then run the connection check from the `workbench-validate-workbench-environment` skill (`test-spo-connection.ps1`).
2. **Validate the SPFx toolchain:** `pwsh -File scripts/check-spfx-toolchain.ps1`.
3. **Prepare hosted workbench URLs and the dev certificate:**

   ```powershell
   pwsh -File scripts/setup-spfx-workbench.ps1 -ProjectPath "path/to/spfx-solution-root" -SiteUrl "https://contoso.sharepoint.com/sites/test-site"
   ```

   The script verifies project prerequisites, ensures the dev certificate is trusted, and prints the local workbench URL, the hosted workbench URL, and the hosted debug URL (`loadSPFX=true` plus `debugManifestsFile`).
   Options: `-DebugPort` (default 4321), `-SkipToolchainCheck`, `-SkipCertInstall`. It works locally and writes nothing to the tenant.
4. **Start local serve and open the hosted debug URL:**

   ```powershell
   cd path/to/spfx-solution-root
   npx gulp serve --nobrowser
   ```

   In the browser, use the hosted debug URL printed in step 3.

## Common failures

- `ERR_CERT_AUTHORITY_INVALID` on localhost: rerun `setup-spfx-workbench.ps1` without `-SkipCertInstall`.
- The web part does not appear in the hosted workbench: ensure `gulp serve` is still running and the URL includes `debugManifestsFile=https://localhost:4321/temp/manifests.js`.
- 401 or 403 on the hosted workbench: verify the tenant and site URL and rerun the connection check from step 1.
