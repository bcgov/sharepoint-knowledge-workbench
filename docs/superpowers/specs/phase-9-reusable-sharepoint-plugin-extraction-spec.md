# Phase 9 Specification — Reusable SharePoint Plugin Extraction


> **Planning status:** `PLANNED`, `EVIDENCE_BASED`, `NOT_IMPLEMENTATION_AUTHORIZATION`, `SOURCE_BASELINE_REQUIRES_PINNING`. This is a forward-phase planning artifact derived from the accepted master initiative plan. It does not authorize implementation. Exact source and destination commits, candidate files, repository paths, commands, plugin boundaries, and test fixtures must be verified through Phase 9 reconnaissance before execution. Phase 9 has not started.

> **Evidence-baseline update (2026-08-01):** A documentation-only reconciliation pass replaced hypothetical candidate descriptions with the actual observed source inventory at `/Users/richardfremmerlid/Projects/jag-csb-cmat-sharepoint-online/plugins/sharepoint-migration/skills/` — **119 directories, 272 files (144 real files + 128 symlinks)** across 33 skills. This inventory is a **source baseline for future classification**, not an extraction authorization, and not a permanent total — the source repository continues to evolve independently. See §3a (Source Evidence Baseline) below. No code, plugin, or CMAT-repository artifact was touched by this reconciliation; see the companion completion report for the exact diff.

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

## 3a. Source Evidence Baseline (observed, not pinned)

**Status:** `SOURCE_BASELINE_REQUIRES_PINNING` — this is an observed inventory snapshot used to strengthen Phase 9 planning, not a pinned extraction baseline. Stage 9.0.1 (below) must pin an exact commit before any extraction begins.

**Location:** `jag-csb-cmat-sharepoint-online/plugins/sharepoint-migration/skills/` (separate GitHub repository, local checkout only — no cross-repository dependency is created by referencing it here).

**Observed scale:** 119 directories, 272 files (144 real files + 128 file-level symlinks) across 33 skills. These figures describe the supplied baseline inventory at the time of this reconciliation (2026-08-01); they are **not permanent totals** — the source repository continues to change independently.

**Observed skill inventory (33 skills, grouped by likely capability family):**

```text
Discovery
  sp-discovering-site-structure
  sp-discovering-lists
  sp-discovering-content-types
  sp-discovering-pages
  sp-discovering-web-parts
  sp-discovering-navigation
  sp-discovering-forms
  sp-discovering-permissions
  sp-discovering-workflows
  sp-synthesizing-discovery

Schema
  sp-auditing-schema
  sp-extracting-choices
  sp-mapping-content-types
  sp-mapping-lists
  sp-mapping-taxonomy
  sp-synthesizing-deployment-matrix

Page modernization
  sp-analysing-aspx-pages
  sp-converting-aspx-pages
  sp-converting-wiki-pages
  sp-remediating-page-layouts
  sp-remediating-web-parts

Link analysis
  sp-extracting-links
  sp-remediating-links
  sp-remediating-document-content-links
  sp-validating-link-integrity

Content migration
  sp-content-migration
  sp-migrating-content
  sp-uploading-content
  sp-running-sharegate-jobs

Provisioning and validation
  sp-provisioning-modern-calendars
  sp-validating-app-registration
  sp-validating-content
  sp-validating-permissions

Reporting and synthesis
  sp-generating-migration-reports
  sp-synthesizing-discovery        (cross-listed with discovery)
  sp-synthesizing-deployment-matrix (cross-listed with schema)
```

This grouping is a **classification hypothesis for Phase 9 planning**, not a committed plugin taxonomy. Actual destination boundaries are decided during Stage 9.2 using the disposition model below, not assumed from this list.

### Implementation-status signal (spot-checked, not exhaustive)

A rough per-skill file count was spot-checked during this reconciliation to sanity-check the hypothesis that source maturity varies widely across skills. Confirmed:

| Skill | File count (spot-check) | Preliminary signal |
|---|---|---|
| `sp-converting-aspx-pages` | 27 | Rich implementation — includes inventory analysis, component classification, layout selection, component mapping, manifest generation/validation, preview generation, report generation, mapping-matrix updates, page-specific scripts, fixtures, pipeline evaluations, unit tests, acceptance criteria, layout rules, manifest schema, architecture diagram |
| `sp-remediating-page-layouts` | 4 | Thin — likely `PLANNED_WITH_NO_STANDALONE_IMPLEMENTATION` |
| `sp-remediating-web-parts` | 4 | Thin — likely `PLANNED_WITH_NO_STANDALONE_IMPLEMENTATION` |
| `sp-discovering-site-structure` | 3 | Thin — likely `PLANNED_WITH_NO_STANDALONE_IMPLEMENTATION` |
| `sp-content-migration` | 4 | Thin — likely mixes generic migration behavior, PnP helpers, ShareGate integration, CMAT-specific waves, deprecated stage scripts |

**This spot-check is illustrative, not the required Stage 9.1/9.2 classification.** A complete implementation-status pass over all 33 skills is required before any pilot selection, per §3b below. Do not treat the presence of `SKILL.md`, `evals.json`, or `results.tsv` as proof that a skill is implemented — the actual script/test/fixture count must be inspected per skill.

## 3b. Implementation-Status and Destination-Disposition Models

Phase 9 requires **two separate classifications** for every source artifact — conflating them was identified as a risk during this reconciliation (a "planned" skill and a "reject this destination" skill are different judgments).

### Implementation-status vocabulary (what actually exists in the source)

```text
ACTIVE_AND_PROVEN
ACTIVE_REQUIRES_REFACTORING
EXPERIMENTAL
PLANNED_WITH_NO_STANDALONE_IMPLEMENTATION
DEPRECATED
HISTORICAL
PROJECT_SPECIFIC
```

### Destination-disposition vocabulary (where it belongs, if anywhere)

```text
EXTRACT_AS_NEW_PLUGIN
EXTRACT_AS_SKILL_IN_EXISTING_PLUGIN
MERGE_WITH_EXISTING_CAPABILITY
EXTRACT_AS_SHARED_CONTRACT
EXTRACT_AS_SHARED_LIBRARY
KEEP_PROJECT_SPECIFIC
RESEARCH
RETIRE
REJECT
```

These replace/extend the single `EXTRACT_NOW` / `EXTRACT_LATER` / ... disposition model in §8 below with a two-axis model: implementation status is a fact about the source; destination disposition is a decision about the workbench. Example:

```text
Source capability: sp-remediating-page-layouts
Implementation status: PLANNED_WITH_NO_STANDALONE_IMPLEMENTATION
Destination disposition: RESEARCH (or MERGE_WITH_EXISTING_CAPABILITY if a working
  implementation is later found nested inside another pipeline)
```

§8's disposition vocabulary (`EXTRACT_NOW`/`EXTRACT_LATER`/etc.) remains valid as the **backlog-priority axis**; Stage 9.2 must apply all three axes (implementation status, destination disposition, backlog priority) to every artifact, not just one.

## 4. Candidate scope

Candidate plugin families (provisional destination hypotheses, not automatic Phase 9 deliverables — see §3b):

- `sharepoint-discovery`;
- `sharepoint-schema`;
- `sharepoint-page-modernization` — the observed 27-file `sp-converting-aspx-pages` implementation makes this a materially stronger pilot candidate than originally assumed; see Stage 9.2.3;
- `sharepoint-link-analysis` — kept distinct from page modernization: link extraction/classification/remediation/validation have different contracts and validation requirements than page reconstruction, and must not be folded into `sharepoint-page-modernization` by default;
- `sharepoint-provisioning`;
- `sharepoint-content-migration`;
- `sharepoint-validation-and-reconciliation`, either plugin or shared infrastructure depending on evidence.

A capability may instead resolve to a skill inside an existing plugin, a shared contract, a shared library, plugin-local/repository-level test infrastructure, research-only, or a rejected/retired item — the list above is not a commitment that seven new plugins will exist.

Individual skills currently stored in the source ORDS plugin may be assessed if their actual responsibility is generic SharePoint work (e.g. generic schema validation, generic duplicate detection, a generic evidence/safe-dry-run pattern). The ORDS API framework itself, its authentication/query/pagination/retry machinery, and JUSTIN/CEIS business rules are excluded — classify by responsibility, not folder location.

## 4a. Relationship to Phase 4.5

```text
Phase 4.5 → establishes the common plugin operating model:
  plugin manifests, domain-native skill ownership, implementation-status metadata,
  independent semantic versions, contract versions, compatibility matrix,
  plugin-local tests, shared contract fixtures, repository integration tests,
  documentation categories, marketplace registration, dependency rules,
  write-safety declarations, evidence packages, lifecycle and removal gates.

Phase 9 → adds selectively extracted SharePoint engineering capabilities
  using that same model.
```

Phase 9 must reuse Phase 4.5 conventions rather than inventing a second plugin format, skill format, versioning model, test architecture, or marketplace model.

**Relationship to the four Phase 4.5 core knowledge plugins** — Phase 9 must compare each source capability against these existing domains before creating a new plugin:

| Source capability shape | Compare against |
|---|---|
| Extracting content from SP2016/classic pages | `source-document-extraction` |
| Semantic analysis of extracted content | `knowledge-analysis` |
| Building reusable structured knowledge | `canonical-knowledge` |
| Rendering human- or agent-facing representations | `knowledge-publication` |
| Reconstructing classic SharePoint pages/web parts | `sharepoint-page-modernization` (new) |
| Inventorying sites, lists, permissions, web parts | `sharepoint-discovery` (new) |
| Capturing/comparing fields, content types, taxonomy | `sharepoint-schema` (new) |
| Publishing SharePoint objects | `sharepoint-provisioning` or a future `sharepoint-publication` |
| Validating source-target parity | `sharepoint-validation-and-reconciliation` (new) |

`knowledge-publication` renders canonical knowledge into consumer representations; `sharepoint-page-modernization` reconstructs legacy SharePoint page *experiences and components*. These are not the same responsibility and must not be conflated.

## 4b. Long-Term Workbench Scope Intent

Phase 9's eventual outcome is intended to expand this repository from a knowledge-conversion workbench into a broader SharePoint engineering workbench — covering not only knowledge publication but also site migration, page conversion/analysis, and web-part analysis. This is a **stated future direction, not an authorization**: it informs why the plugin conventions established in Phase 4.5 must be general enough for both families, but it does not change Phase 9's `LATER` disposition or its entry gate.

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

Every source capability receives a backlog-priority status (this is the third axis alongside the implementation-status and destination-disposition axes defined in §3b — all three must be recorded, not just this one):

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
- safe default;
- **implementation-status** (§3b);
- **destination-disposition** (§3b).

## 8a. Symlink Inventory Requirement

The source skill taxonomy makes extensive use of skill-local file symlinks pointing to centralized scripts, configuration examples, shared templates, project analysis files, references in other skills, deprecated scripts, and test harnesses (128 of the observed 272 files are symlinks — see §3a).

Phase 9 must inventory every symlink before extraction, recording:

```text
link path
resolved source
artifact type
current owner
implementation status
genericity
runtime necessity
destination owner
copy / refactor / replace decision
```

Source symlinks must **not** be reproduced automatically in the destination plugin. No extracted plugin may depend at runtime on the CMAT repository — every symlink target that is retained must be physically copied and refactored into the destination plugin's own hub-and-spoke structure (per this repository's `plugin-architecture-policy.md` and `symlink-cross-platform.md` rules), never linked back to the source.

## 8b. Provenance Requirement

Every extracted capability must record:

```text
source repository
source commit
source plugin
source skill
source scripts
source tests
source references
source implementation status
destination plugin or skill
removed project coupling
intentional behavior changes
new neutral fixtures
parity evidence
```

The workbench must not erase a capability's origin. This is in addition to, not a replacement for, the provenance manifest already required in §18 and §19 (`provenance manifest`, Subphase 9.3.3).

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

**Exit statement:** At least one proven generic SharePoint capability family has been independently extracted from a pinned CMAT source baseline into the SharePoint Knowledge Workbench using the Phase 4.5 plugin conventions. The extracted capability has no runtime dependency on CMAT, ORDS, project-specific environments, source-repository paths, or cross-repository symlinks; uses neutral contracts and fixtures; passes independent and parity tests; records complete provenance; and leaves the original CMAT repository unchanged and independently operable. Every remaining source capability has an implementation-status and destination disposition rather than being copied automatically.

- One approved generic SharePoint capability family exists as an independent first-party workbench plugin, built using Phase 4.5's manifest, skill-ownership, versioning, test-tier, and documentation conventions (§4a).
- The source baseline is pinned (exact commit) and every retained behaviour is traceable.
- No live CMAT, ORDS, JUSTIN, CEIS, tenant, environment, credential, or cross-repository runtime dependency remains.
- No source symlink was reproduced at runtime in the destination plugin (§8a).
- Neutral fixtures and complete tests exist.
- Independence, semantic parity, negative, ambiguous, permission/safety, and mutation cases pass.
- Shared rules were reconciled without importing project overlays.
- The source CMAT repository and plugins remain unchanged and independently operable.
- Every remaining source capability (all 33 observed skills, not only the extracted one) has an implementation-status classification (§3b) and a destination disposition (§3b) — none are copied automatically.
- Ownership and lifecycle are documented.
- No CMAT rebind, second extraction, or general orchestrator begins automatically.

## 21. Deferred work

- Additional plugin families after the pilot.
- Write-capable provisioning and migration extraction.
- Shared validation or PowerShell infrastructure until multiple consumers justify it.
- Agent adaptation and cross-plugin orchestration.
- CMAT rebinding to consume reusable plugins.
- Distribution, marketplace, and production support commitments beyond the approved pilot.
