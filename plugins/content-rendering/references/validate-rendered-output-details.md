# Rendered output validation details

## Contents

- [What is validated](#what-is-validated)
- [Interface](#interface)
- [Failure behavior](#failure-behavior)
- [Dependencies](#dependencies)

## What is validated

A staged rendered-output directory (not an already-promoted one), produced by
`content-render-multipage-markdown` or `content-render-sharepoint-aspx`, against the `CanonicalPackage` it
was rendered from. Detections, for both formats:

- missing index or page-manifest, missing `pages/` directory;
- missing or orphan pages, page-count mismatch;
- broken local links and media references;
- path traversal or absolute-path references escaping the rendered output;
- stale source content: the canonical package was reconverted after this render was staged, detected via
  `render-result.json`'s recorded `source_content_sha256`;
- rendered page content not traceable back to its source chunk.

Every issue is `severity="error"`. Status is always `PASS` or `FAIL`, never `WARN`.

## Interface

```python
from renderers.validate_rendered import (
    validate_rendered_output,       # Markdown: (rendered_dir, package) -> ValidationReport
    validate_aspx_rendered_output,  # ASPX: (rendered_dir, package) -> ValidationReport
    render_and_promote,             # Markdown: full stage -> validate -> promote pipeline
    render_and_promote_aspx,        # ASPX: full stage -> validate -> promote pipeline
)

result, report, promoted, output_dir = render_and_promote(package, output_root)
# or, for the ASPX renderer:
result, report, promoted, output_dir = render_and_promote_aspx(package, output_root)
```

## Failure behavior

A `FAIL` never promotes. The prior accepted render, if any, under `output_root / "rendered-output"` is left
untouched, and the failed staging directory is retained for diagnosis.

## Dependencies

Python standard library only for Markdown validation. ASPX traceability re-derives the expected page content
with `pandoc`. A pandoc failure during that recomputation is treated as "cannot verify", not as a false
`page_content_not_traceable` finding.
