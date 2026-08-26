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

1. **`scaffold-spfx-react-app`**: Generates an enterprise-grade React 17/18 SPFx Web Part boilerplate with Fluent UI, PnPjs v4 cross-site context, Tailwind CSS integration, and self-healing GUID recovery.
2. **`scaffold-spfx-master-detail`**: Generates a consolidated Master-Detail dossier SPFx web part boilerplate (TypeScript, SCSS module, manifest) based on a JSON list layout specification.
3. **`scaffold-spfx-webpart`**: Generic, interactive scaffolding workflow for any new SPFx web part — confirms toolchain dependencies, gathers requirements via clarifying questions, runs the official Yeoman generator, and guides customization of the generated files.
4. **`package-spfx-solution`**: Automates production build verification (`heft test` / `heft package-solution`) and verifies `.sppkg` package integrity.
5. **`deploy-spfx-solution`**: Provides PnP PowerShell runbooks and scripts to upload, deploy, and verify `.sppkg` packages in Site Collection or Tenant App Catalogs.
6. **`publish-spfx-package`**: Publishes a `.sppkg` package directly to Site or Tenant App Catalog using config-driven PnP PowerShell automation and catalog verification.
7. **`request-site-collection-app-catalog`**: Guides the setup and provisioning of Site Collection App Catalogs via ServiceNow ticket requests in BC Gov enterprise tenancy or direct Admin GUI/PnP PowerShell execution in trial/sandbox environments.
8. **`setup-spfx-workbench`**: Prepares and validates a local SPFx project for hosted SharePoint Online `/_layouts/15/workbench.aspx` testing, including toolchain verification, dev certificate trust, and canonical hosted debug URL generation.
9. **`scaffold-spfx-form-customizer`**: Scaffolds, implements, tests, packages, deploys, associates, validates, and rolls back an SPFx Form Customizer extension for custom New/Edit/Display forms with URL-driven related-item lookups (`?SelectedID=...`).

## Reference Documentation

- `references/form-customizer-lifecycle.md` — Complete lifecycle, context APIs, and base class architecture for Form Customizers.
- `references/content-type-association.md` — Content type client-side component properties and PnP PowerShell association mechanics.
- `references/url-driven-related-item-pattern.md` — Parent/child state management, integer lookup ID handling, and OData queries.
- `references/validation-checklist.md` — Comprehensive automated unit and live tenant integration testing checklist.
- `references/SPFX-TAILWIND-INTEGRATION-GUIDE.md` — Tailwind CSS v3/v4 CLI compilation with Heft.
- `references/SPFX-PNPJS-V4-CROSS-SITE-ARCHITECTURE.md` — Hub-and-Spoke data patterns and per-user state isolation.
- `references/SPFX-SELF-HEALING-MIGRATION-GUIDE.md` — Self-healing list title and GUID recovery algorithms.
- `references/MODERN-PAGE-DYNAMIC-FILTERING-GAP.md` — Detailed platform gap analysis and architectural rationale.
- `references/FULL-SETUP-GUIDE.md` — 8-step build, package, upload, and deployment runbook.

## Acknowledgements

Architectural patterns, PnPjs v4 singleton designs, and self-healing migration resilience featured in this plugin incorporate learnings and enterprise patterns established during enterprise SharePoint modernization initiatives.
