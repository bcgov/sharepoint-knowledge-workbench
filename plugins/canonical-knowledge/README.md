# canonical-knowledge

Canonical content package construction for the SharePoint Knowledge
Workbench: cleanup, chunking, validation, and atomic promotion from a
confirmed `analysis-plan` into a `canonical-package` (plus a
`publication-map` for grouped packages).

This plugin is the **producer** of `canonical-package` and
`publication-map`: the authoritative schemas live inside this plugin at
`scripts/canonical_schema/` and `references/contracts/`, not in a shared
top-level distribution. This plugin has **zero dependency on any other
workbench distribution or the repository root** — it installs and runs
standalone. It carries a plugin-local consumer copy of the
`analysis-plan` contract (`scripts/canonical_schema/analysis_plan.py`,
kept in sync by hand with knowledge-analysis's producer copy) so it can
consume a *confirmed* plan dict without importing knowledge-analysis's
package at runtime.

**Flat `scripts/` layout** (matching `docx-to-content`'s existing
convention and the other three domain plugins' Wave 2/3 corrections —
bare module names, no enclosing package-name folder):

```
plugins/canonical-knowledge/
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
│   ├── atomic_output.py         # staging/promotion primitive + generator-info
│   ├── hashing.py                # canonical-JSON hashing + content_hash
│   ├── chunk_identity.py         # stable chunk/topic identity (local duplicate of
│   │                              # knowledge-analysis's identity.py -- see decision doc)
│   ├── chunk_grouping.py         # topic-boundary detection at convert time (local
│   │                              # duplicate of knowledge-analysis's topic_grouping.py)
│   ├── plan_verification.py      # plan/source verification checks (local duplicate of
│   │                              # knowledge-analysis's plans.py verify/require functions)
│   ├── pandoc_cleanup/            # pandoc markdown cleanup steps (local duplicate of
│   │                              # source-document-extraction's scripts/pandoc/)
│   ├── emf_convert.py             # legacy .emf -> .png conversion (local duplicate of
│   │                              # source-document-extraction's emf_convert.py)
│   └── canonical_schema/          # this plugin's own canonical-package/publication-map
│       │                          # contracts, plus a consumer copy of analysis-plan
│       ├── canonical_package.py
│       ├── publication_map.py
│       ├── analysis_plan.py
│       └── shared.py
├── references/contracts/
├── skills/build-canonical-package/
└── tests/
```

Several modules above are **deliberate local duplicates** of code that
also exists in `source-document-extraction` or `knowledge-analysis`,
rather than cross-plugin imports — per the dependency-boundary rule (spec
Section 11), a real domain plugin never imports another domain plugin's
implementation package. See
`docs/superpowers/plans/phase-4-5-evidence/wave-4-canonical-knowledge-split-decision.md`
for the rationale behind each duplication.

Part of Phase 4.5's decomposition of the combined `docx-to-content` plugin
into four independently installable domain plugins — see
`docs/superpowers/plans/2026-08-01-phase-4-5-core-knowledge-plugin-domain-refactoring.md`.

## Install

```bash
pip install -e plugins/canonical-knowledge
```

No other package needs to be installed first.

## Public interface

```python
from canonical_knowledge import build_canonical_package

result = build_canonical_package(analysis_plan_dict, source_dir, output_dir)
# {"manifest": ..., "validation_report": ..., "promoted": bool, "package_dir": str}
```

`analysis_plan_dict` must be a *confirmed* `analysis-plan` v1 dict (e.g.
produced by `knowledge-analysis`).

## Tests

```bash
cd plugins/canonical-knowledge
pip install -e .
python -m pytest tests/ -v
```

## Isolated-install proof

Proves this plugin installs and runs with **no other workbench
distribution present** (no sibling plugin, no repository-root Python
package):

```bash
cd tools/phase-4-5-core-plugin-refactoring
python isolated_install_check.py --plugin canonical-knowledge --import-package canonical_knowledge
```
