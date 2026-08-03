# Phase 6 Task 11 — Exit Evidence and Review (CORRECTED, remediation pass)

**Corrected 2026-08-03** per human review disposition `PHASE_6_REMEDIATION_REQUIRED`. The original
version of this document described the four evaluation gaps below as "genuine open items,
correctly left open," implying they were non-blocking. **That was wrong.** They block the Phase 6
evaluation exit criterion, even though they do not invalidate the completed implementation work
(30/30 skills, 46+189 passing tests, real drift-detection code). This version states that
explicitly and does not soften it.

## Disposition

**`PHASE_6_IMPLEMENTATION_COMPLETE_EVALUATION_BLOCKED`.** Implementation (Task 0's 30 skills,
Tasks 1–10/12's shared-capability-model artifacts) is complete and tested. The Phase 6 evaluation
exit criterion — both runtimes' common evaluation set actually run and graded — is **not met**,
for reasons that are real capability/access boundaries in this session, not deferred convenience.

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

## Blocking items (corrected — these ARE blocking, not optional follow-ups)

1. **`native-sharepoint` execution of the Task 5 common set** — 0 of 7 applicable cases executed;
   no live tenant/PnP/Copilot access in this session. **This blocks the Phase 6 evaluation exit
   criterion.** Requires a session with live tenant access.
2. **`BOUND-01`'s case-definition-vs-code mismatch** — needs a human decision (correct the case to
   match the actual hard-reject behavior, or change the code to soft-cap). **Blocks full
   confidence in the boundary case's disposition** until resolved, though the underlying code
   behavior itself was proven safe (over-strict, not under-strict).
3. **`sharepoint-content-publication`'s isolated-install failure** (`canonical_package`
   cross-plugin dependency) — a real, pre-existing architecture defect surfaced by this
   remediation's Item 6 check, not previously known/documented. **Blocks that plugin's own
   isolated-installability claim** until fixed; does not block Task 0's skill-completion count
   (the skills themselves work correctly when co-installed with `structured-content-rendering`,
   which every real invocation of this repo's plugins already does).

## What is genuinely resolved, not blocking

- `AMB-01`'s scope correction (native-only, verified) — resolved.
- Repository-claude semantic-review execution for all 5 applicable cases — resolved.
- Catalog documentation drift for `sharepoint-agents-and-skills`/`sharepoint-content-publication`
  — resolved (both `.json` and `.md` catalog files corrected to reflect actual implementation
  status).
- Task 12's publication-authority overstatement — resolved.

## Explicit approval before merge

**Still required, still not obtained.** This corrected document, and the remediation bundle it
belongs to (see the remediation bundle index), are ready for the human partner's review. Per this
repo's own Mandatory Phase Transition Protocol, merge does not happen until that review is given
and accepted, and — per this remediation's own corrected disposition — **the Phase 6 evaluation
exit criterion specifically requires either completing the two remaining blocking items above, or
an explicit human decision to accept the phase as implementation-complete-but-evaluation-blocked
and proceed anyway.** That decision is the human partner's to make, not this session's.
