# Use Case: Site Discovery & Assessment

Read-only analysis of an exported classic SharePoint site: per-page migration complexity scoring,
functional grouping of web-part code, navigation-depth analysis, custom-form classification, and
permissions auditing.

## When to use this

You have (or can produce) an export of a classic SharePoint site and need to understand what's on
it — complexity, custom code, form usage, permission structure — before deciding how to migrate
or modernize it.

## Workflow at a glance

Five independent analysis skills, each reading an export you already have and writing analysis
artifacts to a directory you name:

- `analyze-page-inventory` — per-page migration complexity scoring.
- `analyze-webpart-code` — functional grouping of custom web-part code.
- `analyze-site-navigation` — navigation depth/structure analysis.
- `analyze-custom-forms` — custom-form classification.
- `analyze-permissions` — permissions auditing.

**Zero SharePoint tenant I/O.** Nothing in this plugin connects to a live tenant or collects the
export it consumes — you provide the export.

## Full detail

[`plugins/sharepoint-discovery/README.md`](../../plugins/sharepoint-discovery/README.md)
