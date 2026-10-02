# Deployment wave planning details

## Contents

- [Why compute order instead of listing it](#why-compute-order-instead-of-listing-it)
- [Honest outcomes](#honest-outcomes)
- [Dependencies by object name only](#dependencies-by-object-name-only)
- [Usage](#usage)
- [Provenance and the 2026-08-08 move](#provenance-and-the-2026-08-08-move)

## Why compute order instead of listing it

A hand-maintained deployment step list can silently drift from the scripts it references. A master orchestrator can keep listing objects or scripts by name in a
fixed order long after some names were consolidated, renamed or removed; nothing catches the drift until it runs against a live tenant, where it fails or silently
skips work. Computing the order from a dependency graph removes that class of staleness: an object that no longer exists, or a dependency that doesn't resolve, is
reported as a planning failure before anything runs.

The skill is independent of `sharepoint-provisioning`'s provision-fields, provision-content-types and provision-list skills. It only computes ORDER; it plans or
applies no field, content-type or list change. Feed its output order into those skills in stage order. It shares `scripts/wave_planning.py` with
`sharepoint-analyze-sharepoint-dependency-graph`; provisioning consumes a finished wave order, it does not produce one.

## Honest outcomes

| Outcome | Meaning |
|---|---|
| `EMPTY` | No objects were supplied; nothing to order |
| `OBSERVED` | Every object's dependencies resolved; a full stage order was computed |
| `FAILED` | A dependency named an object absent from the input, or the graph contains a cycle; `blocking_findings` says exactly which |

`plan_waves` never raises on a bad input graph and never silently drops or guesses an order for an unresolvable object.

## Dependencies by object name only

`DeploymentObject.depends_on` names other objects by `name` only. A caller declares "depends on this specific named thing", never "depends on some earlier numbered
stage", which is the hand-maintained coupling (a stage number standing in for its contents) that goes stale silently. See `scripts/wave_planning.py`'s module
docstring for the source ambiguity this deliberately does not carry forward.

## Usage

```python
from wave_planning import DeploymentObject, plan_waves

objects = [
    DeploymentObject(name='SiteColumnA', object_type='SiteColumn'),
    DeploymentObject(name='ContentTypeB', object_type='ContentType', depends_on=('SiteColumnA',)),
    DeploymentObject(name='ListC', object_type='List', depends_on=('ContentTypeB',)),
]
plan = plan_waves(objects)
print(plan.outcome, plan.to_dict())
```

Exports: `DeploymentObject`, `WavePlan`, `plan_waves`, `CycleDetected`, `UnresolvedDependency`.

## Provenance and the 2026-08-08 move

New-build work generalizing a pattern observed in a separate repository's migration orchestrator (a hand-maintained, fixed-order step list that had drifted from the
consolidated set of scripts). Not a code port; only the principle (compute order from a dependency graph) was generalized, so no entry is needed in the Phase 9
`provenance.md`.

`wave_planning.py` and its skills were originally authored in `sharepoint-provisioning`. On 2026-08-08 (external architecture review and user decision) they moved here:
nothing in provisioning's field, content-type, list or calendar logic ever called `plan_waves`, only this skill did, and the plugin building on it
(dependency-graph shaping, completeness checks, wave order) belongs together. `sharepoint-provisioning` now consumes a computed wave plan as an input to its own gated apply.
