# AI-Assisted Structured Knowledge Workbench

Moving document-centric manuals (Word/PDF) into a content-centric, governed knowledge architecture (**Content + Template + Renderer = Published Output**).

---

## 🎯 Overview

The **AI-Assisted Structured Knowledge Workbench** is a multi-phase initiative designed to transform legacy enterprise manuals into modular, version-controlled, canonical Markdown assets. This enables multi-target publishing to human readers (SharePoint/ASPX/Web) and grounded AI RAG agents (Microsoft Copilot, custom SharePoint Agents).

Phase 1 and Phase 2 are **engineering-complete**, demonstrating automated `.docx` analysis, human plan confirmation, structured content chunking, TDD validation, and multipage Markdown rendering on the pilot **CEIS Manual**. Phase 3.0 has completed substantial tenant discovery in real SharePoint Online environments. Phase 4.5 is **complete**: the original combined conversion plugin has been decomposed into four independently-installable domain plugins (`source-document-extraction`, `document-structure-analysis`, `structured-content-assembly`, `structured-content-rendering`), each installable and testable standalone — see [start-here.md](start-here.md) for the branch/merge status and Phase 5 readiness.

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
                               |  Canonical Markdown Core    |
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
* [start-here.md](start-here.md) — **Authoritative Resume & Status Document** (Read this first for active state, phase gates, and workflow guidelines).
* [architecture.md](architecture.md) — System structure, directory maps, and technical component flow.
* [CLAUDE.md](CLAUDE.md) / [GEMINI.md](GEMINI.md) / [AGENTS.md](AGENTS.md) — Agent coding conventions, TDD rules, and project guidelines.
* [DEPENDENCIES.md](DEPENDENCIES.md) — Running log of external CLI requirements (Pandoc, LibreOffice).

### 🏛️ Vision & Master Initiative Roadmap
* [docs/vision/master-initiative-plan-workstreams-and-phases.md](docs/vision/master-initiative-plan-workstreams-and-phases.md) — Authoritative 8-Phase Master Plan & Traceability Matrix.
* [docs/vision/README.md](docs/vision/README.md) — Vision overview and change-control rules.
* [docs/superpowers/FUTURE-PHASE-PLANNING-INDEX.md](docs/superpowers/FUTURE-PHASE-PLANNING-INDEX.md) — Forward-Phase Index (Phases 4–8 specifications and plan scaffolds).

### 🔬 Research & Empirical Evidence
* [docs/research/README.md](docs/research/README.md) — Comprehensive Research Index & Decision Guides.
* [docs/research/concept-dual-target-rendering-agent-vs-human.md](docs/research/concept-dual-target-rendering-agent-vs-human.md) — **Dual-Target Rendering Model** (Human-Facing vs. Agent-Optimized Output).
* [docs/research/field-note-sharepoint-agentassets-review-manual-topics-skill.md](docs/research/field-note-sharepoint-agentassets-review-manual-topics-skill.md) — Empirical Phase 3.0 SharePoint `AgentAssets` discovery findings.
* [docs/research/skill-runtime-decision-guide-sharepoint-vs-github-copilot.md](docs/research/skill-runtime-decision-guide-sharepoint-vs-github-copilot.md) — Decision framework for SharePoint-native vs. GitHub-repository skills.

---

## 📊 Key Architectural Diagrams

The repository maintains formal Mermaid architecture diagrams in [docs/diagrams/](docs/diagrams/README.md):

1. **[Overall System Architecture](docs/diagrams/high-level.mmd)** — End-to-end view from `.docx` intake to canonical storage and multi-runtime agent delivery.
2. **[Phase 1 Conversion Pipeline](docs/diagrams/01-phase1-overview.mmd)** — Stage breakdown (`analyze` → `confirm` → `convert` → `render`).
3. **[Document Analysis & Plan Confirmation](docs/diagrams/02-analyze-and-confirm.mmd)** — Interactive human-in-the-loop plan confirmation.
4. **[Canonical Content Creation](docs/diagrams/03-create-canonical-content.mmd)** — Pandoc AST cleanup, media extraction, structural anchor resolution, and packaging.
5. **[Render & Multi-Target Generation](docs/diagrams/04-generate-and-render.mmd)** — Multipage Markdown & dual-target rendering engine.
6. **[Validation & Atomic Promotion](docs/diagrams/05-validation-and-evidence.mmd)** — Content-loss prevention, schema validation, and atomic staging promotion.

---

## 🛠️ Active Implementation & Tools

- **Core Conversion Plugins** (Phase 4.5, `plugins/`): four independently-installable domain plugins
  - `source-document-extraction` — Structural analysis, defect detection, normalized-source-document extraction.
  - `document-structure-analysis` — Topic-boundary reasoning, chunking-strategy recommendation, draft conversion-plan construction.
  - `structured-content-assembly` — Pandoc AST postprocessing, chunking, canonical package build and validation.
  - `structured-content-rendering` — Multi-target publication rendering & validation.
- **Intake & Runs**:
  - `intake/` — Source `.docx` input files (CEIS Manual pilot).
  - `runs/ceis-manual-v2/` — Current authoritative, fully validated conversion run.
