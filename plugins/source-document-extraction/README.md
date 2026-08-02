# source-document-extraction

Source-format inspection and extraction for the SharePoint Knowledge
Workbench. Runs `pandoc` once against a source `.docx` and produces a
`normalized-source-document` v1 contract (markdown text, media files, source
content hash, heading structure, raw-TOC/defect signals, extended
statistics) — the single upstream extraction step every other domain plugin
(`document-structure-analysis`, `structured-content-assembly`, `structured-content-rendering`)
builds on.

This plugin is the **producer** of `normalized-source-document`: the
authoritative schema lives inside this plugin at
`scripts/schema/normalized_source_document.py` and
`references/contracts/normalized-source-document.md`, not in a shared
top-level distribution. This plugin has **zero dependency on any other
workbench distribution or the repository root** — it installs and runs
standalone. See
`docs/superpowers/plans/phase-4-5-evidence/wave-2-contract-materialization-correction.md`
for why.

**Flat `scripts/` layout** (matching `docx-to-content`'s existing
convention — bare module names, no enclosing package-name folder):

```
plugins/source-document-extraction/
├── scripts/
│   ├── extraction.py            # public interface: extract_and_normalize()
│   ├── dependencies.py
│   ├── emf_convert.py
│   ├── heading_parsing.py
│   ├── path_safety.py
│   ├── schema/                  # this plugin's own schema for what it produces
│   │   ├── normalized_source_document.py
│   │   └── shared.py
│   └── pandoc/                  # pandoc cleanup + validation, one family
│       ├── attrs.py
│       ├── footnotes.py
│       ├── heading_emphasis.py
│       ├── images.py
│       ├── tables.py
│       ├── toc.py
│       └── validate.py
├── references/contracts/        # canonical docs -- symlinked into skills/extract-docx/ via symlink_manager.py
├── skills/extract-docx/
└── tests/
```

Part of Phase 4.5's decomposition of the combined `docx-to-content` plugin
into four independently installable domain plugins — see
`docs/superpowers/plans/2026-08-01-phase-4-5-core-knowledge-plugin-domain-refactoring.md`.

## Install

```bash
pip install -e plugins/source-document-extraction
```

No other package needs to be installed first.

## Public interface

```python
from extraction import extract_and_normalize

normalized = extract_and_normalize(source="intake/Manual.docx", output_dir="analysis/Manual")
```

Returns a `normalized-source-document` v1 dict, validated against this
plugin's own `schema.normalized_source_document.validate`.

## Dependencies

Requires `pandoc` on PATH. `emf_convert` also uses `soffice` (LibreOffice)
when legacy `.emf`/`.wmf` media conversion is needed — see the
repository's `DEPENDENCIES.md`.

## Tests

```bash
cd plugins/source-document-extraction
pip install -e .
python -m pytest tests/ -v
```

## Isolated-install proof

Proves this plugin installs and runs with **no other workbench
distribution present** (no sibling plugin, no repository-root Python
package):

```bash
cd tools/phase-4-5-core-plugin-refactoring
python isolated_install_check.py --plugin source-document-extraction --import-package extraction
```
