# Use Case: Document Conversion

Convert a legacy Word/PDF manual (document-centric: content + formatting baked together) into
modular, version-controlled structured Markdown (content-centric: **Content + Template + Renderer
= Published Output**), then publish it to multiple targets — human-readable pages (Markdown/ASPX)
and agent-optimized grounding content.

## When to use this

You have a source `.docx`/`.pdf` manual that needs to become maintainable, structurally validated,
multi-target content — not a one-off pandoc conversion.

## Workflow at a glance

A real analyze → confirm → convert → render pipeline, chained across four independently
installable plugins:

1. **`source-document-extraction`** — structural analysis, defect detection, and normalized
   extraction from the source `.docx`.
2. **`document-structure-analysis`** — topic-boundary reasoning, chunking-strategy
   recommendation, draft conversion-plan construction. A human confirms the plan before anything
   is built.
3. **`structured-content-assembly`** — Pandoc AST postprocessing, chunking, canonical-package
   build, and content-loss/structural validation.
4. **`structured-content-rendering`** — multi-target rendering (multipage Markdown,
   SharePoint ASPX) plus template creation/validation and rendered-output validation.

Each plugin installs standalone (`pip install -e plugins/<name>`) and has its own test suite.

## Full detail

- [`plugins/sharepoint-document-conversion/README.md`](../../plugins/sharepoint-document-conversion/README.md) (extraction, structure analysis, assembly, rendering and editorial review)
- [Master Architecture & Workflow diagram](../../README.md#%EF%B8%8F-master-architecture--workflow) in the main README
- [`docs/diagrams/`](../diagrams/README.md) — the formal per-stage Mermaid diagrams

## Open design questions

The pipeline above is built and validated, but the *operating model beyond initial conversion* —
what the stable unit of knowledge is, how topics assemble into multiple publications, what happens
when someone edits the original source or the canonical content after cutover, governance/
ownership/reuse rules, and more — is still genuinely unresolved. These aren't implementation gaps
in the plugins; they're open design questions the POC was meant to help answer, not yet decided:

- [`docs/vision/key-unanswered-questions.md`](../vision/key-unanswered-questions.md) — 16 open
  questions across topic-unit definition, the assembly/publication-map layer, post-migration
  editing, governance, reuse, metadata, records/retention, security, accessibility, link/identity
  lifecycle, localization, schema evolution, quality metrics, rollback, and AI trust boundaries.
- The roadmap's [Phase 6.5 section](../vision/master-initiative-plan-workstreams-and-phases.md#phase-65--ongoing-structured-content-authoring-and-republishing)
  records where a future SharePoint-editing → re-render → republish loop belongs; that end-to-end
  workflow is not implemented.
