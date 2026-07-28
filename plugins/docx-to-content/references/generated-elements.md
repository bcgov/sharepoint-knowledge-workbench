# Generated Elements

These elements are produced by code from canonical content — authors never
hand-write them, and hand-writing one only creates drift the next time
content is rendered (see `references/content-authoring-guide.md`).

| Element | Canonical source | Status |
|---|---|---|
| Table of contents | Chunk order and `source_heading_path` in the canonical package's `manifest.json` | implemented (multipage-markdown renderer's `index.md`) |
| Navigation (page-to-page links) | Local links rewritten by the renderer from the canonical package's chunk-to-chunk references | implemented (multipage-markdown renderer) |

Only the elements marked `implemented` above are actually produced by the
Phase 1 pipeline today (the `multipage-markdown` renderer). No other
generated element — page numbering, breadcrumb trails, print headers,
cross-format search indexes, or anything else — exists yet; do not assume
or document any of those as implemented until a renderer actually produces
them. See `references/future-output-profiles.md` for elements planned for
future output profiles.
