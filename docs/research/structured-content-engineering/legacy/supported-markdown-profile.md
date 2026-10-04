# Supported Markdown Profile

This document defines the subset of Markdown that authored canonical
content is expected to use. Staying inside this profile is what keeps
content renderable across every output format the pipeline supports.

## Relative-path rules for images and links

- **Images**: reference image files with a relative path from the topic
  file, such as `../media/intake-form.png`.
  Never use an absolute filesystem path, a `file://` URL, or a bare
  filename that assumes a specific working directory.
- **Links to other topics**: reference other topic files with a relative
  path to that file, such as `related-topic.md`. Never
  hardcode a rendered-output URL, page number, or site path — the same
  relative reference must resolve correctly regardless of which output
  format the content is eventually rendered to.
- **External links**: `http://` and `https://` links to resources outside
  this content set are permitted as-is.

## Permitted constructs

- Headings (`#` through `######`), used to express real document
  structure — not for visual emphasis.
- Paragraphs, bold, italic, inline code.
- Ordered and unordered lists, including nested lists.
- Fenced code blocks with a language hint where applicable.
- Tables (pipe-table syntax).
- Relative image references and links to other topic files.
- Semantic callouts in the `> [!TYPE]` form documented in
  `templates/components/README.md`.
- Blockquotes for quoted material (not for callouts — use the semantic
  callout syntax instead).

## Prohibited constructs

- Raw HTML blocks or inline HTML (breaks portability across output
  formats).
- Absolute filesystem paths or `file://` URLs.
- Embedded scripts, iframes, or any executable content.
- Hand-written tables of contents, page numbers, or "next/previous"
  navigation links (these are code-generated — see
  `references/generated-elements.md`).
- Word-artifact bookmark links (e.g. links targeting `#_Toc...` anchors)
  — these are stripped by the conversion pipeline and must never be
  authored directly.
- Non-semantic emphasis used to simulate a callout (e.g. **Warning:** in
  bold text instead of a `> [!WARNING]` callout).
