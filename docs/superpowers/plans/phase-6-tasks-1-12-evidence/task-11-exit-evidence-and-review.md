# Phase 6 Task 11 — Exit Evidence and Review

Consolidates Tasks 1–10 and 12 into one derivation trace. This document is the exit-evidence
package Task 11 requires; it is not itself the "explicit approval before merge" the task also
requires — that remains a human action, listed at the end, not claimed here.

## Derivation trace

1. **Task 1** (`task-1-brainstorming-and-task-2-inventory.md`) — recovered original intent from
   written evidence (Phase 4 spec, `SKILL.md`, Phase 6 spec's own entry-gate/goal language): the
   repository/deterministic-integrity vs. native/semantic-synthesis division of responsibilities
   is the essential architectural seam; the second runtime exists specifically to satisfy Phase
   6's stated entry gate.
2. **Task 2** (same file) — 14-dimension inventory of both runtimes, grounded in actual
   `SKILL.md` text and `review_manual_topics.py` code, not assumption.
3. **Task 3** (`task-3-shared-capability-specification.md`) — every capability element classified
   ESSENTIAL/TARGET_SPECIFIC/ACCIDENTAL/DEFERRED/REJECTED, each traced to Task 1/2 evidence.
4. **Task 4** (`task-4-adversarial-intent-preservation-review.md`) — independent adversarial pass;
   found one real actionable gap (related-topic-cap under-tested), one expected-behavior
   clarification (100% metadata-unavailable is correct for repository-claude, not a defect), one
   forward-looking non-transferable-assumption caveat, and confirmed one classification by reading
   actual code rather than trusting the label.
5. **Task 5** (`plugins/sharepoint-agents-and-skills/evaluations/common/`) — 12-case common
   evaluation set (11 reused from Phase 4 + 1 new, closing Task 4's gap), each annotated with
   `applicable_runtimes`.
6. **Task 6** (`task-6-baseline-evaluation-findings.md`) — real execution of the deterministic-
   resolution layer against real CEIS content: 2 cases PASS (NORM-01, NEG-01), 1 case BLOCKED
   with a genuine, disclosed finding (AMB-01's topic slug doesn't exist in the real corpus).
   native-sharepoint execution disclosed as blocked by lack of live tenant access in this session,
   not simulated.
7. **Task 7** (`task-7-target-adapters-decision.md`) — decision: no new adapter code required;
   both runtimes already express shared intent natively.
8. **Task 8** (`plugins/sharepoint-agents-and-skills/scripts/drift_detection.py` +
   `tests/unit/test_drift_detection.py`) — real drift-detection code, 9 passing tests including a
   deliberate-drift proof (cap-exceeded case actually caught, not just asserted).
9. **Task 9** (`task-9-reuse-vs-specific-decision.md`) — concrete SHARED/INDEPENDENT/ADAPTED
   disposition for every real artifact (SKILL.md, evaluation cases, resolution logic, drift
   tooling, permission cases).
10. **Task 10** (`task-10-versioning-and-compatibility.md`) — decision: no new version field
    introduced (nothing yet to version against); compatibility/deprecation rules stated for when
    they become relevant.
11. **Task 12** (`task-12-runtime-placement-content-lifecycle-actions.md`) — 7-action runtime
    placement table for the ongoing content-lifecycle loop, the preview-vs-authoritative rule
    restated formally and generalized, and a per-runtime evidence/rollback matrix built from
    artifacts this session directly verified exist and work (atomic promotion, `rollback-
    sharepoint-publication`).

## Evaluations

`plugins/sharepoint-agents-and-skills/evaluations/common/` — 12 cases, see Task 5/6 above for
execution status per case.

## Drift proof

`plugins/sharepoint-agents-and-skills/tests/unit/test_drift_detection.py::
test_related_topic_cap_exceeded_is_drift` — deliberately introduces a cap violation
(`related_count=3` against `related_topic_allowance=2`) and proves `detect_drift()` catches it
with `code="related_topic_cap_exceeded"`, `severity="error"`. Full suite: 40/40 passing
(`plugins/sharepoint-agents-and-skills/tests/`).

## Intent review

Task 4's adversarial pass is the intent-preservation review. Its disposition: **accepted with two
required corrections** (both applied — the new `BOUND-01` case at Task 5, the explicit expected-
behavior note in Task 6's findings) **and one forward-looking caveat recorded** (Task 3/9's
permission-model note). No erased safety control found that isn't already flagged and addressed.

## Decision record

Task 9's table is the decision record: what is shared, adapted, or kept independent, and why,
for every real artifact this work touched.

## Genuine open items (not resolved, correctly left open)

1. `AMB-01`'s topic-slug mismatch (Task 6) — needs a human decision between rewriting the case or
   marking it native-only; not resolvable from repository evidence alone.
2. `native-sharepoint` re-run of the Task 5 common set — needs a session with live tenant access.
3. Full semantic-review execution/grading beyond the resolver-layer proof (Task 6) — a bounded,
   real follow-up, not a blocker to this task's own completion.
4. `BOUND-01`'s fixture — still needs a real or synthetic multi-link topic to exist.

None of these four block Task 11's own deliverable (the derivation trace above); they are Phase 6
Tasks 1–12's own honestly-disclosed remaining work, carried forward rather than hidden.

## Explicit approval before merge

**Required by this task, not yet obtained.** This document, and Tasks 1–10/12's artifacts it
indexes, are ready for the human partner's review. Per this repo's own Mandatory Phase Transition
Protocol, merge does not happen until that review is given and accepted — recorded here as the one
remaining gate, not worked around.
