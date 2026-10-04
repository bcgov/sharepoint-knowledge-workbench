# Use Case: Content Provisioning

Declarative, JSON-schema-driven provisioning of SharePoint site columns, content types, lists,
libraries, and modern calendar lists.

## When to use this

You have a target schema (in JSON) and need to reconcile a live site toward it — create missing
columns/content types/lists, without hand-scripting each PnP call yourself.

## Workflow at a glance

- `plan-column-changes` / `plan-content-type-changes` / `reconcile-site-schema` — reconcile site columns,
  content types, and lists/libraries against a caller-supplied schema.
- `reconcile-calendar-list` — modern-calendar-specific provisioning that structurally
  prevents a known Start/End platform bug.

Every write goes through a three-gate safety contract: **planning is pure** (no I/O — it only
reads a schema and a caller-supplied observation of current state), **apply is dry-run by
default**, and **a real write requires both an explicitly injected executor and a plan-derived
confirmation token**. This plugin never fetches tenant state itself — you (or an orchestrating
caller) supply the current-state observation.

## Full detail

[`plugins/sharepoint-site-build-and-publish/README.md`](../../plugins/sharepoint-site-build-and-publish/README.md)
