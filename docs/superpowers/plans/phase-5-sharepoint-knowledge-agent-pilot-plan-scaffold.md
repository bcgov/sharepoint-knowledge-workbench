# Phase 5 Plan Scaffold — SharePoint Knowledge Agent Pilot

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

## Entry gate

Do not finalize or execute until Phase 3 and the required Phase 3.0 evidence exist. Determine whether Phase 4 is a dependency from the selected scenario.

## Task 0 — Confirm entry evidence

Verify governed library, agent-creation authority, approval path, source-format support, and owner. Record whether the scenario is grounding-only or skill-dependent.

## Task 1 — Superpowers brainstorming and scenario selection

Compare bounded scenarios. Select one with a real user need, owner, approved source set, and testable outcomes.

## Task 2 — Approve grounding-source inventory

Create source inventory with ownership, permissions, currency, lineage, format support, and inclusion rationale.

## Task 3 — Define agent instructions and refusal boundaries

Write purpose, intended users, approved behavior, prohibited behavior, insufficient-evidence response, conflict handling, and escalation. Review before deployment.

## Task 4 — Define currency policy

Specify current/stale/out-of-review/superseded/conflicting handling. Create test fixtures or staged pilot items for each applicable state.

## Task 5 — Define deployment and sharing path

Document creator authority, target site, sharing scope, owner, review cadence, disable/remove procedure, and evidence capture. No deployment yet.

## Task 6 — Create the agent manually through the approved path

A named human performs creation/configuration. Verify settings and source scope against reviewed artifacts.

## Task 7 — Run answerable evaluations

Check correct grounding, source use, citations, exceptions, and completeness. Record reviewer judgment.

## Task 8 — Run unanswerable and boundary evaluations

Prove refusal or insufficient-evidence behavior. Include ambiguity and conflicting-source cases.

## Task 9 — Run currency evaluations

Exercise current, stale, out-of-review, and superseded cases. Confirm behavior matches policy.

## Task 10 — Run permission/oversharing evaluations

Use at least two authorized identities with different access. Treat any disclosure as blocking.

## Task 11 — Lifecycle and removal exercise

Document version/update process and exercise disable/removal in the non-production pilot if authorized.

## Task 12 — Consolidated evidence and retrospective

Produce results, limitations, unsupported source-format findings, and recommendations. Do not start Phase 6 automatically.

## Task 13 — Exit review and merge gate

Review all evidence, repository docs, metadata disposition, and git state. Obtain explicit approval before merge.

## Cost allocation

- Low-cost: inventories, evaluation formatting, evidence collation.
- Mid-tier: evaluation harnesses and repository validation utilities.
- Strong reasoning: instructions, refusal boundaries, currency policy, permission review, final acceptance.
