"""Tests for wave_planning.py -- pure topological-sort computation of a
deployment wave plan from a caller-supplied, dependency-annotated object
list. No tenant I/O; mirrors this plugin's existing honest-outcome and
genericity conventions."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from wave_planning import (
    CycleDetected,
    DeploymentObject,
    UnresolvedDependency,
    plan_waves,
)
from provisioning_outcomes import Outcome


def test_empty_input_is_empty_outcome():
    plan = plan_waves([])
    assert plan.outcome == Outcome.EMPTY
    assert plan.stages == ()


def test_linear_chain_produces_three_stages_in_order():
    # A depends on B depends on C -> C, then B, then A
    a = DeploymentObject(name="A", object_type="List", depends_on=("B",))
    b = DeploymentObject(name="B", object_type="List", depends_on=("C",))
    c = DeploymentObject(name="C", object_type="SiteColumn")

    plan = plan_waves([a, b, c])

    assert plan.outcome == Outcome.OBSERVED
    assert len(plan.stages) == 3
    assert [obj.name for obj in plan.stages[0]] == ["C"]
    assert [obj.name for obj in plan.stages[1]] == ["B"]
    assert [obj.name for obj in plan.stages[2]] == ["A"]


def test_diamond_dependency_groups_middle_stage_together():
    # A and B both depend on C; D depends on both A and B.
    c = DeploymentObject(name="C", object_type="SiteColumn")
    a = DeploymentObject(name="A", object_type="ContentType", depends_on=("C",))
    b = DeploymentObject(name="B", object_type="ContentType", depends_on=("C",))
    d = DeploymentObject(name="D", object_type="List", depends_on=("A", "B"))

    plan = plan_waves([c, a, b, d])

    assert plan.outcome == Outcome.OBSERVED
    assert len(plan.stages) == 3
    assert [obj.name for obj in plan.stages[0]] == ["C"]
    assert {obj.name for obj in plan.stages[1]} == {"A", "B"}
    assert [obj.name for obj in plan.stages[2]] == ["D"]


def test_cycle_is_detected_and_reported_not_silently_misordered():
    a = DeploymentObject(name="A", object_type="List", depends_on=("B",))
    b = DeploymentObject(name="B", object_type="List", depends_on=("A",))

    plan = plan_waves([a, b])

    assert plan.outcome == Outcome.FAILED
    assert plan.stages == ()
    assert any("cycle" in finding.lower() for finding in plan.blocking_findings)


def test_cycle_raising_helper_error_type_exists_for_callers_that_want_it():
    # CycleDetected is exported for callers that prefer exceptions -- but
    # plan_waves itself must report honestly, never raise, per Outcome
    # vocabulary conventions used throughout this plugin.
    assert issubclass(CycleDetected, Exception)


def test_dependency_naming_nonexistent_object_is_reported_not_ignored():
    a = DeploymentObject(name="A", object_type="List", depends_on=("Ghost",))

    plan = plan_waves([a])

    assert plan.outcome == Outcome.FAILED
    assert plan.stages == ()
    assert any("Ghost" in finding for finding in plan.blocking_findings)


def test_unresolved_dependency_error_type_exists_for_callers_that_want_it():
    assert issubclass(UnresolvedDependency, Exception)


def test_to_dict_is_json_serializable_and_matches_stage_shape():
    a = DeploymentObject(name="A", object_type="List")
    plan = plan_waves([a])

    result = plan.to_dict()

    assert result["outcome"] == Outcome.OBSERVED
    assert result["stages"] == [[{"name": "A", "object_type": "List", "depends_on": []}]]
    assert result["blocking_findings"] == []

