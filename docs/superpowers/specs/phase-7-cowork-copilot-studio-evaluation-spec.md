# Phase 7 Specification — Copilot Cowork and Copilot Studio Evaluation

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
**Entry gate:** A concrete use case and named accountable owner must exist for each target evaluated. An empty candidate list is a valid outcome.

## 2. Goal

Reach an evidence-based build/no-build decision for Copilot Cowork and Copilot Studio separately, based on capability gaps that proven existing workbench capabilities cannot satisfy.

## 3. Non-goals

- No speculative plugin scaffolding.
- No manifests or connector implementation without a selected use case.
- No assumption that Cowork and Copilot Studio solve the same problem.
- No build merely to demonstrate product familiarity.
- No licensing, capacity, environment, connector, or deployment assumptions without observed evidence.

## 4. Candidate requirements

Every candidate must have:

- named owner;
- real users;
- concrete workflow;
- current pain or unmet requirement;
- expected value;
- data and system scope;
- security/privacy classification;
- success criteria;
- reason existing SharePoint, GitHub, or other capabilities are insufficient.

## 5. Capability-gap analysis

For each candidate compare against actual delivered capabilities from Phases 1–6:

- repository skills and scripts;
- canonical/publication pipeline;
- governed SharePoint library;
- native SharePoint skill;
- SharePoint knowledge agent;
- shared capability model, if Phase 6 exists.

A gap exists only when the requirement cannot be achieved appropriately or efficiently with proven existing capabilities.

## 6. Cowork evaluation dimensions

Where a Cowork candidate exists, verify from current official evidence and tenant facts:

- distribution and user surface;
- supported skill/package format;
- connector need;
- governance and sharing;
- information-barrier or tenant constraints;
- lifecycle and approval;
- licensing and capacity;
- differentiated value beyond native capability.

## 7. Copilot Studio evaluation dimensions

Where a Studio candidate exists, verify:

- connectors or external systems;
- actions and workflows;
- environment strategy;
- identity and permissions;
- lifecycle/ALM;
- capacity and licensing;
- channels;
- orchestration need;
- operational ownership;
- testing and monitoring.

## 8. Build/no-build criteria

A `BUILD` recommendation requires:

- named owner and funded/approved operating path;
- verified capability gap;
- feasible identity and permission model;
- known licensing/capacity route;
- bounded pilot;
- measurable success criteria;
- governance and exit/rollback plan.

Otherwise classify:

```text
NO_BUILD
REMAIN_RESEARCH
DEFERRED_UNTIL_EVIDENCE
REJECTED_FOR_NOW
```

## 9. Decision independence

Cowork and Copilot Studio receive separate decisions. Building one does not imply building the other.

## 10. Evidence package

```text
candidate use-case list
owner confirmations
existing-capability comparison
gap-analysis memo
tenant/licensing/capacity evidence
security and permission assessment
bounded-pilot proposal
build/no-build decision per target
```

## 11. Exit criteria

- Each target has a documented decision.
- Each decision traces to a concrete use case and owner, or explicitly states none exists.
- No target is built merely because it is technically available.
- Any build recommendation defines a separately approved pilot plan rather than beginning implementation automatically.
