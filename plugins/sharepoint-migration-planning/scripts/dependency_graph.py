"""
dependency_graph.py
=====================

Purpose:
    Shape a caller-supplied, matrix-shaped object list (conforming to
    ``assets/dependency-matrix-schema.json``) into ``wave_planning.
    DeploymentObject`` instances, and emit a complete dependency-matrix.json
    document -- the declared objects plus their computed wave order.

    Deliberately thin: all deployment-order computation is delegated to
    ``wave_planning.plan_waves`` (authored in this plugin -- moved from
    sharepoint-provisioning 2026-08-08, which never called it internally;
    see this plugin's README's "why 3a and 3b are split" section -- not
    reimplemented here, just relocated to its actual owner). This module's
    only job is the matrix <-> DeploymentObject shape translation and
    honest, per-object validation errors, so a malformed raw matrix entry is
    reported with enough context (object name or array index) to fix it
    directly, rather than a bare KeyError.

Layer: sharepoint-migration-planning / dependency-graph analysis (stage 3a)

Key Input Dependencies:
    - wave_planning.DeploymentObject / plan_waves (local to this plugin)
    - provisioning_outcomes.Outcome (symlinked from sharepoint-provisioning)
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from provisioning_outcomes import Outcome
from wave_planning import DeploymentObject, plan_waves


class MatrixValidationError(ValueError):
    """Raised when a raw matrix object entry is missing a required field or
    duplicates another entry's name. Always names the offending entry (by
    its own ``name`` if present, otherwise its array index) so the caller
    can fix the exact entry, not just learn that "something" is wrong."""


def load_matrix_objects(raw_objects: Sequence[Mapping[str, Any]]) -> tuple[DeploymentObject, ...]:
    """Validate and translate raw matrix object dicts (the
    ``assets/dependency-matrix-schema.json`` ``objects`` array shape) into
    ``DeploymentObject`` instances. Pure -- no I/O, no network."""
    seen_names: set[str] = set()
    objects: list[DeploymentObject] = []

    for index, raw in enumerate(raw_objects):
        name = raw.get("name")
        if not name:
            raise MatrixValidationError(f"matrix object at index {index} is missing required field 'name'")
        if name in seen_names:
            raise MatrixValidationError(f"duplicate object name '{name}' in matrix -- names must be unique")
        seen_names.add(name)

        object_type = raw.get("objectType")
        if not object_type:
            raise MatrixValidationError(f"'{name}' is missing required field 'objectType'")

        depends_on = raw.get("dependsOn")
        if depends_on is None:
            raise MatrixValidationError(f"'{name}' is missing required field 'dependsOn' (use [] for none)")

        objects.append(
            DeploymentObject(name=name, object_type=object_type, depends_on=tuple(depends_on))
        )

    return tuple(objects)


def build_dependency_matrix(objects: Sequence[DeploymentObject]) -> dict[str, Any]:
    """Compute the wave order for ``objects`` and emit a complete
    dependency-matrix.json document: the declared objects plus the computed
    ``waves`` array, conforming to ``assets/dependency-matrix-schema.json``.
    Never raises for a bad dependency graph -- an unresolved dependency or a
    cycle is reported honestly via ``blocking_findings`` with an ``outcome``
    of ``Outcome.FAILED`` and an empty ``waves`` array, exactly as
    ``wave_planning.plan_waves`` reports it."""
    plan = plan_waves(objects)

    if plan.outcome == Outcome.EMPTY:
        waves: list[list[str]] = []
    elif plan.blocking_findings:
        waves = []
    else:
        waves = [[obj.name for obj in stage] for stage in plan.stages]

    return {
        "outcome": plan.outcome,
        "objects": [_to_schema_dict(obj) for obj in objects],
        "waves": waves,
        "blocking_findings": list(plan.blocking_findings),
    }


def _to_schema_dict(obj: DeploymentObject) -> dict[str, Any]:
    """Render a DeploymentObject back into assets/dependency-matrix-schema.json's
    camelCase object shape (name/objectType/dependsOn) -- DeploymentObject.to_dict()
    uses this module's snake_case field names, not the matrix schema's."""
    return {"name": obj.name, "objectType": obj.object_type, "dependsOn": list(obj.depends_on)}
