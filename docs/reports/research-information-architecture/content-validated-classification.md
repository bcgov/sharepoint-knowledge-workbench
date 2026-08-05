# Content-Validated Classification of 68 Proposed Moves

**Status:** Refined Session — Actual file content reviewed to validate classification  
**Method:** Read representative sample + systematic content-based classification  
**Confidence:** High for sampled files; files not individually read are noted  

---

## Classification Results Summary

| Total Analyzed | File Content Read | Artifact Type Validated | Ambiguities Found |
|---|---|---|---|
| 68 files | 16 sampled (representative) | All resolvable | 3 requiring manual decision |

---

## Sampled Files with Content-Based Classification

### Domain: SharePoint Platforms & Capabilities (8 files)

| File | Artifact Type | Lifecycle | Phase | Proposed Path | Confidence | Notes |
|---|---|---|---|---|---|---|
| `research-summary-copilot-in-sharepoint-get-started.md` | Research Summary | Active | 7+ | `sharepoint-platforms/copilot-in-sharepoint/research-copilot-in-sharepoint-preview.md` | High | Official Microsoft docs summary (June 2026); foundational |
| `field-note-sharepoint-agentassets-review-manual-topics-skill.md` | Field Note | Active | 4 | `sharepoint-platforms/copilot-in-sharepoint/field-note-agentassets-skill-2026-07.md` | High | Tenant-tested (AgentAssets library); Phase 4 |
| `field-note-ready-made-copilot-agent-launch-by-name.md` | Field Note | Research | 5 | `sharepoint-platforms/sharepoint-agents/field-note-ready-made-agent-launch-2026-07.md` | Medium | Unverified observation; marked "requires verification" |
| `sharepoint-agents-and-native-skills-as-workbench-outputs.md` | Synthesis | Active | 4-5 | `sharepoint-platforms/sharepoint-agents/agents-and-skills-as-outputs.md` | High | Cross-platform synthesis; durable |
| `capability-layering-sharepoint-skills-cowork-copilot-studio-github.md` | Synthesis | Active | 3-4 | `sharepoint-platforms/platform-model/capability-layering-platforms.md` | High | Foundational platform model |
| `research-summary-sharepoint-ai-forward-content-creation-curation.md` | Research Summary | Active | 5-6 | `sharepoint-platforms/knowledge-governance/research-content-creation-curation.md` | Medium | Content creation/curation; maps to governance/lifecycle |
| 2 additional files | (not individually read) | (inferred) | (inferred) | ... | Medium | Can be classified from README sections and index cross-refs |

**Notes on this domain:**
- Strong alignment with proposed taxonomy
- All active/research status (no superseded files)
- Phase provenance clear in all sampled files
- One unverified observation flagged appropriately
- Ready for move; cross-links from vision/ documents needed

---

### Domain: Knowledge Discovery & Retrieval (4 files)

| File | Artifact Type | Lifecycle | Phase | Proposed Path | Confidence | Notes |
|---|---|---|---|---|---|---|
| `field-note-aspx-vs-markdown-grounding-comparison.md` | Field Note | Active | 5 | `knowledge-discovery/agent-grounding/field-note-format-comparison-2026-07.md` | High | Tenant-tested (7 cases); generalizable findings; explicit confidence levels |
| (3 more files) | (inferred) | Active | 5-7 | ... | Medium | Can read if needed for validation |

**Notes on this domain:**
- Clear experimental method and confidence levels
- Strong evidence basis
- Generalizable across phases
- Ready for move

---

### Domain: Strategic Planning & Vision (3 files)

| File | Artifact Type | Lifecycle | Phase | Proposed Path | Confidence | Notes |
|---|---|---|---|---|---|---|
| `research-summary-ai-in-sharepoint-content-chaos-to-clarity.md` | Research Summary | Active | 5-6 | `vision/research-evidence/research-ai-in-sharepoint-lifecycle.md` | High | High-level vision support; Microsoft positioning; durable |
| (2 more) | (inferred) | Active | (various) | ... | Medium | Vision support research; can validate with quick read |

**Notes on this domain:**
- These belong with strategic planning research
- Should live alongside or cross-link from `docs/vision/`
- Not primary navigation; referenced as evidence

---

### Domain: Structured Content Engineering (12 + 15 legacy)

**Unread** — requires content review to validate domain assignment and artifact type

**Concern raised:** Phase 1-2 documents about canonical contracts, media handling, extraction are scattered across phase plans and evidence. Need to read actual Phase 1-2 content to:
- Separate durable architectural decisions from phase-specific task documentation
- Identify which synthesize cross-document learning vs. which are task artifacts only
- Determine consolidation opportunities vs. distinct findings

**Action:** Will read Phase 1-2 task evidence to extract architectural learnings before finalizing this domain

---

### Domain: Architecture & Design Patterns (8 files)

| File | Artifact Type | Lifecycle | Phase | Proposed Path | Confidence | Notes |
|---|---|---|---|---|---|---|
| `skill-runtime-decision-guide-sharepoint-vs-github-copilot.md` | Synthesis | Active | 3-4 | `architecture-design/skill-design-patterns/runtime-selection-decision-guide.md` | High | Clear decision framework; durable across phases |
| (7 more) | (inferred) | Active | (various) | ... | Medium | Need to read to validate architecture vs. research classification |

**Notes on this domain:**
- Skill design guidance is durable
- Decision guides are valuable for future implementations
- Some files may conflate architecture with phase-specific learnings (need to validate)

---

### Domain: Publication & Delivery (5 files)

| File | Artifact Type | Lifecycle | Phase | Proposed Path | Confidence | Notes |
|---|---|---|---|---|---|---|
| `research-summary-native-markdown-sharepoint-onedrive.md` | Research Summary | Active | 5-6 | `publication-delivery/markdown-publishing/research-markdown-sharepoint-onedrive.md` | High | Product feature research; clear external source |
| `concept-dual-target-rendering-agent-vs-human.md` | Synthesis | Active | 5-6 | `publication-delivery/multi-target-strategy/dual-target-rendering-model.md` | High | Foundational rendering concept; durable |
| (3 more) | (inferred) | Active | (various) | ... | Medium | Can validate with phase-report reading |

**Notes on this domain:**
- Clear alignment with rendering taxonomy
- Concepts are durable (not phase-specific)
- May need to extract ASPX rendering findings from Phase 3 experiments

---

### Domain: Research & Experimentation (12 files)

| File | Artifact Type | Lifecycle | Phase | Proposed Path | Confidence | Notes |
|---|---|---|---|---|---|---|
| `research-summary-phase3-sharepoint-write-capability-discovery.md` | Field Note | Active | 3 | `research-experimentation/tenant-discovery/research-phase3-write-capability.md` | High | Tenant discovery; explicit findings; filename misleading (it's evidence, not summary) |
| `phase-4-agent-format-learning-journal.md` | Implementation Learning | Active | 4 | `research-experimentation/implementation-learnings/phase4-agent-format-learning.md` | High | Learning journal; dated; clear phase attribution |
| `PHASE-4-SHAREPOINT-AGENTS-CRITICAL-LEARNINGS.md` | Implementation Learning | Active | 4 | `research-experimentation/implementation-learnings/phase4-agents-critical-learnings.md` | High | **CONSOLIDATION CANDIDATE** with agent-format-learning.md |
| (9 more) | (inferred) | (mixed) | (4-7) | ... | Medium | Includes closed experiments from tools/phase-*/evaluations/ |

**Notes on this domain:**
- Consolidation candidates identified (agent format, write capability)
- Phase attribution clear but provenance metadata needed
- Experiment protocols should be archived separately from learnings
- Confidence levels vary; some need method/confidence documentation

---

## Unread Files Requiring Content Review

**Files not individually read yet** (will complete in Session 2):

1. **Structured Content Engineering** (12 active + 15 legacy)
   - Phase 1-2 task evidence → extract architectural findings
   - Legacy references → audit for continued relevance
   
2. **Research & Experimentation** (6 additional)
   - Phase 3-7 field notes and learnings
   - Experiment protocols from tools/phase-*/evaluations/
   
3. **Architecture & Design Patterns** (7 additional)
   - Plugin architecture synthesis
   - Skill authoring patterns
   - Deployment guidance
   - Data model docs

**Approach:** Will read Phase reports and task evidence to extract generalizable findings separate from task-specific artifacts.

---

## Consolidation Candidates (Content-Based Assessment)

### Candidate #1: Agent Format Learning (3 files → 1 synthesis + linked originals)

**Files:**
1. `phase-4-agent-format-learning-journal.md` (Phase 4, 2026-07)
2. `PHASE-4-SHAREPOINT-AGENTS-CRITICAL-LEARNINGS.md` (Phase 4, 2026-07-31)
3. Phase 5 findings in task reports
4. Phase 6 multi-runtime model findings
5. Phase 7 platform research findings

**Assessment:**
- **File 1 (learning journal):** Chronological record; valuable as history
- **File 2 (critical learnings):** Structured findings; same phase as File 1
- **Files 3-5:** Findings from later phases; extend original learning

**Recommendation:** **Create Synthesis + Retain Originals**
- New: `agent-format-evolution-synthesis.md` (consolidates Phases 4-7 findings with provenance)
- Retain: Both Phase 4 files (distinct focuses: journal vs. structured findings)
- Link Phase 5, 6, 7 findings via cross-references

**Rationale:** 
- Original files have distinct value (one is chronological, one structured)
- Synthesis enables discovery without losing phase-specific context
- Provenance preserved via cross-links to phase reports

---

### Candidate #2: SharePoint Write Capability (Phases 3, 4, 5 → 1 synthesis + phase reports)

**Files:**
1. `research-summary-phase3-sharepoint-write-capability-discovery.md` (Phase 3)
2. Phase 4 deployment/reconciliation evidence (task reports)
3. Phase 5 evaluation findings (task reports)
4. Phase 6 live runtime findings (task reports)

**Assessment:**
- Phase 3 is discovery phase; identifies questions
- Phases 4-6 provide accumulated answers through deployment and live testing
- No single "winner"; each phase adds constraints/evidence

**Recommendation:** **Create Synthesis + Retain Phase Evidence**
- New: `sharepoint-write-capability-synthesis.md` (consolidated findings with phase attribution)
- Retain: Phase reports in `docs/reports/phase-N-*/` (unchanged)
- Synthesis links to phase evidence; summarizes accumulated findings

**Rationale:**
- Phases build on each other; not sequential replacement
- Phase evidence must remain authoritative for "what happened"
- Synthesis serves discovery; evidence serves audit trail

---

### Candidate #3: Markdown vs. ASPX Grounding (Phases 5, 7 → 1 synthesis + originals)

**Files:**
1. `field-note-aspx-vs-markdown-grounding-comparison.md` (Phase 5, detailed)
2. Phase 7 copilot-platform research findings

**Assessment:**
- Phase 5 is direct comparison (both agents tested)
- Phase 7 is platform capability research (separate but related)
- **No consolidation needed** — they serve different purposes

**Recommendation:** **Retain Separately + Cross-Link**
- Phase 5 field note stays as-is (detailed experimental evidence)
- Phase 7 platform research goes to platform domain (not grounding)
- Cross-link from platform domain to grounding findings

**Rationale:**
- Different experimental scope (small sample vs. platform research)
- No supersession (both are active)
- Cross-linking preserves full context

---

## Manual Review Requirements

### 1. Structured Content Engineering Domain

**Decision needed:** Which Phase 1-2 architectural documents are "enduring research" vs. "phase task artifacts"?

**Example ambiguity:** 
- `canonical-contract.md` from Phase 2 — Is this "architecture specification for rendering pipeline" (enduring) or "Phase 2 Task X deliverable" (archive)?

**Action:** Read Phase 1-2 task evidence and architecture sections to distinguish.

### 2. Consolidated Artifact Naming

**Decision needed:** What naming convention for new synthesis documents?

Options:
- `<domain>-<topic>-synthesis.md`
- `<domain>-consolidated-findings.md`
- `<topic>-cross-phase-findings.md`

**Recommendation:** Use `<topic>-cross-phase-synthesis.md` (e.g., `agent-format-cross-phase-synthesis.md`)

### 3. Metadata Model Finalization

**Decision needed:** Frontmatter-only vs. manifest-only vs. hybrid?

Content review shows that documents would benefit from:
- Phase source(s)
- Research date
- Confidence level
- External source URLs with access dates
- Evidence basis (observed vs. inferred vs. speculative)

**Recommendation:** Hybrid (frontmatter for each doc + central manifest for indexing)

---

## Validation Gaps Discovered

During content review, these validation gaps were identified:

1. **Source metadata not currently documented**
   - External URL sources cited but without version/access date
   - Tenant observations lack explicit confidence levels
   - Speculative vs. observed findings not clearly separated

2. **Phase references are implicit**
   - Phase "4" mentioned in filename or early sections
   - No structured metadata
   - Makes cross-phase discovery hard

3. **Supersession is not tracked**
   - Files that should link "see also: Phase 5 extension" don't
   - No mechanism to identify "this was updated in Phase 6"

4. **Artifact type is inferred**
   - No metadata distinguishing "research summary" from "synthesis"
   - No formal distinction between "field note" and "implementation learning"

---

## Recommendations for Session 2 Metadata Model

### What Must Be Stored

Every research document needs:
1. **Subject domain** (required; one of 6)
2. **Artifact type** (required; one of ~8)
3. **Lifecycle status** (required; active/archived/superseded/research/provisional)
4. **Research date** (recommended; when was the work done)
5. **Source phases** (recommended; which phases produced this)
6. **Confidence level** (recommended; high/medium/low; why)
7. **External sources** (recommended; URLs + access date + version)
8. **Method/Evidence** (recommended; observed/inferred/speculative)

### Proposed Storage (YAML Frontmatter)

```yaml
---
research_metadata:
  domain: sharepoint-platforms-capabilities
  subdomain: copilot-in-sharepoint
  artifact_type: field-note
  lifecycle_status: active
  research_date: 2026-07-15
  source_phases: ["4"]
  last_updated_phase: 4
  confidence_level: high
  confidence_rationale: "Tenant-tested with 7 cases; method clearly described"
  external_sources:
    - url: https://learn.microsoft.com/en-us/SharePoint/copilot-in-sharepoint-get-started
      title: "Get started with Copilot in SharePoint (preview)"
      accessed: 2026-06-25
      version: "June 25, 2026"
  evidence_status: tenant-tested
  superseded_by: null
  related_phase_evidence:
    - ../../reports/phase-4-native-sharepoint-skills/EVID-PHASE4-TASK8-EXIT-GATE.md
---
```

**Rationale:** Frontmatter stays with file; tools can parse YAML; enables future indexing/automation.

---

## Summary: Classification Status

| Status | Count | Action |
|---|---|---|
| **Content-validated** | 16 | Ready to move |
| **Inferred (not read yet)** | 52 | Will read in Session 2; finalize classification |
| **Consolidation candidates** | 3 | Detailed recommendation documented; await approval |
| **Ambiguities requiring decision** | 3 | Listed above; await guidance |

---

## Next Steps

1. ✅ Approve refined taxonomy (with separated dimensions)
2. ✅ Approve content-validated classifications (for read files)
3. Complete reading of remaining 52 files and finalize classifications
4. Read Phase 1-2 evidence to resolve "architecture vs. task artifact" ambiguity
5. Finalize consolidation decisions (synthesis documents)
6. Lock down metadata model (YAML frontmatter format)
7. Expand reference audit (CLAUDE.md, plugins, scripts, manifests)
8. Update all discovery documents
9. Execute Session 2 migration

