# Phase 9 Plan Scaffold — Reusable SharePoint Plugin Extraction


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

## Entry gate

Do not finalize or execute this plan until the Phase 9 specification is approved, the source baseline is pinned, one pilot capability is selected, and current destination plugin conventions are verified.

## Task 0 — Confirm entry evidence

**Deliverable:** Phase 9 entry-gate checklist.  
**Verification:** every prerequisite links to accepted evidence.  
**Stop condition:** missing source baseline, missing owner, unresolved source-repository authority, or no selected pilot blocks execution.

## Task 1 — Run Superpowers brainstorming and select the pilot family

Compare at least `sharepoint-discovery`, `sharepoint-schema`, and `sharepoint-page-modernization`. Record expected value, source maturity, coupling, write risk, overlap, users, owner, and rejected alternatives.

**Recommended candidate:** `sharepoint-discovery`.  
**Evidence:** candidate-selection memo.  
**Commit:** planning artifacts only.

## Task 2 — Pin and manifest the source baseline

Record the CMAT repository commit or immutable bundle, hashes, source plugin versions, applicable tests, and evidence location.

**Verification:** baseline can be independently resolved.  
**Prohibition:** do not modify the source repository.

## Task 3 — Inventory source artifacts and behaviours

Inventory relevant plugins, skills, agents, scripts, modules, tests, fixtures, references, rules, assets, configuration, symlinks, planned stubs, and consumers.

Create a source-behaviour matrix linking capability claims to real tests or evidence.

**Evidence:** inventory completeness check and source-behaviour matrix.

## Task 4 — Classify capabilities and backlog

Apply:

```text
EXTRACT_NOW
EXTRACT_LATER
MERGE_WITH_EXISTING_CAPABILITY
KEEP_PROJECT_SPECIFIC
RESEARCH
RETIRE
REJECT
```

Review individual skills under the ORDS plugin for generic SharePoint value, while excluding the ORDS framework and court-system rules.

**Evidence:** capability matrix and backlog disposition record.  
**No automatic migration.**

## Task 5 — Build the coupling matrix

Search and classify:

- CMAT/ORDS/JUSTIN/CEIS literals;
- list, field, content-type, and wave names;
- tenant URLs, GUIDs, app registrations, and environments;
- business rules;
- authentication assumptions;
- cross-plugin calls and symlinks;
- source paths;
- configuration and write permissions;
- test and fixture dependencies.

**Verification:** every dependency has a disposition.  
**Evidence:** raw scan output plus reviewed coupling matrix.

## Task 6 — Define the generic capability contract

Specify target-neutral inputs, outputs, errors, result statuses, permissions, dry-run behaviour, evidence, versioning, and safe defaults.

**Adversarial review:** challenge renamed project concepts, hidden environment assumptions, silent partial success, and speculative abstraction.

## Task 7 — Reconcile shared instructions and rules

Classify source `CLAUDE.md`, Copilot instructions, and applicable rule files. Produce proposed destination changes without wholesale copying.

**Verification:** CMAT and environment overlays remain in the source.  
**Evidence:** rule-classification report and reviewed diff.

## Task 8 — Decide the code and module boundary

Determine whether each reusable component remains plugin-local, uses an existing shared component, justifies a new shared component with multiple consumers, or remains source-project-specific.

Do not reproduce the source symlink structure automatically.

**Evidence:** module-boundary decision record.

## Task 9 — Write failing contract and safety tests

Before implementation, create tests for:

- generic inputs and outputs;
- missing configuration;
- permission denial;
- partial discovery;
- no project literals;
- no source dependency;
- read-only default;
- no silent success;
- sanitized evidence;
- provenance.

**TDD:** tests fail for the intended reason before extracted implementation is added.

## Task 10 — Create neutral fixtures

Build project-independent fixtures covering normal, negative, ambiguous, permission, partial-failure, and scale boundaries appropriate to the selected capability.

**Verification:** fixture audit finds no live identifiers, protected content, CMAT schema, or ORDS data.

## Task 11 — Create the destination plugin scaffold

Create only the selected plugin using current workbench conventions:

```text
manifest and metadata
bounded skills
scripts/modules
schemas
references
fixtures
tests
acceptance criteria
README
```

**Verification:** plugin/marketplace metadata and path conventions are checked against the current repository, not assumed from this scaffold.

## Task 12 — Extract and refactor the selected capability

Copy only approved source material into the Phase 9 worktree. Remove or replace project coupling through neutral contracts and explicit configuration.

Preserve source provenance for each adapted component.

**Prohibition:** no runtime dependency, symlink, or import back to the CMAT repository.

## Task 13 — Implement honest partial-failure reporting

Ensure each probe or sub-operation reports `Observed`, `Empty`, `Forbidden`, `Unavailable`, `NotSupported`, `Partial`, or `Failed` rather than collapsing failures into empty success.

**Evidence:** negative tests and result examples.

## Task 14 — Prove read-only and permission boundaries

For a discovery pilot, classify every operation and prove no write path is reachable. For later write-capable plugins, use a separately approved plan with dry-run, confirmation, least privilege, rollback, and evidence.

**Blocking:** any unauthorized tenant write or permission expansion.

## Task 15 — Prove independence

Run tests with the CMAT repository, source configuration, cross-repository symlinks, CMAT schemas, and environment values unavailable.

Add a transitive dependency scan and negative-control self-test.

**Evidence:** independence report and exact suite counts.

## Task 16 — Prove semantic parity

Execute selected generic source behaviours against source oracles and destination neutral fixtures. Compare meaning, not incidental formatting.

Record every intentional improvement or divergence.

**Evidence:** parity report with reviewer dispositions.

## Task 17 — Run adversarial and mutation evaluations

Deliberately introduce:

- forbidden project literals;
- source-repository imports;
- malformed configuration;
- missing permissions;
- partial result loss;
- unsafe write reachability;
- false PASS states;
- provenance breaks.

Prove intended detection and retain required meta-tests.

## Task 18 — Integrate plugin documentation and metadata

Update applicable:

- plugin metadata;
- marketplace metadata;
- root README;
- architecture;
- dependency records;
- plugin documentation;
- evidence index;
- `start-here.md`.

Distinguish implemented capabilities from later extraction candidates.

## Task 19 — Define lifecycle and ownership

Record owner, versioning, compatibility, review cadence, provenance maintenance, update/rollback, deprecation, retirement, and the gate for another extraction.

Exercise one safe update/rollback or artifact-removal path where applicable.

## Task 20 — Prove source-repository preservation

Verify that extraction changed no source file, created no source dependency on the workbench, and introduced no cross-repository symlink.

Run the pinned source baseline tests where safely available or compare against the immutable baseline.

**Evidence:** source-preservation and non-rebinding report.

## Task 21 — Prioritize remaining plugin families

Rank remaining discovery, schema, page-modernization, link, provisioning, content-migration, and validation candidates using evidence from the pilot.

Do not start a second extraction.

## Task 22 — Consolidate evidence and retrospective

Produce the Phase 9 evidence report and `phase-9-retrospective.md`. Cite every artifact, limitation, intentional divergence, and deferred candidate.

## Task 23 — Exit review and merge gate

Verify:

- all tests and mutations pass;
- no live project/environment dependency remains;
- source repository is unchanged;
- plugin metadata and docs are correct;
- evidence is sanitized;
- ownership exists;
- no CMAT rebind or second extraction began;
- `git status --short` is clean or fully explained.

Obtain explicit approval before merge.

## Cost allocation

- **Low-cost agent:** inventories, path/link checks, literal scans, trace tables, fixture audits, evidence collation, established test commands.
- **Mid-tier implementation agent:** PowerShell/module refactoring, schemas, validators, fixtures, plugin code, parity harnesses, debugging.
- **Strong reasoning agent:** candidate selection, generic capability contract, coupling decisions, shared-rule reconciliation, security/write boundary, adversarial review, final acceptance.

## Explicit prohibitions

Do not:

- modify or rename the CMAT repository;
- move or delete source plugins;
- extract the ORDS integration framework;
- migrate all skills or backlog items automatically;
- preserve cross-repository symlinks;
- create speculative shared infrastructure for one consumer;
- weaken tests to force parity;
- introduce autonomous production writes;
- rebind CMAT to the workbench;
- start a second plugin extraction automatically.
