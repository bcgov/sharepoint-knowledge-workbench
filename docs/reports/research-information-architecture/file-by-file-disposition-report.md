# File-by-File Disposition Report — Review Point 2

Generated from `research-migration-manifest.json`. Status: PROPOSED/RECOMMENDED for most entries; only 10 reach APPROVED (all retain-in-place, zero moves).

| ID | Source | Operation | Destination | Filename | Status | Confidence basis |
|---|---|---|---|---|---|---|
| arch-001 | `docs/architecture/docx-to-content-legacy-references/README.md` | move | docs/research/structured-content-engineering/legacy | README.md | **recommended** | 100% read (full) |
| arch-002 | `docs/architecture/docx-to-content-legacy-references/canonical-contract.md` | move | docs/research/structured-content-engineering/legacy | canonical-contract.md | **recommended** | 16% read (minimal-sample) |
| arch-003 | `docs/architecture/docx-to-content-legacy-references/content-authoring-guide.md` | move | docs/research/structured-content-engineering/legacy | content-authoring-guide.md | **tentative** | 25% read (minimal-sample) |
| arch-004 | `docs/architecture/docx-to-content-legacy-references/extraction-triggers.md` | move | docs/research/structured-content-engineering/legacy | extraction-triggers.md | **tentative** | 44% read (minimal-sample) |
| arch-005 | `docs/architecture/docx-to-content-legacy-references/future-output-profiles.md` | move | docs/research/structured-content-engineering/legacy | future-output-profiles.md | **tentative** | 4% read (minimal-sample) |
| arch-006 | `docs/architecture/docx-to-content-legacy-references/generated-elements.md` | move | docs/research/structured-content-engineering/legacy | generated-elements.md | **recommended** | 83% read (substantial-partial) |
| arch-007 | `docs/architecture/docx-to-content-legacy-references/known-pandoc-gaps.md` | exclude | — | known-pandoc-gaps.md | **recommended** | 100% read (full) |
| arch-008 | `docs/architecture/docx-to-content-legacy-references/pandoc-docx-setup.md` | exclude | — | pandoc-docx-setup.md | **recommended** | 100% read (full) |
| arch-009 | `docs/architecture/docx-to-content-legacy-references/publication-map-contract.md` | move | docs/research/structured-content-engineering/legacy | publication-map-contract.md | **recommended** | 20% read (minimal-sample) |
| arch-010 | `docs/architecture/docx-to-content-legacy-references/supported-markdown-profile.md` | move | docs/research/structured-content-engineering/legacy | supported-markdown-profile.md | **tentative** | 31% read (minimal-sample) |
| arch-011 | `docs/architecture/docx-to-content-legacy-references/templates/components/README.md` | move | docs/research/structured-content-engineering/legacy/templates/components | README.md | **recommended** | 38% read (minimal-sample) |
| arch-012 | `docs/architecture/docx-to-content-legacy-references/templates/content/manual-topic.md` | move | docs/research/structured-content-engineering/legacy/templates/content | manual-topic.md | **tentative** | 33% read (minimal-sample) |
| arch-013 | `docs/architecture/docx-to-content-legacy-references/templates/examples/manual-topic-example.md` | move | docs/research/structured-content-engineering/legacy/templates/examples | manual-topic-example.md | **tentative** | 25% read (minimal-sample) |
| arch-014 | `docs/architecture/phase-4-5-target-architecture.md` | retain | docs/architecture | phase-4-5-target-architecture.md | **recommended** | 51% read (substantial-partial) |
| arch-015 | `docs/architecture/complete-plugin-skill-catalog-after-phase-9.md` | retain | docs/architecture | complete-plugin-skill-catalog-after-phase-9.md | **approved** | 13% read (minimal-sample) |
| arch-016 | `docs/architecture/complete-plugin-skill-catalog-after-phase-9.json` | retain | docs/architecture | complete-plugin-skill-catalog-after-phase-9.json | **approved** | 2% read (minimal-sample) |
| arch-017 | `docs/architecture/validate_plugin_skill_catalog.py` | retain | docs/architecture | validate_plugin_skill_catalog.py | **approved** | 7% read (minimal-sample) |
| diag-000 | `docs/diagrams/README.md` | retain | docs/diagrams | README.md | **recommended** | 100% read (full) |
| diag-001 | `docs/diagrams/01-phase1-overview.mmd` | retain | docs/diagrams | 01-phase1-overview.mmd | **approved** | 30% read (minimal-sample) |
| diag-002 | `docs/diagrams/02-analyze-and-confirm.mmd` | retain | docs/diagrams | 02-analyze-and-confirm.mmd | **approved** | 32% read (minimal-sample) |
| diag-003 | `docs/diagrams/03-create-canonical-content.mmd` | retain | docs/diagrams | 03-create-canonical-content.mmd | **approved** | 20% read (minimal-sample) |
| diag-004 | `docs/diagrams/04-generate-and-render.mmd` | retain | docs/diagrams | 04-generate-and-render.mmd | **approved** | 24% read (minimal-sample) |
| diag-005 | `docs/diagrams/05-validation-and-evidence.mmd` | retain | docs/diagrams | 05-validation-and-evidence.mmd | **approved** | 11% read (minimal-sample) |
| diag-006 | `docs/diagrams/06-editing-workflow-hybrid-option.mmd` | move | docs/vision | 06-editing-workflow-hybrid-option.mmd | **recommended** | 5% read (minimal-sample) |
| diag-007 | `docs/diagrams/07-publisher-triggered-render-workflow.mmd` | move | docs/vision | 07-publisher-triggered-render-workflow.mmd | **recommended** | 30% read (minimal-sample) |
| diag-008 | `docs/diagrams/08-editor-submission-and-approval-workflow.mmd` | move | docs/vision | 08-editor-submission-and-approval-workflow.mmd | **recommended** | 32% read (minimal-sample) |
| diag-009 | `docs/diagrams/09-phase6-5-ongoing-authoring-and-republishing-loop.mmd` | move | docs/vision | 09-phase6-5-ongoing-authoring-and-republishing-loop.mmd | **recommended** | 9% read (minimal-sample) |
| diag-010 | `docs/diagrams/high-level.mmd` | retain | docs/diagrams | high-level.mmd | **approved** | 12% read (minimal-sample) |
| res-001 | `docs/research/README.md` | retain | docs/research | README.md | **recommended** | 33% read (minimal-sample) |
| res-002 | `docs/research/research-summary-copilot-in-sharepoint-get-started.md` | move | docs/research/sharepoint-platforms-capabilities | research-copilot-in-sharepoint-preview.md | **tentative** | 9% read (minimal-sample) |
| res-003 | `docs/research/research-summary-native-markdown-sharepoint-onedrive.md` | move | docs/research/publication-delivery | research-markdown-support-sharepoint-onedrive.md | **tentative** | 6% read (minimal-sample) |
| res-004 | `docs/research/research-summary-ai-in-sharepoint-content-chaos-to-clarity.md` | move | docs/research/strategic-planning-vision | research-ai-in-sharepoint-setup-automate-insight.md | **tentative** | 6% read (minimal-sample) |
| res-005 | `docs/research/research-summary-sharepoint-ai-forward-content-creation-curation.md` | move | docs/research/knowledge-discovery-retrieval | research-sharepoint-content-creation-and-curation.md | **tentative** | 7% read (minimal-sample) |
| res-006 | `docs/research/capability-layering-sharepoint-skills-cowork-copilot-studio-github.md` | move | docs/research/sharepoint-platforms-capabilities | capability-layering-across-platforms.md | **tentative** | 11% read (minimal-sample) |
| res-007 | `docs/research/sharepoint-agents-and-native-skills-as-workbench-outputs.md` | move | docs/research/sharepoint-platforms-capabilities | sharepoint-agents-and-native-skills-as-workbench-outputs.md | **tentative** | 8% read (minimal-sample) |
| res-008 | `docs/research/skill-runtime-decision-guide-sharepoint-vs-github-copilot.md` | move | docs/research/architecture-design-patterns | skill-runtime-decision-guide-sharepoint-vs-github-copilot.md | **tentative** | 8% read (minimal-sample) |
| res-009 | `docs/research/field-note-sharepoint-agentassets-review-manual-topics-skill.md` | move | docs/research/sharepoint-platforms-capabilities | field-note-agentassets-skill-creation.md | **recommended** | 12% read (minimal-sample) |
| res-010 | `docs/research/field-note-ready-made-copilot-agent-launch-by-name.md` | move | docs/research/sharepoint-platforms-capabilities | field-note-agent-launch-by-name-not-a-handoff.md | **recommended** | 50% read (substantial-partial) |
| res-011 | `docs/research/field-note-aspx-vs-markdown-grounding-comparison.md` | move | docs/research/knowledge-discovery-retrieval | field-note-aspx-vs-markdown-grounding.md | **recommended** | 66% read (substantial-partial) |
| res-012 | `docs/research/research-summary-phase3-sharepoint-write-capability-discovery.md` | move | docs/research/research-experimentation | field-note-sharepoint-write-capability-discovery.md | **tentative** | 4% read (minimal-sample) |
| res-013 | `docs/research/phase-4-agent-format-learning-journal.md` | move | docs/research/research-experimentation | phase-4-agent-format-learning-journal.md | **recommended** | 28% read (minimal-sample) |
| res-014 | `docs/research/PHASE-4-SHAREPOINT-AGENTS-CRITICAL-LEARNINGS.md` | move | docs/research/research-experimentation | PHASE-4-SHAREPOINT-AGENTS-CRITICAL-LEARNINGS.md | **tentative** | 12% read (minimal-sample) |
| res-015 | `docs/research/EVID-PHASE4-TASK8-EXIT-GATE.md` | archive | docs/reports/phase-4-native-sharepoint-skills | EVID-PHASE4-TASK8-EXIT-GATE.md | **recommended** | 27% read (minimal-sample) |
| res-016 | `docs/research/concept-dual-target-rendering-agent-vs-human.md` | move | docs/research/publication-delivery | dual-target-rendering-concept.md | **recommended** | 75% read (substantial-partial) |
| root-001 | `docs/implementation-baseline.md` | retain | docs | implementation-baseline.md | **tentative** | 40% read (minimal-sample) |
| vis-001 | `docs/vision/README.md` | retain | docs/vision | README.md | **recommended** | 35% read (minimal-sample) |
| vis-002 | `docs/vision/ai-assisted-structured-knowledge-workbench-broader-plan.md` | retain | docs/vision | ai-assisted-structured-knowledge-workbench-broader-plan.md | **recommended** | 1% read (minimal-sample) |
| vis-003 | `docs/vision/ai-assisted-sharepoint-knowledge-workbench-government-vision.md` | retain | docs/vision | ai-assisted-sharepoint-knowledge-workbench-government-vision.md | **recommended** | 1% read (minimal-sample) |
| vis-004 | `docs/vision/government-structured-knowledge-sharepoint-governance-vision-v2.md` | archive | docs/vision/archive | government-structured-knowledge-sharepoint-governance-vision-v2.md | **recommended** | 100% read (full) |
| vis-005 | `docs/vision/key-unanswered-questions.md` | retain | docs/vision | key-unanswered-questions.md | **recommended** | 3% read (minimal-sample) |
| vis-006 | `docs/vision/vision-original.md` | archive | docs/vision/archive | vision-original.md | **recommended** | 14% read (minimal-sample) |
| vis-007 | `docs/vision/plan-content-management-proposal.md` | archive | docs/vision/archive | plan-content-management-proposal.md | **recommended** | 3% read (minimal-sample) |
| vis-008 | `docs/vision/plan-copilot-knowledge-access-proposal.md` | archive | docs/vision/archive | plan-copilot-knowledge-access-proposal.md | **recommended** | 4% read (minimal-sample) |
| vis-009 | `docs/vision/editing-workflow-options-for-external-review.md` | retain | docs/vision | editing-workflow-options-for-external-review.md | **recommended** | 3% read (minimal-sample) |
| vis-010 | `docs/vision/open-question-ongoing-editing-and-agent-assisted-rendering-phase-placement.md` | retain | docs/vision | open-question-ongoing-editing-and-agent-assisted-rendering-phase-placement.md | **recommended** | 8% read (minimal-sample) |
| vis-011 | `docs/vision/master-initiative-plan-workstreams-and-phases.md` | retain | docs/vision | master-initiative-plan-workstreams-and-phases.md | **approved** | 100% read (full) |