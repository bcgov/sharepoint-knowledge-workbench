# AI-Assisted Structured Knowledge Workbench

A public toolkit of reusable skills, tools, and scripts for SharePoint engineering, modernization, and knowledge transformation:

1. **SharePoint Site Migration**: End-to-end site discovery, dependency wave sequencing, link remediation, and content migration.
2. **SharePoint Object Creation**: Automated, declarative provisioning of lists, document libraries, views, site columns, content types, and permissions.
3. **Publishing & Modifying Content**: Modernizing classic ASPX pages, authoring/updating modern SharePoint pages, and publishing Markdown/assets.
4. **Creating & Publishing Copilot Agents & Skills**: Authoring, validating, deploying, and managing SharePoint Copilot agents (`.agent` packages) and native Copilot Studio skills in SharePoint.
5. **Content Maintenance, Continuous Improvement & Document Decomposition**: Breaking huge documents and legacy manuals (Word/PDF) into modular, maintainable subpages in SharePoint, continuously improved and supported by Copilot agents and skills (**Content + Template + Renderer = Published Output**).

---

## 🎯 Overview

The **SharePoint Knowledge Workbench** provides a modular ecosystem of **unified plugin with 11 domain-focused skills and 9 sub-agents** and associated agent skills/scripts designed to bridge SharePoint site modernization, automated object provisioning, and intelligent knowledge management.

Rather than maintaining monolithic Word/PDF manuals or writing one-off migration scripts, the workbench enables teams to decompose massive documents into structured subpages maintainable directly in SharePoint, while providing enterprise-grade tooling to plan and execute SharePoint migrations, provision schema and objects, deploy Copilot Studio agents/skills, and maintain high-fidelity SharePoint sites.

See [INSTALL.md](INSTALL.md) for installation and consumer integration options, or browse **[docs/use-cases/](docs/use-cases/README.md)** for detailed guides across all functional areas.

---

## 🗺️ Content Conversion Workstream: Architecture & Workflow

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

### File and link inventories for migration

The `assessing-sharepoint-sites` and `migrating-sharepoint-sites` skills support recursive CSV file inventories, selected bulk downloads, and offline Python link inventories for static HTML/HTM/ASPX and Office documents. An Online collector exports modern-page stored fields for the same Python analysis.

```powershell
# User-run file inventory: choose the target and destination folder.
pwsh -File plugins/sharepoint-workbench/skills/assessing-sharepoint-sites/scripts/collect-sharepoint-content-inventory.ps1 -SiteUrl https://sharepoint.example.org/ -OutputDir ./inventory

# Offline Python analysis after selected downloads.
python plugins/sharepoint-workbench/skills/modernizing-sharepoint-pages/scripts/link-remediation/export_link_inventory.py --manifest-csv ./downloads/downloads.csv --output-dir ./links
```

The collector writes `files.csv`, including source site/subsite, container/library, path, filename, extension and metadata; it also writes library/error CSVs and a status manifest. Online hostnames select interactive browser sign-in; on-prem prompts for credentials. No file contents are downloaded by the inventory collector. Link extraction retains original source URLs and reports failed/unsupported sources.

See the [bulk content/link workflow](plugins/sharepoint-workbench/skills/modernizing-sharepoint-pages/references/bulk-content-link-workflow.md) for download, modern-field export, conversion, rewrite, publishing and validation stages.

### 1. Prerequisite (SharePoint use cases only): request an app registration

Skip this step if you only need the [document-conversion pipeline](#-content-conversion-workstream-architecture--workflow) (no live SharePoint tenant access). Any use case that connects to a real tenant (`setting-up-sharepoint-workbench`'s live network/auth checks, `publishing-sharepoint-pages`, live discovery/migration work) needs an Entra ID app registration your tenant administrator creates — request it before starting.

**Two distinct registration types exist for two distinct purposes** — an unattended, App-Only/certificate registration for scheduled jobs (no signed-in user, no MFA), and an interactive/delegated registration for human-operator provisioning and migration work (requires an M365 E3/E5 licence, browser/device-code sign-in). Both use `Sites.Selected` (Graph and SharePoint, Application permission type) — not the broader `AllSites.*` grants — which grants zero site access by itself; a tenant administrator must separately grant your specific sites via `Grant-PnPAzureADAppSitePermission` after admin consent.

The `setting-up-sharepoint-workbench` skill walks through both types end to end via mode `app-registration`. See [`plugins/sharepoint-workbench/skills/setting-up-sharepoint-workbench/references/effective-permissions-matrix.md`](plugins/sharepoint-workbench/skills/setting-up-sharepoint-workbench/references/effective-permissions-matrix.md) for the full permission model and empirical findings.

Once approved, record the **Application (client) ID** and **Directory (tenant) ID** — both are needed by `init-connection`.

### 2. Install the Unified Workbench Package

Install the workbench using **APM** (Agent Package Manager) across your active agent harnesses:

```bash
# Install globally for Claude, Copilot, Codex, and Antigravity
apm install @sharepoint/sharepoint-workbench --global --target claude,copilot,codex,antigravity

# Or install locally in your active repository
apm install @sharepoint/sharepoint-workbench --target claude,copilot,codex,antigravity
```

Alternatively, install via native Claude Code marketplace:
```text
/plugin marketplace add richfrem/sharepoint-knowledge-workbench
/plugin install sharepoint-workbench@sharepoint-knowledge-workbench
```

### 3. Run workbench setup

`setting-up-sharepoint-workbench` provides 5 focused modes:

1. **`app-registration`** — Generates fillable service requests and approval guides for tenant administrators.
2. **`init-connection`** — Writes the root, git-ignored `config.psd1` (site URL, tenant ID, client ID, auth mode).
3. **`workflow-intake`** — Interactive intake wizard; configures document-workflow profiles and publication targets.
4. **`validate-connection`** — Validates connection parameters, executes live tenant auth probes, and tests permission boundaries.
5. **`resolve-paths`** — Resolves document IDs and execution profiles into concrete tool parameters.

---

## 📚 Key Navigation & Core Documents

### 🚀 Getting Started & Execution Status

- [start-here.md](start-here.md) — **Primary Quick-Start & Status Guide**. Read this first for active state, phase gates, and workflow guidelines.
- [docs/use-cases/](docs/use-cases/README.md) — **All 12 use cases this repository serves (11 built, 1 target-state vision), one overview doc each.** Start here if you're looking for "how do I do X" rather than architecture/status.
- [architecture.md](architecture.md) — System structure, directory maps, and technical component flow.
- [CLAUDE.md](CLAUDE.md) / [AGENTS.md](AGENTS.md) — Agent coding conventions, TDD rules, and project guidelines.
- [DEPENDENCIES.md](DEPENDENCIES.md) — Running log of external CLI requirements, including Pandoc and LibreOffice.

### 🏛️ Vision & Master Initiative Roadmap

- [Master Initiative Plan and Traceability Matrix](docs/vision/master-initiative-plan-workstreams-and-phases.md) — Master plan, workstreams, phases, and traceability.
- [Vision Overview](docs/vision/README.md) — Vision overview and change-control rules.

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

The repository ships **1 unified domain plugin** (`@sharepoint/sharepoint-workbench`) under `plugins/sharepoint-workbench/`, comprising **11 domain skills** and **9 specialized subagents**:

### The 11 Domain Skills (`plugins/sharepoint-workbench/skills/`)

- **[`setting-up-sharepoint-workbench`](plugins/sharepoint-workbench/skills/setting-up-sharepoint-workbench/SKILL.md)** — Access, connection configuration, project intake profiles, path resolution, and live tenant verification.
- **[`assessing-sharepoint-sites`](plugins/sharepoint-workbench/skills/assessing-sharepoint-sites/SKILL.md)** — Read-only site inventory, schema drift analysis, calculated/choice column extraction, and assessment reporting.
- **[`converting-sharepoint-documents`](plugins/sharepoint-workbench/skills/converting-sharepoint-documents/SKILL.md)** — Document decomposition: extraction, structure analysis, package assembly, dual-target rendering, and editorial review.
- **[`managing-sharepoint-schema`](plugins/sharepoint-workbench/skills/managing-sharepoint-schema/SKILL.md)** — Declarative schema planning and reconciliation (site columns, content types, schema diffing, and scaffolding).
- **[`managing-sharepoint-lists-and-libraries`](plugins/sharepoint-workbench/skills/managing-sharepoint-lists-and-libraries/SKILL.md)** — Provision and manage SharePoint lists, document libraries, list views, and calendar lists.
- **[`managing-sharepoint-navigation`](plugins/sharepoint-workbench/skills/managing-sharepoint-navigation/SKILL.md)** — Declarative navigation management, Excel/CSV sync, structure extraction, and validation.
- **[`publishing-sharepoint-pages`](plugins/sharepoint-workbench/skills/publishing-sharepoint-pages/SKILL.md)** — Modern page publishing, static ASPX asset upload, Markdown publication, dynamic ASPX page migration, and state verification.
- **[`modernizing-sharepoint-pages`](plugins/sharepoint-workbench/skills/modernizing-sharepoint-pages/SKILL.md)** — Classic-to-modern page transformation, web part modernization, page previews, and design-system compliance.
- **[`migrating-sharepoint-sites`](plugins/sharepoint-workbench/skills/migrating-sharepoint-sites/SKILL.md)** — End-to-end migration execution: dependency waves, list content migration, link remediation, and wave scaffolding.
- **[`developing-spfx-solutions`](plugins/sharepoint-workbench/skills/developing-spfx-solutions/SKILL.md)** — SPFx solution scaffolding, React/master-detail web parts, extensions, packaging, and App Catalog deployment.
- **[`managing-sharepoint-copilot-agents-and-skills`](plugins/sharepoint-workbench/skills/managing-sharepoint-copilot-agents-and-skills/SKILL.md)** — Author, deploy, verify, back up, and restore Copilot Studio agents and native SharePoint skills.

### The 9 Specialized Subagents (`plugins/sharepoint-workbench/agents/`)

- `sharepoint-discovery-agent`, `sharepoint-deployment-planning-agent`, `sharepoint-deployment-sequencing-agent`, `sharepoint-content-migration-sequencing-agent`, `sharepoint-modernization-agent`, `sharepoint-webpart-modernization-analysis-agent`, `sharepoint-link-agent`, `sharepoint-link-remediation-analysis-agent`, `sharepoint-validation-agent`.

---

## 🌐 Use Cases: SharePoint Migration & Modernization Engineering

| Use case | Overview | Skill Hub | What it does |
|---|---|---|---|
| **Document conversion & decomposition** | [overview](docs/use-cases/sharepoint-document-conversion.md) | [`converting-sharepoint-documents`](plugins/sharepoint-workbench/skills/converting-sharepoint-documents/SKILL.md) | Extract, analyze, assemble and render Word manuals into governed Markdown / SharePoint pages. |
| **Site assessment & schema comparison** | [overview](docs/use-cases/sharepoint-site-assessment-discovery.md) | [`assessing-sharepoint-sites`](plugins/sharepoint-workbench/skills/assessing-sharepoint-sites/SKILL.md) | Read-only analysis of classic SharePoint inventories, schema drift, calculated columns, and permissions. |
| **Schema reconciliation** | [overview](docs/use-cases/sharepoint-site-assessment-schema.md) | [`managing-sharepoint-schema`](plugins/sharepoint-workbench/skills/managing-sharepoint-schema/SKILL.md) | Declarative planning and reconciliation of site columns, content types, and schema exports. |
| **Tenant provisioning** | [overview](docs/use-cases/sharepoint-site-build-and-publish-provisioning.md) | [`managing-sharepoint-lists-and-libraries`](plugins/sharepoint-workbench/skills/managing-sharepoint-lists-and-libraries/SKILL.md) | Real PnP executors for lists, libraries, columns, content types, views, and items. |
| **Tenant publication** | [overview](docs/use-cases/sharepoint-site-build-and-publish-content.md) | [`publishing-sharepoint-pages`](plugins/sharepoint-workbench/skills/publishing-sharepoint-pages/SKILL.md) | Markdown and page publication plans, dynamic ASPX migration, static ASPX asset uploads. |
| **Classic-to-modern page conversion** | [overview](docs/use-cases/sharepoint-site-migration-page-modernization.md) | [`modernizing-sharepoint-pages`](plugins/sharepoint-workbench/skills/modernizing-sharepoint-pages/SKILL.md) | Classic page analysis, modernization planning, single/library conversion, validation and reports. |
| **Link remediation** | [overview](docs/use-cases/sharepoint-site-migration-link-remediation.md) | [`migrating-sharepoint-sites`](plugins/sharepoint-workbench/skills/migrating-sharepoint-sites/SKILL.md) | Extraction, URL updating and validation of page/document links and rich-text image links. |
| **Content migration** | [overview](docs/use-cases/sharepoint-site-migration-content.md) | [`migrating-sharepoint-sites`](plugins/sharepoint-workbench/skills/migrating-sharepoint-sites/SKILL.md) | Item-level list content migration with two-pass lookup-ID re-linking. |
| **Migration wave planning** | [overview](docs/use-cases/sharepoint-site-migration-planning.md) | [`migrating-sharepoint-sites`](plugins/sharepoint-workbench/skills/migrating-sharepoint-sites/SKILL.md) | Dependency-graph analysis, migration wave planning and wave script scaffolding. |
| **SPFx web part development** | (no overview doc) | [`developing-spfx-solutions`](plugins/sharepoint-workbench/skills/developing-spfx-solutions/SKILL.md) | Web part scaffolding, packaging and App Catalog / direct-publication delivery. |
| **Workbench setup** | [overview](docs/use-cases/sharepoint-workbench-setup.md) | [`setting-up-sharepoint-workbench`](plugins/sharepoint-workbench/skills/setting-up-sharepoint-workbench/SKILL.md) | Connection config, document-workflow and publication-profile setup shared by the other use cases. |
| **Agent & native-skill lifecycle** | [overview](docs/use-cases/sharepoint-copilot-agents-and-skills.md) | [`managing-sharepoint-copilot-agents-and-skills`](plugins/sharepoint-workbench/skills/managing-sharepoint-copilot-agents-and-skills/SKILL.md) | Create/update/deploy/verify/undeploy/backup/restore for SharePoint Copilot agents and native skills. |

The unified package is installable via APM (`apm install @sharepoint/sharepoint-workbench`). Most write-capable modules across this set share one safety contract: planning is pure (no I/O), apply is dry-run by default, and a real tenant write requires both an explicitly injected executor and a plan-derived confirmation token. For full technical details and transition records, see [`docs/plans/master_migration_inventory.csv`](docs/plans/master_migration_inventory.csv).

---

## 🔭 Target-State Vision: AI-Assisted Knowledge Management Pipeline (not yet built)

Beyond the use cases above (all real, working, tested), the repository has a documented but
**not yet implemented** target state: moving knowledge management itself — not just the initial
conversion — to an AI-assisted, agent-enabled pipeline. Natural-language library setup, AI-assisted
metadata/classification/cleanup, governed review and approval, SharePoint knowledge agents managed
as a governed product, and continuous knowledge-health monitoring. See
[docs/use-cases/ai-assisted-knowledge-management-pipeline.md](docs/use-cases/ai-assisted-knowledge-management-pipeline.md)
for what's real today versus what's still proposed, and
[`docs/vision/ai-assisted-sharepoint-knowledge-workbench-governance-vision.md`](docs/vision/ai-assisted-sharepoint-knowledge-workbench-governance-vision.md)
for the full capability vision. Nothing in this section is authorized backlog — it exists to
document direction, not current capability.
