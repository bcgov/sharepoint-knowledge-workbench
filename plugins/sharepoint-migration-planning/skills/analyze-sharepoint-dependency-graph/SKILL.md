---
name: analyze-sharepoint-dependency-graph
plugin: sharepoint-migration-planning
status: design-scaffold
description: >
  NOT YET IMPLEMENTED. Will deterministically derive an object dependency
  graph (which lists/content types/fields depend on which others) from a
  site export, compute deployment wave order by reusing
  sharepoint-provisioning's wave_planning.plan_waves, and emit the result as
  dependency-matrix.json conforming to assets/dependency-matrix-schema.json.
  Pure computation -- no tenant I/O, no AI-model involvement, fully
  deterministic and testable.
allowed-tools: Bash, Read, Write
---

# Analyze SharePoint Dependency Graph

> **Status: design scaffold, not implemented.**

## Trigger and Purpose (planned)

Stage 3a — the **deterministic half** of dependency analysis. Same input always produces the same
output; this is why it is plain, TDD-tested Python, not an agent-assisted step (see
`../generate-sharepoint-wave-scripts/SKILL.md` for the AI-assisted half, and
`../../rules/test-driven-wave-deployment.md` for why this split matters).

## Planned behavior

1. Read the export produced/supplied by `discover-sharepoint-site-inventory`.
2. Derive `DeploymentObject`s (name, object type, `depends_on`) — e.g., a lookup field depends on
   its target list; a content type depends on the fields it links.
3. Call `sharepoint-provisioning`'s existing `wave_planning.plan_waves()` — **reuse, do not
   reimplement** the topological-sort/cycle-detection logic already built and tested there.
4. Emit `dependency-matrix.json`, validated against `../../assets/dependency-matrix-schema.json`.

## Honest outcomes (planned)

A cycle or a dependency naming a nonexistent object must be reported explicitly (matching
`wave_planning.py`'s existing behavior), never silently dropped or guessed around.

## Provenance

New design work, generalizing the *concept* of `wave-dependency-matrix.json` observed in a separate
SharePoint migration repository — that file was hand-curated there (no script builds it
automatically in the source), so this skill is new automation, not a code port.
