---
name: content-enrich-navigation
plugin: sharepoint-document-conversion
description: Assesses how well a document's own structure supports progressive discovery and, only with the user's consent, prepares an optional AI-generated navigation layer (clearly flagged, never authoritative) for documents whose structure is weak or absent. Use after extraction when a document lacks bookmarks, headings or indexes, or when asked about summaries, indexes or AI structuring.
allowed-tools: Bash, Read
examples:
  - "python3 -c \"import sys; sys.path.insert(0, 'scripts/enrichment'); import structure_quality as sq; print(sq.assess_structure(normalized)['recommendation'])\""
---

# Enrich Navigation (optional, AI-assisted)

## Contents

- [Constraints](#constraints)
- [Status](#status)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Trust model](#trust-model)
- [Verification](#verification)
- [References](#references)

## Constraints

- Deterministic extraction stays authoritative. Never modify `raw/extracted.md`; write generated files to a separate `ai-navigation/` tree.
- Never run generation without the user's explicit yes. It costs credits, and the provider sees document text.
- Every AI-generated file carries the visible notice and the trust metadata below. No exceptions.
- Prefer existing trustworthy structure. AI fills structural gaps; it does not replace good bookmarks or headings.
- Topic files are verbatim slices of the extraction. AI may choose where to cut, never rewrite the text.

## Status

Implemented: the structure-quality assessment, overrides, page map, trust metadata, notice and validators (step 1),
agent-mediated decomposition (step 2), and summaries, chapter/document roll-up, relations, the hierarchical index and
approval-gated publication (step 3), and the evaluation mode (step 4). All planned parts are implemented.

## Agent-mediated generation

No code here calls a model. `decompose.py` writes `ai-navigation/requests/NNN.json`; the host agent, once the user has
approved, reads each request and writes its JSON answer (`{"topics": [{"start", "title", "uncertain"}]}`), which
`apply_response` validates (starts must be listed block edges, so tables are never split). A bad answer is retried up to
3 times per window, then that window is reported failed while the rest still publish. `write_topics` writes verbatim
slices to `ai-navigation/topics/`; `validate_topics` and `is_generation_stale` check the result. `generation.json`
records model, prompt version, timestamp, source and extraction hashes. Consent is stored by `record_consent` in
`enrichment-state.json`; `build_requests` refuses to run without it. The provider sees the document text.

Summaries and index (`navigation.py`): `build_summary_requests` (one per topic: summary, keywords, synonyms; a summary
may not copy more than 120 characters of source), then `build_rollup_request` (titles and summaries only, so it is
cheap) for the document summary, chapters and relations; every topic must be in exactly one chapter. `write_navigation`
writes `index.md`, `chapters/NN-*.md` and `navigation.json`, each with the notice and metadata; topics without
summaries stay listed. `approve` records the human reviewer; `publish` copies to a separate folder only when approved,
valid (notice, trust flags, pages, links) and not stale. Retrieval order for agents: `index.md`, chapter, topic,
then the extraction and original PDF as the factual basis. A worked example is in
`assets/examples/enrichment-example/` (regenerate with `scripts/enrichment/build_example.py`; wording is canned).

## Quick start

```python
import sys
sys.path.insert(0, "scripts/enrichment")
import structure_quality as sq
assessment = sq.assess_structure(normalized)          # normalized from extract_pdf_and_normalize
decision = sq.decide_enrichment(assessment, "intake/Manual.pdf", sq.load_overrides("enrichment-overrides.json"))
```

## Workflow

1. Assess each extracted document with `assess_structure`. It is deterministic and free. Grades: `sufficient`,
   `partial`, `weak`, `none`, `not_assessable` (scanned: OCR first).
2. Recommendation: `off` (structure is enough), `gaps` (only oversized or untitled regions), `full` (whole document).
3. Overrides, highest priority first: per-document, batch default, then the assessment. File
   `enrichment-overrides.json`: `{"batch_default": "auto|off|gaps|full", "documents": {"<source path>": "auto|off|gaps|full"}}`.
   An override cannot enrich a scanned document before OCR.
4. Ask the user one question at a time, with the recommendation as the default and the cost estimate shown:
   add the AI layer at all? for which documents? Skip questions when an override already answers them.
5. Generated files are reviewed and approved by a human before publication.

## Trust model

Authority, highest first: original source, deterministic extraction, AI topic restructuring, AI indexes and summaries.

AI files start with front matter: `content_type: ai_generated_navigation`, `trust_level: discovery_only`,
`authoritative: false`, `generated_from`, `source_document`, `extracted_content`, `source_sha256`, `generation_model`,
`prompt_version`, `generation_timestamp`, `source_pages`, plus the notice "AI-GENERATED NAVIGATION AID ... Do not treat it
as authoritative." Extracted files use `content_type: deterministic_extraction`, `trust_level: authoritative_extraction`,
`authoritative: true`. A different `source_sha256` marks generated files stale.

## Verification

`validate_ai_artifact` checks metadata, trust flags, the notice, `source_pages` range, links and staleness.
Run `pytest plugins/sharepoint-workbench/tests/test_enrichment_foundations.py`.

## References

- `scripts/enrichment/structure_quality.py`, `scripts/enrichment/provenance.py`, `scripts/enrichment/decompose.py`, `scripts/enrichment/navigation.py`
- [content-extract-pdf.md](content-extract-pdf.md) for `raw/page_map.json`
- [enrichment-trust-model.md](../enrichment-trust-model.md): trust hierarchy, metadata and workflow
- `scripts/enrichment/evaluation.py`: four-arm evaluation (`build_tasks`, `score_run`, `summarize`, `render_report`)
