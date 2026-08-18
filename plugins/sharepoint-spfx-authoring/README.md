# sharepoint-spfx-authoring

SPFx solution scaffolding, Master-Detail component templating, Heft/Webpack build packaging, and App Catalog deployment helpers for SharePoint Online modern replatforming.

## Overview

Modern SharePoint Online out-of-the-box List Web Parts do not support query parameter filtering (`?SelectedID=...`) and only respond to manual mouse clicks from other native list web parts. When modernizing legacy SharePoint 2013/2016 multi-list briefing or dossier pages (`Appearing_Persons_Briefing.aspx`, `Add_Edit_Persons.aspx`), this plugin provides a consolidated **Master-Detail SPFx Web Part** scaffold to replace multi-web-part classic layouts with a single, high-performance TypeScript component.

## Toolchain & Runtime Requirements

- **Node.js**: LTS version (v18 or v22)
- **SPFx**: 1.20+ (using Heft / Webpack build toolchain)
- **PowerShell**: PowerShell 7 (`pwsh`) with `PnP.PowerShell` for App Catalog deployment
- **Python**: Python 3.8+ (for manifest generator scripts)

## Skills Included

1. **`scaffold-spfx-master-detail`**: Generates a complete Master-Detail dossier SPFx web part boilerplate (TypeScript, SCSS module, manifest) based on a JSON list layout specification.
2. **`package-spfx-solution`**: Automates production build verification (`heft test` / `heft package-solution`) and verifies `.sppkg` package integrity.
3. **`deploy-spfx-solution`**: Provides PnP PowerShell runbooks and scripts to upload, deploy, and verify `.sppkg` packages in Site Collection or Tenant App Catalogs.
4. **`request-site-collection-app-catalog`**: Guides the setup and provisioning of Site Collection App Catalogs via ServiceNow ticket requests in BC Gov enterprise tenancy or direct Admin GUI/PnP PowerShell execution in trial/sandbox environments.


## Reference Documentation

- `references/MODERN-PAGE-DYNAMIC-FILTERING-GAP.md` — Detailed platform gap analysis and architectural rationale.
- `references/FULL-SETUP-GUIDE.md` — 8-step build, package, upload, and deployment runbook.
- `references/SPFX-MASTER-DETAIL-SKILL-PROPOSAL.md` — Original skill extraction specification.
