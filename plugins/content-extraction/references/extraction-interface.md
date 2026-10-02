# DOCX extraction interface

## Contents

- [Public interface](#public-interface)
- [Arguments and return value](#arguments-and-return-value)
- [Errors](#errors)
- [Scope](#scope)
- [Contract](#contract)
- [External tools](#external-tools)

## Public interface

```python
from extraction import extract_and_normalize

result = extract_and_normalize(source="intake/Manual.docx", output_dir="analysis/Manual")
```

## Arguments and return value

- `source`: path to the source `.docx` file; it must exist and be a file.
- `output_dir`: directory the transitory `raw/` pandoc output is written to; created if missing.
- Returns a `normalized-source-document` v1 dict, validated against this plugin's own bundled schema:
  raw markdown text (a single `pandoc` pass), the extracted media file list, a source content hash, and
  source-level observations (heading structure, image stats, raw-TOC and defect signals, extended
  statistics) that the `content-structure-analysis` plugin's `recommend_from_normalized` consumes without
  re-parsing.

## Errors

- `FileNotFoundError` if `source` does not exist.
- `dependencies.MissingDependencyError` if `pandoc` is not on `PATH`.

## Scope

This skill only observes the source. It never interprets strategy (single or chunked), never proposes
topic boundaries, and never writes structured content.

## Contract

`references/contracts/normalized-source-document.md` describes the output shape. No repository-root or
sibling-plugin lookup is required.

## External tools

`pandoc` on `PATH`. No other workbench package is required; the plugin has zero dependency on any other
distribution.
