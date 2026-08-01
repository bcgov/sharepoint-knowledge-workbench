# Phase 9 Specification — Reusable SharePoint Plugin Extraction


> **Planning status:** This is a forward-phase planning artifact derived from the accepted master initiative plan. It does not authorize implementation. Exact source and destination commits, candidate files, repository paths, commands, plugin boundaries, and test fixtures must be verified through Phase 9 reconnaissance before execution.

## Planning discipline

- Run `superpowers:brainstorming` before finalizing candidate selection or extraction boundaries.
- Verify the pinned CMAT source baseline and current destination repository state.
- Use `superpowers:writing-plans` only after this specification is reviewed and the pilot capability is approved.
- Use a dedicated Phase 9 branch/worktree in the SharePoint Knowledge Workbench.
- Do not change the CMAT repository as part of extraction.
- Use `CONFIRMED`, `RECOMMENDED`, `PROVISIONAL`, `DEFERRED_UNTIL_EVIDENCE`, `BLOCKED`, `RESEARCH`, and `LATER` explicitly.
- Store durable sanitized evidence in tracked locations; keep tenant/environment-specific originals in approved controlled storage.
- Start with the cheapest capable agent and escalate for architecture, security, PowerShell module boundaries, contradictory source behaviour, or failed parity tests.

## 1. Status and authority

**Disposition:** `LATER`.  
**Authority:** The master initiative plan is authoritative. This specification adds detail without changing Phase 9's gates.  
**Current authorization:** Planning artifact only. No extraction, source-repository change, plugin creation, or backlog migration is authorized by this document.

## 2. Goal

Selectively extract one proven generic SharePoint capability family from the existing CMAT replatform repository, refactor it into an independently reusable first-party SharePoint Knowledge Workbench plugin, and prove independence, safety, semantic parity, evidence quality, and source-repository preservation.

## 3. Core repository boundary

```text
CMAT replatform repository
= remains intact, operational, and independently maintained
= source implementation and regression oracle

SharePoint Knowledge Workbench
= receives independently copied and refactored generic capabilities
= owns the new reusable plugin after extraction
```

Phase 9 does not rename, replace, dismantle, or relocate the source repository.

## 4. Candidate scope

Candidate plugin families:

- `sharepoint-discovery` (`RECOMMENDED` first pilot);
- `sharepoint-schema`;
- `sharepoint-page-modernization`;
- `sharepoint-link-analysis`;
- `sharepoint-provisioning`;
- `sharepoint-content-migration`;
- SharePoint validation/reconciliation capability, either plugin or shared infrastructure depending on evidence.

Individual skills currently stored in the source ORDS plugin may be assessed if their actual responsibility is generic SharePoint work. The ORDS API framework and court-system business logic are excluded.

## 5. Non-goals

- No source repository rename or migration.
- No deletion or relocation of source plugins, skills, agents, scripts, rules, or history.
- No cross-repository symlinks, runtime imports, or hidden source dependency.
- No ORDS API/auth/query/paging/retry framework extraction.
- No JUSTIN, CEIS, court-appearance, courthouse, calendar-routing, or CMAT business-rule extraction.
- No automatic migration of all 28 skills, seven agents, source backlog, planned stubs, or historical scripts.
- No immediate CMAT rebind to the extracted plugin.
- No general-purpose routing agent.
- No assumption that the source plugin taxonomy is the correct destination plugin taxonomy.

## 6. Preconditions

| Precondition | Required evidence | Status |
|---|---|---|
| Stable destination plugin conventions | Current first-party plugin and roadmap evidence | `DEFERRED_UNTIL_EVIDENCE` |
| SharePoint expected/actual state and evidence patterns | Accepted Phase 3 outputs | `DEFERRED_UNTIL_EVIDENCE` |
| Immutable source baseline | CMAT commit or immutable bundle plus hashes | `BLOCKED` |
| Candidate inventory | Source plugin/skill/script/rule inventory | `BLOCKED` |
| One pilot family selected | Approved candidate-selection memo | `BLOCKED` |
| Source repository remains independently operable | Baseline tests and dependency record | `BLOCKED` |

## 7. Candidate-selection criteria

The selected pilot must:

- have clear SharePoint value beyond CMAT;
- have a bounded user journey;
- have existing source behaviour, tests, or acceptance criteria;
- be separable from CMAT and ORDS dependencies;
- fit or deliberately extend destination plugin conventions;
- have an accountable owner;
- support neutral fixtures;
- have explicit permission and write boundaries;
- provide differentiated value beside existing workbench plugins;
- permit independent testing without a live CMAT tenant.

Read-only `sharepoint-discovery` is recommended as the first pilot because it minimizes write risk and provides evidence inputs for schema, migration, modernization, governance, and agent readiness.

## 8. Capability disposition model

Every source capability receives one status:

```text
EXTRACT_NOW
EXTRACT_LATER
MERGE_WITH_EXISTING_CAPABILITY
KEEP_PROJECT_SPECIFIC
RESEARCH
RETIRE
REJECT
```

Each disposition must record:

- source location and baseline;
- actual responsibility;
- current consumers;
- reusable value;
- project and environment coupling;
- permissions and write risk;
- test maturity;
- destination overlap;
- owner;
- reason;
- safe default.

## 9. Genericity contract

The extracted plugin must not require:

- CMAT list, field, content-type, wave, or manifest names;
- ORDS, JUSTIN, or CEIS endpoints or data shapes;
- court-appearance, courthouse, or calendar-routing rules;
- BC Government tenant URLs, GUIDs, app registrations, or environment names;
- source-repository paths or symlinks;
- source `CLAUDE.md` or project runbooks at runtime;
- live protected content or raw tenant evidence.

Project-specific examples may appear only in clearly marked historical/provenance documentation or negative-control fixtures, never in live defaults.

## 10. Destination plugin package

Subject to final reconnaissance, the pilot package should contain:

```text
plugin manifest
plugin metadata
bounded skills
scripts or PowerShell modules
schemas/contracts
references
sanitized fixtures
tests/evaluations
acceptance criteria
security and permission notes
provenance manifest
README and lifecycle record
```

Exact paths must follow the destination repository's current conventions at execution time.

## 11. Shared rule reconciliation

Source instructions are classified as:

```text
GENERIC_ENGINEERING
GENERIC_SHAREPOINT
PLUGIN_SPECIFIC
CMAT_SPECIFIC
ENVIRONMENT_FACT
DUPLICATE
CONFLICTING
```

Rules are reconciled, not copied wholesale.

- Generic engineering rules may improve root workbench guidance after review.
- Generic SharePoint rules belong in the approved shared rule layer.
- Plugin-specific rules belong with the extracted plugin.
- CMAT rules and environment facts remain in the source repository.
- Duplicate or conflicting rules receive an explicit decision.

## 12. PowerShell and dependency boundary

The extraction must decide, from evidence, whether reusable code belongs in:

- the plugin's own `scripts/` or modules;
- an existing shared workbench component;
- a new shared component justified by at least two consumers;
- project-specific source code that should not be extracted.

Do not create a shared PowerShell framework for a single consumer. Do not preserve source symlink topology automatically. Prefer explicit modules or plugin-local code when that is simpler and clearer.

## 13. Security and write boundary

- Read-only discovery is the default for the first pilot.
- Every cmdlet or operation is classified read-only, write, permission-management, tenant-admin, or external-system.
- Write capabilities require dry-run, explicit confirmation, least privilege, rollback, partial-failure reporting, and evidence.
- Permission limitations must produce honest partial results, not empty-success reports.
- Credentials, live URLs, GUIDs, group identities, and raw tenant exports do not enter committed fixtures.
- No autonomous production write is introduced through extraction.

## 14. Independence verification

The destination plugin must pass with all source dependencies unavailable:

```text
CMAT repository absent
ORDS configuration absent
source symlinks absent
CMAT schemas absent
BC Government URLs/GUIDs absent
source environment unavailable
```

A transitive dependency scan must confirm no source-runtime dependency remains.

## 15. Semantic parity verification

Parity applies only to behaviours deliberately retained in the generic contract.

For each retained behaviour, record:

- source input/fixture;
- source expected result;
- destination neutral fixture;
- destination result;
- semantic comparison;
- intentional differences;
- reviewer disposition.

Byte identity is not required when the destination contract intentionally improves output. Silent behaviour loss is prohibited.

## 16. Evaluation model

### Normal

Generic SharePoint fixture produces the expected inventory, analysis, or report.

### Negative

Missing permissions, malformed configuration, unsupported object types, missing dependencies, and partial retrieval fail honestly.

### Ambiguous

Conflicting schema, duplicate names, uncertain mappings, or incomplete source evidence is surfaced for review rather than guessed.

### Permission and safety

Read-only boundaries, least privilege, dry-run, confirmation gates, and no-secret/no-live-identifier rules are enforced.

### Independence

The source repository and project configuration are unavailable.

### Parity

Selected generic source behaviours remain intact or intentionally improve under a reviewed contract.

### Mutation

Deliberate project-literal leakage, source dependency, silent partial failure, and unsafe write paths reach their intended detectors.

## 17. Source-repository preservation

Phase 9 must verify:

- no source file was removed or changed by extraction;
- no source plugin was made dependent on the workbench;
- no cross-repository symlink was introduced;
- source tests remain at baseline where safely runnable;
- source history remains intact;
- any future CMAT rebind is a separate, explicitly approved phase or project plan.

## 18. Evidence requirements

```text
source-baseline record
source inventory
source-behaviour matrix
capability disposition matrix
candidate-selection memo
coupling matrix
generic capability contract
provenance manifest
rule-classification report
rule-reconciliation decision
fixture audit
independence test report
parity report
adversarial/mutation matrix
security/write-boundary report
plugin metadata and documentation validation
source-preservation report
remaining-capability roadmap
backlog disposition record
phase-9 retrospective
```

Tracked reports must be sanitized. Controlled originals remain outside Git with evidence IDs and references.

## 19. Lifecycle

Define:

- accountable owner;
- plugin versioning;
- compatibility policy;
- update and rollback process;
- review cadence;
- source-provenance maintenance;
- deprecation and retirement;
- criteria for extracting another plugin family;
- criteria for considering a future CMAT consumer rebind.

## 20. Exit criteria

- One approved generic SharePoint capability family exists as an independent first-party workbench plugin.
- The source baseline is pinned and every retained behaviour is traceable.
- No live CMAT, ORDS, JUSTIN, CEIS, tenant, environment, credential, or cross-repository runtime dependency remains.
- Neutral fixtures and complete tests exist.
- Independence, semantic parity, negative, ambiguous, permission/safety, and mutation cases pass.
- Shared rules were reconciled without importing project overlays.
- The source CMAT repository and plugins remain unchanged and independently operable.
- Remaining capabilities and backlog items are dispositioned rather than automatically copied.
- Ownership and lifecycle are documented.
- No CMAT rebind, second extraction, or general orchestrator begins automatically.

## 21. Deferred work

- Additional plugin families after the pilot.
- Write-capable provisioning and migration extraction.
- Shared validation or PowerShell infrastructure until multiple consumers justify it.
- Agent adaptation and cross-plugin orchestration.
- CMAT rebinding to consume reusable plugins.
- Distribution, marketplace, and production support commitments beyond the approved pilot.
