# structured-content-assembly

Canonical content package construction for the SharePoint Knowledge
Workbench: cleanup, chunking, validation, and atomic promotion from a
confirmed `analysis-plan` into a `canonical-package` (plus a
`publication-map` for grouped packages).

This plugin is the **producer** of `canonical-package` and
`publication-map`: the authoritative schemas live inside this plugin at
`scripts/canonical_schema/` and `references/contracts/`, not in a shared
top-level distribution. This plugin has **zero dependency on any other
workbench distribution or the repository root at install/runtime** — it
installs and runs standalone. It carries a plugin-local consumer copy of
the `analysis-plan` contract (`scripts/canonical_schema/analysis_plan.py`,
a genuinely independent schema subset kept in sync by hand — this one is
small, contract-shape-only, and changes rarely) so it can consume a
*confirmed* plan dict without importing document-structure-analysis's package at
runtime. Several other modules that used to be hand-duplicated
implementation code are now **managed cross-plugin file-level symlinks**
instead (see `symlinks.json` and
`docs/superpowers/plans/phase-4-5-evidence/wave-9-duplication-remediation-report.md`)
— editing the canonical source automatically updates every consumer, and
the installed wheel/skill copy is a real, independent file materialized
at build/install time, never a runtime dependency on the producer plugin.

**Flat `scripts/` layout** (matching `docx-to-content`'s existing
convention and the other three domain plugins' Wave 2/3 corrections —
bare module names, no enclosing package-name folder):

```
plugins/structured-content-assembly/
├── scripts/
│   ├── canonical_knowledge.py   # public interface: build_canonical_package()
│   ├── convert.py               # pandoc extraction + cleanup + chunk/promote pipeline
│   ├── chunking.py              # heading-slice -> ChunkSlice/SlicedDocument
│   ├── package.py               # canonical-package builder (chunk/media/manifest writer)
│   ├── canonical_package.py     # renderer-side CanonicalPackage.load()
│   ├── dispositions.py          # warning-disposition reconciliation
│   ├── media_disposition.py     # media-decision classification
│   ├── publication_map.py       # publication-map builder (grouped packages)
│   ├── validate_canonical.py    # canonical-package validator
│   ├── atomic_output.py         # [symlink -> structured-content-assembly is the canonical owner]
│   ├── hashing.py                # [symlink -> structured-content-assembly is the canonical owner]
│   ├── identity_core.py          # [symlink -> document-structure-analysis's canonical identity_core.py]
│   ├── topic_boundary_core.py    # [symlink -> document-structure-analysis's canonical topic_boundary_core.py]
│   ├── plan_verification.py      # [symlink -> document-structure-analysis's canonical plan_verification_core.py]
│   ├── pandoc_cleanup/            # [symlinks -> source-document-extraction's scripts/pandoc/*]
│   ├── emf_convert.py             # [symlink -> source-document-extraction is the canonical owner]
│   └── canonical_schema/          # this plugin's own canonical-package/publication-map
│       │                          # contracts (real files); analysis_plan.py is a genuinely
│       │                          # independent, hand-synced consumer schema copy
│       ├── canonical_package.py
│       ├── publication_map.py
│       ├── analysis_plan.py
│       └── shared.py
├── references/contracts/
├── skills/build-canonical-package/
└── tests/
```

Modules marked `[symlink -> ...]` above are **managed cross-plugin
file-level symlinks** (via `.agents/skills/symlink-manager/scripts/symlink_manager.py`,
recorded in `symlinks.json`), never hand-maintained duplicate
implementations — per the dependency-boundary rule (spec Section 11), a
real domain plugin never imports another domain plugin's implementation
package *at runtime*, but the underlying source file is shared at the
filesystem/build level: `setuptools` dereferences the symlink into a
real, independent file when building this plugin's wheel, and
`symlink_manager.py`'s installer path does the same for `.agents/skills/`
installs — so the installed/distributed artifact never depends on the
producer plugin being present. See
`docs/superpowers/plans/phase-4-5-evidence/wave-9-duplication-remediation-report.md`
for the full rationale and verification evidence (this superseded the
original hand-duplication approach recorded in
`wave-4-structured-content-assembly-split-decision.md`).

Part of Phase 4.5's decomposition of the combined `docx-to-content` plugin
into four independently installable domain plugins — see
`docs/superpowers/plans/2026-08-01-phase-4-5-core-knowledge-plugin-domain-refactoring.md`.

## Install

```bash
pip install -e plugins/structured-content-assembly
```

No other package needs to be installed first.

## Public interface

```python
from canonical_knowledge import build_canonical_package

result = build_canonical_package(analysis_plan_dict, source_dir, output_dir)
# {"manifest": ..., "validation_report": ..., "promoted": bool, "package_dir": str}
```

`analysis_plan_dict` must be a *confirmed* `analysis-plan` v1 dict (e.g.
produced by `document-structure-analysis`).

## Tests

```bash
cd plugins/structured-content-assembly
pip install -e .
python -m pytest tests/ -v
```

## Isolated-install proof

Proves this plugin installs and runs with **no other workbench
distribution present** (no sibling plugin, no repository-root Python
package):

```bash
cd tools/phase-4-5-core-plugin-refactoring
python isolated_install_check.py --plugin structured-content-assembly --import-package canonical_knowledge
```
