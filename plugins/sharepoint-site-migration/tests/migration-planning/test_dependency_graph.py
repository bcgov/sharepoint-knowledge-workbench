"""Tests for dependency_graph.py -- shapes a caller-supplied object list into
wave_planning.DeploymentObjects, computes the wave order via plan_waves
(local to this plugin -- moved from sharepoint-provisioning 2026-08-08, see
this plugin's README), and emits a dependency-matrix.json-shaped dict
conforming to assets/migration-planning/dependency-matrix-schema.json."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts" / "migration-planning"))

import pytest

from dependency_graph import (
    MatrixValidationError,
    build_dependency_matrix,
    load_matrix_objects,
)
from provisioning_outcomes import Outcome
from wave_planning import DeploymentObject


class TestLoadMatrixObjects:
    def test_loads_valid_objects(self):
        raw = [
            {"name": "SiteColumnA", "objectType": "SiteColumn", "dependsOn": []},
            {"name": "ListA", "objectType": "List", "dependsOn": ["SiteColumnA"]},
        ]
        objects = load_matrix_objects(raw)
        assert objects == (
            DeploymentObject(name="SiteColumnA", object_type="SiteColumn", depends_on=()),
            DeploymentObject(name="ListA", object_type="List", depends_on=("SiteColumnA",)),
        )

    def test_missing_required_field_raises_with_object_name_or_index(self):
        raw = [{"name": "ListA", "dependsOn": []}]  # missing objectType
        with pytest.raises(MatrixValidationError, match="ListA"):
            load_matrix_objects(raw)

    def test_missing_name_raises_with_index(self):
        raw = [{"objectType": "List", "dependsOn": []}]
        with pytest.raises(MatrixValidationError, match="index 0"):
            load_matrix_objects(raw)

    def test_duplicate_names_raise(self):
        raw = [
            {"name": "ListA", "objectType": "List", "dependsOn": []},
            {"name": "ListA", "objectType": "List", "dependsOn": []},
        ]
        with pytest.raises(MatrixValidationError, match="duplicate"):
            load_matrix_objects(raw)


class TestBuildDependencyMatrix:
    def test_emits_objects_and_waves_conforming_to_schema_shape(self):
        objects = (
            DeploymentObject(name="SiteColumnA", object_type="SiteColumn", depends_on=()),
            DeploymentObject(name="ListA", object_type="List", depends_on=("SiteColumnA",)),
        )
        matrix = build_dependency_matrix(objects)
        assert matrix["outcome"] == Outcome.OBSERVED
        assert {o["name"] for o in matrix["objects"]} == {"SiteColumnA", "ListA"}
        assert matrix["waves"] == [["SiteColumnA"], ["ListA"]]

    def test_reports_blocking_findings_without_raising(self):
        objects = (DeploymentObject(name="ListA", object_type="List", depends_on=("Missing",)),)
        matrix = build_dependency_matrix(objects)
        assert matrix["outcome"] == Outcome.FAILED
        assert matrix["waves"] == []
        assert any("Missing" in f for f in matrix["blocking_findings"])

    def test_empty_input_is_empty_outcome(self):
        matrix = build_dependency_matrix(())
        assert matrix["outcome"] == Outcome.EMPTY
        assert matrix["objects"] == []
        assert matrix["waves"] == []
