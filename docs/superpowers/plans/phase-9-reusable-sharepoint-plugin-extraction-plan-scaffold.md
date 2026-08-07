# Phase 9 Plan Scaffold — Reusable SharePoint Plugin Extraction


> **Planning status:** `PLANNED`, `EVIDENCE_BASED`, `NOT_IMPLEMENTATION_AUTHORIZATION`, `SOURCE_BASELINE_REQUIRES_PINNING`. This is a forward-phase planning artifact derived from the accepted master initiative plan. It does not authorize implementation. Exact source and destination commits, candidate files, repository paths, commands, plugin boundaries, and test fixtures must be verified through Phase 9 reconnaissance before execution. Phase 9 has not started.

> **Evidence-baseline update (2026-08-01, historical):** See `phase-9-reusable-sharepoint-plugin-extraction-spec.md` §3a for the observed source inventory (119 dirs / 272 files / 33 skills) that grounded Tasks 1–5 below at the time. This is a source baseline for classification, not a pinned extraction commit.
>
> **Superseded (2026-08-03):** a direct recount found **34 skill directories**, not 33/31 —
> corrected across all Phase 9 documents. See spec §8d for the complete, current 34-skill mapping
> with per-skill implementation-status, destination, and disposition.

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

**Phase 3 entry-gate waiver — scoped, not blanket (recorded 2026-08-07).** Spec §6 lists "SharePoint expected/actual state and evidence patterns — Accepted Phase 3 outputs" as a precondition. Phase 3's exit gate is **confirmed not met** (verified 2026-08-07: the master plan lists Phase 3 as `NEXT, gated behind 3.0`; no `docs/reports/phase-3-*` evidence directory exists). Richard has explicitly authorized proceeding with Phase 9 entry-gate work regardless.

That waiver is sound for capabilities whose contracts do **not** depend on Phase 3's unfinished decisions — discovery, schema, page modernization, link remediation. Phase 3 owns the destination library's metadata schema, source-of-truth lifecycle, and republish/rollback policy, none of which those capabilities touch.

It is **not** sound for publication-path work. `sp-uploading-content` → `sharepoint-content-publication` writes into exactly the library whose schema and lifecycle Phase 3 has not yet decided. Extracting it now risks encoding a contract that Phase 3 later contradicts.

**Recommended handling:** treat the waiver as covering non-publication capabilities only. `sp-validating-app-registration` → `workbench-setup` is unaffected (pure auth validation, upstream of any publication decision) and is the safer first merge. Any publication-path extraction should either wait for Phase 3, or be built deliberately contract-thin with the Phase 3 dependency recorded as an explicit limitation.

**Phase 6 overlap finding (2026-08-03, not Phase 9 execution):** see the Phase 9 spec's §8c for
the full comparison of Phase 6 Task 0's 30 skills against CMAT's `sharepoint-migration` plugin.
`rollback-sharepoint-publication` has no CMAT counterpart at all (confirmed genuinely new work,
both repos). **No new Phase 9 plugin is justified by the Phase 6 overlap subset alone. The
broader CMAT inventory still contains distinct SharePoint engineering domains that require Phase
9 destination classification** — see spec §8d for the complete 34-skill mapping (corrected from
the previously-cited 31/33) and §8e for the full destination-architecture evaluation: 5 of 7
provisional candidate plugins (`sharepoint-discovery`, `sharepoint-schema`, `sharepoint-page-
modernization`, `sharepoint-link-remediation`, `sharepoint-content-migration`) are provisionally
justified by real implemented evidence; 2 (`sharepoint-provisioning`, `sharepoint-validation-and-
reconciliation`) are not currently justified as standalone plugins. None of this authorizes Phase
9 execution.

## Amendments (2026-08-07) — read before executing any task below

A direct structural inspection of the source tree produced five changes to this plan. The task list below is otherwise unchanged; these amendments override it where they conflict.

1. **The extraction unit is `scripts/`, not `skills/`** (spec §3c). CMAT skills are 3-file shells symlinking into a centralized 183-file `scripts/` tree. **New Task 8a** extracts the shared `scripts/lib/` foundation layer *before* skill extraction. Spec §12's "no shared framework for a single consumer" prohibition does not apply — `lib/` has 9+ consumers in the source, which is evidence.
2. **Symlink resolution must precede classification.** Task 8's symlink inventory currently runs *after* Tasks 3/4 have already classified skills using symlink counts. **New Task 2a** moves resolution/verification ahead of classification. Task 8 retains the destination-side copy/refactor decisions.
3. **Agents were never classified.** 9 agent files exist (spec §8f); the plan and spec covered skills only. **New Task 3a** classifies them.
4. **Literal density is a selection axis.** Task 1 must score genericization cost, not just write risk — the flagship read-only discovery scripts are the two most literal-saturated files in the source (spec §8h).
5. **Task 21 is rewritten** from "do not start a second extraction" to a batched-wave model matching the actual goal of broad reusable coverage.

**Repository hard gates (spec §9a) apply to every task that touches `plugins/`:** `symlink_manager.py diagnose` before/after with zero broken links and zero real-file imposters, `audit_plugin_structure.py <plugin>`, `plugin_add.py <plugin-path> -y`, `isolated_install_check.py`, a `map-debt.md` entry for every friction event (including inline fixes), and the verbatim Pre-Completion Gate block before claiming any task complete. No deletions without explicit human permission.

## Task 0 — Confirm entry evidence

**Deliverable:** Phase 9 entry-gate checklist.  
**Verification:** every prerequisite links to accepted evidence.  
**Stop condition:** missing source baseline, missing owner, unresolved source-repository authority, or no selected pilot blocks execution.

## Task 1 — Run Superpowers brainstorming and select the pilot family

Compare at least `sharepoint-discovery`, `sharepoint-schema`, and `sharepoint-page-modernization`. Record expected value, source maturity, coupling, write risk, overlap, users, owner, and rejected alternatives.

**Do not hard-code `sharepoint-discovery` as the winner without this comparison.** The observed source inventory (spec §3a) shows `sp-converting-aspx-pages` (the core of `sharepoint-page-modernization`) has a materially richer implementation (27 files: inventory analysis, component classification, layout selection, component mapping, manifest generation/validation, preview generation, report generation, pipeline evaluations, unit tests, acceptance criteria, layout rules, manifest schema, architecture diagram) than most discovery skills (3-10 files each, several likely `PLANNED_WITH_NO_STANDALONE_IMPLEMENTATION`). This may make page modernization a stronger pilot than originally assumed — Task 1 must weigh actual implementation maturity, not just read/write risk, when selecting.

**No candidate is pre-selected.** The prior "Recommended candidate: sharepoint-discovery" language is superseded by this evidence — a full implementation-status pass (Task 4) is required before any recommendation is reaffirmed.

**Fourth selection axis added 2026-08-07 — literal density / genericization cost (spec §8h).** Score every candidate on this axis alongside value, maturity, coupling, and write risk. Write risk and extraction cost are independent: the two scripts backing `sp-discovering-site-structure` — the flagship of the "safe, read-only" `sharepoint-discovery` candidate — carry **178 and 147 project-literal hits**, the highest of any non-deprecated files in the source. Spec §7's read-only recommendation is a *safety* statement and must not be read as a cost statement. 57 files repo-wide require scrubbing.

**Selection must also consume Task 2a's recomputed implementation signals**, not §8d's raw symlink counts — three candidate-anchoring skills are affected by broken/deprecated/escaping links.  
**Evidence:** candidate-selection memo.  
**Commit:** planning artifacts only.

## Task 2 — Pin and manifest the source baseline

Record the CMAT repository commit or immutable bundle, hashes, source plugin versions, applicable tests, and evidence location.

**Verification:** baseline can be independently resolved.  
**Prohibition:** do not modify the source repository.

## Task 2a — Resolve and verify every symlink (NEW, 2026-08-07 — must precede Task 4)

Against the commit pinned in Task 2, walk every symlink under `plugins/sharepoint-migration/skills/` and record its **resolved** target. Classify each as exactly one of:

```text
LIVE                — resolves to a real, non-deprecated file inside the plugin
BROKEN              — dangling (4 known: sp-auditing-schema ×1, sp-migrating-content ×3)
DEPRECATED_TARGET   — resolves into scripts/_deprecated/ (12 known, all sp-migrating-content)
ESCAPES_PLUGIN      — resolves outside plugins/ (6 known, sp-discovering-web-parts → 01_source_sharepoint/analysis)
PROJECT_DATA        — resolves to project analysis data rather than executable capability
```

Then recompute each skill's implementation signal as **`LIVE` links + real files beyond the 3-file baseline** (`SKILL.md`, `evals/evals.json`, `evals/results.tsv`).

**Why this must run before Task 4:** spec §8d's implementation statuses were derived from raw symlink counts that include all five classes above. Three skills that anchor §8e plugin justifications are affected — `sp-auditing-schema` (sole basis for `sharepoint-schema`), `sp-migrating-content` (sole basis for `sharepoint-content-migration`), `sp-discovering-web-parts` (anchors `sharepoint-discovery`).

**Deliverable:** resolved-symlink matrix, one row per link.
**Verification:** every link in the source has exactly one class; recomputed per-skill signals are stated alongside §8d's original figures with deltas called out.
**Prohibitions:** do not repair broken links in CMAT (§17 forbids source modification); never extract `BROKEN`, `DEPRECATED_TARGET`, or `ESCAPES_PLUGIN` targets without an explicit, recorded human decision.

## Task 3 — Inventory source artifacts and behaviours

Inventory relevant plugins, skills, agents, scripts, modules, tests, fixtures, references, rules, assets, configuration, symlinks, planned stubs, and consumers.

Use the observed baseline in spec §3a/§8d (119 dirs / 272 files, **34 skills** — directly re-counted 2026-08-03, corrected from the earlier 33/31 figures — across discovery, schema, page-modernization, link-analysis, content-migration, provisioning/validation, and reporting families) as the starting point — re-verify it against the pinned commit from Task 2, since the source repository continues to change independently and these figures are a snapshot, not a permanent total.

Create a source-behaviour matrix linking capability claims to real tests or evidence. Do not treat the presence of `SKILL.md`, `evals.json`, or `results.tsv` alone as proof of implementation — inspect actual script/test/fixture counts per skill (spec §3a's spot-check found a range from 3 files to 27 files across skills).

**Evidence:** inventory completeness check and source-behaviour matrix.

## Task 3a — Classify the 9 agents (NEW, 2026-08-07)

Apply the same three axes as Task 4 to every file in `plugins/sharepoint-migration/agents/` (spec §8f), plus an agent-specific orchestration-coupling judgment:

```text
GENERIC_SHAREPOINT_AGENT
AGENT_REQUIRES_GENERICIZING
ORCHESTRATOR_COUPLED_TO_CMAT_WAVES
PROJECT_SPECIFIC_AGENT
```

Agents in scope: `sp-discovery-agent`, `sp-schema-agent`, `sp-modernization-agent`, `sp-link-agent`, `sp-migration-agent`, `sp-validation-agent`, `sp-deployment-planner`, `sp-migration-orchestrator`, `sp-wave-orchestrator` — plus `agents/references/`.

**Destination matching:** this repository already owns `plugins/sharepoint-agents-and-skills/`. Per the §8c destination-plugin-matching rule, every extraction-eligible agent must be matched against that plugin **before** any new agent-hosting plugin is proposed.

**Known signal:** `sp-wave-orchestrator.md` carries 33 project-literal hits and orchestrates CMAT's wave model — provisionally `ORCHESTRATOR_COUPLED_TO_CMAT_WAVES`. Per-domain agents are the more plausible generic candidates; none inspected in detail yet.

**Deliverable:** agent-classification matrix (9 rows).
**Verification:** every agent has all four judgments and a destination or an explicit rejection reason.

## Task 4 — Classify capabilities and backlog (three-axis model)

Apply all three classification axes to every one of the **34** observed skills (spec §3b/§8d —
corrected from the earlier 33/31 counts), not just one:

**Axis 1 — Implementation status** (what actually exists in source):
```text
ACTIVE_AND_PROVEN
ACTIVE_REQUIRES_REFACTORING
EXPERIMENTAL
PLANNED_WITH_NO_STANDALONE_IMPLEMENTATION
DEPRECATED
HISTORICAL
PROJECT_SPECIFIC
```

**Axis 2 — Destination disposition** (where it belongs, if anywhere):
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

**Axis 3 — Backlog priority** (spec §8):
```text
EXTRACT_NOW
EXTRACT_LATER
MERGE_WITH_EXISTING_CAPABILITY
KEEP_PROJECT_SPECIFIC
RESEARCH
RETIRE
REJECT
```

Review individual skills under the ORDS plugin for generic SharePoint value (e.g. generic schema validation, generic duplicate detection, a generic evidence/safe-dry-run pattern), while excluding the ORDS framework itself and JUSTIN/CEIS court-system rules — classify by responsibility, not folder location.

**Evidence:** three-axis capability matrix and backlog disposition record.  
**No automatic migration.**

## Task 4a — Destination classification against the final workbench plugin inventory

Match every capability from Task 4 against the **current, final** workbench plugin inventory —
`source-document-extraction`, `document-structure-analysis`, `structured-content-assembly`,
`structured-content-rendering`, `sharepoint-content-publication`, `sharepoint-agents-and-skills`,
`workbench-setup` — before considering any new plugin. Spec §8e is the starting classification
(5 of 7 candidate plugins provisionally justified, 2 not); this task re-verifies it against
whatever the workbench plugin inventory actually looks like at Phase 9 execution time (it may have
changed since this note was written).

**Deliverable:** destination-classification record, one row per capability, stating existing-
plugin-owner-found or no-suitable-owner-found.  
**Verification:** every capability assigned to an existing plugin unless it demonstrably has no
suitable owner.  
**Evidence:** the classification record plus spec §8e's justification criteria applied per
candidate plugin.

## Task 4b — Overlap analysis with Phase 6 capabilities

Cross-check every Task 4 capability against the Phase 6 Task 0 skill set (spec §8c, 30 skills).
Confirm no Phase 9 candidate silently duplicates a Phase 6 skill's *scope* (narrower Phase 6
skills and broader CMAT capabilities may share a name without being the same responsibility — see
§8c's `render-sharepoint-aspx` vs. `sp-converting-aspx-pages` comparison for the pattern to
follow).

**Deliverable:** overlap-analysis record.  
**Verification:** every Phase 6 skill with a CMAT counterpart (§8c's 8 explicit comparisons) has
its Phase 9 disposition re-confirmed against Phase 6's actual built state at Phase 9 execution
time (not just this note's snapshot).  
**Evidence:** the overlap record.

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

## Task 5a — Plugin-boundary confirmation

For each of the 7 candidate plugins (spec §8e), confirm or reject its boundary justification using
the stated criteria: distinct domain, cohesive responsibility, independent installation value,
real implemented skills/scripts (not `SKILL.md`/`evals.json`/`results.tsv` alone), independent
testing, lifecycle/versioning rationale, no suitable existing owner. §8e's provisional finding (5
justified, 2 not) is a starting point, not a final decision — this task re-verifies it with
current evidence and produces the actual go/no-go per candidate plugin.

**Deliverable:** plugin-boundary confirmation record, one disposition per candidate plugin.  
**Verification:** every `PHASE_9_EXTRACT_AS_NEW_PLUGIN`-disposed skill traces to an approved
plugin boundary, not an assumed one.  
**Evidence:** the confirmation record.

## Task 6 — Define the generic capability contract

Specify target-neutral inputs, outputs, errors, result statuses, permissions, dry-run behaviour, evidence, versioning, and safe defaults.

**Adversarial review:** challenge renamed project concepts, hidden environment assumptions, silent partial success, and speculative abstraction.

## Task 7 — Reconcile shared instructions and rules

Classify source `CLAUDE.md`, Copilot instructions, and applicable rule files. Produce proposed destination changes without wholesale copying.

**Verification:** CMAT and environment overlays remain in the source.  
**Evidence:** rule-classification report and reviewed diff.

## Task 8 — Decide the code and module boundary

Determine whether each reusable component remains plugin-local, uses an existing shared component, justifies a new shared component with multiple consumers, or remains source-project-specific.

**Symlink inventory (spec §8a):** 128 of the observed 272 source files are symlinks (spec §3a). Before extraction, inventory every symlink touching the selected pilot's skill directory, recording: link path, resolved source, artifact type, current owner, implementation status, genericity, runtime necessity, destination owner, and copy/refactor/replace decision. Do not reproduce the source symlink structure automatically — every retained symlink target must be physically copied and refactored into the destination plugin's own hub-and-spoke structure (this repository's `plugin-architecture-policy.md`/`symlink-cross-platform.md` rules), never linked back to the CMAT repository at runtime.

**Evidence:** module-boundary decision record and symlink-resolution matrix.

## Task 8a — Extract the shared foundation layer (NEW, 2026-08-07 — must precede Task 12)

CMAT's real implementation lives in a centralized `scripts/` tree, not in skill folders (spec §3c). Ten shared PowerShell helper modules underpin most extraction-eligible capabilities:

```text
scripts/lib/auth-helpers.ps1          scripts/lib/logging-helpers.ps1
scripts/lib/field-helpers.ps1         scripts/lib/list-helpers.ps1
scripts/lib/content-type-lib.ps1      scripts/lib/user-groups-lib.ps1
scripts/lib/xml-helpers.ps1           scripts/lib/guidmap-helpers.ps1
scripts/lib/migrate-helpers.ps1       scripts/lib/sp-extract-lib.ps1
```

**Why this is not speculative shared infrastructure:** spec §12 forbids creating a shared framework "for a single consumer." `scripts/lib/` has 9+ consuming skills *in the source today* — that is observed evidence of multi-consumer demand, which is exactly the bar §12 sets. Extracting skills individually without this layer forces either duplication (violating the zero-duplication rule in `plugin-architecture-policy.md` §2.1) or repeated re-scrubbing of the same helpers.

**Decide, per module:** does it belong in the consuming plugin's own `scripts/`, in an existing plugin (`workbench-setup` is the natural owner for auth/connection concerns — see Task 12's `-TestConnection` work), or in a justified shared location? Record the consumer count backing each decision.

**Genericity:** these modules are where tenant/auth assumptions concentrate — apply spec §9 rigorously and cross-check against §8h's literal-density scan.

**Placement:** plugin root `scripts/` with flat bare module names per CLAUDE.md, file-level symlinks into consuming skills via `symlink_manager.py` only (§9a).

**TDD:** these are critical runtime paths (auth boundaries, path resolution, file parsing) — per `.agent/rules/test-driven-development.md`, they must be tested with **real** subprocess/filesystem execution, not mocks.

**Deliverable:** foundation-layer extraction record with per-module destination, consumer count, and genericity evidence.
**Verification:** no consuming skill duplicates a helper; `symlink_manager.py diagnose` clean.

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

## Task 21 — Prioritize remaining plugin families and define the extraction waves

**Rewritten 2026-08-07.** The original instruction — "do not start a second extraction" — was written for a single-pilot Phase 9. The goal is now broad reusable coverage of all generic SharePoint capabilities. That does not license a bulk sweep; it changes the unit from *one pilot* to *reviewed waves*.

Rank remaining discovery, schema, page-modernization, link, provisioning, content-migration, and validation candidates using evidence from the pilot, then group them into waves:

```text
Wave 0  Shared foundation (Task 8a) — scripts/lib/, already complete before the pilot
Wave 1  The approved pilot family (Task 1 selection)
Wave 2  Merges into EXISTING plugins — no new plugin boundary needed
          (sp-uploading-content → sharepoint-content-publication;
           sp-validating-app-registration → workbench-setup)
Wave 3+ New-plugin candidates, one plugin per wave, in ranked order
```

**Wave gate — each wave requires, before the next begins:**
- all tests green, `isolated_install_check.py` passing for every plugin touched;
- `symlink_manager.py diagnose` clean; `audit_plugin_structure.py` clean;
- provenance recorded (spec §8b) for every extracted artifact;
- explicit human approval to proceed.

**Still prohibited:** starting a subsequent wave before the current one passes its gate; bulk-copying any capability without its three-axis classification; creating a new plugin whose boundary Task 5a has not confirmed. Per `self-evolution-policy.md` #6 (one logical fix per pass), waves are sequential, not parallel.

**Note on ordering:** Wave 2 merges into existing plugins are lower-risk than new-plugin creation and should generally precede Wave 3+, **except** where a capability's contract depends on an unmet upstream gate — `sp-uploading-content` writes into the library whose schema and source-of-truth lifecycle Phase 3 owns, and Phase 3's exit gate is not met (see the entry-gate note below).

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
