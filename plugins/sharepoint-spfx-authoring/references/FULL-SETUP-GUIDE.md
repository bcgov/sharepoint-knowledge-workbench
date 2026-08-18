# Full Setup Guide — SelectedIdFilter SPFx POC

_lastUpdated: 2026-08-17 — consolidated step-by-step guide covering dependencies through build/upload/test_

## 1. One-Time Environment Setup (Dependencies)

1. **Node.js v22 LTS** (or v18 LTS):
   ```powershell
   winget install CoreyButler.NVMforWindows
   # close/reopen terminal
   nvm install 22
   nvm use 22          # NOTE: per-terminal-session only, re-run in new window
   node --version      # confirm v22.x.x
   ```
2. **Yeoman + SPFx Generator**:
   ```powershell
   npm install -g yo
   npm install -g @microsoft/generator-sharepoint
   ```
3. **PnP PowerShell**:
   - Always use `pwsh` (PowerShell 7) with `PnP.PowerShell` 3.x+ for App Catalog deployment.

## 2. Project Scaffolding

```powershell
md spfx-selectedid-filter
cd spfx-selectedid-filter
yo @microsoft/sharepoint
```
Prompts: solution name = default, component type = `WebPart`, web part name = `SelectedIdFilter`, template = `Minimal`.

## 3. Site Collection App Catalog

Provisioning the app catalog on a site only needs to happen **once per site**.
To enable:
```powershell
Connect-PnPOnline -Url "https://<tenant>.sharepoint.com/sites/<site>" -Interactive
Add-PnPSiteCollectionAppCatalog
```

## 4. Edit Code

File: `spfx-selectedid-filter\src\webparts\selectedIdFilter\SelectedIdFilterWebPart.ts`

## 5. Build

From the project root (`spfx-selectedid-filter\`):
```powershell
npm run build
```
This runs `heft test --clean --production && heft package-solution --production`.
Output package: `spfx-selectedid-filter\sharepoint\solution\spfx-selectedid-filter.sppkg`.

## 6. Upload / Redeploy Package

1. Go to: `https://<tenant>.sharepoint.com/sites/<site>/AppCatalog/AppCatalog`
2. Upload `spfx-selectedid-filter.sppkg`.
3. Select **Enable app** / **Deploy**.

## 7. Test on Page

Page: `https://<tenant>.sharepoint.com/sites/<site>/SitePages/<page>.aspx?SelectedID=3`
- Valid item ID → renders 5-section Master-Detail briefing dossier with photo and action links.

## Important Safety Note on Dependencies

Do **not** run `npm audit fix --force` inside SPFx solutions. Pinned toolchain dependencies (`@rushstack/heft`, `@microsoft/spfx-web-build-rig`) will be broken by forced major-version upgrades.
