# sharepoint-migration-planning

> **Status: `IMPLEMENTED`.** All four pipeline skills are real, tested, and install standalone —
> `setup-sharepoint-migration-project` (stage 1), `discover-sharepoint-site-inventory` (stage 2,
> scoped to its buildable half), `analyze-sharepoint-dependency-graph` (stage 3a, deterministic),
> and `generate-sharepoint-wave-scripts` (stage 3b). Stage 2's live-tenant discovery connector
> (`sharepoint-collection`) remains design-only and out of scope — stage 2 here validates an
> already-produced export directory, it does not connect to a tenant itself. Stage 3b is
> implemented as a pure, deterministic templating function rather than an AI-model call (a
> deviation from this plugin's original "explicitly agent-assisted" design intent — flagged here,
> not silently papered over); see that skill's `SKILL.md` for why its output is still exactly
> test-verifiable.

## Why this plugin exists (the gap it fills)

Confirmed against every other plugin in this workbench: nothing else does this.

- `sharepoint-discovery` / `sharepoint-schema` analyze **one already-exported site** (inventory,
  audit, diff, choice-field extraction) — read-only, no cross-object dependency graph, no
  sequencing.
- `sharepoint-provisioning` **executes** a single-pass reconcile of one target schema (three-gate
  write safety) — it consumes a computed wave order as an input to that apply, it does not discover
  a site, build a dependency graph, or compute wave order itself.
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
1. setup-sharepoint-migration-project   (project_setup.py -- filesystem + text check only)
     confirm source/target site args + workbench-setup's config.psd1 exists, create a working folder

2. discover-sharepoint-site-inventory   (inventory_validation.py -- validates a human-produced export)
     accepts an already-produced export directory as input; real live-tenant discovery
     (sharepoint-collection, Part A) remains NOT YET BUILT

3a. analyze-sharepoint-dependency-graph  (DETERMINISTIC, Python)
     export -> DeploymentObjects + depends_on -> wave_planning.plan_waves() -> dependency-matrix.json

3b. generate-sharepoint-wave-scripts     (wave_script_generation.py -- deterministic templating)
     dependency-matrix.json -> new site-specific wave script skeletons + a wave guide
```

**Why 3a and 3b are split:** deriving the dependency graph and computing wave order is
deterministic — same input always produces the same graph and the same topological order, so it
belongs in tested Python (`wave_planning.py`, authored in this plugin — see
`plan-sharepoint-deployment-waves`'s provenance for why it moved here from
`sharepoint-provisioning` on 2026-08-08). Turning that graph into *readable, well-structured
deployment scripts and a human runbook* was originally scoped as agent-assisted synthesis — the
same script structure can be expressed many reasonable ways — but is implemented as a thin,
deterministic templating function (`wave_script_generation.py`) instead: the matrix carries only
`name`/`objectType`/`dependsOn`, not field-level schema, so full synthesis genuinely isn't
mechanically derivable from it, and a deterministic fill (real names/types/dependsOn only, an
honest `NotImplementedError` TODO where field schema would go) keeps the output exactly
test-verifiable rather than requiring an AI-model call for what the matrix alone can support. The
assets below remain style/shape references for that templating, not values ever copied verbatim.

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

## Real `sharepoint-provisioning` executors (2026-08-11)

`sharepoint-provisioning` has zero tenant I/O of any kind (enforced by its
own test suite) — its four planning modules (`field_provisioning.py`,
`content_type_provisioning.py`, `list_provisioning.py`,
`calendar_provisioning.py`) each define a real, gated `apply_*` step that
raises `ExecutorRequired` without an injected executor callable. Per that
plugin's own README ("Deliberate scope limits"), the real tenant-facing
executor for those plans belongs in a different plugin — this one, which
already positions itself as generating wave deployment scripts that call
into `sharepoint-provisioning`'s plan/apply functions and never opens a new,
parallel write path. Four real `.ps1` scripts now live in `scripts/`:

- `scripts/spo-provision-site-columns.ps1` — consumes `field_provisioning.py`'s
  planned `FieldAction`s; typed fields via `Add-PnPField`, raw-XML field
  types (Calculated/Lookup/User) via `Add-PnPFieldFromXml` fed by the plan's
  own pre-built XML. Refuses outright if a plan ever names `Start`/`End` —
  those must never be site columns (see the calendar-bug note below).
- `scripts/spo-provision-content-types.ps1` — consumes
  `content_type_provisioning.py`'s planned `ContentTypeAction` steps
  (`create_content_type`/`link_field`/`hide_field`/`show_field`/
  `unlink_field`/`attach_content_type`); applies exactly what the plan says,
  infers nothing locally.
- `scripts/spo-provision-list.ps1` — consumes `list_provisioning.py`'s
  `ProvisioningPlan`; refuses the entire plan outright if
  `blocking_findings` (duplicate-titled lists) is non-empty, before any
  deletion or creation step is processed — the non-optional core safety
  contract `detect_duplicate_lists` exists to enforce.
- `scripts/spo-provision-calendar.ps1` — consumes
  `calendar_provisioning.py`'s `CalendarProvisioningPlan`; structurally
  prevents the real, confirmed SPO platform bug where Start/End declared as
  site columns silently breaks calendar-view rendering, by refusing any
  `list_creation.template` other than 100 and always submitting Start/End
  list-scoped (`-List <title>`), never as a bare site column.

All four are dry-run by default; a real write additionally requires
`-Execute` plus the script's own literal `-ConfirmToken`
(`PROVISION-SPO-SITE-COLUMNS` / `PROVISION-SPO-CONTENT-TYPES` /
`PROVISION-SPO-LIST` / `PROVISION-SPO-CALENDAR`), and reuse the canonical
`Get-WorkbenchConnectionConfig.ps1` (owned by `workbench-setup`, symlinked
into this plugin's `scripts/` root). See each script's own comment-based
help for its exact plan JSON shape and any honest design seam where the
Python module's `to_dict()` doesn't carry a field this script's cmdlet
sequence needs (mirroring `sharepoint-content-migration`'s
`spo-migrate-list-items.ps1` and `sharepoint-link-remediation`'s
`spo-remediate-document-content-links.ps1` seams). `sharepoint-provisioning`
itself was not touched — it still ships zero tenant I/O.

## A fifth, standalone skill: `plan-sharepoint-deployment-waves`

Exposes `wave_planning.plan_waves()` directly for a caller that already has a dependency-annotated
object list and just needs wave order — the same primitive stage 3a's `build_dependency_matrix`
uses internally, without the matrix-shaping/completeness-check layer around it. Moved here from
`sharepoint-provisioning` on 2026-08-08 (see that skill's own Provenance section) — provisioning
never called it internally, only exposed it; the plugin that actually builds on it (this one) now
owns it directly.

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
  `discover-sharepoint-site-inventory` validates an export directory a human already produced; it
  never connects to a tenant itself.
- Whether stage 3a should also accept `sharepoint-provisioning`'s existing `ListDef`/
  `ContentTypeDef`/`FieldDef` shapes directly as an alternative input, or only a raw export.
- Full field-level schema synthesis inside generated wave scripts — the dependency matrix carries
  only `name`/`objectType`/`dependsOn`, so each generated script's `build_schema()` is an honest
  `NotImplementedError` TODO, filled in by hand before a wave is actually run.
