# sharepoint-migration-planning

> **Status: `DESIGN_SCAFFOLD`, `NOT_IMPLEMENTED`.** This plugin's folder structure, skill names,
> and pipeline diagram exist so the design can be agreed before any real code is written. No
> skill below has a working implementation yet — each `SKILL.md` states what it *will* do, not
> what it does today. Do not install or invoke anything here expecting a working result.

## Why this plugin exists (the gap it fills)

Confirmed against every other plugin in this workbench: nothing else does this.

- `sharepoint-discovery` / `sharepoint-schema` analyze **one already-exported site** (inventory,
  audit, diff, choice-field extraction) — read-only, no cross-object dependency graph, no
  sequencing.
- `sharepoint-provisioning` **executes** a single-pass reconcile of one target schema (three-gate
  write safety), and its `wave_planning.py` module topologically sorts a dependency list **it is
  handed** — it does not discover a site or build that list itself.
- `sharepoint-collection` (design only, not built — see
  `docs/superpowers/specs/2026-08-07-sharepoint-collection-and-orchestration-design.md`) would be
  the raw connector only — no analysis, no generation.
- **Nothing in the workbench generates new deployment scripts as an output.**

This plugin is the missing middle layer: source-site discovery → dependency-graph analysis →
generated, site-specific wave deployment scripts — sitting between the not-yet-built collector and
the already-built executor.

## Pipeline

See `references/pipeline-overview.mmd` for the full diagram. Four stages:

```text
1. setup-sharepoint-migration-project   (interactive)
     ask source/target site, confirm workbench-setup's config.psd1 exists, create a working folder

2. discover-sharepoint-site-inventory   (depends on sharepoint-collection -- NOT YET BUILT)
     until Part A exists: accepts an already-produced export directory as input

3a. analyze-sharepoint-dependency-graph  (DETERMINISTIC, Python)
     export -> DeploymentObjects + depends_on -> wave_planning.plan_waves() -> dependency-matrix.json

3b. generate-sharepoint-wave-scripts     (AI-MODEL-ASSISTED, not pure function)
     dependency-matrix.json + template assets -> new site-specific wave scripts + a wave guide
```

**Why 3a and 3b are split:** deriving the dependency graph and computing wave order is
deterministic — same input always produces the same graph and the same topological order, so it
belongs in tested Python (`sharepoint-provisioning`'s `wave_planning.py` is reused directly, not
reimplemented). Turning that graph into *readable, well-structured deployment scripts and a human
runbook* is a synthesis task — the same script structure can be expressed many reasonable ways —
so that step is explicitly agent-assisted, using the assets below as style/shape references, not a
pure function with one correct output.

**Design lineage, stated explicitly:** this 3a/3b split is the same underlying discipline as the
"2-Stage Deep Architectural Review Protocol" observed in a discovery agent in the source
repository — Stage 1 deterministic script execution, Stage 2 mandatory AI reasoning pass over the
real output, never synthesize before the deterministic stage has produced something real to reason
over. That source agent was evaluated and rejected for extraction (it orchestrates live-tenant
scripts and its final step calls a script already rejected elsewhere in this workbench's evidence
for fabricating headline metrics), so nothing was ported from it — but the two-stage discipline
itself is sound and is what this plugin's 3a/3b split generalizes, applied once at the pipeline
level rather than per discovery step, and grounded in an offline export rather than live-tenant
calls.

## Assets (templates the agent step reads, not executable code)

- `assets/dependency-matrix-schema.json` — JSON Schema the deterministic step's output must satisfy
- `assets/dependency-matrix-reference.md` — reference doc explaining the schema's fields
- `assets/wave-script-template.example.py` — example wave-script shape (generic, no site-specific content) the generation step follows
- `assets/wave-guide-template.md` — example human runbook shape (generic) the generation step follows

## Rules

- `rules/schema-driven-sharepoint-deployment.md` — same principle already established in
  `sharepoint-provisioning/rules/`: schema/dependency definitions live in JSON, never hardcoded in
  scripts; deploy and validation logic both read the same JSON so they cannot drift from each
  other.
- `rules/test-driven-wave-deployment.md` — draws the explicit parallel between this repo's
  `.agent/rules/test-driven-development.md` and the wave-by-wave discipline this plugin automates:
  test → deploy → retest, one wave at a time, is Red-Green-Refactor applied to infrastructure
  provisioning, not a separate convention.

## Explicitly not decided/built yet

- Stage 2's real discovery connector (`sharepoint-collection`) — blocked on an auth-model decision.
- Whether stage 3a should also accept `sharepoint-provisioning`'s existing `ListDef`/
  `ContentTypeDef`/`FieldDef` shapes directly as an alternative input, or only a raw export.
- Exact generated wave-script language/shape (Python calling `sharepoint-provisioning`'s
  `list_provisioning`/`content_type_provisioning`/`field_provisioning`, most likely — not decided).
