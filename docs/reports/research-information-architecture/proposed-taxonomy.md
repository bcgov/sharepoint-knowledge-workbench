# Proposed Research Information Architecture — Domain Taxonomy

## Executive Summary

This repository's research and knowledge artifacts currently span **218 files** organized by phase number and document type rather than by durable domain. This taxonomy proposes a **subject-oriented, phase-agnostic** reorganization that:

- Preserves provenance through metadata and cross-references
- Groups related knowledge by capability domain, not execution phase
- Supports discovery without requiring readers to know which phase produced what
- Enables durable links to canonical knowledge (superseding phase-based paths)
- Maintains phase evidence as a discoverable byproduct, not the organizing frame

---

## Proposed Domain Structure

### Level 1: Primary Domains

#### 1. **SharePoint Platforms & Capabilities**
Knowledge about the Microsoft 365 ecosystem, SharePoint Online capabilities, licensing, and permissions.

**Subdomains:**
- `sharepoint-agents/` — Custom agents in SharePoint, discovery, configuration, lifecycle
- `copilot-in-sharepoint/` — Native Copilot in SharePoint skills, storage, execution, limitations
- `copilot-cowork/` — Microsoft 365 Copilot extensions and plugins
- `copilot-studio/` — Copilot Studio agent design and orchestration
- `content-permissions-governance/` — Permission boundaries, sensitivity, disclosure, audit

**Key Properties:**
- Not durable by phase; Microsoft product evolution may supersede research
- Requires dated retrieval records and source verification
- Field notes from tenant observation are primary evidence

---

#### 2. **Structured Content Engineering**
Knowledge about converting unstructured documents into versioned, maintainable, canonically-modeled content.

**Subdomains:**
- `document-extraction-analysis/` — DOCX/PDF parsing, structure detection, defect identification
- `content-models-contracts/` — Canonical representation, publication maps, metadata schemas
- `content-cleanup-chunking/` — Normalization, media handling, structural anchoring
- `multi-format-rendering/` — Human-facing and agent-optimized publication targets

**Key Properties:**
- Durable across pilot documents and phases
- Strongly tied to tooling (pandoc, LibreOffice, Python plugins)
- Implementation details live in `plugins/`; architecture and contracts live here

---

#### 3. **Publication & Delivery**
Knowledge about rendering structured content to multiple targets and managing versions in destination systems.

**Subdomains:**
- `sharepoint-publishing/` — Upload workflows, ASPX, modern pages, lifecycle
- `markdown-publishing/` — GitHub/repository publication, sourcing, versioning
- `publication-lifecycle/` — Approval, promotion, rollback, archival
- `multi-target-strategy/` — Rendering the same source for different audiences

**Key Properties:**
- Bridges content engineering and platform selection
- Includes both architecture and proof-of-concept evidence
- Durable target-neutral patterns

---

#### 4. **Knowledge Discovery & Retrieval**
Knowledge about how agents and users find, reason about, and act on knowledge.

**Subdomains:**
- `agent-grounding/` — Source formats, citation, retrieval constraints
- `search-retrieval/` — Indexing, querying, discoverability patterns
- `knowledge-curation/` — Continuous maintenance, obsolescence, quality signals
- `human-ai-collaboration/` — Workflows combining human review with AI-assisted discovery

**Key Properties:**
- Emerging domain; many findings are experimental
- Highly sensitive to platform capabilities and agent model
- Requires iteration as capabilities evolve

---

#### 5. **Capability Specifications & Contracts**
Knowledge defining what a skill, agent, or workflow should do and how it should behave.

**Subdomains:**
- `native-sharepoint-skills/` — Capability specs, evaluation cases, runtime contracts
- `sharepoint-agents/` — Agent behavior specs, grounding, output formats
- `hybrid-workflows/` — Specs combining repository and platform execution
- `governance-policies/` — Rules, approval patterns, lifecycle controls

**Key Properties:**
- Durable across runtimes and implementations
- Separates intent (spec) from execution (phase evidence)
- Foundational for multi-runtime validation

---

#### 6. **Architecture & Design Patterns**
Knowledge about system structure, component boundaries, and engineering decisions.

**Subdomains:**
- `plugin-architecture/` — Plugin decomposition, dependency management, packaging
- `skill-design-patterns/` — Skill definition standards, authoring guides, templates
- `data-models/` — Schemas, ontologies, information structures
- `deployment-patterns/` — Provisioning, configuration, lifecycle automation

**Key Properties:**
- Durable across phases (with evolution notes)
- Bridges implementation details and strategic vision
- Includes both approved and candidate patterns

---

#### 7. **Research & Experimentation**
Knowledge from exploratory work, tenant probes, and learning before full commitment.

**Subdomains:**
- `tenant-discovery/` — Capabilities verified against real environments
- `format-comparison/` — ASPX vs. Markdown, renderers, performance
- `platform-evaluation/` — Feasibility, limitations, roadmap-dependent features
- `implementation-learnings/` — Lessons from field work, bugs found, workarounds

**Key Properties:**
- Temporary to urgent; provides evidence gates for next phases
- Explicitly distinguishes empirical findings from speculation
- Cross-references to authoritative sources (Microsoft docs, version checks)

---

#### 8. **Strategic Planning & Vision**
Knowledge about long-term direction, phase structure, and executive decisions.

**Subdomains:**
- `master-roadmap/` — Phase structure, dependencies, entry/exit gates
- `capability-vision/` — Multi-runtime, multi-target, long-term architecture
- `initiative-governance/` — Human decisions, authorization boundaries, deferred items
- `risk-analysis/` — Known constraints, blockers, platform dependencies

**Key Properties:**
- Authoritative; not overwritten by research findings
- Explicitly records decisions with rationale and alternatives
- Includes forward-looking phases at structural level only until evidence exists

---

#### 9. **Phase Execution & Evidence**
Knowledge about what happened during a specific phase and its completion criteria.

**Subdomains:**
- `phase-plans/` — Phase-specific task breakdown, gates, dependencies
- `phase-evidence/` — Task results, verification, exit-gate proof
- `phase-dispositions/` — Human review outcomes, accepted limitations, next-phase implications
- `cross-phase-synthesis/` — Learnings that ripple across phases

**Key Properties:**
- Temporary; archived after phase closure
- Organized by phase number at discovery level only
- Evidence is linked to eternal domains when conclusions are durable

---

### Level 2: Document Types

Within each subdomain, documents are classified by type and purpose:

| Type | Purpose | Retention | Example |
|------|---------|-----------|---------|
| **Synthesis** | Durable, cross-referenced knowledge | Permanent | `capability-layering-sharepoint-skills-cowork-copilot-studio-github.md` |
| **Specification** | Formal definition of behavior, contract, or design | Permanent | `phase-3-tenant-capability-report.md` |
| **Field Note** | Empirical observation from tenant work, with date and method | Permanent | `field-note-aspx-vs-markdown-grounding-comparison.md` |
| **Research Summary** | Curated findings from external sources or exploratory work | Permanent | `research-summary-copilot-in-sharepoint-get-started.md` |
| **Capability Spec** | Formal definition of what a skill/agent should do | Permanent | `shared-capability-specification.md` (proposed) |
| **Decision Record** | Named decision, rationale, alternatives, disposition | Permanent | Part of planning docs and vision |
| **Plan** | Phase-specific execution plan with task breakdown | Archived after phase | `phase-7-cowork-copilot-studio-desk-research-plan.md` |
| **Evidence Report** | Task results, verification, exit-gate proof | Archived after phase | `phase-6-remediation-bundle.md` |
| **Implementation Note** | Lessons, bugs, workarounds from execution | Archive or promote | `wave-3-analysis-plan-split-decision.md` |
| **Legacy Reference** | Superseded but historically useful | Archive | `docx-to-content-legacy-references/` |
| **Experiment Protocol** | Method for a controlled probe or test | Archive if concluded | `phase-5-evaluation-cases/` |

---

## Proposed Reorganization Rules

### File Naming
- **Synthesized knowledge:** `<domain>-<subject>[-<version>].md`
  - Example: `sharepoint-agents-capability-spec.md`
- **Field notes:** `field-note-<finding>-<date>.md` (date YYYY-MM-DD optional if obvious from context)
  - Example: `field-note-aspx-vs-markdown-grounding-2026-07-28.md`
- **Research summaries:** `research-<topic>-<source-type>.md`
  - Example: `research-copilot-in-sharepoint-official-docs.md`
- **Specifications:** `<domain>-<subject>-spec.md`
  - Example: `native-sharepoint-skills-spec.md`
- **Phase evidence:** Remains in `docs/reports/phase-N-*/` with clear task scoping
  - Example: `docs/reports/phase-6-task-0/task-0-migration-ledger-and-review-bundle.md`

### Provenance & Cross-Reference
Every document retains or gains:
- **Source phase(s)** (metadata comment or section)
- **Authored/verified date** (ISO 8601)
- **External sources** (links + retrieval date + version/commit + method)
- **Cross-references** to related domains

### Superseding & Archival
- **Superseded documents** are marked with a banner pointing to the new location
- **Legacy references** live in `./legacy/` subdirectories with explanatory READMEs
- **Archived evidence** remains searchable; phase reports are durable even after closure
- **Experiment protocols** are archived to `./experiments/closed/` once concluded

### Phase Provenance in Metadata
Each domain directory includes a `.provenance.json` mapping:
```json
{
  "documents": [
    {
      "file": "field-note-aspx-vs-markdown-grounding.md",
      "authored_phase": "phase-5",
      "task": "5.7-8",
      "durable": true,
      "supersedes": null,
      "deprecated": false
    }
  ]
}
```

---

## Navigation & Discovery Patterns

### For Users Asking "Where Is…?"

| User Question | Navigate To |
|---|---|
| "How do I create a native SharePoint skill?" | `docs/research/sharepoint-platforms/copilot-in-sharepoint/skill-design-patterns/` |
| "What are the permission limits for agents?" | `docs/research/sharepoint-platforms/content-permissions-governance/` |
| "How does document conversion work?" | `docs/research/structured-content-engineering/document-extraction-analysis/` |
| "What happened in Phase 4?" | `docs/reports/phase-4-native-sharepoint-skills/` |
| "Has Markdown grounding been tested?" | `docs/research/knowledge-discovery-retrieval/agent-grounding/field-notes/` |
| "What's the long-term vision?" | `docs/vision/master-roadmap/` |

### For Readers Asking "What Changed?"

- Phase closure documents are retained in `docs/reports/phase-N-*/`
- Each domain's `.provenance.json` shows which phase last updated key documents
- A `docs/research/CHANGELOG.md` records major reorganizations and file moves

---

## Migration Implications

### Immediate Actions (Session 1 — Planning Only)
1. ✅ Propose this taxonomy
2. ✅ Inventory all 218 research-like files
3. ✅ Map current path → proposed path
4. ✅ Identify collision candidates and consolidations
5. ✅ Approve before any moves

### Deferred to Session 2 (Execution)
- Move files using approved JSON manifest
- Update all inbound references
- Verify internal link consistency
- Produce audit report

### What Will NOT Change This Session
- Phase reports remain under `docs/reports/phase-N-*/`
- Plugin documentation remains in `plugins/*/docs/`
- Specifications and plans under `docs/superpowers/` stay put (may cross-link to new research locations)
- Vision documents under `docs/vision/` stay put (may link to organized research)

---

## Domain-Specific Guidance

### SharePoint Platforms & Capabilities
**Scope:** Everything about Microsoft 365, Copilot, SharePoint Online, governance, and permissions.
**Retention:** Permanent (but dated; external sources require version checks).
**Key Files:** capability-layering-*.md, research-summary-copilot-*.md, field-note-*.md
**Next Action:** Organize by subdomain; add retrieval-date metadata to external-source references.

### Structured Content Engineering
**Scope:** Document conversion, content models, chunking, anchoring, validation.
**Retention:** Permanent (durable across documents and pilots).
**Key Files:** Canonical/publication contracts, schema docs, media-handling notes.
**Next Action:** Move legacy phase-specific notes to a `./learnings/` folder; keep architectural decisions at the top level.

### Publication & Delivery
**Scope:** Rendering, approval workflows, publishing to SharePoint/Markdown/other targets.
**Retention:** Permanent with evolution notes as platforms change.
**Key Files:** Rendering architecture, publication-map contracts, multi-target strategy.
**Next Action:** Separate "how to render this source" (durable) from "Phase 5 tested X" (evidence).

### Knowledge Discovery & Retrieval
**Scope:** Agent grounding, search, indexing, citation, curation.
**Retention:** Permanent for patterns; field notes archived by date.
**Key Files:** Grounding format comparisons, agent behavior findings.
**Next Action:** Clearly label "empirical" vs. "speculative"; add platform/model version metadata.

### Capability Specifications
**Scope:** Formal specs for skills, agents, and workflows.
**Retention:** Permanent (but version-tracked; supersession is explicit).
**Key Files:** Phase-specific capability specs → Move to top-level domains with phase links.
**Next Action:** Consolidate overlapping specs from different phases; link phase evidence.

### Architecture & Design
**Scope:** Plugin structure, skill patterns, data models, deployment.
**Retention:** Permanent; superseded versions archived.
**Key Files:** Plugin architecture, skill design guidance, schema docs.
**Next Action:** Separate "how we built it" (phase evidence) from "how you should build it" (pattern).

### Research & Experimentation
**Scope:** Exploratory work, tenant probes, format comparisons, platform evaluation.
**Retention:** Permanent; labeled with date and method; clear confidence levels.
**Key Files:** Field notes, experiment protocols, tenant-discovered constraints.
**Next Action:** Add `.metadata.json` to each experiment with date, method, findings, confidence level.

### Strategic Planning & Vision
**Scope:** Long-term direction, phase roadmap, executive decisions.
**Retention:** Permanent; forward-looking phases at structural level only.
**Key Files:** master-initiative-plan, vision documents, decision records.
**Next Action:** Remains in `docs/vision/` (no move proposed); cross-link to research evidence.

### Phase Execution & Evidence
**Scope:** What happened, when, and why; task results and gate proofs.
**Retention:** Permanent archive; accessible by phase number.
**Key Files:** Phase reports, task evidence, exit-gate proofs, dispositions.
**Next Action:** Remains in `docs/reports/phase-N-*/` (no move proposed); cross-link generalizable findings to eternal domains.

---

## Durable Link Strategy

Every moved document will have:
1. **Old path (permanent redirect):** A stub with a pointer to the new location
2. **New path (canonical):** The authoritative location with metadata
3. **Cross-reference:** Links from related eternal domains

Example:
```markdown
# MOVED

This document moved to: `docs/research/sharepoint-platforms/copilot-in-sharepoint/research-copilot-in-sharepoint-preview-and-controls.md`

Original phase: Phase 7
Provenance: `docs/reports/phase-7-cowork-copilot-studio-evaluation/`
```

---

## Success Criteria

By the end of this taxonomy work:
- ✅ Every research file has an explicit domain assignment
- ✅ No file is classified by phase number as its primary home
- ✅ Phase provenance is metadata, not the folder structure
- ✅ Readers can navigate by question/topic, not phase
- ✅ All 218 files are accounted for (moved, retained, or archived)
- ✅ Internal links still work (via redirects or updated references)
- ✅ New research naturally finds a domain home, not a phase folder

---

## Next Session (Execution)

Once this taxonomy is approved:
1. Create exact `old_path → new_path` mapping in JSON
2. Generate migration script (validation + reference updates + verification)
3. Execute moves via git-aware operations
4. Validate all internal links
5. Produce audit report

See `research-path-migration.proposed.json` and `current-to-target-content-map.md` for detailed mappings.
