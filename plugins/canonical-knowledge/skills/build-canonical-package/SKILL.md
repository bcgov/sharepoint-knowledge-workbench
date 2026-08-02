---
name: build-canonical-package
plugin: canonical-knowledge
description: Build a validated, atomically-promoted canonical-content package from a confirmed analysis-plan and a source document.
allowed-tools: Bash, Read
examples:
  - "python -c \"from canonical_knowledge import build_canonical_package; build_canonical_package(plan, source_dir, output_dir)\""
---

# Build Canonical Package

## Trigger and Purpose

Use this skill to convert a *confirmed* `analysis-plan` v1 dict (produced
by `knowledge-analysis`'s `recommend_from_normalized` plus human
confirmation) into a validated `canonical-package` on disk: pandoc
extraction, markdown cleanup, heading-based chunking, media
inventory/copy/rewrite, manifest assembly, validation, and atomic
promotion. For a `strategy: "grouped"` plan, also builds and validates a
`publication-map`.

This plugin never constructs or confirms a plan itself — that is
`knowledge-analysis`'s job. It consumes an already-confirmed plan dict.

## Public Interface

```python
from canonical_knowledge import build_canonical_package

result = build_canonical_package(analysis_plan, source_dir, output_dir)
# {"manifest": ..., "validation_report": ..., "promoted": bool, "package_dir": str}
```

- `analysis_plan` — a confirmed `analysis-plan` v1 dict
  (`confirmation.status == "confirmed"`).
- `source_dir` — path to the directory containing the source `.docx`
  referenced by the plan.
- `output_dir` — path under which the canonical package is staged and
  (on a PASS validation) atomically promoted.
- Returns a dict with the `Manifest`/`ValidationReport` contents,
  whether promotion happened, and the final package directory. See
  `references/contracts/canonical-package.md` and
  `publication-map.md` (symlinked into this skill folder — no
  repository-root or sibling-plugin lookup required).

A `FAIL` validation never promotes: the prior accepted package (if any)
under `output_dir` is left untouched, and the failed staging directory is
retained for diagnosis.

## Installation

```bash
pip install -e plugins/canonical-knowledge
```

No other package needs to be installed first — this plugin has zero
dependency on any other workbench distribution or the repository root.

## Dependencies

`pandoc` and (for legacy `.emf` media) LibreOffice's `soffice` must be on
`PATH` — see `DEPENDENCIES.md` at the repository root.
