---
name: render-content
plugin: knowledge-publication
description: Render an accepted canonical-package (and publication-map, for grouped packages) to a validated, atomically-promoted multipage-markdown publication output.
allowed-tools: Bash, Read
examples:
  - "python -c \"from knowledge_publication import render; render(package_dir, output_dir)\""
---

# Render Content

## Trigger and Purpose

Use this skill to load an already-accepted `canonical-package` from disk
(built and validated by `canonical-knowledge`) and render it to a
multipage-markdown publication output: one page per chunk, a
hierarchical/path-aware index, media copied and reference-rewritten,
internal links rewritten to page-relative targets, validated, and
atomically promoted.

This plugin never builds or validates a canonical package itself — that
is `canonical-knowledge`'s job. It consumes an already-promoted package.

## Public Interface

```python
from knowledge_publication import render

result = render(package_dir, output_dir)
# {"render_result": ..., "validation_report": ..., "promoted": bool, "output_dir": str}
```

- `package_dir` — path to an accepted `canonical-package` directory (the
  one `canonical-knowledge`'s `build_canonical_package` promoted).
- `output_dir` — path under which the render is staged and (on a PASS
  validation) atomically promoted to `output_dir / "rendered-output"`.
- Returns a dict with the `RenderResult`/`ValidationReport` contents,
  whether promotion happened, and the final output directory. See
  `references/contracts/rendered-output-profile.md` (symlinked into this
  skill folder — no repository-root or sibling-plugin lookup required).

A `FAIL` validation never promotes: the prior accepted render (if any)
under `output_dir` is left untouched, and the failed staging directory is
retained for diagnosis.

## Installation

```bash
pip install -e plugins/knowledge-publication
```

No other package needs to be installed first — this plugin has zero
dependency on any other workbench distribution or the repository root.

## Dependencies

None beyond the Python standard library.
