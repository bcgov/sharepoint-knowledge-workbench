# AI-Assisted Structured Knowledge Workbench

Moving document-centric manuals (Word/PDF) into a content-centric, governed knowledge architecture (**Content + Template + Renderer = Published Output**).

---

## 🎯 Overview

The **AI-Assisted Structured Knowledge Workbench** is a multi-phase initiative designed to transform legacy enterprise manuals into modular, version-controlled, structured Markdown assets. This enables multi-target publishing to human readers (SharePoint/ASPX/Web) and grounded AI RAG agents (Microsoft Copilot, custom SharePoint Agents).

Phase 1 and Phase 2 are **engineering-complete**, demonstrating automated `.docx` analysis, human plan confirmation, structured content chunking, TDD validation, and multipage Markdown rendering on the pilot **CEIS Manual**. Phase 3.0 has completed substantial tenant discovery in real SharePoint Online environments. Phase 4.5 is **complete**: the original combined conversion plugin has been decomposed into four independently installable domain plugins (`source-document-extraction`, `document-structure-analysis`, `structured-content-assembly`, `structured-content-rendering`), each installable and testable standalone. See [start-here.md](start-here.md) for the current branch/merge status and authoritative phase context.

**This document-conversion pipeline is the founding use case and remains the primary reference architecture below — but it is no longer the only use case this repository serves.** Phase 9 built out a second, independently real cluster of capability: general-purpose SharePoint migration and modernization engineering tooling (site discovery, schema auditing, provisioning, page modernization, link/reference remediation, content migration, wave planning, tenant publication, and agent/skill lifecycle management) — 10 additional plugins, each its own use case — plus one documented but not-yet-built target-state use case (an AI-assisted knowledge management pipeline). See **[docs/use-cases/](docs/use-cases/README.md)** for a one-page overview of all 12, or jump straight to the **[Additional Use Cases](#-additional-use-cases-sharepoint-migration--modernization-engineering)** or **[Target-State Vision](#-target-state-vision-ai-assisted-knowledge-management-pipeline-not-yet-built)** sections below.

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

## ⚡ Getting Started: Installation & Setup

### 1. Prerequisite (SharePoint use cases only): request an app registration

Skip this step if you only need the [document-conversion pipeline](#-master-architecture--workflow)
(no live SharePoint tenant access). Any use case that connects to a real tenant
(`validate-workbench-environment`'s live network/auth checks, `sharepoint-content-publication`,
live discovery/migration work) needs an Entra ID app registration your tenant administrator
creates — request it before starting.

**Two distinct registration types exist for two distinct purposes** — an unattended, App-Only/
certificate registration for scheduled jobs (no signed-in user, no MFA), and an interactive/
delegated registration for human-operator provisioning and migration work (requires an M365 E3/E5
licence, browser/device-code sign-in). Both use `Sites.Selected` (Graph and SharePoint,
Application permission type) — not the broader `AllSites.*` grants — which grants zero site access
by itself; a tenant administrator must separately grant your specific sites via
`Grant-PnPAzureADAppSitePermission` after admin consent. **Do not treat the PnP grant tier
(`Read`/`Write`/`Manage`/`FullControl`) as a reliable predictor of what operations will succeed**
— production testing showed a `write`-tier grant sufficient for full content/schema provisioning
(lists, libraries, pages, items, files, site columns, content types), contrary to an earlier,
disproven assumption.

The `workbench-setup` plugin's `request-app-registration` skill (step 3 below) walks through both
types end to end — which one to request, the fillable service-request templates, the Entra API
permission/admin-consent/Enterprise-Application steps, the PnP site-level grant, populating
`config.psd1` with the new registration, and validating it against the live tenant. See
[`plugins/workbench-setup/references/effective-permissions-matrix.md`](plugins/workbench-setup/references/effective-permissions-matrix.md)
for the full permission model and empirical findings.

Once approved, record the **Application (client) ID** and **Directory (tenant) ID** — both are
needed by `initialize-workbench-config` (step 3 below).

### 2. Install all plugins

From a clone of this repository:

```bash
uvx --from git+https://github.com/richfrem/agent-plugins-skills plugin-add --all --yes
```

This fetches the cross-platform plugin installer (hosted in the sibling `agent-plugins-skills`
marketplace repo, run ephemerally via `uvx` — no local install needed) and points it at the
current directory (this repo, defaulting `source` to `.`), installing all 14 plugins listed in
[`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json). Add `--dry-run` first to
preview without writing anything, or drop `--all` to pick plugins interactively.

### 3. Run workbench setup

`workbench-setup`'s 5 skills, in this order (see
[`plugins/workbench-setup/README.md`](plugins/workbench-setup/README.md) for full detail on each):

1. **`request-app-registration`** — pure guidance, no I/O: generates a filled service-request
   document for your tenant/cloud administrator, and provides the generalized step-by-step sequence
   (Entra API permissions, admin consent, Enterprise Application user assignment, and the separate
   PnP PowerShell site-level grant) for once it's approved.
2. **`initialize-workbench-config`** — writes the root, git-ignored `config.psd1` (site URL,
   tenant ID, client ID from step 1, auth mode). Generating the file never connects to anything by
   itself.
3. **`initialize-document-workflow`** — interactive intake wizard; writes a document-workflow
   profile and a publication profile for your source document.
4. **`validate-workbench-environment`** — **this is the connection test.** Validates what steps
   2-3 wrote (always PASS or FAIL, never a soft warning), confirms the app registration from step 1
   actually authenticates against the live tenant (OAuth2 device-code flow + a real
   `_api/contextinfo` REST call, plus a permission-boundary proof), and provides real,
   `pwsh`-runnable network-reachability and interactive-authentication scripts. Zero tenant I/O
   unless you explicitly run one of those live scripts yourself.
5. **`resolve-workbench-paths`** — once you're moving into a SharePoint-analysis use case
   (discovery, schema, link-remediation, page-modernization), resolves your document ID and the
   profiles from steps 2-3 into the concrete arguments those plugins need. Prints invocations; never
   executes them.

---

## 📚 Key Navigation & Core Documents

### 🚀 Getting Started & Execution Status

- [start-here.md](start-here.md) — **Authoritative Resume & Status Document**. Read this first for active state, phase gates, and workflow guidelines.
- [docs/use-cases/](docs/use-cases/README.md) — **All 12 use cases this repository serves (11 built, 1 target-state vision), one overview doc each.** Start here if you're looking for "how do I do X" rather than architecture/status.
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

- **Core Conversion Plugins** (Phase 4.5, `plugins/`): four independently installable domain plugins, 10 skills total
  - `source-document-extraction` (1 skill) — Structural analysis, defect detection, and normalized-source-document extraction (`extract-docx`).
  - `document-structure-analysis` (1 skill) — Topic-boundary reasoning, chunking-strategy recommendation, and draft conversion-plan construction (`analyze-document-structure`).
  - `structured-content-assembly` (1 skill) — Pandoc AST postprocessing, chunking, structured-package build, and validation (`assemble-structured-content`).
  - `structured-content-rendering` (7 skills) — Multi-target publication rendering and validation: `render-multipage-markdown`, `render-sharepoint-aspx`, `create-markdown-rendering-template`, `create-aspx-rendering-template`, `validate-rendering-template`, `validate-rendered-output`, `compare-rendered-output`.
- **SharePoint Domain Plugins** (Phase 9, `plugins/`): 10 independently installable plugins, 53 skills
  and 9 agents total, extracted/generalized from a separate SharePoint migration repository per an
  exhaustive 505-file source audit (`temp/phase9-source-audit/file-tracking.json`)
  - `sharepoint-discovery` (5 skills) — read-only analysis of exported classic SharePoint inventories: `analyze-site-navigation`, `analyze-permissions`, `analyze-page-inventory`, `analyze-webpart-code`, `analyze-custom-forms`.
  - `sharepoint-schema` (4 skills, 1 agent) — read-only schema variance/duplicate-field/choice-field auditing: `audit-schema`, `diff-sharepoint-schema`, `extract-choice-fields`, `generate-sharepoint-schema-from-export`; agent: `sharepoint-schema-agent`.
  - `sharepoint-provisioning` (4 skills) — declarative, gated site-column/content-type/list/calendar provisioning: `provision-fields`, `provision-content-types`, `provision-list`, `provision-modern-calendar-list`.
  - `sharepoint-page-modernization` (3 skills, 2 agents) — classic-to-modern page conversion manifest generation: `analyze-aspx-pages`, `convert-aspx-pages`, `compose-page-preview`; agents: `sharepoint-modernization-agent`, `sharepoint-webpart-modernization-analysis-agent`.
  - `sharepoint-link-remediation` (5 skills, 2 agents) — page/document/field-content link extraction, remediation, validation: `extract-links`, `remediate-links`, `remediate-document-content-links`, `remediate-field-image-references`, `validate-link-integrity`; agents: `sharepoint-link-agent`, `sharepoint-link-remediation-analysis-agent`.
  - `sharepoint-content-migration` (1 skill, 1 agent) — item-level content migration with two-pass lookup-ID re-link (`migrate-sharepoint-list-content`); agent: `sharepoint-content-migration-sequencing-agent`.
  - `sharepoint-migration-planning` (5 skills, 2 agents) — dependency-graph analysis and deployment wave-order computation: `discover-sharepoint-site-inventory`, `analyze-sharepoint-dependency-graph`, `generate-sharepoint-wave-scripts`, `setup-sharepoint-migration-project`, `plan-sharepoint-deployment-waves` (only `analyze-sharepoint-dependency-graph` is fully implemented; the rest remain design scaffolds); agents: `sharepoint-deployment-planning-agent`, `sharepoint-deployment-sequencing-agent`.
  - `sharepoint-content-publication` (6 skills, 1 agent) — tenant publication: `upload-content`, `publish-markdown-to-sharepoint`, `publish-aspx-to-sharepoint`, `validate-sharepoint-publication`, `reconcile-sharepoint-publication`, `rollback-sharepoint-publication`; agent: `sharepoint-validation-agent`.
  - `workbench-setup` (4 skills) — connection/config setup: `initialize-workbench-config`, `initialize-document-workflow`, `validate-workbench-environment` (also covers app-registration validation and live network/auth checks), `resolve-workbench-paths`.
  - `sharepoint-agents-and-skills` (15 skills, 0 agents) — agent/native-skill lifecycle only
    (create/update/deploy/verify/rollback/backup/restore agents and native skills); the 9 Claude
    Code routing/analysis agents formerly listed here have moved to their owning domain plugins
    above (link, schema, modernization, migration-planning, content-migration,
    content-publication).
- **Intake & Runs**
  - `intake/` — Source `.docx` input files for the CEIS Manual pilot.
  - `runs/ceis-manual-v2/` — Current authoritative, fully validated conversion run.

---

## 🌐 Additional Use Cases: SharePoint Migration & Modernization Engineering

The document-conversion pipeline above (Master Architecture & Workflow) is this repository's founding use case and remains its primary reference architecture. Phase 9 added a second, independently real cluster of capability — general-purpose SharePoint migration/modernization engineering, decoupled from document conversion — as 10 additional standalone plugins. Each is its own use case with its own README, skills, agents, and test suite; none require the conversion pipeline to be useful on their own.

Full use-case overviews (what it is, when to use it, workflow at a glance) live under [`docs/use-cases/`](docs/use-cases/README.md), one doc per use case, each linking down to its plugin's own README for full technical detail.

| Use case | Overview | Plugin | What it does |
|---|---|---|---|
| **Site discovery & assessment** | [overview](docs/use-cases/sharepoint-discovery.md) | [`sharepoint-discovery`](plugins/sharepoint-discovery/README.md) | Read-only analysis of exported classic SharePoint inventories — navigation, permissions, page inventory, webpart code, custom forms. |
| **Schema auditing** | [overview](docs/use-cases/sharepoint-schema.md) | [`sharepoint-schema`](plugins/sharepoint-schema/README.md) | Schema variance, duplicate-field, and choice-field auditing across site exports. |
| **Content provisioning** | [overview](docs/use-cases/sharepoint-provisioning.md) | [`sharepoint-provisioning`](plugins/sharepoint-provisioning/README.md) | Declarative, gated provisioning of site columns, content types, lists, and modern calendars. |
| **Classic-to-modern page conversion** | [overview](docs/use-cases/sharepoint-page-modernization.md) | [`sharepoint-page-modernization`](plugins/sharepoint-page-modernization/README.md) | Classic ASPX page analysis and modern-page conversion manifest generation. |
| **Link & embedded-reference remediation** | [overview](docs/use-cases/sharepoint-link-remediation.md) | [`sharepoint-link-remediation`](plugins/sharepoint-link-remediation/README.md) | Extraction, remediation, and validation of page/document links and embedded field image references. |
| **Content migration** | [overview](docs/use-cases/sharepoint-content-migration.md) | [`sharepoint-content-migration`](plugins/sharepoint-content-migration/README.md) | Item-level list content migration with two-pass lookup-ID re-linking. |
| **Migration wave planning** | [overview](docs/use-cases/sharepoint-migration-planning.md) | [`sharepoint-migration-planning`](plugins/sharepoint-migration-planning/README.md) | Dependency-graph analysis and deployment wave-order computation across a migration project. |
| **Tenant publication** | [overview](docs/use-cases/sharepoint-content-publication.md) | [`sharepoint-content-publication`](plugins/sharepoint-content-publication/README.md) | Markdown/ASPX upload, validation, reconciliation, and rollback against a live tenant. |
| **Workbench/connection setup** | [overview](docs/use-cases/workbench-setup.md) | [`workbench-setup`](plugins/workbench-setup/README.md) | Cross-cutting connection config, document-workflow, and publication-profile setup shared by the other use cases. |
| **Agent & native-skill lifecycle** | [overview](docs/use-cases/sharepoint-agents-and-skills.md) | [`sharepoint-agents-and-skills`](plugins/sharepoint-agents-and-skills/README.md) | Create/update/deploy/verify/rollback/backup/restore for SharePoint Copilot agents and native skills. |

Each plugin installs and runs standalone (`pip install -e plugins/<name>`). Every write-capable module across this set shares one safety contract: planning is pure (no I/O), apply is dry-run by default, and a real tenant write requires both an explicitly injected executor and a plan-derived confirmation token — see each plugin's own README for its specific gate. For the full architectural picture (including which decisions were made, which remain design scaffolds, and cross-plugin dependencies), see [start-here.md](start-here.md)'s "Phase 9" section and [`docs/vision/ai-assisted-structured-knowledge-workbench-broader-plan.md`](docs/vision/ai-assisted-structured-knowledge-workbench-broader-plan.md)'s "Scope-expansion update" note.

---

## 🔭 Target-State Vision: AI-Assisted Knowledge Management Pipeline (not yet built)

Beyond the 11 use cases above (all real, working, tested), the repository has a documented but
**not yet implemented** target state: moving knowledge management itself — not just the initial
conversion — to an AI-assisted, agent-enabled pipeline. Natural-language library setup, AI-assisted
metadata/classification/cleanup, governed review and approval, SharePoint knowledge agents managed
as a governed product, and continuous knowledge-health monitoring. See
[docs/use-cases/ai-assisted-knowledge-management-pipeline.md](docs/use-cases/ai-assisted-knowledge-management-pipeline.md)
for what's real today versus what's still proposed, and
[`docs/vision/ai-assisted-sharepoint-knowledge-workbench-governance-vision.md`](docs/vision/ai-assisted-sharepoint-knowledge-workbench-governance-vision.md)
for the full capability vision. Nothing in this section is authorized backlog — it exists to
document direction, not current capability.
