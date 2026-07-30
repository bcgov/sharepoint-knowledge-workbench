# Future-Phase Planning Index

## Purpose

This index records forward-phase specification drafts and implementation-plan scaffolds for the
AI-Assisted Structured Knowledge Workbench.

These artifacts preserve architectural intent and reduce future planning effort. Their presence does not
mean that a phase is authorized, that its entry gate has been met, or that its plan is implementation-ready.

Every phase must still follow:

1. `start-here.md`
2. the master initiative plan
3. phase-entry verification
4. `superpowers:brainstorming`
5. repository and platform reconnaissance
6. specification review
7. `superpowers:writing-plans`
8. adversarial plan review
9. explicit implementation approval
10. phase-specific branch/worktree creation

External review supplements this process. It does not replace brainstorming, evidence gathering, or human
approval.

## Artifact Status Definitions

### Specification draft

A specification draft preserves intended goals, non-goals, contracts, governance boundaries, entry gates,
evidence requirements, and exit criteria.

A specification draft is not approved merely because it exists.

### Plan scaffold

A plan scaffold preserves expected workstreams and task sequencing but intentionally omits implementation
details that depend on future evidence.

A plan scaffold must not be called implementation-ready until:

- its phase entry gate is met;
- all blocking evidence exists;
- provisional assumptions are replaced with observed facts;
- exact repository files and contracts are identified;
- test and validation commands are known;
- rollback is defined;
- the specification is approved;
- `superpowers:writing-plans` has produced the final plan;
- the final plan has passed adversarial review;
- the user explicitly authorizes execution.

## Status Vocabulary

Use these labels:

- `CONFIRMED`
- `RECOMMENDED`
- `PROVISIONAL`
- `DEFERRED_UNTIL_EVIDENCE`
- `BLOCKED`
- `RESEARCH`
- `LATER`
- `REJECTED_FOR_NOW`

Do not use `TBD` by itself.

## Phase 3 — Governed SharePoint Knowledge Pilot

**Disposition:** `NEXT`, gated behind Phase 3.0

**Specification:**

- `specs/phase-3-governed-sharepoint-knowledge-pilot-spec.md`

**Companions:**

- `specs/phase-3-tenant-evidence-consumption-matrix.md`
- `specs/phase-3-unresolved-decisions.md`

**Plan scaffold:**

- `plans/phase-3-governed-sharepoint-knowledge-pilot-plan-scaffold.md`

**Entry gate:**

- Phase 2 exit gate met (confirmed).
- Phase 3.0 produces an accepted `tenant-capability-report.md` (not yet met).

This is the actual next phase in sequence per `start-here.md` and the master plan. Phases 4–7 below are
recorded for architectural continuity only and do not change that order.

## Phase 4 — Native SharePoint Skills Pilot

**Disposition:** `RESEARCH`

**Specification:**

- `specs/phase-4-native-sharepoint-skills-pilot-spec.md`

**Plan scaffold:**

- `plans/phase-4-native-sharepoint-skills-pilot-plan-scaffold.md`

**Entry gate:**

- Phase 3.0 confirms native skill authoring availability.
- The actual `AgentAssets` identity, schema, permissions, and authoring path are known.
- Phase 3 provides a governed SharePoint knowledge library.
- A named owner and authorized deployer exist.
- Candidate skill inputs exist in the pilot library.

**Current leading candidate:**

- `review-manual-topics`

Candidate selection remains subject to Superpowers brainstorming and observed tenant evidence.

**Before final planning:**

- replace generic skill assumptions with the tenant-observed schema;
- identify actual manual deployment and rollback steps;
- confirm permissions;
- confirm the evaluation identities;
- determine whether the skill requires a pre-provisioned review list;
- verify evidence storage and redaction requirements.

No second native skill or deployment automation is authorized by these files.

## Phase 5 — SharePoint Knowledge Agent Pilot

**Disposition:** `RESEARCH`

**Specification:**

- `specs/phase-5-sharepoint-knowledge-agent-pilot-spec.md`

**Plan scaffold:**

- `plans/phase-5-sharepoint-knowledge-agent-pilot-plan-scaffold.md`

**Entry gate:**

- Phase 3 governed library exists.
- Phase 3.0 confirms agent-creation permissions and approval path.
- A named agent owner exists.
- An approved grounding-source set exists.
- Supported source formats are verified in the tenant.

Phase 4 is required only if the selected agent scenario invokes or depends on a native SharePoint skill.

At phase start, classify the scenario as:

- `GROUNDING_ONLY`
- `GROUNDING_PLUS_NATIVE_SKILL`

This is a bounded knowledge-agent pilot. It does not authorize a general-purpose routing or orchestration
agent.

## Phase 6 — Multi-Runtime Capability Model

**Disposition:** `LATER`

**Specification:**

- `specs/phase-6-multi-runtime-capability-model-spec.md`

**Plan scaffold:**

- `plans/phase-6-multi-runtime-capability-model-plan-scaffold.md`

**Entry gate:**

- At least two real runtimes implement the same capability.
- Both implementations have operational evidence.
- The original user and governance intent is recoverable.
- Both implementations have evaluation artifacts.

Do not manufacture a second runtime merely to activate Phase 6.

The shared capability contract must be derived from original intent and observed implementation behaviour.
It must not be created by taking only the intersection of two implementations.

Phase 6 must preserve:

- essential shared behaviour;
- target-specific differences;
- permission differences;
- runtime-specific guarantees;
- human approval points;
- safety boundaries;
- meaning-based common evaluations.

## Phase 7 — Cowork and Copilot Studio Evaluation

**Disposition:** `RESEARCH`

**Specification:**

- `specs/phase-7-cowork-copilot-studio-evaluation-spec.md`

**Plan scaffold:**

- `plans/phase-7-cowork-copilot-studio-evaluation-plan-scaffold.md`

**Entry gate per target:**

- a concrete use case exists;
- a named accountable owner exists;
- the expected value is defined;
- a real capability gap remains after comparison with delivered Phase 1–6 capabilities.

Cowork and Copilot Studio receive separate decisions.

Permitted outcomes include:

- `BUILD`
- `NO_BUILD`
- `REMAIN_RESEARCH`
- `DEFERRED_UNTIL_EVIDENCE`
- `REJECTED_FOR_NOW`

A `BUILD` decision authorizes creation of a separate bounded pilot specification and plan. It does not
authorize immediate implementation.

## Agent-Cost Guidance

### Low-cost agents

Use for:

- repository inventories;
- link and path validation;
- evidence matrices;
- mechanical document scaffolding;
- repetitive evaluation-case formatting;
- established validation commands;
- evidence collation.

### Mid-tier agents

Use for:

- validators;
- evaluation harnesses;
- non-trivial schemas;
- adapters;
- reconciliation or drift-detection logic;
- debugging.

### Strong reasoning agents

Reserve for:

- Superpowers brainstorming;
- architecture and source-of-truth decisions;
- permission and oversharing boundaries;
- refusal and safety design;
- shared-capability derivation;
- Cowork versus Copilot Studio product decisions;
- adversarial plan review;
- final acceptance.

Cost never justifies skipping the required workflow.

## Future-Phase Activation Checklist

Before opening a future phase for detailed planning, confirm:

- [ ] The preceding phase exit gate is satisfied.
- [ ] The phase-specific entry gate is satisfied.
- [ ] Evidence is current and stored in a tracked location.
- [ ] `start-here.md` identifies this phase as the actual next action.
- [ ] A fresh session has been started.
- [ ] A dedicated branch/worktree has been created.
- [ ] `superpowers:brainstorming` has been invoked.
- [ ] Recommendations are separated from confirmed decisions.
- [ ] Missing facts have named evidence sources and owners.
- [ ] The existing specification draft has been reviewed.
- [ ] The plan scaffold has not been mistaken for an approved plan.
- [ ] `superpowers:writing-plans` will produce the final executable plan.
- [ ] Implementation approval will be requested separately.

## Document Maintenance

When a future phase becomes active:

1. Keep the original specification filename.
2. Rewrite the specification in place after brainstorming.
3. Do not create `-old`, `-final2`, or duplicate superseded copies.
4. Preserve history through Git.
5. Replace the plan scaffold with, or rename it to, the approved dated implementation plan according to
   repository conventions (e.g. `docs/superpowers/plans/2026-MM-DD-phase-4-native-sharepoint-skills-pilot.md`
   — do not simply remove `-scaffold` and imply approval).
6. Update this index with:
   - entry-gate evidence;
   - specification status;
   - final plan path;
   - approval status;
   - branch/worktree;
   - exit evidence.
7. Update `start-here.md`.
8. Do not activate the next phase automatically.
