# Architecture Overview

The **SharePoint Knowledge Workbench** is a public toolkit of reusable skills, tools, and scripts designed for SharePoint engineering, modernization, and knowledge transformation:

1. **SharePoint Site Migration**: Comprehensive discovery, dependency wave planning, link/reference remediation, and content migration.
2. **SharePoint Object Creation**: Automated, declarative provisioning of SharePoint objects (lists, libraries, views, site columns, content types, branding, and permissions).
3. **Publishing & Modifying Content**: Converting classic ASPX pages, authoring/updating modern ASPX pages, publishing Markdown, and managing assets.
4. **Creating & Publishing Copilot Agents & Skills**: Authoring, validating, deploying, and managing SharePoint Copilot agents (`.agent` packages) and native Copilot Studio skills in SharePoint.
5. **Content Maintenance, Continuous Improvement & Document Decomposition**: Breaking huge documents and legacy manuals (Word/PDF) into modular, maintainable subpages in SharePoint, continuously improved and supported by Copilot agents and skills (**Content + Template + Renderer = Published Output**).

The repository is organized into **7 independently installable domain plugins** under `plugins/` (104 skills). Each plugin is one domain with functional groups inside it, and has its own tests, tools, and skill definitions.

---

## 1. Project Directory Structure

```
sharepoint-knowledge-workbench/
├── plugins/                  # 7 domain plugins (see Section 3)
│   ├── sharepoint-workbench-setup/
│   ├── sharepoint-document-conversion/
│   ├── sharepoint-site-assessment/
│   ├── sharepoint-site-build-and-publish/
│   ├── sharepoint-site-migration/
│   ├── sharepoint-copilot-agents-and-skills/
│   └── sharepoint-spfx-development/
├── docs/                     # Guides, design specs, and use cases
├── architecture.md           # This plain-language system overview
├── START-HERE.md             # Quick-start roadmap and status tracker
├── INSTALL.md                # Installation and setup guide
├── DEPENDENCIES.md           # External tools (pandoc, LibreOffice, PowerShell)
└── CLAUDE.md / GEMINI.md / AGENTS.md # Instructions and safety rules for AI agents
```

---

## 2. Document Decomposition & Content Maintenance Pipeline

The core decomposition pipeline breaks huge documents (Word/PDF manuals) into modular, easily maintained SharePoint subpages and AI-ready knowledge packages through four clear steps, gated by human review:

```text
1. Intake Document (.docx / PDF)
   │
   ▼  [sharepoint-document-conversion: content-extract-docx] Extract text, tables, images, and outline
   │
2. Clean Source Document
   │
   ▼  [sharepoint-document-conversion: content-analyze-document-structure] Analyze headings and recommend page boundaries
   │
3. Draft Conversion Plan (Requires Human Approval Before Continuing)
   │
   ▼  [sharepoint-document-conversion: content-assemble-structured-content] Clean formatting, organize media, and create content package
   │
4. Structured Content Package (Standard JSON manifest, clean Markdown chunks, images)
   │
   ▼  [sharepoint-document-conversion: content-render-markdown-pages / content-render-sharepoint-pages] Format into final output
   │
5. Published Output
   ├── A. Human Readers: Modern SharePoint Pages (ASPX / Web)
   └── B. AI Agents: High-density knowledge summaries for Microsoft Copilot & Search
```

---

## 3. What the 7 Plugins Do

Each plugin is one user-facing domain. Functional groups organize its skills; they are not separate plugins. Packages that consolidate several earlier implementations keep each one in its own namespace folder under `scripts/`, `tests/` and `references/` (see each plugin's README) so same-named modules never collide.

1. **`sharepoint-workbench-setup`** (5 skills) — Access, connection, project/document configuration, path resolution and readiness.
   - *Access, project/document configuration, path resolution and readiness*: `workbench-initialize-connection-config`, `workbench-initialize-document-workflow`, `workbench-request-app-registration`, `workbench-resolve-document-paths`, `workbench-validate-sharepoint-connection`

2. **`sharepoint-document-conversion`** (11 skills) — Extract, analyze, assemble, render and editorially review manual content.
   - *Assemble a content package*: `content-assemble-structured-content`
   - *Editorial topic review*: `content-review-manual-topic`
   - *Extract source content*: `content-extract-docx`
   - *Organize topics and pages*: `content-analyze-document-structure`
   - *Render and check output*: `content-compare-rendered-output`, `content-create-markdown-rendering-template`, `content-create-sharepoint-rendering-template`, `content-render-markdown-pages`, `content-render-sharepoint-pages`, `content-validate-rendered-output`, `content-validate-rendering-template`

3. **`sharepoint-site-assessment`** (12 skills, 1 agent) — Read-only inventory, analysis and assessment of classic/modern sites.
   - *Inventory, analysis and read-only assessment*: `sharepoint-analyze-custom-forms`, `sharepoint-analyze-page-inventory`, `sharepoint-analyze-permissions`, `sharepoint-analyze-site-navigation`, `sharepoint-analyze-webpart-behavior`, `sharepoint-audit-managed-metadata`, `sharepoint-audit-onprem-schema-drift`, `sharepoint-collect-site-inventory`, `sharepoint-compare-schema-exports`, `sharepoint-extract-calculated-columns`, `sharepoint-extract-choice-columns`, `sharepoint-generate-assessment-reports`

4. **`sharepoint-site-build-and-publish`** (33 skills, 1 agent) — Create/configure SharePoint objects and publish content (dry-run-first writers).
   - *Create and configure SharePoint objects*: `sharepoint-add-list-column`, `sharepoint-add-list-item`, `sharepoint-apply-provisioning-plan`, `sharepoint-compare-schema-definitions`, `sharepoint-configure-column-formatting`, `sharepoint-configure-library-settings`, `sharepoint-create-content-type`, `sharepoint-create-document-library`, `sharepoint-create-list`, `sharepoint-create-list-view`, `sharepoint-create-site-column`, `sharepoint-detach-content-type`, `sharepoint-generate-schema-definition-from-export`, `sharepoint-plan-column-changes`, `sharepoint-plan-content-type-changes`, `sharepoint-reconcile-calendar-list`, `sharepoint-reconcile-site-schema`, `sharepoint-remove-content-type`, `sharepoint-remove-list`, `sharepoint-remove-list-column`, `sharepoint-remove-site-column`, `sharepoint-scaffold-schema-definition`, `sharepoint-update-content-type`, `sharepoint-update-list-column`, `sharepoint-update-list-settings`, `sharepoint-update-site-column`
   - *Publish and maintain SharePoint content*: `sharepoint-apply-page-publication-plan`, `sharepoint-compare-publication-state`, `sharepoint-copy-page-between-sites`, `sharepoint-plan-page-publication`, `sharepoint-publish-markdown-files`, `sharepoint-remove-publication`, `sharepoint-validate-publication`

5. **`sharepoint-site-migration`** (19 skills, 7 agents) — Plan and run site migration: waves, page modernization, list content, links.
   - *Migrate and modernize SharePoint sites*: `sharepoint-analyze-classic-pages`, `sharepoint-analyze-migration-dependencies`, `sharepoint-audit-list-migration`, `sharepoint-convert-page-library-to-modern`, `sharepoint-convert-page-to-modern`, `sharepoint-create-page-preview`, `sharepoint-extract-links`, `sharepoint-generate-modernization-report`, `sharepoint-initialize-migration-project`, `sharepoint-migrate-list-content`, `sharepoint-normalize-migration-inventory`, `sharepoint-plan-migration-waves`, `sharepoint-plan-page-modernization`, `sharepoint-scaffold-migration-wave-scripts`, `sharepoint-update-links-in-documents`, `sharepoint-update-page-links`, `sharepoint-update-rich-text-image-links`, `sharepoint-validate-link-integrity`, `sharepoint-validate-page-modernization`

6. **`sharepoint-copilot-agents-and-skills`** (14 skills) — Author, deploy, verify, back up and restore Copilot agents and native skills.
   - *Agent and native skill lifecycle*: `sharepoint-backup-agents`, `sharepoint-backup-native-skills`, `sharepoint-create-agent-package`, `sharepoint-create-agent-package-from-template`, `sharepoint-create-agent-template`, `sharepoint-create-native-skill`, `sharepoint-deploy-native-skill`, `sharepoint-inspect-agent-knowledge`, `sharepoint-prepare-agentassets-library`, `sharepoint-restore-agents`, `sharepoint-restore-native-skills`, `sharepoint-undeploy-native-skill`, `sharepoint-update-agent-package`, `sharepoint-verify-native-skill`

7. **`sharepoint-spfx-development`** (10 skills) — SPFx scaffolding, packaging and both delivery routes.
   - *Develop, package, deploy and activate*: `sharepoint-deploy-spfx-solution`, `sharepoint-develop-spfx-form-customizer`, `sharepoint-develop-spfx-listview-command-set`, `sharepoint-package-spfx-solution`, `sharepoint-publish-spfx-package`, `sharepoint-request-site-collection-app-catalog`, `sharepoint-scaffold-spfx-master-detail-webpart`, `sharepoint-scaffold-spfx-react-webpart`, `sharepoint-scaffold-spfx-webpart`, `sharepoint-setup-spfx-hosted-workbench`

Skill names changed in the seven-domain migration; the previous-to-current mapping is in each plugin README ("Previous identities") and in
[`docs/architecture/seven-domain-plugin-skill-catalog.md`](docs/architecture/seven-domain-plugin-skill-catalog.md).

---

## 4. Safety Rules for Live SharePoint Changes

To protect production and DEV environments from accidental changes, most tenant-writing tools follow three safety gates (verified by a static scan of the PowerShell scripts: 42 of 53 detected tenant-writing scripts are fully gated; always check a script's own parameters before running it):

1. **Planning is Safe (Read-Only)**: Planning tools only read data and create local plan files on disk. They never modify a live site.
2. **Dry-Run by Default**: Running a gated script previews what actions would take place without applying them.
3. **Explicit Confirmation Required**: Real changes require the `-Execute` switch and a specific confirmation token (e.g. `-ConfirmToken PROVISION-SPO-LIST`).

**Documented exceptions (these act when run, or use a different gate):**

- `sharepoint-spfx-development`: `deploy-spfx-package.ps1`, `publish-spfx-package.ps1`, `register-listview-command-set.ps1` and `provision-sample-dossier-schema.ps1` have no `-Execute`/token gate; `associate-form-customizer.ps1` and `remove-form-customizer-association.ps1` require `-Execute` but no token. A rename does not add a gate.
- `sharepoint-copilot-agents-and-skills`: `provision-agentassets.ps1` creates the AgentAssets library immediately; `deploy-and-verify-skill.ps1` is gated by `-Execute` only (preflight by default).
- `sharepoint-site-migration`: the preserved consumer-specific repair script in the content-audit folder writes unless `-DryRun` is passed.
- `sharepoint-workbench-setup`: `test-pnp-effective-capability-probe.ps1` is an operator-run live probe.

---

## 5. Built-In Common Skills vs. One-Off Scripts

To keep the codebase clean, consistent, and easy to maintain across multiple projects:

1. **Use Built-In Skills (Avoid Throwaway Scripts)**:
   - Always run the existing parameterized scripts in `plugins/` rather than writing one-off `.ps1` scripts for standard tasks (like creating lists, packaging web parts, or uploading content).
2. **Flexible Parameters & Automatic Configuration**:
   - Every script automatically finds the active `config.psd1` file.
   - You can also pass direct command-line overrides (such as `-SiteUrl "https://..."` or `-ClientId "..."`) to target any site without changing configuration files.
3. **Common Standards Built In**:
   - **SPFx Web Part Packaging**: Automatically compiles CSS (`build:tailwind`) and builds production `.sppkg` packages using local tools.
   - **App Deployment**: Handles site vs. tenant permissions and provides direct 1-click links if manual approval is needed.
   - **List Relationships**: Automatically handles lookup columns (`ApplicationIdId`) and ensures default `Title` fields do not block automated writes.
