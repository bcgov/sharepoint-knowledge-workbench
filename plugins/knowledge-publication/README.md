# knowledge-publication

Renders a validated `canonical-package` (and its `publication-map`, for
grouped packages) to a multipage-markdown publication output, for the
SharePoint Knowledge Workbench.

This plugin is the **producer** of `rendered-output-profile`
(`RenderResult`): the authoritative schema lives inside this plugin at
`scripts/render_result.py` and `references/contracts/rendered-output-profile.md`,
not in a shared top-level distribution. This plugin has **zero dependency
on any other workbench distribution or the repository root** — it
installs and runs standalone. It carries plugin-local duplicate copies of
everything it needs to load and validate a canonical package
(`canonical_package.py`, `dispositions.py`, `hashing.py`,
`publication_map.py`, `atomic_output.py`, `path_safety.py`, and a
consumer copy of the `canonical-package`/`publication-map` schemas under
`canonical_schema/`) rather than importing canonical-knowledge's or
source-document-extraction's packages at runtime.

**Flat `scripts/` layout** (matching the other three domain plugins'
convention — bare module names, cohesive multi-file families grouped into
subfolders):

```
plugins/knowledge-publication/
├── scripts/
│   ├── knowledge_publication.py  # public interface: render()
│   ├── render_result.py          # this plugin's own RenderResult contract
│   ├── canonical_package.py      # local duplicate: canonical-package loader
│   ├── dispositions.py           # local duplicate: warning-disposition reconciliation
│   ├── hashing.py                # local duplicate: canonical-JSON hashing
│   ├── publication_map.py        # local duplicate: publication-map loader
│   ├── atomic_output.py          # local duplicate: staging/promotion + generator-info
│   ├── path_safety.py            # local duplicate: media/link path-safety classification
│   ├── canonical_schema/         # consumer copy of canonical-package/publication-map schemas
│   └── renderers/
│       ├── protocol.py            # Renderer structural protocol + registry
│       ├── multipage_markdown.py  # the concrete multipage-markdown Renderer
│       └── validate_rendered.py   # render validator + render_and_promote
├── references/contracts/
├── skills/render-content/
└── tests/
```

Every "local duplicate" module above is a **deliberate** copy of code
that also exists in `canonical-knowledge` or `source-document-extraction`,
not a cross-plugin import — per the dependency-boundary rule (spec
Section 11), a real domain plugin never imports another domain plugin's
implementation package. See
`docs/superpowers/plans/phase-4-5-evidence/wave-5-knowledge-publication-split-decision.md`
for the rationale.

Part of Phase 4.5's decomposition of the combined `docx-to-content` plugin
into four independently installable domain plugins — see
`docs/superpowers/plans/2026-08-01-phase-4-5-core-knowledge-plugin-domain-refactoring.md`.

## Install

```bash
pip install -e plugins/knowledge-publication
```

No other package needs to be installed first.

## Public interface

```python
from knowledge_publication import render

result = render(package_dir, output_dir)
# {"render_result": ..., "validation_report": ..., "promoted": bool, "output_dir": str}
```

`package_dir` must be an accepted `canonical-package` directory (as
produced by `canonical-knowledge`'s `build_canonical_package`).

## Tests

```bash
cd plugins/knowledge-publication
pip install -e .
python -m pytest tests/ -v
```

## Isolated-install proof

Proves this plugin installs and runs with **no other workbench
distribution present** (no sibling plugin, no repository-root Python
package):

```bash
cd tools/phase-4-5-core-plugin-refactoring
python isolated_install_check.py --plugin knowledge-publication --import-package knowledge_publication
```
