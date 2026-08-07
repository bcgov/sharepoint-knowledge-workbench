# Phase 9 Specification — Reusable SharePoint Plugin Extraction


> **Planning status:** `PLANNED`, `EVIDENCE_BASED`, `NOT_IMPLEMENTATION_AUTHORIZATION`, `SOURCE_BASELINE_REQUIRES_PINNING`. This is a forward-phase planning artifact derived from the accepted master initiative plan. It does not authorize implementation. Exact source and destination commits, candidate files, repository paths, commands, plugin boundaries, and test fixtures must be verified through Phase 9 reconnaissance before execution. Phase 9 has not started.

> **Source-architecture correction (2026-08-07) — READ BEFORE §8d/§8e.** A direct structural inspection of the pinned source tree found that **CMAT skills are thin shells, not implementation units**: every one of the 34 skills contains the same 3 real files (`SKILL.md`, `evals/evals.json`, `evals/results.tsv`) plus symlinks into a *centralized* `plugins/sharepoint-migration/scripts/` tree (183 files across 14 subdirectories) and `scripts/lib/` (10 shared PowerShell helper modules). §8d's per-skill symlink counts therefore measure **coupling to shared scripts**, not independently extractable implementation. This does not invalidate §8d/§8e's classification *framework* — it changes the **extraction unit**. See §3c (Source Architecture Correction), §8f (agent inventory — previously omitted entirely), §8g (symlink-resolution defects), and §8h (literal-density axis) below, all of which supersede the affected portions of §8d/§8e's supporting data while leaving their three-axis model and destination-matching rule intact.
>
> **Evidence-baseline update (2026-08-01):** A documentation-only reconciliation pass replaced hypothetical candidate descriptions with the actual observed source inventory at `/Users/richardfremmerlid/Projects/jag-csb-cmat-sharepoint-online/plugins/sharepoint-migration/skills/` — **119 directories, 272 files (144 real files + 128 symlinks)** across 33 skills (historical snapshot, dated 2026-08-01). This inventory is a **source baseline for future classification**, not an extraction authorization, and not a permanent total — the source repository continues to evolve independently. **A direct recount on 2026-08-03 found 34 skill directories — see §8d for the current, verified figure and complete per-skill mapping.** See §3a (Source Evidence Baseline) below for the 2026-08-01 historical snapshot. No code, plugin, or CMAT-repository artifact was touched by this reconciliation; see the companion completion report for the exact diff.

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

**Observed scale (historical, 2026-08-01):** 119 directories, 272 files (144 real files + 128 file-level symlinks) across 33 skills. These figures describe the supplied baseline inventory at the time of that reconciliation; they are **not permanent totals** — the source repository continues to change independently. **Superseded by a direct recount on 2026-08-03: 34 skill directories — see §8d.**

**Observed skill inventory (33 skills as of the 2026-08-01 historical snapshot, grouped by likely capability family — see §8d for the current 2026-08-03 recount of 34):**

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

**This spot-check is illustrative, not the required Stage 9.1/9.2 classification.** A complete implementation-status pass over all 34 skills (§8d) is required before any pilot selection, per §3b below. Do not treat the presence of `SKILL.md`, `evals.json`, or `results.tsv` as proof that a skill is implemented — the actual script/test/fixture count must be inspected per skill.

## 3c. Source Architecture Correction (2026-08-07) — the extraction unit is `scripts/`, not `skills/`

**Status:** `CONFIRMED` by direct inspection. This section supersedes any reading of §3a/§8d that treats a CMAT *skill directory* as a self-contained extractable unit.

### What the source actually looks like

```text
plugins/sharepoint-migration/
  skills/<34 skill dirs>/        ← thin shells: SKILL.md + evals/evals.json + evals/results.tsv
                                    + file symlinks pointing OUT to ../../../scripts/...
  scripts/                       ← THE REAL IMPLEMENTATION SURFACE (183 files, 14 subdirs)
    lib/                (10 files)  auth, logging, field, list, content-type,
                                    xml, guidmap, migrate, user-groups, sp-extract helpers
    page-migration/     (21 files)  ← 28 inbound symlinks from skills
    utilities/          (25 files)
    _deprecated/        (25 files)  ← 12 inbound symlinks from a live skill
    calendars/          (22 files)  ← CMAT-specific (court scheduling)
    tests/              (21 files)  ← 12 inbound symlinks
    app-reg-tests/      (15 files)
    waves/              (13 files)  ← CMAT-schema-coupled
    diagnostics/         (8 files)
    content-migration/   (7 files)
    upload/              (6 files)
    link-conversion/     (5 files)
    inventory/           (3 files)
    schema-audit/        (2 files)
  agents/                        ← 9 agent .md files — NOT classified anywhere in §8d (see §8f)
  config/config.psd1.example     ← single-file tenant config (see §9a for workbench alignment)
  assets/templates/
  references/
```

### Why this changes the plan

1. **Shared-script fan-in is high.** `scripts/page-migration` has 28 inbound symlinks, `scripts/waves` 12, `scripts/tests` 12, `scripts/lib` 9. Extracting skill-by-skill (Plan Task 12) repeatedly re-encounters the same underlying scripts.
2. **A shared library layer is genuinely justified.** §12 forbids creating shared infrastructure "for a single consumer." `scripts/lib/` has 9+ consumers *in the source* — that is evidence, not speculation. The prohibition does not apply; a foundation-layer extraction task is required and is added as Plan Task 8a.
3. **`SKILL.md` + `evals.json` + `results.tsv` is the universal baseline**, present in all 34 skills including every `PLANNED_WITH_NO_IMPLEMENTATION` one. §8d already warned not to treat these as proof of implementation; this section confirms empirically that they are exactly the 3-file floor.

### Corrected implementation signal

The reliable per-skill implementation signal is **resolved, non-broken, non-deprecated symlink targets plus any real script files beyond the 3-file baseline** — not raw file counts. Spot-corrections to §8d's figures found during this inspection:

| Skill | §8d says | Direct inspection | Note |
|---|---|---|---|
| `sp-converting-aspx-pages` | 12 scripts + 5 symlinks | **32 real files** + 5 symlinks | §8d **undercounted**; still the richest skill |
| `sp-validating-app-registration` | 7 symlinks | 7 real files + 7 symlinks | Richer than recorded |
| `sp-auditing-schema` | `IMPLEMENTED` (7 symlinks) | 7 symlinks, **≥1 broken** | See §8g |
| `sp-migrating-content` | `IMPLEMENTED` (44 symlinks) | 44 symlinks, **12 → `_deprecated/`, ≥3 broken** | See §8g |
| `sp-discovering-web-parts` | `IMPLEMENTED` (19 symlinks) | 19 symlinks, **6 escape the plugin** | See §8g |

**Instruction:** Plan Task 3's inventory must record, per skill, the resolved target of every symlink and whether that target is live/deprecated/broken/plugin-escaping — *before* Task 4 assigns any implementation status. §8d's statuses are provisional until that pass runs against the pinned commit.

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
| Semantic analysis of extracted content | `document-structure-analysis` |
| Building reusable structured knowledge | `structured-content-assembly` |
| Rendering human- or agent-facing representations | `structured-content-rendering` |
| Reconstructing classic SharePoint pages/web parts | `sharepoint-page-modernization` (new) |
| Inventorying sites, lists, permissions, web parts | `sharepoint-discovery` (new) |
| Capturing/comparing fields, content types, taxonomy | `sharepoint-schema` (new) |
| Publishing SharePoint objects | `sharepoint-provisioning` or the existing `sharepoint-content-publication` (currently `TRANSITIONAL_HOLDING_LOCATION`) |
| Validating source-target parity | `sharepoint-validation-and-reconciliation` (new) |

`structured-content-rendering` renders structured content into consumer representations; `sharepoint-page-modernization` reconstructs legacy SharePoint page *experiences and components*. These are not the same responsibility and must not be conflated.

## 4b. Long-Term Workbench Scope Intent

Phase 9's eventual outcome is intended to expand this repository from a knowledge-conversion workbench into a broader SharePoint engineering workbench — covering not only knowledge publication but also site migration, page conversion/analysis, and web-part analysis. This is a **stated future direction, not an authorization**: it informs why the plugin conventions established in Phase 4.5 must be general enough for both families, but it does not change Phase 9's `LATER` disposition or its entry gate.

## 5. Non-goals

- No source repository rename or migration.
- No deletion or relocation of source plugins, skills, agents, scripts, rules, or history.
- No cross-repository symlinks, runtime imports, or hidden source dependency.
- No ORDS API/auth/query/paging/retry framework extraction.
- No JUSTIN, CEIS, court-appearance, courthouse, calendar-routing, or CMAT business-rule extraction.
- No automatic migration of all 34 skills (§8d), **nine agents** (corrected 2026-08-07 from "seven" — direct count is 9, see §8f), the 183-file shared `scripts/` tree (§3c), source backlog, planned stubs, or historical scripts.
- No extraction of broken, deprecated-target, or plugin-escaping symlink targets (§8g).
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

## 8c. Phase 6 Overlap Findings (2026-08-03) — not Phase 9 execution

**Purpose:** prevent Phase 6 Task 0 from recreating capabilities already proven in the CMAT
repository (`/Users/richardfremmerlid/Projects/jag-csb-cmat-sharepoint-online`, plugin
`sharepoint-migration`), and record where Phase 6 should stay minimal pending Phase 9 extraction.
This section is a **finding record only** — it does not begin Phase 9 work, does not extract any
CMAT file, and does not modify CMAT.

**Scope surveyed:** `plugins/sharepoint-migration/` (34 skills — see §8d for the complete mapping; `scripts/{diagnostics,upload,
content-migration,page-migration,link-conversion,schema-audit,inventory,waves,...}`).
`plugins/ords-integration-migration/` is out of scope — court-scheduling ETL, disposition
`ORDS_SPECIFIC_OUT_OF_SCOPE`, no overlap with any Phase 6 skill.

**Disposition vocabulary for this section** (distinct from §8's three-axis model, used here for
direct Phase-6-skill-to-CMAT-capability comparison):

```text
PHASE_6_IMPLEMENT_NOW
PHASE_6_REUSE_EXISTING_WORKBENCH_CODE
PHASE_6_MINIMAL_INTERFACE_PENDING_PHASE_9
PHASE_9_EXTRACT_TO_EXISTING_PLUGIN
PHASE_9_CREATE_NEW_PLUGIN
PHASE_9_MERGE_WITH_EXISTING_SKILL
KEEP_CMAT_SPECIFIC
ORDS_SPECIFIC_OUT_OF_SCOPE
REQUIRES_HUMAN_DECISION
```

| Phase 6 skill/script | CMAT plugin/skill/script | Source path | Responsibility comparison | Maturity | Test evidence | Richer implementation | Disposition |
|---|---|---|---|---|---|---|---|
| `render-sharepoint-aspx` (structured-content-rendering, Task 0.16) | `sp-converting-aspx-pages` | `plugins/sharepoint-migration/skills/sp-converting-aspx-pages/` | CMAT: analyzes existing classic `.aspx` and produces modern-SPO *conversion* manifests/layout decisions/component mappings/previews. Phase 6: renders a structured-content package (never was SharePoint) into new `.aspx`-compatible artifacts — no source-page analysis step, different input entirely. Related but not identical: one converts existing pages, the other originates new ones. | CMAT: `status: active`, real implementation | CMAT has a populated `scripts/tests/` suite (wave/matrix tests); Phase 6 has none yet | CMAT (real conversion logic, page-layout decisions, preview generation) | `PHASE_6_MINIMAL_INTERFACE_PENDING_PHASE_9` — build the narrow origination-only renderer now (page-creation API output shape only); do not attempt page-analysis/conversion logic Phase 6 doesn't need. Full page-layout/component-mapping sophistication deferred to Phase 9 `PHASE_9_EXTRACT_TO_EXISTING_PLUGIN` (→ `structured-content-rendering`) if a future need for analyzing/converting *existing* SharePoint pages arises. |
| `publish-aspx-to-sharepoint` (sharepoint-content-publication, Task 0.15) | `sp-uploading-content`, `scripts/upload/upload-modern-page.ps1`, `upload-modern-page-rest.ps1` | `plugins/sharepoint-migration/skills/sp-uploading-content/`, `scripts/upload/` | Both use the `Add-PnPPage`/`Add-PnPPageTextPart`-equivalent modern-page creation approach. CMAT's is generalized across HTML/page/site-asset content and both PnP-PowerShell and raw-REST paths; Phase 6's is scoped to one structured-content package's rendered ASPX output only. | CMAT: `status: active`, two working upload mechanisms (PnP + REST) | CMAT: none of the `scripts/tests/` files target `upload/` specifically (gap in CMAT too, not just Phase 6) | CMAT (broader, dual-mechanism, already tenant-proven) | `PHASE_6_REUSE_EXISTING_WORKBENCH_CODE` for the page-creation call pattern (already independently confirmed working in this workbench's own Phase 3.0 §15 probe — do not re-derive from CMAT, use the workbench's own confirmed evidence); `PHASE_9_EXTRACT_TO_EXISTING_PLUGIN` (→ `sharepoint-content-publication`) for CMAT's richer dual-mechanism/generalized upload capability once genericized. |
| `inventory-and-validate-agentassets` (sharepoint-agents-and-skills, Task 0.4) | `sp-discovering-site-structure`, `sp-synthesizing-discovery` | `plugins/sharepoint-migration/skills/sp-discovering-site-structure/`, `sp-synthesizing-discovery/` | CMAT: full site-structure/list/library/field/view/content-type/permissions inventory across an entire site collection, feeding a 13-domain discovery meta-review. Phase 6: narrowly checks `AgentAssets` library/`Skills` folder existence and inventories `SKILL.md` files only — a tiny, single-purpose subset of CMAT's capability, different domain object (`AgentAssets`, a Copilot-specific library, vs. general site structure). | CMAT: `status: active`, deep | Phase 6's basis (`verify-agentassets-ready.ps1`) has no dedicated unit tests yet; CMAT's discovery skills have populated `scripts/tests/` | CMAT (far broader scope) | `PHASE_6_IMPLEMENT_NOW` — the two are not the same capability at the scope Phase 6 needs; do not adopt CMAT's general-purpose site-structure discovery for this narrow `AgentAssets`-only check. `REQUIRES_HUMAN_DECISION` on whether a future, broader "SharePoint site inventory" capability belongs in `sharepoint-agents-and-skills` at all, or is purely a Phase 9 `sp-discovering-*` extraction target with no Phase 6 counterpart. |
| `setup-sharepoint-connection`, `validate-workbench-environment` (workbench-setup, Task 0.17) | `sp-validating-app-registration`, `scripts/diagnostics/test-spo-auth.ps1`, `test-csb-intranet-connections.ps1` | `plugins/sharepoint-migration/skills/sp-validating-app-registration/`, `scripts/diagnostics/` | CMAT: validates Entra ID app registrations (delegated + app-only) against a live tenant, confirms auth succeeds and permission boundaries are enforced — real tenant-write-adjacent validation. Phase 6: `setup-sharepoint-connection` never connects by default (explicit opt-in `-TestConnection` only); `validate-workbench-environment` validates local config/profile *files*, not live tenant auth. Different point in the lifecycle — CMAT validates an existing tenant identity, Phase 6 validates local setup before any connection is attempted. | CMAT: `status: active`, real | CMAT: `app-reg-tests/test-etl-app-registration.ps1` exists (ORDS-side, not directly this skill's own test); Phase 6 skills not yet built | CMAT (proven against real tenant) | `PHASE_6_IMPLEMENT_NOW` for the two narrow, non-overlapping Phase 6 skills as designed. `PHASE_9_MERGE_WITH_EXISTING_SKILL` — once `setup-sharepoint-connection`'s optional `-TestConnection` path is built, its live-validation logic should reuse `sp-validating-app-registration`'s proven approach rather than re-deriving auth-validation from scratch; extract into `workbench-setup` (or symlink-share, per this repo's hub-and-spoke rule) at that time. |
| `publish-markdown-to-sharepoint` (sharepoint-content-publication, Task 0.15) | `sp-migrating-content`, `scripts/content-migration/`, `scripts/upload/migrate-site-assets.ps1` | `plugins/sharepoint-migration/skills/sp-migrating-content/`, `scripts/content-migration/` | CMAT: runs a 10-wave (`wave0a`–`wave9`) full-schema provisioning + content migration pipeline with TDD RED→GREEN gates, clean-slate wipe, choices extraction. Phase 6: uploads one document's rendered Markdown + navigation + media to one target library/folder — a single-document operation, not a schema-provisioning pipeline. | CMAT: `status: active`, extremely deep (10 waves, dedicated test suite per wave: `test-wave0a.ps1` through `test-wave9.ps1`) | CMAT: `scripts/tests/test-wave{0a..9}.ps1`, `test-all.ps1` — real, populated | CMAT (dramatically richer — full migration pipeline vs. single-document upload) | `PHASE_6_IMPLEMENT_NOW` — scale mismatch is intentional; Phase 6 does not need wave-based schema migration. `KEEP_CMAT_SPECIFIC` for the wave pipeline itself (deeply CMAT-schema-coupled); `PHASE_9_EXTRACT_TO_EXISTING_PLUGIN` only for the underlying single-item upload primitive (`migrate-site-assets.ps1`-style), if genericized, → `sharepoint-content-publication`. |
| `reconcile-sharepoint-publication`, `validate-sharepoint-publication` (sharepoint-content-publication, Task 0.15) | `sp-validating-link-integrity`, `sp-generating-migration-reports`, `sp-validating-content` (planned) | `plugins/sharepoint-migration/skills/sp-validating-link-integrity/`, `sp-generating-migration-reports/` | CMAT: `sp-validating-link-integrity` verifies converted links resolve post-migration (active); `sp-generating-migration-reports` produces executive/strategic/technical reports (active); `sp-validating-content` (item-count/field-value/attachment-integrity parity check) is `status: planned`, **no backing script exists** in CMAT either. Phase 6's `reconcile-sharepoint-publication`/`validate-sharepoint-publication` target a narrower, single-document publication-map reconciliation. | CMAT: 2 of 3 relevant skills active, 1 planned/unbuilt | CMAT: link-integrity has real evidence; content-validation does not (same gap as Phase 6) | CMAT (for link integrity and reporting specifically); **neither** repo has a mature content-parity validator | `PHASE_6_IMPLEMENT_NOW` for the two Phase 6 skills as scoped (package-only, matches existing zero-tenant-I/O `sharepoint_reconcile.py`/`sharepoint_dry_run.py` basis). `PHASE_9_EXTRACT_TO_EXISTING_PLUGIN` (→ `sharepoint-content-publication`) for CMAT's link-integrity-validation technique specifically, once genericized. The content-parity-validation gap (`sp-validating-content`) is real in both repos — `REQUIRES_HUMAN_DECISION` on whether either project builds it first. |
| `rollback-sharepoint-publication` (sharepoint-content-publication, Task 0.15) | none found | — | **No CMAT skill or script matches this responsibility.** Surveyed `scripts/calendars/clean-all-calendars.ps1`, `scripts/utilities/reset-and-recreate-appearance-schema.ps1`, `scripts/utilities/audit-spo-duplicates.ps1` — all are CMAT-schema-specific reset/cleanup utilities (calendar events, appearance lists), not a general exact-target publication rollback with a confirm-string safety gate. | n/a — no CMAT equivalent | n/a | n/a — genuinely missing in both repos | `PHASE_6_IMPLEMENT_NOW` — this is real new-build work, not duplicative of anything in CMAT. No Phase 9 action implied; nothing to extract. |
| Rendering-template creation (`create-markdown-rendering-template`, `create-aspx-rendering-template`, structured-content-rendering, Task 0.16) | `sp-converting-aspx-pages`'s layout-decision/component-mapping output, `sp-remediating-page-layouts` (planned), `sp-remediating-web-parts` (planned) | `plugins/sharepoint-migration/skills/sp-converting-aspx-pages/`, `sp-remediating-page-layouts/`, `sp-remediating-web-parts/` | CMAT's page-layout-rules/web-part-mapping-matrix concept (`layout-rules.json` LR-001–LR-004, referenced by `sp-remediating-page-layouts`) is the closest analog to a rendering-template schema, but **`sp-remediating-page-layouts` and `sp-remediating-web-parts` are both `status: planned` — no backing script exists in CMAT either.** Only `sp-converting-aspx-pages` (active) actually produces layout decisions/previews, as a byproduct of page conversion, not as a standalone reusable template system. | CMAT: 1 of 3 relevant capabilities active, 2 planned/unbuilt | CMAT: none specific to template/layout-rule validation | Neither repo has a mature, standalone rendering-template system | `PHASE_6_IMPLEMENT_NOW` — build Phase 6's narrow template-validation scope (schema/placeholder/section/asset/profile checks) fresh; CMAT has no reusable template system to draw from, only conversion-time layout decisions embedded in one active skill. `PHASE_9_EXTRACT_TO_EXISTING_PLUGIN` (→ `structured-content-rendering`) only if CMAT's `layout-rules.json` concept is later formalized into its own reusable schema — not proven mature enough to extract now. |

**Explicit non-duplication instruction followed:** no CMAT file was migrated, copied, or referenced
as executable source during Phase 6 Task 0. Every `PHASE_6_IMPLEMENT_NOW`/`PHASE_6_MINIMAL_
INTERFACE_PENDING_PHASE_9` row above scopes Phase 6's build to its own narrow, already-specified
requirements — none of them were widened or narrowed based on what CMAT happens to already have.

### Phase 9 destination-plugin-matching rule (added 2026-08-03)

Before any future Phase 9 extraction creates a new plugin, it must first be matched against the
**current** destination plugin inventory: `source-document-extraction`, `document-structure-
analysis`, `structured-content-assembly`, `structured-content-rendering`, `sharepoint-content-
publication`, `sharepoint-agents-and-skills`, `workbench-setup`. If an existing plugin already owns
the responsibility, Phase 9 adds or merges a skill there (`PHASE_9_EXTRACT_TO_EXISTING_PLUGIN` /
`PHASE_9_MERGE_WITH_EXISTING_SKILL`) rather than automatically creating another plugin
(`PHASE_9_CREATE_NEW_PLUGIN`). A new Phase 9 plugin is justified only when the capability has: a
distinct domain; independent user journeys; independent installation value; its own lifecycle/
versioning; and no suitable existing owner. Every candidate row in the §8c table has been checked
against this rule for the Phase-6-overlap subset only — **no new Phase 9 plugin is justified by
the Phase 6 overlap subset alone. The broader CMAT inventory still contains distinct SharePoint
engineering domains that require Phase 9 destination classification** — see §8d below for the
complete 34-skill mapping and §8e for the full destination-architecture evaluation, including 7
provisional Phase 9 plugin candidates not yet approved.

## 8d. Complete CMAT skill mapping (2026-08-03) — all 34 `sharepoint-migration` skills

> **Amended 2026-08-07 — supporting data is provisional, framework stands.** The three-axis model, destination-plugin-matching rule, and per-skill destination assignments in this section remain the working basis for Phase 9. However, the **implementation-status column is provisional** pending the symlink-resolution pass required by §3c and §8g: symlink counts here include broken links (4 confirmed), links into `scripts/_deprecated/` (12), and links escaping the plugin into project-analysis data (6). Skills whose status materially depends on those links — `sp-auditing-schema`, `sp-migrating-content`, `sp-discovering-web-parts` — must be re-verified against the pinned commit before any extraction decision relies on them. Skill directories are also **thin shells**, not implementation units (§3c) — this table's rows describe *capabilities*, and the code implementing them lives in the shared `scripts/` tree. Agents are not covered here at all; see §8f.

**Directly audited** (not inferred from filenames): `ls plugins/sharepoint-migration/skills/*/`
returns **34 skill directories**, not 31 — the 31 figure named in the audit request undercounted;
corrected here to the actual count. Per instruction, `SKILL.md` frontmatter's `status:` field,
`evals.json`, and `results.tsv` are **not** treated as proof of implementation — each row's
"backing evidence" column reflects actual files found (regular script files or real, verified
symlinks into the skill folder), not the claimed status.

Every row's source is the CMAT repository (`/Users/richardfremmerlid/Projects/jag-csb-cmat-
sharepoint-online`, `plugins/sharepoint-migration/skills/<name>/`) — no row in this table has any
other source. **Implementation-status category is strictly one of three, mutually exclusive, and
sums to exactly 34** (genericity/CMAT-specificity and cross-skill scope questions are separate
axes recorded in their own columns, not folded into the status count):

- `IMPLEMENTED` — real script files or real, verified symlinks found in the skill folder (21 skills).
- `UNVERIFIED_ACTIVE_CLAIM` — `SKILL.md` claims `status: active`, zero script files and zero symlinks found; the claim itself is unconfirmed, not treated as implemented (2 skills).
- `PLANNED_WITH_NO_IMPLEMENTATION` — `SKILL.md` claims `status: planned`, zero backing found — confirms the claim (11 skills).

| Skill | Implementation status | Generic vs. CMAT-specific | Destination plugin | Destination skill name | Extraction disposition | Phase 9 task | Deliverable | Tests | Acceptance criteria | Overlap with Phase 6 |
|---|---|---|---|---|---|---|---|---|---|---|
| `sp-discovering-site-structure` | `IMPLEMENTED` (3 symlinks) | generic | `sharepoint-discovery` (candidate) | `discover-site-structure` | `PHASE_9_EXTRACT_AS_NEW_PLUGIN` | Task 3 (inventory) → Task 12 (extract) | extracted skill + scripts under `sharepoint-discovery` | Task 9 contract/safety tests + Task 16 parity | passes genericity contract (§9); parity vs. CMAT source behavior proven | none (Phase 6's `inventory-and-validate-agentassets` is `AgentAssets`-only, narrower) |
| `sp-discovering-lists` | `PLANNED_WITH_NO_IMPLEMENTATION` | n/a | `sharepoint-discovery` | — | `PLANNED_WITH_NO_IMPLEMENTATION` | none — no CMAT implementation to extract | n/a — gap, not a future guaranteed skill | n/a | CMAT skill must be built first, or this row is dropped from the eventual plugin | none |
| `sp-discovering-content-types` | `PLANNED_WITH_NO_IMPLEMENTATION` | n/a | `sharepoint-discovery` | — | `PLANNED_WITH_NO_IMPLEMENTATION` | none | n/a — gap | n/a | same as above | none |
| `sp-discovering-pages` | `IMPLEMENTED` (3 symlinks) | generic | `sharepoint-discovery` | `discover-pages` | `PHASE_9_EXTRACT_AS_NEW_PLUGIN` | Task 3 → Task 12 | extracted skill + scripts | Task 9 + Task 16 | genericity + parity proven | none |
| `sp-discovering-web-parts` | `IMPLEMENTED` (19 symlinks, richest discovery skill) | generic concept; CMAT's mapping-matrix content needs genericity review | `sharepoint-discovery` | `discover-web-parts` | `PHASE_9_EXTRACT_AS_NEW_PLUGIN` | Task 3 → Task 6 (contract) → Task 12 | extracted skill + genericized mapping matrix | Task 9 + Task 16 | CMAT-specific mapping entries removed/parameterized before parity proof | none |
| `sp-discovering-navigation` | `IMPLEMENTED` (2 symlinks) | generic | `sharepoint-discovery` | `discover-navigation` | `PHASE_9_EXTRACT_AS_NEW_PLUGIN` | Task 3 → Task 12 | extracted skill | Task 9 + Task 16 | genericity + parity proven | none |
| `sp-discovering-forms` | `IMPLEMENTED` (2 symlinks) | generic | `sharepoint-discovery` | `discover-forms` | `PHASE_9_EXTRACT_AS_NEW_PLUGIN` | Task 3 → Task 12 | extracted skill | Task 9 + Task 16 | genericity + parity proven | none |
| `sp-discovering-permissions` | `IMPLEMENTED` (1 symlink, thin) | generic | `sharepoint-discovery` | `discover-permissions` | `PHASE_9_EXTRACT_AS_NEW_PLUGIN` | Task 3 → Task 12 | extracted skill | Task 9 + Task 16 | verify real depth beyond 1 symlink before parity claim | none |
| `sp-discovering-workflows` | `PLANNED_WITH_NO_IMPLEMENTATION` | n/a | `sharepoint-discovery` | — | `PLANNED_WITH_NO_IMPLEMENTATION` | none | n/a — gap | n/a | build first, or drop | none |
| `sp-synthesizing-discovery` | `IMPLEMENTED` (1 symlink, thin) | generic (13-domain meta-review) | `sharepoint-discovery` | `synthesize-discovery-report` | `PHASE_9_EXTRACT_AS_NEW_PLUGIN` | Task 3 → Task 12 | extracted skill | Task 9 + Task 16 | genericity + parity proven | conceptual only, vs. `inventory-and-validate-agentassets`'s reporting shape |
| `sp-auditing-schema` | `IMPLEMENTED` (7 symlinks) | generic | `sharepoint-schema` (candidate) | `audit-schema` | `PHASE_9_EXTRACT_AS_NEW_PLUGIN` | Task 3 → Task 12 | extracted skill | Task 9 + Task 16 | genericity + parity proven | none |
| `sp-extracting-choices` | `IMPLEMENTED` (1 symlink, thin) | generic | `sharepoint-schema` | `extract-choice-fields` | `PHASE_9_EXTRACT_AS_NEW_PLUGIN` | Task 3 → Task 12 | extracted skill | Task 9 + Task 16 | verify depth beyond 1 symlink | none |
| `sp-mapping-content-types` | `PLANNED_WITH_NO_IMPLEMENTATION` | n/a | `sharepoint-schema` | — | `PLANNED_WITH_NO_IMPLEMENTATION` | none | n/a — gap | n/a | build first, or drop | none |
| `sp-mapping-lists` | `PLANNED_WITH_NO_IMPLEMENTATION` | n/a | `sharepoint-schema` | — | `PLANNED_WITH_NO_IMPLEMENTATION` | none | n/a — gap | n/a | build first, or drop | none |
| `sp-mapping-taxonomy` | `PLANNED_WITH_NO_IMPLEMENTATION` | n/a | `sharepoint-schema` | — | `PLANNED_WITH_NO_IMPLEMENTATION` | none | n/a — gap | n/a | build first, or drop | none |
| `sp-synthesizing-deployment-matrix` | `UNVERIFIED_ACTIVE_CLAIM` (0 symlinks, 0 scripts) | unverified | `sharepoint-provisioning` (candidate, not currently justified) | — | `REQUIRES_HUMAN_DECISION` | Task 3 re-verification before any Task 4 classification | n/a until verified | n/a | direct script inspection in CMAT repo to confirm or correct the `active` claim | none |
| `sp-provisioning-modern-calendars` | `IMPLEMENTED` (4 symlinks) | CMAT-specific (calendar/court-scheduling concept) | n/a | n/a | `KEEP_CMAT_SPECIFIC` | none — not extraction-eligible | n/a | n/a | n/a | none |
| `sp-analysing-aspx-pages` | `IMPLEMENTED` (5 symlinks) | generic (classic-page analysis) | `sharepoint-page-modernization` (candidate) | `analyze-aspx-pages` | `PHASE_9_EXTRACT_AS_NEW_PLUGIN` | Task 3 → Task 12 | extracted skill | Task 9 + Task 16 | genericity + parity proven | feeds `render-sharepoint-aspx`'s analysis gap (§8c) |
| `sp-converting-aspx-pages` | `IMPLEMENTED` (12 scripts + 5 symlinks, richest in repo) | generic (conversion manifest/layout/component-mapping) | `sharepoint-page-modernization` | `convert-aspx-pages` | `PHASE_9_EXTRACT_AS_NEW_PLUGIN` | Task 1 (pilot-family candidate) → Task 3 → Task 6 → Task 12 | extracted skill, highest-value single extraction in the whole repo | Task 9 + Task 16 + Task 17 (adversarial) | genericity + parity + adversarial evaluation proven | directly overlaps `render-sharepoint-aspx` — Phase 6 stays `PHASE_6_MINIMAL_INTERFACE_PENDING_PHASE_9` (§8c) |
| `sp-converting-wiki-pages` | `IMPLEMENTED` (2 symlinks) | generic | `sharepoint-page-modernization` | `convert-wiki-pages` | `PHASE_9_EXTRACT_AS_NEW_PLUGIN` | Task 3 → Task 12 | extracted skill | Task 9 + Task 16 | genericity + parity proven | none |
| `sp-remediating-page-layouts` | `PLANNED_WITH_NO_IMPLEMENTATION` | n/a | `sharepoint-page-modernization` | — | `PLANNED_WITH_NO_IMPLEMENTATION` | none | n/a — gap | n/a | build first, or drop | closest analog to Task 0.16's rendering-template creation, itself also unbuilt in Phase 6 |
| `sp-remediating-web-parts` | `PLANNED_WITH_NO_IMPLEMENTATION` | n/a | `sharepoint-page-modernization` | — | `PLANNED_WITH_NO_IMPLEMENTATION` | none | n/a — gap | n/a | build first, or drop | none |
| `sp-extracting-links` | `IMPLEMENTED` (5 symlinks) | generic | `sharepoint-link-remediation` (candidate) | `extract-links` | `PHASE_9_EXTRACT_AS_NEW_PLUGIN` | Task 3 → Task 12 | extracted skill | Task 9 + Task 16 | genericity + parity proven | none |
| `sp-remediating-links` | `IMPLEMENTED` (3 symlinks) | generic (regex URL-rewrite) | `sharepoint-link-remediation` | `remediate-links` | `PHASE_9_EXTRACT_AS_NEW_PLUGIN` | Task 3 → Task 12 | extracted skill | Task 9 + Task 16 | genericity + parity proven | none |
| `sp-remediating-document-content-links` | `PLANNED_WITH_NO_IMPLEMENTATION` | n/a | `sharepoint-link-remediation` | — | `PLANNED_WITH_NO_IMPLEMENTATION` | none | n/a — gap | n/a | build first, or drop | none |
| `sp-validating-link-integrity` | `IMPLEMENTED` (1 symlink, thin) | generic | `sharepoint-link-remediation` | `validate-link-integrity` | `PHASE_9_EXTRACT_AS_NEW_PLUGIN` | Task 3 → Task 12 | extracted skill | Task 9 + Task 16 | verify depth beyond 1 symlink | candidate technique for `reconcile-/validate-sharepoint-publication` (§8c) |
| `sp-content-migration` | `IMPLEMENTED` (6 symlinks + 1 reference doc) | mixed — scope vs. `sp-migrating-content` unresolved | `sharepoint-content-migration` (candidate) | `migrate-content` (or merged into `sp-migrating-content`'s extraction) | `REQUIRES_HUMAN_DECISION` | Task 4b (overlap analysis) before Task 12 | n/a until scope resolved | n/a | direct script-content comparison against `sp-migrating-content` before assigning final disposition | overlaps `publish-markdown-to-sharepoint` at the single-item-upload level (§8c) |
| `sp-migrating-content` | `IMPLEMENTED` (44 symlinks, richest skill in repo by link count) | mixed — wave-execution mechanism may generalize, wave *content* is CMAT-schema-coupled | `sharepoint-content-migration` | `run-migration-waves` (mechanism only) | `PHASE_9_EXTRACT_AS_NEW_PLUGIN` (mechanism) + `KEEP_CMAT_SPECIFIC` (wave content) | Task 1 (pilot-family candidate) → Task 6 (contract, separate mechanism from content) → Task 12 | extracted mechanism skill, wave content stays in CMAT | Task 9 + Task 16 + Task 17 | mechanism/content separation proven, not just claimed | explicitly compared in §8c — scale mismatch intentional, Phase 6 does not need this |
| `sp-running-sharegate-jobs` | `IMPLEMENTED` (3 symlinks) | generic if Sharegate is an assumed available tool; record as external dependency otherwise | `sharepoint-content-migration` | `run-sharegate-jobs` | `PHASE_9_EXTRACT_AS_NEW_PLUGIN` | Task 3 → Task 5 (coupling matrix, confirm Sharegate licensing assumption) → Task 12 | extracted skill | Task 9 + Task 16 | Sharegate dependency documented, not silently assumed | none |
| `sp-uploading-content` | `IMPLEMENTED` (4 symlinks) | generic (PnP + REST modern-page/asset upload) | **`sharepoint-content-publication` (existing plugin)** | `upload-content` | `PHASE_9_EXTRACT_TO_EXISTING_PLUGIN` | Task 4a (destination classification) → Task 12 (extract into existing plugin, not a new one) | new skill inside the existing `sharepoint-content-publication` plugin | Task 9 + Task 16 | merges cleanly with `publish-aspx-to-sharepoint`'s already-confirmed page-creation approach | directly named in §8c |
| `sp-validating-content` | `PLANNED_WITH_NO_IMPLEMENTATION` | n/a | `sharepoint-validation-and-reconciliation` (candidate, not currently justified) | — | `PLANNED_WITH_NO_IMPLEMENTATION` | none | n/a — gap | n/a | neither repo has a mature content-parity validator — build first, or drop | directly named in §8c |
| `sp-validating-permissions` | `PLANNED_WITH_NO_IMPLEMENTATION` | n/a | `sharepoint-validation-and-reconciliation` | — | `PLANNED_WITH_NO_IMPLEMENTATION` | none | n/a — gap | n/a | build first, or drop | none |
| `sp-validating-app-registration` | `IMPLEMENTED` (7 symlinks) | generic (Entra ID app-registration validation) | **`workbench-setup` (existing plugin)** | `validate-app-registration` | `PHASE_9_MERGE_WITH_EXISTING_SKILL` | Task 4a → Task 12 (merge into existing plugin, not a new one) | new skill inside the existing `workbench-setup` plugin | Task 9 + Task 16 | reused by `setup-sharepoint-connection`'s optional `-TestConnection` path | directly named in §8c |
| `sp-generating-migration-reports` | `UNVERIFIED_ACTIVE_CLAIM` (0 symlinks, 0 scripts) | unverified | `sharepoint-validation-and-reconciliation` | — | `REQUIRES_HUMAN_DECISION` | Task 3 re-verification before any Task 4 classification | n/a until verified | n/a | direct script inspection in CMAT repo to confirm or correct the `active` claim | none |

**ORDS boundary (unchanged, re-confirmed):** `plugins/ords-integration-migration/` is entirely
outside this table — `ORDS_SPECIFIC_OUT_OF_SCOPE` by default for its whole scope (ORDS queries,
JUSTIN/CEIS matching, courthouse routing, monitored-person logic, appearance cleanup, CMAT
calendars, CMAT retention rules). Only a generic SharePoint helper found inside it would ever be
extraction-eligible, and none was identified in this audit.

**Tally — mutually exclusive, sums to exactly 34, computed directly from the table above:**

| Implementation status | Count |
|---|---|
| `IMPLEMENTED` | 21 |
| `UNVERIFIED_ACTIVE_CLAIM` | 2 (`sp-synthesizing-deployment-matrix`, `sp-generating-migration-reports`) |
| `PLANNED_WITH_NO_IMPLEMENTATION` | 11 |
| **Total** | **34** |

`KEEP_CMAT_SPECIFIC` (`sp-provisioning-modern-calendars`) and the `sp-content-migration`/
`sp-migrating-content` scope-overlap flag are recorded in the **genericity** and **extraction-
disposition** columns respectively — separate axes from implementation status, not additional
tally buckets. No skill is counted twice.

## 8e. Destination architecture — existing plugins vs. Phase 9 candidate plugins (2026-08-03)

**Existing workbench plugins** (use when responsibility already fits — no new plugin needed):
`workbench-setup`, `structured-content-rendering`, `sharepoint-content-publication`,
`sharepoint-agents-and-skills`, `source-document-extraction`, `document-structure-analysis`,
`structured-content-assembly`. Per §8d, `sp-validating-app-registration` and `sp-uploading-content`
already map here (`PHASE_9_MERGE_WITH_EXISTING_SKILL` / `PHASE_9_EXTRACT_TO_EXISTING_PLUGIN`).

**Candidate new Phase 9 plugins** (provisional — none approved yet; a new plugin is justified only
when the audited capabilities demonstrate distinct user intent, cohesive responsibility,
independent installation value, real implemented skills/scripts, independent testing,
lifecycle/versioning rationale, and no suitable existing owner):

| Candidate plugin | Skills mapped (§8d) | Implemented | Planned-empty | Unverified | Justification status |
|---|---|---|---|---|---|
| `sharepoint-discovery` | 10 | 7 | 3 | 0 | Real implemented core (7 skills, up to 19 symlinks on the richest). Cohesive "inventory an existing site" user intent, distinct from all existing workbench plugins. **Provisionally justified**, pending genericity review of `sp-discovering-web-parts`'s mapping-matrix content. |
| `sharepoint-schema` | 5 | 2 | 3 | 0 | Only 2 of 5 implemented, both thin (1 symlink each for the richer one, `sp-auditing-schema` has 7 — actually the stronger of the two). Real but narrow. **Provisionally justified** on `sp-auditing-schema` alone; the other 4 are speculative until built. |
| `sharepoint-provisioning` | 2 | 0 confirmed | 0 | 2 | **Not justified as a standalone plugin** — both mapped skills are unverified (`REQUIRES_HUMAN_DECISION`) or CMAT-specific (`KEEP_CMAT_SPECIFIC`). No confirmed generic implemented skill exists here at all. Re-evaluate after §8d's two `REQUIRES_HUMAN_DECISION` items are resolved by direct CMAT inspection. |
| `sharepoint-page-modernization` | 5 | 3 | 2 | 0 | Contains the single richest implementation in the entire CMAT audit (`sp-converting-aspx-pages`, 12 scripts + 5 symlinks). Distinct domain from `structured-content-rendering` per the user's own boundary (reconstructs legacy pages vs. renders new content from structured workbench data). **Justified**, and the strongest single Phase 9 pilot candidate. |
| `sharepoint-link-remediation` | 4 | 3 | 1 | 0 | Real, cohesive, distinct "fix broken links post-migration" user intent. **Provisionally justified.** |
| `sharepoint-content-migration` | 4 | 3 confirmed + 1 unclear | 0 | 1 | Contains `sp-migrating-content`, the richest single skill by symlink count (44) — but genericity is the hardest open question here (separating the reusable wave-execution mechanism from CMAT's specific wave content). `sp-uploading-content` is reassigned to `sharepoint-content-publication` instead (existing plugin preferred). **Provisionally justified** on `sp-migrating-content`'s mechanism alone, contingent on genericity review; `sp-content-migration` vs. `sp-migrating-content` overlap must be resolved first. |
| `sharepoint-validation-and-reconciliation` | 4 | 1 confirmed + 1 reassigned | 2 | 1 | Only 1 skill has real backing (`sp-validating-app-registration`), and that one is being reassigned to `workbench-setup` (existing plugin preferred per the destination-matching rule). **Not currently justified as a standalone plugin** — after reassignment, only 2 planned-empty skills and 1 unverified skill remain, no real implemented core. Re-evaluate if `sp-validating-content`/`sp-validating-permissions` are ever built. |

**No reporting-plugin created automatically**, per instruction — discovery reports stay owned by
`sharepoint-discovery`, modernization reports by `sharepoint-page-modernization`, migration
reports by `sharepoint-content-migration`, validation evidence by `sharepoint-validation-and-
reconciliation` (if it ever becomes justified), provisioning evidence by `sharepoint-provisioning`
(if it ever becomes justified).

**Bottom line:** of the 7 candidate plugins, **5 are provisionally justified by real implemented
evidence** (`sharepoint-discovery`, `sharepoint-schema`, `sharepoint-page-modernization`,
`sharepoint-link-remediation`, `sharepoint-content-migration`), **2 are not currently justified as
standalone plugins** (`sharepoint-provisioning`, `sharepoint-validation-and-reconciliation`)
pending further evidence or reassignment to existing plugins. None of this authorizes Phase 9
execution — these are classification findings only.

## 8f. Agent inventory (2026-08-07) — previously omitted from all classification

**Gap acknowledged:** §8d classifies skills only. `plugins/sharepoint-migration/agents/` contains **9 agent definition files** plus an `agents/references/` directory, none of which appear in any classification table. §5's non-goals mention "seven agents" in passing — that count is **stale and wrong** (9, not 7) and a non-goal is not a classification.

```text
sp-discovery-agent.md
sp-schema-agent.md
sp-modernization-agent.md
sp-link-agent.md
sp-migration-agent.md
sp-validation-agent.md
sp-deployment-planner.md
sp-migration-orchestrator.md
sp-wave-orchestrator.md
```

**Required:** every agent receives the same three-axis classification as skills (§3b), plus an **orchestration-coupling** judgment specific to agents:

```text
GENERIC_SHAREPOINT_AGENT          — reusable, no project coupling
AGENT_REQUIRES_GENERICIZING       — reusable shape, project literals inside
ORCHESTRATOR_COUPLED_TO_CMAT_WAVES — depends on CMAT's specific wave/schema model
PROJECT_SPECIFIC_AGENT            — not extraction-eligible
```

**Known signal:** `sp-wave-orchestrator.md` contains 33 project-literal hits (§8h) and orchestrates CMAT's wave model — provisionally `ORCHESTRATOR_COUPLED_TO_CMAT_WAVES`. The per-domain agents (`sp-discovery-agent`, `sp-schema-agent`, `sp-link-agent`, `sp-modernization-agent`) are the more plausible generic candidates, but none has been inspected in detail yet.

**Destination consideration:** this repository already owns `plugins/sharepoint-agents-and-skills/`. Per the §8c destination-plugin-matching rule, extracted agents must be matched against that existing plugin **before** any new agent-hosting plugin is contemplated.

## 8g. Symlink-resolution defects in the source (2026-08-07)

Direct inspection found three defect classes that §8d's "real, verified symlinks" methodology did not detect. **All three affect skills §8d currently marks `IMPLEMENTED`, and two of them weaken §8e's plugin justifications.**

### Class 1 — Broken symlinks (4 confirmed)

```text
skills/sp-auditing-schema/scripts/compare-live-schema-test-vs-spo.ps1   → dangling
skills/sp-migrating-content/scripts/waves/wave4-pio-cases.ps1           → dangling
skills/sp-migrating-content/scripts/waves/wave5-icm-cases.ps1           → dangling
skills/sp-migrating-content/scripts/waves/wave6-itau-cases.ps1          → dangling
```

`sp-auditing-schema` is the skill §8e leans on to justify the entire `sharepoint-schema` candidate plugin ("**Provisionally justified** on `sp-auditing-schema` alone"). At least one of its script links resolves to nothing. **That justification must be re-derived from what actually resolves.**

### Class 2 — Deprecated code symlinked into a live skill (12 links)

`skills/sp-migrating-content/` symlinks 12 files from `scripts/_deprecated/stages/`. §8d calls this skill "richest skill in repo by symlink count (44)" and §8e provisionally justifies `sharepoint-content-migration` on its wave-execution *mechanism*. A material share of that 44 is deprecated and/or broken. **The mechanism-vs-content split §8d proposes is still the right idea, but the mechanism must be identified from live, non-deprecated code — the current evidence does not establish that such a mechanism exists outside `_deprecated/`.**

### Class 3 — Symlinks escaping the plugin boundary (6 links)

```text
skills/sp-discovering-web-parts/references/*  →  ../../../../../01_source_sharepoint/analysis
```

These traverse five levels up, out of `plugins/` entirely, into a repository-root project-analysis data directory. §8a's symlink-inventory requirement implicitly assumes links resolve *within* the plugin; this class was unanticipated. These are **project analysis data, not generic code** — 6 of the 19 links that make `sp-discovering-web-parts` "the richest discovery skill" and anchor `sharepoint-discovery`'s justification in §8e.

### Required handling

- Plan Task 3's inventory must classify every symlink as `LIVE` / `BROKEN` / `DEPRECATED_TARGET` / `ESCAPES_PLUGIN` / `PROJECT_DATA`.
- **Broken links are never extracted** — they are recorded as source defects and reported, not copied. Do not "fix" them in CMAT (§17 forbids source modification).
- **Deprecated targets are never extracted** without an explicit human decision recorded per link.
- **Plugin-escaping links to project data are never extracted** — they fail the genericity contract (§9) by definition.
- Every discarded link is recorded in the disposition matrix with a reason. Silent omission is prohibited.

## 8h. Literal-density axis (2026-08-07) — extraction cost is not the same as write risk

A repository-wide scan for project literals (`JUSTIN`, `CEIS`, `ORDS`, `courthouse`, `appearance`, `AG-CSB*`, `ITAU`, `PIO`, `ICM`) across `scripts/`, `agents/`, and `config/` found **57 files requiring genericity scrubbing**. Density is highly uneven and — critically — **inversely correlated with the "safe pilot" assumption in §7**.

| File | Literal hits | Relevance |
|---|---|---|
| `scripts/inventory/export-sharepoint-inventory-custom.ps1` | 178 | Backs `sp-discovering-site-structure` |
| `scripts/inventory/export-sharepoint-inventory.ps1` | 147 | Backs `sp-discovering-site-structure` |
| `scripts/_deprecated/state-{before,after}.json` | 206 each | Deprecated state fixtures |
| `scripts/content-migration/backfill-lookups.ps1` | 102 | Content migration |
| `config/config.psd1.example` | 41 | Tenant config — see §9a |
| `agents/sp-wave-orchestrator.md` | 33 | See §8f |

**Finding that changes candidate selection:** §7 recommends read-only `sharepoint-discovery` as the first pilot "because it minimizes write risk." Write risk and *extraction cost* are different axes. The two scripts backing the flagship discovery skill are the **two most literal-saturated non-deprecated files in the entire source** (178 and 147 hits). A read-only capability can still be extremely expensive to genericize.

**Required:** Plan Task 1's candidate-selection memo must score every candidate on a fourth axis — **literal density / genericization cost** — alongside expected value, source maturity, coupling, and write risk. §7's "read-only is recommended" guidance stands as a *safety* statement only and must not be read as a cost statement.

## 9a. Destination rule compliance — this repository's own hard gates

Extraction must satisfy this repository's rules, which are **stricter than the source repository's conventions**. The source's structure cannot be reproduced as-is.

### Symlinks (`.agent/rules/symlink-cross-platform.md`)

- CMAT's ~100+ skill symlinks were created directly (no manifest). This repo **prohibits `ln -s`** and requires every link to be registered in `symlinks.json` and created via `.agents/skills/symlink-manager/scripts/symlink_manager.py`.
- Required per extraction batch: `diagnose` before → add manifest entries → `restore` → `diagnose` after, with **zero** `? regular file (not a link)` and **zero** `✗ broken symlink` before commit.
- The source contains 4 broken symlinks (§8g). Copying link topology blindly imports that breakage into a repo whose gate rejects it.

### Hub-and-spoke (`.agent/rules/plugin-architecture-policy.md`, self-evolution Hard Gate #12)

- Every extracted script lands at `plugins/<plugin>/scripts/` (flat, bare module names per CLAUDE.md) **first**, then is symlinked into the consuming skill — never written directly inside a skill directory, **even when it has only one consumer**.
- `audit_plugin_structure.py <plugin>` must run before any extracted skill is considered complete (Hard Gate #12 — it catches real-file-in-skill-dir drift that `audit.py` does not flag). **Path correction (2026-08-07, found during Wave 2):** this script does **not** exist in this repository. It ships with the installed `agent-scaffolders` marketplace plugin at `~/.claude/plugins/marketplaces/richfrem-agent-plugins-skills/plugins/agent-scaffolders/scripts/audit_plugin_structure.py` (also mirrored under `~/.claude/plugins/cache/`). Hard Gate #12 and the earlier text here both read as though it were a repo-local tool, which sent Wave 2 looking for a nonexistent path. Until it is vendored or wrapped locally, invoke it from the plugin path above, and fall back to this repo's own `audit.py --path plugins/<plugin>` (weaker — it does not flag real-file-in-skill-dir drift) only with that limitation stated explicitly. Logged `OPEN`, `Repeat: YES` in `.agent/map-debt.md`.
- `plugin_add.py <plugin-path> -y` must run after modifying files under `plugins/` (Hard Gate #10).
- **Directory-level symlinks are forbidden** (`npx` drops them). CMAT's `sp-migrating-content/scripts/waves/` and `sp-discovering-web-parts/references/` are directory-shaped link groups — they must be decomposed into file-level links or real files.

### Self-contained skills (`plugin-architecture-policy.md` §3.2)

Every file a skill references must exist inside the skill directory, and all `SKILL.md` paths must be **relative to the skill root** (`../scripts/x.py`, never repo-root-relative or absolute). CMAT's `../../../scripts/...` traversal pattern is a source-layout artifact and **must not survive extraction**.

### Pluggable independence (`plugin-architecture-policy.md` §1.3)

Each destination plugin must install and run in isolation. This repo already enforces this via `tools/phase-4-5-core-plugin-refactoring/isolated_install_check.py` — every plugin Phase 9 touches or creates must pass it, per the precedent set in Phase 6 Task 0.16/0.17 where a real wheel-packaging defect was caught only by this check.

### TDD (`.agent/rules/test-driven-development.md`)

- Failing test first, failing **for the expected reason** — Plan Task 9 is correctly ordered before Task 12 and that ordering is non-negotiable.
- **Critical runtime paths must not be mocked**: script-execution wrappers, filesystem path resolution, file readers/parsers, and external API client boundaries. Extracted PowerShell path-resolution logic falls squarely in this category — test it with real subprocess and real filesystem resolution.
- **Prefer replay fixtures over synthetic mocks**: capture real (sanitized) SharePoint/PnP response payloads as fixtures rather than fabricating them, per §10's neutral-fixture requirement. Sanitization must strip tenant URLs, GUIDs, and group identities (§13).

### Self-evolution (`.agent/rules/self-evolution-policy.md`)

- **Every friction event gets a `map-debt.md` entry**, including ones fixed inline (`Status: RESOLVED`). Extraction will generate friction — broken source links, ambiguous genericity calls, packaging defects. A silent inline fix is a policy violation.
- **No deletions without explicit human permission** (Hard Gate #4, and the Absorption Fallacy in #5): if an extracted capability appears to supersede something already in this workbench, **flag it — never delete**. Run `git log --follow -- <file>` first (Hard Gate #11).
- **One logical fix per pass** (#6) — reinforces the batched-wave model in Plan Task 21 over a single sweeping extraction.
- The **Pre-Completion Gate block** must be emitted verbatim before any Phase 9 task is claimed complete.

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
- Every remaining source capability (all 34 observed skills — §8d, not only the extracted one) has an implementation-status classification (§3b) and a destination disposition (§3b) — none are copied automatically.
- **All 9 agents (§8f) carry a three-axis classification plus an orchestration-coupling judgment** — added 2026-08-07; agent coverage was previously absent from the exit criteria entirely.
- **Every symlink in the pilot's dependency closure is classified** `LIVE`/`BROKEN`/`DEPRECATED_TARGET`/`ESCAPES_PLUGIN`/`PROJECT_DATA` (§8g), with every discarded link recorded and reasoned — no silent omission.
- **This repository's own hard gates pass** (§9a): `symlink_manager.py diagnose` clean, `audit_plugin_structure.py` clean, `plugin_add.py` run, `isolated_install_check.py` passing for every plugin touched or created, and every friction event logged in `map-debt.md`.
- Ownership and lifecycle are documented.
- No CMAT rebind, second extraction, or general orchestrator begins automatically.

## 21. Deferred work

- Additional plugin families after the pilot.
- Write-capable provisioning and migration extraction.
- Shared validation or PowerShell infrastructure until multiple consumers justify it.
- Agent adaptation and cross-plugin orchestration.
- CMAT rebinding to consume reusable plugins.
- Distribution, marketplace, and production support commitments beyond the approved pilot.
