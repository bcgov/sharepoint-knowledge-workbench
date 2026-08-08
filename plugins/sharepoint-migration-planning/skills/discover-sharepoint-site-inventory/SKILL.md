---
name: discover-sharepoint-site-inventory
plugin: sharepoint-migration-planning
status: design-scaffold
description: >
  NOT YET IMPLEMENTED, AND PARTIALLY BLOCKED. Will produce a raw inventory
  export of the source site (lists, content types, site columns, fields,
  lookup-column targets) for the analysis stage to consume. The real,
  live-tenant discovery connector this depends on -- sharepoint-collection,
  Part A -- is design-only and not authorized to build (blocked on an
  auth-model decision). Until it exists, this skill accepts an
  already-produced export directory as input.
allowed-tools: Bash, Read
---

# Discover SharePoint Site Inventory

> **Status: design scaffold, not implemented, partially blocked on an external decision.**

## Trigger and Purpose (planned)

Stage 2 of the `sharepoint-migration-planning` pipeline. Produces (or, for now, accepts) the raw
site export that stage 3a analyzes: lists, content types, site columns, per-list fields, and
critically — **lookup-column targets** (which list a lookup field points at), the relationship the
dependency graph is built from. `sharepoint-schema`'s existing export/definition capture does not
currently record lookup-target relationships explicitly; this is a design gap this stage's output
schema must close, whether or not this stage itself performs live discovery.

## Blocked half vs. buildable half

- **Real live-tenant discovery**: connecting to the source site and pulling this inventory directly
  is exactly `sharepoint-collection`'s (Part A's) job — design-only, `REQUIRES_HUMAN_DECISION`, not
  authorized to build. See
  `docs/superpowers/specs/2026-08-07-sharepoint-collection-and-orchestration-design.md`.
- **Buildable now**: accepting an export directory a human already produced (by hand, or with an
  existing script run outside this workbench) as this skill's input, and normalizing/validating its
  shape for stage 3a. This does not require solving the live-connection question.

## Planned behavior

1. Accept a path to an export directory (or, once Part A exists, an option to invoke it directly).
2. Validate the export contains what stage 3a needs, including lookup-column target information.
3. Report honestly (missing/partial/unavailable sections), never silently proceed on an incomplete
   export.

## Provenance

New design work. The source repository's equivalent (`export-sharepoint-inventory-custom.ps1`) is
a live-tenant collector out of scope for this workbench's zero-tenant-I/O plugins — not ported.
