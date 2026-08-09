# Use Cases

This repository serves 12 use cases — 11 built and working, 1 target-state vision — grouped into
three clusters. Each doc here is a short overview — what the use case is, when you'd reach for it,
and the workflow at a glance — then links down to the owning plugin's own README for full
technical detail (skills, agents, install steps, write-safety gates). These docs are intentionally
not a duplicate of that technical detail.

## Document Conversion (the founding use case)

| Use case | Plugin(s) |
|---|---|
| [Convert a Word/PDF manual into structured, multi-target published content](document-conversion.md) | `source-document-extraction`, `document-structure-analysis`, `structured-content-assembly`, `structured-content-rendering` |

## SharePoint Migration & Modernization Engineering (added Phase 9)

| Use case | Plugin |
|---|---|
| [Assess a classic SharePoint site before migrating it](sharepoint-discovery.md) | `sharepoint-discovery` |
| [Audit schema drift across site exports](sharepoint-schema.md) | `sharepoint-schema` |
| [Provision target lists, content types, and columns](sharepoint-provisioning.md) | `sharepoint-provisioning` |
| [Convert classic pages to modern pages](sharepoint-page-modernization.md) | `sharepoint-page-modernization` |
| [Find and fix broken links and embedded references](sharepoint-link-remediation.md) | `sharepoint-link-remediation` |
| [Migrate list-item content to a provisioned target](sharepoint-content-migration.md) | `sharepoint-content-migration` |
| [Plan a multi-object migration's dependency order and waves](sharepoint-migration-planning.md) | `sharepoint-migration-planning` |
| [Publish converted content to a live tenant](sharepoint-content-publication.md) | `sharepoint-content-publication` |
| [Set up connection config and document workflow](workbench-setup.md) | `workbench-setup` |
| [Manage Copilot agent and native-skill lifecycle](sharepoint-agents-and-skills.md) | `sharepoint-agents-and-skills` |

## Target-State Vision (not yet built)

| Use case | Status |
|---|---|
| [AI-assisted knowledge management pipeline — natural-language setup, governed review/approval, knowledge agents, health monitoring](ai-assisted-knowledge-management-pipeline.md) | **NOT YET IMPLEMENTED** — vision only, see `docs/vision/` |

See the [main README](../../README.md) for the overall repository map, and
[`start-here.md`](../../start-here.md) for current phase/branch status.
