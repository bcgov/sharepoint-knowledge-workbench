# Resume — Phase 1–4 Merged; Phase 4.5 Waves 0–6 COMPLETE; Wave 7 authorized, not started

> **2026-08-01 update (Waves 4-6, same session, human pre-authorized execution of Waves 5-8 with
> per-wave commits, direct execution not yet independently reviewed):**
>
> - **Wave 4 (`canonical-knowledge`):** ✓ COMPLETE, committed (`2a210e6`), pushed. Extracted
>   `convert.py`/`chunking.py`/`package.py`/`canonical_package.py`/`dispositions.py`/
>   `media_disposition.py`/`publication_map.py`/`hashing.py`/`validate_canonical.py`/
>   `atomic_output.py` wholesale, plus the `canonical-package`/`publication-map` contract
>   dataclasses (materialized as `canonical_schema/`). Fixed five real cross-plugin-dependency
>   violations via local duplication (`chunk_identity`/`chunk_grouping`/`pandoc_cleanup`/
>   `plan_verification`/`emf_convert`), including a genuine `cli.py` bug (caught the wrong
>   `PlanVerificationError` class after `convert.py` moved). 173/173 tests, isolated-install proof
>   passed. See `docs/superpowers/plans/phase-4-5-evidence/wave-4-canonical-knowledge-split-decision.md`.
> - **Wave 5 (`knowledge-publication`):** ✓ COMPLETE, committed (`199343e`), pushed. Extracted
>   `renderers/` (protocol, multipage-markdown renderer, render validator) and the `RenderResult`
>   contract (renamed `render_result.py`; `docx-to-content/scripts/contracts.py` deleted outright,
>   zero remaining local consumers). Duplicated the full consumer-side chain needed to load/validate
>   a canonical package (`canonical_package`/`dispositions`/`hashing`/`publication_map`/
>   `atomic_output`/`path_safety`/`canonical_schema`) locally, since the render pipeline's
>   dependency graph runs deeper than the convert pipeline's did. 49/49 tests, isolated-install
>   proof passed. See `docs/superpowers/plans/phase-4-5-evidence/wave-5-knowledge-publication-split-decision.md`.
> - **Wave 6 (repository-wide reconciliation):** ✓ COMPLETE. Built
>   `combined_install_check.py` (all four plugin wheels co-installed in one clean venv, zero
>   collisions, each plugin's own suite passes) — caught and fixed a real bug in the harness itself
>   (`build_wheel()`'s alphabetical-last-wheel-in-shared-dir picking logic silently returned the
>   same wheel four times when building into one shared dist dir). Ran the real, non-skipped
>   golden-master proof: the CEIS manual converted through `canonical_knowledge.build_canonical_package`
>   → `knowledge_publication.render` (each stage in its own subprocess — `canonical-knowledge` and
>   `knowledge-publication` share several duplicated bare module names, so both cannot be imported
>   in one long-lived interpreter without a namespace collision; this is an expected architecture
>   boundary, documented in `docs/architecture/phase-4-5-target-architecture.md`) reproduces
>   `runs/ceis-manual-v2/`'s canonical-content and rendered-output trees byte-identically (modulo
>   documented run-specific fields: `generator-info.json`'s timestamp,
>   `render-result.json`'s absolute `output_files` paths). Hashes recorded in
>   `docs/superpowers/plans/phase-4-5-evidence/wave-6-golden-master-manifest.json`. New
>   `tests/integration/test_full_ceis_pipeline_across_plugins.py` executed with zero skips.
>   Not yet committed as of this note — commit immediately after, same session.
>
> **Combined test totals, end of Wave 6:** `source-document-extraction` 78,
> `knowledge-analysis` 70, `canonical-knowledge` 173, `knowledge-publication` 49,
> `docx-to-content` 171 (170 passed/1 skipped), `tools/phase-4-5-core-plugin-refactoring` 42
> (40 fast + 2 slow), repo-root `tests/integration/` 1 — see
> `docs/superpowers/plans/phase-4-5-evidence/wave-6-final-test-migration-ledger.md`.
>
> **Next action on resume: Wave 7** (retire approved compatibility facades — read the plan's Wave
> 7 section, `docs/superpowers/plans/2026-08-01-phase-4-5-core-knowledge-plugin-domain-refactoring.md`,
> before starting).


> **Phase 4.5 Status (2026-08-01, end of session):** Executing the approved nine-wave plan
> (`docs/superpowers/plans/2026-08-01-phase-4-5-core-knowledge-plugin-domain-refactoring.md`) on
> branch `phase-4-5-core-plugin-refactoring`.
>
> - **Wave 0:** ✓ COMPLETE, reviewed, committed, and pushed (commits `9b14629`, `ae9933a`, `99e4b87`).
> - **Wave 1:** ✓ COMPLETE, reviewed, committed, and pushed (commit `6ee91b3`, accepted). Its
>   shared-contracts-distribution decision was later corrected — see next bullet.
> - **⚠️ Two mid-Wave-2 architecture corrections (2026-08-01, same session, human-flagged):**
>   1. **Shared-distribution correction:** Wave 1's approved model — every plugin's
>      `pyproject.toml` depends on a shared, unpublished `knowledge-workbench-contracts` pip
>      distribution (`contracts/python/`) — made standalone plugin installation impossible and
>      conflicted with `.agent/rules/plugin-architecture-policy.md`'s plugin-independence rule.
>      **Corrected:** each contract is materialized inside its *producer* plugin's own package
>      (no shared pip dependency); `contracts/python/` and `runtime/python/` were **deleted
>      entirely** (not just reclassified — zero plugin ever ended up depending on either after the
>      fix). Full record:
>      `docs/superpowers/plans/phase-4-5-evidence/wave-2-contract-materialization-correction.md`.
>   2. **Flat-`scripts/`-layout correction:** the first fix still nested the plugin's code under
>      `src/source_document_extraction/...` — that nesting was itself corrected in the same session
>      to a **flat `scripts/` directory** (bare module names, e.g. `scripts/extraction.py`; cohesive
>      multi-file families grouped into a subfolder, e.g. `scripts/pandoc/`, `scripts/schema/`),
>      matching `docx-to-content`'s own pre-existing convention exactly. This also surfaced and fixed
>      a real bare-name collision (`contracts/` collided with `docx-to-content/scripts/contracts.py`,
>      an unrelated pre-existing module — renamed to `schema/`) and a self-shadowing bug in
>      `docx-to-content`'s compatibility shim files (deleted entirely rather than rewritten, since
>      `pip install -e`'d `source-document-extraction` now supplies those bare names directly). Full
>      record: `docs/superpowers/plans/phase-4-5-evidence/wave-2-flat-scripts-correction.md`.
>
>   Spec amended (§13d, Revision 4), `wave-1-decisions.json` updated
>   (`shared_contract_decision_approved: false`), plan amended (Waves 2-5 common sequence + Wave 6
>   combined-install script, both correction notices), isolated-install harness rewritten
>   (`isolated_install_check.py` no longer co-installs a contracts wheel; new
>   `check_no_workbench_family_dependency()` static gate; `--import-package extraction`, not a
>   package name). **Read both correction docs before starting Wave 3** — Wave 3's
>   `knowledge-analysis` is the first plugin to implement the consumer side (generated local schema
>   copy) of the corrected contract model, using the flat `scripts/` layout from the start.
> - **Wave 2:** ✓ COMPLETE, corrected twice, and fully re-verified (this session, direct execution
>   — not yet independently reviewed). `plugins/source-document-extraction/` is a real,
>   **standalone-installable** package with a **flat `scripts/` layout**:
>   ```
>   plugins/source-document-extraction/scripts/
>   ├── extraction.py        # public interface: extract_and_normalize()
>   ├── dependencies.py
>   ├── emf_convert.py
>   ├── heading_parsing.py
>   ├── path_safety.py
>   ├── schema/              # this plugin's own schema for what it produces (was `contracts/` -- renamed, real name collision)
>   │   └── normalized_source_document.py
>   └── pandoc/              # cleanup + validation, one family (was `pandoc_fixes/`; `validate.py` folded in)
>   ```
>   `extract_and_normalize` produces `normalized-source-document` v1, validated against this
>   plugin's own materialized `scripts/schema/normalized_source_document.py` (authoritative — this
>   plugin is the producer) plus `references/contracts/normalized-source-document.md` (symlinked
>   into `skills/extract-docx/references/contracts/` via `symlink_manager.py`). Old
>   `docx-to-content` compatibility shim files (`dependencies.py`, `emf_convert.py`,
>   `pandoc_validate.py`, `path_safety.py`, `pandoc_fixes/*.py`) were **deleted**, not rewritten —
>   `docx-to-content`'s existing bare imports now resolve directly to the installed
>   `source-document-extraction` package. **Plugin Self-Containment Gate passed**:
>   `isolated_install_check.py --plugin source-document-extraction --import-package extraction`,
>   exit 0, real wheel build in a clean venv, **zero other workbench distribution installed or
>   importable**. Dependency-boundary check: zero violations. Test counts:
>   `source-document-extraction` 78/78 passed (isolated, standalone, both editable-install and real
>   wheel-install); `docx-to-content` 452 passed/1 skipped (down from 529/1 — tests relocated, not
>   lost; see `docs/superpowers/plans/phase-4-5-evidence/wave-2-test-migration-ledger.md`);
>   `tools/phase-4-5-core-plugin-refactoring` 40/40 passed. `symlink_manager.py diagnose`: all links
>   OK. **Not yet committed to git as of this note being written — commit immediately after this
>   edit, in the same session.**
> - **Wave 3 (knowledge-analysis):** ✓ COMPLETE (same session, direct execution — not yet
>   independently reviewed). `plugins/knowledge-analysis/` extracted as a real,
>   **standalone-installable** package with a flat `scripts/` layout from the start:
>   `recommend_from_normalized(normalized_source_document: dict) -> dict` (analysis-plan v1),
>   composing `identity.py`/`topic_grouping.py`/`plans.py` (moved **wholesale**, plus 4 of
>   `contracts.py`'s 15 dataclasses — `SourceFingerprint`/`StructuralAnchor`/`Confirmation`/
>   `ConversionPlan` — materialized as this plugin's own authoritative `plan_schema/analysis_plan.py`,
>   since this plugin is the sole producer of `analysis-plan`). `docx-to-content/scripts/analyze_structure.py`
>   rewritten as a pure compatibility orchestrator: composes the installed `source-document-extraction`
>   + `knowledge-analysis` packages, merges in the still-local `media_disposition.py` proposal
>   (unmoved, `canonical-knowledge` domain), writes both output files. Full decision record + two
>   real bugs found and fixed (a `hashing` bare-name collision with `docx-to-content`'s own
>   `hashing.py` — fixed by naming this plugin's module `plan_hashing.py`; an
>   `analyze_structure.iter_heading_matches` re-export loss that broke `chunking.py` — fixed by
>   importing directly from `heading_parsing`):
>   `docs/superpowers/plans/phase-4-5-evidence/wave-3-analysis-plan-split-decision.md`.
>   **Plugin Self-Containment Gate passed**: `isolated_install_check.py --plugin knowledge-analysis
>   --import-package analysis`, exit 0, zero sibling distribution installed or importable.
>   Dependency-boundary check: zero violations. Test counts: `knowledge-analysis` 70/70
>   passed (isolated, standalone); `docx-to-content` 393 passed/1 skipped (down from 452/1 — tests
>   relocated, not lost); `source-document-extraction` unaffected, 78/78;
>   `tools/phase-4-5-core-plugin-refactoring` 40/40 (after fixing a stale test-count threshold in
>   `test_wave0_test_ledger.py`). `symlink_manager.py diagnose`: all 26 links OK. **Not yet
>   committed to git as of this note being written — commit immediately after this edit, in the
>   same session.**
> - **Wave 4 (canonical-knowledge):** AUTHORIZED TO START IN THE NEXT SESSION. **NOT STARTED.**
>   Consumes `analysis-plan` (confirmed), produces `canonical-package`/`publication-map` via
>   `build_canonical_package`. Known File Inventory assigns it: `validate_canonical.py`,
>   `package.py`, `canonical_package.py`, `chunking.py`, `dispositions.py`, `media_disposition.py`,
>   `identity.py` (**a fresh copy** — Wave 3 already moved the analysis-side copy to
>   `knowledge-analysis`; `chunking.py`'s reconciliation needs its own, since cross-plugin imports
>   are prohibited), `publication_map.py`, `hashing.py` (the REMAINING `docx-to-content` one, for
>   `content_hash`/`canonical_json_bytes` — check for bare-name collisions against
>   `knowledge-analysis`'s `plan_hashing.py` and `source-document-extraction` before naming
>   anything), plus `convert.py`'s canonical-knowledge half and `atomic_output.py` (materialized
>   fresh, not from a shared runtime distribution — see the Wave 2 contract-materialization
>   correction doc). `plans.py`'s `confirm_plan`/`verify_plan_against_source`/`verify_plan_integrity`/
>   `require_confirmed` stayed in `knowledge-analysis` per Wave 3's decision — `canonical-knowledge`
>   consumes a *confirmed* plan dict, it does not need those functions itself; read
>   `wave-3-analysis-plan-split-decision.md` before assuming otherwise. **Grep every other plugin
>   for any bare module/package name before picking one** — both Wave 2 (`contracts`/`schema`) and
>   Wave 3 (`hashing`/`plan_hashing`) hit real collisions from skipping this.
>
> **Wave 1 accepted decisions (binding for Wave 2 onward):**
> - `analyze_structure.py` ownership split approved: `source-document-extraction` owns every
>   source-observation function (`_run_pandoc_raw`, heading parsing, statistics, defect
>   detection); `knowledge-analysis` owns only semantic interpretation (topic-boundary reasoning,
>   `recommend_strategy`). See `docs/superpowers/plans/phase-4-5-evidence/wave-1-analyze-structure-split-decision.md`.
> - `cli.py::cmd_analyze` remains the compatibility orchestrator (not `analyze_structure.py::analyze_document`).
> - `knowledge-workbench-contracts` (`contracts/python/`) remains contract/schema-only — no
>   executable runtime logic ever goes here.
> - `knowledge-workbench-runtime` (`runtime/python/`) owns approved shared runtime primitives —
>   currently only `atomic_output.py`'s `create_staging_dir`/`promote`. Explicitly **not** a
>   general-purpose shared-utility dumping ground; adding anything else requires the same kind of
>   explicit human decision this got. See spec §13c.
> - `orchestrate-conversion` remains `RETAINED_PUBLIC_ORCHESTRATOR` — the public workflow
>   orchestrator, not retired in Wave 6 as the plan's original example proposed.
> - `analyze-document`, `convert-document`, `render-content` remain `TEMPORARY_COMPATIBILITY_WRAPPER`.
> - **All four original skills (including `orchestrate-conversion`) are reassessed in Wave 7**
>   using the final consumer scan — none pre-approved for removal.
> - Five dependency edges remain genuinely unresolved for later boundary decisions (`package.py ->
>   topic_grouping.py`, `topic_grouping.py -> identity.py`, `renderers/protocol.py ->
>   canonical_package.py`, `renderers/validate_rendered.py -> path_safety.py`,
>   `validate_canonical.py -> pandoc_validate.py`) — see `wave-0-classified-edges.json`.
> - **No plugin extraction has started.** `plugins/docx-to-content/` is still the only running
>   plugin.
>
> **Current test baseline (end of Wave 1):**
> - Contracts distribution (`contracts/python/`): 21 passed
> - Runtime distribution (`runtime/python/`): 5 passed
> - Phase 4.5 tooling (`tools/phase-4-5-core-plugin-refactoring/`): 38 passed, 1 slow test passed
> - Existing `docx-to-content` suite: 529 passed, 1 skipped (unchanged by Waves 0–1)
>
> **`origin/main` currency:** ✓ `phase-4-5-planning` was merged to `main` via PR #11 (`8a7b977`) and
> the Phase 4 exit-gate reconciliation merged via PR #12 (`98c1943`). Waves 0–1 live only on
> `phase-4-5-core-plugin-refactoring` (not yet merged to `main` — merge is not authorized until the
> full plan's exit gate, per the plan's own git workflow).
>
> **Registered-worktree note:** `git worktree list` shows only the current checkout as registered.
> The three `.worktrees/phase-4-native-sharepoint-skills/`, `.worktrees/phase-3-governed-sharepoint-pilot/`,
> `.worktrees/phase-3-0-tenant-capability-discovery/` directories found on disk are classified
> `ORPHANED_BROKEN_WORKTREE` (Wave 0 Step 7 evidence — stale `.git` pointers to this repo's
> pre-rename path). **Do not delete, repair, or touch them** — out of scope until Wave 7 Step 1's
> re-classification.
>
> **Next actions (start of next session):**
> 1. Start a fresh session, read this file in full.
> 2. **Before writing any Wave 2 code**, read
>    `docs/superpowers/plans/2026-08-01-phase-4-5-core-knowledge-plugin-domain-refactoring.md`'s
>    "Waves 2-5 — Extract Each Plugin as a Real Installable Package" section in full — the 11-step
>    common sequence (scaffold → fixture generation → failing test → move/adapt code → ledger
>    migration → compatibility shim → skill/README → dependency-boundary check → isolated-install
>    gate → commit) and Wave 2's specific row in that section's Public Interface Contract table
>    (`extract_and_normalize`, consumes nothing, produces `normalized-source-document`). The
>    decisions summarized above are what to build; that section is how — do not improvise the
>    mechanics from the summary alone.
> 3. Begin Wave 2 (`plugins/source-document-extraction/`) per that plan section and the Wave
>    1-approved decisions above: extract DOCX/Pandoc source handling and the Wave 1-approved
>    source-observation functions; produce the `normalized-source-document` contract; prove wheel
>    build, isolated installation, public import, and independent tests; maintain the existing 529
>    passed/1 skipped baseline; preserve byte-identical accepted output.
> 4. Do not begin Wave 2 work retroactively tonight — this session stopped deliberately at the
>    Wave 1 checkpoint with no Wave 2 files created.

> **Phase 4 Status (2026-08-01):** ✓ COMPLETE & MERGED. Tasks 0–12 executed and merged to `main` via PR #9 (commit `e66fe02`); exit-gate evidence reconciled against real per-task reports (see Phase 4.5 note above).
> - Tasks 0–7.5: Accepted (entry gate, vendor evaluation, deployment prep, normal-case eval)
> - Task 8: Scope drift reconciled; native skill deployed & verified (hash 9586379f...)
> - Task 9: Metadata visibility probe passed (7/7 fields, full structured access)
> - Task 10: Permission evaluation waived (licensing blocker; SharePoint security understood)
> - Task 11: Safety evaluation passed (12/12 tests, zero blocking issues)
> - Task 12: Rollback exercise complete (restoration verified) — see `EVID-PHASE4-TASK12-ROLLBACK-COMPLETION.md`
>
> **Exit Gate Verdict:** ✓ ACCEPTED — Phase 4 exit criteria satisfied (reconciled 2026-08-01, see above)
> **Phase 4 merge:** Merged to main (commit 395c49f in the branch history; PR #9 merge commit `e66fe02` on `main`)
> **Test results:** Phase 4 (49 passed), docx-to-content plugin (529 passed, 1 skipped)
> **Research preserved:** All Phase 5 candidate scripts and learnings retained
> **Phase 5 authorization:** AUTHORIZED pending Phase 4.5 execution (Phase 4.5 is now planned and spec/plan-approved, not yet executed — see above)
>
> **Phase 3 Exit Gate Status (2026-07-30):** COMPLETE & MERGED.
> All 6 tasks of `docs/superpowers/plans/2026-07-30-phase-3-governed-sharepoint-knowledge-pilot.md` executed. Pure-Python tooling (`sharepoint_package.py`, `sharepoint_dry_run.py`, `sharepoint_reconcile.py`, `sharepoint_cli.py`) built under TDD (529 tests passing). Automated PnP.PowerShell script (`run-phase3-tenant-pilot.ps1`) executed against live SharePoint tenant site `AG-CSB-intranet-dev`, publishing all 25 CEIS topic pages and 319 media files directly into dedicated Document Library `CEISPilotKnowledge/` as formatted HTML with custom metadata (`TopicId`, `PackageIdentity`, `PublicationOrder`, `TopicContentSHA256`, `SourceDocumentSHA256`). Reconciliation against `actual-state.csv` verified **100% MATCH** with zero issues (`package_identity: sha256:041e1186...`).

## Mandatory Planning Protocol for Phase 3 and Every Future Phase

This protocol is authoritative for future phase planning. External review is an additional quality gate; it never replaces the required Superpowers workflow.

### Required workflow

For each new phase, subphase, major architecture change, repository restructure, plugin extraction, or runtime target:

```text
1. Read start-here.md and the master initiative plan.
2. Verify repository state and phase-entry evidence.
3. Run superpowers:brainstorming.
4. Record confirmed decisions, recommendations, assumptions, missing facts, and contradictions.
5. Perform reconnaissance against real files and contracts.
6. Draft the design specification.
7. Obtain required human review or approval.
8. Run superpowers:writing-plans.
9. Review the plan adversarially.
10. Obtain explicit approval before implementation.
11. Create the phase branch/worktree.
12. Execute the approved plan.
13. Satisfy the exit gate before merge.
14. Update start-here.md after merge; start the next phase in a fresh session.
```

Never skip brainstorming because detailed direction already exists, the work looks simple, the artifact is called a draft, a low-cost model can write it quickly, or GPT/Opus review will occur later. Brainstorming distinguishes settled decisions from recommendations, provisional design, tenant-dependent facts, ambiguity, and blockers; it does not re-litigate accepted decisions.

### Mandatory brainstorming record

Before a specification or implementation plan is written, create a concise record with:

```text
CONFIRMED DECISIONS
RECOMMENDATIONS REQUIRING REVIEW
MISSING FACTS OR ENTRY-GATE EVIDENCE
CONTRADICTIONS OR AMBIGUITIES
BOUNDED PHASE OUTCOME
NON-GOALS
RISKS AND FAILURE MODES
DECISIONS NEEDED FROM A HUMAN
```

Use `CONFIRMED`, `RECOMMENDED`, `PROVISIONAL`, `DEFERRED_UNTIL_EVIDENCE`, `BLOCKED`, `RESEARCH`, and `REJECTED_FOR_NOW`. Never use `TBD` alone. Every unresolved item states why it matters, evidence needed, decision owner, latest responsible decision point, and safe default.

### Source-reading and evidence discipline

- Read every required file in full or report it as unavailable, empty, malformed, generated, or a stub.
- If a substantive file appears to contain only one line, inspect size and line endings; check for escaped newlines, links, pointers, or placeholders; open the underlying target; and do not claim review until the content was actually reviewed.
- Verify claims against current repository files, schemas, tests, manifests, git state, and accepted evidence.
- Vision and research documents provide direction; they do not prove implementation or authorize work.
- Near phases become implementation-ready only when their entry-gate evidence exists.
- Far phases retain structure and evidence gates without fabricated implementation details.
- Tenant-dependent values come from observed tenant evidence, not generic documentation or model memory.
- Never invent URLs, library names, field types, identities, licences, permissions, API behaviour, or commands.

### Planning is not implementation

Unless expressly authorized, planning does not modify a tenant, create SharePoint artifacts, request or grant Entra permissions, scaffold plugins, rename or restructure the repository, migrate every research item into the backlog, merge branches, or start a later phase.

### Reviewer/implementer state disputes

When an external reviewer (or a fresh session) flags issues an implementer believes are already fixed, do
not resolve it with competing prose summaries — a summarized grep ("all hits are in correction notes") is a
conclusion, not evidence. The deterministic resolver is:

1. Implementer posts `git rev-parse HEAD`.
2. Implementer posts the raw `grep -n` (or equivalent) output — the actual lines, not a description of them.
3. Reviewer re-reviews against that exact commit.

This came up concretely during Phase 3 spec review: an external reviewer's second pass flagged several
"still broken" findings that were, in fact, already fixed in the current commit — the reviewer had been
shown a stale, pre-fix copy (uploaded once, not refreshed after the fix landed). Posting the commit hash
and raw grep output resolved the dispute in one round instead of costing a repeat review cycle. When
sending documents to an external reviewer, give them the exact commit hash explicitly so they don't hit
the same stale-copy problem.

### Model-cost discipline

Use the cheapest capable model without weakening the workflow:

```text
Low-cost: inventory, link checks, mechanical tables, approved scaffolding,
fixtures, established validation commands, evidence collation.

Mid-tier: non-trivial refactoring, schemas, validators, reconciliation logic,
test design, migration logic, debugging.

Strong reasoning: architecture, adversarial brainstorming, source-of-truth,
security/permission boundaries, ambiguous contracts, plan review, acceptance.
```

Escalate only when architecture, ambiguity, security, cross-plugin impact, failed tests, or contradictory evidence requires it.

### Git and repository hygiene

Persistent specs, plans, decisions, reports, and evidence belong in approved tracked paths, not only under ignored scratch directories. Keep transient state ignored at every depth, including `.superpowers/`, `__pycache__/`, `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`, and `.DS_Store`. Do not automatically ignore `.github/`, `.claude-plugin/`, agent definitions, skills, scripts, tests, or approved documentation.

Before merge, report focused tests, the full suite, required evidence, documentation changes, plugin/marketplace metadata disposition, `git status --short`, and all retained warnings or deferred decisions.

### Phase 3 two-state rule

```text
Before Phase 3.0 evidence:
brainstorming + draft specification + evidence-consumption matrix +
unresolved-decision register + implementation-plan scaffold.

After Phase 3.0 evidence:
replace assumptions with observed facts + finalize the implementation-ready
Phase 3 plan + obtain approval before execution.
```

Phase 3 is not implementation-ready until an accepted `tenant-capability-report.md` exists and every blocking dependency maps to observed evidence.

Required pre-discovery outputs:

```text
phase-3-governed-sharepoint-knowledge-pilot-spec.md
phase-3-tenant-evidence-consumption-matrix.md
phase-3-unresolved-decisions.md
phase-3-governed-sharepoint-knowledge-pilot-plan-scaffold.md
Phase 3 evidence-package proposal
```

Phase 3 brainstorming must examine the smallest coherent pilot and publication unit, field-level authority, direct editing and drift, package-only deployment, reconciliation, republish/rollback/rename/retirement, permission and Protected B discoverability risks, stage-versus-exit-gate contradictions, and tenant facts Phase 3.0 must establish.

### Forward-Phase Specification and Plan Scaffolds

Forward-phase planning artifacts now exist for Phases 4–8:

```text
docs/superpowers/specs/phase-4-native-sharepoint-skills-pilot-spec.md
docs/superpowers/plans/phase-4-native-sharepoint-skills-pilot-plan-scaffold.md

docs/superpowers/specs/phase-5-sharepoint-knowledge-agent-pilot-spec.md
docs/superpowers/plans/phase-5-sharepoint-knowledge-agent-pilot-plan-scaffold.md

docs/superpowers/specs/phase-6-multi-runtime-capability-model-spec.md
docs/superpowers/plans/phase-6-multi-runtime-capability-model-plan-scaffold.md

docs/superpowers/specs/phase-7-cowork-copilot-studio-evaluation-spec.md
docs/superpowers/plans/phase-7-cowork-copilot-studio-evaluation-plan-scaffold.md

docs/superpowers/specs/phase-8-scale-promotion-operations-spec.md
docs/superpowers/plans/phase-8-scale-promotion-operations-plan-scaffold.md
```

See:

```text
docs/superpowers/FUTURE-PHASE-PLANNING-INDEX.md
```

These files are architectural head starts only.

They are not:

- approved implementation plans;
- evidence that a phase entry gate is satisfied;
- authorization to create SharePoint skills or agents;
- authorization to build Cowork or Copilot Studio solutions;
- permission to skip Superpowers brainstorming;
- permission to start later phases automatically.

When a future phase becomes active:

```text
verify entry gate
→ start fresh session
→ create branch/worktree
→ run superpowers:brainstorming
→ review and rewrite specification in place
→ replace assumptions with observed evidence
→ run superpowers:writing-plans
→ adversarially review final plan
→ obtain explicit implementation approval
```

Do not create duplicate `-old`, `-final`, or `-v2` artifacts merely because a scaffold is being refined.
Preserve history through Git.

Current next action remains Phase 3 planning. The existence of Phase 4–8 files does not change phase order
or authorization.

## Planning Artifacts (read these first, in this order)

1. `docs/vision/master-initiative-plan-workstreams-and-phases.md` — the whole-spectrum master plan
   (Phase 1 through 8, plus 3.0 and 5.5), with a git/session workflow every phase follows (branch/worktree
   per phase, commit per task, exit-gate-is-merge-gate, update this file, start the next phase in a fresh
   session). Went through external adversarial review (round 3/4, `temp/plan-reviews/full-plan-review/`).
2. `docs/superpowers/specs/2026-07-28-phase2-canonical-publication-contract-hardening-design.md` — the
   approved Phase 2 design spec.
3. `docs/superpowers/plans/2026-07-28-phase2-canonical-publication-contract-hardening.md` — the approved,
   18-task (Task 0–17), TDD-ready Phase 2 implementation plan. Three rounds of external review behind it
   (`temp/plan-reviews/`, `temp/plan-reviews/phase2/`, `temp/plan-reviews/full-plan-review/`). **All 18
   tasks executed and merged to `main`** — see the "Phase 2 ... complete" section below for full evidence.
4. This file, below — Phase 1 and Phase 2's detailed history and verified status. Trust this over any
   other handoff summary; verify against `git log` regardless.

**Actual next action, in order:**
1. **Phase 1 is fully complete** — the `fix-grid-table-rendering-defect` PR (#2) is merged to
   `origin/main`, and the human spot-check pass (rows 1, 2, 3, 4, 6 of
   `runs/ceis-manual-v2/evidence-report.md`'s checklist) was completed as a human+agent walkthrough. Row 5
   remains N/A (genuinely no footnotes in the source). Nothing further is needed on Phase 1.
2. **Phase 2 (Canonical/Publication Contract Hardening) is fully complete and merged to `main`** — all 18
   tasks (0–17) executed via `superpowers:subagent-driven-development`, two independent final whole-branch
   reviews performed (both dispositioned, all Important/real-bug findings fixed and re-reviewed clean), the
   golden-master proof passed (real CEIS manual publication content byte-identical to the Task 0 baseline),
   full suite green at 509 passed/1 skipped, merged via PR into `origin/main`. See the "Phase 2 ... complete"
   section below for full detail.
3. **Begin Phase 3 planning in a new session** — do not continue in the same long-running session that did
   Phase 1/Phase 2 execution. The Mandatory Planning Protocol above is binding. External review never substitutes for brainstorming or reconnaissance. Per the master plan's phase-gating discipline, Phase 3 is only planned at a
   structural level today (gated on evidence — tenant facts, pilot outcomes — that doesn't exist yet); read
   `docs/vision/master-initiative-plan-workstreams-and-phases.md`'s Phase 3 section before scoping detailed
   work. **Do this planning work via the `superpowers` skills, in this order:**
   1. `superpowers:brainstorming` — work through Phase 3's open questions and design decisions with the
      human partner first (do not skip straight to writing a spec/plan).
   2. Once the design is settled, write the Phase 3 design spec (following the same pattern as
      `docs/superpowers/specs/2026-07-28-phase2-canonical-publication-contract-hardening-design.md`),
      under `docs/superpowers/specs/`.
   3. `superpowers:writing-plans` — turn the approved spec into a TDD-ready, task-by-task implementation
      plan (following the same pattern as
      `docs/superpowers/plans/2026-07-28-phase2-canonical-publication-contract-hardening.md`), under
      `docs/superpowers/plans/`.
   4. Only after the plan is reviewed/approved does execution begin (in its own branch/worktree, via
      `superpowers:subagent-driven-development`, per the master plan's Per-Phase Git & Session Workflow) —
      that is a separate step from this planning work, not part of it.

## Authoritative Inputs (Phase 1 detail)

Before changing anything, read in full:

1. `docs/superpowers/specs/2026-07-25-docx-to-content-plugin-design-v3-ammendments.md` — the authoritative v3 spec (includes the v3.1 Deviation Notice, Section 14a authoring guidance, Section 14b future-output-profiles/SharePoint boundary).
2. `docs/superpowers/plans/2026-07-25-docx-to-content-phase1-implementation-plan-v3-ammendments.md` — the authoritative v3 plan for Tasks 0–16.
3. `docs/superpowers/plans/2026-07-28-docx-to-content-topic-grouping.md` — the plan for the grouped-strategy work (Tasks 1–9 of that plan), **complete and merged**.
4. `docs/implementation-baseline.md` — Task 0 reconnaissance findings (dated 2026-07-25; paths in it reference the pre-rename `sourcedocuments/`/`output/` directory names — historically accurate, not a live reference).
5. This file — the actual, verified current status. Trust this over any other handoff summary; verify against `git log` regardless.

The v1 spec/plan (`2026-07-25-docx-to-content-plugin-design.md` / `...-implementation-plan.md`, no `-ammendments` suffix) are superseded, kept only for historical comparison.

**Broader context:** this repo is Phase 1 of a larger initiative — see `docs/vision/README.md` and `docs/vision/ai-assisted-structured-knowledge-workbench-broader-plan.md` for direction beyond Phase 1 (repository/plugin boundaries, SharePoint delivery, agents, publication, evaluation). Those documents propose future direction; they do not authorize work beyond the current approved Phase 1 plan.

## Where the work lives

Historical Phase 1 and Phase 2 work is merged on `main`. Phase 3 planning and every future phase must begin on a dedicated branch/worktree per the master plan. Current implementation location:

```text
plugin path:   plugins/docx-to-content/
run tests:     cd plugins/docx-to-content && python3 -m pytest tests/ -q
```

Two commits landed this session on top of the prior session's merge (`99faab2`):
- `b325ae6` — mixed-level logical-root detection for the grouped topic strategy (topic_grouping.py's `classify_headings`, `confirmed_topic_roots` persisted on the plan, `.gitignore` hygiene: `.superpowers/`/`.pytest_cache/` at every depth, two tracked SDD reports preserved to `docs/reports/`).
- `40bf069` — general media-disposition mechanism (`media_disposition.py`, `plans.apply_media_decision`, `ConversionPlan.media_decisions`, `validate_canonical._check_media_decisions`) plus two real-document convert fixes (glued-image heading-identity normalization; preamble-aware content-loss comparison).

Check `git log origin/main..main --oneline` before assuming remote state matches local — confirm with the user before pushing.

## Actual Current Status (verified, not reported)

**Tasks 0–16 and Task 17-topic-grouping are complete** (see prior session detail in git history; `main` up through `90a6033`/merge `99faab2` documents itself).

**Task 18 (real CEIS pilot cutover) is now complete**, run end-to-end through the plugin CLI against the real document (`intake/CEIS MANUAL - working version.docx`):

1. **`analyze` rerun** found a real crash: `topic_grouping.compute_topic_boundaries` hardcoded "every level-1 heading starts a topic," but the real document authors its first 14 top-level sections as Heading 2 and the remaining 11 as Heading 1 (verified against raw docx XML — standard Word styles, no pandoc bug, a genuine source-authoring inconsistency; every section's children are consistently Heading 3, never a genuine Heading 2 child beneath a Heading 1). Fixed via `classify_headings`'s dynamic root-level tracking (`root`/`promoted-root`/`ambiguous-root`/`internal-heading` classification), with the confirmed root set persisted on the plan (`confirmed_topic_roots`) so `convert` consumes it rather than recomputing the heuristic.
2. **Real `proposed_topics` reviewed**: exactly 25 topics (14 at source level 2, 11 promoted from level 1), `MIXED_LOGICAL_ROOT_LEVELS`/`PROMOTED_TOPIC_ROOT` warnings surfaced and reviewed, zero ambiguous roots (the real document's inconsistency is one-directional).
3. **`strategy: "grouped"` set** on the draft plan (a process bug during this session set it only after an initial confirm defaulted to `"chunked"` — caught before proceeding, plan rebuilt with `strategy=grouped` preserving the already-reviewed `confirmed_topic_roots`/`media_decisions`, then reconfirmed).
4. **Preamble/image findings re-verified**: title ("Civil Electronic Information System")/subtitle ("SEARCHABLE GUIDE")/version ("Version 1.9") → publication metadata; `Ctrl+F` instruction → omitted; Word TOC → raw dump detected, removed and regenerated from the publication map; `image1.png` → directly inspected (not inferred from dimensions), found to be a stale (2021-02-11) Internet Explorer browser-window screenshot of the CEIS-in-Motion portal landing page (OS taskbar, tab bar, address bar, active Find-toolbar search state all visible; the CEIS wordmark is embedded within it, not a standalone branding asset) — classified `obsolete-source-layout-artifact`, dispositioned `omit-as-reviewed-artifact` (not cropped — cropping would have manufactured an unapproved derived branding asset). This is the first real use of the new general media-disposition mechanism (see below).
5. **Explicit human plan confirmation obtained** before any `confirm`/`convert`/`render` ran (spec Section 7.1/7.2 gate honored).
6. **`confirm` → `convert` → `render` run against the real document**: `convert` validation status **PASS**, 159 structural anchors retained for lineage, 25 topic chunks, every anchor assigned to exactly one topic, `publication-map.json` present (25 entries, contiguous order 0–24). `render` validation status **PASS**, 25 pages, `index.md` in publication-map order, no raw TOC survived, `image1.png` confirmed absent from both canonical and rendered media.
7. Output lives at `runs/ceis-manual-v2/` (canonical-content + render/rendered-output). **Decision (user-confirmed): kept side by side with the old pre-plugin `runs/ceis-manual/`, not replaced** — the old directory is retained deliberately as historical evidence of the bare-pandoc problem the plugin was built to solve; `runs/ceis-manual-v2/` is the current, authoritative, plugin-produced output. `CLAUDE.md`'s "Conversion workflow" section has been updated to describe both and say so explicitly.

**Two real, generalizable defects were found and fixed while running the real document for the first time** (every prior test used synthetic fixtures that happened not to exercise these paths):
- Heading-identity divergence for a heading with an image glued directly onto its own line: `analyze_structure._normalize_heading_text` now also applies `pandoc_fixes.images.fix_glued_images` (previously only `strip_whole_heading_emphasis`, Task 17's fix for a different divergence of the same class), matching what convert's cleanup pipeline actually does before reconciliation.
- Content-loss/duplication false positive on any document with non-empty preamble content: `convert.py`'s `_run_conversion_pipeline` now compares staged chunk content against **preamble-stripped** cleaned text (`sliced_document.preamble` is never copied into any chunk by design — chunking.py — but the validation comparison was using the full cleaned document, which every synthetic test fixture's empty preamble had masked).

**General media-disposition mechanism added** (`scripts/media_disposition.py`, `plans.apply_media_decision`, `ConversionPlan.media_decisions`, `validate_canonical._check_media_decisions`), scoped deliberately to preamble media only (the one concrete integration point that exists today — `SlicedDocument.preamble`, never copied into canonical output). `analyze` proposes objective-signal-only records (`requires-human-review`/`requires-human-decision`) for every preamble media reference; a human confirms the real classification/disposition via `plans.apply_media_decision` before `confirm`; a still-pending record blocks conversion (`unclassified_media`), a reviewed omission does not. **Full body-content media classification** (screenshots inside procedures, decorative-vs-meaningful, derived-asset authorization workflow) was explicitly scoped OUT as future work — not attempted this session.

Full plugin suite as of this session's last commit (`40bf069`): **448 passed, 1 skipped**.

### What is NOT done yet — explicitly withheld pending further direction

- **General (non-preamble) media classification/disposition** — screenshots inside procedures, decorative-vs-meaningful classification, derived-asset authorization — is future work per the media-disposition mechanism's deliberately narrow Task 18 scope.
- **Nothing has been pushed to `origin`** — `main` is ahead of `origin/main` (check exact count via `git log origin/main..main --oneline`); confirm with the user before pushing.

## Evidence-report assembly, a real defect found AND fixed, real output regenerated (this session)

Assembled `runs/ceis-manual-v2/evidence-report.md` (spec Section 10's required Task 17/18
deliverable, never previously produced) by reconciling `manifest.json`/`validation.json`/
`renderer-validation.json`/`analysis-report.json`/chunk metadata against each other. This
surfaced a real defect, not just a documentation gap — and it has since been **fixed, verified,
and the real CEIS output regenerated**, not just described:

**The defect:** `image239.emf` (body content in `PROTECTION ORDERS`, not preamble) was absent
from both promoted canonical and rendered media, with a dead absolute-path reference baked into
both promoted outputs, and **both validators reported PASS with zero issues** despite it.

**Root cause:** the image's alt text contains a markdown-escaped `]` (from Word content quoting
"[Order Terminating a Protection Order]"). Four copies of the same naive regex —
`!\[[^\]]*\]\(...\)` — silently stop matching alt text at that literal `]` byte, so the reference
was never recognized as media at all, in: `convert.py`'s `_ABS_MEDIA_REF`, `package.py`'s
`_IMAGE_REF`, and **two** places in `validate_canonical.py` (`_IMAGE_REF_FOR_COMPARISON` and,
critically, `_IMAGE_REF` inside `_check_media_references` — the actual broken-link validator,
which never saw the reference to check it). `renderers/validate_rendered.py` carried the
identical bug on the render side.

**Fix:** all four sites now use `(?:[^\]\\]|\\.)*` for alt/link text — correctly treats `\]` as
an escaped literal rather than a terminator. A regression test was added first and confirmed
failing against the old code, then passing after the fix:
`tests/unit/test_package.py::test_alt_text_with_escaped_brackets_still_recognized_as_media_ref`.
Full suite: **449 passed, 1 skipped** (up from 448 — the new test executes, nothing else broke).

**Regeneration:** `convert` and `render` were rerun against the *same* confirmed plan (source and
plan unchanged — only pipeline code was fixed) via:
```bash
python -m scripts.cli convert --source "../../intake/CEIS MANUAL - working version.docx" --plan ../../temp/ceis-manual-analysis/conversion-plan.confirmed.json --output ../../runs/ceis-manual-v2
python -m scripts.cli render --canonical ../../runs/ceis-manual-v2/canonical-content --renderer multipage-markdown --output ../../runs/ceis-manual-v2/render
```
Both PASS. `runs/ceis-manual-v2/` now has **319/319** media files on both the canonical and
rendered sides (up from 318/318), `image239.png` present and correctly referenced as
`../media/image239.png` in both the canonical chunk and the rendered page — confirmed by direct
file inspection, not validator status alone. 159/159 heading anchors, 25/25 topic chunks
unchanged (the fix only affected media handling, not chunking/anchoring).

**Process gap, flagged for the record:** this rerun reused the already-approved confirmed plan
from Task 18 without explicitly telling the user that's what was happening — no new
chunking/strategy questions were asked because none were needed (nothing about topic boundaries
changed), but silently reusing an old approval rather than stating "reusing plan `<id>`, no
chunking changes, only the media fix is being validated" is a real gap against this project's
approval-gate conventions, caught by the user after the fact, not surfaced proactively. See the
governance note in `runs/ceis-manual-v2/evidence-report.md`'s header for the full note. Going
forward: any time a prior confirmed plan is reused rather than re-derived, say so explicitly
before running `convert`/`render` again, even when re-analysis is genuinely unnecessary.

**Update: also fixed.** Three more files carried the identical `[^\]]*` bug
(`pandoc_validate.py`'s `_IMAGE_LINK`/`_HEADING_WITH_IMAGE`, `analyze_structure.py`'s
`_IMAGE_REF`/`_LOCAL_LINK`/`_IMAGE_REFERENCE`, `pandoc_fixes/images.py`'s `_IMAGE`). Initially
left unfixed as "out of scope," which was a self-evolution-policy violation (Fix Forward, Never
Skip) caught by the user — fixed instead of deferred. Full suite still 449/1. Rerunning `analyze`
against the real document confirmed the fix: `image_reference_count` went from 341 → 342 (the
same `image239` reference now correctly recognized at analysis time too), all other counts
(159 headings, 185 local links, 25 topics) unchanged.

**Update (this session, resumed): completed.** The human spot-check checklist has now been
filled in — see `runs/ceis-manual-v2/evidence-report.md`'s "Human Spot-Check Checklist" section.
All applicable rows (1, 2, 3, 4, 6) were reviewed by a human (in-chat file review plus an
independent GitHub preview check for Row 3's inline images); Row 5 remains genuinely N/A (zero
footnotes in the source). **Phase 1's human sign-off precondition is satisfied; nothing further
is outstanding on Phase 1.**

## Table-detection/rendering defect found and fixed (later session, during human spot-check attempt)

While starting the human spot-check pass (row 6, viewing the last topic page,
`ceis-support-faq--218dfe1f.md`), a real defect surfaced: its rendered table had a spurious
`| --- | --- |` separator row injected after almost every data row, corrupting otherwise-valid
pandoc grid-table markup.

**Root cause:** `pandoc_fixes/tables.py`'s `fix_malformed_tables` was designed/tested only against
GFM-style pipe tables. Pandoc emits **grid tables** (bounded by `+---+`/`+===+` lines) for
complex/merged-cell Word tables — a format the function never recognized. Its `_PIPE_ROW` regex
matches every pipe-delimited row, including grid-table data rows; since the `+---+` boundary lines
reset internal `in_table` state, every content row looked like a fresh headerless pipe table,
triggering a spurious separator insertion after each one. A second, related defect shared the same
blind spot: `analyze_structure.py`'s `compute_statistics` only counted GFM-style separators toward
`table_count`, so this document (which has 3 grid tables, zero pipe tables) was reported as
`table_count: 0` — which had incorrectly justified marking spot-check row 2 as N/A.

**Fix:** `fix_malformed_tables` now recognizes grid-table boundary lines and passes grid-table
blocks through untouched (they already carry a valid `+===+` header separator). `compute_statistics`
now also counts grid-table header separators toward `table_count`. Regression tests added first,
confirmed failing against the old code, then passing after the fix:
`tests/unit/test_tables.py::TestFixMalformedTables::test_leaves_grid_table_untouched` and
`tests/unit/test_analyze_structure.py::test_table_count_detects_pandoc_grid_tables`. Full suite:
**451 passed, 1 skipped** (up from 449).

**Regeneration:** `analyze`, `convert`, and `render` rerun against the real document, reusing the
same already-approved `conversion-plan.confirmed.json` (stated explicitly before rerunning, per
this project's prior process-gap lesson — no new chunking/strategy/media questions were needed,
since only table-handling code changed). Both `convert` and `render`: **PASS**. Media (319/319) and
chunk/page counts (25/25) unchanged on both sides — the fix affected only table markup.
`analyze`'s `table_count` now correctly reports `3` (was `0`); other statistics (159 headings, 185
local links, 342 image references, 25 topics) unchanged. `evidence-report.md`'s checklist and
"Table-Detection and Rendering Defect" section updated with this finding; row 2 is no longer
marked N/A and now requires an actual human look, same as the other unresolved rows.

## Orchestrate-conversion skill (added this session, after Task 18)

Deferred work from before Task 18 is now done: `plugins/docx-to-content/skills/orchestrate-conversion/SKILL.md`
is a pure-instruction (no new code) skill that sequences the same
`analyze`/`confirm`/`convert`/`render` CLI calls the other three skills
already document, with the mandatory human plan-review and media-decision
gates made explicit (pause-and-summarize after `analyze`, inline
image-review + `plans.apply_media_decision` for unclassified preamble
media, loop until explicit approval before `confirm`, stop on any FAIL or
undispositioned WARN at `convert`/`render`). It has not yet had a real
dry run against an actual document in this session — do that before
relying on it for a second real conversion. No new tests were added since
no new code was written; full suite still 448 passed, 1 skipped
(unchanged, verified after adding the skill).

## Phase 2 (Canonical/Publication Contract Hardening) — complete, merged to main

All 18 tasks (0-17) of `docs/superpowers/plans/2026-07-28-phase2-canonical-publication-contract-hardening.md`
are complete, executed via `superpowers:subagent-driven-development` (fresh implementer + fresh reviewer
per task), and merged to `main` via PR. Two independent final whole-branch reviews were performed (one
found only a stale docstring; a second, more thorough review found one genuine cross-task integration bug
in `CanonicalPackage.load()`'s non-grouped branch — a malformed `publication-map.json` could escape the
module's documented `CanonicalPackageError` contract — plus stale contract-doc drift in
`publication-map-contract.md`/`canonical-contract.md`). All findings were fixed (a guard + regression test
for the bug, doc corrections for the drift) and independently re-reviewed clean before merge.

**Full suite: 509 passed, 1 skipped** (`python3 -m pytest tests/ -q` from `plugins/docx-to-content/`). The
1 skip is `tests/unit/test_package_load.py:189` ("small_single.docx fixture has no media references to
tamper with") — a pre-existing, unrelated fixture limitation, not Task 16's golden-master test.

**Task 16's golden-master test PASSED, not skipped** — this is the actual completion evidence, per Task
17's own explicit warning not to conflate the aggregate pass count with this specific proof:
```
tests/integration/test_golden_master.py::test_index_is_byte_identical_to_golden_master PASSED
tests/integration/test_golden_master.py::test_pages_are_file_set_identical_and_byte_identical_to_golden_master PASSED
tests/integration/test_golden_master.py::test_media_is_file_set_identical_and_byte_identical_to_golden_master PASSED
tests/integration/test_golden_master.py::test_control_metadata_is_semantically_correct_not_byte_identical PASSED
```
This proves the real CEIS manual's published output (`index.md`, all 25 `pages/**`, all 319 `media/**`
files) is byte-identical to the Task 0 pre-Phase-2 baseline — Phase 2 changed only internal contract
metadata, never a single byte of the actual publication content.

### Pre-existing tests whose assertions intentionally changed (Tasks 1, 2, 4)

- **Task 1** (`package_identity` double-prefix fix) — `tests/unit/test_package.py::test_grouped_package_identity_is_not_double_prefixed`
  is a new test (not a changed pre-existing one) asserting `package_identity == plan_id` and does not
  start with `sha256:sha256:`.
- **Task 2** (`source_manifest_hash` → `source_content_sha256` field rename):
  - `tests/contract/test_contracts.py::test_render_result_uses_source_content_sha256_not_manifest_hash` — new test for the renamed field.
  - `tests/unit/test_multipage_markdown.py::test_single_chunk_package_renders_one_page_and_index` — assertion changed from `result.source_manifest_hash == FAKE_SHA` to `result.source_content_sha256 == FAKE_SHA`.
  - `tests/unit/test_renderer_protocol.py` (`_ListChunksTestRenderer` fixture helper) — constructor kwarg renamed `source_manifest_hash=` → `source_content_sha256=`.
  - `tests/unit/test_validate_rendered.py::test_manifest_hash_mismatch_detected` — assertion changed from checking issue code `manifest_hash_mismatch` to `source_content_stale` (this test's name is stale/cosmetic per Task 2's own deferred-minor note; the assertion body is correct).
- **Task 4** (`chunk_id` now holds a real chunk ID, not a path; `parent_topic_id` removed):
  - `tests/unit/test_multipage_markdown.py` (`_build_synthetic_grouped_package` fixture helper) — `chunk_id="chunks/alpha--22222222.md"` → `chunk_id="alpha--22222222"` (and same for `beta--11111111`).
  - `tests/unit/test_publication_map.py::test_publication_map_supports_parent_topic_id_hierarchy` — no longer passes `parent_topic_ids=` to `build_publication_map`; now asserts `"parent_topic_id" not in as_dict["entries"][0]` instead of asserting the field is `None`.

Every other pre-existing test not listed above still passes unchanged.

## Phase 3.0 (SharePoint Tenant-Capability Discovery) — substance largely done, formal exit gate NOT met

Per `docs/vision/master-initiative-plan-workstreams-and-phases.md`'s Phase 3.0 section, the
**sole required deliverable is `tenant-capability-report.md`**, answering all 5 capability-probe
questions (Stages 3.0.2.1–3.0.2.5) with cited evidence, plus a dependency-status map (Stage
3.0.3.2). **That report does not exist yet.** What exists instead:

- `tools/phase-3-sharepoint-discovery/phase-3-0-tenant-discovery.ps1` +
  `tools/phase-3-sharepoint-discovery/reports/phase-3-0-discovery-report.json` — the original
  **read-only** tenant inventory (Stage 3.0.1.1/3.0.1.2: access record, surface/list inventory).
- `docs/research/research-summary-phase3-sharepoint-write-capability-discovery.md` — a large, continuously
  updated **raw findings log** from hands-on, staged/authorized write-based capability probes
  (agent creation, `.agent`/`SKILL.md` authoring, format compliance, write-action refusal, native
  Markdown rendering, multi-document synthesis, etc.) run directly against the real BC Gov dev
  site (`AG-CSB-INTRANET-DEV`). This covers (and in several cases exceeds) all 5 required
  probes, but it is evidence, not the synthesized report the exit gate names.
- An external review (GPT-5.6) of that findings log was incorporated, tightening 4 overclaimed
  conclusions and adding a **9-priority follow-up test backlog** (permission-boundary matrix,
  ready-made-vs-custom-agent comparison, skill collision/routing, isolated asset-retrieval
  retest, embedded media/link fidelity, agent lifecycle via file ops, `.agent` schema mutation
  suite, source-scope variants, Restricted Content Discovery) — see the "Prioritized follow-up
  test backlog" section near the top of `research-summary-phase3-sharepoint-write-capability-discovery.md`. None of these 9
  priorities have been executed yet.
- **New this session (§15 of the findings doc): ASPX / modern-page conversion experiment —
  tests whether SharePoint can be a multi-format Renderer target alongside the Markdown renderer
  (this repo's `Content + Template + Renderer = Published Output` vision).** Converted one real
  CEIS topic page to HTML via `pandoc` and pushed it two ways: (1) raw hand-authored `.aspx` file
  uploaded directly to Site Pages via `Add-PnPFile` — **`Access denied`, a confirmed platform
  boundary**, not a permissions gap (same account succeeded at every other write probe in this
  doc); (2) `Add-PnPPage` + `Add-PnPPageTextPart` (the supported modern-page API) with the same
  HTML — **pushed and rendered correctly**, confirmed by user screenshot
  (`tools/phase-3-sharepoint-discovery/aspx-experiment/modern-page-rendered-screenshot.png`):
  heading, bullet list, and the first embedded image all rendered inline as authored. A sibling
  BC Gov project's more mature migration research
  (`jag-csb-cmat-sharepoint-online/plugins/sharepoint-migration/skills/sp-converting-wiki-pages/references/aspx-to-spo-migration-strategy.md`)
  independently corroborates this from a real production-migration angle: classic pages cannot
  be directly converted ("reconstruct, not convert"), and `Add-PnPPage`/`Add-PnPPageWebPart` is
  the correct/recommended automation path. Reusable script:
  `tools/phase-3-sharepoint-discovery/push-aspx-experiment.ps1`. Explicitly **not yet tested**:
  `.docx`/`.pptx` generation from the same source (flagged as cheap future follow-up — pandoc
  already supports both), multi-section/multi-web-part pages, and whether the topic's second
  image + both data tables rendered correctly (the shared screenshot only showed the top of the
  page).
- **Also new this session: three official Microsoft doc summaries added (§16-18 of the findings
  doc), each cited to its source URL.** Most consequential new facts: (1) **agents cannot use
  List data as a grounding source, and Site Pages library can never be added as an agent source
  at all** — reframes §8's write-action test (the List we tested was never a groundable surface
  to begin with) and caps how far §15's modern-page idea could ever combine with agent grounding;
  (2) the ready-made vs. custom-agent model is now officially confirmed exactly as reverse-
  engineered (ready-made has no `.agent` file; Restricted Content Discovery is specifically the
  admin mechanism to remove it — directly relevant to backlog Priority 9); (3) **SharePoint
  custom agents are independently discoverable/usable from the Microsoft Teams app store** — a
  materially different host surface than the SharePoint chat pane every finding in this document
  was tested through. Added as new backlog **Priority 10 (Teams cross-surface parity)** —
  nothing has been re-verified there yet.
- **Also new this session: a folder-vs-flat-files structuring implication added to the master
  plan's Subphase 3.1** (`docs/vision/master-initiative-plan-workstreams-and-phases.md`) — a
  folder counts as one agent source item regardless of file count inside it (Microsoft's
  documented 20-source-item cap workaround: "nest the data at a higher level"). The CEIS pilot's
  ~26 topic pages alone would burn past 20 if left flat, so the pilot library's folder structure
  (by manual section/chapter) needs to be planned during Stage 3.1.1's schema-mapping work, not
  left flat and restructured later.

**Remaining work to formally close Phase 3.0 (exit gate) — status corrected below (see note):**

**Correction (this session):** a later session (working from a stale read of this file) duplicated
Stage 3.0.3.1/3.0.3.2 into new files under `docs/research/` (`tenant-capability-report.md`,
`phase-3-dependency-status-map.md`) without first checking `docs/superpowers/specs/`, where a
**prior session had already done this work, more thoroughly, and merged it to `main`** (commits
`48bfa13`→`e897c3d`, PR #4). The `docs/research/*` duplicates have been **removed** (explicit user
permission obtained) — the authoritative Phase 3.0/Phase 3 documents are, and remain:
- `docs/superpowers/specs/phase-3-tenant-capability-report.md` — the real Stage 3.0.3.1 deliverable
  (synthesizes the same evidence, additionally records dated 2026-07-30 user resolutions of most
  open items, and concludes "Phase 3 is now implementation-ready per the two-state rule").
- `docs/superpowers/specs/phase-3-tenant-evidence-consumption-matrix.md` — Stage 3.0.3.2's
  dependency-mapping equivalent (maps each Phase 3 decision to its required Phase 3.0 evidence).
- `docs/superpowers/specs/phase-3-unresolved-decisions.md` — 14 numbered decisions, all but a
  couple already resolved with named owners/dates.
- `docs/superpowers/specs/phase-3-governed-sharepoint-knowledge-pilot-spec.md` — the full 607-line
  Phase 3 design spec (field-authority matrix, source-of-truth lifecycle, reconciliation,
  republish/rollback/rename handling, governance controls).
- `docs/superpowers/plans/phase-3-governed-sharepoint-knowledge-pilot-plan-scaffold.md` — the
  task-by-task scaffold for Subphases 3.1–3.5, ready to convert into a real, placeholder-free plan
  via `superpowers:writing-plans` now that the spec's open decisions are resolved.

**Lesson for future sessions:** before writing any new Phase 3/3.0 deliverable, grep
`docs/superpowers/specs/` and `docs/superpowers/plans/` for existing phase-3 files first — this
file's own "Remaining work" framing had gone stale relative to work already merged, and cost a
throwaway duplicate-artifact cycle.

Genuinely still-open items, per the existing (authoritative) documents above:
1. Decide whether to run any of the 9 follow-up-backlog priorities (from
   `research-summary-phase3-sharepoint-write-capability-discovery.md`) before proceeding, or defer
   them — **not yet decided**.
2. Clean up the `TEST-DO-NOT-USE-*` tenant artifacts per the staged-write protocol — **not yet
   done**; several are still in active use for potential follow-up tests, raise with the user
   before deleting.
3. `phase-3-unresolved-decisions.md`'s remaining non-resolved items (see that file directly for the
   current count — most are already resolved as of 2026-07-30).

## Next action on resume — this is the actual remaining work

1. **Phase 1 is done.** ✓ Merged to main.
2. **Phase 2 is done.** ✓ Merged to main.
3. **Phase 3 is done.** ✓ Merged to main.
4. **Phase 4 is IN PROGRESS.** Branch: `phase-4-native-sharepoint-skills` (not merged).
   
   **Current state:**
   - Tasks 0–7.5: Accepted
   - Task 8: Scope drift detected. Custom SharePoint agent research was performed and preserved. Native-skill deployment requires reconciliation.
   - Tasks 9–12: Not started
   - Exit gate: Not met
   
   **Immediate work (do not skip):**
   1. **Reconcile Task 8 native-skill status** (read-only)
      - Verify `tools/phase-4-native-sharepoint-skills/skills/review-manual-topics/SKILL.md` in repository
      - Check if deployed to AgentAssets/Skills/review-manual-topics/ on tenant
      - Record repository SHA-256 vs. deployed SHA-256
      - Determine deployment status: COMPLETE, PARTIALLY_COMPLETE, UNDEPLOYED, or DRIFT_DETECTED
   
   2. **Audit commit 83c60b7 and classify all nine files**
      - All custom-agent scripts preserved (do not delete)
      - Classify each as Phase 5 candidate, supporting research, or infrastructure
      - Create disposition record for each file (path, purpose, tenant action, result, proposed location)
      - Record in `docs/research/PHASE-4-SHAREPOINT-AGENTS-CRITICAL-LEARNINGS.md`
   
   3. **Inventory tenant artifacts** created during scope-drift experiments
      - AgentAssets library location and status
      - SKILL.md files deployed or present
      - .agent files created (count, paths)
      - Test pages, lists, or folders
      - Classify each as retain / research / cleanup-approved / unknown
   
   4. **Execute Tasks 9–12** per Phase 4 plan scaffold
      - Task 9: Metadata visibility empirical probe
      - Task 10: No-skill vs. skill-enabled evaluation
      - Task 11: Permission and safety evaluations
      - Task 12: Rollback exercise and exit-gate validation
   
   5. **Collect Phase 4 exit evidence**
      - Native-skill deployment reconciliation (Task 8 final)
      - Evaluation results (Tasks 9–12)
      - Evidence document with reviewer disposition
      - Obtain explicit human acceptance of Phase 4 exit gate
   
   **Do not:**
   - Merge to main
   - Delete or discard any committed work
   - Declare Phase 4 complete
   - Begin Phase 5 implementation
   - Fabricate missing Tasks 9–12 evidence

5. **Phase 5 — SharePoint Knowledge Agent Pilot — AWAITING Phase 4 COMPLETION:**
   - Entry gate requirement: Phase 4 exit evidence (currently incomplete)
   - Reference spec: `docs/superpowers/specs/phase-5-sharepoint-knowledge-agent-pilot-spec.md`
   - Reference plan scaffold: `docs/superpowers/plans/phase-5-sharepoint-knowledge-agent-pilot-plan-scaffold.md`
   - **Phase 5 implementation is NOT authorized until Phase 4 exits successfully**
   - When Phase 4 is complete, begin Phase 5 planning in a fresh session following mandatory protocol

## Efficiency notes for continuing this session or a fresh one

- Do not start Phase 3 planning or implementation directly on `main`. The historical `fix-grid-table-rendering-defect` branch (PR #2) is merged and deleted. Create a fresh phase branch/worktree with `superpowers:using-git-worktrees` and verify no stale worktree is being reused.
- This repo's `CLAUDE.md`: use the cheapest viable sub-agent model per dispatch, and don't spawn a sub-agent when the job doesn't need one. This entire Task 18 session (mixed-level root detection, media-disposition mechanism, both real-document convert fixes) was done directly via Read/Edit/Bash, not dispatched sub-agents — the work was well-understood, self-verifiable via the test suite, and the human (via chat) was the actual source of the classification decisions the pipeline itself can't infer (e.g. image1.png's disposition required looking at the actual image, not just objective signals).
- `origin` is `https://github.com/richfrem/manual-conversion-poc.git`. `main` is the default branch on GitHub.
- A `temp/bundles/manifest.json` exists for bundling key files via the `context-bundler` skill into a single `.md` for external review — keep it updated as files change if that hand-off is still wanted.
- The confirmed plan used for the real Task 18 run lives at `temp/ceis-manual-analysis/conversion-plan.confirmed.json` (and its draft counterpart) — `temp/` is gitignored (scratch), so this is not a durable artifact; re-run `analyze`/`confirm` fresh if resuming after `temp/` has been cleared.
