# Architecture Overview

This repository contains the core toolset for the **AI-Assisted Structured Knowledge Workbench**: pulling content out of Word/PDF documents (where content and formatting are baked together) into structured content that can be rendered into many outputs and ground SharePoint knowledge-access agents, alongside comprehensive SharePoint discovery, migration, and provisioning tooling. Update this file as the repo's actual shape changes — don't let it drift into describing a system that isn't here.

**Decomposed Plugin Architecture:** The ecosystem is modularized into 16 independently-installable domain plugins (§3 below), each installing and running standalone with zero editable-source duplication between them. See `INSTALL.md` for installation and integration options.

## 1. Project Structure

```
sharepoint-knowledge-workbench/
├── plugins/                  # 16 independently-installable domain plugins — see §3
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
│   ├── vision/               # broader-initiative direction: naming, phases, plugin/agent boundaries
│   ├── research/              # product research / field notes feeding the broader vision
│   ├── use-cases/             # per-use-case operational overviews across all workbench capabilities
│   └── superpowers/
│       ├── specs/             # design specs (brainstorming skill output)
│       └── plans/             # implementation plans (writing-plans skill output)
├── architecture.md           # this file
├── INSTALL.md                # comprehensive installation and bootstrapping guide
├── DEPENDENCIES.md           # running log of required external CLI tools (pandoc, LibreOffice, PnP.PowerShell)
├── CLAUDE.md / GEMINI.md / AGENTS.md # behavioral guidelines + repository conventions
├── .claude-plugin/marketplace.json # marketplace manifest for all 16 plugins
├── symlinks.json             # tracking manifest for cross-platform symlinks across all plugins and skills
├── skills-lock.json          # machine-generated install record for .agents/skills/
└── .agents/skills/           # installed skills in the active IDE agent environment
```

Consumer documents, intake files, run outputs, and project-specific tests are managed in separate consumer repositories (e.g. project POC repositories).

This repo **is** a git repository, pushed to `github.com/richfrem/sharepoint-knowledge-workbench` (`main` is the default branch).

## 2. High-Level Flow (Conversion Pipeline)

The conversion pipeline runs across four chained domain plugins, gated by explicit human confirmation:

```
intake/<doc>.docx
        |
        v  content-extraction: extract_and_normalize()
        |     real pandoc extraction, structural analysis, defect-signal detection
        |     -> normalized-source-document
        |
        v  content-structure-analysis: recommend_from_normalized()
        |     topic-boundary reasoning, chunking-strategy recommendation
        |     -> DRAFT ConversionPlan (analysis-plan)
        |
Draft ConversionPlan  ── requires explicit human confirmation before proceeding
        |
        v  content-assembly: build_canonical_package()
        |     cleanup pipeline -> structural-anchor reconciliation/chunking
        |     -> package build -> validate_canonical.py -> atomic promotion
        |
Structured Content Package (manifest.json, validated chunks + sidecars, media/,
publication-map.json for the "grouped" strategy)
        |
        v  content-rendering: render()
        |     CanonicalPackage.load() (full re-validation) -> registered renderer
        |     (multipage-markdown, sharepoint-aspx) -> renderers/validate_rendered.py -> atomic promotion
        |
Published Output (navigable human-facing pages/ASPX + token-dense agent-optimized digests)
```

## 3. Plugins — 16 independently-installable domain plugins

All 16 plugins live directly in this repository under `plugins/` and follow strict standard taxonomy prefixes (`content-*`, `sharepoint-*`, `workbench-*`). Every skill within each plugin carries the matching prefix, ensuring uniform discovery and zero naming collisions.

### Core Conversion Plugins (Phase 4.5)
1. **`content-extraction`** (1 skill) — `content-extract-docx`: Pandoc AST extraction, defect detection, and normalized source document generation.
2. **`content-structure-analysis`** (1 skill) — `content-analyze-document-structure`: Semantic structure analysis, topic boundary reasoning, and chunking strategy recommendation.
3. **`content-assembly`** (1 skill) — `content-assemble-structured-content`: Cleanup pipeline, chunking, canonical package building, validation, and atomic staging promotion.
4. **`content-rendering`** (7 skills) — `content-render-multipage-markdown`, `content-render-sharepoint-aspx`, `content-create-markdown-rendering-template`, `content-create-aspx-rendering-template`, `content-validate-rendering-template`, `content-validate-rendered-output`, `content-compare-rendered-output`.

### SharePoint Engineering Domain Plugins (Phase 9)
5. **`sharepoint-discovery`** (15 skills) — Read-only analysis and schema auditing of exported classic SharePoint site inventories: navigation, permissions, page inventories, webpart code, custom forms, calculated columns, choice fields, and schema drift.
6. **`sharepoint-schema-reconciliation`** (4 skills) — Declarative, JSON-schema-driven planning for site columns, content types, lists, and modern calendar provisioning (pure planning, zero tenant I/O).
7. **`sharepoint-provisioning`** (1 skill: `sharepoint-apply-provisioning-plan`) — 17 real PnP.PowerShell executors for applying declarative site-column, list-column, content-type, view, item, site, branding, hub, navigation, permissions, and taxonomy provisioning plans (gated by `-Execute` and confirmation tokens).
8. **`sharepoint-page-modernization`** (4 skills, 2 agents: `sharepoint-modernization-agent`, `sharepoint-webpart-modernization-analysis-agent`) — Classic ASPX page analysis, component classification, layout mapping, and modern conversion manifest generation.
9. **`sharepoint-page-modernization-execution`** (4 skills) — Real PnP.PowerShell executors for single-page conversion, bulk page conversion, cross-site page copying, and post-conversion validation.
10. **`sharepoint-link-remediation`** (5 skills, 2 agents: `sharepoint-link-agent`, `sharepoint-link-remediation-analysis-agent`) — Page, document, and field image link extraction, rule-based rewrite remediation, and link-integrity verification.
11. **`sharepoint-content-migration`** (1 skill: `sharepoint-migrate-sharepoint-list-content`, 1 agent: `sharepoint-content-migration-sequencing-agent`) — Item-level list item and document library file migration with two-pass lookup-ID resolution.
12. **`sharepoint-migration-planning`** (5 skills, 2 agents: `sharepoint-deployment-planning-agent`, `sharepoint-deployment-sequencing-agent`) — Migration project setup, site inventory validation, dependency-graph analysis, deployment wave sequencing, and wave script generation.
13. **`sharepoint-content-publication`** (6 skills, 1 agent: `sharepoint-validation-agent`) — SharePoint tenant publication: package upload, markdown/ASPX publishing, validation, state reconciliation, and rollback.
14. **`sharepoint-spfx-authoring`** (5 skills) — Custom SPFx web part and Master-Detail dossier scaffolding, solution packaging (`.sppkg`), App Catalog provisioning guidance, and PnP deployment.
15. **`sharepoint-agents-and-skills`** (15 skills) — Lifecycle management (create, update, deploy, verify, rollback, backup, restore) for SharePoint Copilot agents and native AgentAssets skills.

### Workbench Setup Plugin
16. **`workbench-setup`** (5 skills) — `workbench-initialize-workbench-config`, `workbench-initialize-document-workflow`, `workbench-validate-workbench-environment`, `workbench-request-app-registration`, `workbench-resolve-workbench-paths`.

## 4. Safety & Execution Contract

Every write-capable module across all plugins enforces a strict three-gate safety model:
1. **Planning is Pure**: Generators, analysis tools, and conversion planners perform zero tenant network I/O and produce reviewable artifacts on disk.
2. **Dry-Run by Default**: Applying any plan defaults to a non-destructive dry-run preview.
3. **Explicit Execution Gate**: Actual tenant writes require an explicit execution flag (`-Execute`) and a plan-derived confirmation token.

## 5. Dependencies
Tracked in `DEPENDENCIES.md` — external system tools (pandoc, LibreOffice/`soffice`, PnP.PowerShell 2.12.0+). System tools are installed manually and confirmed before introduction.

## 5. What This Repo Deliberately Does Not Have (Phase 1 scope, plus later corrections)

- No running service, no API, no database, no CI/CD pipeline.
- No preview/editing tool for content — SharePoint Online already provides native markdown
  preview/editing at the eventual destination.
- **Corrected 2026-08-08:** an actual publish step into SharePoint and native SharePoint skills
  now exist (`sharepoint-content-publication`, `sharepoint-agents-and-skills`) — this line
  originally said neither was built or authorized; that was true for Phase 1 scope only, and is
  superseded by Phase 6/9 work merged since. Live-tenant I/O beyond opt-in connection testing
  still does not exist anywhere in this workbench — every write-capable module (publication,
  provisioning, content migration, link/field-image remediation) ships zero transport of its own
  and requires an explicitly injected executor/writer plus a plan-derived confirmation token; nothing
  writes to a real tenant autonomously.
- No renderers beyond `multipage_markdown.py` — see
  `docs/research/structured-content-engineering/legacy/future-output-profiles.md` for candidate
  profiles (including dual-target rendering for human visual consumption vs. agent-optimized RAG
  digests).

## 6. Roadmap / Open Questions

- **Phase 1 status:** engineering-complete (enterprise manual conversion proven through the finished plugin pipeline, `convert`/`render` validated, full test suite passing).
- **Phase 2 status:** planned canonical publication contract hardening design.
- **The authoritative full roadmap** — Phase 2 through Phase 8, plus 3.0 and 5.5A/5.5B, each with
  subphases, implementation stages, entry/exit gates, and a full traceability matrix — is
  `docs/vision/master-initiative-plan-workstreams-and-phases.md`. This supersedes the original
  high-level proposal in `docs/vision/ai-assisted-structured-knowledge-workbench-broader-plan.md`
  (kept for historical comparison) with a structure that survived several rounds of external
  review: proposed plugin boundaries (`sharepoint-knowledge`, `structured-content-rendering`,
  `knowledge-evaluation`) and a repository rename are explicitly deferred, not authorized by either
  document alone — each requires its own reviewed decision when its trigger condition is met (see
  the master plan's traceability matrix and extraction-triggers reference).
- Open architecture/governance questions (knowledge-unit boundaries, publication-map reuse,
  metadata authority, security boundaries, stable identity, and more) are tracked in
  `docs/vision/key-unanswered-questions.md`.

## 7. Project Identification

Project Name: sharepoint-knowledge-workbench

Repository: `github.com/richfrem/sharepoint-knowledge-workbench`, `main` branch (default, pushed)

Primary Contact: Richard Fremmerlid

Date of Last Update: 2026-08-02
