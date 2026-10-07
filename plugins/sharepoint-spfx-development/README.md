# sharepoint-spfx-development

SPFx solution scaffolding, Master-Detail component templating, Heft/Webpack build
packaging, App Catalog deployment, Form Customizer association, and list-scoped
ListView Command Set registration for SharePoint Online modern replatforming.

## Overview

Modern SharePoint Online out-of-the-box List Web Parts do not support query parameter filtering (`?SelectedID=...`) and only respond to manual mouse clicks from other native list web parts. When modernizing legacy SharePoint 2013/2016 multi-list briefing or dossier pages (`Author_Briefing.aspx`, `Add_Edit_Authors.aspx`), this plugin provides a consolidated **Master-Detail SPFx Web Part** scaffold to replace multi-web-part classic layouts with a single, high-performance TypeScript component.

## Toolchain & Runtime Requirements

- **Node.js**: LTS version (v18 or v22)
- **SPFx**: 1.20+ (using Heft / Webpack build toolchain)
- **PowerShell**: PowerShell 7 (`pwsh`) with `PnP.PowerShell` for App Catalog deployment
- **Python**: Python 3.8+ (for manifest generator scripts)

## Skills Included

1. **`scaffold-spfx-react-webpart`**: Generates an enterprise-grade React 17/18 SPFx Web Part boilerplate with Fluent UI, PnPjs v4 cross-site context, Tailwind CSS integration, and self-healing GUID recovery.
2. **`scaffold-spfx-master-detail-webpart`**: Generates a consolidated Master-Detail dossier SPFx web part boilerplate (TypeScript, SCSS module, manifest) based on a JSON list layout specification.
3. **`scaffold-spfx-webpart`**: Generic, interactive scaffolding workflow for any new SPFx web part — confirms toolchain dependencies, gathers requirements via clarifying questions, runs the official Yeoman generator, and guides customization of the generated files.
4. **`package-spfx-solution`**: Automates production build verification (`heft test` / `heft package-solution`) and verifies `.sppkg` package integrity.
5. **`deploy-spfx-solution`**: Provides PnP PowerShell runbooks and scripts to upload, deploy, and verify `.sppkg` packages in Site Collection or Tenant App Catalogs.
6. **`publish-spfx-package`**: Publishes a `.sppkg` package directly to Site or Tenant App Catalog using config-driven PnP PowerShell automation and catalog verification.
7. **`request-site-collection-app-catalog`**: Guides the setup and provisioning of Site Collection App Catalogs via service-desk ticket requests in an enterprise tenancy or direct Admin GUI/PnP PowerShell execution in trial/sandbox environments.
8. **`setup-spfx-hosted-workbench`**: Prepares and validates a local SPFx project for hosted SharePoint Online `/_layouts/15/workbench.aspx` testing, including toolchain verification, dev certificate trust, and canonical hosted debug URL generation.
9. **`develop-spfx-form-customizer`**: Scaffolds, implements, tests, packages, deploys, associates, validates, and rolls back an SPFx Form Customizer extension for custom New/Edit/Display forms with URL-driven related-item lookups (`?SelectedID=...`).
10. **`develop-spfx-listview-command-set`**: Scaffolds command-bar extensions that open URLs, act on selected rows, or host SPFx-owned React dialogs and panels; includes list-scoped registration, validation, and rollback.

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

## Skills by functional group

### Develop, package, deploy and activate

- `sharepoint-deploy-spfx-solution` -- Provides PnP PowerShell runbooks and scripts to upload, deploy and verify .sppkg packages in Site Collection or Tenant App Catalogs. Use after packaging an SPFx solution, to get it into an App Catalog and confirm it...
- `sharepoint-develop-spfx-form-customizer` -- Scaffolds, implements, tests, packages, deploys, associates, validates and rolls back an SPFx Form Customizer extension for SharePoint Online list New, Edit and Display forms. Use when a list needs a customized item...
- `sharepoint-develop-spfx-listview-command-set` -- Scaffolds, implements, packages, deploys, registers, validates and removes an SPFx ListView Command Set for SharePoint list or library command bars, including commands that open URLs or host React dialogs and panels....
- `sharepoint-package-spfx-solution` -- Automates production SPFx solution builds using Heft and Webpack and verifies .sppkg package integrity, for both web parts and Form Customizers. Use when an SPFx solution is ready to be built into a deployable package.
- `sharepoint-publish-spfx-package` -- Publishes an SPFx .sppkg package to a Site Collection App Catalog or Tenant App Catalog using config.psd1-driven connection settings, then performs basic catalog verification. Use to publish (and optionally install)...
- `sharepoint-request-site-collection-app-catalog` -- Guides the setup of Site Collection App Catalogs through service-desk ticket requests in an enterprise tenancy, or through direct Admin Center and PnP PowerShell execution in trial and sandbox environments. Use...
- `sharepoint-scaffold-spfx-master-detail-webpart` -- Scaffolds a complete SPFx Master-Detail Web Part boilerplate (TypeScript, SCSS module, manifest) from a JSON list layout specification. Use when modernizing legacy SharePoint 2013/2016 multi-list briefing or dossier...
- `sharepoint-scaffold-spfx-react-webpart` -- Scaffolds an enterprise-grade React 17/18 SPFx Web Part with Fluent UI 8/9, PnPjs v4 cross-site context, Tailwind CSS, self-healing migration GUID recovery and robust state management. Use for complex, interactive...
- `sharepoint-scaffold-spfx-webpart` -- Guides scaffolding of any new, generic SPFx web part from scratch by confirming toolchain dependencies, interactively gathering the web part's requirements (name, purpose, data source, framework, configurability),...
- `sharepoint-setup-spfx-hosted-workbench` -- Sets up and validates a local SPFx web part development workflow that can be tested in the SharePoint Online hosted workbench (workbench.aspx). Use when preparing an SPFx project to debug against localhost manifests...

## Plugin structure

Shared scripts and references live at the plugin root; each skill links to them with file-level symlinks.

```text
sharepoint-spfx-development/
├── .claude-plugin/plugin.json   # Plugin manifest
├── assets/                      # SPFx scaffolding templates
├── references/                  # Shared references and per-skill acceptance criteria
├── scripts/                     # Canonical scaffold, package and deploy scripts
├── skills/<skill-name>/         # SKILL.md plus symlinked scripts/ and references/
├── tests/                       # Plugin tests
├── plugin.json
├── plugin.yaml
└── pyproject.toml
```

## Previous identities

Skill and plugin names changed in the seven-domain migration (issue #6). Old names are not retained as aliases.

| Previous skill | Current skill | Previous plugin |
|---|---|---|
| `sharepoint-scaffold-spfx-form-customizer` | `sharepoint-develop-spfx-form-customizer` | `sharepoint-spfx-authoring` |
| `sharepoint-scaffold-spfx-listview-command-set` | `sharepoint-develop-spfx-listview-command-set` | `sharepoint-spfx-authoring` |
| `sharepoint-scaffold-spfx-master-detail` | `sharepoint-scaffold-spfx-master-detail-webpart` | `sharepoint-spfx-authoring` |
| `sharepoint-scaffold-spfx-react-app` | `sharepoint-scaffold-spfx-react-webpart` | `sharepoint-spfx-authoring` |
| `sharepoint-setup-spfx-workbench` | `sharepoint-setup-spfx-hosted-workbench` | `sharepoint-spfx-authoring` |

## Installing

See the repository [INSTALL.md](../../INSTALL.md). Example:

```text
/plugin install sharepoint-spfx-development@sharepoint-knowledge-workbench
```
