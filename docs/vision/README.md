# Vision and Implementation Planning

This directory contains the evolving vision, strategic questions, original proposals, and broader implementation plan for the **AI-Assisted Structured Knowledge Workbench**.

The initiative began as a document-conversion proof of concept in the `manual-conversion-poc` repository. Research and implementation showed that raw DOCX-to-Markdown conversion is only an extraction step. The broader problem is how to create, govern, publish, maintain, and reuse structured knowledge across multiple delivery and agent platforms.

## Recommended Naming

```text
Initiative:
AI-Assisted Structured Knowledge Workbench

Proposed repository name:
structured-knowledge-workbench

Phase 1:
Structured Knowledge Conversion and Canonical Content POC

Phase 1 plugin:
docx-to-content

Phase 1 pilot:
CEIS Manual
```

**Naming reconciliation (added 2026-08-02):** the repository was renamed, but to
`sharepoint-knowledge-workbench`, not the `structured-knowledge-workbench` recommended above.
`docx-to-content` was decommissioned 2026-08-01 (Phase 4.5 Wave 8) and decomposed into four real
plugins (`source-document-extraction`, `document-structure-analysis`, `structured-content-assembly`,
`structured-content-rendering`). See the fuller naming-reconciliation note in
`ai-assisted-structured-knowledge-workbench-broader-plan.md` (near its top) before treating any
plugin name in this directory's documents as current.

The initiative name is intentionally broader than SharePoint. SharePoint is a major operational platform and deployment target, but the workbench also covers canonical content, publication assembly, validation, GitHub Copilot skills, Cowork packaging, Copilot Studio integration, evaluation, and generated outputs.

## Directory Purpose

Use this directory for documents that answer one of these questions:

- What future state are we trying to create?
- Why is structured knowledge preferable to document-only management?
- How do SharePoint, agents, skills, publishing, and governance fit together?
- What decisions remain unresolved?
- How should the repository and implementation roadmap evolve?

Do not use this directory for:

- detailed implementation plans;
- completed architecture decisions;
- product research notes;
- test evidence;
- generated output;
- temporary agent working notes.

Recommended destinations for those artifacts are:

```text
docs/plans/       bounded implementation plans
docs/decisions/   accepted architecture decisions and ADRs
docs/research/    product research and field notes
docs/phases/      phase charters and exit criteria
evidence/         generated validation and release evidence
```

## Current Documents

### 1. Current umbrella plan

[`ai-assisted-structured-knowledge-workbench-broader-plan.md`](ai-assisted-structured-knowledge-workbench-broader-plan.md)

**Role:** Primary strategic roadmap and repository-transformation proposal.

Use this document for:

- initiative and repository naming;
- one-repository versus multiple-repository guidance;
- proposed plugin and agent boundaries;
- proposed repository structure;
- phased roadmap;
- Superpowers brainstorming and plan-writing workflow;
- low-cost, mid-tier, and high-reasoning agent allocation;
- repository rename and non-destructive restructuring strategy;
- backlog classification.

**Status:** Active proposal. It requires repository reconnaissance and adversarial review before rename, restructuring, or plugin scaffolding.

### 2. Current government workbench vision

[`ai-assisted-sharepoint-knowledge-workbench-government-vision.md`](ai-assisted-sharepoint-knowledge-workbench-government-vision.md)

**Role:** Detailed future-state capability and governance vision centred on government knowledge management and SharePoint operations.

Use this document for:

- Setup, Automate, and Insight capability pillars;
- seven user-facing workbench journeys;
- Explore, Design, Prepare, Execute, and Monitor modes;
- metadata authority;
- topic, publication, and release governance;
- SharePoint delivery models;
- proposed skill families;
- proposed agent boundaries;
- government security, privacy, records, accessibility, approval, and audit controls.

**Status:** Active future-state architecture. It does not expand the authorized scope of Phase 1.

### 3. Active unanswered questions

[`key-unanswered-questions.md`](key-unanswered-questions.md)

**Role:** Architecture question and risk register.

Use this document to track unresolved decisions about:

- knowledge-unit and topic boundaries;
- publication maps and reuse;
- post-migration source-of-truth rules;
- ownership, approval, retirement, and records;
- metadata authority;
- security boundaries;
- accessibility;
- stable identity and long-lived links;
- localization;
- schema evolution;
- quality metrics;
- rollback;
- AI trust boundaries.

**Status:** Active. Questions should move to `docs/decisions/` when resolved rather than being silently removed.

### 4. Earlier government governance vision

[`government-structured-knowledge-sharepoint-governance-vision-v2.md`](government-structured-knowledge-sharepoint-governance-vision-v2.md)

**Role:** Earlier detailed version of the government structured-knowledge and SharePoint governance vision.

Most of its core material is incorporated into the newer `ai-assisted-sharepoint-knowledge-workbench-government-vision.md`, which adds the broader workbench framing, user journeys, operating modes, routing, and SharePoint-agent concepts.

**Status:** Superseded as the primary vision, but retained for history until content reconciliation proves that no unique requirement would be lost by archiving it.

**Recommended action:** Compare it against the current workbench vision, extract any unique requirements, then move it to `docs/vision/archive/` with a supersession note.

### 5. Original combined vision

[`vision-original.md`](vision-original.md)

**Role:** Historical bridge between the original content-management proposal and the original Copilot knowledge-access proposal.

It records the key early insight that:

```text
raw DOCX-to-Markdown extraction
≠ canonical structured content
```

It also explains why conversational knowledge access is a downstream payoff of creating governed canonical content.

**Status:** Historical foundation. Retain as provenance rather than treating it as the current roadmap.

### 6. Original content-management proposal

[`plan-content-management-proposal.md`](plan-content-management-proposal.md)

**Role:** Original proposal to move from document-centric knowledge management to:

```text
Content + Template + Renderer = Published Output
```

**Status:** Historical source proposal. Its major ideas are incorporated into the current vision and broader plan.

### 7. Original knowledge-access proposal

[`plan-copilot-knowledge-access-proposal.md`](plan-copilot-knowledge-access-proposal.md)

**Role:** Original proposal for conversational access to approved organizational knowledge, including policy support, procedure assistance, learning support, quizzes, discovery, pilot measurement, and consumption-based licensing investigation.

**Status:** Historical source proposal. Its major ideas are incorporated into the current workbench and agent vision.

## Recommended Reading Order

### For a new contributor

```text
1. This README
2. ai-assisted-structured-knowledge-workbench-broader-plan.md
3. ai-assisted-sharepoint-knowledge-workbench-government-vision.md
4. key-unanswered-questions.md
```

### To understand how the idea evolved

```text
1. plan-content-management-proposal.md
2. plan-copilot-knowledge-access-proposal.md
3. vision-original.md
4. government-structured-knowledge-sharepoint-governance-vision-v2.md
5. ai-assisted-sharepoint-knowledge-workbench-government-vision.md
6. ai-assisted-structured-knowledge-workbench-broader-plan.md
```

### To plan implementation

```text
1. ai-assisted-structured-knowledge-workbench-broader-plan.md
2. key-unanswered-questions.md
3. current repository inventory
4. accepted decisions in docs/decisions/
5. bounded phase plan in docs/plans/
```

## Document Authority and Status

The documents do not all have equal authority.

```text
Current strategic direction
→ ai-assisted-structured-knowledge-workbench-broader-plan.md

Current detailed government capability vision
→ ai-assisted-sharepoint-knowledge-workbench-government-vision.md

Open decision register
→ key-unanswered-questions.md

Superseded detailed vision
→ government-structured-knowledge-sharepoint-governance-vision-v2.md

Historical origin documents
→ vision-original.md
→ plan-content-management-proposal.md
→ plan-copilot-knowledge-access-proposal.md
```

A vision document may propose capabilities, but does not authorize implementation. Authorization should come from a reviewed phase plan or accepted architecture decision.

## Recommended Folder Organization

Do not perform a broad file move while the repository rename and restructuring decision is still pending. Adding this README provides immediate logical organization without breaking links.

After repository reconnaissance and approval, use this target structure:

```text
docs/vision/
├── README.md
├── ai-assisted-structured-knowledge-workbench-broader-plan.md
├── ai-assisted-sharepoint-knowledge-workbench-government-vision.md
├── key-unanswered-questions.md
└── archive/
    ├── README.md
    ├── government-structured-knowledge-sharepoint-governance-vision-v2.md
    ├── vision-original.md
    ├── plan-content-management-proposal.md
    └── plan-copilot-knowledge-access-proposal.md
```

### Why this layout

- Three active documents remain easy to find.
- Historical evolution is preserved.
- Superseded material is not mistaken for current direction.
- Relative-link disruption is limited to one reviewed archive move.
- Detailed implementation plans remain outside the vision directory.

## Proposed Archive README

When the archive move is approved, add `docs/vision/archive/README.md` with content similar to:

```markdown
# Archived Vision Documents

These documents preserve the evolution of the AI-Assisted Structured Knowledge Workbench vision.

They are retained for provenance and research history but are not the current source of strategic direction.

Current documents:

- ../ai-assisted-structured-knowledge-workbench-broader-plan.md
- ../ai-assisted-sharepoint-knowledge-workbench-government-vision.md
- ../key-unanswered-questions.md
```

## Review Findings

### 1. The directory has a clear conceptual progression

The seven documents show a traceable evolution:

```text
content-centric proposal
+ conversational knowledge-access proposal
→ original combined vision
→ detailed government governance vision
→ expanded SharePoint Knowledge Workbench vision
→ broader multi-plugin initiative and implementation roadmap
```

This history is useful and should be preserved.

### 2. There is substantial duplication

The two long government vision documents overlap heavily. The newer workbench vision appears to extend the earlier governance vision rather than represent a separate competing direction.

Recommended treatment:

- retain the newer document as current;
- reconcile unique content before archiving the earlier version;
- do not continue updating both documents independently.

### 3. The broader plan and detailed vision serve different purposes

Do not merge them into one very large document.

```text
Broader plan
→ naming, repository structure, plugins, agents, phases, planning workflow

Government workbench vision
→ future capabilities, governance model, operating modes, trust boundaries
```

Cross-link them instead.

### 4. The unanswered-questions file should remain separate

It is useful as an explicit challenge register. Moving unresolved issues into prose inside the vision would make them easier to overlook.

When a question is resolved:

```text
unanswered question
→ architecture decision
→ implementation plan, if required
→ evidence
```

### 5. Original proposals should remain immutable historical sources

Avoid repeatedly editing the original proposals to match the current architecture. Add a status banner or archive them instead. Their value is showing how the broader vision emerged.

## Recommended Cross-Links

Add a short navigation block near the top of the two current primary documents.

### In the broader plan

```markdown
## Related Documents

- [Detailed government workbench vision](ai-assisted-sharepoint-knowledge-workbench-government-vision.md)
- [Key unanswered questions](key-unanswered-questions.md)
- [Vision directory guide](README.md)
```

### In the detailed government vision

```markdown
## Related Documents

- [Broader initiative and implementation plan](ai-assisted-structured-knowledge-workbench-broader-plan.md)
- [Key unanswered questions](key-unanswered-questions.md)
- [Vision directory guide](README.md)
```

## Change-Control Rules for This Directory

1. Update the broader plan when initiative naming, plugin boundaries, repository structure, phases, or implementation strategy changes.
2. Update the government workbench vision when target capabilities, governance principles, operating modes, or trust boundaries change.
3. Update `key-unanswered-questions.md` when a significant unresolved architecture or operating-model question is discovered.
4. Record accepted decisions in `docs/decisions/`; do not rewrite history to make old proposals appear decided.
5. Move superseded material to `archive/` only after unique content has been reconciled.
6. Do not treat proposed skills or agents as authorized backlog items merely because they appear in a vision document.
7. Apply the backlog states `NOW`, `NEXT`, `LATER`, `RESEARCH`, and `REJECTED` before implementation planning.
8. Preserve package-only and design-only modes for capabilities that lack approved deployment permissions.
9. Keep repository renaming, file moves, plugin extraction, and behavioural changes in separate reviewed steps where practical.
10. Update applicable plugin and marketplace metadata when an implemented capability changes repository-distributed artifacts.

## Immediate Next Steps

The immediate work should remain bounded:

1. Complete the current CEIS Phase 1 evidence and cutover work under its approved plan.
2. Use Superpowers brainstorming and repository reconnaissance to test the broader plan against the real repository.
3. Decide whether to rename the repository to `structured-knowledge-workbench`.
4. Decide which plugin boundaries are justified now versus later.
5. Reconcile the two detailed government vision documents.
6. Create accepted architecture decisions before moving active files or scaffolding new plugins.
7. Write one small implementation plan for any approved rename and non-destructive restructure.

## Non-Goals

This directory does not authorize:

- renaming the repository;
- moving files;
- scaffolding new plugins;
- creating production SharePoint libraries or agents;
- granting Microsoft Entra permissions;
- deploying Copilot Studio solutions;
- converting all research ideas into backlog items;
- expanding the current Phase 1 implementation without an approved plan.

## Summary

The recommended organization is deliberately simple:

```text
One README
Three active vision/strategy documents
Four archived origin or superseded documents
```

The broader initiative is now clear enough to name and plan, but repository structure and plugin boundaries still require evidence-based review against the actual implementation.
