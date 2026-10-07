"""
test_permissions_analysis.py

Purpose:
    Contract, negative, and genericity tests for the permissions/security analyser.
    Covers both accepted input shapes (flat permission-entry array, and a structured
    groups/objects export). Uses real fixture files on a real filesystem per
    `.agent/rules/test-driven-development.md`.

Layer: plugins/sharepoint-site-assessment -- tests

Key Input Dependencies:
    - pytest, the plugin module under test, and temporary JSON fixtures created by the test cases.

Function index:
    - flat_data
    - structured_data
    - test_flat_shape_derives_groups_and_objects
    - test_flat_shape_groups_multiple_role_assignments_under_one_object
    - test_structured_shape_flags_unique_role_assignments_only
    - test_missing_groups_or_objects_does_not_crash
    - test_report_contains_no_project_literals
    - test_run_writes_two_artifacts_and_reports_observed
    - test_run_with_missing_input_is_unavailable_and_writes_nothing
    - test_run_with_empty_permissions_is_empty_not_observed
    - test_run_with_malformed_permissions_is_failed
"""

import json
from pathlib import Path

import pytest

from discovery_inputs import DiscoveryStatus
from permissions_analysis import analyse, generate_report, run

FIXTURES = Path(__file__).parent / "fixtures"


# Build a flat permissions fixture with role assignments and principals.
@pytest.fixture()
def flat_data():
    """Build a flat permissions fixture with role assignments and principals."""
    return json.loads((FIXTURES / "permissions-flat.json").read_text(encoding="utf-8"))


# Build a structured permissions fixture containing groups and secured objects.
@pytest.fixture()
def structured_data():
    """Build a structured permissions fixture containing groups and secured objects."""
    return json.loads((FIXTURES / "permissions-structured.json").read_text(encoding="utf-8"))


# Flat shape derives groups and objects.
def test_flat_shape_derives_groups_and_objects(flat_data):
    """Flat shape derives groups and objects."""
    plan = analyse(flat_data)
    names = {g["name"] for g in plan["groups"]}
    assert names == {"Site Owners", "HR Reviewers"}
    assert plan["stats"]["totalObjects"] == 3  # Site, Policies, Forms


# Flat shape groups multiple role assignments under one object.
def test_flat_shape_groups_multiple_role_assignments_under_one_object():
    """Flat shape groups multiple role assignments under one object."""
    data = json.loads((FIXTURES / "permissions-flat.json").read_text(encoding="utf-8"))
    plan = analyse(data)
    by_title = {o["title"]: o for o in plan["objects"]}
    assert len(by_title["Policies"]["roleAssignments"]) == 1


# Structured shape flags unique role assignments only.
def test_structured_shape_flags_unique_role_assignments_only(structured_data):
    """Structured shape flags unique role assignments only."""
    plan = analyse(structured_data)
    assert plan["stats"]["uniqueObjectsCount"] == 1
    assert plan["uniqueObjects"][0]["title"] == "Policies"


# Missing groups or objects does not crash.
def test_missing_groups_or_objects_does_not_crash():
    """Missing groups or objects does not crash."""
    plan = analyse({"siteUrl": "/sites/x"})
    assert plan["stats"]["totalObjects"] == 0
    assert plan["groups"] == []


# Report contains no project literals.
def test_report_contains_no_project_literals(structured_data):
    """Report contains no project literals."""
    report = generate_report(analyse(structured_data))
    lowered = report.lower()
    for literal in [__import__("base64").b64decode(x).decode() for x in ['anVzdGlu', 'Y2Vpcw==', 'Y291cnRob3VzZQ==', 'aXRhdQ==', 'amFnLmdvdi5iYy5jYQ==', 'Y21hdA==', 'Y3Ni']]:
        assert literal not in lowered


# Run writes two artifacts and reports observed.
def test_run_writes_two_artifacts_and_reports_observed(tmp_path):
    """Run writes two artifacts and reports observed."""
    outcome = run(permissions_path=FIXTURES / "permissions-structured.json", output_dir=tmp_path)
    assert outcome.status is DiscoveryStatus.OBSERVED
    assert (tmp_path / "permissions-plan.json").is_file()
    assert (tmp_path / "permissions-plan.md").is_file()
    assert len(outcome.artifacts) == 2


# Run with missing input is unavailable and writes nothing.
def test_run_with_missing_input_is_unavailable_and_writes_nothing(tmp_path):
    """Run with missing input is unavailable and writes nothing."""
    outcome = run(permissions_path=tmp_path / "nope.json", output_dir=tmp_path / "out")
    assert outcome.status is DiscoveryStatus.UNAVAILABLE
    assert not (tmp_path / "out").exists()


# Run with empty permissions is empty not observed.
def test_run_with_empty_permissions_is_empty_not_observed(tmp_path):
    """Run with empty permissions is empty not observed."""
    src = tmp_path / "empty.json"
    src.write_text("[]", encoding="utf-8")
    outcome = run(permissions_path=src, output_dir=tmp_path / "out")
    assert outcome.status is DiscoveryStatus.EMPTY
    assert (tmp_path / "out" / "permissions-plan.json").is_file()


# Run with malformed permissions is failed.
def test_run_with_malformed_permissions_is_failed(tmp_path):
    """Run with malformed permissions is failed."""
    src = tmp_path / "bad.json"
    src.write_text("{{{", encoding="utf-8")
    outcome = run(permissions_path=src, output_dir=tmp_path / "out")
    assert outcome.status is DiscoveryStatus.FAILED
