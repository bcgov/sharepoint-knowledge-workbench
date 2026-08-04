# Current → Target Content Map — Proposed File Moves

**Status:** Planning phase — moves are proposed, not executed  
**Authorization:** Requires user approval before execution in Session 2  
**Mechanism:** Session 2 will use `research-path-migration.proposed.json` as the authoritative move manifest  

---

## Summary by Move Type

| Move Type | Count | Notes |
|---|---|---|
| **Move to eternal domain** | 68 | Research, field notes, synthesized findings moving from phase-folders or research/ to domain-org |
| **Retain in place** | 95 | Vision, superpowers specs/plans, architecture, reports, tools — no change |
| **Archive to legacy folder** | 15 | Historical docx-to-content references; stay accessible with README |
| **Consolidate** | 5 | Overlapping findings from different phases → single canonical document |
| **Total files in scope** | 218 | All research-like files analyzed |

---

## Move Categories

### Category A: Research Findings → Domain Homes (68 files moving)

#### SharePoint Platforms & Capabilities (8 files)

| Current Path | Target Path | Filename Change | Rationale |
|---|---|---|---|
| `docs/research/research-summary-copilot-in-sharepoint-get-started.md` | `docs/research/sharepoint-platforms-capabilities/copilot-in-sharepoint/research-copilot-in-sharepoint-preview.md` | Rename for clarity | Research summary, durable knowledge |
| `docs/research/sharepoint-agents-and-native-skills-as-workbench-outputs.md` | `docs/research/sharepoint-platforms-capabilities/sharepoint-agents/agents-and-skills-as-outputs.md` | Rename for conciseness | Core synthesis document |
| `docs/research/capability-layering-sharepoint-skills-cowork-copilot-studio-github.md` | `docs/research/sharepoint-platforms-capabilities/platform-model/capability-layering-across-platforms.md` | Reorganize hierarchy | Foundation platform doc |
| `docs/research/field-note-sharepoint-agentassets-review-manual-topics-skill.md` | `docs/research/sharepoint-platforms-capabilities/copilot-in-sharepoint/field-note-agentassets-skill-2026-07.md` | Standardize FN naming | Tenant-tested finding |
| `docs/research/field-note-ready-made-copilot-agent-launch-by-name.md` | `docs/research/sharepoint-platforms-capabilities/sharepoint-agents/field-note-ready-made-agent-launch-2026-07.md` | Standardize FN naming | Observation requiring verification |
| `research-summary-sharepoint-ai-forward-content-creation-curation.md` | `docs/research/sharepoint-platforms-capabilities/knowledge-governance/research-content-curation-lifecycle.md` | Move to governance subdomain | Lifecycle-focused finding |
| (3 extracted findings) | `docs/research/sharepoint-platforms-capabilities/content-permissions-governance/*` | New files | Extracted from phase evidence |
| (3 new synthesis docs) | `docs/research/sharepoint-platforms-capabilities/*/` | New homes | Cross-phase consolidation |

**Total: 8 files (3 moved, 5 new/consolidated)**

#### Structured Content Engineering (12 + 15 legacy files)

| Current | Target | Notes |
|---|---|---|
| `docs/architecture/docx-to-content-legacy-references/*` | `docs/research/structured-content-engineering/legacy/` | 15 legacy files; add README |
| (Extracted canonical-contract findings) | `docs/research/structured-content-engineering/content-models/` | New synthesis |
| (Extracted media-handling findings) | `docs/research/structured-content-engineering/media-processing/` | New synthesis |
| (Extracted extraction-defect findings) | `docs/research/structured-content-engineering/document-extraction/` | New synthesis |
| (Chunk strategy findings) | `docs/research/structured-content-engineering/chunking-strategy/` | New synthesis |

**Total: 12 files (3 moved, 9 new/consolidated) + 15 legacy archive**

#### Publication & Delivery (5 files)

| Current | Target | Notes |
|---|---|---|
| `docs/research/research-summary-native-markdown-sharepoint-onedrive.md` | `docs/research/publication-delivery/markdown-publishing/research-markdown-in-sharepoint-onedrive.md` | Move + rename |
| `docs/research/concept-dual-target-rendering-agent-vs-human.md` | `docs/research/publication-delivery/multi-target-strategy/dual-target-rendering-model.md` | Move + rename |
| (Extracted ASPX modern-page findings) | `docs/research/publication-delivery/sharepoint-publishing/aspx-modern-page-rendering-findings.md` | New synthesis |
| (Rendering architecture synthesis) | `docs/research/publication-delivery/rendering-architecture/` | New doc |
| (Publication map contracts) | `docs/research/publication-delivery/publication-lifecycle/` | New doc |

**Total: 5 files**

#### Knowledge Discovery & Retrieval (4 files)

| Current | Target | Notes |
|---|---|---|
| `docs/research/field-note-aspx-vs-markdown-grounding-comparison.md` | `docs/research/knowledge-discovery-retrieval/agent-grounding/field-note-format-comparison-2026-07.md` | Move + standardize naming |
| (Extracted grounding format findings) | `docs/research/knowledge-discovery-retrieval/agent-grounding/grounding-format-comparison-synthesis.md` | New synthesis |
| `research-summary-sharepoint-ai-forward-content-creation-curation.md` (curation portion) | `docs/research/knowledge-discovery-retrieval/knowledge-curation/content-health-and-lifecycle.md` | Extract to new domain |
| (Citation/citation-verification findings) | `docs/research/knowledge-discovery-retrieval/citation-and-verification/` | New doc |

**Total: 4 files**

#### Research & Experimentation (12 files)

| Current | Target | Notes |
|---|---|---|
| `docs/research/research-summary-phase3-sharepoint-write-capability-discovery.md` | `docs/research/research-experimentation/tenant-discovery/research-phase3-write-capability-2026-07.md` | Move + archive phase ref |
| `docs/research/phase-4-agent-format-learning-journal.md` | `docs/research/research-experimentation/implementation-learnings/field-note-agent-format-learning-2026-07.md` | Move + rename + archive phase |
| `docs/research/PHASE-4-SHAREPOINT-AGENTS-CRITICAL-LEARNINGS.md` | `docs/research/research-experimentation/implementation-learnings/phase4-critical-learnings-synthesis.md` | Move + rename + archive phase |
| (Consolidated from phases 4, 5, 6, 7) | `docs/research/research-experimentation/implementation-learnings/multi-phase-agent-format-consolidation.md` | New consolidation |
| (Consolidated tenant findings) | `docs/research/research-experimentation/tenant-discovery/consolidated-sharepoint-capabilities.md` | New synthesis |
| (Closed experiment protocols) | `docs/research/research-experimentation/experiments-closed/*/` | 6 new archives |
| (Platform evaluation findings) | `docs/research/research-experimentation/platform-evaluation/*/` | 2 new docs |

**Total: 12 files**

#### Architecture & Design Patterns (8 files)

| Current | Target | Notes |
|---|---|---|
| `docs/research/skill-runtime-decision-guide-sharepoint-vs-github-copilot.md` | `docs/research/architecture-design-patterns/skill-design-patterns/runtime-selection-decision-guide.md` | Move + rename |
| (Plugin architecture synthesis) | `docs/research/architecture-design-patterns/plugin-architecture/plugin-decomposition-patterns.md` | New synthesis |
| (Skill authoring patterns) | `docs/research/architecture-design-patterns/skill-design-patterns/skill-definition-standards.md` | New synthesis |
| (Deployment patterns) | `docs/research/architecture-design-patterns/deployment-patterns/provisioning-and-lifecycle.md` | New synthesis |
| (Data model synthesis) | `docs/research/architecture-design-patterns/data-models/schema-and-ontology-design.md` | New synthesis |
| (Extracted from phase 4, 5, 6 specs) | `docs/research/architecture-design-patterns/*/` | 3 new docs |

**Total: 8 files**

#### Strategic Planning & Vision (3 files)

| Current | Target | Notes |
|---|---|---|
| `docs/research/research-summary-ai-in-sharepoint-content-chaos-to-clarity.md` | `docs/vision/research-evidence/research-ai-in-sharepoint-content-lifecycle.md` | Move (links to vision/) |
| (Extracted phase-independent vision) | `docs/vision/research-evidence/` | New linking folder |

**Note:** Vision documents themselves (`docs/vision/*.md`) remain in place and are NOT moved. This is research *supporting* vision, not vision itself.

**Total: 3 files (moved as supporting evidence, linked from vision/)**

### Category B: No Move — Retain in Current Location (95 files)

#### Vision (9 files) — NO MOVE
```
docs/vision/README.md
docs/vision/master-initiative-plan-workstreams-and-phases.md
docs/vision/ai-assisted-structured-knowledge-workbench-broader-plan.md
docs/vision/ai-assisted-sharepoint-knowledge-workbench-government-vision.md
docs/vision/government-structured-knowledge-sharepoint-governance-vision-v2.md
docs/vision/key-unanswered-questions.md
docs/vision/plan-content-management-proposal.md
docs/vision/plan-copilot-knowledge-access-proposal.md
docs/vision/editing-workflow-options-for-external-review.md
docs/vision/open-question-ongoing-editing-and-agent-assisted-rendering-phase-placement.md
```

**Rationale:** Vision is authoritative direction; research supports but doesn't supplant it. Cross-links to research added during execution.

#### Architecture (3 files) — NO MOVE
```
docs/architecture/phase-4-5-target-architecture.md
docs/architecture/complete-plugin-skill-catalog-after-phase-9.md
docs/architecture/complete-plugin-skill-catalog-after-phase-9.json
```

**Rationale:** Forward-looking architecture references; cross-link to design-patterns research. Legacy folder reorganized under research.

#### Superpowers Specs (12 files) — NO MOVE
```
docs/superpowers/specs/2026-07-25-docx-to-content-plugin-design-v3-ammendments.md
docs/superpowers/specs/2026-07-25-docx-to-content-plugin-design.md
docs/superpowers/specs/2026-07-28-phase2-canonical-publication-contract-hardening-design.md
docs/superpowers/specs/2026-08-02-multi-document-destination-configuration-design.md
docs/superpowers/specs/2026-08-02-phase-5-ceis-grounding-prototype-design.md
docs/superpowers/specs/2026-08-02-sharepoint-agents-and-skills-plugin-design.md
docs/superpowers/specs/2026-08-03-phase-7-cowork-copilot-studio-desk-research-design.md
docs/superpowers/specs/phase-3-governed-sharepoint-knowledge-pilot-spec.md
docs/superpowers/specs/phase-3-tenant-capability-report.md
docs/superpowers/specs/phase-3-tenant-evidence-consumption-matrix.md
docs/superpowers/specs/phase-3-unresolved-decisions.md
docs/superpowers/specs/phase-4-5-core-knowledge-plugin-domain-refactoring-spec.md
+ 9 more phase specs (3, 4, 5, 6, 7, 8, 9)
```

**Rationale:** Specifications are phase-scoped; authoritative for their phase. Research cites and links to them. No move.

#### Superpowers Plans (20 files) — NO MOVE
```
docs/superpowers/plans/2026-07-25-docx-to-content-phase1-implementation-plan-v3-ammendments.md
docs/superpowers/plans/2026-07-25-docx-to-content-phase1-implementation-plan.md
docs/superpowers/plans/2026-07-28-docx-to-content-topic-grouping.md
docs/superpowers/plans/2026-07-28-phase2-canonical-publication-contract-hardening.md
docs/superpowers/plans/2026-07-29-aspx-modern-page-experiment.md
docs/superpowers/plans/2026-07-30-phase-3-governed-sharepoint-knowledge-pilot.md
docs/superpowers/plans/2026-07-30-phase3-governed-sharepoint-knowledge-pilot.md
docs/superpowers/plans/2026-07-31-phase-4-native-sharepoint-skills-pilot.md
docs/superpowers/plans/2026-08-01-phase-4-5-core-knowledge-plugin-domain-refactoring.md
docs/superpowers/plans/2026-08-02-multi-document-destination-configuration.md
docs/superpowers/plans/2026-08-02-phase-5-ceis-grounding-prototype.md
+ 9 more plans (phase scaffolds, etc.)
```

**Rationale:** Implementation plans are phase-durable; executed work with test ledgers and SDD. Stay with specs.

#### Superpowers Phase Evidence (14 files) — NO MOVE
```
docs/superpowers/plans/phase-4-5-evidence/wave-*.md (9 files)
docs/superpowers/plans/phase-4-5-evidence/wave-*.json (6 files)
docs/superpowers/plans/phase-6-tasks-1-12-evidence/task-*.md (7 files)
+ FUTURE-PHASE-PLANNING-INDEX.md
```

**Rationale:** Wave reports and task evidence are historical record. Retain for auditability.

#### Phase Reports (52 files) — NO MOVE
```
docs/reports/phase-4-native-sharepoint-skills/* (22 files)
docs/reports/phase-5-sharepoint-knowledge-agent-pilot/* (15 files)
docs/reports/phase-6-task-0/* (4 files)
docs/reports/phase-7-cowork-copilot-studio-evaluation/* (4 files)
docs/reports/phase-4-5-core-plugin-refactoring/* (5 files)
docs/reports/multi-document-destination-config/* (2 files)
```

**Rationale:** Phase evidence is durable; referenced by start-here.md and master roadmap. No move. Generalizable findings extracted to research domains.

#### Tools / Phase Artifacts (30 files) — NO MOVE
```
tools/phase-3-sharepoint-discovery/* (10 files)
tools/phase-4-native-sharepoint-skills/* (23 files)
tools/phase-5-sharepoint-knowledge-agent-pilot/* (22 files)
```

**Rationale:** Temporary implementation artifacts; stay in tools/. Findings extracted to research.

### Category C: Archive to Legacy Folder (15 files)

#### Legacy References → `docs/research/structured-content-engineering/legacy/`

```
docs/architecture/docx-to-content-legacy-references/
  ├── README.md
  ├── canonical-contract.md
  ├── content-authoring-guide.md
  ├── extraction-triggers.md
  ├── future-output-profiles.md
  ├── generated-elements.md
  ├── known-pandoc-gaps.md
  ├── pandoc-docx-setup.md
  ├── publication-map-contract.md
  ├── supported-markdown-profile.md
  ├── templates/components/README.md
  ├── templates/content/manual-topic.md
  ├── templates/examples/manual-topic-example.md
```

**Rationale:** These are pre-Phase-1 reference docs from when the pipeline was designed. Valuable historical context; not current docs. Archived with README explaining their status.

---

## Consolidation Candidates (5 files → 2 consolidated docs)

### Consolidation #1: Agent Format Learning (3 → 1)

| Source 1 | Source 2 | Source 3 | Consolidated Target |
|---|---|---|---|
| `docs/research/phase-4-agent-format-learning-journal.md` | `docs/research/PHASE-4-SHAREPOINT-AGENTS-CRITICAL-LEARNINGS.md` | Phase 5 & 6 findings (from reports) | `docs/research/research-experimentation/implementation-learnings/agent-format-and-evolution.md` |

**Method:** Extract agent-related findings from Phase 4, 5, 6, and 7 evidence; synthesize into one canonical doc with phase-provenance metadata.

### Consolidation #2: SharePoint Write Capability (2 → 1)

| Source 1 | Source 2 | Consolidated Target |
|---|---|---|
| `docs/research/research-summary-phase3-sharepoint-write-capability-discovery.md` | Phase 4, 5 findings on write behavior | `docs/research/research-experimentation/tenant-discovery/sharepoint-write-capability-synthesis.md` |

**Method:** Consolidate Phase 3, 4, 5, 6, 7 tenant-observed write constraints into one master reference.

**Note:** These consolidations are proposed for Session 2 decision-making. Actual consolidation requires careful merge of findings with phase attribution preserved.

---

## Files with Ambiguous Domains (Requires Review)

### `docs/research/EVID-PHASE4-TASK8-EXIT-GATE.md`

**Current:** `docs/research/`  
**Issue:** Phase-scoped evidence, not research  
**Proposed:** Move to `docs/reports/phase-4-native-sharepoint-skills/`  
**Rationale:** Phase evidence lives under phase folder, not research/

### `docs/reports/multi-document-destination-config/`

**Current:** `docs/reports/`  
**Issue:** Could belong in either phase-evidence or architecture  
**Proposed:** Keep in reports (multi-doc config is Phase 3/4 decision); add cross-link from `architecture-design/deployment-patterns/`  
**Rationale:** Decision scope spans phases; reports/ is appropriate

### `tools/phase-3-sharepoint-discovery/aspx-experiment/README.md`

**Current:** `tools/phase-3-sharepoint-discovery/`  
**Issue:** Experimental finding with durable relevance  
**Proposed:** Extract findings summary to `docs/research/publication-delivery/sharepoint-publishing/aspx-modern-page-experiment.md`; retain original in tools/  
**Rationale:** Tool artifact stays; finding moves to research

---

## Link Update Scope (Session 2)

The following inbound-link categories will be updated:

1. **Direct file references** in other `.md` files (relative and absolute paths)
2. **README index files** in each domain (new files will need docs/research/INDEX.md updates)
3. **Navigation/cross-reference links** (e.g., "see also: [other doc]()")
4. **start-here.md** references (if any point to research files)
5. **CLAUDE.md** references (research-guidance sections)
6. **Vision document cross-links** (vision/ files linking to research evidence)
7. **Phase report cross-links** (phase-evidence referencing moved research)

**Out of scope:** References inside commit messages, git history, or archived/deleted files.

---

## Success Verification (Session 2)

After all moves:
- ✅ 68 files in new domain homes
- ✅ 15 legacy files in archive with README
- ✅ 0 broken internal links
- ✅ All git mv operations recorded
- ✅ New domain README files updated with listings
- ✅ Provenance metadata added to each domain
- ✅ Redirect stubs in place at old locations (optional, for external refs)

---

## Appendix: Session 2 Execution Checklist

- [ ] User approves taxonomy + inventory + content map
- [ ] Generate `research-path-migration.proposed.json` with all 68 moves
- [ ] Run `reference-audit.md` scan (identify all inbound links)
- [ ] Create migration script (validated moves + reference updates)
- [ ] Dry-run migration (no commits yet)
- [ ] Verify all internal links in dry-run output
- [ ] Commit approved moves (git mv via script)
- [ ] Update all inbound references
- [ ] Verify new domain README files list files correctly
- [ ] Run link-validation checker
- [ ] Produce audit report (moves, reference updates, any manual fixes)
- [ ] Commit reference updates
- [ ] Remove any old-location stubs (or keep as redirects per policy)
- [ ] Final verification: git diff shows only approved moves + reference repairs

