"""
wave_planning.py
=================

Purpose:
    Given a caller-supplied, dependency-annotated list of deployment objects,
    compute a deployment wave plan via topological sort (Kahn's algorithm):
    group objects into ordered stages such that every object's dependencies
    are satisfied by a strictly earlier stage. Pure computation -- no I/O, no
    tenant contact.

    Generalized from a real hand-maintained-orchestrator failure mode: a
    master deployment script in a separate repo kept a hardcoded, fixed-order
    step list that referenced wave scripts which had since been consolidated
    and renamed. Nothing caught the drift until the orchestrator was actually
    run. Computing deployment order from a dependency graph instead of a
    hand-maintained list removes that class of silent staleness -- an object
    that no longer exists, or a dependency that no longer resolves, is
    reported as a plan failure rather than discovered at run time.

    Deliberate generalization decision: the source material's dependency
    field mixed two different kinds of reference in the same list -- some
    entries named another object, others named a bare wave-number string
    (e.g. a dependency of ``"3"`` meaning "whatever wave 3 contains").  This
    plugin's ``DeploymentObject.depends_on`` intentionally supports ONLY
    dependencies by object name. A caller should declare "depends on this
    specific named thing," not "depends on some earlier numbered stage" --
    the latter is exactly the kind of hand-maintained coupling (a stage
    number standing in for its contents) that goes stale silently, which is
    the same failure mode this module exists to eliminate.

Layer: sharepoint-site-build-and-publish / deployment-order planning

Key Input Dependencies:
    - provisioning_outcomes.Outcome (shared honest-outcome vocabulary)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Sequence

from provisioning_outcomes import Outcome


class WavePlanningError(RuntimeError):
    """Base class for wave-planning-specific errors."""


class CycleDetected(WavePlanningError):
    """Raised by callers that prefer an exception when the input graph
    contains a dependency cycle. ``plan_waves`` itself never raises this --
    it reports the cycle honestly via ``WavePlan.outcome``/``blocking_findings``,
    consistent with this plugin's Outcome vocabulary conventions."""


class UnresolvedDependency(WavePlanningError):
    """Raised by callers that prefer an exception when a dependency names an
    object absent from the input. ``plan_waves`` itself never raises this --
    see ``CycleDetected`` for why."""


@dataclass(frozen=True)
class DeploymentObject:
    """A single caller-declared deployment object. ``object_type`` is free
    text defined entirely by the caller (e.g. "SiteColumn", "ContentType",
    "List") -- this module has no domain knowledge of what kinds of objects
    exist. ``depends_on`` names other ``DeploymentObject`` instances by
    ``name`` only -- see the module docstring for why a bare wave-number
    reference is deliberately not supported."""

    name: str
    object_type: str
    depends_on: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "object_type": self.object_type,
            "depends_on": list(self.depends_on),
        }


@dataclass(frozen=True)
class WavePlan:
    """A complete, reviewable deployment order. ``stages`` is an ordered
    sequence of stages, each a tuple of ``DeploymentObject``s whose
    dependencies are all satisfied by strictly earlier stages. Producing a
    plan performs no I/O."""

    stages: tuple[tuple[DeploymentObject, ...], ...] = ()
    blocking_findings: tuple[str, ...] = ()
    outcome: str = Outcome.EMPTY

    def to_dict(self) -> dict[str, Any]:
        return {
            "outcome": self.outcome,
            "stages": [[obj.to_dict() for obj in stage] for stage in self.stages],
            "blocking_findings": list(self.blocking_findings),
        }


def plan_waves(objects: Sequence[DeploymentObject]) -> WavePlan:
    """Compute a deployment wave plan from a caller-supplied list of
    ``DeploymentObject``s via Kahn's algorithm. Never raises for a bad input
    graph -- an unresolved dependency or a cycle is reported honestly as a
    ``Outcome.FAILED`` plan with ``blocking_findings`` describing exactly
    what is wrong, never silently dropped, guessed, or mis-ordered."""
    if not objects:
        return WavePlan(stages=(), blocking_findings=(), outcome=Outcome.EMPTY)

    blocking_findings: list[str] = []
    seen_names: set[str] = set()
    by_name: dict[str, DeploymentObject] = {}
    for obj in objects:
        if obj.name in seen_names:
            blocking_findings.append(
                f"DUPLICATE OBJECT: '{obj.name}' is declared more than once in the supplied object list"
            )
        else:
            seen_names.add(obj.name)
            by_name[obj.name] = obj

    for obj in objects:
        for dep in obj.depends_on:
            if dep not in by_name:
                blocking_findings.append(
                    f"UNRESOLVED DEPENDENCY: '{obj.name}' depends on '{dep}', which is "
                    "not present in the supplied object list"
                )

    if blocking_findings:
        return WavePlan(stages=(), blocking_findings=tuple(blocking_findings), outcome=Outcome.FAILED)

    # Kahn's algorithm.
    remaining = dict(by_name)
    stages: list[tuple[DeploymentObject, ...]] = []
    placed: set[str] = set()

    while remaining:
        ready = sorted(
            name
            for name, obj in remaining.items()
            if all(dep in placed for dep in obj.depends_on)
        )
        if not ready:
            cycle_members = sorted(remaining.keys())
            blocking_findings.append(
                "CYCLE DETECTED: the following objects have unresolvable circular "
                f"dependencies and cannot be ordered: {', '.join(cycle_members)}"
            )
            return WavePlan(stages=(), blocking_findings=tuple(blocking_findings), outcome=Outcome.FAILED)

        stage = tuple(remaining[name] for name in ready)
        stages.append(stage)
        for name in ready:
            placed.add(name)
            del remaining[name]

    return WavePlan(stages=tuple(stages), blocking_findings=(), outcome=Outcome.OBSERVED)
