# Output Formats, Image Rules & B.C. Design System Reference

## Contents

- [Interactive format choice](#interactive-format-choice)
- [Supported inputs and build options](#supported-inputs-and-build-options)
- [Output formats](#output-formats)
- [B.C. Design System reference](#bc-design-system-reference)
- [Verification & link check](#verification--link-check)

## Interactive format choice

Skip asking when the user already named the format (`"convert to html"`, `"make it Markdown for my agents"`). Otherwise ask before anything else:
- **(a) Agent-optimized Markdown** (`--format agent-md`): knowledge pages for AI agents and search (front matter, stable headings, index, `chunks.jsonl`).
- **(b) Nicely formatted HTML** (`--format html`): a readable static HTML5 site for people (navigation, styled tables, B.C. Design System typography).

`--format markdown-basic` produces plain linked Markdown without front matter when explicitly requested.

## Supported inputs and build options

- Single `.pdf` file or folder of `.pdf` files (text-layer PDFs with bookmarks, distinct heading font sizes, or weak structure).
- Optional `build` flags: `--no-images`, `--min-image-px N` (default 64; < 24 pt always skipped), `--vector-figures`, `--image-dpi N` (default 150), `--org "Name"`, `--doc-date "Month YYYY"`, `--no-pdf-copy`.

## Output formats

Both formats write one page per topic, `images/` (when extractable), a copy of the PDF (for `#page=N` links), `topics.xlsx`, `manifest.json`, and `validation.json`.

- **Images:** `images/<topic-file>-p<page>-<n>.<ext>`. JPEGs saved byte-for-byte; others decoded to PNG (rasterized fallback). Deduplicated by SHA-256; decorative/repeated logos (>= 40% of pages and >= 3 pages) skipped; nearby `Figure/Image N` lines become captions/alt text.
- **Agent-optimized Markdown (`--format agent-md`):** `index.md`, `01-<topic>.md ...` (YAML front matter: `type, topic_id, title, source_file, source_title, page_start, page_end, topic_number, topic_count, parent_topic, previous, next, summary, keywords, tables, images, images_not_extracted, topic_source`), `chunks.jsonl` (retrieval chunks, tables never split), `images/`, `validation.md`.
- **Formatted HTML (`--format html`):** `index.html` (cover + topic card grid), `01-<topic>.html ...` (header, subheader, accordion sidebar, breadcrumbs, summary callout, "On this page" list, content, prev/next buttons, footer), `images/`, `style.css` (from `assets/`), `validation.html`. Works offline with zero scripts.

## B.C. Design System reference

Mirrors B.C. Design System tokens v5.1.0 / component library 0.9.0 (Nov 2026). All tokens live in `assets/bc_tokens.css`; component styles in `assets/bc_components.css` use `var(--...)` only.
- **Font:** `"BC Sans","Noto Sans",Verdana,Arial,sans-serif`; weights 300/400/700; body `1rem/1.5`.
- **Colours:** primary blue `#013366` (hover `#1E5189`, pressed `#01264C`), gold `#FCBA19`, text `#2D2D2D`/`#474543`, link `#255A90`, focus `#2E5DD7`, border `#D8D8D8`. Light-themed only (no dark mode).
- **Accessibility:** WCAG 2.1 AA (`lang="en-CA"`, skip link, `aria-current`, 4.5:1 contrast, alt text, responsive & print styles). Header is text-only unless `--ds-logo` is supplied.

## Verification & link check

Every `build` and `publish` runs `scripts/check_links.py`:
- Every relative `href`/`src`/Markdown link resolves (percent-decoded) and every `#anchor` exists.
- Every `<pdf>#page=N` has `N` within `1..page_count` and the PDF copy beside the pages.
- Every page has exactly one `<h1>` and no skipped heading levels.
- `chunks.jsonl`, `manifest.json`, and front matter `previous`/`next`/`images` resolve.

Broken links or heading problems set `status` to `FAIL` (exit code 2, staging folder kept).
