---
name: content-extract-pdf
plugin: sharepoint-document-conversion
description: Extracts a text-layer source .pdf with PyMuPDF into the same normalized-source-document contract as the DOCX extractor (markdown text, media files, heading structure, statistics), plus page numbers per heading. Use as the first step when converting a PDF; scanned PDFs need OCR first. Observes the source only; never interprets strategy or writes structured content.
allowed-tools: Bash, Read
examples:
  - "python3 -c \"import sys; sys.path.insert(0, 'scripts/extraction'); from pdf_extraction import extract_pdf_and_normalize; extract_pdf_and_normalize('intake/Manual.pdf', 'analysis/Manual')\""
---

# Extract PDF

Extract a text-layer `.pdf` into a `normalized-source-document` v1 contract that structure analysis
consumes unchanged.

## Constraints

- Observe only. Never choose a strategy, propose topic boundaries, or write structured content.
- Requires PyMuPDF (`pip install pymupdf`); otherwise `dependencies.MissingDependencyError`.
- Scanned PDFs (no text layer) are not converted: `defect_signals.no_text_layer` is `true` and the
  markdown is empty. OCR them first and extract the searchable PDF.
- `heading_source` is `outline` (PDF bookmarks, reliable), `inferred` (font-size/bold heuristic: a human
  must review the heading list before assembly) or `none` (no headings found; single-topic document).
- Tables are detected with PyMuPDF `find_tables()` and written as GFM pipe tables (first row = header).
  A table that continues on the next page is merged into one (repeated header row dropped). Cells with
  several lines use `<br>`. Merged cells (rowspan/colspan) come back empty and nested headers are not
  represented; borderless tables may be missed. Report these as limits, not as preserved.
- Image alt text is the nearby `Figure/Chart/...` caption, else `Image on page N`. Pass `ocr=True` (needs tesseract,
  found on PATH, `$TESSERACT_CMD` or the default Windows install) to add a `> Text in image:` line after each
  image; OCR output can contain misread characters and skips images with too little text. Photos and diagrams
  are not described. Not yet handled by this mode: hyperlinks. Do not claim they were preserved.

## Quick start

```python
import sys; sys.path.insert(0, "scripts/extraction")
from pdf_extraction import extract_pdf_and_normalize
result = extract_pdf_and_normalize(source="intake/Manual.pdf", output_dir="analysis/Manual")
```

## Workflow

1. Confirm the `.pdf` exists and choose an `output_dir`; `raw/extracted.md` and `raw/media/` are written there.
2. Call `extract_pdf_and_normalize(source, output_dir)` (add `ocr=True` to read text inside images).
3. Report the contract plus PDF-only fields: `source_format`, `page_count`, `heading_source`,
   `heading_pages` (parallel to `headings`, absent if the counts disagree) and `warnings`.
4. Hand the result to the analyze mode; do not interpret it here.

## Verification

Confirm the dict validates against the bundled schema, `raw/extracted.md` exists, and every
`![](media/...)` reference resolves under `raw/media/`. Report `warnings` (outline headings not found in the
page text, skipped contents pages) as observed, not as decisions.
