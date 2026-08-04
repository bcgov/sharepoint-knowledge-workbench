# Proposed Research Information Architecture — Refined Taxonomy

**Status:** ⚠️ UNTESTED HYPOTHESIS, NOT A DECISION. Per corrected process direction (2026-08-04), the six-domain
tree below is one candidate architecture to be evaluated against the completed corpus manifest
(`research-migration-manifest.json`), alongside at least four other structural alternatives (see that
file's `architecture_alternatives_status` block). It must not be treated as approved or as a constraint
on how remaining corpus files are classified. The corpus-first process is: (1) inventory and
content-classify every file into the manifest with `proposed_destination: null`, (2) compare structural
alternatives against the completed inventory, (3) only then finalize a directory tree.  
**Previous version:** Commit c3957b9 (initial sketch); this document is retained as one input to the
architecture comparison, not as the answer.  
**Open question this taxonomy does NOT yet resolve:** whether `docs/research/` and `docs/reports/`
should remain separate trees, merge into one subject-organized corpus with artifact-type metadata, or
follow a hybrid model. See `research-migration-manifest.json`'s `architecture_alternatives_status.alternatives_to_evaluate` for the five options under consideration.

---

## Executive Summary

This repository's research corpus (218 files) is currently organized by **phase number** and **document filename**, making it difficult to discover durable knowledge across phases. This taxonomy proposes a **subject-oriented, multidimensional reorganization** that:

- Separates **subject-based research domains** (SharePoint, content engineering, publishing, etc.) from artifact types and lifecycle status
- Treats **phase as metadata** (provenance tracking), not the primary organizing frame
- Keeps **phase execution evidence** as a distinct historical area (remains under `docs/reports/phase-N-*/`)
- Preserves **durable, cross-cutting knowledge** in enduring research domains
- Enables discovery by subject without requiring readers to know which phase produced what

---

## Organizing Dimensions (Independent Classification Axes)

Research artifacts are classified along **four independent dimensions**, not forced into a single hierarchy:

### Dimension 1: Subject Domain (Content-Based)

What is the research *about*? Which problem space?

**Primary subject domains (mutually exclusive; every research document belongs to exactly one):**

1. **SharePoint Platforms & Capabilities** — Microsoft 365, Copilot in SharePoint, agents, licensing, permissions
2. **Structured Content Engineering** — Document extraction, normalization, models, chunking, validation
3. **Publication & Delivery** — Rendering targets (Markdown, ASPX, multi-format), approval workflows, SharePoint publishing
4. **Knowledge Discovery & Retrieval** — Agent grounding, search, indexing, discoverability, curation
5. **Architecture & Design Patterns** — Plugin structure, skill authoring standards, data models, deployment approaches
6. **Strategic Planning & Vision** — Long-term direction, roadmap structure, governance model, risk analysis

**Key principle:** Subject domains are NOT hierarchy levels. A document belongs to one domain and may relate to others via cross-references.

### Dimension 2: Artifact Type (Purpose & Genre)

What kind of artifact is this? What is it used for?

| Type | Purpose | Example |
|---|---|---|
| **Research Summary** | Curated findings from external sources or exploratory work | `research-summary-copilot-in-sharepoint-get-started.md` |
| **Synthesis** | Cross-phase knowledge integration; durable conclusions | `capability-layering-sharepoint-skills-cowork-copilot-studio-github.md` |
| **Field Note** | Empirical observation from tenant work; dated | `field-note-aspx-vs-markdown-grounding-comparison.md` (2026-07) |
| **Specification** | Formal definition of behavior, contract, design, or capability | `native-sharepoint-skills-spec.md` |
| **Decision Record** | Named decision, rationale, alternatives, owner, date, disposition | Part of vision/specs |
| **Implementation Learning** | Lessons, bugs, workarounds, defects from execution | `phase-4-agent-format-learning-journal.md` |
| **Experiment Protocol** | Method, controls, findings from a controlled probe | Phase-specific evaluation cases |
| **Capability Index** | Navigation and reference material | Domain README files |

### Dimension 3: Lifecycle Status (Temporal Classification)

What is the current state and validity of this content?

| Status | Definition | Treatment |
|---|---|---|
| **Active** | Current; actively maintained; used for decisions | Primary navigation focus |
| **Superseded** | Replaced by newer version; older version retained for history | Cross-link to replacement; archive original with banner |
| **Archived** | Concluded (experiment finished, phase closed) or historically useful only | Retain in archive location; link from active; no updates |
| **Provisional** | Candidate; not yet confirmed; decision pending | Marked as such; linked from decision point; archived once resolved |
| **Research** | Exploratory; findings not yet synthesized; confidence TBD | Labeled with method, limitations, confidence; may lead to durable docs |

### Dimension 4: Phase Provenance (Historical Context)

Which phase(s) generated or last updated this research?

**Recorded as metadata**, not used for primary navigation:
- **Source phase:** Which phase did this research originate in? (Phase 3, Phase 4, Phase 5, etc.)
- **Last updated:** Which phase most recently substantively changed this? (May differ from source phase)
- **Finding date:** When was the research conducted?
- **Evidence status:** Is this observation, finding, or conclusion? How confident?

**Key principle:** Provenance is tracked but *does not determine folder location*. Cross-phase findings go to subject domains, not phase folders.

---

## Proposed Directory Structure

### Level 1: Organizational Top Level

```
docs/research/
├── README.md                          (Master index and navigation guide)
├── INDEX.md                           (Detailed cross-domain navigation)
│
├── sharepoint-platforms-capabilities/         (Subject Domain #1)
├── structured-content-engineering/            (Subject Domain #2)
├── publication-delivery/                      (Subject Domain #3)
├── knowledge-discovery-retrieval/             (Subject Domain #4)
├── architecture-design-patterns/              (Subject Domain #5)
├── strategic-planning-vision/                 (Subject Domain #6)
│
└── _meta/                             (Metadata, indexes, navigation)
    ├── .provenance.json               (Phase provenance manifest)
    ├── .metadata-schema.md            (Format spec for research metadata)
    ├── domain-glossary.md             (Cross-domain terminology)
    └── research-methods.md            (Audit trail of how research was conducted)
```

### Level 2: Subdomains by Subject (Examples; full list below)

**SharePoint Platforms & Capabilities:**
```
sharepoint-platforms-capabilities/
├── README.md
├── sharepoint-agents/                 (Custom agent research)
├── copilot-in-sharepoint/             (Native Copilot skill research)
├── copilot-cowork/                    (Microsoft 365 Copilot plugins)
├── copilot-studio/                    (Copilot Studio research)
├── content-permissions-governance/    (Permission boundaries, disclosure, audit)
└── platform-features-and-limits/      (Capabilities, licensing, roadmap)
```

**Structured Content Engineering:**
```
structured-content-engineering/
├── README.md
├── document-extraction-analysis/      (DOCX/PDF parsing, structure detection)
├── content-models-contracts/          (Canonical representation, schemas)
├── content-cleanup-chunking/          (Normalization, media, anchoring)
├── multi-format-rendering/            (Output profiles, validation)
└── legacy/                            (Pre-Phase-1 references, archived)
```

**Publication & Delivery:**
```
publication-delivery/
├── README.md
├── sharepoint-publishing/             (ASPX, modern pages, lifecycle)
├── markdown-publishing/               (GitHub, repository-based)
├── publication-lifecycle/             (Approval, promotion, rollback, archival)
├── multi-target-strategy/             (Rendering same source to different audiences)
└── rendering-architecture/            (Template system, renderer contracts)
```

**Knowledge Discovery & Retrieval:**
```
knowledge-discovery-retrieval/
├── README.md
├── agent-grounding/                   (Source formats, citation, retrieval constraints)
├── search-retrieval/                  (Indexing, querying, discoverability)
├── knowledge-curation/                (Continuous maintenance, quality signals)
├── human-ai-collaboration/            (Workflows combining human + AI)
└── citation-verification/             (Citation accuracy, source tracking)
```

**Architecture & Design Patterns:**
```
architecture-design-patterns/
├── README.md
├── plugin-architecture/               (Plugin decomposition, dependency management)
├── skill-design-patterns/             (Skill definition standards, authoring guides)
├── data-models/                       (Schemas, ontologies, information structures)
└── deployment-patterns/               (Provisioning, configuration, lifecycle)
```

**Strategic Planning & Vision:**
```
strategic-planning-vision/
├── README.md
├── master-roadmap/                    (Phase structure, dependencies, gates)
├── capability-vision/                 (Multi-runtime, multi-target architecture)
├── initiative-governance/             (Human decisions, authorization boundaries)
└── risk-analysis/                     (Known constraints, blockers, dependencies)
```

### Level 3: Document Organization Within Subdomains

Files are organized chronologically or by confidence level (not phase):

```
sharepoint-platforms-capabilities/copilot-in-sharepoint/
├── README.md                                           (Subdomain index)
├── research-copilot-in-sharepoint-preview-features.md (Research summary from official docs)
├── field-note-copilot-skill-storage-constraints.md    (Tenant observation, 2026-07)
├── field-note-agentassets-skill-library-setup.md      (Tenant observation, 2026-07)
├── spec-native-sharepoint-skills-capability.md        (Formal specification)
└── experiments-closed/
    ├── README.md                                        (Explanation of archival)
    └── experiment-skill-discovery-and-launch.md        (Closed experiment record)
```

---

## File-Type Conventions

### Naming Pattern for Each Artifact Type

**Research Summary:**
```
research-<topic>-<source-type>.md
Example: research-copilot-in-sharepoint-official-docs.md
```

**Field Note:**
```
field-note-<finding>[-<date>].md
Example: field-note-aspx-vs-markdown-grounding-2026-07.md
```

**Synthesis/Overview:**
```
<topic>-synthesis.md  OR  <topic>-overview.md
Example: agent-format-evolution-synthesis.md
```

**Specification:**
```
<domain>-<subject>-spec.md
Example: native-sharepoint-skills-spec.md
```

**Implementation Learning:**
```
implementation-notes-<phase-or-project>-<topic>.md
Example: implementation-notes-phase4-agent-format-learning.md
```

---

## Phase Evidence (Separate from Research Domains)

**Phase execution evidence REMAINS in `docs/reports/phase-N-*/`** — NOT moved to research domains.

Why: Phase evidence is inherently temporal and tied to specific tasks/gates. It answers "What happened in Phase N?" not "What do we know about SharePoint?"

Phase reports are discoverable, durable, and remain authoritative for their phase. Research domains *link* to phase evidence when durable conclusions are grounded in it.

Example cross-link:
```markdown
**Evidence:** This finding is based on Phase 4 Task 8 deployment results.
See [Phase 4 Native SharePoint Skills Evaluation](../../reports/phase-4-native-sharepoint-skills/EVID-PHASE4-TASK8-EXIT-GATE.md).
```

---

## Consolidation Strategy (Content-Validated)

**Consolidation is NOT automatic.** Files are consolidated only when:

1. They address the same subject (same domain)
2. The newer document truly supersedes the older (or merging adds clear value without losing provenance)
3. Merging does not erase distinct findings or chronological context
4. Phase attribution is preserved (if research spans multiple phases)

**Default: Retain separately** unless consolidation provides clear benefit.

**Three consolidation outcomes:**

| Outcome | Use When | How |
|---|---|---|
| **Retain Separately** | Files have distinct focus, distinct phase origin, or distinct evidence basis | Keep both; cross-link; add provenance metadata |
| **Consolidate** | Newer doc completely supersedes older; same subject; no lost context | Merge findings with phase provenance; link to archived original |
| **Create Synthesis + Retain** | Multiple files have value; synthesis adds organizing value | New `*-synthesis.md` cross-references originals; keep originals linked |

**Consolidation candidates to be reviewed in detail in this refinement session:**
1. Agent format learning (Phase 4, Phase 5, Phase 6, Phase 7 findings)
2. SharePoint write capability (Phase 3, Phase 4, Phase 5 findings)
3. Markdown vs. ASPX grounding (Phase 5 detailed + Phase 7 platform research)

---

## Metadata and Provenance Model (Proposed Approach)

Every enduring research document will have:

### **Option A: Document Frontmatter (Recommended)**

At the top of each `.md` file:

```yaml
---
metadata:
  domain: sharepoint-platforms-capabilities
  subdomain: copilot-in-sharepoint
  artifact_type: field-note
  lifecycle_status: active
  research_date: 2026-07-15
  source_phases: [4]
  last_updated_phase: 4
  last_updated_date: 2026-07-20
  confidence_level: high
  external_sources:
    - url: https://learn.microsoft.com/en-us/copilot/...
      title: Copilot in SharePoint Preview
      accessed: 2026-07-15
      version: 2026-07 docs
  supersedes: null
  superseded_by: null
  related_experiments:
    - phase-4-task-8-deployment-evaluation
  related_phase_evidence:
    - ../../reports/phase-4-native-sharepoint-skills/EVID-PHASE4-TASK8-EXIT-GATE.md
---
```

**Pros:** Discoverable via YAML parsing; lives with the document; tools can extract it  
**Cons:** Makes files slightly harder to read

### **Option B: Separate Manifest**

Single `docs/research/_meta/.provenance.json`:

```json
{
  "documents": [
    {
      "path": "sharepoint-platforms-capabilities/copilot-in-sharepoint/field-note-agentassets-skill.md",
      "domain": "sharepoint-platforms-capabilities",
      "artifact_type": "field-note",
      "lifecycle_status": "active",
      "research_date": "2026-07-15",
      "source_phases": ["4"],
      ...
    }
  ]
}
```

**Pros:** Centralized; easy to parse and analyze  
**Cons:** Requires separate tool to navigate; single point of failure

### **Recommended: Hybrid Approach**

- **Frontmatter in each file:** Core metadata (domain, type, date, confidence, external sources)
- **Central manifest:** Rollup for automated indexing and cross-linking
- **README files:** Human-readable provenance summary for each subdomain

---

## How Phase is Preserved

Every moved research document will retain phase provenance via:

1. **Frontmatter metadata:** `source_phases: [3, 4]` if research spans phases
2. **Cross-links to phase evidence:** Links from research to authoritative phase reports
3. **Provenance manifest:** Central JSON record of all source phases
4. **File dating:** `research_date` and `last_updated_date` fields track when work was done

Example:

```markdown
# Agent Format Evolution

**Source:** Phase 4, Phase 5, Phase 6 research  
**Last Updated:** 2026-07-28

This document synthesizes agent format learning from multiple phases...

## Phase 4 Findings
[Learning Journal](../../reports/phase-4-native-sharepoint-skills/...)

## Phase 5 Findings
[EXIT-REPORT](../../reports/phase-5-sharepoint-knowledge-agent-pilot/EXIT-REPORT.md)

## Phase 6 Findings
[Remediation Bundle](../../reports/phase-6-task-0/task-0-migration-ledger-and-review-bundle.md)
```

---

## Navigation Patterns

### For Readers Asking "Where Is…?"

| Question | Navigation Path |
|---|---|
| "How do I create a native SharePoint skill?" | `docs/research/sharepoint-platforms-capabilities/copilot-in-sharepoint/` → spec + field notes |
| "What are the permission limits for agents?" | `docs/research/sharepoint-platforms-capabilities/content-permissions-governance/` |
| "How does document conversion work?" | `docs/research/structured-content-engineering/document-extraction-analysis/` |
| "What happened in Phase 4?" | `docs/reports/phase-4-native-sharepoint-skills/` |
| "Has Markdown grounding been tested?" | `docs/research/knowledge-discovery-retrieval/agent-grounding/` → field notes + synthesis |
| "What's the long-term vision?" | `docs/vision/master-roadmap/` + links to `strategic-planning-vision/` research |

### For Readers Asking "What Changed?"

- Phase closure documents are retained in `docs/reports/phase-N-*/`
- Each domain's `_meta/.provenance.json` shows phase provenance and last-update
- Each subdomain README lists files by artifact type and date
- A `docs/research/CHANGELOG.md` records major reorganizations (this is Session 2 artifact)

---

## What Changes; What Stays

### MOVED to Enduring Research Domains (68 files)
- Research summaries, field notes, synthesized findings from `docs/research/`
- Generalizable conclusions extracted from phase evidence
- Architectural patterns and design decisions
- Learning synthesized across phases

### REMAIN in Current Locations (95 files)
- Vision documents (`docs/vision/`) — no move
- Specifications and implementation plans (`docs/superpowers/specs/` and `plans/`) — no move
- Phase evidence (`docs/reports/phase-N-*/`) — no move
- Tool artifacts (`tools/phase-*/`) — no move
- Plugin documentation (`plugins/*/docs/`) — no move

### ARCHIVED to Legacy Subfolder (15 files)
- Pre-Phase-1 docx-to-content references → `docs/research/structured-content-engineering/legacy/`
- Marked with README explaining status and archival rationale

---

## Success Criteria

By end of Session 2 execution:

- ✅ 68 files moved to enduring research domains (organized by subject)
- ✅ 15 legacy files archived with explanatory README
- ✅ Phase provenance preserved in metadata (frontmatter + manifest)
- ✅ All inbound references updated and validated
- ✅ Domain README files created and indexed
- ✅ Master research index updated
- ✅ No files lost or content corrupted
- ✅ Navigation works for both subject-based and phase-based discovery

---

## Next Steps (Session 2)

1. ✅ Approve revised taxonomy and directory structure
2. Validate content-based classification (actual file reading)
3. Expand reference audit (CLAUDE.md, plugins, scripts, configs, tests)
4. Finalize metadata model choice (frontmatter, manifest, hybrid)
5. Execute migration using Git-aware operations
6. Validate all links and dependencies
7. Produce execution report

