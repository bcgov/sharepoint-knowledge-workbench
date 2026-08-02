# structured-content-rendering

Renders a validated `canonical-package` (and its `publication-map`, for
grouped packages) to a multipage-markdown publication output, for the
SharePoint Knowledge Workbench.

This plugin is the **producer** of `rendered-output-profile`
(`RenderResult`): the authoritative schema lives inside this plugin at
`scripts/render_result.py` and `references/contracts/rendered-output-profile.md`,
not in a shared top-level distribution. This plugin has **zero dependency
on any other workbench distribution or the repository root at
install/runtime** — it installs and runs standalone. Everything it needs
to load and validate a canonical package (`canonical_package.py`,
`dispositions.py`, `hashing.py`, `publication_map.py`, `atomic_output.py`,
`path_safety.py`, and the `canonical-package`/`publication-map` schemas
under `canonical_schema/`) is a **managed cross-plugin file-level
symlink** to `structured-content-assembly`'s or `source-document-extraction`'s
canonical source (see `symlinks.json`), not a hand-maintained duplicate —
`setuptools` dereferences each symlink into a real, independent file when
building this plugin's wheel, so the installed/distributed artifact never
depends on the producer plugin being present at runtime.

**Flat `scripts/` layout** (matching the other three domain plugins'
convention — bare module names, cohesive multi-file families grouped into
subfolders):

```
plugins/structured-content-rendering/
├── scripts/
│   ├── structured_content_rendering.py  # public interface: render()
│   ├── render_result.py          # this plugin's own RenderResult contract (real file)
│   ├── canonical_package.py      # [symlink -> structured-content-assembly is the canonical owner]
│   ├── dispositions.py           # [symlink -> structured-content-assembly is the canonical owner]
│   ├── hashing.py                # [symlink -> structured-content-assembly is the canonical owner]
│   ├── publication_map.py        # [symlink -> structured-content-assembly is the canonical owner]
│   ├── atomic_output.py          # [symlink -> structured-content-assembly is the canonical owner]
│   ├── path_safety.py            # [symlink -> source-document-extraction is the canonical owner]
│   ├── canonical_schema/         # [symlinks -> structured-content-assembly's canonical_schema/*]
│   └── renderers/                 # real files (this plugin's own domain logic)
│       ├── protocol.py            # Renderer structural protocol + registry
│       ├── multipage_markdown.py  # the concrete multipage-markdown Renderer
│       └── validate_rendered.py   # render validator + render_and_promote
├── references/contracts/
├── skills/render-structured-content/
└── tests/
```

Modules marked `[symlink -> ...]` above are managed via
`.agents/skills/symlink-manager/scripts/symlink_manager.py` — per the
dependency-boundary rule (spec Section 11), a real domain plugin never
imports another domain plugin's implementation package *at runtime*, but
the underlying source file is shared at the filesystem/build level, so
there is exactly one editable copy of each. See
`docs/superpowers/plans/phase-4-5-evidence/wave-9-duplication-remediation-report.md`
for the full rationale and verification evidence (this superseded the
original hand-duplication approach recorded in
`wave-5-knowledge-publication-split-decision.md`, using the plugin name in
effect at that time).

Part of Phase 4.5's decomposition of the combined `docx-to-content` plugin
into four independently installable domain plugins — see
`docs/superpowers/plans/2026-08-01-phase-4-5-core-knowledge-plugin-domain-refactoring.md`.

## Install

```bash
pip install -e plugins/structured-content-rendering
```

No other package needs to be installed first.

## Public interface

```python
from structured_content_rendering import render

result = render(package_dir, output_dir)
# {"render_result": ..., "validation_report": ..., "promoted": bool, "output_dir": str}
```

`package_dir` must be an accepted `canonical-package` directory (as
produced by `structured-content-assembly`'s `build_canonical_package`).

## Tests

```bash
cd plugins/structured-content-rendering
pip install -e .
python -m pytest tests/ -v
```

## Isolated-install proof

Proves this plugin installs and runs with **no other workbench
distribution present** (no sibling plugin, no repository-root Python
package):

```bash
cd tools/phase-4-5-core-plugin-refactoring
python isolated_install_check.py --plugin structured-content-rendering --import-package structured_content_rendering
```
