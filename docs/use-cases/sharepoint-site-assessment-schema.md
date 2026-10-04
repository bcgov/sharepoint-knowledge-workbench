# Use Case: Schema Auditing

Compare two exported SharePoint schema snapshots for list/content-type/site-column/field
variance, audit a single export for duplicate display names, and inventory Choice field option
sets.

## When to use this

You need to know whether two environments (e.g. source vs. target, or before vs. after a change)
actually have the same schema — or you need a clean inventory of an export's Choice fields before
provisioning against it.

## Workflow at a glance

- `compare-schema-exports` — variance comparison between two schema exports, plus duplicate-field detection
  within one export.
- `extract-choice-columns` — inventories Choice field option sets from an export.
- `compare-schema-definitions` / `generate-schema-definition-from-export` — schema definition
  generation and diffing.

**Zero SharePoint tenant I/O.** No environment names are hardcoded — you supply caller-defined
labels (not a built-in "prod"/"test" pair) and the export files themselves.

## Full detail

[`plugins/sharepoint-site-assessment/README.md`](../../plugins/sharepoint-site-assessment/README.md)
