# Wave 6 — Final Test Migration Ledger

**Date:** 2026-08-01

## Reconciliation

The plan text's "reconcile the 45-test total" (Wave 6 Step 1) refers to Revision 2's
much-smaller-scope planning estimate and does not match this repo's actual baseline — Wave 0's
`wave-0-test-ledger.json` recorded **529 collected / 530 tests** (1 skipped) in the original
combined `docx-to-content` plugin, not 45. This ledger reconciles the real baseline against the
real post-Wave-5 distribution instead of the stale planning figure.

## Per-plugin test counts, end of Wave 5

| Plugin | Tests collected | Source |
|---|---|---|
| `source-document-extraction` | 78 | Wave 2 extraction |
| `knowledge-analysis` | 70 | Wave 3 extraction |
| `canonical-knowledge` | 173 | Wave 4 extraction (includes `test_canonical_package_contract.py`, new `plan_verification`/`chunk_identity`/`chunk_grouping` coverage carried over from moved files) |
| `knowledge-publication` | 49 | Wave 5 extraction |
| `docx-to-content` (transitional, retired Wave 7/8) | 171 (170 passed + 1 skipped) | Remaining orchestration (`cli.py`, `analyze_structure.py`) + compatibility-shim integration tests that depend on more than one plugin (`test_atomic_promotion.py`, `test_convert.py`, `test_package_load.py`, `test_renderer_protocol_integration.py`, `test_cli_plan_integration.py`) |
| `tools/phase-4-5-core-plugin-refactoring` | 42 (40 fast + 2 slow) | Wave 0/1 harness + Wave 6's new `test_combined_install_check.py` |
| repository-root `tests/integration/` (new, Wave 6) | 1 | `test_full_ceis_pipeline_across_plugins.py` |

**Total across all suites: 78 + 70 + 173 + 49 + 171 + 42 + 1 = 584** (up from Wave 0's 530 —
growth is expected and correct: every wave's extraction added new local-duplication coverage
(`chunk_identity`/`chunk_grouping`/`pandoc_cleanup`/`plan_verification` in `canonical-knowledge`;
the render-pipeline duplicate chain in `knowledge-publication`) plus Wave 6's own new
combined-install and cross-plugin integration tests — none of this is loss, it is real new
coverage of the boundaries this refactor introduced).

## Test migration record, by wave

- **Wave 2** (`source-document-extraction`): see that wave's own test-migration record in
  `wave-2-flat-scripts-correction.md`.
- **Wave 3** (`knowledge-analysis`): see `wave-3-analysis-plan-split-decision.md`'s "Test
  migration" section.
- **Wave 4** (`canonical-knowledge`): see `wave-4-canonical-knowledge-split-decision.md`'s "Test
  migration" section.
- **Wave 5** (`knowledge-publication`): see `wave-5-knowledge-publication-split-decision.md`'s
  "Test migration" section.
- **Wave 6** (this wave): added `tools/phase-4-5-core-plugin-refactoring/tests/test_combined_install_check.py`
  (2 tests) and `tests/integration/test_full_ceis_pipeline_across_plugins.py` (1 test, executed
  with zero skips at wave closure — see `wave-6-golden-master-manifest.json`).

Every test in every plugin's suite traces to one of: (a) a Wave 0 baseline test moved wholesale via
`git mv` with imports fixed, (b) a new contract/structural test written during that wave's own
extraction to prove the new plugin boundary (e.g. `test_contract_schema_and_implementation_are_distinct_modules`-style
checks, dependency-boundary conformance), or (c) a genuinely new cross-plugin integration test
written in Wave 6 to prove the reconciled whole. No test was silently dropped without a documented
reason (the two exceptions — `test_analyze_structure.py`'s duplicate constant test in Wave 3, and
`test_multipage_markdown.py`'s redundant end-to-end test in Wave 5 — are recorded in their
respective wave's own decision doc as deliberate, justified removals of true duplicates, not
silent loss).
