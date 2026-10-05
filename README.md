# AI-Assisted Structured Knowledge Workbench

A public toolkit of reusable skills, tools, and scripts for SharePoint engineering, modernization, and knowledge transformation:

1. **SharePoint Site Migration**: End-to-end site discovery, dependency wave sequencing, link remediation, and content migration.
2. **SharePoint Object Creation**: Automated, declarative provisioning of lists, document libraries, views, site columns, content types, and permissions.
3. **Publishing & Modifying Content**: Modernizing classic ASPX pages, authoring/updating modern SharePoint pages, and publishing Markdown/assets.
4. **Creating & Publishing Copilot Agents & Skills**: Authoring, validating, deploying, and managing SharePoint Copilot agents (`.agent` packages) and native Copilot Studio skills in SharePoint.
5. **Content Maintenance, Continuous Improvement & Document Decomposition**: Breaking huge documents and legacy manuals (Word/PDF) into modular, maintainable subpages in SharePoint, continuously improved and supported by Copilot agents and skills (**Content + Template + Renderer = Published Output**).

---

## 🎯 Overview

The **SharePoint Knowledge Workbench** provides a modular ecosystem of **7 independently-installable domain plugins** and associated agent skills/scripts designed to bridge SharePoint site modernization, automated object provisioning, and intelligent knowledge management.

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

### 1. Prerequisite (SharePoint use cases only): request an app registration

Skip this step if you only need the [document-conversion pipeline](#-content-conversion-workstream-architecture--workflow)
(no live SharePoint tenant access). Any use case that connects to a real tenant
(`validate-sharepoint-connection`'s live network/auth checks, `sharepoint-site-build-and-publish`,
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

The `sharepoint-workbench-setup` plugin's `request-app-registration` skill (step 3 below) walks through both
types end to end — which one to request, the fillable service-request templates, the Entra API
permission/admin-consent/Enterprise-Application steps, the PnP site-level grant, populating
`config.psd1` with the new registration, and validating it against the live tenant. See
[`plugins/sharepoint-workbench-setup/references/effective-permissions-matrix.md`](plugins/sharepoint-workbench-setup/references/effective-permissions-matrix.md)
for the full permission model and empirical findings.

Once approved, record the **Application (client) ID** and **Directory (tenant) ID** — both are
needed by `initialize-connection-config` (step 3 below).

### 2. Install all plugins

From a clone of this repository:

```bash
uvx --from git+https://github.com/richfrem/agent-plugins-skills plugin-add --all --yes
```

This fetches the cross-platform plugin installer (hosted in the sibling `agent-plugins-skills`
marketplace repo, run ephemerally via `uvx` — no local install needed) and points it at the
current directory (this repo, defaulting `source` to `.`), installing all 7 plugins listed in
[`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json). Add `--dry-run` first to
preview without writing anything, or drop `--all` to pick plugins interactively.

### 3. Run workbench setup

`sharepoint-workbench-setup`'s 5 skills, in this order (see
[`plugins/sharepoint-workbench-setup/README.md`](plugins/sharepoint-workbench-setup/README.md) for full detail on each):

1. **`request-app-registration`** — pure guidance, no I/O: generates a filled service-request
   document for your tenant/cloud administrator, and provides the generalized step-by-step sequence
   (Entra API permissions, admin consent, Enterprise Application user assignment, and the separate
   PnP PowerShell site-level grant) for once it's approved.
2. **`initialize-connection-config`** — writes the root, git-ignored `config.psd1` (site URL,
   tenant ID, client ID from step 1, auth mode). Generating the file never connects to anything by
   itself.
3. **`initialize-document-workflow`** — interactive intake wizard; writes a document-workflow
   profile and a publication profile for your source document.
4. **`validate-sharepoint-connection`** — **this is the connection test.** Validates what steps
   2-3 wrote (always PASS or FAIL, never a soft warning), confirms the app registration from step 1
   actually authenticates against the live tenant (OAuth2 device-code flow + a real
   `_api/contextinfo` REST call, plus a permission-boundary proof), and provides real,
   `pwsh`-runnable network-reachability and interactive-authentication scripts. Zero tenant I/O
   unless you explicitly run one of those live scripts yourself.
5. **`resolve-document-paths`** — once you're moving into a SharePoint-analysis use case
   (discovery, schema, link-remediation, page-modernization), resolves your document ID and the
   profiles from steps 2-3 into the concrete arguments those plugins need. Prints invocations; never
   executes them.

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

The repository ships **7 independently installable domain plugins** (104 skills, 9 agents) under `plugins/`. One domain is one plugin; functional groups inside a plugin organize its skills.

- **[`sharepoint-workbench-setup`](plugins/sharepoint-workbench-setup/README.md)** (5 skills) — access, connection, project/document configuration, path resolution and readiness.
  - *Access, project/document configuration, path resolution and readiness*: `workbench-initialize-connection-config`, `workbench-initialize-document-workflow`, `workbench-request-app-registration`, `workbench-resolve-document-paths`, `workbench-validate-sharepoint-connection`
- **[`sharepoint-document-conversion`](plugins/sharepoint-document-conversion/README.md)** (11 skills) — extract, analyze, assemble, render and editorially review manual content.
  - *Assemble a content package*: `content-assemble-structured-content`
  - *Editorial topic review*: `content-review-manual-topic`
  - *Extract source content*: `content-extract-docx`
  - *Organize topics and pages*: `content-analyze-document-structure`
  - *Render and check output*: `content-compare-rendered-output`, `content-create-markdown-rendering-template`, `content-create-sharepoint-rendering-template`, `content-render-markdown-pages`, `content-render-sharepoint-pages`, `content-validate-rendered-output`, `content-validate-rendering-template`
- **[`sharepoint-site-assessment`](plugins/sharepoint-site-assessment/README.md)** (12 skills, 1 agent) — read-only inventory, analysis and assessment of classic/modern sites.
  - *Inventory, analysis and read-only assessment*: `sharepoint-analyze-custom-forms`, `sharepoint-analyze-page-inventory`, `sharepoint-analyze-permissions`, `sharepoint-analyze-site-navigation`, `sharepoint-analyze-webpart-behavior`, `sharepoint-audit-managed-metadata`, `sharepoint-audit-onprem-schema-drift`, `sharepoint-collect-site-inventory`, `sharepoint-compare-schema-exports`, `sharepoint-extract-calculated-columns`, `sharepoint-extract-choice-columns`, `sharepoint-generate-assessment-reports`
- **[`sharepoint-site-build-and-publish`](plugins/sharepoint-site-build-and-publish/README.md)** (35 skills, 1 agent) — create/configure SharePoint objects and publish content (dry-run-first writers).
  - *Create and configure SharePoint objects*: `sharepoint-add-list-column`, `sharepoint-add-list-item`, `sharepoint-apply-provisioning-plan`, `sharepoint-compare-schema-definitions`, `sharepoint-configure-column-formatting`, `sharepoint-configure-library-settings`, `sharepoint-create-content-type`, `sharepoint-create-document-library`, `sharepoint-create-list`, `sharepoint-create-list-view`, `sharepoint-create-site-column`, `sharepoint-detach-content-type`, `sharepoint-generate-schema-definition-from-export`, `sharepoint-plan-column-changes`, `sharepoint-plan-content-type-changes`, `sharepoint-reconcile-calendar-list`, `sharepoint-reconcile-site-schema`, `sharepoint-remove-content-type`, `sharepoint-remove-list`, `sharepoint-remove-list-column`, `sharepoint-remove-site-column`, `sharepoint-scaffold-schema-definition`, `sharepoint-update-content-type`, `sharepoint-update-list-column`, `sharepoint-update-list-settings`, `sharepoint-update-site-column`
  - *Publish and maintain SharePoint content*: `sharepoint-apply-page-publication-plan`, `sharepoint-compare-publication-state`, `sharepoint-copy-page-between-sites`, `sharepoint-plan-page-publication`, `sharepoint-publish-markdown-files`, `sharepoint-remove-publication`, `sharepoint-validate-publication`
- **[`sharepoint-site-migration`](plugins/sharepoint-site-migration/README.md)** (19 skills, 7 agents) — plan and run site migration: waves, page modernization, list content, links.
  - *Migrate and modernize SharePoint sites*: `sharepoint-analyze-classic-pages`, `sharepoint-analyze-migration-dependencies`, `sharepoint-audit-list-migration`, `sharepoint-convert-page-library-to-modern`, `sharepoint-convert-page-to-modern`, `sharepoint-create-page-preview`, `sharepoint-extract-links`, `sharepoint-generate-modernization-report`, `sharepoint-initialize-migration-project`, `sharepoint-migrate-list-content`, `sharepoint-normalize-migration-inventory`, `sharepoint-plan-migration-waves`, `sharepoint-plan-page-modernization`, `sharepoint-scaffold-migration-wave-scripts`, `sharepoint-update-links-in-documents`, `sharepoint-update-page-links`, `sharepoint-update-rich-text-image-links`, `sharepoint-validate-link-integrity`, `sharepoint-validate-page-modernization`
- **[`sharepoint-copilot-agents-and-skills`](plugins/sharepoint-copilot-agents-and-skills/README.md)** (14 skills) — author, deploy, verify, back up and restore Copilot agents and native skills.
  - *Agent and native skill lifecycle*: `sharepoint-backup-agents`, `sharepoint-backup-native-skills`, `sharepoint-create-agent-package`, `sharepoint-create-agent-package-from-template`, `sharepoint-create-agent-template`, `sharepoint-create-native-skill`, `sharepoint-deploy-native-skill`, `sharepoint-inspect-agent-knowledge`, `sharepoint-prepare-agentassets-library`, `sharepoint-restore-agents`, `sharepoint-restore-native-skills`, `sharepoint-undeploy-native-skill`, `sharepoint-update-agent-package`, `sharepoint-verify-native-skill`
- **[`sharepoint-spfx-development`](plugins/sharepoint-spfx-development/README.md)** (10 skills) — SPFx scaffolding, packaging and both delivery routes.
  - *Develop, package, deploy and activate*: `sharepoint-deploy-spfx-solution`, `sharepoint-develop-spfx-form-customizer`, `sharepoint-develop-spfx-listview-command-set`, `sharepoint-package-spfx-solution`, `sharepoint-publish-spfx-package`, `sharepoint-request-site-collection-app-catalog`, `sharepoint-scaffold-spfx-master-detail-webpart`, `sharepoint-scaffold-spfx-react-webpart`, `sharepoint-scaffold-spfx-webpart`, `sharepoint-setup-spfx-hosted-workbench`

Previous names: skill and plugin names changed in the seven-domain migration (issue #6). See each plugin README ("Previous identities") and [`docs/architecture/seven-domain-plugin-skill-catalog.md`](docs/architecture/seven-domain-plugin-skill-catalog.md).

---

## 🌐 Additional Use Cases: SharePoint Migration & Modernization Engineering

The document-conversion pipeline above (Master Architecture & Workflow) is this repository's founding use case and remains its primary reference architecture. Phase 9 added general-purpose SharePoint migration/modernization engineering, decoupled from document conversion, across the SharePoint domain plugins listed above.

Full use-case overviews (what it is, when to use it, workflow at a glance) live under [`docs/use-cases/`](docs/use-cases/README.md), one doc per use case, each linking down to its plugin's own README for full technical detail.

| Use case | Overview | Plugin | What it does |
|---|---|---|---|
| **Document conversion & decomposition** | [overview](docs/use-cases/sharepoint-document-conversion.md) | [`sharepoint-document-conversion`](plugins/sharepoint-document-conversion/README.md) | Extract, analyze, assemble and render Word manuals into governed Markdown / SharePoint pages, with single-topic editorial review. |
| **Site assessment & schema comparison** | [overview](docs/use-cases/sharepoint-site-assessment-discovery.md) | [`sharepoint-site-assessment`](plugins/sharepoint-site-assessment/README.md) | Read-only analysis of exported or live classic SharePoint inventories, schema export comparison, choice/calculated-column and permission analysis. |
| **Schema reconciliation** | [overview](docs/use-cases/sharepoint-site-assessment-schema.md) | [`sharepoint-site-build-and-publish`](plugins/sharepoint-site-build-and-publish/README.md) | Declarative, pure planning of site columns, content types, lists and calendar lists, plus schema-definition generation and comparison. |
| **Tenant provisioning** | [overview](docs/use-cases/sharepoint-site-build-and-publish-provisioning.md) | [`sharepoint-site-build-and-publish`](plugins/sharepoint-site-build-and-publish/README.md) | Real PnP executors for site columns, list columns, content types, views, items, libraries, sites, branding and taxonomy. |
| **Tenant publication** | [overview](docs/use-cases/sharepoint-site-build-and-publish-content.md) | [`sharepoint-site-build-and-publish`](plugins/sharepoint-site-build-and-publish/README.md) | Markdown and page publication plans, state comparison and removal against a live tenant. |
| **Classic-to-modern page conversion** | [overview](docs/use-cases/sharepoint-site-migration-page-modernization.md) | [`sharepoint-site-migration`](plugins/sharepoint-site-migration/README.md) | Classic page analysis, modernization planning, single/library conversion, validation and reports. |
| **Link & embedded-reference remediation** | [overview](docs/use-cases/sharepoint-site-migration-link-remediation.md) | [`sharepoint-site-migration`](plugins/sharepoint-site-migration/README.md) | Extraction, update and validation of page/document links and rich-text image links. |
| **Content migration** | [overview](docs/use-cases/sharepoint-site-migration-content.md) | [`sharepoint-site-migration`](plugins/sharepoint-site-migration/README.md) | Item-level list content migration with two-pass lookup-ID re-linking. |
| **Migration wave planning** | [overview](docs/use-cases/sharepoint-site-migration-planning.md) | [`sharepoint-site-migration`](plugins/sharepoint-site-migration/README.md) | Dependency-graph analysis, migration wave planning and wave script scaffolding. |
| **SPFx web part development** | (no overview doc) | [`sharepoint-spfx-development`](plugins/sharepoint-spfx-development/README.md) | Web part scaffolding, packaging and App Catalog / direct-publication delivery. |
| **Workbench/connection setup** | [overview](docs/use-cases/sharepoint-workbench-setup.md) | [`sharepoint-workbench-setup`](plugins/sharepoint-workbench-setup/README.md) | Connection config, document-workflow and publication-profile setup shared by the other use cases. |
| **Agent & native-skill lifecycle** | [overview](docs/use-cases/sharepoint-copilot-agents-and-skills.md) | [`sharepoint-copilot-agents-and-skills`](plugins/sharepoint-copilot-agents-and-skills/README.md) | Create/update/deploy/verify/undeploy/backup/restore for SharePoint Copilot agents and native skills. |

Each plugin installs and runs standalone. The single-source plugins (`sharepoint-workbench-setup`, `sharepoint-site-assessment`, `sharepoint-copilot-agents-and-skills`, `sharepoint-spfx-development`) can be installed in editable Python mode (`pip install -e plugins/<name>`); the consolidated plugins keep one flat-module namespace per original implementation, run their scripts from the namespace folder and test with `python3 plugins/<name>/tests/run_namespaces.py`. Most write-capable modules across this set share one safety contract: planning is pure (no I/O), apply is dry-run by default, and a real tenant write requires both an explicitly injected executor and a plan-derived confirmation token. A few preserved scripts use a different gate or none (see [architecture.md](architecture.md) section 4) — check each script's own parameters. For the full architectural picture (including which decisions were made, which remain design scaffolds, and cross-plugin dependencies), see [start-here.md](start-here.md)'s "Phase 9" section and [`docs/vision/ai-assisted-structured-knowledge-workbench-broader-plan.md`](docs/vision/ai-assisted-structured-knowledge-workbench-broader-plan.md)'s "Scope-expansion update" note.

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
