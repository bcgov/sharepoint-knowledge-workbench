# document-structure-analysis

Semantic structure analysis for the SharePoint Knowledge Workbench:
topic-boundary reasoning, chunking-strategy recommendation, and draft-plan
construction from a `normalized-source-document`.

This plugin is the **producer** of `analysis-plan`: the authoritative
schema lives inside this plugin at `scripts/plan_schema/analysis_plan.py`
and `references/contracts/analysis-plan.md`, not in a shared top-level
distribution. This plugin has **zero dependency on any other workbench
distribution or the repository root** — it installs and runs standalone.

**Flat `scripts/` layout** (matching `docx-to-content`'s existing
convention and `source-document-extraction`'s Wave 2 correction — bare
module names, no enclosing package-name folder):

```
plugins/document-structure-analysis/
├── scripts/
│   ├── analysis.py               # public interface: recommend_from_normalized()
│   ├── identity.py               # thin re-export of identity_core.py
│   ├── identity_core.py          # CANONICAL: stable chunk/topic identity -- also consumed
│   │                              # by structured-content-assembly via a managed cross-plugin symlink
│   ├── topic_grouping.py         # thin re-export of topic_boundary_core.py
│   ├── topic_boundary_core.py    # CANONICAL: topic-boundary detection -- also consumed
│   │                              # by structured-content-assembly via a managed cross-plugin symlink
│   ├── plans.py                   # draft-plan construction, confirmation, media decisions
│   ├── plan_verification_core.py  # CANONICAL: plan-ID computation + confirmed-plan
│   │                              # verification -- also consumed by structured-content-assembly
│   │                              # via a managed cross-plugin symlink
│   ├── plan_hashing.py            # canonical-JSON hashing (thin re-export of
│   │                              # plan_verification_core's compute_plan_id; named to
│   │                              # avoid colliding with other plugins' own hashing.py)
│   └── plan_schema/               # this plugin's own analysis-plan contract
│       ├── analysis_plan.py
│       └── shared.py
├── references/contracts/
├── skills/analyze-content-structure/
└── tests/
```

Three modules here (`identity_core.py`, `topic_boundary_core.py`,
`plan_verification_core.py`) are this plugin's own **canonical
ownership** of behavior that `structured-content-assembly` also needs at
convert-time. `structured-content-assembly` consumes each via a **managed
cross-plugin file-level symlink** (see `symlinks.json`) under the exact
same bare module name — never a hand-maintained duplicate, never a
runtime cross-plugin import. See
`docs/superpowers/plans/phase-4-5-evidence/wave-9-duplication-remediation-report.md`.

Part of Phase 4.5's decomposition of the combined `docx-to-content` plugin
into four independently installable domain plugins — see
`docs/superpowers/plans/2026-08-01-phase-4-5-core-knowledge-plugin-domain-refactoring.md`.

## Install

```bash
pip install -e plugins/document-structure-analysis
```

No other package needs to be installed first.

## Public interface

```python
from analysis import recommend_from_normalized

analysis_plan = recommend_from_normalized(normalized_source_document)
```

Returns an `analysis-plan` v1 dict, validated against this plugin's own
`plan_schema.analysis_plan.validate`.

## Tests

```bash
cd plugins/document-structure-analysis
pip install -e .
python -m pytest tests/ -v
```

## Isolated-install proof

Proves this plugin installs and runs with **no other workbench
distribution present** (no sibling plugin, no repository-root Python
package):

```bash
cd tools/phase-4-5-core-plugin-refactoring
python isolated_install_check.py --plugin document-structure-analysis --import-package analysis
```
