# Phase 7 Plan Scaffold — Copilot Cowork and Copilot Studio Evaluation

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

Run separately per target. If no real use case and owner exists, record `REMAIN_RESEARCH` and stop that target's workstream.

## Task 0 — Confirm candidate and owner

Document workflow, users, owner, expected value, data scope, and success criteria. Empty result is valid.

## Task 1 — Superpowers brainstorming

Challenge whether the candidate is a product need, a process problem, or an existing-capability gap. Define non-goals and the smallest decision needed.

## Task 2 — Inventory proven existing capabilities

Compare the candidate against what Phases 1–6 actually deliver. Do not compare against vision-only capabilities.

## Task 3 — Produce capability-gap analysis

For each requirement, classify `MET_EXISTING`, `PARTIAL`, `GAP`, `TENANT_UNKNOWN`, or `NOT_REQUIRED` with evidence.

## Task 4A — Cowork evidence discovery

Only if a Cowork candidate remains viable: verify current package/skill/connector, tenant, governance, distribution, licensing, and capacity facts from official and tenant evidence.

## Task 4B — Copilot Studio evidence discovery

Only if a Studio candidate remains viable: verify connectors/actions, environment, identity, ALM, channels, orchestration, licensing/capacity, and operational ownership.

## Task 5 — Security and governance assessment

Assess data classification, least privilege, connector trust, sharing, evidence, records implications, rollback, and accountable ownership.

## Task 6 — Define bounded pilot options

For each viable target, propose the smallest pilot, measurable outcomes, non-goals, test cases, failure/rollback, and cost/ownership. Do not implement.

## Task 7 — Build/no-build decision

Create one decision record per target using `BUILD`, `NO_BUILD`, `REMAIN_RESEARCH`, `DEFERRED_UNTIL_EVIDENCE`, or `REJECTED_FOR_NOW`.

## Task 8 — Adversarial review

Challenge product bias, duplicated capability, hidden licensing/operations cost, premature connector use, and missing owner.

## Task 9 — Update master traceability and handoff

After approval, update the master plan/traceability only as authorized. A `BUILD` decision creates a new bounded pilot specification and plan; it does not authorize implementation itself.

## Cost allocation

- Low-cost: inventories, comparison matrices, evidence collation.
- Mid-tier: prototype analysis only if explicitly authorized.
- Strong reasoning: gap analysis, governance, product selection, build/no-build decision.
