# Open Question for External Review — Where Does an Ongoing SharePoint Editing → Re-render Flow Belong?

**Status:** RESOLVED (placement decision only — no implementation authorized). Raised during
Phase 5 brainstorming (2026-08-02); resolved the same day via external review (GPT 5.6). See
"Resolution" below for the decision; the rest of this document is preserved as the original
architecture note that review was based on.

## Resolution (2026-08-02, external review — GPT 5.6)

Do not fold this concern entirely into any single option above. Split it across two existing
phases, and record — but do not authorize — a future implementation phase:

- **Phase 3, Stage 3.1.4** owns the full ongoing structured-content maintenance workflow: where
  editing happens, which representation is authoritative, how changes are proposed/reviewed/
  approved/versioned/audited, how an edited topic re-enters the structured content package, and
  how IDs/lineage/hashes/manifests/cross-references/publication maps are recalculated. Updated in
  `docs/vision/master-initiative-plan-workstreams-and-phases.md`'s Stage 3.1.4.
- **Phase 6, new Subphase 6.3 ("Runtime placement for content-lifecycle actions")** owns *which
  runtime* (deterministic pipeline, native skill, or conversational agent) performs each of Phase
  3.1.4's actions, and the rule that agent-generated output is a non-authoritative preview unless
  it passes the same contracts/validation as the deterministic pipeline. Added to the master plan,
  `docs/superpowers/specs/phase-6-multi-runtime-capability-model-spec.md` (Section 13), and
  `docs/superpowers/plans/phase-6-multi-runtime-capability-model-plan-scaffold.md` (Task 12).
- **Phase 5.5B stays scoped to deterministic renderer expansion only** — explicit guardrail added
  to the master plan's Phase 5.5B section against broadening it into an agent editing/publication
  workflow.
- **A new placeholder phase, "Phase 6.5 — Ongoing Structured Content Authoring and
  Republishing,"** is recorded in the master plan, disposition NOT TRIGGERED / NOT AUTHORIZED,
  structure-only, gated behind both Phase 3.1.4 and Phase 6.3 answering their design questions plus
  a real edited-content example and business editor. This document's Options 1/2/3 are superseded
  by this split; the corrected architecture is **three** flows, not two — ingestion, ongoing
  authoring, and publication (the two-flow diagram below predates this correction).

The operating model going forward for any agent-adjacent editing/rendering work: agent assists or
requests → deterministic tooling updates/renders → validation executes → human/governed workflow
approves → publication reconciles. Conversational rendering is never authoritative on its own.

## Follow-up elaboration (2026-08-02, same-day external review — GPT 5.6)

A second review pass confirmed this placement and filled in the loop and runtime division in
detail, now folded into Phase 6.5 itself in the master plan:

```text
Published structured content
  → edit or change proposal (SharePoint: direct edit, change proposal, review comment,
    agent-assisted drafting)
  → GitHub Copilot/Claude-assisted review and update (workstation applies the approved change
    to structured source content)
  → validated structured content package (deterministic tooling recalculates identity, lineage,
    hashes, cross-references, publication mappings)
  → re-render (deterministic renderer(s), all affected representations)
  → republish and reconcile in SharePoint
  → SharePoint agents/native skills consume the updated published content
  → discover another improvement (loop repeats)
```

Runtime division: **SharePoint agent/native skill** proposes/reviews/gathers intent only; **GitHub
Copilot/Claude workbench** applies the approved change to structured source; **deterministic
tooling** validates/hashes/renders/republishes (the actual validation and rendering authority);
**SharePoint** hosts the outputs; **SharePoint agents** are the consuming user-facing interface.
Confirmed: this becomes a later dedicated phase, *after* the current Phase 5 prototype clarifies
how people actually interact with the published content — not pulled forward ahead of that
evidence. Renamed accordingly from the initial working title "Ongoing Structured Content
Maintenance and Assisted Republishing" to "Ongoing Structured Content Authoring and Republishing."

---

## Original architecture note (as submitted for review)

## The two flows already in the architecture

The workbench's core workflow, as built through Phase 2, is two sequential, one-directional
flows over a single canonical source of truth:

```text
Flow 1 — Extract:      source .docx  --[extract/analyze/confirm/convert]-->  canonical content
Flow 2 — Render:       canonical content  --[render]-->  one or more output formats
                                                          (multipage-markdown today;
                                                           .aspx, PDF, Word, etc. per
                                                           Phase 5.5B's renderer-expansion path)
```

Both flows are **one-shot and deterministic**: Flow 1 runs once per source document (or re-run
from scratch on a new source revision); Flow 2 is a pure function of canonical content → output,
re-run any time canonical content changes, always producing the same output for the same input.
Neither flow, as currently built, has a notion of *editing after conversion* — canonical content
is treated as authored once (by the extraction pipeline) and then only re-rendered.

## The open question: an ongoing editing flow

Two related but distinct capabilities are missing from the above model, and neither has a clearly
assigned phase yet:

1. **Editing canonical content after initial extraction.** A human (likely a non-technical
   business content owner) wants to correct/update a topic's canonical Markdown chunk after the
   initial conversion — without going through git/VS Code. `docs/vision/
   editing-workflow-options-for-external-review.md` already names this problem and lays out
   editing-location models A–G (Git-only, SharePoint-hosted Markdown authoring, change-proposal
   workflows, central publishing team, hybrid). This is currently tracked as an open design
   question under **Phase 3, Stage 3.1.4** ("source-of-truth lifecycle rules") — general to *where
   editing happens*, not yet resolved, and not yet a committed phase of work.

2. **Agent-assisted re-rendering of edited content into multiple formats on demand.** A distinct,
   narrower idea raised during Phase 5 brainstorming: once a chunk is edited (wherever that
   editing happens), could a **SharePoint agent or native skill** — not the deterministic
   pipeline's `render()` function — assemble/transform the edited canonical chunk into whichever
   output format is needed (`.aspx`, consumption-`.md`, etc.), on request, inside the SharePoint
   surface itself? This is meaningfully different from Phase 5.5B's renderer-expansion path, which
   adds a new *deterministic, code-based* renderer to the existing pipeline (`Renderer` protocol,
   golden-master validated) — not an agent performing ad hoc assembly/transformation as a
   conversational or skill-invoked action.

## Where this doesn't currently fit

- **Phase 3, Stage 3.1.4** covers *where authoring/editing happens* (Git vs. SharePoint vs.
  hybrid) — it does not cover *agent-performed rendering* of edited content into multiple formats.
- **Phase 5.5A (Content Model Expansion)** is about generalizing the canonical *content model* to
  a second content type (e.g. policy vs. manual) — unrelated to this question.
- **Phase 5.5B (Renderer Expansion)** is about adding one new *deterministic* renderer to the
  existing pipeline, validated against golden-master fidelity — it assumes canonical content is
  already finalized before rendering, not that an agent is doing ad hoc, per-request
  transformation of freshly-edited content.
- **Phase 6 (Multi-Runtime Capability Model)** was not reviewed in depth for this question yet —
  it may be the more natural home if it already covers "which runtime (pipeline vs. agent vs.
  skill) performs a given capability," since agent-as-renderer is fundamentally a runtime-
  placement decision. Needs confirmation, not assumed here.

## Options for external review

**Option 1 — Fold into Phase 5.5B, scoped as a variant.** Treat "agent-assisted rendering of
edited content" as one additional renderer-expansion scenario alongside new deterministic output
formats, evaluated under the same fidelity/golden-master discipline (Stage 5.5B.1.5) but with an
agent as the execution runtime instead of pipeline code.

**Option 2 — Fold into Phase 3, Stage 3.1.4, as part of the editing-workflow decision.** Since the
ongoing-editing question and the agent-rendering question are causally linked (you can't
agent-render an edit that has no supported editing path yet), resolve both together as part of the
source-of-truth lifecycle design work already scoped there.

**Option 3 — New Phase 5.5C (or equivalent), dedicated to ongoing content lifecycle.** Split
out as its own phase, distinct from 5.5A (content-model generalization) and 5.5B (new deterministic
renderers): "Ongoing Editing & Agent-Assisted Re-rendering" — covering both where editing happens
and whether/how an agent (vs. pipeline code) can re-render edited content into needed formats.
Would need its own entry gate (e.g., a real edited-content example, a real second-format need) per
the master plan's evidence-gated phase-authorization discipline.

**Not yet decided:** which option, or whether Phase 6 already covers part of this and should be
read first before choosing. No implementation, phase creation, or spec work is authorized by this
document — it exists solely to get an external second opinion on placement before committing.
