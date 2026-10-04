---
description: >
  Schema/dependency definitions for a SharePoint migration must live in JSON,
  never hardcoded inside generated or hand-written deployment scripts.
globs:
  - "plugins/sharepoint-site-migration/**/*.py"
  - "plugins/sharepoint-site-migration/assets/migration-planning/*.json"
---

# Rule: Schema-Driven SharePoint Deployment

Same principle already established in `plugins/sharepoint-site-build-and-publish/rules/
schema-driven-sharepoint-deployment.md` — kept as a plugin-local copy here because this plugin is
the one that actually authors deployment scripts. If the two drift, treat that as a defect to
reconcile, not two independent rules.

## Why this rule exists

A hand-maintained deployment step list can silently drift from reality — a script gets renamed,
split, or consolidated, and nothing tells you the orchestrator's hardcoded reference is now wrong.
It stays broken until someone actually runs the stale path, which may be a long time if the
operator's own discipline (testing one stage at a time, not running the "run everything" path) is
what's actually protecting production.

## Iron laws

1. **No hardcoded object definitions inside a generated wave script.** Every list/field/
   content-type name a generated script touches must come from `dependency-matrix.json`, never be
   typed into the script by the generation step as a literal.
2. **The deploy script and its validation/test companion must read the same JSON.** If a script
   and its test derive their expectations from different sources, they can drift from each other
   silently — this was the specific failure mode `dependency-matrix.json`'s design is meant to
   prevent.
3. **Wave order is computed, never hand-assigned.** `analyze-migration-dependencies` derives
   order via topological sort (`sharepoint-site-migration`'s own `wave_planning.py`) from
   declared dependencies — it is never a human-maintained sequence of stage numbers.
4. **A dependency is declared by name, not by wave number.** Referring to "whatever ran in an
   earlier stage" instead of a specific named object is exactly the kind of coupling that goes
   stale when stages are renumbered, split, or reordered.
