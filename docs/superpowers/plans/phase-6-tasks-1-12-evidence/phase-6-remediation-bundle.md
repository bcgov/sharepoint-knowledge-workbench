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

## What round 1 did NOT do (left for round 2, per the human review's follow-up)

- Did not fix `sharepoint-content-publication`'s `canonical_package` cross-plugin dependency.
- Did not resolve `BOUND-01`'s case-vs-code mismatch.
- Did not obtain live tenant access or simulate `native-sharepoint` execution.
- Did not start Phase 7. Did not merge this branch.

---

## Round 2 addendum (2026-08-03) — response to `PHASE_6_REMEDIATION_REQUIRED` round 2

The round-1 review correctly identified that Task 0's own exit gate requires plugin independence,
which `sharepoint-content-publication`'s isolated-install failure violated — Task 0 was not fully
complete either, not just Tasks 1–12's evaluation gate.

### 1. `sharepoint-content-publication`'s dependency — fixed, following repository dependency rules

Determined `canonical_package.py` is neither a shared contract nor a wrongly-placed
implementation — it is `structured-content-assembly`'s own real module, already shared with
`structured-content-rendering` via this repo's existing hub-and-spoke convention (a managed
file-level symlink, dereferenced into a real independent copy at wheel-build time, per
`symlinks.json`). `sharepoint-content-publication` was simply missing that same symlink +
`pyproject.toml` declaration — not a case requiring a new sharing mechanism. Applied the identical
pattern: 4 top-level modules (`canonical_package.py`, `dispositions.py`, `hashing.py`,
`publication_map.py`) + 4 `canonical_schema/` submodules symlinked from `structured-content-
assembly`'s real source, registered in `symlinks.json`, declared in `pyproject.toml`. **Not** a
blind copy (a real symlink, one authoritative source), **not** a runtime repository-path
dependency (resolves through the normal Python package/wheel mechanism, proven by the isolated
harness itself). Re-ran isolated wheel installation for real: **PASS, 26/26**, genuinely isolated.

### 2. `BOUND-01` — resolved from the approved capability contract, not convenience

Read `SKILL.md`'s own "Repository/Claude Runtime Execution" section directly (not assumed): it
already specifies `TooManyRelatedTopicsError` / explicit-refusal as the approved
`repository-claude` contract — "report this explicitly rather than silently picking 2, matching
the native runtime's own max-2 boundary" — verbatim matching the existing, already-tested
`review_manual_topics.py` code. **The implementation was correct; the case definition
(`BOUND-01`'s original `expected_semantic_behaviours`) was wrong** — it described a soft-cap flow
that contradicts the approved contract. Corrected the case file to state per-runtime expected
behavior explicitly (hard-reject for `repository-claude`, per the specific contract note; soft
`REFERENCE_NOT_RETRIEVED` cap for `native-sharepoint`, per the general Cross-Reference Terminology
section that governs that runtime instead). No implementation change was made or needed.

### 3. Seven native-sharepoint cases prepared for live execution

`plugins/sharepoint-agents-and-skills/evaluations/common/NATIVE-SHAREPOINT-EXECUTION-RUNBOOK.md`
— preconditions, per-case execution steps, raw-response-preservation and grading requirements,
results location. **The 7 case files' prompts and expectations were not changed** to prepare this
runbook (verified: `AMB-01` plus the 6 `PERM-*` cases, confirmed programmatically as exactly the
set with `applicable_runtimes == ["native-sharepoint"]`).

### 4. Stopped before live execution

Per Item 4: this session has no live tenant/PnP/Copilot access, so the runbook was prepared and
the live run was not attempted, simulated, or worked around.

### Disposition after round 2

`PHASE_6_IMPLEMENTATION_COMPLETE_EVALUATION_BLOCKED_ON_LIVE_TENANT_ONLY`. Task 0's exit gate is
now genuinely met (all plugins isolated-installable). Tasks 1–12 are complete with `BOUND-01`
resolved. The **only** remaining item is running the prepared 7-case runbook against a live
tenant. Not starting Phase 7. Not merging this branch.

---

## Final addendum (2026-08-04) — live native-runtime execution

The human partner obtained live tenant access (PnP PowerShell, Entra app registration) and
personally drove the `native-sharepoint` runtime's live Copilot chat pane, using the prepared
runbook's exact prompts and identities, unchanged throughout.

### Precondition check found and fixed a real deployment gap

Before running any case, `reconcile-deployed-skill.ps1` (fixed for real, live-tenant bugs found
in the process — see below) confirmed the deployed `review-manual-topics` skill was **stale**
(`DISPOSITION: DEPLOYED_ARTIFACT_DRIFT_DETECTED`) — its hash did not match this repo's current
`SKILL.md`. Redeployed via `deploy-and-verify-skill.ps1 -Execute`; byte-for-byte readback
confirmed a match; re-ran reconciliation and confirmed
`DISPOSITION: TASK_8_ARTIFACT_ALREADY_PRESENT_AND_RECONCILED` before proceeding to any case.

### 4 real cmdlet bugs found and fixed along the way

Both scripts had apparently never been run against a real live tenant before this session (no
test coverage, no prior live-execution evidence found). All four are documented in
`.agent/map-debt.md`'s 2026-08-03 entries and committed (`5e05893`, `0345b5f`):
1. `Get-PnPFolderInFolder -FolderSiteRelativeUrl` given a server-relative path instead of a
   site-relative one — silently returned zero folders (a false "no skills deployed" report,
   caught only because the human partner independently verified against the SharePoint UI and
   pushed back).
2. `Get-PnPFile -AsFile` without `-Path` — wrong parameter set, caused an interactive prompt.
3. A second `Get-PnPFile` call passed a combined file path to `-Path` instead of splitting
   directory/filename — a second interactive-prompt bug.
4. `Add-PnPFile -FileName` instead of `-NewFileName` — wrong parameter set, blocked the actual
   redeployment write until fixed.

### Live execution results: 3 of 7 executed, 4 explicitly skipped by human decision

- **Executed and PASS**: `AMB-01` (2/2 runs), `PERM-01`, `PERM-02`.
- **Skipped by the human partner's own explicit decision**: `PERM-03`, `PERM-04`, `PERM-05`,
  `PERM-06` — not a technical failure, not an access limitation; the human partner stated they
  already know the SharePoint permission behavior these would demonstrate. Recorded honestly as
  skipped, not folded into a false "7/7 executed" claim.
- Full raw responses, per-case grading, and the cross-runtime drift check:
  `plugins/sharepoint-agents-and-skills/evaluations/common/native-sharepoint-results/` (`RESULT-
  AMB-01.md`, `RESULT-PERM-01.md`, `RESULT-PERM-02.md`, `DRIFT-CHECK.md`, `SUMMARY.md`).

### One real, confirmed finding — not fixed, recorded honestly

`AMB-01`'s live responses named 3 (run 1) and 7 (run 2) related topics as consulted, both
exceeding the case's `related_topic_allowance: 2`. Ran this through `drift_detection.py`'s actual
`detect_drift()` function (not eyeballed) — confirmed `related_topic_cap_exceeded` for both runs.
This is empirical, live-observed proof of the theoretical asymmetry Task 4's adversarial review
flagged earlier this session: the related-topic cap is code-enforced on `repository-claude` but
only behavioral on `native-sharepoint`, and here that behavioral enforcement did not hold. **Not
fixed this session** — a real, separate follow-up (tuning the deployed `SKILL.md` or the live
agent's own configuration and re-testing live), not a bounded correction to make unilaterally.

### Final disposition — human-reviewed and accepted

**`PHASE_6_ACCEPTED_WITH_LIMITATIONS`** (human review disposition, 2026-08-04). The confirmed live
drift finding is accepted as a documented Phase 6 outcome, not a merge blocker — per the human
partner's own words: "the live finding does not invalidate Phase 6. It proves the multi-runtime
model and drift detector found exactly the type of behavioral divergence Phase 6 was designed to
expose." All prior blocking items are resolved. No additional Phase 6 manual testing is required.
The `native-sharepoint` related-topic-cap limitation is carried forward as a confirmed runtime
limitation and future native-skill remediation/evaluation item — not to be silently fixed,
generalized, or treated as runtime-equivalence by a later session. Not starting Phase 7. Merge
approved from the Phase 6 review perspective — the human partner opens and merges the PR
themselves; this session does not merge.
