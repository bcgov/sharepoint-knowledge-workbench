# Resume — Phase 1–5 Complete and Merged to main; Phase 6 Task 0 In Progress (27/30)

## Current status (2026-08-03, verified against git)

**`PHASE_TRANSITION_READY`** — Phase 5 → Phase 6. All Mandatory Phase Transition Protocol checks
below are satisfied: Phase 5 tasks have explicit dispositions, evidence/exit report exist, the
feature branch is merged with a recorded merge commit, `main` sync is verified (see "Verified
repository state" below), handoff documentation is current, and no Phase 6 files/branch exist yet.

**Phase 4.5 is fully complete and merged to `main`** (PR #25, merge commit `8719f49`), including
Wave 9 (duplication remediation) and the follow-on plugin/skill naming refactor.

**Phase 5 (CEIS grounding-only prototype) is complete AND merged to `main`.**

- Disposition: **`PHASE_5_ACCEPTED_WITH_LIMITATIONS`**.
- Merged through PR #29.
- Phase 5 merge commit: `e104d1a`.
- Phase 5 closure disposition commit: `7735764` ("docs(phase5): close Phase 5 — PHASE_5_ACCEPTED_WITH_LIMITATIONS").
- Design-stream corrections commit: `7735b6d`.
- Tasks 0–8: **COMPLETE**.
- Manual control testing: **COMPLETE** — no additional Phase 5 agent-question runs required.
- Task 5 (upload): 25 Markdown topic pages, 1 `index.md`, 319 existing media items unchanged,
  0 image duplication, 0 upload failures.
- Task 6: Markdown-grounded comparison agent created and verified.
- Task 7: 7 evaluation cases run against both agents — 14 final agent/case evidence records,
  20 recorded runs retained in the provenance ledger, no technical retries.
- Task 8: consolidated findings accepted.
- Citation status: **`CITATION_SUPPORT_NOT_VERIFIED`**.
- **Phase 6: Task 0 `AUTHORIZED_AND_IN_PROGRESS` — 27/30 skill names complete. See "Phase 6 —
  Task 0 handoff (2026-08-03)" below for the full resume state.**

**Phase 5's bounded conclusion:**

- ASPX and Markdown grounding were compared using seven approved cases.
- Both representations produced usable responses within the prototype scope.
- Evidence was mixed and no winner was declared.
- The prototype does not certify production readiness, legal accuracy, citation correctness, or
  complete permission safety.
- This was an exploratory prototype, not a full governed Phase-5 exit-gate pilot — see the
  "Phase 5" section below for the full summary.

**Deferred out of Phase 5, not yet done:** citation-support verification, multi-identity
permission/oversharing testing, production governance, native-skill comparison, legal-accuracy
validation.

## Phase 6 — Task 0 handoff (2026-08-03)

**Branch:** `phase-6-multi-runtime-capability-model`, worktree at
`.worktrees/phase-6-multi-runtime-capability-model`.
**Latest pushed commit:** `30bd605` ("feat(phase6-task0.16): package compare-rendered-output
skill"), pushed to `origin/phase-6-multi-runtime-capability-model`.
**Not merged to `main`.** Task 0's own exit gate (all 30 skill names implemented/packaged/
tested + migration ledger + one focused context-bundler review package) is not yet met — do not
merge, and do not treat the 27 completed skills below as separately, finally accepted. They are
accepted as in-progress Task 0 work only. Final external review occurs once all 30 are complete.

**Task 0 progress: 27/30 skill names complete.**

- `sharepoint-agents-and-skills`: **15/15 complete**, plugin manifests in place, **31/31 tests
  passing**. Includes the repository/Claude second runtime for `review-manual-topics` that closes
  Phase 6's actual entry gate (two real runtimes of the same capability now exist). Two real bugs
  found and fixed via testing during this work: a `Write-Error`-terminates-before-JSON-write
  ordering bug (fixed in `rollback-skill-deployment.ps1` and the new restore scripts), and a
  `ConvertTo-Json` single-element-array-collapse bug (fixed in `create-sharepoint-agent.ps1` with
  an explicit `[System.Object[]]` cast).
- `sharepoint-content-publication`: **5/5 complete**, **6/6 new tests passing**. Real
  architectural finding, correctly respected rather than bypassed: this plugin's Phase 3 design is
  explicitly package-only/zero-tenant-I/O, and real automated tenant writes remain gated behind
  Stage 3.4.3's unapproved write-identity decision — **this package-only behavior is correct as-
  is; the current design still excludes unauthorized tenant writes.** The 3 new-build publication
  skills (`publish-markdown-to-sharepoint`, `publish-aspx-to-sharepoint`,
  `rollback-sharepoint-publication`) produce human-actionable plans, not tenant writes.

**Task 0.16 — `structured-content-rendering` (7 skills): COMPLETE.**

- `render-multipage-markdown` — renamed from `render-structured-content` (naming/boundary
  verification only; the underlying renderer already worked). 49/49 pre-existing tests still pass
  after the rename.
- `render-sharepoint-aspx` — genuine new `Renderer`-protocol-conformant renderer
  (`scripts/renderers/sharepoint_aspx.py`): one HTML fragment per chunk + `page-manifest.json`,
  staged for `Add-PnPPage`/`Add-PnPPageTextPart` (raw `.aspx` upload confirmed `Access denied`,
  Phase 3.0 §15). Zero SharePoint tenant I/O. **Golden-master fidelity proof complete**: the real
  CEIS manual canonical package (25 chunks, 319 media files, grouped strategy) renders end-to-end
  with validation PASS, and a fresh render is byte-identical to a recorded baseline committed at
  `runs/ceis-manual-v2/render-aspx/rendered-output/` (see
  `plugins/structured-content-rendering/tests/integration/test_golden_master_aspx.py`).
- `create-markdown-rendering-template` / `create-aspx-rendering-template` — shared
  `scripts/templates.py` module; canonical starter templates for both profiles (`generic`, `ceis`)
  and both formats under `assets/templates/`.
- `validate-rendering-template` — `scripts/template_validation.py`, one negative-control test per
  detection class (unknown profile/format, missing/unknown placeholder, title not in a real
  heading construct, forbidden ASPX full-page wrapper).
- `validate-rendered-output` — extended `renderers/validate_rendered.py` with an ASPX counterpart
  to every Markdown detection, plus `render_and_promote_aspx`; packaged as its own named skill
  (previously only reachable indirectly through `render-multipage-markdown`'s bundled scripts).
- `compare-rendered-output` — new `scripts/compare_rendered_output.py`, packaging the Phase 2
  Subphase 2.5.4 golden-master comparison pattern as a standalone, reusable primitive (used by the
  ASPX golden-master proof above).
- **Real packaging defect found and fixed while verifying installability:** `templates.py`'s
  canonical starter templates lived at the plugin root, outside `pyproject.toml`'s
  `package-dir=scripts/` boundary — invisible under `pip install -e` (editable installs point back
  at the live source tree) but broke a real isolated wheel install
  (`tools/phase-4-5-core-plugin-refactoring/isolated_install_check.py`) with
  `FileNotFoundError`. Fixed via `scripts/assets/templates/...` as real packages (empty
  `__init__.py` markers + file-level symlinks back to the plugin-root canonical source, per the
  hub-and-spoke convention) plus `package-data`/`py-modules` declarations. Isolated wheel install
  now passes.
- **Final verification:** full plugin suite **96/96 passing** (unit + contract + integration), a
  fresh isolated wheel install also passes 96/96, no broken symlinks anywhere in the plugin.
- Latest Task 0.16 commits (chronological): `20849b8`, `2d06426`, `506e193`, `ef80836`, `e98b17f`,
  `5c6aee2`, `617514e`, `30bd605`.

**Next: Task 0.17 — `workbench-setup` (3 skills). Corrected 2026-08-03: owned by this repo, NOT
cross-repository.**

- **Correction record:** an earlier pass of this plan/handoff wrongly concluded `workbench-setup`
  was a Category 1 (marketplace-style) skill set that had to be authored in the sibling
  `agent-plugins-skills` repo. That was a real mistake, not a design decision — it conflated "use
  the `marketplace-manager` skill *installed from* `agent-plugins-skills` as a tool/procedure for
  `marketplace.json` updates" with "author this new plugin *inside* `agent-plugins-skills`." Those
  are unrelated: `agent-plugins-skills` is a generic marketplace repo consumed by this repo (and
  others) for reusable, cross-project skills; `workbench-setup` is a workbench-specific plugin,
  same category as `sharepoint-agents-and-skills`/`sharepoint-content-publication`. A worktree/
  branch briefly created in `agent-plugins-skills` for this task (3 untracked `.psd1.example`
  files only, never committed or pushed) has been deleted; that repo is unaffected.
- `setup-sharepoint-connection`, `initialize-document-workflow`, `validate-workbench-environment`
  (per `docs/superpowers/specs/2026-08-02-multi-document-destination-configuration-design.md`
  Section 8) belong at `plugins/workbench-setup/` in **this** repo, following the same
  plugin-manifest/`SKILL.md`/`symlink_manager.py`/installer-hard-copy/test conventions as every
  other Phase 4.5/Phase 6 domain plugin here (see CLAUDE.md's "Plugin-Local Resource Sharing").
- The `marketplace-manager` skill (installed from `agent-plugins-skills` into this repo's
  `.agents/skills/`) is consulted only as the procedure/tool for the applicable `marketplace.json`
  registration step — not as an indication of where the plugin's code lives.

**Phase 6 Tasks 1–12 (shared-capability derivation): `NOT_STARTED`.** Do not begin these until
Task 0's exit gate is met.

**Resume instructions for the next session:**
1. Read this file in full.
2. `git fetch origin`, checkout/enter the worktree at `.worktrees/phase-6-multi-runtime-capability-
   model` (or recreate it from `origin/phase-6-multi-runtime-capability-model` if the worktree
   itself isn't present), confirm `HEAD` matches `30bd605`.
3. Task 0.16 (`structured-content-rendering`) is complete — do not redo it.
4. Continue Task 0.17 at `plugins/workbench-setup/` in **this** repo (not in `agent-plugins-skills`
   — see the correction record above).
5. Do not start Phase 6 Tasks 1–12.
6. Do not create another review gate before all 30 skill names are complete — the approved
   external-review gate is after Task 0 in full, not after each plugin.

**Separate architecture-design stream — design-complete, not implemented, committed to `main`:**

- `sharepoint-agents-and-skills` plugin design: **`DESIGN_COMPLETE`**, **`IMPLEMENTATION_NOT_AUTHORIZED`**, **`MIGRATION_NOT_STARTED`**.
- Multi-document destination configuration design: **`PLANNING_ONLY`**, **`IMPLEMENTATION_NOT_AUTHORIZED`**.
- Design-stream documents (the multi-document-destination-configuration design,
  sharepoint-agents-and-skills plugin design, broader-plan vision update, and CLAUDE.md
  correction) are committed on `main` through `7735b6d` ("docs: land remaining design-stream
  corrections onto main"). Do not treat these designs as authorization to implement.

**Verified repository state (as of this entry):**

- Local `main` tracks `origin/main`.
- `HEAD` equals `origin/main` (`7735b6d`).
- Working tree clean.
- No Phase 6 branch or worktree exists.
- No Phase 6 implementation has started.

**Current plugin names** (renamed 2026-08-02 from internal architecture terms to plain
operational-purpose names — see `docs/reports/phase-4-5-core-plugin-refactoring/plugin-skill-name-migration.md`
for the full old→new mapping):
- `source-document-extraction` — DOCX/Pandoc extraction, structural analysis, defect detection.
- `document-structure-analysis` — topic-boundary reasoning, chunking-strategy recommendation, draft plan construction.
- `structured-content-assembly` — cleanup, chunking, canonical package build and validation.
- `structured-content-rendering` — multi-target publication rendering and validation.
- `sharepoint-content-publication` — SharePoint publication tooling, still `TRANSITIONAL_HOLDING_LOCATION` (not yet a real Phase-4.5-style domain plugin).

Each of the four core plugins installs and runs standalone (`pip install -e plugins/<name>`), with
zero editable-source duplication between them — cross-plugin sharing goes through managed
file-level symlinks (`symlink_manager.py`, `symlinks.json`), verified to dereference into real,
independent files at wheel-build time. `plugins/docx-to-content/` (the original combined plugin)
was fully decommissioned in Wave 8.

**Read these first, in this order, for the full evidence trail** (all other wave-by-wave detail
that used to live in this file has been consolidated into these documents — do not look for it
here anymore):
1. `docs/superpowers/plans/phase-4-5-evidence/phase-4-5-exit-statement.md` — the Wave 0-8 exit record.
2. `docs/superpowers/plans/phase-4-5-evidence/wave-9-duplication-remediation-report.md` — the
   post-hoc architecture correction (symlink-based deduplication) and its full verification evidence.
3. `docs/reports/phase-4-5-core-plugin-refactoring/plugin-skill-name-migration.md` — the
   2026-08-02 naming refactor's old→new mapping and verification evidence.
4. `docs/architecture/phase-4-5-target-architecture.md` — as-built distribution graph (diagram
   preserved under the pre-rename names as historical record, with a pointer to the current names).

Historical wave-by-wave narrative (what was decided and why, using the plugin names in effect at
the time each wave executed) lives in `docs/superpowers/plans/phase-4-5-evidence/wave-0-*` through
`wave-9-*`. Those files are the authoritative historical record and are deliberately not rewritten
for the naming refactor — only the three most-recently-active ones carry a banner pointing to the
migration map.

Separately, `sharepoint-content-publication` remains a provisional holding location — a future
session should either build it out as a real domain plugin or fold its scope into a later phase.

## Phase 5 — CEIS Grounding-Only Prototype (complete)

**Disposition: `PHASE_5_ACCEPTED_WITH_LIMITATIONS`.** Full exit report:
`docs/reports/phase-5-sharepoint-knowledge-agent-pilot/EXIT-REPORT.md` — read this first for the
complete picture (tasks, tenant artifacts retained, findings, limitations, citation-verification
status, deferred work).

- Branch: `phase-5-ceis-grounding-prototype`. **Merged to `main` via PR #29** (merge commit
  `e104d1a`; closure disposition commit `7735764`).
- Design/spec: `docs/superpowers/specs/2026-08-02-phase-5-ceis-grounding-prototype-design.md`.
- Plan: `docs/superpowers/plans/2026-08-02-phase-5-ceis-grounding-prototype.md`.
- Consolidated findings: `tools/phase-5-sharepoint-knowledge-agent-pilot/results/task8-consolidated-findings.md`.
- Generalizable findings extracted into `docs/research/field-note-aspx-vs-markdown-grounding-comparison.md`
  (two reproducible failure modes found on **both** tested agents — a currency-from-upload-timestamp
  inference bug, and cross-run relationship-answer instability — likely model-level, not
  format-specific).
- **Standing protocol established this phase:** after each task (not just each phase), check
  whether its findings are generalizable enough to warrant a `docs/research/` field note or update —
  do this as part of the task's own closure, don't wait to be asked.
- Explicitly deferred (not tested, not "passed"): native-skill comparison, multi-identity
  permission/oversharing testing, citation-accuracy verification, production governance/exit-gate
  evidence. This prototype does **not** satisfy the full governed
  `docs/superpowers/specs/phase-5-sharepoint-knowledge-agent-pilot-spec.md` — that remains open for
  a future, more rigorous pilot if one is ever authorized.

## Separate architecture-design stream — design-complete, committed, not implemented

Real architecture drift was found during Phase 5 (reusable SharePoint scripts/skills were being
written into `tools/phase-N-*/` instead of an installable plugin — see `.agent/map-debt.md`'s
2026-08-02 entry). The corrective design work is **design-complete, implementation/migration NOT
authorized**, and was landed on `main` through commit `7735b6d` ("docs: land remaining
design-stream corrections onto main"):

```
CLAUDE.md
docs/superpowers/specs/2026-08-02-multi-document-destination-configuration-design.md
docs/superpowers/specs/2026-08-02-sharepoint-agents-and-skills-plugin-design.md
docs/vision/ai-assisted-structured-knowledge-workbench-broader-plan.md
```

- `sharepoint-agents-and-skills` plugin design: `DESIGN_COMPLETE`, `IMPLEMENTATION_NOT_AUTHORIZED`, `MIGRATION_NOT_STARTED`.
- Multi-document destination configuration design: `PLANNING_ONLY`, `IMPLEMENTATION_NOT_AUTHORIZED`.

Do not implement either of these as part of Phase 6 unless separately authorized.

## MANDATORY PHASE TRANSITION PROTOCOL

No phase may be declared closed, and no next phase may begin, until every applicable item below is
verified. This section is permanent — apply it at every future phase boundary, not just the
Phase 5 → Phase 6 transition that motivated writing it down.

### Phase completion

- All planned tasks have explicit dispositions.
- Required tests and evidence are complete.
- External or independent review is recorded.
- Human exit disposition is recorded.
- Limitations and deferred items are explicit.
- A final phase exit report exists.

### Feature branch and merge

- All phase-owned changes are committed.
- The feature branch is pushed.
- No unrelated planning stream is included in the phase's PR.
- The PR is reviewed and merged by the user.
- The merge commit is identified (recorded by hash, not description).
- The phase branch is not treated as authoritative after merge — `main` is.

### Main synchronization

Run and verify:

```bash
git fetch origin --prune
git checkout main
git branch --set-upstream-to=origin/main main
git pull --ff-only origin main
git rev-parse HEAD
git rev-parse origin/main
git status --short --branch
```

Required result:

- Local `main` tracks `origin/main`.
- `HEAD` equals `origin/main`.
- Working tree is clean.

Do not infer synchronization from a successful pull alone. Do not interpret ahead/behind counts
until the tracked upstream branch has been verified.

### Handoff documentation

Before ending the phase:

- Update `start-here.md` after the merge.
- Record the actual merge commit.
- Record the exact next phase and its status.
- Record parallel planning streams separately from the phase that just closed.
- List outstanding human decisions.
- Provide exact fresh-session resume steps.
- Remove stale statements about unmerged branches or uncommitted files.

### Next-phase contamination gate

Before the next phase begins, confirm:

- No next-phase implementation files exist.
- No next-phase branch or worktree exists unless intentionally created after closure.
- No background agent or command remains active.
- No tenant write remains in progress.
- No unrelated files are staged.
- The next phase has its own approved scope, branch, worktree, and session.

### Fresh-session rule

The next phase must begin in a fresh session. The new session must be able to resume from:

- `start-here.md`;
- committed specifications and plans;
- phase exit evidence;
- Git history.

The new session must not depend on the previous conversation transcript.

### Fail-closed transition status

Every phase-transition check ends in exactly one of:

- `PHASE_TRANSITION_READY`
- `PHASE_TRANSITION_BLOCKED`

If blocked, list the exact failed checks.

Do not use phrases such as "essentially complete," "ready except for documentation," "not a
blocker," or "can be fixed later" when a mandatory transition check remains unresolved. A stale
`start-here.md` is a transition blocker, not a cosmetic gap.

## Phase 6 (not started)

Per `docs/vision/master-initiative-plan-workstreams-and-phases.md`, Phase 6 requires its own fresh
branch/worktree and session, following the Mandatory Planning Protocol below (brainstorming before
plan mode). Treat this file and committed evidence as authority — not any prior conversation
transcript. No Phase 6 branch/worktree or files exist yet; no Phase 6 implementation has started.

### Next-session procedure

1. Open a fresh session.
2. Read this file (`start-here.md`) in full.
3. `git fetch origin` and confirm current `main` is clean (`HEAD` == `origin/main`, working tree
   clean).
4. Create a dedicated Phase 6 branch/worktree via `superpowers:using-git-worktrees`.
5. Invoke `superpowers:brainstorming` before any planning or implementation — do not begin from
   `docs/superpowers/specs/phase-6-multi-runtime-capability-model-spec.md` as though its scope is
   already approved; it is a forward-looking scaffold only.
6. Reuse Phase 4 and Phase 5 evidence rather than re-deriving it.
7. Do not repeat Phase 5's full manual test matrix.
8. Do not implement `sharepoint-agents-and-skills` or the multi-document destination
   configuration design as part of Phase 6 unless separately authorized.

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

**This section is historical** (it describes the Phase 4 native-skills reconciliation work as it
stood mid-phase). That work was completed and merged; see the Phase 4.5 and Phase 5 sections above
for current, accurate status. Left in place as a record of the reconciliation process actually
followed — do not treat any status claim below as current.

1. **Phase 1 is done.** ✓ Merged to main.
2. **Phase 2 is done.** ✓ Merged to main.
3. **Phase 3 is done.** ✓ Merged to main.
4. **Phase 4 / 4.5 are done.** ✓ Merged to main (see Phase 4.5 section above for the naming
   refactor and evidence trail).
5. **Phase 5 is done** (exploratory prototype, `PHASE_5_ACCEPTED_WITH_LIMITATIONS`) — see the
   Phase 5 section above. Merged to `main` via PR #29 (`e104d1a`).
6. **Phase 6 is next** — not started. Requires a fresh branch/worktree/session and the Mandatory
   Planning Protocol below (brainstorming before plan mode). Do not begin Phase 6 work from a
   continuation of the Phase 5 session/branch.

**Resume instructions for a fresh session:** superseded by the "Next-session procedure" in the
"Phase 6 (not started)" section above — use that, not this historical block.

## Efficiency notes for continuing this session or a fresh one

- Do not start Phase 3 planning or implementation directly on `main`. The historical `fix-grid-table-rendering-defect` branch (PR #2) is merged and deleted. Create a fresh phase branch/worktree with `superpowers:using-git-worktrees` and verify no stale worktree is being reused.
- This repo's `CLAUDE.md`: use the cheapest viable sub-agent model per dispatch, and don't spawn a sub-agent when the job doesn't need one. This entire Task 18 session (mixed-level root detection, media-disposition mechanism, both real-document convert fixes) was done directly via Read/Edit/Bash, not dispatched sub-agents — the work was well-understood, self-verifiable via the test suite, and the human (via chat) was the actual source of the classification decisions the pipeline itself can't infer (e.g. image1.png's disposition required looking at the actual image, not just objective signals).
- `origin` is `https://github.com/richfrem/manual-conversion-poc.git`. `main` is the default branch on GitHub.
- A `temp/bundles/manifest.json` exists for bundling key files via the `context-bundler` skill into a single `.md` for external review — keep it updated as files change if that hand-off is still wanted.
- The confirmed plan used for the real Task 18 run lives at `temp/ceis-manual-analysis/conversion-plan.confirmed.json` (and its draft counterpart) — `temp/` is gitignored (scratch), so this is not a durable artifact; re-run `analyze`/`confirm` fresh if resuming after `temp/` has been cleared.
