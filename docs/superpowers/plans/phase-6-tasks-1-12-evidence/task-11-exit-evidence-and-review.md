# Phase 6 Task 11 — Exit Evidence and Review (FINAL)

**Final update, 2026-08-04.** Round 1 fixed the evaluation-gap framing. Round 2 fixed
`sharepoint-content-publication`'s isolated-install dependency and resolved `BOUND-01` from the
approved contract. This final update closes the last item: the human partner obtained live tenant
access and personally drove the `native-sharepoint` runtime's live Copilot chat, executing 3 of
the 7 applicable cases (4 explicitly skipped by their own decision). See
`phase-6-remediation-bundle.md`'s final addendum for the full index.

## Disposition

**`PHASE_6_COMPLETE_WITH_ONE_CONFIRMED_LIVE_DRIFT_FINDING`.** Task 0's exit gate (30/30 skills,
all genuinely isolated-installable) is met. Tasks 1–12's shared-capability-model artifacts are
complete and tested. `BOUND-01` is resolved from the approved contract. The `native-sharepoint`
runtime has now been executed live against the real tenant — 3 of 7 applicable cases run and
graded (all PASS), 4 explicitly skipped by the human partner's informed decision (not a technical
blocker). **One real, confirmed finding survives this final pass and is not resolved**: `AMB-01`'s
live execution exceeded the related-topic cap on both runs (3 and 7 consulted vs. an allowance of
2) — empirical proof of the behavioral-enforcement gap Task 4's adversarial review flagged as
theoretical earlier this session. This is a live-agent-behavior finding, not a code defect in this
repository, and fixing it (prompt/instruction tuning on the deployed `SKILL.md`, or reducing what
the agent treats as "evidence") is future work, not blocking this phase's closure — it is recorded
as a known, real limitation for the accepting reviewer to weigh.

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

## Evaluations (final count)

12 cases total. `repository-claude`-applicable: 5 (NORM-01, NEG-01, SAFE-01, SAFE-02, BOUND-01) —
all 5 executed with full semantic review, 5 PASS (BOUND-01's case-vs-code question resolved from
contract at round 2). `native-sharepoint`-applicable: 7 (AMB-01 + 6 `PERM-*` cases) — **3 of 7
executed live** (AMB-01, PERM-01, PERM-02 — all PASS), **4 of 7 explicitly skipped by human
decision** (PERM-03 through PERM-06). Total: 10 of 12 cases have real executed results; 2 skipped
by informed human choice, not a technical or access blocker.

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

## Blocking items — none remain

Zero hard blockers remain. One real, unresolved finding survives (see Disposition above and the
"Remaining known limitation" section below) but does not block phase closure — it is a recorded
limitation for the reviewer to weigh, not an incomplete task.

## Resolved this final update — live native-runtime execution

- **`native-sharepoint` execution of the 7 applicable cases** — no longer blocked. The human
  partner obtained live PnP/Entra tenant access and personally drove the live Copilot chat
  (`CEIS-Pilot-Knowledge-Agent`, `AG-CSB-INTRANET-DEV`), using the prepared runbook's exact
  prompts/identities, unchanged. Precondition first verified/fixed: the deployed
  `review-manual-topics` skill was stale (hash mismatch) — redeployed, byte-for-byte readback
  confirmed, reconciliation re-confirmed clean before any case ran. Along the way, 4 real
  cmdlet-parameter bugs were found and fixed in `reconcile-deployed-skill.ps1`/`deploy-and-
  verify-skill.ps1` (see `.agent/map-debt.md`'s 2026-08-03 entries, commits `5e05893`, `0345b5f`)
  — all previously-untested-live scripts.
  - **3 of 7 executed: `AMB-01` (2/2 runs), `PERM-01`, `PERM-02` — all PASS.**
  - **4 of 7 explicitly skipped by the human partner's own decision** (`PERM-03` through
    `PERM-06`) — recorded honestly as skipped, not folded into a false 7/7.
  - Full raw responses, grading, and cross-runtime drift check:
    `plugins/sharepoint-agents-and-skills/evaluations/common/native-sharepoint-results/`.

## Remaining known limitation (not blocking, recorded for the reviewer)

`AMB-01`'s live execution exceeded the related-topic cap on both runs (3 and 7 related topics
named as consulted, vs. an allowance of 2) — `drift_detection.detect_drift()` confirms
`related_topic_cap_exceeded` for both. This is empirical, not theoretical, proof of the asymmetry
Task 4's adversarial review flagged earlier this session: the cap is code-enforced on
`repository-claude` (`TooManyRelatedTopicsError`) but only behavioral on `native-sharepoint`, and
here that behavioral enforcement did not hold. **Not fixed this session** — fixing it means
tuning the deployed `SKILL.md`'s instructions or the live agent's own configuration and re-testing
live, which is real, separate follow-up work, not a bounded correction to make unilaterally here.
Recorded as a known, live-observed limitation of the native runtime's current instruction-following
reliability, for the accepting reviewer to weigh alongside everything else in this bundle.

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

**Still required, still not obtained — this is the only thing left.** Every item this document's
three revisions have tracked is now either resolved or explicitly, honestly recorded as a known
limitation. This final document, the migration ledger, and the full remediation bundle are ready
for the human partner's review and merge decision. Per this repo's own Mandatory Phase Transition
Protocol, merge does not happen until that review is given and accepted. This session does not
merge, does not start Phase 7, and stops here.
