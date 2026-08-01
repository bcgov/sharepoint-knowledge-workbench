# Wave 1 Step 1 — `analyze_structure.py` Split Decision

**Date:** 2026-08-01
**Status:** ✓ APPROVED (human decision, 2026-08-01) — revises the original proposal below. See "Approved split (final)" section.

## Approved split (final)

The human reviewer approved a **more extraction-favoring split** than this document's original proposal, on the grounds that parsing headings and identifying source defects are part of producing the `normalized-source-document` contract, not semantic knowledge analysis:

- **`source-document-extraction` owns:** `_run_pandoc_raw`, `_normalize_heading_text`, `iter_heading_matches`, `parse_headings`, `_counts_by_level`, `_repeated_heading_texts`, `_repeated_paths`, `_image_stats`, `detect_raw_toc`, `detect_defect_signals` — every function that produces a source-level *observation* (heading structure, statistics, defect signals), regardless of whether it touches `pandoc` directly. These become part of `source_document_extraction.extraction.extract_and_normalize`'s output — the `normalized-source-document` contract itself is expanded to carry these observations, not just raw markdown text.
- **`knowledge-analysis` owns:** semantic/structural *interpretation* of those observations — topic-boundary reasoning and `recommend_strategy` — producing the `analysis-plan` contract. `knowledge_analysis.analysis.recommend_from_normalized` consumes the expanded `normalized-source-document` contract (headings/statistics/defects already computed) and reasons about strategy from it; it does not re-parse or re-detect anything already produced upstream.
- **`AnalysisResult`** (the current combined dataclass) is not preserved as a single type — it splits along the same boundary: the extraction-side fields become part of `normalized-source-document`, the analysis-side fields (recommended strategy, defect-driven human-review flags) become part of `analysis-plan`.
- **`cmd_analyze`** (in `cli.py`, not `analyze_document` — corrected function name per human review) is **preserved as the temporary compatibility orchestrator**, calling `extract_and_normalize` then `recommend_from_normalized` in sequence. It stays in `plugins/docx-to-content/scripts/cli.py` per `cli.py`'s own disposition ("compatibility orchestrator, not moved") until Wave 7/8 retirement.

This supersedes the original proposal below, which is retained for the record (it drew the line one function later, treating heading-parsing/statistics as analysis rather than extraction — the human reviewer's correction is the more defensible split, and is what Waves 2/3 implement).

---

## Original proposal (superseded, retained for the record)

## Provenance note

The plan instructs "same content as Revision 2 Wave 1 Step 1, unchanged." A repository-wide search (`git log --all`, `find -iname "*revision-2*"`) found no trace of a Revision 2 plan document anywhere in this repository's history — only Revision 3 (the current plan) was ever committed. That referenced content could not be located and is not reproduced here as if recovered; this decision is derived fresh from the real file, grounded in Wave 0's evidence.

## What `analyze_structure.py` actually does (577 lines, 14 top-level functions + 1 dataclass)

Read directly from `plugins/docx-to-content/scripts/analyze_structure.py`:

| Function | Responsibility |
|---|---|
| `_run_pandoc_raw` | Invokes `pandoc` directly to produce raw markdown from the source `.docx` — a source-format extraction operation, not analysis. |
| `_normalize_heading_text`, `iter_heading_matches`, `parse_headings` | Parse heading structure out of already-extracted markdown text. |
| `_counts_by_level`, `_repeated_heading_texts`, `_repeated_paths`, `_image_stats`, `detect_raw_toc`, `detect_defect_signals`, `compute_statistics` | Analyze the parsed structure for statistics and defects (repeated headings, raw TOC dumps, image issues). |
| `recommend_strategy` | Recommends a chunking/grouping strategy from the computed statistics. |
| `analyze_document` | Top-level orchestrator: calls `_run_pandoc_raw`, then the parsing/statistics/recommendation functions, and returns an `AnalysisResult`. |

## Proposed split

This file already has a natural seam at exactly the point Wave 0's edge classification independently flagged (`analyze_structure.py` touches `SOURCE_FORMAT_COUPLING`-classified edges into `dependencies.py`, `emf_convert.py`, `pandoc_validate.py` — all `source-document-extraction`-owned per the plan's Known File Inventory table):

- **`source-document-extraction`** gets `_run_pandoc_raw` — the actual pandoc invocation. This becomes (part of) `source_document_extraction.extraction.extract_and_normalize`'s implementation, matching the Wave 2 table's stated public interface function and the `normalized-source-document` contract it produces.
- **`knowledge-analysis`** gets everything downstream of raw extraction: `_normalize_heading_text`, `iter_heading_matches`, `parse_headings`, all statistics/defect-detection functions, `recommend_strategy`, and the `AnalysisResult` dataclass. These operate purely on already-extracted markdown text + a media directory — never touch the source `.docx` or invoke `pandoc` directly. This becomes `knowledge_analysis.analysis.recommend_from_normalized`, consuming the `normalized-source-document` contract and producing `analysis-plan`, matching the Wave 3 table exactly.
- `analyze_document`, the current top-level orchestrator, is **not preserved as a single function** — it becomes the composition `recommend_from_normalized(extract_and_normalize(source, output_dir))`, performed by whichever caller needs both steps (the compatibility shim in Wave 7, or a future orchestration skill), not duplicated inside either plugin.

## Why this split, not an alternative

An alternative would keep `analyze_document`'s full pipeline (extraction + analysis) inside `knowledge-analysis` and have it internally shell out to `source-document-extraction`'s installed package for the raw-pandoc step. Rejected: that would make `knowledge-analysis` responsible for driving extraction, which contradicts the Wave 2-5 contract table's own division (`source-document-extraction` produces `normalized-source-document`; `knowledge-analysis` only ever consumes it) and would require `knowledge-analysis` to depend on `source-document-extraction`'s implementation package, which the plan's dependency-boundary rule prohibits (only the contracts distribution may be a cross-plugin dependency).

## Impact on Wave 0 evidence

Edges touching `analyze_structure.py` in `wave-0-classified-edges.json` currently carry `proposed_source_domain: UNRESOLVED` (or `UNRESOLVED` as target), per the plan's own Known File Inventory marking this file "split." Once this decision is approved, Wave 2/3's extraction waves resolve those specific edges by moving the code to the domain the split above assigns — no Wave 0 edge classification needs to be redone; Wave 0 already correctly deferred the decision to this step rather than guessing.
