# Architecture Overview

The **SharePoint Knowledge Workbench** is a public toolkit of reusable skills, tools, and scripts designed for SharePoint engineering, modernization, and knowledge transformation:

1. **SharePoint Site Migration**: Comprehensive discovery, dependency wave planning, link/reference remediation, and content migration.
2. **SharePoint Object Creation**: Automated, declarative provisioning of SharePoint objects (lists, libraries, views, site columns, content types, branding, and permissions).
3. **Publishing & Modifying Content**: Converting classic ASPX pages, authoring/updating modern ASPX pages, publishing Markdown, and managing assets.
4. **Creating & Publishing Copilot Agents & Skills**: Authoring, validating, deploying, and managing SharePoint Copilot agents (`.agent` packages) and native Copilot Studio skills in SharePoint.
5. **Content Maintenance, Continuous Improvement & Document Decomposition**: Breaking huge documents and legacy manuals (Word/PDF) into modular, maintainable subpages in SharePoint, continuously improved and supported by Copilot agents and skills (**Content + Template + Renderer = Published Output**).

The repository is organized into **16 self-contained plugins** under `plugins/`. Each plugin has its own automated tests, tools, and skill definitions.

---

## 1. Project Directory Structure

```
sharepoint-knowledge-workbench/
├── plugins/                  # 16 standard plugins (see Section 3)
│   ├── content-extraction/
│   ├── content-structure-analysis/
│   ├── content-assembly/
│   ├── content-rendering/
│   ├── sharepoint-discovery/
│   ├── sharepoint-schema-reconciliation/
│   ├── sharepoint-provisioning/
│   ├── sharepoint-page-modernization/
│   ├── sharepoint-page-modernization-execution/
│   ├── sharepoint-link-remediation/
│   ├── sharepoint-content-migration/
│   ├── sharepoint-migration-planning/
│   ├── sharepoint-content-publication/
│   ├── sharepoint-spfx-authoring/
│   ├── sharepoint-agents-and-skills/
│   └── workbench-setup/
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
   ▼  [content-extraction] Extract text, tables, images, and outline
   │
2. Clean Source Document
   │
   ▼  [content-structure-analysis] Analyze headings and recommend page boundaries
   │
3. Draft Conversion Plan (Requires Human Approval Before Continuing)
   │
   ▼  [content-assembly] Clean formatting, organize media, and create content package
   │
4. Structured Content Package (Standard JSON manifest, clean Markdown chunks, images)
   │
   ▼  [content-rendering] Format into final output
   │
5. Published Output
   ├── A. Human Readers: Modern SharePoint Pages (ASPX / Web)
   └── B. AI Agents: High-density knowledge summaries for Microsoft Copilot & Search
```

---

## 3. What the 16 Plugins Do

The tools are grouped into three main areas:

### Area A: Document Conversion (4 Plugins)
1. **`content-extraction`** (1 skill) — Reads `.docx` and PDF files, extracts images/tables, and creates a clean text outline.
2. **`content-structure-analysis`** (1 skill) — Evaluates document sections and recommends how to split large documents into logical web topics.
3. **`content-assembly`** (1 skill) — Cleans up formatting quirks, organizes media files, and bundles content into a structured package.
4. **`content-rendering`** (7 skills) — Converts structured packages into modern SharePoint pages, multipage Markdown, or custom web templates.

### Area B: SharePoint Engineering & Modernization (11 Plugins)
5. **`sharepoint-discovery`** (15 skills) — Safely inspects existing SharePoint sites to discover lists, columns, navigation, permissions, and custom forms.
6. **`sharepoint-schema-reconciliation`** (4 skills) — Creates plans for creating or updating lists, site columns, and content types without touching the live server.
7. **`sharepoint-provisioning`** (19 skills) — Creates and updates SharePoint lists, document libraries, views, site columns, and branding using PowerShell.
8. **`sharepoint-page-modernization`** (4 skills, 2 agents) — Analyzes classic SharePoint pages and plans their conversion to modern layouts.
9. **`sharepoint-page-modernization-execution`** (4 skills) — Converts classic pages to modern SharePoint pages individually or in bulk.
10. **`sharepoint-link-remediation`** (5 skills, 2 agents) — Finds and updates old intranet hyperlinks and image URLs to point to modern destinations.
11. **`sharepoint-content-migration`** (1 skill, 1 agent) — Migrates list items and documents while preserving lookup relationships and attachments.
12. **`sharepoint-migration-planning`** (5 skills, 2 agents) — Calculates dependencies between lists and schedules migration in the correct sequence.
13. **`sharepoint-content-publication`** (6 skills, 1 agent) — Publishes rendered modern pages and Markdown files to SharePoint libraries, with rollback support.
14. **`sharepoint-spfx-authoring`** (7 skills) — Builds, packages, and deploys custom React SPFx web parts (such as the *My Applications* dashboard).
15. **`sharepoint-agents-and-skills`** (15 skills) — Creates, deploys, and manages SharePoint Copilot agents and native AI skills.

### Area C: Setup & Configuration (1 Plugin)
16. **`workbench-setup`** (5 skills) — Configures connection profiles (`config.psd1`), checks network connectivity, and validates permissions.

---

## 4. Safety Rules for Live SharePoint Changes

To protect production and DEV environments from accidental changes, every tool follows three strict safety gates:

1. **Planning is Safe (Read-Only)**: Planning tools only read data and create local plan files on disk. They never modify a live site.
2. **Dry-Run by Default**: Running a script previews what actions would take place without applying them.
3. **Explicit Confirmation Required**: Real changes require the `-Execute` switch and a specific confirmation token (e.g. `-ConfirmToken PROVISION-SPO-LIST`).

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
