# Use Cases

This repository serves 12 use cases — 11 built and working, 1 target-state vision — grouped across
the seven installable plugins. Each doc here is a short overview — what the use case is, when you'd reach for it,
and the workflow at a glance — then links down to the owning plugin's own README for full
technical detail (skills, agents, install steps, write-safety gates). These docs are intentionally
not a duplicate of that technical detail.

## Document Conversion (the founding use case)

| Use case | Plugin |
|---|---|
| [Convert a Word/PDF manual into structured, multi-target published content](sharepoint-document-conversion.md) | `sharepoint-document-conversion` |

## SharePoint Migration & Modernization Engineering (added Phase 9)

| Use case | Plugin |
|---|---|
| [Assess a classic SharePoint site before migrating it](sharepoint-site-assessment-discovery.md) | `sharepoint-site-assessment` |
| [Audit schema drift across site exports](sharepoint-site-assessment-schema.md) | `sharepoint-site-assessment` |
| [Provision target lists, content types, and columns](sharepoint-site-build-and-publish-provisioning.md) | `sharepoint-site-build-and-publish` |
| [Convert classic pages to modern pages](sharepoint-site-migration-page-modernization.md) | `sharepoint-site-migration` |
| [Find and fix broken links and embedded references](sharepoint-site-migration-link-remediation.md) | `sharepoint-site-migration` |
| [Migrate list-item content to a provisioned target](sharepoint-site-migration-content.md) | `sharepoint-site-migration` |
| [Plan a multi-object migration's dependency order and waves](sharepoint-site-migration-planning.md) | `sharepoint-site-migration` |
| [Publish converted content to a live tenant](sharepoint-site-build-and-publish-content.md) | `sharepoint-site-build-and-publish` |
| [Set up connection config and document workflow](sharepoint-workbench-setup.md) | `sharepoint-workbench-setup` |
| [Manage Copilot agent and native-skill lifecycle](sharepoint-copilot-agents-and-skills.md) | `sharepoint-copilot-agents-and-skills` |

## Target-State Vision (not yet built)

| Use case | Status |
|---|---|
| [AI-assisted knowledge management pipeline — natural-language setup, governed review/approval, knowledge agents, health monitoring](ai-assisted-knowledge-management-pipeline.md) | **NOT YET IMPLEMENTED** — vision only, see `docs/vision/` |

See the [main README](../../README.md) for the overall repository map, and
[`START-HERE.md`](../../START-HERE.md) for current project navigation.
