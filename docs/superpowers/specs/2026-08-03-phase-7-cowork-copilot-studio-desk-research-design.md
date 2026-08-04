# Phase 7 Design — Copilot Cowork and Copilot Studio Desk-Research Evaluation

> **Planning status:** This design bounds Phase 7's actual scope for this round of work. It
> supersedes the broader, multi-target-agnostic framing in
> `docs/superpowers/specs/phase-7-cowork-copilot-studio-evaluation-spec.md` and
> `docs/superpowers/plans/phase-7-cowork-copilot-studio-evaluation-plan-scaffold.md` only where
> this document narrows or clarifies scope; it does not contradict either document's disposition
> (`RESEARCH`) or non-goals. It does not authorize implementation, tenant changes, environment
> creation, or a proof of concept.

## 1. Candidate and owner (entry gate satisfied)

- **Primary use case (single, not a set):** the interactive document-conversion and publication
  workflow for the SharePoint Knowledge Workbench — intake → document selection → output formats →
  destinations → agent grounding → validation → human approval.
- **Owner:** Richard Fremmerlid, workbench pilot owner and decision-maker.
- **Why this satisfies the Phase 7 entry gate:** a concrete use case and named accountable owner
  exist, per `phase-7-cowork-copilot-studio-evaluation-spec.md` Section 1.

## 2. Scope boundaries (this round)

- Evaluate **one** primary workflow only. The broader Phase 1–6 workbench capability set
  (extraction, canonical/publication pipeline, governed SharePoint library, native SharePoint
  skill, knowledge agent, shared capability model) is used **only as comparison baseline and
  integration context** — it is not independently re-evaluated capability-by-capability.
- **Desk research only.** No live build, no environment creation, no tenant change, no plugin/
  skill scaffolding, no proof of concept. Reasons (confirmed platform-access facts, not capability
  conclusions):
  - Copilot Cowork: `NOT_ENABLED_IN_TENANCY` — `LIVE_EVALUATION_BLOCKED`.
  - Copilot Studio: `ACCESS_CONFIRMED`, `DEDICATED_ENVIRONMENT_NOT_AVAILABLE` —
    `LIVE_BUILD_AND_VALIDATION_BLOCKED`.
- Cowork and Copilot Studio receive **separate** decisions (per the base spec's Section 9,
  unchanged).
- **Platform-access status must never be conflated with a capability conclusion.** Explicitly do
  not describe:
  - Copilot Studio as unlicensed or unavailable (it is licensed; only a dedicated environment is
    unavailable);
  - Copilot Cowork as available but untested (it is not enabled at all);
  - either platform as live-validated;
  - the access limitation itself as evidence that either platform lacks capability.
- Every substantive conclusion in the evidence memo is tagged exactly one of:
  - `DOC_SUPPORTED` — backed by current official Microsoft documentation reviewed during this
    phase;
  - `HYPOTHESIS_PENDING_HANDS_ON_VALIDATION` — plausible from documentation but unverified without
    a live environment.

## 3. Copilot Studio evaluation angle: agent/skill-as-artifact pattern

Phase 6 built `sharepoint-agents-and-skills` as a versioned, testable, deployable artifact model
for native SharePoint agents and skills (author → package → deploy → reconcile against tenant →
drift-detect). Copilot Studio plausibly supports a structurally similar pattern for its own
agents/actions/connectors (author → publish → environment/ALM → channels), potentially with
additional capabilities (custom connectors, richer orchestration, multi-channel distribution) that
native SharePoint skills do not have.

This is folded into the Studio evaluation as one explicit comparison angle, not a scope expansion:
does Studio's authoring/ALM model offer documented capability beyond what
`sharepoint-agents-and-skills` already delivers for the primary workflow, and is that capability
relevant to this specific workflow's needs? Any conclusion here is tagged
`DOC_SUPPORTED` or `HYPOTHESIS_PENDING_HANDS_ON_VALIDATION` like every other finding — it cannot be
`DOC_SUPPORTED` for claims that require observing Studio's actual authoring UX, since no
environment is available.

## 4. Deliverable

One evidence memo, no additional reports:

```
docs/reports/phase-7-cowork-copilot-studio-evaluation/desk-research-evidence-memo.md
```

Contents:

1. Primary use case restated, owner, success criteria for "meaningful advantage."
2. Baseline: what Phases 1–6 already deliver for this workflow (brief references to existing
   evidence — `start-here.md`, Phase 4.5/6 exit evidence — not re-derivation).
3. **Cowork section:** documented capabilities relevant to the workflow, from official
   documentation only; explicit `NOT_ENABLED_IN_TENANCY` / `LIVE_EVALUATION_BLOCKED` status stated
   separately from capability findings; disposition.
4. **Copilot Studio section:** documented capabilities relevant to the workflow, including the
   agent/skill-as-artifact comparison angle (Section 3 above); explicit `ACCESS_CONFIRMED` /
   `DEDICATED_ENVIRONMENT_NOT_AVAILABLE` / `LIVE_BUILD_AND_VALIDATION_BLOCKED` status stated
   separately from capability findings; disposition.
5. Per-finding tagging: every conclusion labeled `DOC_SUPPORTED` or
   `HYPOTHESIS_PENDING_HANDS_ON_VALIDATION`.
6. Final section: what would need to be true (specific documented capability advantage, plus
   platform access) to justify a future pilot for each target.

## 5. Dispositions

For Cowork and Copilot Studio **separately**, one of:

- `JUSTIFIED_FOR_FUTURE_PILOT` — a specific, documented capability advantage over the existing
  repository/Claude workbench was found for the primary workflow, and a future pilot is
  recommended once platform access allows it.
- `REMAIN_RESEARCH` — inconclusive from documentation alone; hands-on validation is required
  before any pilot recommendation can be made.
- `NO_ADDITIONAL_VALUE_DEMONSTRATED` — documentation review found no meaningful advantage over the
  existing workbench for this workflow.
- `BLOCKED_PENDING_PLATFORM_ACCESS` — used when the access blocker itself prevents forming even a
  documentation-only conclusion (e.g., a claim can only be verified by observing the authoring
  UX). This is an access-status disposition, not a capability disposition, and must not be used as
  a substitute for `NO_ADDITIONAL_VALUE_DEMONSTRATED`.

These replace the base spec's generic `BUILD` / `NO_BUILD` / `DEFERRED_UNTIL_EVIDENCE` /
`REJECTED_FOR_NOW` set (Section 8 of the base spec) for this round, since no build path is in
scope and the base spec's four-way set does not distinguish access blockers from capability
findings the way this round requires.

## 6. Non-goals (restated, explicit)

- No platform build, environment creation, tenant change, plugin/skill/connector scaffolding, or
  proof of concept.
- No claim of live validation for either platform.
- No capability-by-capability evaluation of the full Phase 1–6 workbench (baseline/context only).
- No recommendation to pursue a future pilot without a specific, documented capability advantage.
- No treatment of the Phase 7 base spec/plan-scaffold documents as superseded beyond the narrowing
  made explicit in this design.

## 7. Method and cost allocation

- Desk research against current official Microsoft documentation for Copilot Cowork and Copilot
  Studio (fetched live during this phase — no reliance on model memory for platform capability
  claims, consistent with `start-here.md`'s "never invent... licences, permissions, API behaviour"
  rule).
- Baseline comparison against already-accepted Phase 1–6 evidence (no re-derivation).
- Low-cost model effort for documentation inventory/collation; stronger reasoning for the
  capability-gap comparison, the agent-as-artifact angle, and the final disposition per target —
  per the base plan scaffold's cost-allocation guidance.

## 8. Exit criteria for this round

- Evidence memo written, committed, at the path in Section 4.
- Both targets have a disposition from the Section 5 set, each traceable to specific documented
  findings.
- Every substantive finding tagged `DOC_SUPPORTED` or `HYPOTHESIS_PENDING_HANDS_ON_VALIDATION`.
- Platform-access status and capability conclusions are never conflated anywhere in the memo.
- No implementation, environment, or tenant action taken.
