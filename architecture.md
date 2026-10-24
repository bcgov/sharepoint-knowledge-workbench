# Architecture Overview

The **SharePoint Knowledge Workbench** is a public toolkit of reusable skills, tools, and scripts designed for SharePoint engineering, modernization, and knowledge transformation:

1. **SharePoint Site Migration**: Comprehensive discovery, dependency wave planning, link/reference remediation, and content migration.
2. **SharePoint Object Creation**: Automated, declarative provisioning of SharePoint objects (lists, libraries, views, site columns, content types, branding, and permissions).
3. **Publishing & Modifying Content**: Converting classic ASPX pages, authoring/updating modern ASPX pages, publishing Markdown, and managing assets.
4. **Creating & Publishing Copilot Agents & Skills**: Authoring, validating, deploying, and managing SharePoint Copilot agents (`.agent` packages) and native Copilot Studio skills in SharePoint.
5. **Content Maintenance, Continuous Improvement & Document Decomposition**: Breaking huge documents and legacy manuals (Word/PDF) into modular, maintainable subpages in SharePoint, continuously improved and supported by Copilot agents and skills (**Content + Template + Renderer = Published Output**).

The repository is organized into a **single canonical plugin** under `plugins/sharepoint-workbench/` (`@sharepoint/sharepoint-workbench`), containing **11 cohesive domain skills** and **9 specialized subagents**. Each skill operates via clean modal execution (`SKILL.md` dispatching to dedicated modal playbooks in `references/modes/`) with self-contained resources and **zero cross-directory symlinks**.

---

## 1. Project Directory Structure

```
sharepoint-knowledge-workbench/
├── plugins/
│   └── sharepoint-workbench/             # Single canonical plugin (@sharepoint/sharepoint-workbench)
│       ├── .claude-plugin/plugin.json     # Claude plugin manifest
│       ├── apm.yml                        # APM package manifest
│       ├── plugin.yaml                    # Canonical plugin metadata
│       ├── README.md                      # Plugin documentation & quick-start
│       ├── agents/                        # 9 specialized subagents
│       ├── skills/                        # 11 modal domain skills (see Section 3)
│       └── tests/                         # Pytest test suite (navigation, HTML sanitization, etc.)
├── docs/                                  # Guides, design specs, master migration inventory, and plans
├── apm.yml                                # Root APM package definition
├── architecture.md                        # This plain-language system overview
├── START-HERE.md                          # Quick-start roadmap and status tracker
├── INSTALL.md                             # Installation and setup guide (APM / Marketplace)
├── DEPENDENCIES.md                        # External tools (pandoc, LibreOffice, PowerShell)
└── CLAUDE.md / GEMINI.md / AGENTS.md      # Instructions and safety rules for AI agents
```

---

## 2. Document Decomposition & Content Maintenance Pipeline

The core decomposition pipeline breaks huge documents (Word/PDF manuals) into modular, easily maintained SharePoint subpages and AI-ready knowledge packages through four clear steps, gated by human review:

```text
1. Intake Document (.docx / PDF)
   │
   ▼  [converting-sharepoint-documents: extract mode] Extract text, tables, images, and outline
   │
2. Clean Source Document
   │
   ▼  [converting-sharepoint-documents: analyze mode] Analyze headings and recommend page boundaries
   │
3. Draft Conversion Plan (Requires Human Approval Before Continuing)
   │
   ▼  [converting-sharepoint-documents: assemble mode] Clean formatting, organize media, and create content package
   │
4. Structured Content Package (Standard JSON manifest, clean Markdown chunks, images)
   │
   ▼  [converting-sharepoint-documents: render-markdown / render-sharepoint modes] Format into final output
   │
5. Published Output
   ├── A. Human Readers: Modern SharePoint Pages (ASPX / Web via publishing-sharepoint-pages)
   └── B. AI Agents: High-density knowledge summaries for Microsoft Copilot & Search
```

---

## 3. What the 11 Domain Skills and 9 Subagents Do

The 108 legacy micro-skills are consolidated into 11 domain hubs under `plugins/sharepoint-workbench/skills/`:

1. **`setting-up-sharepoint-workbench`** — Access, connection, project/document configuration, path resolution, and live tenant readiness.
   - *Modes*: `init-connection`, `validate-connection`, `workflow-intake`, `resolve-paths`, `app-registration`
2. **`assessing-sharepoint-sites`** — Read-only inventory, schema drift analysis, calculated/choice columns, custom forms, and assessment reports.
   - *Modes*: `site-inventory`, `schema-compare`, `extract-calculated-columns`, `extract-choice-columns`, `analyze-custom-forms`, `analyze-permissions`, `analyze-navigation`, `analyze-webparts`, `audit-metadata`, `generate-reports`
3. **`converting-sharepoint-documents`** — Extract, analyze, assemble, render, and editorially review manual content.
   - *Modes*: `extract-docx`, `analyze-structure`, `assemble-package`, `render-markdown`, `render-sharepoint`, `validate-rendering`, `editorial-review`
4. **`managing-sharepoint-schema`** — Declarative schema planning and reconciliation (site columns, content types, schema diffing, and scaffolding).
   - *Modes*: `scaffold-schema`, `plan-site-columns`, `plan-content-types`, `diff-schema`, `reconcile-schema`
5. **`managing-sharepoint-lists-and-libraries`** — Provision and manage SharePoint lists, document libraries, list views, and calendar lists.
   - *Modes*: `provision-list`, `provision-library`, `configure-views`, `configure-settings`, `add-column`, `update-column`, `add-item`, `reconcile-calendar`
6. **`managing-sharepoint-navigation`** — Declarative navigation management, Excel/CSV sync, structure extraction, and validation.
   - *Modes*: `extract-navigation`, `plan-navigation`, `provision-navigation`, `validate-navigation`
7. **`publishing-sharepoint-pages`** — Modern page publishing, static ASPX asset upload, Markdown publication, dynamic ASPX page migration, and state verification.
   - *Modes*: `plan-publication`, `publish-modern-page`, `publish-markdown`, `upload-file`, `copy-page`, `verify-publication`, `dynamic-aspx-page-publication`, `static-aspx-file-publication`
8. **`modernizing-sharepoint-pages`** — Classic-to-modern page transformation, web part modernization, page previews, and design-system compliance.
   - *Modes*: `analyze-pages`, `plan-modernization`, `convert-single-page`, `convert-library`, `generate-preview`, `validate-modernization`
9. **`migrating-sharepoint-sites`** — End-to-end migration execution: dependency waves, list content migration, link remediation, and wave scaffolding.
   - *Modes*: `init-migration`, `plan-waves`, `scaffold-waves`, `migrate-content`, `audit-content`, `extract-links`, `rewrite-links`, `validate-links`
10. **`developing-spfx-solutions`** — SPFx solution scaffolding, React/master-detail web parts, extensions, packaging, and App Catalog deployment.
    - *Modes*: `scaffold-webpart`, `scaffold-react`, `scaffold-extension`, `package-solution`, `deploy-catalog`, `publish-direct`
11. **`managing-sharepoint-copilot-agents-and-skills`** — Author, deploy, verify, back up, and restore Copilot Studio agents and native SharePoint skills.
    - *Modes*: `create-agent`, `scaffold-skill`, `apply-template`, `deploy-skill`, `verify-skill-probe`, `backup-restore-agents`, `backup-restore-skills`

### The 9 Specialized Subagents (`plugins/sharepoint-workbench/agents/`)

1. **`sharepoint-discovery-agent`**: Autonomous read-only site discovery and inventory collector.
2. **`sharepoint-deployment-planning-agent`**: Generates dependency-ordered provisioning plans for schema and lists.
3. **`sharepoint-deployment-sequencing-agent`**: Orchestrates safe multi-wave object deployment.
4. **`sharepoint-content-migration-sequencing-agent`**: Plans two-pass content migration with lookup ID resolution.
5. **`sharepoint-modernization-agent`**: Analyzes classic web parts and layout modernization readiness.
6. **`sharepoint-webpart-modernization-analysis-agent`**: Deep inspection of classic web part properties and modern equivalents.
7. **`sharepoint-link-agent`**: Extracts and catalogs all internal, external, and document links.
8. **`sharepoint-link-remediation-analysis-agent`**: Computes deterministic URL rewrite plans with coverage matrices.
9. **`sharepoint-validation-agent`**: Automated pre-flight and post-deployment verification inspector.

---

## 4. Safety Rules for Live SharePoint Changes

### File and Embedded-Link Inventory Workflow

The inventory, download, and link tools provide a safe, read-only discovery workflow:

1. `assessing-sharepoint-sites` (`collect-sharepoint-content-inventory.ps1`): Online/on-prem collector inventories files across libraries and descendant subsites into `files.csv`.
2. `publishing-sharepoint-pages` (`spo-upload-file.ps1` / download modes): Previews or downloads selected files, retaining source URLs in `downloads.csv`.
3. `migrating-sharepoint-sites` (`link-remediation` tools): Python exports links and per-source coverage CSVs from static pages, Office external relationships, and exported modern-page content.
4. `migrating-sharepoint-sites` (`update-page-links`): Builds an explicit source-to-target file map and generates a reviewable link-rewrite plan without writing directly to SharePoint.

Online uses browser-based interactive authentication; on-prem prompts for credentials and never defaults to the current Windows session. All scripts are self-contained within each skill without cross-directory symlinks.

### The Three Safety Gates for Live Tenant Operations

To protect production and DEV environments from accidental changes, tenant-writing tools follow three strict safety gates:

1. **Planning is Safe (Read-Only)**: Planning tools only read data and create local plan files (`plan.json`) on disk. They never modify a live site.
2. **Dry-Run by Default**: Running a script previews what actions would take place without applying them.
3. **Explicit Confirmation Required**: Real changes require the `-Execute` switch and a specific confirmation token:
   - `-ConfirmToken PROVISION-SPO-LIST` (for list/library provisioning)
   - `-ConfirmToken PROVISION-SPO-SCHEMA` (for site columns and content types)
   - `-ConfirmToken PROVISION-SPO-NAV` (for navigation menu changes)
   - `-ConfirmToken PUBLISH-SPO-PAGE` (for modern page publishing)
   - `-ConfirmToken UPLOAD-STATIC-PAGE` (for static ASPX asset uploads)

---

## 5. Built-In Common Skills vs. One-Off Scripts

To keep the codebase clean, consistent, and easy to maintain across multiple projects:

1. **Use Built-In Skills (Avoid Throwaway Scripts)**:
   - Always run the existing parameterized scripts in `plugins/sharepoint-workbench/skills/` rather than writing one-off `.ps1` scripts for standard tasks.
2. **Flexible Parameters & Automatic Configuration**:
   - Every script automatically resolves the active `config.psd1` file.
   - You can also pass direct command-line overrides (`-SiteUrl "https://..."` or `-ClientId "..."`) to target any site without changing configuration files.
3. **Common Standards Built In**:
   - **SPFx Web Part Packaging**: Automatically compiles CSS (`build:tailwind`) and builds production `.sppkg` packages.
   - **App Deployment**: Handles site vs. tenant permissions and provides direct links if manual approval is needed.
   - **List Relationships**: Automatically resolves lookup columns (`ApplicationIdId`) and ensures default fields do not block automated writes.
