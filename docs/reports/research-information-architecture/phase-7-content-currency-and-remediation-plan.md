# Phase 7 Content Currency and Remediation Plan

**Status:** Generated from `research-migration-manifest.json`. This document is a report,
not a source of truth — the manifest's `contentCurrency`/`recommendedContentAction`/etc.
fields are authoritative; this file summarizes them for human review.

**Scope:** Same 56-entry corpus as the migration manifest (`docs/research/`,
`docs/architecture/`, `docs/diagrams/`, `docs/vision/`, `docs/` root). `docs/superpowers/`
and `docs/reports/` excluded.

**What this is NOT:** No source document was edited to produce this report. Every
assessment below is a recommendation requiring separate approval (`contentUpdateApproval:
pending` on every entry) before any content changes are made. Content updates, if approved,
should land as their own commit(s), separate from the file-move/rename/reference migration.

## Distinction Applied

- **Historically accurate** — correct record of what was known at the time; not rewritten to
  reflect later knowledge.
- **Currently authoritative** — intended to guide current work; should reflect Phase 7 findings.
- **Superseded** — retained for provenance, explicitly linked to newer authority.
- **Cross-phase candidate** — better served by a new synthesis than repeated edits across
  several historical documents.
- **Uncertain** — this session's reading was insufficient to responsibly assess currency;
  flagged rather than guessed.

## 1. Current Through Phase 7 (no action needed)

**11 entries**

| Source Path | Currency | Validated Through Phase | Action |
|---|---|---|---|
| `docs/research/skill-runtime-decision-guide-sharepoint-vs-github-copilot.md` | current | 4 | cross-link |
| `docs/architecture/docx-to-content-legacy-references/README.md` | current | 4 | none |
| `docs/architecture/docx-to-content-legacy-references/generated-elements.md` | current | 1 | none |
| `docs/architecture/docx-to-content-legacy-references/templates/components/README.md` | current | 1 | none |
| `docs/architecture/docx-to-content-legacy-references/templates/content/manual-topic.md` | current | 1 | none |
| `docs/architecture/docx-to-content-legacy-references/templates/examples/manual-topic-example.md` | current | 1 | none |
| `docs/architecture/complete-plugin-skill-catalog-after-phase-9.md` | current | 6 | cross-link |
| `docs/architecture/complete-plugin-skill-catalog-after-phase-9.json` | current | 6 | cross-link |
| `docs/architecture/validate_plugin_skill_catalog.py` | current | 6 | none |
| `docs/diagrams/09-phase6-5-ongoing-authoring-and-republishing-loop.mmd` | current | 6.5 | none |
| `docs/vision/open-question-ongoing-editing-and-agent-assisted-rendering-phase-placement.md` | current | 5 | cross-link |

- **`res-008`** (skill-runtime-decision-guide-sharepoint-vs-github-copilot.md): Decision-tree guidance is process-level, not fact-level — remains applicable; would benefit from a cross-link to Phase 6's actual runtime-selection outcomes as a worked example, not a rewrite.
- **`arch-001`** (README.md): The folder's own index; accurately describes its own contents as of Phase 4.5.
- **`arch-006`** (generated-elements.md): Small, stable reference table; companion to arch-003.
- **`arch-011`** (README.md): Small, self-contained authoring-syntax convention; unlikely to have changed.
- **`arch-012`** (manual-topic.md): Reusable template; frontmatter schema is a candidate input to the wider metadata-model design question but the template itself is not stale.
- **`arch-013`** (manual-topic-example.md): Companion example to arch-012.
- **`arch-015`** (complete-plugin-skill-catalog-after-phase-9.md): Live tracking artifact, actively regenerated as Phase 6/9 progress — not something to freeze as historical, but its exact currency relative to the latest Phase 6 state was not independently re-verified this session.
- **`arch-016`** (complete-plugin-skill-catalog-after-phase-9.json): Same as arch-015 — machine-readable half of the same artifact.
- **`arch-017`** (validate_plugin_skill_catalog.py): Executable validator, correctness is defined by whether it still passes against its siblings, not by 'currency' in the documentation sense.
- **`diag-009`** (09-phase6-5-ongoing-authoring-and-republishing-loop.mmd): Explicitly 'NOT TRIGGERED, NOT AUTHORIZED' — this status is still accurate as of Phase 7 close per start-here.md (Phase 6.5 has not been triggered).
- **`vis-010`** (open-question-ongoing-editing-and-agent-assisted-rendering-phase-placement.md): Resolution itself remains valid (Phase 6.5 still not triggered) — needs indexing/cross-linking, not content changes.

## 2. Requires Substantive Update

**10 entries**

| Source Path | Currency | Validated Through Phase | Action |
|---|---|---|---|
| `docs/research/README.md` | partially-current | 6 | update |
| `docs/research/capability-layering-sharepoint-skills-cowork-copilot-studio-github.md` | partially-current | 4 | update |
| `docs/research/concept-dual-target-rendering-agent-vs-human.md` | partially-current | 5 | update |
| `docs/architecture/docx-to-content-legacy-references/future-output-profiles.md` | uncertain | 1 | update |
| `docs/diagrams/README.md` | partially-current | 6.5 | update |
| `docs/vision/README.md` | partially-current | 6 | update |
| `docs/vision/ai-assisted-structured-knowledge-workbench-broader-plan.md` | partially-current | 6 | update |
| `docs/vision/ai-assisted-sharepoint-knowledge-workbench-government-vision.md` | partially-current | 6 | update |
| `docs/vision/key-unanswered-questions.md` | partially-current | 5 | update |
| `docs/vision/master-initiative-plan-workstreams-and-phases.md` | uncertain | None | update |

- **`res-001`** (README.md): Index/vision section predates Phase 7 close; reading paths and 'near-term priorities' list have not been re-checked against Phase 5-7 actual outcomes.
- **`res-006`** (capability-layering-sharepoint-skills-cowork-copilot-studio-github.md): Foundational synthesis, but the Phase 6 multi-runtime finding is a real extension/refinement of its core claims, not just an application of them — the abstract model this document describes was tested and found to have a real behavioral gap between runtimes.
- **`res-016`** (concept-dual-target-rendering-agent-vs-human.md): Foundational architecture concept later actually implemented (not just theorized) in Phase 6 — the concept document should point forward to its own realization as evidence the model works, rather than remain purely speculative in tone.
- **`arch-005`** (future-output-profiles.md): Largest legacy file; explicitly forward-looking survey of rendering targets — Phase 6 partially realized one of the targets it likely surveys. Needs a full read before an update can be scoped precisely.
- **`diag-000`** (README.md): Accurately describes the 10 files that exist, but the broken external reference and the 06-09 vision-document pairings this session found are not reflected in the README's own text.
- **`vis-001`** (README.md): Confirmed incompleteness: the authority table is missing 2 real files. Should be corrected as part of or alongside this IA effort.
- **`vis-002`** (ai-assisted-structured-knowledge-workbench-broader-plan.md): Highest-authority vision document; its currency banner should be refreshed to Phase 7's actual closing state rather than left at its Phase 6-era wording.
- **`vis-003`** (ai-assisted-sharepoint-knowledge-workbench-government-vision.md): Tier-2 authority document with the same staleness class as vis-002.
- **`vis-005`** (key-unanswered-questions.md): This is exactly the kind of 'open decision register' whose currency depends on marking items resolved as findings land — worth a dedicated resolution-sweep, not a full rewrite.
- **`vis-011`** (master-initiative-plan-workstreams-and-phases.md): HIGHEST-PRIORITY UNCERTAIN ITEM: this is the single most-cited, highest-authority planning document in the whole corpus (10+ confirmed inbound references including CLAUDE.md), yet this session's read of it was the shallowest relative to its length and importance. A full read specifically checking Phase 7 alignment should happen before any currency claim is trusted for this file.

## 3. Requires Only a Status Note or Cross-Link

**20 entries**

| Source Path | Currency | Validated Through Phase | Action |
|---|---|---|---|
| `docs/research/research-summary-copilot-in-sharepoint-get-started.md` | historical | None | add-status-note |
| `docs/research/research-summary-native-markdown-sharepoint-onedrive.md` | historical | None | add-status-note |
| `docs/research/research-summary-ai-in-sharepoint-content-chaos-to-clarity.md` | historical | None | add-status-note |
| `docs/research/research-summary-sharepoint-ai-forward-content-creation-curation.md` | historical | None | add-status-note |
| `docs/research/sharepoint-agents-and-native-skills-as-workbench-outputs.md` | partially-current | 5 | cross-link |
| `docs/research/skill-runtime-decision-guide-sharepoint-vs-github-copilot.md` | current | 4 | cross-link |
| `docs/research/field-note-aspx-vs-markdown-grounding-comparison.md` | historical | 5 | cross-link |
| `docs/research/phase-4-agent-format-learning-journal.md` | historical | 4 | add-status-note |
| `docs/research/PHASE-4-SHAREPOINT-AGENTS-CRITICAL-LEARNINGS.md` | partially-current | 4 | add-status-note |
| `docs/architecture/docx-to-content-legacy-references/content-authoring-guide.md` | uncertain | 1 | add-status-note |
| `docs/architecture/docx-to-content-legacy-references/extraction-triggers.md` | uncertain | 1 | add-status-note |
| `docs/architecture/docx-to-content-legacy-references/supported-markdown-profile.md` | uncertain | 1 | add-status-note |
| `docs/architecture/complete-plugin-skill-catalog-after-phase-9.md` | current | 6 | cross-link |
| `docs/architecture/complete-plugin-skill-catalog-after-phase-9.json` | current | 6 | cross-link |
| `docs/diagrams/06-editing-workflow-hybrid-option.mmd` | historical | 3 | add-status-note |
| `docs/diagrams/07-publisher-triggered-render-workflow.mmd` | historical | 3 | add-status-note |
| `docs/diagrams/08-editor-submission-and-approval-workflow.mmd` | historical | 3 | add-status-note |
| `docs/implementation-baseline.md` | historical | 1 | add-status-note |
| `docs/vision/editing-workflow-options-for-external-review.md` | uncertain | 3 | add-status-note |
| `docs/vision/open-question-ongoing-editing-and-agent-assisted-rendering-phase-placement.md` | current | 5 | cross-link |

- **`res-002`** (research-summary-copilot-in-sharepoint-get-started.md): Dated external-source summary; historically accurate as a record of what Microsoft published on that date. Should carry an explicit 'verify current status before relying on licensing/limit claims' note rather than be silently treated as still-current.
- **`res-003`** (research-summary-native-markdown-sharepoint-onedrive.md): Same class as res-002 — dated external announcement summary.
- **`res-004`** (research-summary-ai-in-sharepoint-content-chaos-to-clarity.md): Dated conference-presentation summary; the government-controls list within it overlaps res-001's own list — worth a cross-link note rather than independent maintenance of two copies.
- **`res-005`** (research-summary-sharepoint-ai-forward-content-creation-curation.md): Dated blog-post summary, same class as res-002/003/004.
- **`res-007`** (sharepoint-agents-and-native-skills-as-workbench-outputs.md): Overlaps res-006 (same consolidation group) — recommend resolving both together via a shared update or synthesis rather than editing independently.
- **`res-008`** (skill-runtime-decision-guide-sharepoint-vs-github-copilot.md): Decision-tree guidance is process-level, not fact-level — remains applicable; would benefit from a cross-link to Phase 6's actual runtime-selection outcomes as a worked example, not a rewrite.
- **`res-011`** (field-note-aspx-vs-markdown-grounding-comparison.md): High-value, well-evidenced Phase 5 field note; recommend adding forward cross-links to later related findings rather than editing the original evidence.
- **`res-013`** (phase-4-agent-format-learning-journal.md): Working journal, correctly historical in form; a forward note pointing to the Phase 6 formalization would help readers without rewriting the journal itself.
- **`res-014`** (PHASE-4-SHAREPOINT-AGENTS-CRITICAL-LEARNINGS.md): Real tension: this file functions as BOTH historical evidence AND (via CLAUDE.md's direct citation) current governing guidance. Recommend adding an explicit status update to the file's own header noting Task 8 was subsequently completed (see EVID-PHASE4-TASK8-EXIT-GATE.md) rather than leaving it reading as still in-progress.
- **`arch-003`** (content-authoring-guide.md): Per folder README this is NOT one of the 2 superseded files, but written for the pre-decomposition combined plugin — marked uncertain rather than assumed still-accurate.
- **`arch-004`** (extraction-triggers.md): Decision framework partially overtaken by events (the Phase 4.5 extraction it hypothesizes about already happened for some workstreams).
- **`arch-010`** (supported-markdown-profile.md): Same uncertainty class as arch-003/004 — plausibly still accurate, not independently verified.
- **`arch-015`** (complete-plugin-skill-catalog-after-phase-9.md): Live tracking artifact, actively regenerated as Phase 6/9 progress — not something to freeze as historical, but its exact currency relative to the latest Phase 6 state was not independently re-verified this session.
- **`arch-016`** (complete-plugin-skill-catalog-after-phase-9.json): Same as arch-015 — machine-readable half of the same artifact.
- **`diag-006`** (06-editing-workflow-hybrid-option.mmd): Speculative and explicitly not-selected; a forward note confirming what Phase 3 actually did (for contrast) would help readers, without rewriting the candidate diagram itself.
- **`diag-007`** (07-publisher-triggered-render-workflow.mmd): Same as diag-006 — paired diagram.
- **`diag-008`** (08-editor-submission-and-approval-workflow.mmd): Same as diag-006/007.
- **`root-001`** (implementation-baseline.md): Task 0 reconnaissance record using pre-rename path names (sourcedocuments/, output/) — a brief note pointing to the current intake/runs/ names would help readers without rewriting the historical record itself.
- **`vis-009`** (editing-workflow-options-for-external-review.md): Genuinely uncertain whether this remains an open question or was quietly resolved elsewhere; also confirmed missing from README's authority table.
- **`vis-010`** (open-question-ongoing-editing-and-agent-assisted-rendering-phase-placement.md): Resolution itself remains valid (Phase 6.5 still not triggered) — needs indexing/cross-linking, not content changes.

## 4. Should Remain Unchanged as Historical Evidence

**10 entries**

| Source Path | Currency | Validated Through Phase | Action |
|---|---|---|---|
| `docs/research/field-note-sharepoint-agentassets-review-manual-topics-skill.md` | historical | 4 | none |
| `docs/research/field-note-ready-made-copilot-agent-launch-by-name.md` | historical | 5 | none |
| `docs/research/EVID-PHASE4-TASK8-EXIT-GATE.md` | historical | 4 | none |
| `docs/architecture/phase-4-5-target-architecture.md` | historical | 4.5 | none |
| `docs/diagrams/01-phase1-overview.mmd` | historical | 1 | none |
| `docs/diagrams/02-analyze-and-confirm.mmd` | historical | 1 | none |
| `docs/diagrams/03-create-canonical-content.mmd` | historical | 1 | none |
| `docs/diagrams/04-generate-and-render.mmd` | historical | 1 | none |
| `docs/diagrams/05-validation-and-evidence.mmd` | historical | 1 | none |
| `docs/diagrams/high-level.mmd` | historical | 1 | none |

- **`res-009`** (field-note-sharepoint-agentassets-review-manual-topics-skill.md): Empirical tenant field note; correctly scoped as a record of what was observed at the time. The file's own text already flags that preview behavior may differ across tenants/time — no rewrite needed.
- **`res-010`** (field-note-ready-made-copilot-agent-launch-by-name.md): Confirmed finding, dated, self-contained — no later phase is known to have revisited this specific behavior.
- **`res-015`** (EVID-PHASE4-TASK8-EXIT-GATE.md): Phase evidence, correctly frozen at its own completion point.
- **`arch-014`** (phase-4-5-target-architecture.md): Self-dated, self-described as a deliberately-preserved historical record with a pointer to current names elsewhere.
- **`diag-001`** (01-phase1-overview.mmd): Accurately depicts completed, accepted Phase 1 flow.
- **`diag-002`** (02-analyze-and-confirm.mmd): Same as diag-001.
- **`diag-003`** (03-create-canonical-content.mmd): Same as diag-001.
- **`diag-004`** (04-generate-and-render.mmd): Same as diag-001.
- **`diag-005`** (05-validation-and-evidence.mmd): Same as diag-001.
- **`diag-010`** (high-level.mmd): Parent/overview companion to diag-001, same currency.

## 5. Superseded but Retained

**3 entries**

| Source Path | Currency | Validated Through Phase | Action |
|---|---|---|---|
| `docs/architecture/docx-to-content-legacy-references/canonical-contract.md` | superseded | 2 | archive |
| `docs/architecture/docx-to-content-legacy-references/publication-map-contract.md` | superseded | 2 | archive |
| `docs/vision/government-structured-knowledge-sharepoint-governance-vision-v2.md` | superseded | None | archive |

- **`arch-002`** (canonical-contract.md): Confirmed superseded by its own folder's README; no content update needed, only relocation/archival treatment.
- **`arch-009`** (publication-map-contract.md): Confirmed superseded per folder README, same class as arch-002.
- **`vis-004`** (government-structured-knowledge-sharepoint-governance-vision-v2.md): Confirmed superseded by both self-declaration and folder README; the repo's own recommended action (extract unique content, then archive) was never executed.

## 6. Archival Candidates (non-superseded — stubs, empty placeholders)

**5 entries**

| Source Path | Currency | Validated Through Phase | Action |
|---|---|---|---|
| `docs/architecture/docx-to-content-legacy-references/known-pandoc-gaps.md` | uncertain | None | archive |
| `docs/architecture/docx-to-content-legacy-references/pandoc-docx-setup.md` | uncertain | None | archive |
| `docs/vision/vision-original.md` | historical | None | archive |
| `docs/vision/plan-content-management-proposal.md` | historical | None | archive |
| `docs/vision/plan-copilot-knowledge-access-proposal.md` | historical | None | archive |

- **`arch-007`** (known-pandoc-gaps.md): Empty 3-line placeholder stub; recommend explicit delete-or-complete decision rather than migrating empty content forward.
- **`arch-008`** (pandoc-docx-setup.md): Same as arch-007 — empty stub, likely fully superseded by DEPENDENCIES.md.
- **`vis-006`** (vision-original.md): README's own tier-5 disposition; historical origin document, correctly frozen.
- **`vis-007`** (plan-content-management-proposal.md): Same tier-5 disposition as vis-006.
- **`vis-008`** (plan-copilot-knowledge-access-proposal.md): Same tier-5 disposition as vis-006/007.

## 7. Unresolved / Uncertain (flagged, not guessed)

**9 entries**

| Source Path | Currency | Validated Through Phase | Action |
|---|---|---|---|
| `docs/research/research-summary-phase3-sharepoint-write-capability-discovery.md` | uncertain | None | none |
| `docs/architecture/docx-to-content-legacy-references/content-authoring-guide.md` | uncertain | 1 | add-status-note |
| `docs/architecture/docx-to-content-legacy-references/extraction-triggers.md` | uncertain | 1 | add-status-note |
| `docs/architecture/docx-to-content-legacy-references/future-output-profiles.md` | uncertain | 1 | update |
| `docs/architecture/docx-to-content-legacy-references/known-pandoc-gaps.md` | uncertain | None | archive |
| `docs/architecture/docx-to-content-legacy-references/pandoc-docx-setup.md` | uncertain | None | archive |
| `docs/architecture/docx-to-content-legacy-references/supported-markdown-profile.md` | uncertain | 1 | add-status-note |
| `docs/vision/editing-workflow-options-for-external-review.md` | uncertain | 3 | add-status-note |
| `docs/vision/master-initiative-plan-workstreams-and-phases.md` | uncertain | None | update |

- **`res-012`** (research-summary-phase3-sharepoint-write-capability-discovery.md): Raw evidence log, explicitly distinct from its own synthesized companion (phase-3-tenant-capability-report.md, excluded from this corpus). Marked uncertain rather than guessing its currency without checking the file's own revision history.
- **`arch-003`** (content-authoring-guide.md): Per folder README this is NOT one of the 2 superseded files, but written for the pre-decomposition combined plugin — marked uncertain rather than assumed still-accurate.
- **`arch-004`** (extraction-triggers.md): Decision framework partially overtaken by events (the Phase 4.5 extraction it hypothesizes about already happened for some workstreams).
- **`arch-005`** (future-output-profiles.md): Largest legacy file; explicitly forward-looking survey of rendering targets — Phase 6 partially realized one of the targets it likely surveys. Needs a full read before an update can be scoped precisely.
- **`arch-007`** (known-pandoc-gaps.md): Empty 3-line placeholder stub; recommend explicit delete-or-complete decision rather than migrating empty content forward.
- **`arch-008`** (pandoc-docx-setup.md): Same as arch-007 — empty stub, likely fully superseded by DEPENDENCIES.md.
- **`arch-010`** (supported-markdown-profile.md): Same uncertainty class as arch-003/004 — plausibly still accurate, not independently verified.
- **`vis-009`** (editing-workflow-options-for-external-review.md): Genuinely uncertain whether this remains an open question or was quietly resolved elsewhere; also confirmed missing from README's authority table.
- **`vis-011`** (master-initiative-plan-workstreams-and-phases.md): HIGHEST-PRIORITY UNCERTAIN ITEM: this is the single most-cited, highest-authority planning document in the whole corpus (10+ confirmed inbound references including CLAUDE.md), yet this session's read of it was the shallowest relative to its length and importance. A full read specifically checking Phase 7 alignment should happen before any currency claim is trusted for this file.

## Priority Flags

Two items warrant attention before any other content work:

1. **`vis-011` (master-initiative-plan-workstreams-and-phases.md)** — the single
   highest-authority, most-cited document in the entire corpus (10+ confirmed inbound
   references, including CLAUDE.md). This session read only its first ~15 lines. Its
   `contentCurrency` is marked `uncertain` deliberately — a full read specifically checking
   Phase 7 alignment is needed before any currency claim about it can be trusted.
2. **`vis-001` (docs/vision/README.md)** — its own document-authority table is confirmed
   incomplete (omits `vis-009` and `vis-010`). This is a factual defect independent of the
   wider IA question and could be fixed on its own.

## Consolidation-Adjacent Content Work

Two groups where `recommendedContentAction` points toward a synthesis rather than editing
multiple historical documents individually:

- **`res-006`/`res-007`** (platform capability-layering model) — both need the same Phase 6
  multi-runtime finding added; better done once as a shared update or synthesis than twice.
- **`res-013`/`res-014`** (Phase 4 agent-format learning) — both need the same forward note
  toward Phase 6's formalization.

## Explicitly Not Decided

- Whether any `update`/`add-status-note` action is approved to execute, and in what commit
  structure relative to the file-move migration.
- Whether `vis-004`'s already-repo-recorded 'extract unique content then archive' action
  should be executed as part of this content-remediation work or the file-move migration.
- Final content for any `create-synthesis` candidate.