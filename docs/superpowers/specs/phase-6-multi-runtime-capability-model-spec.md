# Phase 6 Specification — Multi-Runtime Capability Model

> **Planning status:** This is a forward-phase planning artifact derived from the accepted master initiative plan. It does not authorize implementation. Tenant-dependent details, exact repository paths, commands, identities, field types, licensing, and platform behavior must be replaced with observed evidence before execution.

## Planning discipline

- Run `superpowers:brainstorming` before finalizing design decisions.
- Run repository reconnaissance against current files and contracts.
- Use `superpowers:writing-plans` only after the specification is reviewed.
- Use a dedicated phase branch/worktree.
- Keep planning separate from implementation.
- Use `CONFIRMED`, `RECOMMENDED`, `PROVISIONAL`, `DEFERRED_UNTIL_EVIDENCE`, `BLOCKED`, and `RESEARCH` explicitly.
- Preserve package-only/manual paths until an approved identity and write path exist.
- Store durable evidence in tracked locations, not ignored `.superpowers/` scratch directories.
- Start with the cheapest capable agent and escalate only for architecture, ambiguity, security, failed tests, or contradictory evidence.

## 1. Status and authority

**Disposition:** LATER.
**Entry gate:** At least two real runtimes implement the same capability in operational use.

**Entry-gate status (verified 2026-08-03):** `SECOND_RUNTIME_REQUIRED`. One real SharePoint-side
runtime exists — `review-manual-topics`
(`tools/phase-4-native-sharepoint-skills/skills/review-manual-topics/SKILL.md`), deployed to the
real dev tenant and exercised in Phase 4 (hash-verified deployment, 7/7 metadata probes, 12/12
safety tests, rollback proven — see `docs/reports/phase-4-native-sharepoint-skills/
phase-4-exit-gate-evidence.md`). No repository/GitHub/Claude-side skill implements the same
capability (single-topic-scoped semantic editorial review: completeness, section structure,
cross-reference consistency, terminology clarity, read-only, no metadata writes, no hash claims,
no full-library scan). The nearest candidate,
`tools/phase-3-sharepoint-discovery/skills/reference-real-skill-review-manual-topics.SKILL.md`, is
a different capability (metadata-gap tracking into a Content Review list) and a different runtime
type (itself a native-SharePoint-skill design, never deployed) — not a match. Until a second real
runtime implementing this same capability exists, this document remains a decision framework, not
an implementation specification.

**Smallest bounded second-runtime candidate:** a repository-owned Claude Code skill implementing
the same `review-manual-topics` capability (same input boundary — one topic, ≤2 cross-referenced;
same prohibited scope — no writes, no hash claims, no full-library scan; same output structure)
over `runs/ceis-manual-v2/`'s rendered Markdown pages. Phase 4's evaluation cases
(`tools/phase-4-native-sharepoint-skills/evaluations/`) are reusable as-is as the Stage 6.1.2
common evaluation set once both runtimes exist. Not implemented as part of this spec — implementing
this second runtime is itself gated on its own scoping/approval, not authorized by this note.

## 2. Goal

Derive a shared capability specification from two real implementations while preserving original business/governance intent, target-specific differences, and common evaluation meaning.

## 3. Non-goals

- No speculative universal capability schema before two implementations exist.
- No forced lowest-common-denominator intersection.
- No requirement that outputs be textually identical.
- No erasure of runtime-specific permissions, tools, or guarantees.
- No automatic deployment packaging for every Microsoft target.

## 4. Required inputs

For one capability implemented in at least two runtimes:

- original user/business intent;
- governance and safety requirements;
- each runtime's real implementation artifact;
- each runtime's evaluation evidence;
- permission and execution model;
- known limitations;
- owners and version history.

## 5. Shared specification contents

The derived specification should define:

- purpose;
- supported inputs and outputs;
- essential behavior;
- prohibited behavior;
- human decision points;
- error/partial-failure semantics;
- evidence requirements;
- common terminology;
- lifecycle expectations;
- target-specific extension points.

## 6. Intent-preservation rule

The shared contract must be checked against the original capability and governance intent, not merely the intersection of existing implementations. If both implementations share the same accidental limitation, that limitation must not become the intended contract without an explicit decision.

## 7. Common evaluation model

Common cases test meaning:

- equivalent decisions;
- equivalent safety boundaries;
- equivalent source grounding or evidence requirements;
- appropriate refusal/failure behavior;
- preserved human approvals;
- allowed target-specific output presentation.

String equality is not sufficient unless the contract explicitly requires it.

## 8. Target adapters

Each adapter declares:

- supported shared behaviors;
- unsupported behaviors;
- target-specific behavior;
- permission model;
- deployment model;
- evidence it can produce;
- deviations and rationale.

## 9. Drift detection

The mechanism must detect:

- one runtime no longer passing common cases;
- shared-spec version incompatibility;
- changed prohibited behavior;
- missing approval points;
- target-specific deviation becoming undocumented;
- meaning drift despite superficially similar output.

A deliberate drift must be introduced in a test fixture and detected before exit.

## 10. Reuse decision rules

Define when to:

- share one instruction block;
- generate target-specific instructions from one specification;
- keep independent implementations;
- reject portability because runtime capabilities or risk differ.

## 11. Evidence package

```text
original-intent record
runtime implementation inventory
shared-contract derivation trace
intent-preservation review
common evaluation set
results from each runtime
adapter declarations
drift-detection proof
reuse-versus-specific decision record
```

## 12. Exit criteria

- At least two real runtimes implement the same capability.
- Every shared element traces to original intent and real behavior.
- Common evaluations run against both runtimes.
- Target-specific differences are explicit, not erased.
- A deliberate drift is detected.
- One real reuse-versus-specific decision is made using the rules.

## 13. Runtime placement for content-lifecycle actions

**(Added from external review, 2026-08-02, GPT 5.6 — see
`docs/vision/open-question-ongoing-editing-and-agent-assisted-rendering-phase-placement.md`.)**
Master plan Subphase 6.3. Phase 3 Stage 3.1.4 owns *what* the ongoing structured-content
maintenance workflow must do (propose/review/approve/version an edit; recalculate lineage, hashes,
manifests, cross-references, publication maps). This section owns *which runtime* performs each
step, once the Section 1 entry gate (≥2 real runtimes) is met — it is not separately gated.

For each content-lifecycle action, decide explicitly:
- may an agent only **recommend** the action;
- may a native skill **invoke** approved deterministic tooling;
- must a **deterministic pipeline/workstation process** perform the authoritative update.

**Preview-vs-authoritative rule (non-negotiable):** conversational/agent rendering of edited
content is never authoritative for official publication on its own. An agent-generated
representation is a non-authoritative preview unless it passes the exact same contracts and
validation as the deterministic pipeline (not a lighter bar). The operating model:

```text
agent assists or requests
  → deterministic tooling updates/renders
  → validation executes
  → human/governed workflow approves
  → publication reconciles
```

Also define, per runtime (deterministic pipeline / native skill / agent): how evidence,
permissions, and rollback differ — do not assume they are equivalent across runtimes.

**Deliverables:** runtime-placement decision table (one row per Phase 3.1.4 maintenance action);
preview-vs-authoritative rule document; per-runtime evidence/rollback matrix. These feed a future
Phase 6.5 (Ongoing Structured Content Authoring and Republishing) entry gate — this
section's completion does not itself authorize that phase.

**Explicit non-goal:** do not let this section, or Phase 5.5B, become an agent editing-and-
publication workflow. Phase 5.5B stays limited to deterministic renderer expansion.
