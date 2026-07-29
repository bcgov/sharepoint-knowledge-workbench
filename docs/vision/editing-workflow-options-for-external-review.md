# Content-Author Editing Workflow Options — Open Question for External Review

**Status:** Draft open question, not yet decided or approved as part of any authorized phase.
Companion to `docs/vision/key-unanswered-questions.md` and the Phase 3 (Governed SharePoint
Knowledge Pilot) section of `docs/vision/master-initiative-plan-workstreams-and-phases.md`.
Shared for external review/feedback (e.g. M365 Copilot, Opus, GPT-5.6) before finalizing.

## Issue Summary

Canonical content today is git-only Markdown, edited via VS Code/GitHub/Copilot CLI. That's fine
for this technical pilot, but it was never designed as the real end-user authoring experience for
the actual intended content owners — non-technical business/government staff (e.g., court registry
staff) who are the example content owners named in the broader vision docs.

A future phase (Phase 3, gated behind a not-yet-started tenant-capability-discovery phase) plans to
publish hardened canonical content into a governed SharePoint knowledge library —
package-only by default, no autonomous write. That phase's own planning already flags an
unresolved question: whether manual editing of published SharePoint content is prohibited,
tolerated, or reconciled, and whether such edits ("drift") should flow back into canonical content.

The plan's existing "reconciliation" work (Phase 3, Subphase 3.3) only **detects** drift between
the canonical publication map and actual SharePoint library items — it does not define any
mechanism to **pull edited content back** into canonical Markdown. If SharePoint becomes an editing
surface without such a mechanism, canonical content in this repo goes stale the moment someone
edits there, and every downstream skill (re-rendering to other formats, future
evaluation/grounding work) only ever operates on canonical content — so SharePoint edits would
otherwise be a dead end with no way back into the system that produced them.

**The core question this document raises:** where do content authors actually edit chunks
day-to-day, and how does edited content re-enter canonical git if the edit location isn't git?

## Context

This repo (`manual-conversion-poc`) implements Phase 1 of an initiative moving Word/PDF manuals
from a document-centric model to a content-centric model: canonical Markdown content + generated
elements (TOC, navigation) + a presentation template = a published output for a given destination.

## Four candidate models (none decided, none built)

| # | Model | How it works | Key tension / open problem |
|---|---|---|---|
| A | **SharePoint-edit + sync-back** | Authors edit in SharePoint; a new sync skill pulls edited content back into canonical git so existing render/validate tools still work | Requires a genuinely hard reverse-conversion (SharePoint's rich-text page storage → clean canonical Markdown) — likely harder than the existing DOCX→canonical pipeline, and not designed at all today |
| B | **Git-only editing, SharePoint = output only** | Authors use VS Code/GitHub/Copilot CLI directly on canonical Markdown; SharePoint only ever receives rendered, read-only published output | Architecturally simplest (no reverse sync needed at all) but likely real friction/adoption risk for non-technical business content owners who don't use git day-to-day |
| C | **SharePoint-native rendering** | A SharePoint-hosted skill runs the render pipeline directly where the content lives (e.g., a Python-backed skill invoked from SharePoint), avoiding round-tripping through canonical git entirely | Raises the question of what's authoritative if canonical git isn't in the loop at all; likely conflicts with the "canonical is source of truth, published is a rendered projection" rule the plan has already committed to (Phase 3, Stage 3.1.3); platform/hosting feasibility for running arbitrary code from SharePoint is unknown pre-tenant-discovery |
| D | **Lightweight web Markdown editor over git** | A simple, purpose-built web UI lets authors edit Markdown without touching git/VS Code/GitHub directly; commits happen behind the scenes on their behalf | A middle ground — less friction than B, avoids the hard reverse-conversion problem of A/C — but is new product surface that has to be designed, built, and maintained; not free |

## Open questions to resolve (not yet answered)

- Which model (or hybrid) is realistic given the actual tenant's real constraints and the actual
  users' real technical comfort level — this is evidence Phase 3.0 (tenant capability discovery)
  is meant to produce, not something to guess at now.
- Is Model A's SharePoint→canonical reverse-conversion problem even tractable? (Unlike a `.docx`,
  a SharePoint modern page's stored representation isn't necessarily clean, parseable Markdown.)
- Is Model C compatible with the source-of-truth rule the plan has already adopted (canonical is
  authoritative; published is a projection)? If SharePoint can render/write independently, does
  "canonical is authoritative" still hold, or does this model implicitly make SharePoint a second
  source of truth?
- Who decides which model is used — is this a single global decision, or could different content
  types/audiences reasonably use different models?
- What does the actual day-to-day authoring loop look like end-to-end under each model — i.e., who
  edits, who/what triggers a re-render, and how do generated elements (nav, TOC) and other
  published formats stay in sync?

## Explicit non-decision

**No model is recommended or selected here.** This is deliberately left open, deferred to Phase 3
(gated behind Phase 3.0's tenant-capability discovery), consistent with this repo's stated
discipline of not building/deciding phases ahead of the evidence that phase is meant to produce.
This document exists to make sure the question is asked and tracked, not answered prematurely.

## Feedback requested

- Are there other realistic candidate models missing from this list?
- Of the four, does any look clearly infeasible or clearly preferable on its face (setting aside
  that a final decision should wait for Phase 3.0 evidence)?
- Is the "canonical is authoritative, SharePoint is a rendered projection" architectural stance
  (already adopted for Phase 3) the right one to hold onto, or does it need revisiting given these
  four models?
