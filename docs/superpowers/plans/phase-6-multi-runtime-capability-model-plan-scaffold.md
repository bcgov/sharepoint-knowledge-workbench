# Phase 6 Plan Scaffold — Multi-Runtime Capability Model

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

Stop unless two real runtimes implement the same capability and have evaluation evidence. Do not manufacture a second implementation to unlock this phase.

## Task 0 — Verify gate and select capability

Record runtimes, owners, operational status, versions, artifacts, and existing evaluations.

## Task 1 — Superpowers brainstorming on original intent

Recover the originating user intent, governance rules, and success criteria. Identify implementation coincidences and unresolved differences.

## Task 2 — Inventory both implementations

Map inputs, outputs, steps, permissions, error behavior, human gates, evidence, and limitations without yet deriving a shared contract.

## Task 3 — Draft the shared capability specification

Classify each proposed element as essential, target-specific, accidental, deferred, or rejected. Trace essential elements to original intent.

## Task 4 — Conduct adversarial intent-preservation review

Challenge the draft for lowest-common-denominator loss, shared accidental limitations, erased safety controls, and false equivalence.

## Task 5 — Build the common evaluation set

Write meaning-based cases both runtimes can execute. Include normal, negative, ambiguous, permission/safety, and human-approval cases where applicable.

## Task 6 — Run baseline evaluations

Execute the common set on both existing runtimes and disposition differences.

## Task 7 — Implement target adapters only where needed

Adapters expose the shared intent while declaring unsupported and target-specific behavior. Avoid unnecessary abstraction.

## Task 8 — Implement drift detection

Compare runtime results against common semantic expectations. Add deliberate drift and prove detection.

## Task 9 — Apply reuse-versus-specific decision rules

Make one real decision about what is shared, generated, adapted, or kept independent.

## Task 10 — Versioning and compatibility

Define shared-spec and adapter compatibility, migration, and deprecation behavior based on real versions.

## Task 11 — Exit evidence and review

Produce derivation trace, evaluations, drift proof, intent review, and decision record. Obtain explicit approval before merge.

## Cost allocation

- Low-cost: inventories, trace tables, evidence packaging.
- Mid-tier: adapters, evaluation harness, drift detector.
- Strong reasoning: original-intent recovery, contract derivation, adversarial review, final decision.
