# Stage 8.3.1 — Incident Drill (Tabletop): `review-manual-topics` (native-sharepoint)

**Status:** `DRILL_PERFORMED_TABLETOP`. This is a tabletop walkthrough performed in this session
against the documented ownership/support charter — **it is not a live tenant incident and no
production or dev-tenant action occurred.** Stated explicitly per the instruction not to present
this as a live incident.

## Scenario chosen

**"The native runtime is observed live-consulting more than the 2-topic cap again."** Chosen
because it is not hypothetical — it already happened twice, live, during Phase 6:
`plugins/sharepoint-agents-and-skills/evaluations/common/native-sharepoint-results/RESULT-AMB-01.md`
records `AMB-01` run 1 consulting 3 related topics and run 2 consulting 7, both against the shared
contract's cap of 2, confirmed by `DRIFT-CHECK.md`'s `related_topic_cap_exceeded` flag. This drill
asks: if that recurred today, would the charter's incident-triage path (`stage-8.3.1-ownership-
support-charter.md`) actually catch and handle it?

## Walkthrough

**Step 1 — notice.** Per the charter, noticing requires a human manually watching a live Copilot
session or reading a transcript afterward. **Walked through concretely:** if Richard were not
actively watching the exact session where the drift occurred, nothing in this capability's current
tooling would surface it. `drift_detection.py`'s `detect_drift()` (referenced in the Phase 6
evidence, `plugins/sharepoint-agents-and-skills/`) only runs when explicitly invoked against a
captured transcript — it is not a standing monitor. **Gap confirmed, not assumed:** there is no
push notification, log alert, or scheduled check; detection is 100% dependent on someone choosing
to run the drift check against a specific saved transcript.

**Step 2 — check against contract/known limitations.** Richard would compare the observed
related-topic count against the shared contract's cap of 2 (defined in the skill's shared contract
description, evaluated in `plugins/sharepoint-agents-and-skills/evaluations/`). The activation
record already lists this exact behavior as a known, accepted limitation (Section 6, item 1: "Not
fixed — a real, open remediation item"). **Decision reached in this walkthrough:** because this
specific drift is a *known, already-accepted* limitation (not a novel one), the correct triage
decision per the charter's own options is **accept-and-monitor**, not fix-and-redeploy or disable —
disabling the skill over a limitation already accepted at Phase 6 exit would contradict that
disposition without new evidence justifying escalation.

**Step 3 — decide.** Accept-and-monitor, with the decision recorded (this document) rather than
made silently. If a *third* occurrence showed a materially worse pattern (e.g., consulting 15+
topics, or exposing content outside the pilot's approved scope), the charter's escalation section
applies: "None defined... no second operator is documented" — meaning **the decision-maker and the person who
would need to be escalated to are the same person.** This drill surfaces that as a real structural
gap, not a process failure: there is currently no independent second reviewer for a decision to
override an already-accepted disposition.

**Step 4 — capture evidence.** Per the charter, Richard would record: which case (`AMB-01` or a
new occurrence), the consulted-topic count, the drift-check output, and the accept-and-monitor
decision with its rationale (already-known limitation, no new evidence). This drill's own record
here **is** that evidence-capture step, performed in template form.

## Real gaps found (stated plainly, per instruction)

1. **No standing detection mechanism.** `detect_drift()` requires manual invocation against a
   manually saved transcript — a real drift between manual checks would go unnoticed indefinitely.
   This is Subphase 8.2 territory (cross-capability monitoring) in the master plan's own framing,
   but even a *single-capability* monitor does not exist yet either, and this charter does not
   claim one does.
2. **No independent escalation path.** The accountable owner and the only possible escalation
   target are the same person. Any future incident requiring a check on Richard's own triage
   decision has nowhere to go. Recorded as an open item for Stage 8.3.1's charter, not solved here.
3. **The charter's "monthly review" cadence has not actually been exercised on schedule** — this
   drill itself is the first documented review-like activity since the 2026-08-01 deployment,
   arriving via a Phase 8 planning exercise rather than a scheduled review.

## What this drill does not claim

- Does not claim the related-topic-cap limitation is fixed — it remains open, exactly as recorded
  in the activation record.
- Does not claim a live incident occurred in this session.
- Does not claim Stage 8.3.1 is fully accepted — the charter plus this drill together satisfy
  spec Section 8.1's "a named owner and a real incident (or drill) run through the documented
  process," but the real structural gaps found above (items 1–3) remain open follow-on work, not
  resolved by having been identified.
