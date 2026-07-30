# Phase 8 Plan Scaffold — Scale, Promotion, and Operations

> **Planning status:** This is a forward-phase planning artifact derived from the accepted master initiative plan. It does not authorize implementation. Phase 8 activates incrementally per proven capability, and its details must be derived from real operational evidence rather than invented in advance.

## Planning discipline

- Run `superpowers:brainstorming` before finalizing any operational design.
- Verify the triggering capability's exit evidence and accountable owner.
- Run repository and platform reconnaissance against current operational state.
- Use `superpowers:writing-plans` only after the specification is reviewed.
- Use a dedicated phase or capability-specific branch/worktree.
- Keep planning separate from implementation.
- Use `CONFIRMED`, `RECOMMENDED`, `PROVISIONAL`, `DEFERRED_UNTIL_EVIDENCE`, `BLOCKED`, `RESEARCH`, and `LATER` explicitly.
- Store durable evidence in tracked, appropriately protected locations rather than ignored scratch paths.
- Start with the cheapest capable agent and escalate only for architecture, security, policy, ambiguity, failed tests, or contradictory evidence.

## How to use this scaffold

Instantiate this plan separately for each capability that reaches its own Phase 8 entry gate. Do not create one oversized implementation plan spanning libraries, skills, and agents before those capabilities exist.

Use a capability-qualified final plan name, for example:

```text
YYYY-MM-DD-phase-8-<capability>-promotion-and-operations.md
```

Cross-capability tasks are activated only when at least two operational capabilities exist.

## Task 0 — Confirm capability activation gate

**Deliverable:** capability-activation record.  
**Verification:** originating phase exit evidence, named owner, operational scope, rollback path, and support responsibility are all present.  
**Stop condition:** missing owner, missing exit evidence, or undefined rollback blocks the plan.

## Task 1 — Run Superpowers brainstorming

Resolve:

- What capability is being operationalized?
- What does “production” mean for this capability?
- Who owns it?
- What failure modes matter?
- What is the smallest promotion path?
- What must be monitored?
- Which lifecycle actions need human approval?
- Has a records/legal trigger emerged?
- Which tasks are capability-specific versus cross-capability?

**Evidence:** brainstorming record with confirmed, recommended, provisional, blocked, and deferred decisions.

## Task 2 — Repository and platform reconnaissance

Inventory actual:

- artifacts and versions;
- environments;
- deployment path;
- identities and permissions;
- current validation/evaluation sets;
- logs and evidence;
- rollback/disable mechanisms;
- owners and support dependencies;
- existing operational standards.

Do not infer production architecture from pilot design alone.

## Task 3 — Define the capability-specific promotion path

Document dev/test/production or the actual approved environment sequence.

Include:

- artifact identity;
- approvals;
- pre-promotion checks;
- promotion steps;
- post-promotion verification;
- rollback;
- evidence;
- emergency disablement.

**Testing:** use a non-production promotion rehearsal before the real promotion where the platform permits.

## Task 4 — Exercise one real promotion

A named authorized person or approved automation promotes one real artifact.

**Evidence:** before/after state, artifact/version identity, approvals, validation, execution log, post-check, and rollback readiness.

**Blocking:** unexplained divergence between approved and deployed state.

## Task 5 — Define and exercise version compatibility

Identify real producers and consumers. Define compatibility and migration rules only for contracts that exist.

Exercise one real version bump or controlled compatibility case.

**Evidence:** compatibility policy and result.

## Task 6 — Define ownership and support

Create the ownership/support charter with accountable owner, technical maintainer, content owner where applicable, triage, escalation, review cadence, dependencies, and handoff.

Do not invent service levels without an accountable commitment.

## Task 7 — Run an incident or recovery drill

Select a realistic non-destructive failure scenario, such as:

- wrong artifact version;
- stale source scope;
- permission drift;
- failed promotion;
- behavioral regression;
- unavailable dependency.

Exercise detection, triage, decision, recovery, and evidence capture.

## Task 8 — Define deprecation and retirement

Write triggers, notification, dependency checks, replacement/migration, access removal, evidence preservation, rollback window, and authorization.

## Task 9 — Exercise one staged retirement

Use a real obsolete test artifact or deliberately staged non-production item. Verify that dependencies, access, evidence, and rollback behave as designed.

## Task 10 — Create and test onboarding guidance

A person unfamiliar with the capability follows the onboarding guide. Record every ambiguity and failure, update the guide, and repeat the blocked portions.

## Task 11 — Determine monitoring activation

Classify monitoring need as:

```text
CAPABILITY_SPECIFIC
CROSS_CAPABILITY
NOT_YET_JUSTIFIED
```

If cross-capability and fewer than two operational capabilities exist, mark `BLOCKED` and stop that workstream.

## Task 12 — Define monitoring and assurance

For justified monitoring, define:

- operational questions;
- minimal signals;
- evidence source;
- collection boundary;
- alert owner;
- review cadence;
- false-positive handling;
- response and escalation;
- sensitive-data treatment.

Reuse accepted evaluation cases where possible.

## Task 13 — Prove behavioral drift detection

Introduce one controlled drift in non-production and prove detection.

**TDD/verification:** the detection test must fail before the drift detector is enabled or corrected and pass afterward, where an automated mechanism is implemented.

**Evidence:** introduced change, expected signal, actual detection, and disposition.

## Task 14 — Define release evidence at operational scale

Specify mandatory evidence for a release. If two or more capabilities exist, define coordinated-release evidence without erasing capability-specific requirements.

Exercise against one real release.

## Task 15 — Determine whether records/retention/audit is triggered

Review Phase 3 retrospective and later operational evidence.

Classify:

```text
NOT_TRIGGERED
DISCOVERY_REQUIRED
POLICY_REVIEW_REQUIRED
AUTHORIZED_TO_PLAN
```

Do not proceed merely because Phase 8 contains this subphase.

## Task 16 — Inventory real records/evidence artifacts

If triggered, inventory actual canonical, published, skill, agent, evaluation, deployment, approval, monitoring, superseded, and audit artifacts.

**Evidence:** classification-input inventory.  
**Do not assign final classes without authorized review.**

## Task 17 — Draft records, retention, audit, and supersession proposals

Prepare proposals for qualified review:

- classification memo;
- retention treatment;
- audit proof requirements;
- supersession handling;
- destruction authorization and evidence;
- legal-hold or incident considerations where applicable.

Every proposal must trace to real artifacts and an identified requirement.

## Task 18 — Obtain records/legal/policy review

A named qualified reviewer reviews the proposals.

**Blocking:** no enforcement, automated retention, deletion, destruction, or final policy claim before signed approval.

## Task 19 — Implement only approved operational controls

Create a new bounded implementation subplan for approved technical controls. Do not combine policy drafting and enforcement in one unreviewed task.

Use TDD for code, policy-as-code, validators, drift checks, or automation.

## Task 20 — Assemble evidence and retrospective

Produce:

- capability activation result;
- promotion evidence;
- compatibility result;
- ownership charter;
- incident/drill result;
- retirement result;
- onboarding result;
- monitoring/drift evidence, if activated;
- release evidence;
- records/legal decision, if triggered;
- deferred work and next triggers.

## Task 21 — Exit review and merge gate

Verify:

- originating guarantees remain intact;
- repository tests and target-specific validations pass;
- promotion and rollback evidence exist;
- owners accepted responsibilities;
- monitoring does not over-collect;
- records controls have required approval;
- documentation is current;
- plugin/marketplace metadata disposition is recorded;
- `git status --short` is clean or fully explained.

Obtain explicit approval before merge.

## Task 22 — Update operational indexes and `start-here.md`

Record which capability and Phase 8 subphases are complete, still blocked, or not triggered. Do not imply global Phase 8 completion from one capability's operationalization.

Start subsequent capability work in a fresh session and branch/worktree.

## Agent-cost allocation

### Low-cost agent

- inventories;
- matrices;
- link and version checks;
- evidence collation;
- onboarding-document formatting;
- established validation execution;
- status/index updates.

### Mid-tier implementation agent

- promotion tooling;
- compatibility validators;
- monitoring integration;
- drift detection;
- release-evidence automation;
- approved policy controls.

### Strong reasoning agent

- operational architecture;
- ownership and incident boundaries;
- security/privacy review;
- monitoring scope;
- records/retention/audit interpretation;
- adversarial plan review;
- final acceptance.

## Explicit prohibitions

Do not:

- create a monolithic Phase 8 implementation plan before capabilities exist;
- require Phase 4 or 5 completion before operationalizing a successful Phase 3 library;
- activate cross-capability monitoring with only one capability;
- fabricate service levels, retention periods, or records classes;
- enforce destruction or retention without approval;
- promote without rollback and evidence;
- treat one completed capability as global Phase 8 completion;
- begin another phase automatically.
