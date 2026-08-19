# Architecture Overview

This repository is the central public toolkit for the **AI-Assisted Structured Knowledge Workbench**, providing a modular, governed knowledge architecture (**Content + Template + Renderer = Published Output**) and a comprehensive suite of SharePoint discovery, migration, and provisioning tooling.

The ecosystem is composed of **16 independently-installable domain plugins** organized under `plugins/`. Each plugin is self-contained with its own tests, packaging, and skill definitions.

---

## 1. Project Structure

```
sharepoint-knowledge-workbench/
├── plugins/                  # 16 independently-installable domain plugins (see §3)
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
├── docs/
│   ├── vision/               # Architecture specs and vision roadmap
│   ├── use-cases/            # Operational overview of workbench capabilities
│   └── superpowers/          # Core technical designs and reference specifications
├── architecture.md           # This architecture summary
├── INSTALL.md                # Installation and consumer bootstrapping guide
├── DEPENDENCIES.md           # Log of system-level CLI dependencies (pandoc, LibreOffice, PnP.PowerShell)
├── CLAUDE.md / GEMINI.md / AGENTS.md # Behavioral rules and repository engineering policies
├── .claude-plugin/marketplace.json   # Claude Code marketplace catalog
├── symlinks.json             # Symlink tracking manifest
└── skills-lock.json          # Skills installation lockfile
```

Consumer documents, intake files, run outputs, and project-specific tests are managed in separate consumer repositories (e.g. project POC repositories).

---

## 2. High-Level Flow (Content Conversion Pipeline)

The content conversion pipeline runs across four chained domain plugins, gated by explicit human plan confirmation:

```text
Intake Source (.docx / PDF)
        │
        ▼  content-extraction: extract_and_normalize()
        │  Pandoc AST extraction, structural analysis, defect-signal detection
        ▼
Normalized Source Document Contract
        │
        ▼  content-structure-analysis: recommend_from_normalized()
        │  Semantic structure analysis, topic-boundary reasoning, chunking recommendation
        ▼
Draft Conversion Plan ── Requires explicit human confirmation
        │
        ▼  content-assembly: build_canonical_package()
        │  Cleanup pipeline -> structural-anchor reconciliation -> canonical package validation
        ▼
Structured Content Package (manifest.json, validated chunks + sidecars, media/, publication-map.json)
        │
        ▼  content-rendering: render()
        │  Format-specific rendering (multipage-markdown, sharepoint-aspx) with validation
        ▼
Published Output (Human-facing modern pages / ASPX + token-dense agent-optimized digests)
```

---

## 3. Domain Plugins Overview

The workbench is organized into 16 plugins across standard functional prefixes (`content-*`, `sharepoint-*`, `workbench-*`):

### Content Conversion Workstream
1. **`content-extraction`** (1 skill) — Pandoc AST extraction, defect detection, and normalized source document generation.
2. **`content-structure-analysis`** (1 skill) — Semantic structure analysis, topic boundary reasoning, and chunking strategy recommendation.
3. **`content-assembly`** (1 skill) — Cleanup pipeline, chunking, canonical package building, validation, and atomic staging promotion.
4. **`content-rendering`** (7 skills) — Multi-format rendering engine supporting multipage Markdown, SharePoint modern ASPX, and custom rendering templates.

### SharePoint Engineering Workstream
5. **`sharepoint-discovery`** (15 skills) — Read-only analysis and schema auditing of exported classic SharePoint site inventories (navigation, permissions, webpart code, custom forms, calculated columns, choice fields, and schema drift).
6. **`sharepoint-schema-reconciliation`** (4 skills) — Declarative, JSON-schema-driven planning for site columns, content types, lists, and modern calendar provisioning (pure planning, zero tenant I/O).
7. **`sharepoint-provisioning`** (19 skills) — 27 real PnP.PowerShell executors for applying direct CRUD and declarative site-column, list-column, content-type, view, item, list, library, site, branding, hub, navigation, permissions, and taxonomy provisioning plans.
8. **`sharepoint-page-modernization`** (4 skills, 2 agents) — Classic ASPX page analysis, component classification, layout mapping, and modern conversion manifest generation.
9. **`sharepoint-page-modernization-execution`** (4 skills) — PnP.PowerShell executors for single-page conversion, bulk page conversion, cross-site page copying, and post-conversion validation.
10. **`sharepoint-link-remediation`** (5 skills, 2 agents) — Page, document, and field image link extraction, rule-based rewrite remediation, and link-integrity verification.
11. **`sharepoint-content-migration`** (1 skill, 1 agent) — Item-level list item and document library file migration with two-pass lookup-ID resolution.
12. **`sharepoint-migration-planning`** (5 skills, 2 agents) — Migration project setup, site inventory validation, dependency-graph analysis, deployment wave sequencing, and wave script generation.
13. **`sharepoint-content-publication`** (6 skills, 1 agent) — SharePoint tenant publication: package upload, markdown/ASPX publishing, validation, state reconciliation, and rollback.
14. **`sharepoint-spfx-authoring`** (6 skills) — Custom SPFx React web part, Master-Detail dossier scaffolding, solution packaging (`.sppkg`), App Catalog provisioning guidance, and PnP deployment.
15. **`sharepoint-agents-and-skills`** (15 skills) — Lifecycle management (create, update, deploy, verify, rollback, backup, restore) for SharePoint Copilot agents and native AgentAssets skills.

### Workbench Setup & Environment
16. **`workbench-setup`** (5 skills) — Configuration initialization, document workflow setup, environment/network validation, and app registration helpers.

---

## 4. Safety & Execution Contract

Every write-capable module across all plugins enforces a strict three-gate safety model:
1. **Planning is Pure**: Generators, analysis tools, and conversion planners perform zero tenant network I/O and produce reviewable artifacts on disk.
2. **Dry-Run by Default**: Applying any plan defaults to a non-destructive dry-run preview.
3. **Explicit Execution Gate**: Actual tenant writes require an explicit execution flag (`-Execute`) and an operation-specific confirmation token.