# `normalized-source-document` v1

**Producer:** `source-document-extraction` (this plugin) — the authoritative
definition of this contract lives in this plugin's own package at
`src/source_document_extraction/contracts/normalized_source_document.py`,
not in any shared/top-level distribution. See
`docs/superpowers/plans/phase-4-5-evidence/wave-2-contract-materialization-correction.md`
for why: an independently installed plugin must not require an unpublished
sibling Python distribution to function.

**Consumers:** `knowledge-analysis`'s `recommend_from_normalized` (Wave 3).
A consumer plugin carries its own plugin-local copy of this schema
(generated/synced from this file, hash-checked for equivalence during
development) — it never imports this plugin's package at runtime.

## Wire format (dict, JSON-serializable)

| Field | Type | Description |
|---|---|---|
| `schema_version` | `str` | Always `"v1"` for this version. |
| `source_content_sha256` | `str` | SHA-256 hex digest of the source `.docx` file's raw bytes. |
| `markdown_text` | `str` | Full pandoc-extracted markdown text. |
| `media_files` | `list[str]` | Relative paths (POSIX, relative to the extracted `media/` dir) of every extracted media file. |
| `source_path` | `str` | The source `.docx` path as given to `extract_and_normalize`. |
| `source_size_bytes` | `int` | Source file size in bytes. |
| `dependencies.pandoc` | `dict` | `{available, version, path}` — the pandoc dependency probe result. |
| `headings` | `list[dict]` | `{level, text, path, occurrence}` per heading, in document order. |
| `heading_counts_by_level` | `dict[int, int]` | Heading count per level. |
| `repeated_heading_texts` | `dict[str, int]` | Heading text → occurrence count, for texts appearing more than once. |
| `repeated_heading_paths` | `list[list[str]]` | Full heading paths that occur more than once. |
| `images` | `dict` | `{count, formats}` — extracted image stats. |
| `raw_toc_detected` | `bool` | Whether a raw Word TOC field dump was detected. |
| `defect_signals` | `dict` | `{raw_toc_detected, glued_images, pandoc_attrs, bold_wrapped_headings}`. |
| `statistics` | `dict` | `{table_count, footnote_reference_count, footnote_definition_count, local_link_count, image_reference_count, generated_toc_entries_detected}`. |

## Producing this contract

```python
from source_document_extraction.extraction import extract_and_normalize

normalized = extract_and_normalize(source="intake/Manual.docx", output_dir="analysis/Manual")
```

## Validating

```python
from source_document_extraction.contracts.normalized_source_document import validate

validate(normalized)  # raises ValueError on missing/mismatched required fields
```
