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

Implemented: the structure-quality assessment, per-document and batch overrides, the page map, trust metadata, the
notice, and the provenance, staleness and verbatim-slice validators. **Not implemented yet:** the provider interface,
decomposition, summaries, indexes and evaluation mode. Do not offer generation until those land.

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

- `scripts/enrichment/structure_quality.py`, `scripts/enrichment/provenance.py`
- [content-extract-pdf.md](content-extract-pdf.md) for `raw/page_map.json`
