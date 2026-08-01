---
name: phase-4-5-core-knowledge-plugin-domain-refactoring
description: Decompose the mature docx-to-content plugin into four independently installable domain plugins with explicit versioned contracts.
status: DRAFT
version: 1.0.0-alpha
date: 2026-08-01
author: Richard Fremmerlid
---

# Phase 4.5 Specification: Core Knowledge Plugin Domain Refactoring

## 1. Status and Authority

**Specification status:** `SPECIFICATION_APPROVED_FOR_IMPLEMENTATION_PLANNING`

**Implementation status:** `NOT_AUTHORIZED`

**Entry-gate status:** `NOT_REVERIFIED`

The architecture was reviewed and approved (2026-08-01) subject to a narrow specification-correction pass (six items — see revision note below), which has now been applied. This status authorizes proceeding to `superpowers:writing-plans` for implementation-plan authoring. **It does not authorize Phase 4.5 implementation or Phase 9 implementation.** Do not use `PHASE_4_5_READY_FOR_EXECUTION` — that status remains unearned until the full sequence below completes.

```text
1. SPECIFICATION_READY_FOR_REVIEW              ← completed
2. SPECIFICATION_APPROVED_FOR_IMPLEMENTATION_PLANNING  ← this document, now
3. IMPLEMENTATION_PLAN_WRITTEN                 ← after superpowers:writing-plans
4. IMPLEMENTATION_PLAN_APPROVED                ← after adversarial plan review + user approval
5. PHASE_4_5_ENTRY_GATE_MET                    ← only once Phase 4 exit evidence is accepted
                                                   AND the Phase 4 feature branch is merged to main
                                                   AND main is clean and current
                                                   (status: NOT_REVERIFIED as of this pass)
6. PHASE_4_5_READY_FOR_EXECUTION               ← only after 1-5 above, in a fresh session,
                                                   on a dedicated Phase 4.5 branch/worktree
```

Steps 1-4 (specification and plan authoring/review) may proceed **before** Phase 4 formally closes — this is planning work, not execution. Step 5 (the actual implementation entry gate) requires Phase 4's exit evidence to be accepted and merged. **Phase 4's formal closure status remains `NOT_REVERIFIED`** — it has not been checked in this or the prior review pass — and must be explicitly reverified before any Phase 4.5 branch/worktree is created.

**Precondition:** This specification may only be activated (i.e., moved to execution) after Phase 4 exit evidence is accepted, the Phase 4 feature branch is merged to main, and a fresh Phase 4.5 branch/worktree is created. Phase 4.5 must not begin inside the Phase 4 worktree.

**Evidence Base:** Established during Phase 4.5 brainstorming (2026-08-01). Incorporates 14 formal corrections to the initial design proposal, one specification-integrity review pass (2026-08-01) that corrected a stale repository reference, imprecise test-count wording, and added missing Phase 9 evidence/extensibility detail, and a second correction pass (2026-08-01) resolving six specification-hardening findings from architecture review — see revision notes below.

**Revision note 2 (2026-08-01, six-item correction pass, architecture approved):** Corrected: (1) marketplace language — replaced unconditional marketplace requirements with `MARKETPLACE_ADOPTION_REQUIRES_HUMAN_DECISION` (§13); (2) contract/plugin version values — replaced asserted `1.0.0`/`v1` values with `PROVISIONAL_CONTRACT_VERSION` (§12, §23 Criterion 8) and `REQUIRES_HUMAN_DECISION_AFTER_WAVE_0` (§13 Plugin Version Starting Values); (3) orchestration sequence contradiction — clarified that the compatibility orchestrator preserves the enforced analyze-confirm-convert-render sequence while domain plugins remain independently invocable (§10); (4) dependency diagram — clarified arrows represent contract/data flow, never implementation-package imports (§11, §23 Criterion 6); (5) original-skill dispositions — changed from final dispositions to `PROPOSED_DISPOSITION`, pending Wave 0/1 consumer evidence (§23 Criterion 10); (6) unsupported-output and deferred-domain assumptions — separated "implemented during Phase 4.5" (existing Markdown renderer) from "architecturally supported but not implemented" (PDF/ASPX/agent-grounding) in knowledge-publication's domain description (§8), broadened the `knowledge-templates` trigger beyond a single renderer-count gate, and corrected the `sharepoint-publication` deferral rationale to avoid mischaracterizing Phase 3's SharePoint work as CMAT-owned (§25).

**Revision note (2026-08-01, specification-integrity pass):** This document was reviewed in full against the latest accepted brainstorming decisions and corrected for: (1) a stale `manual-conversion-poc` repository reference in §5, (2) imprecise "530 tests" wording that should distinguish collected/passed/skipped counts (§2, §5, §18 Wave 6, §26), (3) missing linkage to the Phase 9 observed source-inventory evidence baseline (§6a, new), (4) missing implementation-status metadata in the plugin manifest model to support future Phase 9 plugins with mixed maturity (§13a, new).

---

## 2. Goal

Decompose the mature combined `plugins/docx-to-content/` (v0.1.0, 530 tests collected / 529 passed / 1 skipped, 4 skills) into four independently installable and independently testable domain plugins with explicit versioned public contracts.

This is a **real responsibility split**, not a folder rename.

**Target plugins:**

```
plugins/source-document-extraction/
plugins/knowledge-analysis/
plugins/canonical-knowledge/
plugins/knowledge-publication/
```

**Deferred boundaries (documented, not scaffolded):**

```
plugins/knowledge-templates/
plugins/sharepoint-publication/
```

---

## 3. Preconditions and Entry Gate

Phase 4.5 begins only when:

- ✓ Phase 4 exit evidence is accepted and merged to main
- ✓ Feature branch `phase-4-native-sharepoint-skills` is merged
- ✓ main branch is clean and current
- ✓ A new Phase 4.5 branch/worktree is created (do not reuse Phase 4 worktree)

Phase 4.5 must NOT be authorized to begin during Phase 4 execution.

---

## 4. Non-Goals

Phase 4.5 does NOT implement:

- PDF extraction capabilities
- New agent-grounding renderer profiles
- Template catalog management
- SharePoint publication or deployment
- Phase 5 agent expansion
- Phase 9 CMAT plugin extraction

These remain separate, authorized phases with their own planning, evidence gates, and decomposition cycles.

---

## 5. Current Combined Implementation

**Current plugin:** `plugins/docx-to-content/` v0.1.0

**Current skills (4 total):**
- `analyze-document` — source inspection and structural analysis
- `convert-document` — canonical package construction
- `render-content` — output generation
- `orchestrate-conversion` — workflow orchestration

**Current test suite:** 530 tests collected across 45 test files — 529 passed, 1 skipped, 0 failed (verified by direct `pytest` run during specification review, 2026-08-01). This is the observed count at review time, not a permanent baseline; Wave 0 must establish the authoritative clean baseline immediately before extraction begins, since the suite may change between now and Phase 4.5 execution.
- Unit tests: plugin-local behavior
- Contract tests: boundary validation
- Integration tests: cross-module workflows
- Fixtures: 23 test fixture directories

**Current manifest structure:**
- `.claude-plugin/plugin.json` (v0.1.0, MIT license)
- `plugin.yaml` (hermes compatibility)
- Repository reference: `github.com/richfrem/sharepoint-knowledge-workbench` (current repository identity; the plugin manifest's `repository` field is stale and points to a prior repository name, `manual-conversion-poc` — Wave 0/2 must correct this field on the extracted plugin manifests)

**Current CLI entry points:**
- `cmd_analyze` — structural analysis
- `cmd_confirm` — human plan confirmation
- `cmd_convert` — canonical package generation
- `cmd_render` — output rendering
- `cmd_run` — full pipeline

**Current renderers:**
- `multipage_markdown.py` — Markdown output
- `validate_rendered.py` — output validation
- `protocol.py` — renderer interface contract

**Scripts inventory:** 30+ Python modules covering extraction, analysis, canonicalization, validation, publication, and media handling.

---

## 6. Target Plugin Ecosystem

After Phase 4.5, the SharePoint Knowledge Workbench will consist of:

```
SharePoint Knowledge Workbench
│
├── Core knowledge pipeline — Phase 4.5 ✓
│   ├── source-document-extraction
│   ├── knowledge-analysis
│   ├── canonical-knowledge
│   └── knowledge-publication
│
├── Future delivery capabilities
│   ├── knowledge-templates (deferred Phase N)
│   └── sharepoint-publication (deferred Phase N)
│
├── Future SharePoint native capabilities
│   ├── sharepoint-native-skills (Phase 5)
│   └── sharepoint-agents (Phase 5+)
│
└── SharePoint engineering (Phase 9 candidates)
    ├── sharepoint-discovery
    ├── sharepoint-schema
    ├── sharepoint-page-modernization
    ├── sharepoint-link-analysis
    ├── sharepoint-provisioning
    ├── sharepoint-content-migration
    └── sharepoint-validation-and-reconciliation
```

**Phase 9 candidate names are NOT implementation commitments.** They represent the ecosystem into which Phase 9 will later introduce selectively extracted generic SharePoint capabilities from the intact CMAT repository.

### 6a. Phase 9 Source-Evidence Baseline (informational, not a Phase 4.5 deliverable)

Phase 9 will later assess an actual source skill ecosystem, observed (2026-08-01, not pinned) at `jag-csb-cmat-sharepoint-online/plugins/sharepoint-migration/skills/`:

```text
119 directories
272 files (144 real files + 128 symlinks)
33 skills
```

These are **observed baseline facts at the time of observation, not permanent totals** — the source repository continues to evolve independently, and Phase 9 must pin an exact commit before any extraction begins (see `phase-9-reusable-sharepoint-plugin-extraction-spec.md` §3a for full detail).

Observed source capability families (classification hypotheses, not committed plugin boundaries):
- SharePoint discovery (site structure, lists, content types, pages, web parts, navigation, forms, permissions, workflows)
- Schema analysis and mapping (audit, choices, content-type/list/taxonomy mapping, deployment matrix)
- ASPX and wiki-page modernization (analysis, conversion, layout/web-part remediation)
- Link extraction and remediation (link extraction, page-link remediation, document-content-link remediation, validation)
- Content migration and upload (migration, upload, ShareGate integration)
- Provisioning and validation (modern calendars, app registration, content, permissions)
- Migration reporting and synthesis

**Phase 4.5 does not implement, import, or scaffold any of these.** Phase 4.5's only relationship to this evidence is that it **establishes the common plugin operating model these future capabilities will use** (§7 below) — the plugin manifest structure, skill ownership, independent versioning, contract versioning, three-tier test architecture, and documentation model designed in this specification must be general enough to accommodate that future ecosystem without requiring a second plugin system. This is a design-generality constraint on Phase 4.5, not a Phase 4.5 implementation scope addition.

---

## 7. Phase 9 Relationship

Phase 4.5 establishes a **coherent plugin model** for the entire workbench, including Phase 9 future additions.

**Phase 9 must reuse Phase 4.5 conventions:**
- Plugin manifests and .claude-plugin/ structure
- Skill ownership and versioning per plugin
- Independent plugin versions
- Contract versioning separate from plugin versions
- Compatibility matrix model
- Dependency rules and reverse-dependency prohibitions
- Test and fixture ownership (three-tier model)
- Documentation categories and update discipline
- Marketplace registration
- Lifecycle and removal gates

**Phase 9 must NOT:**
- Invent a second plugin system
- Establish conflicting manifest conventions
- Create cross-repository symlinks or automatic backlog migration
- Make this workbench depend on the intact CMAT repository

**Disposition rules for Phase 9 candidates:**

Every extracted capability receives one explicit disposition:
- `EXTRACT_AS_NEW_PLUGIN` — if domain-scoped and reusable
- `MERGE_WITH_EXISTING_PLUGIN` — if narrow and belongs with core
- `EXTRACT_AS_SKILL_IN_EXISTING_PLUGIN` — if scoped to one domain
- `EXTRACT_AS_SHARED_CONTRACT_OR_LIBRARY` — if generic
- `KEEP_PROJECT_SPECIFIC` — if CMAT-only
- `RESEARCH` — if validation needed
- `RETIRE` — if superseded
- `REJECT` — if out of scope

The ORDS framework is excluded from Phase 9 scope.

---

## 8. Domain Responsibilities and Non-Responsibilities

### source-document-extraction

**Owns:**
- Source-format inspection and parsing
- DOCX extraction and structure detection
- Pandoc integration
- Word-specific defect detection (mixed heading levels, glued images, etc.)
- Source cleanup and normalization
- Media extraction (EMF→PNG conversion, etc.)
- Normalized source-document construction
- Source-level validation

**Does NOT own:**
- Semantic topic modeling or content analysis
- Canonical identities or topic IDs
- Publication maps or navigation
- Rendering or output generation
- SharePoint deployment or provisioning

**Future scope:** DOCX is the first implemented format. The plugin domain is intentionally broader to receive PDF, HTML, or other format extractors without renaming.

### knowledge-analysis

**Owns:**
- Source-independent structural analysis
- Heading hierarchy interpretation
- Topic-boundary recommendations
- Cross-reference detection and analysis
- Semantic observations (missing sections, content clarity, organization quality)
- Analysis-plan or conversion-plan proposal
- Human-confirmation workflows and revisions

**Does NOT own:**
- DOCX or Pandoc behavior (that's source-document-extraction)
- Canonical hashing, identities, or package assembly
- Publication maps or rendering
- SharePoint deployment
- Media handling

### canonical-knowledge

**Owns:**
- Confirmed-plan consumption
- Canonical-topic construction
- Stable topic and chunk identities
- Structural anchors (for source lineage)
- Content hashes and content comparison
- Package manifests and metadata
- Publication maps (topic ordering, navigation, chapter structure)
- Canonical-package loading and deserialization
- Canonical-package validation
- Canonical-package comparison (byte-identity and semantic drift detection)

**Does NOT own:**
- Source-file extraction (source-document-extraction)
- Semantic analysis (knowledge-analysis)
- Rendering or output generation
- SharePoint upload or reconciliation

### knowledge-publication

**Owns:**
- Canonical-package consumption and interpretation
- Publication-map consumption
- Renderer registry and renderer protocol
- Multipage Markdown rendering
- Navigation assembly (index.md, breadcrumbs, etc.)
- Media reference resolution and placement
- Rendered-output validation

**Implemented during Phase 4.5:**
- Existing multipage Markdown renderer (migrated from `docx-to-content`)
- Existing rendered-output validation (migrated from `docx-to-content`)

**Architecturally supported by this plugin's renderer-registry design, but NOT implemented during Phase 4.5** (consistent with §4's non-goals — no new renderer profiles, no PDF rendering, no SharePoint publication):
- PDF output
- ASPX output
- Agent-grounding output profile (topic digests, source maps)
- Any other future output profile

Do not let the implementation plan create new renderers to satisfy this domain description — the renderer-registry architecture is deliberately extensible, but Phase 4.5's deliverable is limited to migrating the one renderer that already exists.

**Does NOT own:**
- DOCX extraction or source parsing
- Topic analysis or semantic reasoning
- Canonical-package creation or validation
- SharePoint upload, publication, or reconciliation

---

## 9. Skill Topology and Compatibility

### Domain-Native Skills (Provisional)

Each plugin owns skills backed by real working implementation.

**source-document-extraction:**
- `analyze-source-document` — inspect source structure
- `extract-docx` — extract and normalize DOCX content
- `normalize-source-document` — apply source cleanup rules
- `validate-extraction` — verify normalized output

**knowledge-analysis:**
- `analyze-content-structure` — identify sections, topics, cross-references
- `recommend-topic-boundaries` — propose topic groupings
- `analyze-cross-references` — detect links and dependencies

**canonical-knowledge:**
- `build-canonical-package` — construct canonical from confirmed plan
- `validate-canonical-package` — verify package integrity
- `inspect-content-lineage` — trace source→canonical mapping
- `compare-canonical-packages` — detect changes and regressions

**knowledge-publication:**
- `render-publication` — orchestrate rendering
- `render-human-markdown` — generate Markdown output
- `validate-rendered-output` — verify rendered integrity

**These names remain PROVISIONAL** until Wave 0 maps actual implementation. Do not create a skill merely to complete the taxonomy.

**Skill requirements:**
- Distinct, clear user intent
- Working, production-ready implementation
- Clear owning plugin
- Independent testable contract
- Meaningful standalone reuse
- Documented inputs, outputs, safety boundaries

### Compatibility Skills (Temporary)

The existing skills may remain temporarily as thin orchestrators:

```
analyze-document
  → analyze-source-document + recommend-topic-boundaries

convert-document
  → (normalize extracted source if needed)
  → consume confirmed-plan
  → build-canonical-package
  → validate-canonical-package

render-content
  → render-publication
  → validate-rendered-output
```

**Requirements:**
- Contain NO domain logic (only orchestration)
- Call ONLY stable new plugin public interfaces
- Preserve existing workflow unchanged
- Have deprecation notices in documentation
- Have tests proving equivalent behavior
- Identify known consumers
- Identify retirement wave (Wave 7 or later)

**Critical rule:** New plugins MUST NOT import or depend on the compatibility layer. Reverse dependency is prohibited.

**Orchestration decision:** Do not create a permanent broad "workbench" plugin solely to host orchestration. A thin compatibility layer is acceptable only as a temporary bridge.

---

## 10. Workflow Orchestration Model

The data flow is:

```
source-document-extraction
        ↓ normalized-source-document contract v1

knowledge-analysis
        ↓ confirmed analysis-plan contract v1

canonical-knowledge
        ↓ canonical-package and publication-map contracts v1

knowledge-publication
        ↓ rendered artifacts
```

This does NOT require every plugin to directly invoke the next plugin.

**Preferred orchestration:**

```
workflow orchestration layer
├── invokes source-document-extraction
├── passes validated output to knowledge-analysis
├── passes confirmed decisions to canonical-knowledge
└── passes canonical package to knowledge-publication
```

The orchestration layer:
- Contains NO domain logic
- Does not hard-code plugin paths (uses interfaces)

**Clarification (resolves an apparent contradiction with §3/§23's preserved-workflow requirement):**

```text
The compatibility workflow orchestrator (the thin layer behind the temporary
analyze-document / convert-document / render-content skills, §9) preserves
the established analyze → human-confirmation → canonical-construction →
render sequence. This sequence remains a required, enforced gate — it is
not optional or reorderable by that orchestrator.

The underlying domain plugins (source-document-extraction, knowledge-analysis,
canonical-knowledge, knowledge-publication) do not enforce that sequence
internally. Each plugin remains independently invocable through its public
contract by other callers who are not going through the compatibility
orchestrator — e.g. a future Phase 5 consumer that only needs
knowledge-publication's rendering capability against an already-built
canonical package, without re-running extraction or analysis.
```

This preserves both requirements simultaneously: the backward-compatible, human-gated CEIS workflow is never bypassed when using the compatibility orchestrator, while the domain plugins themselves remain composable and do not control or depend on one another's invocation order.

**Dependency violations:**

Known reverse or cross-domain dependencies must be FIXED in the extraction wave that exposes them. Do not carry violations until Wave 7.

Allowed temporary compatibility:
```
old external entry point (skill, command)
  → compatibility facade
  → new plugin API
```

Prohibited:
```
new plugin
  → old plugin implementation
```

---

## 11. Dependency Direction and Prohibited Imports

### Mandated Direction — Contract/Data Flow, Not Implementation Chaining

**Important clarification:** the vertical arrow diagram below (and the similar diagram in §10) represents **contract/data flow** — the order in which artifacts are produced and consumed — not permission for one plugin to import or invoke another plugin's implementation. Read every arrow as "produces an artifact consumed by," never as "calls into" or "depends on the package of."

**Precise (non-misleading) statement of the architecture:**

```text
source-document-extraction
  → produces normalized-source-document

knowledge-analysis
  → consumes normalized-source-document
  → produces analysis-plan (confirmed via human-confirmation gate)

canonical-knowledge
  → consumes confirmed analysis-plan
  → produces canonical-package and publication-map

knowledge-publication
  → consumes canonical-package and publication-map
  → produces rendered outputs
```

The workflow orchestrator (§10) passes these artifacts between plugins at runtime. No plugin imports, calls, or links against another plugin's package.

**Shorthand diagram (retained for quick reference only — always defer to the precise statement above if the two appear to conflict):**

```
source-document-extraction
      ↓
knowledge-analysis
      ↓
canonical-knowledge
      ↓
knowledge-publication
```

**The desired implementation dependency direction is:**

```text
plugin → shared public contract schema/interface   (ALLOWED)
```

**Never:**

```text
plugin → next plugin's implementation package        (PROHIBITED)
```

### Prohibited Imports

No plugin may import:

**source-document-extraction may NOT import from:**
- knowledge-analysis
- canonical-knowledge
- knowledge-publication
- old docx-to-content compatibility layer

**knowledge-analysis may NOT import from:**
- source-document-extraction implementation internals (only contracts)
- canonical-knowledge
- knowledge-publication
- DOCX or Pandoc handlers

**canonical-knowledge may NOT import from:**
- source-document-extraction
- knowledge-analysis implementation internals (only contracts)
- knowledge-publication
- DOCX runtime or analysis logic

**knowledge-publication may NOT import from:**
- source-document-extraction
- knowledge-analysis
- canonical-knowledge implementation internals (only contracts)
- DOCX extraction or Pandoc

### Enforcement

Automated dependency tests must reject prohibited imports at every wave boundary. A wave cannot close if forbidden imports exist.

---

## 12. Public Contracts and Versioning

### Explicit Versioned Contracts

**Status:** `PROVISIONAL_CONTRACT_VERSION`. The version labels below (shown as "v1") are illustrative, not approved. Wave 1 must explicitly approve the first authoritative contract versions after confirming current schema compatibility, existing contract history, breaking-change implications, supported manifest syntax, and fixture compatibility. The implementation plan may recommend "v1" as a starting point, but Wave 1's approval — not this specification — is the authoritative source.

Minimum documented contracts:

| Contract | Version (provisional) | Producer | Consumer | Purpose |
|----------|---------|----------|----------|---------|
| normalized-source-document | PROVISIONAL_CONTRACT_VERSION (illustrated as v1) | source-extraction | knowledge-analysis | Extracted and cleaned source structure |
| analysis-plan | PROVISIONAL_CONTRACT_VERSION (illustrated as v1) | knowledge-analysis | canonical-knowledge | Confirmed topic boundaries and content decisions |
| canonical-package | PROVISIONAL_CONTRACT_VERSION (illustrated as v1) | canonical-knowledge | knowledge-publication | Versioned, hashable, lineage-rich content package |
| publication-map | PROVISIONAL_CONTRACT_VERSION (illustrated as v1) | canonical-knowledge | knowledge-publication | Topic ordering, navigation, chapter structure |
| rendered-output-profile | PROVISIONAL_CONTRACT_VERSION (illustrated as v1) | knowledge-publication | (users) | Final formatted output (existing multipage Markdown renderer; see §8 correction on implemented-vs-future output profiles) |

### Contract Record

For each contract, maintain:

- Contract name
- Contract version (independent of plugin version)
- Authoritative schema or specification
- Producer plugin
- Consumer plugin(s)
- Compatibility policy (breaking vs. additive changes)
- Validation command
- Fixture set location
- Deprecation path (if any)

### Contract vs. Plugin Versioning

**Plugin versions** (semantic: major.minor.patch) track the plugin's own evolution.

**Contract versions** track the public data interfaces between plugins. A plugin patch release does not automatically require a schema change. A schema change does not automatically require every dependent plugin to release a new version.

Plugin manifests must declare:
- Consumed contract names and versions (ranges if supported)
- Produced contract names and versions

---

## 13. Plugin Manifests and Marketplace Model

> **Amendment (2026-08-01, pre-planning-approval, recorded in the Specification Revision History at the end of this document):** The original manifest diagram below (`scripts/` directly on the plugin root, no packaging) was reviewed against this repository's actual Python conventions and found insufficient to prove independent installability — a requirement of spec §23 Criteria 4-5. §13b below amends the structure to a real `src/`-layout, `pyproject.toml`-based installable package per plugin, distinct from the plugin's Claude-Code distribution identity. This amendment was applied to the specification **before** implementation-plan approval, not deferred to Wave 1 execution.

### Manifest Structure (Claude Code plugin metadata — unchanged by this amendment)

Each plugin uses the established repository convention for its **Claude Code plugin identity** (skills, `plugin.json`, `plugin.yaml`):

```
plugins/<plugin-name>/
├── .claude-plugin/
│   └── plugin.json
├── plugin.yaml
├── README.md
├── skills/
│   ├── <skill-1>/
│   │   └── SKILL.md
│   └── <skill-2>/
│       └── SKILL.md
├── src/<python_package_name>/    # amended — see §13b; NOT bare scripts/
├── tests/
├── fixtures/
└── references/
```

The plugin's **Claude Code identity** (`plugins/<plugin-name>/`, hyphenated) and its **Python import package** (`src/<python_package_name>/`, underscored) are two distinct namespaces — see §13b.

**plugin.json fields** (inspected from current plugin, Phase 4.5 maintains compatibility). The `version` and contract-version values below are **illustrative placeholders, not approved values** — see `REQUIRES_HUMAN_DECISION_AFTER_WAVE_0` in the Plugin Version Starting Values section immediately below, and `PROVISIONAL_CONTRACT_VERSION` in §12:

```json
{
  "name": "source-document-extraction",
  "version": "<REQUIRES_HUMAN_DECISION_AFTER_WAVE_0>",
  "description": "...",
  "author": { "name": "..." },
  "repository": "https://github.com/richfrem/sharepoint-knowledge-workbench",
  "license": "MIT",
  "keywords": [...],
  "capabilities": [...],
  "consumed_contracts": {
    "normalized-source-document": "<PROVISIONAL_CONTRACT_VERSION>"
  },
  "produced_contracts": {
    "normalized-source-document": "<PROVISIONAL_CONTRACT_VERSION>"
  },
  "dependencies": [...]
}
```

Do not hard-code `1.0.0` into generated manifests during early waves merely because this specification uses it illustratively elsewhere.

Do not invent manifest fields unsupported by the repository's actual plugin loader. Document compatibility and add executable validation where supported.

### 13a. Implementation-Status Metadata (extensibility requirement for future plugins)

Because Phase 9 will later introduce plugins and skills drawn from a source ecosystem with mixed maturity (§6a — implemented, experimental, planned-only, deprecated, and project-specific skills coexist in the observed source inventory), the plugin/skill model Phase 4.5 establishes must support an explicit **implementation-status** declaration at the skill level, not just the plugin level.

**Minimum required values:**

```text
IMPLEMENTED
EXPERIMENTAL
PLANNED
DEPRECATED
```

**Rule:** The presence of `SKILL.md`, `evals.json`, or a results file (e.g. `results.tsv`) does NOT by itself indicate `IMPLEMENTED` status. A skill directory containing only documentation and eval placeholders, with no working script/test backing, is `PLANNED` regardless of how complete its `SKILL.md` reads. This distinction is required so that a future Phase 9 plugin can honestly represent a skill that exists as a documented intent without misrepresenting it as executable.

Each of the four Phase 4.5 plugins' skills are expected to be `IMPLEMENTED` at Phase 4.5 exit (§23 Criterion 9 — "Domain-Native Skills Are Functional" already requires working implementation backing every skill). This metadata field exists primarily to make the *model* extensible for Phase 9, not because any Phase 4.5 skill is expected to ship as `PLANNED` or `EXPERIMENTAL`.

**Manifest field (provisional, subject to Wave 1 validation against the actual plugin loader):**

```json
{
  "skills": {
    "extract-docx": { "implementation_status": "IMPLEMENTED" }
  }
}
```

Do not invent this field's exact schema location without confirming the repository's plugin loader supports arbitrary per-skill metadata — Wave 1 must verify and, if unsupported, document the status in the plugin's README skill table instead (GENERATED_REFERENCE category, §17).

### 13b. Python Packaging and Contract Distribution Model (amendment)

**This section replaces any earlier implication that a plugin's `scripts/` directory, made importable via `sys.path` manipulation in a test `conftest.py`, satisfies the independent-installability requirement of §23 Criteria 4-5.** A test passing because pytest's `conftest.py` inserted a directory onto `sys.path` proves the code runs inside a checkout under a custom path setup — it does not prove the plugin can be built, installed, and imported as an independent Python distribution outside this monorepo, which is what "independently installable" means.

**Plugin distribution ID vs. Python import package — two distinct namespaces:**

| Plugin distribution ID (Claude Code identity, hyphenated) | Python import package (underscored) |
|---|---|
| `source-document-extraction` | `source_document_extraction` |
| `knowledge-analysis` | `knowledge_analysis` |
| `canonical-knowledge` | `canonical_knowledge` |
| `knowledge-publication` | `knowledge_publication` |

**Required layout per plugin (`src/`-layout, matching standard Python packaging practice):**

```
plugins/source-document-extraction/
├── .claude-plugin/
│   └── plugin.json
├── plugin.yaml
├── pyproject.toml
├── src/
│   └── source_document_extraction/
│       ├── __init__.py
│       ├── extraction.py
│       └── ...
├── skills/
│   └── extract-docx/
│       └── SKILL.md
└── tests/
    ├── unit/
    └── fixtures/
```

**`conftest.py` may contain test fixtures only.** Application/production imports (`import source_document_extraction.extraction`) must work after the package is installed (e.g. `pip install -e .` or a built wheel), with no `sys.path` manipulation required. This is the executable proof of independent installability.

**Public contracts — independently distributable, not repository-root-discovered:**

Public contract schemas (dataclasses + `validate()` functions, zero domain logic) are packaged as their own independently installable Python distribution, provisionally:

```
contracts/python/
├── pyproject.toml
└── src/
    └── knowledge_workbench_contracts/
        ├── __init__.py
        ├── normalized_source_document.py
        ├── analysis_plan.py
        ├── canonical_package.py
        ├── publication_map.py
        └── rendered_output_profile.py
```

The exact distribution/import name (`knowledge_workbench_contracts` above) is provisional, subject to Wave 1's collision and naming review. **Requirements, non-negotiable:**

- Unique import namespace, not owned by any of the four domain plugins.
- Zero domain implementation logic — schema/dataclass validation only.
- Independently versioned (contract version, separate from any plugin version — see §12).
- Buildable into a wheel and independently installable.
- Runtime code that imports it does **not** perform a repository-root lookup or upward directory walk — it is a declared package dependency, resolved through normal Python import machinery after installation, exactly like any third-party dependency.
- Each of the four domain plugins declares this contracts distribution as a dependency in its own `pyproject.toml`; a domain plugin never imports another domain plugin's implementation package under any circumstance, including via the contracts distribution as an indirection.

**Repository-level fixtures remain separate from the installable distributions:**

`tests/contracts/fixtures/` (repository root) remains the authoritative, human-reviewed evidence used for monorepo-level integration testing (spec §14 Tier 2/3) — it is not itself installed or shipped. A plugin's own `tests/fixtures/` (packaged with that plugin's test suite) carries the minimal fixtures that plugin's isolated, installed test run actually needs; these may be generated from (but are not identical storage to) the repository-level fixtures.

**Repository-root discovery tooling is repository-only, never runtime:** any `find_repo_root()`-style helper is confined to `tools/phase-4-5-core-plugin-refactoring/` for use by monorepo-level scripts and CI, and is explicitly prohibited from being imported by any plugin's `src/` (production) code or by the contracts distribution.

**Isolated-install proof (required gate, detailed in the implementation plan):** each plugin's wheel is built, installed into a clean virtual environment alongside only its declared dependencies (including the contracts distribution), and its tests plus at least one public-API call are exercised outside pytest's `conftest.py` machinery — proving the package, not merely the checkout, is independently usable. A combined-environment test installs all four plugin distributions together to detect namespace or dependency collisions before any wave closes.

### 13c. Neutral Runtime-Utility Distribution (amendment, Wave 1 human decision, 2026-08-01)

**Trigger:** Wave 1's disposition decision for `plugins/docx-to-content/scripts/atomic_output.py` (`create_staging_dir`/`promote`, the plugin's atomic staging-and-promotion primitives). The plan's default disposition was "duplicated: canonical-knowledge + knowledge-publication"; this section records why that default, and the alternative of placing the code in `knowledge_workbench_contracts`, were both rejected, and what was approved instead.

**Why `atomic_output.py` is not a contract.** §13b scopes `knowledge_workbench_contracts` to "types, schemas, and validation only — no domain implementation logic." `create_staging_dir`/`promote` are executable runtime/workflow logic (real filesystem operations with crash-recovery semantics) — not a schema, not a `validate()` function, not a data type. Placing them in the contracts distribution would violate §13b's own requirement regardless of how generic or dependency-free the code is; genericity does not make executable logic a schema.

**Why duplication was rejected.** `promote()`'s crash-recovery logic (atomic-rename-with-backup, restore-on-failure) is safety-critical: a bug in it can corrupt or lose a promoted package. Two independently-maintained copies of 173 lines of this logic, one in `canonical-knowledge` and one in `knowledge-publication`, would diverge the first time either is patched without the other being updated in lockstep — a known failure mode this specification's Rollback Model and evidence-discipline sections exist specifically to avoid elsewhere in the plan. A single, independently versioned distribution avoids this by construction.

**Approved runtime-utility scope.** A new, independently installable, independently versioned distribution:

```
runtime/python/
├── pyproject.toml
└── src/
    └── knowledge_workbench_runtime/
        ├── __init__.py
        └── atomic_output.py
```

- Distribution ID (provisional, confirmed in `wave-1-decisions.json`): `knowledge-workbench-runtime`. Python import package: `knowledge_workbench_runtime`.
- Initial approved responsibility: `create_staging_dir`/`promote` (atomic output directory promotion, crash-safe output replacement) and, if approved individually in a future wave, only other **directly related deterministic filesystem primitives** — never approved implicitly by analogy.
- **Explicit non-goal:** this distribution must not become a generic shared-utility dumping ground. Adding a function here requires the same kind of explicit Wave-level human decision this section itself required for `atomic_output.py` — it is not a lower-friction alternative to the contracts distribution's own dependency-boundary discipline.
- `build_generator_info`/`write_generator_info` (the two `atomic_output.py` functions that call `dependencies.probe_pandoc()`/`probe_soffice()`) are **not** part of this distribution — `dependencies.py` is `source-document-extraction`-domain logic per the Known File Inventory, and this neutral distribution must never depend on any domain plugin's implementation package, exactly as `knowledge_workbench_contracts` must not. Each of `canonical-knowledge` and `knowledge-publication` implements its own thin generator-info wrapper independently.
- Both `canonical-knowledge` and `knowledge-publication` **declare `knowledge-workbench-runtime` explicitly** as a dependency in their own `pyproject.toml` — no implicit or transitive reliance, matching the contracts distribution's own declared-dependency discipline in §13b.
- Independently packaged, tested (in isolation, via the same isolated-install harness pattern as every plugin and the contracts distribution), and versioned — a change to `knowledge_workbench_runtime` does not force a version bump of `knowledge_workbench_contracts` or vice versa, matching §12's per-contract independent-versioning principle.
- The dependency-boundary checker (`tools/phase-4-5-core-plugin-refactoring/dependency_boundary.py`) applies to this distribution's own `src/` exactly as it applies to every plugin's `src/` — `knowledge_workbench_runtime`'s production code must not import `repo_root` or any domain plugin's implementation package.

### Marketplace Model

**Status:** `MARKETPLACE_ADOPTION_REQUIRES_HUMAN_DECISION`

Current repository inspection found no active `marketplace.json`. Marketplace adoption is an **unmade distribution decision**, not a Phase 4.5 requirement. Wave 1 surfaces this decision explicitly for human approval; it does not default to "yes" merely because the specification describes what a marketplace catalog would look like if adopted.

**If marketplace adoption is approved (Wave 1 decision):**
- Create one repository-level marketplace catalog (`.claude-plugin/marketplace.json` at repo root) referencing all four independently installable plugins. Do not duplicate a complete marketplace catalog inside every plugin unless current tooling requires it.
- Include marketplace validation in wave gates and the final exit gate.

**If marketplace adoption is not approved (Wave 1 decision):**
- Record `NOT_APPLICABLE_WITH_DECISION` in the Wave 1 report.
- Do not create a marketplace catalog merely to satisfy this specification.
- Omit marketplace validation from required executable gates — every later section in this document that references "marketplace catalog," "marketplace validation," or "marketplace entries" as a gate item applies **only if marketplace adoption was approved**; read those references as "marketplace validation, if adopted" throughout §14, §18 (Wave 6 gate), §19, §23 (Criterion 5, 14), and §26.

### Plugin Version Starting Values

**Status:** `REQUIRES_HUMAN_DECISION_AFTER_WAVE_0`

Initial decomposition should establish one coordinated tested compatibility release, but starting version numbers must derive from the current plugin's history and be explicitly approved after Wave 0's inventory, not assumed from this specification.

Current plugin version: v0.1.0 (early development)

**Illustrative starting point only (not approved):** starting decomposed plugins at v1.0.0 would signal the beginning of independent versioning. This is one candidate the implementation plan may propose, but the actual starting version for each of the four plugins is `REQUIRES_HUMAN_DECISION_AFTER_WAVE_0` — a human must explicitly approve it, and it must not be hard-coded into any generated manifest before that approval.

---

## 14. Test Architecture (Three-Tier Model)

### Tier 1: Plugin-Local Tests

**Location:** `plugins/<plugin>/tests/`

**Scope:** Unit tests and plugin-internal integration tests for that plugin's implementation.

**Fixtures:** Small synthetic or sanitized fixtures independent of upstream plugins.

**Independence requirement:** Each plugin tests without executing upstream implementations.

**Examples:**

- `knowledge-analysis/tests/` consumes a `normalized-source-document` contract fixture directly
- `canonical-knowledge/tests/` consumes a `confirmed-plan` fixture without running the analysis
- `knowledge-publication/tests/` consumes a `canonical-package` fixture without running extraction or analysis

**Critical rule:** No plugin may invoke an upstream plugin merely to construct test inputs. Use fixtures instead.

### Tier 2: Shared Contract Tests

**Location:** `tests/contracts/fixtures/` (or repository-level test convention discovered in Wave 0)

**Scope:** Fixtures representing public cross-plugin contracts.

**Ownership:** Repository-level (shared), but used by both producer and consumer plugins.

**Suggested structure:**

```
tests/contracts/fixtures/
├── normalized-source-document/
│   └── v1/
│       ├── minimal-valid/
│       ├── headings-and-media/
│       └── invalid/
├── analysis-plan/
│   └── v1/
├── canonical-package/
│   └── v1/
├── publication-map/
│   └── v1/
└── rendered-output-profile/
    └── v1/
```

**Fixture record requirements:**

- Contract name
- Contract version
- Fixture purpose
- Producer plugin
- Consumer plugin(s)
- Authoritative schema
- Expected validation result
- Source or generation method
- Reviewer approval

**Non-goals:** Do not create a general shared-fixtures dumping ground. Fixtures belong in `tests/contracts/` only if they validate a public interface used by multiple plugins.

### Tier 3: Repository-Level Integration and Golden-Master Tests

**Location:** `tests/integration/`, `tests/end-to-end/`, `tests/golden-master/` (or repository convention)

**Scope:** Full workflow validation, complete CEIS pipeline, and accepted output verification.

**Test ownership:** Repository-level, not any single plugin.

**Tests for:**
- Source document through full pipeline
- Plugin interoperability
- Workflow orchestration
- Contract compatibility
- Complete CEIS canonical output (byte-identical)
- Complete CEIS rendered output (byte-identical)
- Media handling end-to-end
- Package identity and publication-map correctness
- Backward-compatible commands

### CEIS Golden-Master Location

One authoritative copy of accepted CEIS artifacts. Never duplicated across plugins.

**Suggested structure:**

```
tests/golden-master/ceis/
├── input/
│   └── CEIS_MANUAL-working_version.docx
├── confirmed-plan/
│   └── ceis-manual-plan.confirmed.json
├── expected-canonical/
│   ├── canonical-content/
│   ├── publication-map.json
│   └── manifest.json
├── expected-publication-map/
│   └── publication-map.json
├── expected-rendered-output/
│   ├── rendered-output/
│   ├── pages/
│   └── media/
└── manifest.json
```

**Manifest contents:**

- Fixture-set version
- Source evidence ID and SHA-256
- Confirmed-plan SHA-256
- Canonical-package SHA-256
- Publication-map SHA-256
- Rendered-output tree hash (or per-file hashes)
- Contract versions
- Plugin compatibility-release versions
- Approved exceptions (if any)
- Reviewer disposition

**Evidence control:** If the real CEIS source or output cannot be committed to Git, retain a controlled evidence ID, hashes, and sanitized representative fixture. Do not weaken existing evidence controls.

---

## 15. Fixture Architecture and Migration

### Fixture Duplication Rules

**Allowed duplication:**
- Small, deliberately independent synthetic fixture for plugin-local tests

**Not allowed:**
- Complete CEIS canonical package copied into multiple plugins
- Complete rendered output in every renderer test directory
- Contract fixtures diverging from `tests/contracts/`

### Fixture Generation

Where fixtures are generated:

- Provide deterministic generation command
- Record: generator name, version, input, contract version, output hashes
- Generated fixtures must NOT require upstream plugin execution during normal plugin-local tests
- Regeneration is a maintenance operation, not a hidden test prerequisite

### Fixture Migration Ledger

Create ledger for all existing fixtures:

| Original Location | Destination | Type | Status | Approver |
|---|---|---|---|---|
| plugins/docx-to-content/tests/fixtures/... | plugins/source-extraction/tests/fixtures/ | plugin-local | MOVED_UNCHANGED | TBD |
| ... | tests/contracts/fixtures/... | shared-contract | MOVED_WITH_APPROVAL | TBD |
| ... | tests/golden-master/ceis/... | golden-master | RETAINED_AUTHORITATIVE | TBD |
| ... | docs/research/ | HISTORICAL | ARCHIVED_WITH_NOTE | TBD |
| ... | — | RETIRE_WITH_APPROVAL | REMOVED | TBD |

**Allowed final statuses:**

- `MOVED_UNCHANGED` — fixture migrated as-is
- `MOVED_WITH_APPROVED_PATH_UPDATE` — fixture migrated with path changes
- `REPLACED_BY_CONTRACT_TEST` — fixture replaced by shared contract
- `REPLACED_BY_INTEGRATION_TEST` — fixture replaced by integration fixture
- `RETAINED_AS_HISTORICAL` — kept as historical evidence
- `RETIRED_WITH_APPROVAL` — removed with documented reason

No fixture may have an undocumented destination.

---

## 16. Golden-Master and Exception Policy

### Byte-Identical Default

The complete CEIS workflow's outputs must remain byte-identical:

- Canonical canonical-content (topics, anchors, lineage)
- Publication maps (chapter structure, ordering)
- Rendered Markdown files and navigation
- Media paths and references
- Package manifests and metadata

Expected to remain constant:
- Topic identifiers
- Topic ordering
- Heading anchors
- Content hashes
- Media filenames
- Relative link paths

### Controlled Exception Process

Some internal artifacts may legitimately change due to plugin decomposition (paths, manifests, provenance fields).

**Exception record requirements:**

- Artifact name
- Before hash (git log, file hash, or commit)
- After hash
- Exact diff or `git diff` output
- Reason for change
- Affected contract
- Whether human-readable meaning changed
- Whether canonical meaning changed
- Whether downstream consumers are affected
- Reviewer disposition
- Human approval
- Updated golden-master authorization

**Allowed classifications:**

- `EXPECTED_ARCHITECTURAL_METADATA_CHANGE` (plugin provenance field updated) → allowed
- `EXPECTED_PATH_OR_PROVENANCE_CHANGE` (internal path changes) → allowed
- `APPROVED_CONTRACT_CHANGE` (schema evolved intentionally) → allowed
- `UNEXPECTED_REGRESSION` (unintended difference) → BLOCKS wave
- `INCONCLUSIVE` (needs investigation) → BLOCKS wave

Only the first three may proceed. UNEXPECTED_REGRESSION and INCONCLUSIVE block progression until resolved.

### Semantic Equivalence Is Not a Default

Do not use broad "semantically equivalent" assertions to permit unexplained differences.

Semantic equivalence is acceptable **only when:**
- Byte identity is impossible or intentionally changed
- The exact difference is understood and documented
- Deterministic comparison confirms unaffected fields
- Authoritative contracts permit the difference
- Downstream compatibility is tested
- A human explicitly approves the new baseline

LLM judgment alone is NOT sufficient.

---

## 17. Documentation Model

### Document Categories

Classify all affected documentation:

| Category | Example | Update Rule | Retirement Rule |
|----------|---------|-------------|-----------------|
| AUTHORITATIVE_CURRENT | README.md, architecture.md, CLAUDE.md, start-here.md, current usage | Update incrementally in each wave | N/A |
| GENERATED_REFERENCE | Plugin catalog, skill inventory, command index, compatibility matrix | Generate/validate at each wave from manifests | Automatically stale if manifest changes |
| HISTORICAL | Phase 1 plans, Phase 2 reports, prior implementation journals | Preserve original wording; add successor notes only | Retain as-is; mark historical |
| TRANSITIONAL | Compatibility wrapper docs, deprecation notices, migration ledger | Identify wave introduced and retirement wave | Remove at identified wave boundary |
| FUTURE_VISION | Master initiative plan, Phase 9 destination, deferred plugins | Update only if Phase 4.5 changes roadmap | Mark capabilities as IMPLEMENTED, IN_TRANSITION, DEFERRED, NOT_AUTHORIZED |
| EVIDENCE_OR_REPORT | Phase 3 reports, exit-gate findings, test results | Preserve as-is | Add successor reference if navigational help needed |

### Wave-by-Wave Documentation Responsibilities

**Wave 0: Baseline and Inventory**

Create:
- Documentation inventory (location and category of every doc reference)
- Live-reference inventory (which docs describe current state)
- Historical-reference inventory (which docs describe past states)
- Diagram inventory
- Command-example inventory
- Manifest inventory

Classify every occurrence of: `docx-to-content`, `plugins/docx-to-content`, `analyze-document`, `convert-document`, `render-content`

Classifications:
- `LIVE_REFERENCE` — currently correct
- `HISTORICAL_REFERENCE` — correct for its time
- `GOLDEN_MASTER_REFERENCE` — used in test or comparison
- `COMPATIBILITY_REFERENCE` — temporary orchestrator reference
- `STALE_REFERENCE` — outdated or incorrect

Do NOT edit during classification unless creating an immediate execution risk.

**Wave 1: Target Architecture**

Update or create:
- High-level architecture diagram showing four plugins and contracts
- Dependency diagram
- Skill ownership matrix
- Responsibility matrix
- Versioning policy document
- Compatibility wrapper documentation

Label explicitly: "Phase 4.5 target architecture (not yet fully implemented)"

**Waves 2-5: Plugin Extraction Waves**

Each extraction wave updates, in same commit series:

- Plugin README.md
- Plugin manifest
- Owned skill documentation
- Input/output contract specification
- Dependency declarations
- Public commands or entry points
- Examples and invocation guidance
- Test and fixture documentation
- Repository plugin index
- Compatibility matrix (current state)

At wave close, documentation must accurately identify:
- What code moved
- What remains in old docx-to-content
- What compatibility wrappers remain
- What old commands still work
- What new skills are available
- What the next wave will move

**Wave 6: Repository-Wide Reconciliation**

Verify and update:
- README.md consistency
- CLAUDE.md and Copilot guidance
- architecture.md accuracy
- DEPENDENCIES.md
- Current diagrams
- Marketplace catalog
- Examples and command snippets
- CI documentation
- Bundle-generation instructions
- Plugin compatibility matrix (final)
- Test commands
- Release guidance

Verify that incremental documentation changes form a coherent whole.

**Wave 7: Compatibility Retirement**

When compatibility wrappers are retired:

- Remove obsolete current command examples
- Preserve historical references
- Update migration guidance
- Update deprecation status
- Verify no current doc recommends removed entry points
- Regenerate factual reference indexes

**Wave 8: Old Plugin Removal Documentation**

Before removing `plugins/docx-to-content/`:

Prove:
- All current capabilities have successor locations
- All live commands have replacements or deprecation notices
- All skill references resolve
- All manifest and marketplace entries resolve
- All compatibility notices are dispositioned
- All historical references remain intentionally historical

After approved removal, update:
- start-here.md
- Current architecture documentation
- Any reference to the completed decomposition

### Limited Manifest-Driven Generation

Implement only lightweight generation producing clear immediate value:

**Good candidates:**
- Plugin catalog from manifests
- Skill inventory from plugin skill directories
- Plugin/version compatibility table
- Contract producer/consumer table
- Command inventory from SKILL.md files
- Manifest-to-README consistency checks
- Broken-path and stale-reference detection

**NOT candidates (require reviewed human-authored content):**
- Architecture rationale
- Plugin design intent
- Migration decisions
- Risk analysis
- Historical explanation
- User journey guidance

### Manifest as Factual Source

Where a fact exists in a plugin manifest, documentation should reference or link to it rather than duplicate independently.

**Examples:**
- Plugin ID
- Plugin version
- Owned skills
- Entry points
- Declared dependencies
- Supported contracts

**Validation:** Fail when:
- README lists a skill absent from manifest
- Manifest references missing skill path
- Repository plugin index omits active plugin
- Marketplace catalog points to stale path
- Compatibility matrix names nonexistent version
- Current command example invokes retired entry point

### README Ownership

Each plugin README must explain:

- Domain purpose and responsibility
- Non-responsibilities (what it does NOT do)
- Public skills (list with brief purpose)
- Inputs (contract names, formats)
- Outputs (contract names, formats)
- Contracts consumed (names, versions, schemas)
- Contracts produced (names, versions, schemas)
- Runtime dependencies (Pandoc, system tools)
- Plugin dependencies (if any)
- Test command
- Known limitations
- Version and compatibility policy

Do not duplicate full contract schemas in README. Link to authoritative specification.

### CLAUDE.md and Copilot Guidance

Update root guidance incrementally when an architectural rule becomes active.

Keep root guidance concise and durable:

- Plugin boundaries and ownership
- Dependency direction rules
- Contract-first integration
- Test ownership model
- Historical-reference preservation rules
- Deletion and removal gates

Place plugin-specific implementation detail in each plugin's own README or references directory.

Do not copy all four plugin READMEs into root CLAUDE.md.

### Diagram Policy

Maintain two diagram states during migration:

- **Current implemented architecture** (accurate as of last wave)
- **Target Phase 4.5 architecture** (goal state, updated in Wave 1)

Do not show the target as fully implemented before extraction completes.

After Wave 8, retire the transitional diagram or mark it explicitly historical.

Every active diagram must identify:
- Status (current/target/historical)
- Source of truth (which docs/manifests it derives from)
- Last validated wave

### Documentation Tests

Add automated checks for mechanically verifiable facts:

- Manifest paths exist
- Documented plugin paths exist
- Current skill links resolve
- Marketplace entries resolve
- Compatibility matrix references valid versions
- Generated reference pages are current
- No forbidden stale live references remain

Do NOT automate judgment about whether architectural prose is correct. Use reviewer checklists for non-mechanical content.

### Documentation Wave Gate

A wave cannot close if:

- Code has moved but current documentation points to old paths
- New plugin skills lack documentation
- Manifest and README disagree
- Architecture diagram misstates implementation status
- Commands in current guidance fail
- Generated references are stale
- Historical documents were rewritten inaccurately

Documentation is part of Definition of Done, not cleanup for later.

---

## 18. Nine-Wave Migration Model

### Wave 0 — Baseline Inventory and Dependency Graph

**Deliverables:**
- Complete artifact inventory (all files, tests, fixtures, skills, manifests)
- Current dependency graph (which module imports which)
- Ownership and responsibility map (preliminary)
- Live-reference classification (docx-to-content occurrences in codebase)
- Wave 1 preconditions checklist

**Gate:** Wave 0 must complete before Wave 1 begins. Transition decision point: Is the inventory complete and understood? Any surprises?

### Wave 1 — Contracts, Ownership, Migration Strategy

**Deliverables:**
- Target architecture diagram (four plugins, contracts, dependency direction)
- Explicit responsibility matrix (what each plugin owns, not owns)
- All public contracts defined and versioned
- Boundary test framework (contract tests for each interface)
- Compatibility wrapper specification (if temporary skills will remain)
- Migration strategy and wave sequence refinement
- Test/fixture ownership model (three-tier details)
- Documentation inventory and update plan

**Gate:** Full suite green (golden masters pass, all current tests pass). Target architecture approved by human.

### Wave 2 — Extract source-document-extraction

**Deliverables:**
- New plugin directory `plugins/source-document-extraction/`
- Plugin manifest and plugin.yaml
- Owned skills (analyze-source-document, extract-docx, normalize-source-document, validate-extraction)
- Owned scripts from current implementation
- Plugin-local tests and fixtures migrated
- Contract tests passing
- Plugin README documenting domain
- Removed LIVE_REFERENCE from docx-to-content for this domain
- Old docx-to-content still contains analysis, canonical, publication code (not yet removed)

**Gate:** Full suite green. source-document-extraction tests pass independently. Plugin installable. No reverse dependencies. Canonical outputs byte-identical.

### Wave 3 — Extract knowledge-analysis

**Deliverables:**
- New plugin directory `plugins/knowledge-analysis/`
- Plugin manifest and plugin.yaml
- Owned skills (analyze-content-structure, recommend-topic-boundaries, analyze-cross-references)
- Owned scripts from current implementation
- Consumes normalized-source-document contract fixture
- Plugin-local tests and fixtures migrated
- Contract tests passing
- Plugin README
- Removed LIVE_REFERENCE from docx-to-content for this domain

**Gate:** Full suite green. knowledge-analysis tests pass independently without running extraction. No reverse dependencies. Canonical outputs byte-identical.

### Wave 4 — Extract canonical-knowledge

**Deliverables:**
- New plugin directory `plugins/canonical-knowledge/`
- Plugin manifest and plugin.yaml
- Owned skills (build-canonical-package, validate-canonical-package, inspect-content-lineage, compare-canonical-packages)
- Owned scripts from current implementation
- Consumes confirmed-plan contract fixture
- Plugin-local tests and fixtures migrated
- Contract tests passing
- Plugin README
- Removed LIVE_REFERENCE from docx-to-content for this domain

**Gate:** Full suite green. canonical-knowledge tests pass independently without running extraction or analysis. No reverse dependencies. Canonical outputs byte-identical.

### Wave 5 — Extract knowledge-publication

**Deliverables:**
- New plugin directory `plugins/knowledge-publication/`
- Plugin manifest and plugin.yaml
- Owned skills (render-publication, render-human-markdown, validate-rendered-output)
- Owned scripts from current implementation
- Consumes canonical-package contract fixture
- Plugin-local tests and fixtures migrated
- Contract tests passing
- Plugin README
- Removed LIVE_REFERENCE from docx-to-content for this domain

**Gate:** Full suite green. knowledge-publication tests pass independently without running extraction, analysis, or canonicalization. No reverse dependencies. Rendered outputs byte-identical.

### Wave 6 — Repository-Wide Test, Fixture, Manifest, Metadata, Automation, Documentation Reconciliation

**Deliverables:**
- All tests from the Wave 0 clean baseline (530 collected / 529 passed / 1 skipped as observed at specification-review time — Wave 0 re-verifies this count against the actual Phase 4.5 start commit) migrated or dispositioned (test migration ledger complete)
- All fixtures migrated or dispositioned (fixture migration ledger complete)
- Shared contract fixtures established in `tests/contracts/fixtures/`
- Golden-master manifest created and validated
- All four plugin manifests synchronized
- Marketplace catalog created or updated (if applicable)
- Compatibility matrix complete and validated
- Documentation updates across all layers
- README consistency checked
- architecture.md updated
- CLAUDE.md updated
- DEPENDENCIES.md updated
- start-here.md updated with Phase 4.5 status
- CI workflows updated to test individual plugins
- Bundle-generation scripts updated
- Stale-reference report (quantify remaining docx-to-content references)

**Gate:** Full suite green. Repository builds and tests cleanly. All documentation matches implementation. All manifests validate. No unexpected stale references. Human review of documentation accuracy.

### Wave 7 — Retire Approved Compatibility Facades and Validate References

**Deliverables:**
- Temporary compatibility orchestrators evaluated: keep or remove?
- If retained: deprecation notices in place, retirement wave identified
- If removed: migration guide updated, old commands documented as historical
- All live references to old entry points removed or updated
- Old skill documentation either updated or archived
- Marketplace catalog updated if needed
- Historical documentation confirmed preserved
- Final stale-reference scan
- No live documentation refers to nonexistent entry points

**Gate:** Full suite green. No current documentation recommends removed commands. All breaking changes documented. Migration path clear for any remaining consumers.

### Wave 8 — Remove plugins/docx-to-content After Explicit Approval

**Deliverables:**
- Removal gate checklist complete and signed:
  - All production code migrated ✓
  - All tests migrated or dispositioned ✓
  - All fixtures migrated or dispositioned ✓
  - All manifests updated ✓
  - All compatibility decisions complete ✓
  - Golden masters pass ✓
  - All dependencies resolved ✓
- Directory `plugins/docx-to-content/` removed
- Git history preserved (commits remain)
- No empty directory, shell, or hidden forwarding
- start-here.md updated: "Phase 4.5 complete, docx-to-content decomposed into four plugins"
- Phase 4.5 exit statement recorded
- Final evidence package assembled

**Gate:** Full suite green. No broken imports or references. Repository clean. Human explicit removal approval recorded in git commit message.

---

## 19. Wave-Specific Test and Quality Gates

### Mandatory Gate: Full Test Suite Green

Every wave closes only when ALL applicable test layers pass:

1. Plugin-local tests (each new or modified plugin)
2. Contract tests (cross-plugin boundary validation)
3. Cross-plugin integration tests
4. Import and dependency-boundary tests (no prohibited imports)
5. Manifest validation (always required); marketplace validation, if adopted (§13 Marketplace Model)
6. Accepted CEIS canonical-package comparison (byte-identical by default)
7. Accepted CEIS rendered-output comparison (byte-identical by default)
8. Stale-reference and path validation

**No wave may knowingly carry failing tests into the next wave.**

If a wave exposes an issue that cannot be fixed in that wave without violating scope, the wave is **rescoped** to include the fix. Only explicit human decision to defer can override.

### Exception Record Gate

Any non-byte-identical output requires a complete exception record (see Section 16) with:
- Exact diff
- Reason
- Contract impact
- Reviewer disposition
- Human approval

UNEXPECTED_REGRESSION or INCONCLUSIVE exceptions block the wave.

### Dependency Boundary Tests

Automated tests must reject prohibited imports. Examples:

```python
# This must fail if committed:
from plugins.knowledge_publication import render
from plugins.source_document_extraction.scripts import *

# This is allowed (contract only):
from plugins.canonical_knowledge.contracts import CanonicalPackage
```

---

## 20. Migration Ledgers

### Test Migration Ledger

For every existing test, record:

| Original Path | Original Name | Protection | Destination Owner | Destination Path | Fixture Dependencies | Contract Protected | Logic Changed | Reason | Wave | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| tests/unit/test_analyze.py | test_heading_classification | topic-boundary | knowledge-analysis | tests/unit/test_analyze.py | normalize-src | analysis-plan | No | Migrated as-is | Wave 3 | MOVED_UNCHANGED |
| tests/integration/test_pipeline.py | test_full_ceis_workflow | end-to-end | (repo-level) | tests/integration/test_pipeline.py | golden-master | all contracts | No | Delegated to integration suite | Wave 6 | REPLACED_BY_INTEGRATION_TEST |
| ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |

**Allowed final statuses:**
- `MOVED_UNCHANGED` — migrated, no changes
- `MOVED_WITH_APPROVED_PATH_UPDATE` — migrated with path normalization
- `REPLACED_BY_CONTRACT_TEST` — functionality now tested at contract level
- `REPLACED_BY_INTEGRATION_TEST` — functionality now tested in integration suite
- `RETAINED_AS_HISTORICAL` — preserved as historical evidence
- `RETIRED_WITH_APPROVAL` — removed with documented reason and sign-off

No test may disappear without an entry in the ledger.

### Fixture Migration Ledger

| Original Location | Fixture Name | Purpose | Destination Type | Destination | Shared? | Approver | Wave | Status |
|---|---|---|---|---|---|---|---|---|
| tests/fixtures/docx/minimal.docx | Minimal DOCX | Unit test | plugin-local | source-extraction/tests/fixtures/ | No | TBD | 2 | MOVED_UNCHANGED |
| tests/fixtures/contracts/norm-src-v1.json | Normalized source | Contract test | shared-contract | tests/contracts/fixtures/normalized-source-document/v1/ | Yes | TBD | 1 | CREATED_NEW |
| ... | ... | ... | ... | ... | ... | ... | ... | ... |

---

## 21. Security and Safety Boundaries

### No New Attack Surface

Plugin decomposition must not introduce new security vulnerabilities:

- Each plugin validates inputs at its contract boundaries
- No plugin trusts another plugin's internal state without re-validating
- Plugin interdependencies use explicit, versioned contracts, not internal APIs
- No hardcoded paths or credentials
- Manifests do not expose internal implementation details
- Tests validate that each plugin enforces its safety boundaries

### Media and Content Handling

Media extraction and rendering must continue to handle:
- Embedded media (images, diagrams)
- External media references
- Malformed or suspicious media
- Missing media gracefully

The split does NOT relax safety requirements. Rendering must still validate all references before output.

### Lineage and Audit Trail

The canonical-knowledge plugin must preserve:
- Source-to-canonical mapping (structural anchors)
- Modification history and hashes
- Confirmed-plan provenance

Rendering and publication must preserve:
- Package identity in output metadata
- Publication-map references
- Topic ordering and navigation integrity

---

## 22. Removal and Rollback Strategy

### plugins/docx-to-content/ Removal Gate

The old combined plugin may be removed ONLY after:

✓ Every artifact has a documented destination (Wave 0/6 ledger complete)
✓ All tests are redistributed (test migration ledger complete)
✓ All contract tests pass
✓ Golden-master comparisons pass (byte-identical)
✓ All plugin manifests validate
✓ All live references are updated
✓ No external consumer is unaccounted for
✓ Explicit human removal approval is obtained and recorded in commit message

The old plugin must NOT remain afterward as:
- An empty directory (delete completely)
- An undocumented forwarding shell (complete removal)
- A hidden runtime dependency (all imports must be explicit)

### Rollback Strategy

If Phase 4.5 must be abandoned mid-execution:

1. Revert all commits in the Phase 4.5 branch
2. Preserve wave reports and migration ledgers as evidence
3. Document what was learned
4. Merge docx-to-content back as-is (or via git reset to pre-Phase-4.5)
5. Start a new Phase 4.5 cycle if appropriate

Rollback at any wave boundary is low-cost if ledgers are maintained.

---

## 23. Phase 4.5 Success Criteria

Phase 4.5 is complete only when ALL of the following are satisfied:

### 1. Four Working Domain Plugins Exist

```
plugins/source-document-extraction/  (working implementation)
plugins/knowledge-analysis/          (working implementation)
plugins/canonical-knowledge/         (working implementation)
plugins/knowledge-publication/       (working implementation)
```

No active plugin may be an empty placeholder.

Deferred domains remain documented but uncreated:
```
plugins/knowledge-templates/         (documented, not scaffolded)
plugins/sharepoint-publication/      (documented, not scaffolded)
```

### 2. Domain Ownership Is Explicit

Every migrated production artifact has one accountable destination:
- source-document-extraction
- knowledge-analysis
- canonical-knowledge
- knowledge-publication
- repository-level orchestration
- repository-level contract
- repository-level integration test
- historical evidence
- approved retirement

**Artifact migration ledger:** Contains no unresolved entries.

### 3. Existing Behavior Is Preserved

The established workflow continues to function:
```
analyze → human confirmation → canonical construction → rendering
```

**Test evidence:**
- Plugin-local tests: PASS
- Contract tests: PASS
- Cross-plugin integration tests: PASS
- Repository end-to-end tests: PASS
- CEIS canonical golden master: PASS (byte-identical)
- CEIS rendered golden master: PASS (byte-identical)
- Manifest validation: PASS
- Marketplace validation: PASS (if applicable)
- Documentation validation: PASS
- Stale-reference validation: PASS

### 4. Each Plugin Is Independently Testable

**Proven:**

- `source-document-extraction` tests without knowledge-analysis, canonical-knowledge, or knowledge-publication
- `knowledge-analysis` tests without Pandoc or DOCX extractor runtime
- `canonical-knowledge` loads, validates, compares packages without source extraction or analysis
- `knowledge-publication` renders canonical packages without Pandoc, DOCX extraction, or analysis

Each plugin may consume approved versioned contract fixtures without installing upstream plugin implementations.

### 5. Each Plugin Is Independently Installable

**For each plugin, validated:**

- Unique plugin identity (no name conflicts)
- Valid plugin manifest (.claude-plugin/plugin.json)
- Owned skill paths resolve
- Public entry points resolve
- Runtime dependencies are declared (Pandoc, system tools, etc.)
- Plugin dependencies are permitted (follow dependency direction)
- Consumed and produced contracts are documented
- Plugin-local tests run in isolation
- README reflects actual behavior
- Version is assigned and matches manifest

Independent installation does NOT mean every workflow runs with one plugin. It means each plugin can be installed, discovered, inspected, and tested according to its bounded responsibility.

### 6. Architectural Dependency Direction Is Proven

The implemented dependency graph matches — arrows are contract/data flow, not implementation imports (see §11):

```
source-document-extraction
        ↓ normalized-source-document contract

knowledge-analysis
        ↓ confirmed analysis-plan contract

canonical-knowledge
        ↓ canonical-package and publication-map contracts

knowledge-publication
        ↓ rendered outputs
```

**Automated dependency tests** reject prohibited imports — specifically, they verify each plugin imports only shared public contract schemas/interfaces, never another plugin's implementation package. Zero prohibited imports at wave close.

### 7. No Reverse or Circular Dependencies Exist

**Required proof:**

- Dependency graph generated
- Cycles detected: **0**
- Reverse-dependency violations: **0**
- Unclassified cross-plugin imports: **0**
- Hidden runtime reliance on docx-to-content: **0**

Temporary compatibility wrappers may point toward new plugin APIs. New plugins MUST NEVER depend on those wrappers.

### 8. Public Contracts Are Explicit and Versioned

**Minimum documented contracts** (versions are `PROVISIONAL_CONTRACT_VERSION` per §12 until Wave 1 approves the authoritative first versions):

| Contract | Version (Wave-1-approved, not pre-decided) | Producer | Consumer |
|----------|---------|----------|----------|
| normalized-source-document | PROVISIONAL_CONTRACT_VERSION | source-extraction | knowledge-analysis |
| analysis-plan | PROVISIONAL_CONTRACT_VERSION | knowledge-analysis | canonical-knowledge |
| canonical-package | PROVISIONAL_CONTRACT_VERSION | canonical-knowledge | knowledge-publication |
| publication-map | PROVISIONAL_CONTRACT_VERSION | canonical-knowledge | knowledge-publication |
| rendered-output-profile | PROVISIONAL_CONTRACT_VERSION | knowledge-publication | users |

**For every contract recorded:**

- Contract name and version
- Authoritative schema or specification
- Producer and consumer plugins
- Compatibility policy
- Fixture set location
- Validation command
- Deprecation path (if any)

Plugin versions and contract versions remain separate and independent.

### 9. Domain-Native Skills Are Functional

Each plugin exposes only skills backed by working capability.

**Provisional target skills finalized:**

- source-document-extraction: analyze-source-document, extract-docx, normalize-source-document, validate-extraction
- knowledge-analysis: analyze-content-structure, recommend-topic-boundaries, analyze-cross-references
- canonical-knowledge: build-canonical-package, validate-canonical-package, inspect-content-lineage, compare-canonical-packages
- knowledge-publication: render-publication, render-human-markdown, validate-rendered-output

(Names finalized after Wave 0 implementation inventory)

### 10. Original Skills Are Dispositioned

**Status:** The table below records `PROPOSED_DISPOSITION`, not a final decision. Wave 0 and Wave 1 must identify actual consumers before any disposition becomes final — internal consumers, documentation consumers, installed-plugin consumers, CLI users, automation or agent references, historical-only references, and compatibility requirements. It would be inconsistent to require this consumer analysis while simultaneously pre-deciding its result.

| Skill | Proposed Disposition | Rationale (subject to Wave 0/1 evidence) | Proposed Retirement Wave |
|-------|-------------|--------|-----------|
| analyze-document | PROPOSED_DISPOSITION: TEMPORARY_COMPATIBILITY_WRAPPER | Orchestrates new domain skills, pending consumer review | Wave 7 (proposed) |
| convert-document | PROPOSED_DISPOSITION: TEMPORARY_COMPATIBILITY_WRAPPER | Orchestrates new domain skills, pending consumer review | Wave 7 (proposed) |
| render-content | PROPOSED_DISPOSITION: TEMPORARY_COMPATIBILITY_WRAPPER | Orchestrates new domain skills, pending consumer review | Wave 7 (proposed) |
| orchestrate-conversion | PROPOSED_DISPOSITION: REPLACED_AND_RETIRED | Candidate merge into compatibility wrappers, pending consumer review | Wave 6 (proposed) |

**Allowed final outcomes (determined by Wave 0/1 consumer evidence, not pre-decided here):**

- `REPLACED_AND_RETIRED`
- `TEMPORARY_COMPATIBILITY_WRAPPER`
- `RETAINED_PUBLIC_ORCHESTRATOR`
- `HISTORICAL_REFERENCE_ONLY`

Preferred direction may remain retirement, but this specification does not guarantee that `orchestrate-conversion` (or any of the other three) disappears at its proposed wave before consumer evidence exists.

If a temporary wrapper remains at Phase 4.5 exit, the report must identify:
- Reason (bridge to existing workflows)
- Known consumers
- Replacement (new skills or commands)
- Retirement owner and trigger

Preferred state (subject to evidence): **consumers migrated, wrappers removed, documentation preserved as historical.**

### 11. Independent Versioning Is Operational

**Each plugin has:**

- Its own semantic version (e.g., source-extraction 1.0.0, knowledge-analysis 1.2.1)
- Its own manifest declaring version
- Its own changelog or release history
- Its own compatibility declarations

The initial four-plugin set is also recorded as one tested workbench compatibility release (e.g., "Knowledge Workbench Release 2026-08-01" or equivalent).

A repository-level compatibility matrix identifies the exact tested combination.

### 12. Test Ownership Is Complete

**Test migration ledger** shows every previous test:

- `MOVED_UNCHANGED` — preserved as-is
- `MOVED_WITH_APPROVED_PATH_UPDATE` — preserved with path normalization
- `REPLACED_BY_CONTRACT_TEST` — replaced by boundary test
- `REPLACED_BY_INTEGRATION_TEST` — replaced by integration test
- `RETAINED_AS_HISTORICAL` — kept as historical evidence
- `RETIRED_WITH_APPROVAL` — removed with documented reason

**Fixture ledger** similarly classifies every fixture:

- plugin-local
- shared-contract
- repository-integration
- golden-master
- historical
- controlled-external-evidence
- retired-with-approval

No test or fixture may be missing or silently dropped.

### 13. Documentation Matches Implemented State

**At completion:**

- README.md (root) — updated
- architecture.md (if exists) — updated
- CLAUDE.md — updated
- DEPENDENCIES.md — updated
- start-here.md — updated with Phase 4.5 completion note
- Plugin READMEs (all four) — complete and accurate
- Current diagrams — show final four-plugin architecture
- Skill documentation — reflects actual implemented skills
- Command examples — use actual working commands
- Marketplace catalog — references valid plugins, if marketplace adoption was approved (§13); otherwise `NOT_APPLICABLE_WITH_DECISION` is recorded
- Compatibility matrix — final, tested combination recorded
- Test instructions — describe how to test individual plugins and full suite

**Historical Phase 1 and Phase 2 records** retain original terminology and receive successor notes where useful.

**Current documentation contains NO unresolved live reference to:**
- `plugins/docx-to-content` (unless explicitly approved transitional or historical)
- Old skill names (unless explicitly deprecated and documented)
- Old command entry points (unless documented as historical)

### 14. Manifests and Marketplace Metadata Are Valid

**Required proof:**

- Four active plugin manifests validate against schema
- Plugin identities are unique and non-empty
- Skill identities and paths resolve
- All entry points resolve
- Dependencies are permitted (follow direction rules)
- Marketplace catalog (if present) references valid manifests
- Versions match the compatibility matrix
- No old active marketplace entry points to docx-to-content
- Consumed and produced contracts are declared

Validation command (if applicable): `claude plugin validate .` or equivalent.

### 15. Old Combined Plugin Is Removed with Approval

`plugins/docx-to-content/` may be removed only after removal gate passes (Section 22).

**Required proof:**

- All production code migrated or retired
- All tests migrated or dispositioned
- All fixtures migrated or dispositioned
- All live references updated
- All manifests updated
- All consumers accounted for
- Compatibility decision complete
- Golden masters pass
- **Explicit human removal approval recorded** in git commit message

After removal:

`plugins/docx-to-content/`

Must NOT remain as:
- An empty directory
- An undocumented compatibility shell
- A hidden runtime dependency

### 16. Full Repository Resumes Cleanly

**Final state:**

- All test layers green ✓
- Working tree clean (`git status` shows nothing staged or modified)
- Feature branch pushed to origin
- Independent review complete
- All wave reports finalized
- Exception records complete
- Migration ledgers complete
- Documentation current and validated
- start-here.md accurate and updated
- No automatic merge conflicts
- Ready for human merge decision

### 17. Phase 4.5 Exit Statement

**Final exit statement:**

> The former combined `plugins/docx-to-content/` implementation has been decomposed into four independently installable, independently testable, domain-scoped plugins connected through explicit versioned contracts. The established CEIS workflow (analyze → confirm → convert → render) is preserved with byte-identical accepted outputs. Dependency direction is enforced, prohibiting reverse imports. Every test and fixture has been dispositioned. All documentation matches the implemented architecture. The obsolete combined plugin has been removed with explicit approval. Phase 4.5 is complete and ready for Phase 5 downstream consumer validation.

---

## 24. Phase 5 Consumer-Validation Handoff

Phase 5 is the first downstream consumer of the new plugin boundaries.

**Phase 5 should include an early architecture-consumer checkpoint:**

Can Phase 5 consume the new plugin boundaries without:
- Importing internal implementation details?
- Recreating old coupling?
- Requiring undocumented additions?

**Record Phase 5 outcomes as:**

| Outcome | Meaning | Next Action |
|---------|---------|-------------|
| `BOUNDARIES_SUFFICIENT` | Plugins are well-scoped and complete | Continue Phase 5 normally |
| `MINOR_PLUGIN_ENHANCEMENT_REQUIRED` | Small addition helps without reshaping | Plan targeted enhancement |
| `NEW_CONTRACT_REQUIRED` | New cross-plugin interface needed | Evaluate contract addition (may require mini-phase) |
| `ABSTRACTION_GAP_DISCOVERED` | Missing capability in one plugin | Evaluate whether it belongs in Phase 4.5 or Phase 5 |
| `OUT_OF_SCOPE_FOR_CORE_PLUGINS` | Finding implies Phase 9 or future need | Document and defer |

**Phase 5 findings inform maintenance and future evolution.** They do NOT retroactively invalidate completed Phase 4.5 unless they reveal a material defect against its approved contracts.

---

## 25. Deferred Capabilities

### Explicitly Documented but Not Implemented

**`plugins/knowledge-templates/`**
- Deferred: Future phase, gated on evidence rather than a single narrow trigger
- Rationale: Template-management logic is not yet demonstrated as independently reusable
- **Gate (broadened — a second renderer profile is one possible trigger, not the only one):** Create `knowledge-templates` when at least one independently reusable template-management capability exists, such as: a semantic content-template catalog, template validation, template versioning, template selection, reusable template application, or presentation-template management across multiple consumers. A second renderer profile may provide supporting evidence for this gate, but it is not itself required or sufficient on its own.
- Owner: To be determined when authorized

**`plugins/sharepoint-publication/`**
- Deferred: Future phase, gated on demonstrated independent reusability
- **Rationale (corrected — not solely a CMAT-coupling claim):** `sharepoint-publication` remains deferred because the current SharePoint publication capabilities (Phase 3's publish/reconciliation/rollback/evidence tooling) are phase-specific pilot tooling and have not yet been demonstrated as an independently reusable plugin boundary. This is a maturity/reusability gap, not a claim that all current publication behavior is CMAT-owned — Phase 3's SharePoint publication work belongs to this workbench, not to CMAT. Phase 3 provides source evidence for future extraction; Phase 9 may separately provide additional overlapping SharePoint-engineering capabilities from the CMAT source ecosystem. The eventual `sharepoint-publication` plugin boundary requires an overlap analysis between these two evidence sources before it is scaffolded.
- Gate: Independent publication requirements, explicit separation need, or the overlap analysis above
- Owner: To be determined when authorized

### Phase 9 Candidates

See Section 7 (Phase 9 Relationship). No Phase 9 plugin is scaffolded during Phase 4.5.

---

## 26. Evidence Package

### Required Artifacts (Final Deliverable)

At Phase 4.5 completion, provide:

1. **Wave Reports** (one per wave: 0-8)
   - Deliverables completed
   - Tests passed (layers and counts)
   - Exception records (if any)
   - Reviewer sign-off

2. **Migration Ledgers**
   - Test migration ledger (all tests from the Wave 0 clean baseline dispositioned — 530 collected / 529 passed / 1 skipped observed at specification-review time, re-verified at Wave 0)
   - Fixture migration ledger (all fixtures dispositioned)
   - Artifact migration ledger (all code/script pieces located)

3. **Final Golden-Master Report**
   - Canonical output: byte-identical ✓
   - Rendered output: byte-identical ✓
   - Contract versions: verified
   - Exception records: (none or documented)
   - Hash verification: complete

4. **Manifest Validation Report**
   - Four plugin manifests: valid
   - Skill paths: all resolve
   - Dependencies: permitted
   - Marketplace catalog: valid (if applicable)

5. **Documentation Audit**
   - Inventory of all documentation changes
   - Stale-reference report (quantified)
   - Historical preservation audit
   - Current accuracy sign-off

6. **Architecture Review**
   - Dependency graph (zero cycles, zero reverse)
   - Prohibited import scan (zero violations)
   - Contract producer/consumer matrix
   - Plugin independence test results

7. **Git History**
   - All commits from Phase 4.5 branch
   - Branch pushed to origin
   - Ready for merge to main

---

## 27. Exit Gate

### Final Merge Checklist

Before merging Phase 4.5 branch to main:

- [ ] All 9 waves complete
- [ ] All wave reports finalized
- [ ] All test layers green
- [ ] Golden-master outputs byte-identical (with approved exceptions)
- [ ] All migration ledgers complete and dispositioned
- [ ] All manifests validate
- [ ] All documentation current
- [ ] Dependency graph: zero cycles, zero reverse
- [ ] Prohibited imports: zero violations
- [ ] Four plugins independently testable
- [ ] Four plugins independently installable
- [ ] Old plugins/docx-to-content/ removed with approval
- [ ] start-here.md updated with Phase 4.5 exit statement
- [ ] Repository clean (`git status` empty)
- [ ] Human review approved
- [ ] Ready to begin Phase 5

---

## Summary

Phase 4.5 is a bounded, evidence-backed, nine-wave refactoring that decomposes a mature single plugin into four independently usable, independently testable domain plugins with explicit versioned contracts. It establishes the plugin architecture and governance model that Phase 9 will later reuse for selective SharePoint engineering capabilities. Every test passes at every wave boundary. Existing behavior is preserved. The old combined plugin is removed only with explicit approval. Phase 5 becomes the first downstream consumer validation, not a completion dependency for Phase 4.5.

---

**Specification status:** `SPECIFICATION_APPROVED_FOR_IMPLEMENTATION_PLANNING`
**Implementation status:** `NOT_AUTHORIZED`
**Entry-gate status:** `NOT_REVERIFIED`

(see §1 for the full planning-vs-execution status sequence)

**Completed:**
1. ✓ User review of this specification
2. ✓ Explicit approval to proceed to `superpowers:writing-plans`, conditional on the six-item correction pass (completed, see §1 Revision note 2)

**Required Before Implementation (separate, later gate — do not conflate with the above):**
3. `superpowers:writing-plans` produces the implementation plan
4. Adversarial review of the implementation plan
5. Explicit user approval of the implementation plan
6. Phase 4 exit evidence confirmed accepted and merged to main (`NOT_REVERIFIED` as of this pass)
7. Fresh session, dedicated Phase 4.5 branch/worktree created
8. `start-here.md` updated to record planning readiness before execution begins

---

## Specification Revision History

**Revision 3 (2026-08-01, pre-plan-approval amendment):** Implementation-plan review (Revision 2 of the plan) surfaced that a `sys.path`/`conftest.py`-based packaging model does not satisfy this specification's own §23 Criteria 4-5 (independent testability and installability). Amended §13 (renamed the manifest diagram's `scripts/` to `src/<python_package_name>/`) and added §13b (Python Packaging and Contract Distribution Model), establishing: (1) each plugin has a distinct hyphenated distribution ID and underscored Python import package name; (2) a `src/`-layout with `pyproject.toml` per plugin, buildable and installable as a real wheel; (3) public contracts as their own independently installable distribution (`contracts/python/`, provisional import name `knowledge_workbench_contracts`), never requiring repository-root discovery at runtime; (4) `find_repo_root()`-style tooling confined to `tools/`, explicitly prohibited from plugin production code. This amendment was applied **before** implementation-plan approval — the plan must conform to it, not the reverse.
