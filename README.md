# AI-Assisted Structured Knowledge Workbench

Moving document-centric manuals (Word/PDF) into a content-centric, governed knowledge architecture (**Content + Template + Renderer = Published Output**).

---

## 🎯 Overview

The **AI-Assisted Structured Knowledge Workbench** is a multi-phase initiative designed to transform legacy enterprise manuals into modular, version-controlled, structured Markdown assets. This enables multi-target publishing to human readers (SharePoint/ASPX/Web) and grounded AI RAG agents (Microsoft Copilot, custom SharePoint Agents).

Phase 1 and Phase 2 are **engineering-complete**, demonstrating automated `.docx` analysis, human plan confirmation, structured content chunking, TDD validation, and multipage Markdown rendering on the pilot **CEIS Manual**. Phase 3.0 has completed substantial tenant discovery in real SharePoint Online environments. Phase 4.5 is **complete**: the original combined conversion plugin has been decomposed into four independently installable domain plugins (`source-document-extraction`, `document-structure-analysis`, `structured-content-assembly`, `structured-content-rendering`), each installable and testable standalone. See [start-here.md](start-here.md) for the current branch/merge status and authoritative phase context.

---

## 🗺️ Master Architecture & Workflow

```text
                               +-----------------------------+
                               |     Legacy Intake (.docx)   |
                               +-----------------------------+
                                              |
                                              v  plugins/ (4 domain plugins)
                               +-----------------------------+
                               |   Analysis & Cleanup Plan   |
                               +-----------------------------+
                                              |
                                              v  TDD Validation
                               +-----------------------------+
                               |  Structured Markdown Core   |
                               |  (Single Source of Truth)   |
                               +-----------------------------+
                                              |
                     +------------------------+------------------------+
                     |                                                 |
                     v                                                 v
    +----------------------------------+             +----------------------------------+
    |     Human-Facing Renderer        |             |     Agent-Optimized Renderer     |
    +----------------------------------+             +----------------------------------+
                     |                                                 |
                     v                                                 v
    +----------------------------------+             +----------------------------------+
    | Target A: Formatted Page / ASPX  |             | Target B: Agent Digest / Index   |
    | - Rich layout, images, CSS       |             | - High semantic density          |
    | - Designed for visual reading    |             | - Embedded source link pointers  |
    +----------------------------------+             +----------------------------------+
```

---

## 📚 Key Navigation & Core Documents

### 🚀 Getting Started & Execution Status

- [start-here.md](start-here.md) — **Authoritative Resume & Status Document**. Read this first for active state, phase gates, and workflow guidelines.
- [architecture.md](architecture.md) — System structure, directory maps, and technical component flow.
- [CLAUDE.md](CLAUDE.md) / [GEMINI.md](GEMINI.md) / [AGENTS.md](AGENTS.md) — Agent coding conventions, TDD rules, and project guidelines.
- [DEPENDENCIES.md](DEPENDENCIES.md) — Running log of external CLI requirements, including Pandoc and LibreOffice.

### 🏛️ Vision & Master Initiative Roadmap

- [Master Initiative Plan and Traceability Matrix](docs/vision/master-initiative-plan-workstreams-and-phases.md) — Authoritative master plan, workstreams, phases, and traceability.
- [Vision Overview](docs/vision/README.md) — Vision overview and change-control rules.
- [Future-Phase Planning Index](docs/superpowers/FUTURE-PHASE-PLANNING-INDEX.md) — Forward-phase specifications and plan scaffolds.

### 🔬 Research & Empirical Evidence

- [Research Index and Decision Guides](docs/research/README.md) — Comprehensive research navigation.
- [Dual-Target Rendering Model](docs/research/publication-delivery/dual-target-rendering-concept.md) — Human-facing versus agent-optimized output.
- [AgentAssets Skill-Creation Field Note](docs/research/sharepoint-platforms-capabilities/field-note-agentassets-skill-creation.md) — Empirical Phase 3.0 SharePoint `AgentAssets` discovery findings.
- [Skill Runtime Decision Guide](docs/research/architecture-design-patterns/skill-runtime-decision-guide-sharepoint-vs-github-copilot.md) — Decision framework for SharePoint-native versus GitHub-repository skills.

---

## 📊 Key Architectural Diagrams

The repository maintains formal Mermaid architecture diagrams in [docs/diagrams/](docs/diagrams/README.md):

1. **[Overall System Architecture](docs/diagrams/high-level.mmd)** — End-to-end view from `.docx` intake to structured storage and multi-runtime agent delivery.
2. **[Phase 1 Conversion Pipeline](docs/diagrams/01-phase1-overview.mmd)** — Stage breakdown (`analyze` → `confirm` → `convert` → `render`).
3. **[Document Analysis & Plan Confirmation](docs/diagrams/02-analyze-and-confirm.mmd)** — Interactive human-in-the-loop plan confirmation.
4. **[Structured Content Creation](docs/diagrams/03-create-canonical-content.mmd)** — Pandoc AST cleanup, media extraction, structural anchor resolution, and packaging.
5. **[Render & Multi-Target Generation](docs/diagrams/04-generate-and-render.mmd)** — Multipage Markdown and dual-target rendering engine.
6. **[Validation & Atomic Promotion](docs/diagrams/05-validation-and-evidence.mmd)** — Content-loss prevention, schema validation, and atomic staging promotion.

---

## 🛠️ Active Implementation & Tools

- **Core Conversion Plugins** (Phase 4.5, `plugins/`): four independently installable domain plugins
  - `source-document-extraction` — Structural analysis, defect detection, and normalized-source-document extraction.
  - `document-structure-analysis` — Topic-boundary reasoning, chunking-strategy recommendation, and draft conversion-plan construction.
  - `structured-content-assembly` — Pandoc AST postprocessing, chunking, structured-package build, and validation.
  - `structured-content-rendering` — Multi-target publication rendering and validation.
- **SharePoint Domain Plugins** (Phase 9, `plugins/`): independently installable, extracted/
  generalized from a separate SharePoint migration repository per an exhaustive 505-file source
  audit (`temp/phase9-source-audit/file-tracking.json`)
  - `sharepoint-discovery` — read-only analysis of exported classic SharePoint inventories.
  - `sharepoint-schema` — read-only schema variance/duplicate-field/choice-field auditing.
  - `sharepoint-provisioning` — declarative, gated site-column/content-type/list/calendar provisioning.
  - `sharepoint-page-modernization` — classic-to-modern page conversion manifest generation.
  - `sharepoint-link-remediation` — page/document/field-content link extraction, remediation, validation.
  - `sharepoint-content-migration` — item-level content migration with two-pass lookup-ID re-link.
  - `sharepoint-migration-planning` — dependency-graph analysis and deployment wave-order computation.
  - `sharepoint-content-publication`, `workbench-setup` — tenant publication and connection/config setup.
  - `sharepoint-agents-and-skills` — agent/native-skill lifecycle plus 11 Claude Code routing/analysis
    agents (`agents/`) spanning link, schema, modernization, deployment, and content-migration domains.
- **Intake & Runs**
  - `intake/` — Source `.docx` input files for the CEIS Manual pilot.
  - `runs/ceis-manual-v2/` — Current authoritative, fully validated conversion run.
