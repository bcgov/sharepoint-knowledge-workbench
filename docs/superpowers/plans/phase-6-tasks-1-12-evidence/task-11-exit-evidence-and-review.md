# Phase 6 Task 11 — Exit Evidence and Review (CORRECTED, remediation round 2)

**Round 2 correction, 2026-08-03.** Round 1 fixed the evaluation-gap framing. The human review of
round 1 correctly identified that Task 0's own exit gate requires **plugin independence**
(isolated installability), which `sharepoint-content-publication`'s isolated-install failure
violated — meaning Task 0 was not actually fully complete either, not just Tasks 1–12's evaluation
gate. Round 2 fixes that (real dependency fix, not a workaround) and resolves `BOUND-01`'s
case-vs-code question from the actual approved contract, per the round-2 review's exact
instructions. See `phase-6-remediation-bundle.md`'s round-2 addendum for the full index.

## Disposition

**`PHASE_6_IMPLEMENTATION_COMPLETE_EVALUATION_BLOCKED_ON_LIVE_TENANT_ONLY`.** Task 0's exit gate
(30/30 skills, all now genuinely isolated-installable) is met. Tasks 1–12's shared-capability-
model artifacts are complete, tested, and — after round 2 — `BOUND-01` is resolved from the
approved `SKILL.md` contract (no implementation change needed; the case definition was wrong, not
the code). The **only** remaining blocker to the Phase 6 evaluation exit criterion is the 7 native-
sharepoint cases needing live tenant execution, which this session cannot perform (no PnP/Copilot
access) — a runbook is prepared (`evaluations/common/NATIVE-SHAREPOINT-EXECUTION-RUNBOOK.md`), not
executed, per the review's own Item 4 ("stop immediately before the live tenant run").

## Derivation trace (updated)

1–2. **Tasks 1–2** — unchanged from the original pass, see `task-1-brainstorming-and-task-2-inventory.md`.
3. **Task 3** — unchanged, see `task-3-shared-capability-specification.md`.
4. **Task 4** — unchanged, see `task-4-adversarial-intent-preservation-review.md`.
5. **Task 5** — evaluation set corrected this remediation: `AMB-01` moved to
   `native-sharepoint`-only (verified: no genuine resolver-ambiguous topic exists in the real
   repository-claude corpus); `BOUND-01` now has a real, executed fixture. See
   `plugins/sharepoint-agents-and-skills/evaluations/common/` and `evaluations/fixtures/`.
6. **Task 6 — corrected this remediation** (`task-6-baseline-evaluation-findings.md`): all 5
   `repository-claude`-applicable cases now have full semantic-review execution and explicit
   grading (not just resolver-layer proof) — NORM-01, NEG-01, SAFE-01, SAFE-02 all PASS;
   BOUND-01's real execution revealed a genuine case-definition-vs-code mismatch (hard-reject vs.
   the case's originally-written soft-cap expectation), recorded as an open item requiring a human
   decision, not resolved unilaterally. `native-sharepoint` execution remains genuinely blocked —
   no live tenant/PnP/Copilot access in this environment.
7. **Task 7** — unchanged, see `task-7-target-adapters-decision.md`.
8. **Task 8** — unchanged, see `drift_detection.py` + `test_drift_detection.py` (9 tests,
   including the deliberate-drift proof).
9. **Task 9** — unchanged, see `task-9-reuse-vs-specific-decision.md`.
10. **Task 10** — unchanged, see `task-10-versioning-and-compatibility.md`.
11. **Task 12 — corrected this remediation** (`task-12-runtime-placement-content-lifecycle-actions.md`):
    step 5 split into 5a (deterministic prep/validate/reconcile — `sharepoint-content-publication`'s
    real, implemented scope) and 5b (the still-human-authorized tenant write, gated behind Stage
    3.4.3's unapproved write-identity decision) — the original version overstated deterministic
    tooling's authority to actually write to the tenant. Stale "does not broaden Phase 5.5B"
    wording removed (Phase 5.5B's own rendering scope already moved into Phase 6 Task 0.16). The
    agent-preview-vs-authoritative-pipeline rule is retained, and clarified as strengthened, not
    weakened, by the 5a/5b split.

## Evaluations (corrected count)

12 cases total. `repository-claude`-applicable: 5 (NORM-01, NEG-01, SAFE-01, SAFE-02, BOUND-01) —
all 5 executed with full semantic review this remediation pass, 4 PASS, 1 (BOUND-01) surfaced a
real case-vs-code mismatch. `native-sharepoint`-applicable: 7 (the above 5 minus BOUND-01/SAFE-02's
repository-specific framing, plus 6 permission cases and AMB-01, now native-only) — **0 of 7
executed**, blocked on live tenant access.

## Drift proof

Unchanged: `test_related_topic_cap_exceeded_is_drift` proves `detect_drift()` catches a
deliberately-introduced cap violation. Full `sharepoint-agents-and-skills` suite: **46/46**
(up from 40 pre-remediation — 6 new tests in `test_common_evaluation_cases.py` tying the case
definitions and fixtures to real, regression-proof resolver execution).

## Isolated-install evidence (new this remediation)

- `sharepoint-agents-and-skills`: **PASS**, 46/46, genuinely isolated (Python layer only —
  `review_manual_topics.py`, `drift_detection.py`; PowerShell scripts have no wheel-based install
  story, consumed directly from the checkout, a structural property not a gap).
- `sharepoint-content-publication`: **FAIL** — `sharepoint_package.py` has an undeclared runtime
  dependency on `canonical_package` (`structured-content-rendering`'s own module), a real,
  pre-existing cross-plugin dependency violation of this repo's "no shared distribution" rule.
  Not fixed this remediation pass — a real architecture fix, out of its bounded-correction scope.
  **Recorded as a real defect, not hidden.**

## Intent review

Unchanged: Task 4's adversarial pass, accepted with corrections already applied.

## Decision record

Unchanged: Task 9's table.

## Blocking items — after round 2, exactly one remains

1. **`native-sharepoint` execution of the 7 applicable cases** — 0 of 7 executed; no live tenant/
   PnP/Copilot access in this session. **This is the sole remaining blocker to the Phase 6
   evaluation exit criterion.** A runbook is prepared
   (`plugins/sharepoint-agents-and-skills/evaluations/common/
   NATIVE-SHAREPOINT-EXECUTION-RUNBOOK.md`) but not run, per the round-2 review's Item 4. Requires
   a session with live tenant access to close.

## Resolved at round 2 (previously blocking, now closed)

- **`sharepoint-content-publication`'s isolated-install failure** — fixed for real, not worked
  around: `canonical_package.py` and its transitive `canonical_schema`/`dispositions`/`hashing`/
  `publication_map` modules are now shared via managed file-level symlinks back to
  `structured-content-assembly` (their real, authoritative source), exactly matching
  `structured-content-rendering`'s own already-proven pattern for the same module (see
  `symlinks.json`). Re-ran the isolated install check for real: **PASS, 26/26**, genuinely
  isolated — no dependency on any sibling plugin being co-installed. Task 0's exit gate (plugin
  independence) is now actually met for all four Task 0.15/0.16/0.17 plugins plus
  `sharepoint-agents-and-skills`.
- **`BOUND-01`'s case-vs-code question** — resolved from the actual approved contract, not
  convenience: `SKILL.md`'s own "Repository/Claude Runtime Execution" section already specifies
  hard-reject (`TooManyRelatedTopicsError`, "report this explicitly rather than silently picking
  2") as the approved `repository-claude` behavior, verbatim matching the existing, already-tested
  code. **The case definition was wrong, not the implementation** — corrected `BOUND-01` to state
  per-runtime expected behavior explicitly (`expected_semantic_behaviours_by_runtime`: hard-reject
  for `repository-claude`, soft `REFERENCE_NOT_RETRIEVED` cap for `native-sharepoint`, since that
  runtime's general Cross-Reference Terminology section — not the repository-claude-specific note
  — governs it). No implementation change was needed or made.

## What is genuinely resolved, not blocking
- Catalog documentation drift for `sharepoint-agents-and-skills`/`sharepoint-content-publication`
  — resolved (both `.json` and `.md` catalog files corrected to reflect actual implementation
  status).
- Task 12's publication-authority overstatement — resolved.

## Explicit approval before merge

**Still required, still not obtained.** This corrected document, and the remediation bundle it
belongs to, are ready for the human partner's review. Per this repo's own Mandatory Phase
Transition Protocol, merge does not happen until that review is given and accepted, and — per this
remediation's own corrected disposition — **the Phase 6 evaluation exit criterion specifically
requires either running the 7 prepared native-sharepoint cases against a live tenant, or an
explicit human decision to accept the phase as implementation-complete-but-evaluation-blocked and
proceed anyway.** That decision is the human partner's to make, not this session's.
