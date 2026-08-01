# knowledge-analysis

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
plugins/knowledge-analysis/
├── scripts/
│   ├── analysis.py           # public interface: recommend_from_normalized()
│   ├── identity.py           # stable chunk/topic identity
│   ├── topic_grouping.py     # topic-boundary detection
│   ├── plans.py               # draft-plan construction, confirmation, verification
│   ├── plan_hashing.py        # canonical-JSON hashing + plan_id (named to avoid
│   │                          # colliding with docx-to-content's own hashing.py)
│   └── plan_schema/           # this plugin's own analysis-plan contract
│       ├── analysis_plan.py
│       └── shared.py
├── references/contracts/
├── skills/analyze-content-structure/
└── tests/
```

Part of Phase 4.5's decomposition of the combined `docx-to-content` plugin
into four independently installable domain plugins — see
`docs/superpowers/plans/2026-08-01-phase-4-5-core-knowledge-plugin-domain-refactoring.md`.

## Install

```bash
pip install -e plugins/knowledge-analysis
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
cd plugins/knowledge-analysis
pip install -e .
python -m pytest tests/ -v
```

## Isolated-install proof

Proves this plugin installs and runs with **no other workbench
distribution present** (no sibling plugin, no repository-root Python
package):

```bash
cd tools/phase-4-5-core-plugin-refactoring
python isolated_install_check.py --plugin knowledge-analysis --import-package analysis
```
