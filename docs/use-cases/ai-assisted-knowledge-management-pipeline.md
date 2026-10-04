# Use Case: AI-Assisted Knowledge Management Pipeline (NOT YET IMPLEMENTED)

> **Status: target-state vision, not built.** Unlike every other doc in this folder, this use
> case does not describe a working plugin — it describes where the workbench is headed once
> [Document Conversion](sharepoint-document-conversion.md) is treated as a one-time extraction step rather
> than the end state. Do not treat anything below as available today.

Move knowledge management itself — not just the initial Word-to-Markdown conversion — from
document-centric editing (content and formatting baked together in a `.docx`) to an AI-assisted,
agent-enabled pipeline: natural-language library setup, AI-assisted metadata/classification/
cleanup, governed review and approval, publication assembly across multiple output formats and
renderer templates, SharePoint knowledge agents as a governed product, and continuous
knowledge-health monitoring — with deterministic tooling remaining the sole validation/rendering/
authority and accountable people remaining responsible for approval and risk.

## When you'd reach for this (once built)

You've converted a manual once (via [Document Conversion](sharepoint-document-conversion.md)) and now need
to **operate** it: someone edits canonical content after cutover, a schema needs to be designed
from a plain-language request, a change needs review/approval before republishing, or a SharePoint
knowledge agent needs to be created and evaluated as a governed product rather than an ungoverned
chatbot layered over arbitrary content.

## The three capability pillars (proposed)

```text
SETUP      Create and configure governed content libraries from natural language
AUTOMATE   Organize, enrich, validate, clean up, and maintain content at scale
INSIGHT    Find, understand, analyze, visualize, and reuse governed knowledge
```

Every pillar follows the same governed pattern: **AI proposes, compares, checks, assembles, and
prepares. Deterministic automation validates, renders, packages, and records. Accountable people
decide, approve, publish, and accept risk.** AI must never silently invent authoritative ownership,
approval, security/records classification, or retention decisions.

## What's real today vs. what this describes

| Already built | Still just proposed |
|---|---|
| Extract/analyze/confirm/convert/render pipeline (`sharepoint-document-conversion`) | Natural-language → governed SharePoint schema design |
| SharePoint content publication (`sharepoint-site-build-and-publish`) | AI-assisted content classification, cleanup, and impact analysis |
| Agent/native-skill lifecycle tooling (`sharepoint-copilot-agents-and-skills`) | Governed review/approval workflow generation |
| — | SharePoint knowledge agents evaluated as a governed product (readiness/drift monitoring) |
| — | Continuous knowledge-health dashboards (stale/orphan/duplicate detection) |
| — | The ongoing SharePoint-edit → re-render → republish loop (placeholder Phase 6.5, `NOT_TRIGGERED`) |

## Full detail

- [`docs/vision/ai-assisted-sharepoint-knowledge-workbench-governance-vision.md`](../vision/ai-assisted-sharepoint-knowledge-workbench-governance-vision.md) —
  the full capability vision: three pillars, seven user-facing journeys, five operating modes
  (Explore/Design/Prepare/Execute/Monitor), proposed skill family, proposed agent boundaries,
  metadata authority model, and governance controls.
- [`docs/vision/ai-assisted-structured-knowledge-workbench-broader-plan.md`](../vision/ai-assisted-structured-knowledge-workbench-broader-plan.md) —
  naming, plugin-boundary, and phased-roadmap strategy for getting from here to there.
- [`docs/vision/key-unanswered-questions.md`](../vision/key-unanswered-questions.md) — 16 open
  design questions this use case depends on answering first (what the stable unit of knowledge is,
  the assembly/publication-map layer, post-cutover editing, governance/reuse/metadata authority,
  and more).
- [`docs/vision/master-initiative-plan-workstreams-and-phases.md`](../vision/master-initiative-plan-workstreams-and-phases.md) —
  the authoritative phase/stage traceability matrix; see Phase 3 Stage 3.1.4, Phase 6 Subphase 6.3,
  and the Phase 6.5 placeholder for where pieces of this use case are gated.

No implementation, phase creation, or spec work is authorized by any of the above documents alone
— see each document's own status/authorization language before treating any part of this as
approved backlog.
