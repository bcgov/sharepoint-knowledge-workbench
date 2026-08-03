# Phase 6 Remediation Bundle (2026-08-03)

Response to human review disposition `PHASE_6_REMEDIATION_REQUIRED`. Consolidated index of every
correction made — read this first, then follow the links for full detail. No plugin redesign or
new governance layer was added, per the review's own instruction; every item below is a bounded
correction to something that already existed.

## Disposition after remediation

**`PHASE_6_IMPLEMENTATION_COMPLETE_EVALUATION_BLOCKED`** — see
`task-11-exit-evidence-and-review.md`'s corrected disposition section for the full statement.
Implementation remains sound (30/30 skills, unchanged). The evaluation exit criterion is now
correctly stated as blocked (not silently passed, not silently ignored), pending either live
tenant access or an explicit human decision to proceed without it.

## 1. Corrected Task 6 (baseline evaluation findings)

`task-6-baseline-evaluation-findings.md` — full rewrite. All 5 `repository-claude`-applicable
common-set cases (NORM-01, NEG-01, SAFE-01, SAFE-02, BOUND-01) now have real, full semantic-review
execution and explicit grading against `expected_semantic_behaviours`/`prohibited_behaviours`, not
just resolver-layer proof. `native-sharepoint` execution status stated plainly: 0 of 7 applicable
cases run, blocked on live tenant access, not simulated or assumed.

## 2. All common-case results

| Case | Runtime(s) | Result |
|---|---|---|
| NORM-01 | repository-claude | PASS |
| NEG-01 | repository-claude | PASS |
| SAFE-01 | repository-claude | PASS |
| SAFE-02 | repository-claude | PASS (new fixture created) |
| BOUND-01 | repository-claude | Executed; real case-vs-code mismatch found (see below) |
| AMB-01 | native-sharepoint only (corrected scope) | Not executable this session (no tenant access) |
| PERM-01 through PERM-06 | native-sharepoint only | Not executable this session (no tenant access) |

## 3. Native and repository execution evidence

- **repository-claude**: real Python execution, this session, against real CEIS content
  (`runs/ceis-manual-v2/render/rendered-output/pages/`) and two new synthetic fixtures
  (`plugins/sharepoint-agents-and-skills/evaluations/fixtures/{bound-01,safe-02}/`). Command
  output and generated review text recorded in `task-6-baseline-evaluation-findings.md`.
  Regression-proofed in `plugins/sharepoint-agents-and-skills/tests/unit/
  test_common_evaluation_cases.py` (6 new tests, all passing).
- **native-sharepoint**: **not executed this session** — no live SharePoint/PnP/Copilot access in
  this environment. Explicitly not simulated, not assumed passing. Phase 4's prior 19-case run
  remains the best available evidence for this runtime until a session with tenant access exists.

## 4. BOUND-01 fixture

`plugins/sharepoint-agents-and-skills/evaluations/fixtures/bound-01/` — a synthetic primary topic
linking to 4 related topics (real content in the corpus was checked first and confirmed to have no
topic with >2 links; the fixture is deliberately synthetic, not passed off as a real CEIS topic).
Real execution: `TooManyRelatedTopicsError` raised as designed. **Finding, not just confirmation:**
this hard-reject behavior does not match `BOUND-01`'s originally-authored `expected_semantic_
behaviours` (which describe a soft-cap-and-continue flow) — recorded as an open item requiring a
human decision in `task-6-baseline-evaluation-findings.md` and `task-11-exit-evidence-and-
review.md`, not resolved unilaterally.

## 5. Corrected Task 11 and Task 12

- `task-11-exit-evidence-and-review.md` — the four evaluation gaps are now stated as **blocking**
  the Phase 6 evaluation exit criterion, not "genuine open items correctly left open" (the
  original framing the review correctly rejected).
- `task-12-runtime-placement-content-lifecycle-actions.md` — step 5 split into 5a (deterministic
  prep/validate/reconcile, `sharepoint-content-publication`'s real implemented scope) and 5b (the
  still-human-authorized tenant write, gated behind Stage 3.4.3). Stale "does not broaden Phase
  5.5B" wording removed. Preview-vs-authoritative rule retained and clarified.

## 6. Isolated-install results

- `structured-content-rendering`: PASS, 96/96 (unchanged from Task 0 completion).
- `workbench-setup`: PASS, 36/36 (unchanged from Task 0 completion).
- `sharepoint-agents-and-skills`: **PASS, 46/46** (newly verified this remediation — `pyproject.toml`
  added; Python layer only, PowerShell scripts have no wheel-based install story).
- `sharepoint-content-publication`: **FAIL** (newly verified this remediation — `pyproject.toml`
  added, but `sharepoint_package.py`'s undeclared `canonical_package` cross-plugin dependency
  causes a real `ModuleNotFoundError` in true isolation). **New, real defect surfaced, not
  previously known.** Not fixed this pass (a real architecture fix, out of bounded-correction
  scope) — recorded as a blocking item for that plugin's own isolated-installability claim.

## 7. Corrected catalog entries

`docs/architecture/complete-plugin-skill-catalog-after-phase-9.{json,md}` — every skill entry for
`sharepoint-agents-and-skills` (15) and `sharepoint-content-publication` (5) that previously read
`phase_6_approved_not_built`/`phase_6_approved_partial` now reads `implemented`, matching their
actual, verified completion. Both plugins' `installation_status` fields corrected to the real
isolated-install findings above (PASS with a scope note for agents-and-skills; FAIL with the exact
root cause for content-publication) rather than the stale "manifests/skills incomplete"/"scaffold
only" text.

## What this remediation did NOT do (bounded correction, not redesign)

- Did not fix `sharepoint-content-publication`'s `canonical_package` cross-plugin dependency —
  real, but a design fix, not a bounded correction.
- Did not resolve `BOUND-01`'s case-vs-code mismatch by picking a side — a human decision.
- Did not obtain live tenant access or simulate `native-sharepoint` execution.
- Did not start Phase 7. Did not merge this branch.
