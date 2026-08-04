# Reference-Impact Report — Review Point 2

Generated from `research-migration-manifest.json`'s `inbound_references` fields. **Not a complete systematic grep** — gathered opportunistically during content reading. Entries proposed for actual move/rename that have live inbound references require those references updated as part of migration execution; this report identifies which ones.

## Runtime dependencies (live plugin SKILL.md files — moving target breaks citation, requires code-adjacent update)

- **res-012** (`docs/research/research-summary-phase3-sharepoint-write-capability-discovery.md`, proposed: move → docs/research/research-experimentation, status: tentative)
  - plugins/sharepoint-content-publication/skills/publish-aspx-to-sharepoint/SKILL.md
  - plugins/structured-content-rendering/skills/render-sharepoint-aspx/SKILL.md
- **res-013** (`docs/research/phase-4-agent-format-learning-journal.md`, proposed: move → docs/research/research-experimentation, status: recommended)
  - plugins/sharepoint-agents-and-skills/skills/configure-sharepoint-agent-knowledge/SKILL.md

## Governance references (CLAUDE.md citations — highest-severity reference class)

- **res-014** (`docs/research/PHASE-4-SHAREPOINT-AGENTS-CRITICAL-LEARNINGS.md`, proposed: move → docs/research/research-experimentation, status: tentative)
  - CLAUDE.md (line 288, governing cross-reference: 'See docs/research/PHASE-4-SHAREPOINT-AGENTS-CRITICAL-LEARNINGS.md for full discovery path...')
- **vis-002** (`docs/vision/ai-assisted-structured-knowledge-workbench-broader-plan.md`, proposed: retain → docs/vision, status: recommended)
  - CLAUDE.md Section 0 (governs plugin-naming checks before new capability work)
- **vis-011** (`docs/vision/master-initiative-plan-workstreams-and-phases.md`, proposed: retain → docs/vision, status: approved)
  - CLAUDE.md (extensively, as 'the authoritative...master plan')

## Vision/architecture cross-references (docs/vision, docs/superpowers, docs/architecture citing corpus entries)

- **res-001** (`docs/research/README.md`, proposed: retain → docs/research, status: recommended)
  - docs/vision/README.md (line: 'docs/research/    product research and field notes')
- **res-002** (`docs/research/research-summary-copilot-in-sharepoint-get-started.md`, proposed: move → docs/research/sharepoint-platforms-capabilities, status: tentative)
  - not yet grepped with line numbers; docs/research/README.md links to it
- **res-003** (`docs/research/research-summary-native-markdown-sharepoint-onedrive.md`, proposed: move → docs/research/publication-delivery, status: tentative)
  - not yet grepped with line numbers
- **res-004** (`docs/research/research-summary-ai-in-sharepoint-content-chaos-to-clarity.md`, proposed: move → docs/research/strategic-planning-vision, status: tentative)
  - not yet grepped
- **res-005** (`docs/research/research-summary-sharepoint-ai-forward-content-creation-curation.md`, proposed: move → docs/research/knowledge-discovery-retrieval, status: tentative)
  - not yet grepped
- **res-006** (`docs/research/capability-layering-sharepoint-skills-cowork-copilot-studio-github.md`, proposed: move → docs/research/sharepoint-platforms-capabilities, status: tentative)
  - docs/vision/master-initiative-plan-workstreams-and-phases.md (multiple, not yet line-numbered)
- **res-007** (`docs/research/sharepoint-agents-and-native-skills-as-workbench-outputs.md`, proposed: move → docs/research/sharepoint-platforms-capabilities, status: tentative)
  - not yet grepped
- **res-008** (`docs/research/skill-runtime-decision-guide-sharepoint-vs-github-copilot.md`, proposed: move → docs/research/architecture-design-patterns, status: tentative)
  - not yet grepped
- **res-009** (`docs/research/field-note-sharepoint-agentassets-review-manual-topics-skill.md`, proposed: move → docs/research/sharepoint-platforms-capabilities, status: recommended)
  - tools/phase-3-sharepoint-discovery/phase-3-0-tenant-discovery.ps1 (script comment)
  - research-summary-phase3-sharepoint-write-capability-discovery.md (cites this file)
- **res-010** (`docs/research/field-note-ready-made-copilot-agent-launch-by-name.md`, proposed: move → docs/research/sharepoint-platforms-capabilities, status: recommended)
  - not yet grepped
- **res-011** (`docs/research/field-note-aspx-vs-markdown-grounding-comparison.md`, proposed: move → docs/research/knowledge-discovery-retrieval, status: recommended)
  - docs/vision/key-unanswered-questions.md
  - docs/vision/master-initiative-plan-workstreams-and-phases.md (2 locations)
  - docs/superpowers/plans/phase-6-multi-runtime-capability-model-plan-scaffold.md
  - docs/research/concept-dual-target-rendering-agent-vs-human.md (cites finding 4 as tenant-tested support)
- **res-012** (`docs/research/research-summary-phase3-sharepoint-write-capability-discovery.md`, proposed: move → docs/research/research-experimentation, status: tentative)
  - docs/vision/master-initiative-plan-workstreams-and-phases.md (2 locations)
  - docs/superpowers/plans/phase-6-multi-runtime-capability-model-plan-scaffold.md (2 locations)
  - docs/superpowers/plans/2026-07-29-aspx-modern-page-experiment.md (4 locations, including a git add instruction)
  - docs/superpowers/specs/2026-08-02-phase-5-ceis-grounding-prototype-design.md
  - docs/superpowers/specs/phase-3-tenant-capability-report.md (2 locations)
  - tools/phase-3-sharepoint-discovery/phase-3-0-tenant-discovery.ps1 (script comment + EvidenceSource string, 3 occurrences)
- **res-013** (`docs/research/phase-4-agent-format-learning-journal.md`, proposed: move → docs/research/research-experimentation, status: recommended)
  - PHASE-4-SHAREPOINT-AGENTS-CRITICAL-LEARNINGS.md
- **res-014** (`docs/research/PHASE-4-SHAREPOINT-AGENTS-CRITICAL-LEARNINGS.md`, proposed: move → docs/research/research-experimentation, status: tentative)
  - EVID-PHASE4-TASK8-EXIT-GATE.md
  - plugins/sharepoint-agents-and-skills/evaluations/common/NATIVE-SHAREPOINT-EXECUTION-RUNBOOK.md
  - docs/superpowers/plans/phase-6-tasks-1-12-evidence/task-1-brainstorming-and-task-2-inventory.md
- **res-015** (`docs/research/EVID-PHASE4-TASK8-EXIT-GATE.md`, proposed: archive → docs/reports/phase-4-native-sharepoint-skills, status: recommended)
  - PHASE-4-SHAREPOINT-AGENTS-CRITICAL-LEARNINGS.md
- **res-016** (`docs/research/concept-dual-target-rendering-agent-vs-human.md`, proposed: move → docs/research/publication-delivery, status: recommended)
  - not yet grepped with line numbers
- **arch-002** (`docs/architecture/docx-to-content-legacy-references/canonical-contract.md`, proposed: move → docs/research/structured-content-engineering/legacy, status: recommended)
  - docs/superpowers/specs/2026-08-02-multi-document-destination-configuration-design.md
- **arch-005** (`docs/architecture/docx-to-content-legacy-references/future-output-profiles.md`, proposed: move → docs/research/structured-content-engineering/legacy, status: tentative)
  - architecture.md (repository-root file)
- **diag-000** (`docs/diagrams/README.md`, proposed: retain → docs/diagrams, status: recommended)
  - docs/vision/editing-workflow-options-for-external-review.md
  - docs/vision/master-initiative-plan-workstreams-and-phases.md
  - .agent/rules/plugin-architecture-policy.md (references docs/diagrams/workflows/discovery.mmd — THIS PATH DOES NOT EXIST in this repo's docs/diagrams/, no workflows/ subfolder present; either a stale reference or describes an unimplemented expected structure)
- **diag-006** (`docs/diagrams/06-editing-workflow-hybrid-option.mmd`, proposed: move → docs/vision, status: recommended)
  - docs/vision/editing-workflow-options-for-external-review.md
- **diag-009** (`docs/diagrams/09-phase6-5-ongoing-authoring-and-republishing-loop.mmd`, proposed: move → docs/vision, status: recommended)
  - docs/vision/master-initiative-plan-workstreams-and-phases.md
- **vis-009** (`docs/vision/editing-workflow-options-for-external-review.md`, proposed: retain → docs/vision, status: recommended)
  - docs/diagrams/README.md
- **vis-010** (`docs/vision/open-question-ongoing-editing-and-agent-assisted-rendering-phase-placement.md`, proposed: retain → docs/vision, status: recommended)
  - docs/diagrams/09-phase6-5-ongoing-authoring-and-republishing-loop.mmd
  - docs/diagrams/README.md
- **vis-011** (`docs/vision/master-initiative-plan-workstreams-and-phases.md`, proposed: retain → docs/vision, status: approved)
  - docs/research/research-summary-phase3-sharepoint-write-capability-discovery.md (2 locations, confirmed earlier this session)
  - docs/research/field-note-aspx-vs-markdown-grounding-comparison.md (2 locations, confirmed earlier this session)
  - docs/superpowers/plans/phase-6-multi-runtime-capability-model-plan-scaffold.md (2 locations)
  - docs/diagrams/README.md

## Stale/broken references found (documented, not fixed)

| File | Broken reference | Issue |
|---|---|---|
| `.agent/rules/plugin-architecture-policy.md` | `docs/diagrams/workflows/discovery.mmd` | Path does not exist -- no workflows/ subfolder in this repo's docs/diagrams/. Either a stale reference (copied from a template or another repo) or evidence of an unbuilt intended structure. |
| `docs/vision/vision-original.md (vis-006)` | `docs/superpowers/specs/diagrams/docx-to-content-workflow.png` | Under the excluded docs/superpowers/ tree; existence not verified this session. |

## Completeness caveat

This report reflects references discovered opportunistically while reading each entry's content, NOT a systematic `grep -rn` pass across the full repository. A complete reference audit (with line numbers, all categories, reconciled counts) is required before migration EXECUTION — specifically before any `recommended`/`tentative` entry is promoted to `approved` for a move/rename operation. This gap is disclosed, not resolved.