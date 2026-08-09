# Structured Content Pipeline Diagram Set

(Originally authored during Phase 1 as the "docx-to-content Diagram Set" — the diagrams below
depict the conceptual pipeline stages, which are unchanged; the implementation has since been
decomposed into `source-document-extraction`, `document-structure-analysis`,
`structured-content-assembly`, and `structured-content-rendering`, per
`docs/reports/phase-4-5-core-plugin-refactoring/plugin-skill-name-migration.md`.)

Files:

1. `01-phase1-overview.mmd` — simplified Phase 1 flow beneath the separate high-level vision diagram.
2. `02-analyze-and-confirm.mmd` — temporary extraction, analysis, recommendations, desired formats/templates, and confirmation.
3. `03-create-canonical-content.mmd` — cleanup, structural reconciliation, structured package creation, validation, and atomic promotion.
4. `04-generate-and-render.mmd` — code-generated TOC/navigation/indexes, template/output selection, rendering, and output validation.
5. `05-validation-and-evidence.mmd` — automated checks, human spot checks, evidence report, and hypothesis decision.

The temporary Markdown extraction is explicitly not structured content. User-maintained content is separated from code-generated elements such as tables of contents, navigation, keyword summaries, and indexes.

Files 01-05 above depict the **authorized Phase 1 pipeline** — implemented, current, load-bearing.
Diagrams 06-09 below are **speculative, unauthorized future-phase illustrations** (Phase 3
candidate editing workflows, Phase 6.5 authoring/republishing loop) — do not treat them as
describing built or authorized behavior. They previously lived in `docs/vision/` (2026-08
information-architecture reorganization, each paired with the specific vision document it
illustrates) and were moved back here on 2026-08-09 with descriptive `phase3-`/`phase6-5-`
filenames replacing their old bare numbered names, so the phase/authorization context survives the
move even without reading this file. **Read this distinction before citing any diagram below as
current or authorized — 01-05 and 06-09 are not the same kind of thing just because they share a
folder.**

6. `06-phase3-editing-workflow-hybrid-candidate.mmd` (formerly `06-editing-workflow-hybrid-option.mmd`) —
   illustrates one candidate (not selected) content-author editing workflow discussed in
   `docs/vision/editing-workflow-options-for-external-review.md`: a hybrid of that document's
   Model C (SharePoint-hosted Markdown authoring) and Model E (SharePoint change-proposal intake),
   showing SharePoint business authoring, the authorized SharePoint-to-Git boundary, Git validation
   and structured promotion, the governed publication pipeline, and the published SharePoint
   knowledge environment. This depicts Phase 3 territory, which is not yet authorized or built —
   see that document for full context and open questions.
7. `07-phase3-publisher-triggered-render-workflow.mmd` (formerly `07-publisher-triggered-render-workflow.mmd`) —
   a narrower, human-in-the-loop variant: an approved SharePoint chunk triggers a Power Automate
   notification to a human publisher, who pulls the approved chunks (via PnP PowerShell) into a
   local repository checkout, runs the repository's render skills through GitHub Copilot, reviews
   validation/preview output, and — once accepted — pushes generated outputs back to SharePoint via
   PnP PowerShell. Also speculative Phase 3 territory, not an authorized workflow.
8. `08-phase3-editor-submission-and-approval-workflow.mmd` (formerly `08-editor-submission-and-approval-workflow.mmd`) —
   the business-editor-facing half of the same flow, upstream of diagram 07: an author edits a
   chunk in SharePoint, submits it for approval, and the chunk moves through Draft → In review →
   Changes requested (looping back to editing) or Approved, at which point the Power Automate
   publisher notification (the entry point of diagram 07) fires. Deliberately excludes
   Git/publisher machinery — see the editing-workflow document's "Third round of review" section
   for why. Also speculative Phase 3 territory, not authorized.
9. `09-phase6-5-ongoing-authoring-and-republishing-loop.mmd` (unchanged name) — the runtime-division
   loop for the future **Phase 6.5 — Ongoing Structured Content Authoring and Republishing** (see
   `docs/vision/master-initiative-plan-workstreams-and-phases.md`'s Phase 6.5 section and
   `docs/vision/resolved-question-ongoing-editing-and-agent-assisted-rendering-phase-placement.md` for
   the full architecture note and external-review resolution this diagram is drawn from). Distinct
   from diagrams 06-08 (Phase 3's business-authoring/approval candidates): this one shows the
   *runtime* split — a SharePoint agent/native skill may only propose/review/gather intent; the
   GitHub Copilot/Claude workbench applies the approved change to structured source content;
   deterministic tooling remains the sole validation/rendering/hashing/lineage authority; the loop
   closes when SharePoint agents consume the republished content and a reader discovers another
   improvement. Speculative Phase 6.5 territory — NOT TRIGGERED, NOT AUTHORIZED, structure only.
