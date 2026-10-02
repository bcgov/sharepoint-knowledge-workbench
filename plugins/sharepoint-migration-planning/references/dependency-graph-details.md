# Dependency graph analysis details

## Contents

- [Public interface](#public-interface)
- [Completeness checks block matrix emission](#completeness-checks-block-matrix-emission)
- [Honest outcomes](#honest-outcomes)
- [Scripts](#scripts)
- [Provenance](#provenance)

## Public interface

```python
from dependency_graph import load_matrix_objects, build_dependency_matrix
from completeness_checks import run_all_checks

objects = load_matrix_objects(raw_matrix_entries)  # validates required fields; raises MatrixValidationError naming the offending name/index

# Run completeness checks BEFORE trusting the matrix enough to compute a wave order.
summary = run_all_checks(objects, source_names=observed_source_object_names)
if not summary.all_passed:
    # report summary.failed_check_names and stop; do not compute waves against a matrix known not to match its source
    ...

matrix = build_dependency_matrix(objects)
# {"outcome", "objects", "waves", "blocking_findings"}; conforms to assets/dependency-matrix-schema.json
```

## Completeness checks block matrix emission

A completeness failure (source coverage, orphan entries, unresolved lookup targets, destination-name collisions) means the matrix does not accurately
describe the source it claims to, and downstream wave computation would build on a wrong premise. Callers must run `run_all_checks` and stop on
`all_passed is False` rather than going straight to `build_dependency_matrix`. This is a distinct concern from `wave_planning.plan_waves`'s own
unresolved-dependency and cycle detection, which only sees the graph it is given, never the source it was supposed to be derived from (see
`completeness_checks.py`'s module docstring).

## Honest outcomes

A cycle, or a dependency naming a nonexistent object, is reported via `blocking_findings` and `outcome=Outcome.FAILED` (matching `wave_planning.py`), never
silently dropped or guessed around. `build_dependency_matrix` never raises for a bad dependency graph; `load_matrix_objects` raises `MatrixValidationError`
for a structurally malformed raw entry, since that is a caller input error, not a planning outcome.

## Scripts

- `scripts/dependency_graph.py`: `load_matrix_objects`, `build_dependency_matrix`, `MatrixValidationError`.
- `scripts/completeness_checks.py`: `run_all_checks` and the four individual checks it composes.
- `scripts/wave_planning.py`: authored in this plugin (moved from `sharepoint-provisioning` on 2026-08-08).
- `scripts/provisioning_outcomes.py`: the shared `Outcome` vocabulary, a real file in this plugin.

## Provenance

`dependency_graph.py` and the matrix shape are new design work, generalizing the concept of a hand-curated dependency matrix observed in a separate SharePoint
migration repository (hand-curated there; no script built it). `completeness_checks.py` generalizes the shape-agnostic subset of an 18-check completeness QA
gate found in the Phase 9 exhaustive source audit (`temp/phase9-source-audit/file-tracking.json`); the project-specific business-rule checks were deliberately not
ported. Source repository only.
