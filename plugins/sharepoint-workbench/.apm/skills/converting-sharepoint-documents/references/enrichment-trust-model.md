# Enrichment trust model and optional workflow

The optional enrichment layer adds AI-generated navigation aids on top of deterministic extraction. It never replaces it.

## Contents

- [Trust hierarchy](#trust-hierarchy)
- [Marking and metadata](#marking-and-metadata)
- [Optional workflow](#optional-workflow)
- [Guardrails](#guardrails)
- [Evaluation](#evaluation)
- [Limits](#limits)

## Trust hierarchy

1. Original PDF or authoritative source.
2. Deterministically extracted or OCR content (`raw/extracted.md`, `raw/page_map.json`).
3. AI topic restructuring (`ai-navigation/topics/`): verbatim slices of level 2 cut at AI-chosen boundaries.
4. AI indexes and summaries (`ai-navigation/index.md`, `chapters/`, `navigation.json`).

Levels 3 and 4 are for finding content. Facts and citations come from levels 1 and 2.

## Marking and metadata

Every AI file has front matter (`content_type: ai_generated_navigation`, `trust_level: discovery_only`,
`authoritative: false`, `generated_from`, `source_document`, `extracted_content`, `source_sha256`, `generation_model`,
`prompt_version`, `generation_timestamp`, `source_pages`, `uncertain_boundary`) and a visible "AI-GENERATED NAVIGATION
AID" notice. Deterministic output is described by `deterministic_metadata` (`content_type: deterministic_extraction`,
`trust_level: authoritative_extraction`, `authoritative: true`).

## Optional workflow

1. Extract deterministically (unchanged; the AI layer can be skipped entirely).
2. `assess_structure` scores the document. Good bookmarks and headings are kept; AI is recommended only for gaps or
   weak or absent structure. Overrides per document or batch: `enrichment-overrides.json`.
3. Ask the user, one question at a time with the cost shown: add the AI layer, and for which documents. Record the
   answer with `record_consent`. The provider sees the document text.
4. Decompose (`decompose.py`), summarise and index (`navigation.py`): the host agent answers request files.
5. A human reviews and `approve`s; `publish` copies only valid, non-stale output to a separate folder.

## Guardrails

Extraction is never modified; output goes to `ai-navigation/`; page provenance is kept; uncertain titles and boundaries
are flagged; model, prompt version, timestamp and hashes are recorded; changed source or extraction marks output stale;
regeneration leaves authoritative files alone; summaries may not copy long source passages; links and page references
are validated before publication.

## Evaluation

`evaluation.py` compares four arms (native PDF, large Markdown, topic Markdown, topic Markdown with navigation) on
retrieval accuracy, completeness, citation correctness, tokens, latency, files retrieved, answer length and failures to
reach authoritative content. Agents write run records; scoring is deterministic.

## Limits

Summaries can still be wrong. Boundaries snap to blank-line block edges, so very long unbroken blocks stay together.
Evaluation results apply to the tested corpus, questions and agent only.
