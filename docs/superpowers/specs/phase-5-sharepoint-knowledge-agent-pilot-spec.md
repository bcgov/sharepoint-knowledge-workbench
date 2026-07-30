# Phase 5 Specification — SharePoint Knowledge Agent Pilot

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

**Disposition:** RESEARCH.  
**Entry gate:** Phase 3 governed library exists; Phase 3.0 confirms agent-creation permissions and approval path. Phase 4 is prerequisite only if the selected agent scenario invokes a native skill.

## 2. Goal

Pilot one bounded SharePoint knowledge agent grounded in approved Phase 3 sources, with explicit answer boundaries, current/stale/superseded behavior, permission trimming, and evidence for answerable and unanswerable cases.

## 3. Non-goals

- No general-purpose routing/orchestration agent.
- No multi-site or enterprise-wide rollout.
- No external connectors or Copilot Studio integration.
- No assumption that native skills are required.
- No automated agent creation unless separately authorized.
- No unbounded source selection.

## 4. Scenario-selection decision

At phase start, classify the pilot as:

```text
GROUNDING_ONLY
GROUNDING_PLUS_NATIVE_SKILL
```

The selected scenario must have a real owner, user need, approved source set, and evaluation questions. If it is `GROUNDING_ONLY`, Phase 4 is not a dependency.

## 5. Grounding-source contract

Every source must have:

- owner;
- approval/review state;
- permission scope;
- content currency state;
- supported format verified in the tenant;
- canonical/package lineage where applicable;
- inclusion rationale;
- removal/supersession rule.

## 6. Agent instruction contract

Define:

- purpose and intended users;
- approved source scope;
- questions the agent should answer;
- questions it must decline;
- behavior when evidence is insufficient;
- treatment of stale, superseded, out-of-review, or conflicting content;
- citation/source expectations;
- escalation path;
- prohibition against inventing authoritative guidance;
- owner and review cadence.

## 7. Currency behavior

The specification must distinguish:

```text
CURRENT
STALE
OUT_OF_REVIEW
SUPERSEDED
CONFLICTING
UNKNOWN
```

For each state, record whether the agent answers, caveats, refuses, or escalates. The decision owner is the assigned agent owner together with the Phase 3 library owner where content governance is involved.

## 8. Permission and oversharing boundary

Test with at least two approved identities that have materially different source access. The agent must not reveal inaccessible source content, titles, summaries, metadata, citations, or inferred details.

## 9. Evaluation sets

### Answerable

Questions with explicit approved source support. Evaluate correctness, grounding, citation, completeness, and treatment of exceptions.

### Unanswerable

Questions not supported by the approved source set. The agent must decline or state insufficient evidence rather than fabricate.

### Currency

Cases against current, stale, out-of-review, and superseded items.

### Permission

Same or equivalent questions under different permission identities.

### Boundary and ambiguity

Conflicting sources, broad questions, sensitive requests, and questions outside the agent purpose.

## 10. Deployment governance

Before deployment, record:

- accountable owner;
- creator/deployer authority;
- target site;
- approved sources;
- sharing scope;
- review cadence;
- disable/remove procedure;
- evidence location;
- approval record.

## 11. Evidence package

```text
scenario-selection memo
approved-grounding-sources.md
agent-instructions-and-boundaries.md
currency-handling-policy.md
answerable evaluation set/results
unanswerable evaluation set/results
currency evaluation results
permission/oversharing results
boundary/ambiguity results
deployment approval record
consolidated evidence report
```

## 12. Exit criteria

- One bounded agent is created through an approved path.
- Grounding sources are owned, approved, scoped, and permission-tested.
- Answerable cases are grounded and cited as required.
- Unanswerable cases decline rather than fabricate.
- Stale/out-of-review/superseded behavior is demonstrated.
- At least two permission identities show no oversharing.
- A named owner, review cadence, and removal procedure exist.
- No general-purpose routing agent is created.
