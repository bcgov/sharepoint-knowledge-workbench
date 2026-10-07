"""Tests for completeness_checks.py -- generalized from a source-repository
matrix-completeness QA gate (~20 checks against a raw source export before
any deployment). This module keeps the checks that are shape-agnostic
(source coverage, orphan matrix entries, unresolved lookup targets,
destination-name collisions) and does not attempt to port the source's
project-specific business-rule checks (calendar structural consistency,
legacy content-type substitution, etc.).

Purpose: Tests for completeness_checks.py -- generalized from a source-repository matrix-completeness QA gate (~20 checks against a raw source export before any deployment).
Key Input Dependencies: completeness_checks, provisioning_outcomes, wave_planning.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts" / "migration-planning"))

from completeness_checks import (
    check_destination_name_collisions,
    check_lookup_targets_exist,
    check_orphan_matrix_entries,
    check_source_coverage,
    run_all_checks,
)
from provisioning_outcomes import Outcome
from wave_planning import DeploymentObject


class TestCheckSourceCoverage:
    def test_empty_is_empty_outcome(self):
        """Verify empty is empty outcome."""
        result = check_source_coverage(matrix_names=set(), source_names=set())
        assert result.outcome == Outcome.EMPTY

    def test_full_coverage_is_observed(self):
        """Verify full coverage is observed."""
        result = check_source_coverage(matrix_names={"A", "B"}, source_names={"A", "B"})
        assert result.outcome == Outcome.OBSERVED
        assert result.missing == ()

    def test_missing_source_object_is_failed_and_named(self):
        """Verify missing source object is failed and named."""
        result = check_source_coverage(matrix_names={"A"}, source_names={"A", "B"})
        assert result.outcome == Outcome.FAILED
        assert result.missing == ("B",)


class TestCheckOrphanMatrixEntries:
    def test_no_orphans_is_observed(self):
        """Verify no orphans is observed."""
        result = check_orphan_matrix_entries(matrix_names={"A"}, source_names={"A", "B"})
        assert result.outcome == Outcome.OBSERVED
        assert result.orphans == ()

    def test_stale_matrix_entry_is_reported_not_dropped(self):
        """A matrix entry with no corresponding source object usually means
        the source was renamed or removed and the matrix went stale --
        report it, never silently ignore it."""
        result = check_orphan_matrix_entries(matrix_names={"A", "Stale"}, source_names={"A"})
        assert result.outcome == Outcome.FAILED
        assert result.orphans == ("Stale",)


class TestCheckLookupTargetsExist:
    def test_all_targets_resolve_is_observed(self):
        """Verify all targets resolve is observed."""
        objects = (
            DeploymentObject(name="Parent", object_type="List", depends_on=()),
            DeploymentObject(name="Child", object_type="List", depends_on=("Parent",)),
        )
        result = check_lookup_targets_exist(objects)
        assert result.outcome == Outcome.OBSERVED
        assert result.unresolved == ()

    def test_unresolved_target_is_failed_and_named(self):
        """Verify unresolved target is failed and named."""
        objects = (DeploymentObject(name="Child", object_type="List", depends_on=("Ghost",)),)
        result = check_lookup_targets_exist(objects)
        assert result.outcome == Outcome.FAILED
        assert result.unresolved == (("Child", "Ghost"),)


class TestCheckDestinationNameCollisions:
    def test_no_collisions_is_observed(self):
        """Verify no collisions is observed."""
        objects = (
            DeploymentObject(name="A", object_type="List", depends_on=()),
            DeploymentObject(name="B", object_type="List", depends_on=()),
        )
        result = check_destination_name_collisions(objects)
        assert result.outcome == Outcome.OBSERVED
        assert result.collisions == ()

    def test_duplicate_names_are_failed_and_named(self):
        """Verify duplicate names are failed and named."""
        objects = (
            DeploymentObject(name="A", object_type="List", depends_on=()),
            DeploymentObject(name="A", object_type="ContentType", depends_on=()),
        )
        result = check_destination_name_collisions(objects)
        assert result.outcome == Outcome.FAILED
        assert result.collisions == ("A",)


class TestRunAllChecks:
    def test_all_pass_gives_observed_summary(self):
        """Verify all pass gives observed summary."""
        objects = (
            DeploymentObject(name="Parent", object_type="List", depends_on=()),
            DeploymentObject(name="Child", object_type="List", depends_on=("Parent",)),
        )
        summary = run_all_checks(objects, source_names={"Parent", "Child"})
        assert summary.outcome == Outcome.OBSERVED
        assert summary.all_passed is True

    def test_any_failure_gives_failed_summary_naming_which_check(self):
        """Verify any failure gives failed summary naming which check."""
        objects = (DeploymentObject(name="Child", object_type="List", depends_on=("Ghost",)),)
        summary = run_all_checks(objects, source_names={"Child"})
        assert summary.outcome == Outcome.FAILED
        assert summary.all_passed is False
        assert "lookup_targets_exist" in summary.failed_check_names
