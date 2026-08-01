# Wave 2 — Test Migration Ledger (`source-document-extraction`)

Per the Wave 0 test ledger's `SOURCE_DOCUMENT_EXTRACTION`-tagged entries.

## Whole files moved (`git mv`), imports fixed to package-relative form

| Old path | New path |
|---|---|
| `plugins/docx-to-content/tests/unit/test_attrs.py` | `plugins/source-document-extraction/tests/unit/test_attrs.py` |
| `plugins/docx-to-content/tests/unit/test_dependencies.py` | `plugins/source-document-extraction/tests/unit/test_dependencies.py` |
| `plugins/docx-to-content/tests/unit/test_emf_convert.py` | `plugins/source-document-extraction/tests/unit/test_emf_convert.py` |
| `plugins/docx-to-content/tests/unit/test_footnotes.py` | `plugins/source-document-extraction/tests/unit/test_footnotes.py` |
| `plugins/docx-to-content/tests/unit/test_heading_emphasis.py` | `plugins/source-document-extraction/tests/unit/test_heading_emphasis.py` |
| `plugins/docx-to-content/tests/unit/test_images.py` | `plugins/source-document-extraction/tests/unit/test_images.py` |
| `plugins/docx-to-content/tests/unit/test_pandoc_validate.py` | `plugins/source-document-extraction/tests/unit/test_pandoc_validate.py` |
| `plugins/docx-to-content/tests/unit/test_tables.py` | `plugins/source-document-extraction/tests/unit/test_tables.py` |
| `plugins/docx-to-content/tests/unit/test_toc.py` | `plugins/source-document-extraction/tests/unit/test_toc.py` |

## Per-test split from `test_analyze_structure.py`

`test_analyze_structure.py`'s `SOURCE_DOCUMENT_EXTRACTION`-tagged tests (20
of 29) were rewritten (not `git mv`'d — the underlying function they call,
`analyze_document`, is not preserved; they now exercise
`extract_and_normalize` and its dict shape) into
`plugins/source-document-extraction/tests/unit/test_extraction.py`. The
remaining 9 `KNOWLEDGE_ANALYSIS`/`CROSS_CUTTING`-tagged tests stay in
`plugins/docx-to-content/tests/unit/test_analyze_structure.py`, still
exercising `analyze_structure.analyze_document` (the still-unsplit
compatibility orchestrator, pending Wave 3).

`test_regression_pipeline.py` (`TestRegressionPipeline::test_all_modules_compose_without_conflict`,
tagged `SOURCE_DOCUMENT_EXTRACTION`) was left in place in
`docx-to-content` — it composes multiple `pandoc_fixes` modules through the
compatibility shim and remains valid coverage of the shim itself; its
functional coverage is otherwise fully duplicated by the individual
`pandoc_fixes` test files already moved above.

## Code moved (`git mv`, no import changes needed — stdlib-only)

`dependencies.py`, `emf_convert.py`, `path_safety.py`, `pandoc_validate.py`,
`pandoc_fixes/{attrs,footnotes,heading_emphasis,images,tables,toc}.py`.

## Code extracted (not `git mv` — split out of `analyze_structure.py`)

`_run_pandoc_raw`, `_normalize_heading_text`, `iter_heading_matches`,
`parse_headings`, `_counts_by_level`, `_repeated_heading_texts`,
`_repeated_paths`, `_image_stats`, `detect_raw_toc`, `detect_defect_signals`,
`compute_statistics` → `plugins/source-document-extraction/src/source_document_extraction/{extraction,heading_parsing}.py`,
per the approved split
(`wave-1-analyze-structure-split-decision.md`). `analyze_structure.py`
retains `analyze_document`, `recommend_strategy`, `AnalysisResult`, and
`MIN_*` constants, importing the moved functions from the installed
`source_document_extraction` package rather than duplicating them
(compatibility shim, retire per Wave 7/8).

## Verification

- `plugins/source-document-extraction` isolated suite: **78 passed** (real
  wheel install, `isolated_install_check.py --plugin source-document-extraction
  --import-package source_document_extraction` exit 0).
- `plugins/docx-to-content` full suite with `source-document-extraction`
  `pip install -e`'d: **452 passed, 1 skipped** (down from 529 passed/1
  skipped — the difference is tests physically relocated, not lost;
  78 + 452 accounts for the full prior 529, with 1 net new test added in
  the new plugin proving the `normalized-source-document` contract shape).
- `check_no_prohibited_imports` / `check_no_repo_root_import_in_production_code`
  against `plugins/source-document-extraction/src/`: zero violations.
