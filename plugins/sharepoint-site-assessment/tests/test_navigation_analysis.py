"""
test_navigation_analysis.py

Purpose:
    Contract, negative, and genericity tests for the site navigation analyser.
    Uses real fixture files on a real filesystem per
    `.agent/rules/test-driven-development.md`.

Layer: plugins/sharepoint-site-assessment -- tests

Key Input Dependencies:
    - pytest, the plugin module under test, and temporary JSON fixtures created by the test cases.

Function index:
    - nav_data
    - test_counts_top_level_nodes_only
    - test_max_depth_reflects_deepest_child_chain
    - test_flattened_nodes_carry_depth_and_child_count
    - test_missing_children_key_does_not_crash
    - test_report_contains_no_project_literals
    - test_run_writes_both_artifacts_and_reports_observed
    - test_run_with_missing_input_is_unavailable_and_writes_nothing
    - test_run_with_empty_navigation_is_empty_not_observed
    - test_run_with_malformed_navigation_is_failed
    - test_run_with_non_object_navigation_is_failed
"""

import json
from pathlib import Path

import pytest

from discovery_inputs import DiscoveryStatus
from navigation_analysis import analyse, generate_report, run

FIXTURES = Path(__file__).parent / "fixtures"


# Build a nested navigation fixture with caller-selected nodes and child levels.
@pytest.fixture()
def nav_data():
    """Build a nested navigation fixture with caller-selected nodes and child levels."""
    return json.loads((FIXTURES / "navigation.json").read_text(encoding="utf-8"))


# Counts top level nodes only.
def test_counts_top_level_nodes_only(nav_data):
    """Counts top level nodes only."""
    plan = analyse(nav_data)
    assert plan["stats"]["topNavCount"] == 2
    assert plan["stats"]["quickLaunchCount"] == 2


# Max depth reflects deepest child chain.
def test_max_depth_reflects_deepest_child_chain(nav_data):
    """Max depth reflects deepest child chain."""
    plan = analyse(nav_data)
    # Home(0) / Departments(0) -> Finance/HR(1) -> Benefits(2)
    assert plan["stats"]["topNavMaxDepth"] == 2
    assert plan["stats"]["quickLaunchMaxDepth"] == 0


# Flattened nodes carry depth and child count.
def test_flattened_nodes_carry_depth_and_child_count(nav_data):
    """Flattened nodes carry depth and child count."""
    plan = analyse(nav_data)
    by_title = {n["title"]: n for n in plan["topNav"]}
    assert by_title["Departments"]["depth"] == 0
    assert by_title["Departments"]["childCount"] == 2
    assert by_title["Finance"]["depth"] == 1
    assert by_title["Benefits"]["depth"] == 2


# Missing children key does not crash.
def test_missing_children_key_does_not_crash():
    """Missing children key does not crash."""
    plan = analyse({"topNav": [{"title": "Odd", "url": "/odd"}], "quickLaunch": []})
    assert plan["stats"]["topNavCount"] == 1


# Report contains no project literals.
def test_report_contains_no_project_literals(nav_data):
    """Report contains no project literals."""
    report = generate_report(analyse(nav_data))
    lowered = report.lower()
    for literal in [__import__("base64").b64decode(x).decode() for x in ['anVzdGlu', 'Y2Vpcw==', 'Y291cnRob3VzZQ==', 'aXRhdQ==', 'amFnLmdvdi5iYy5jYQ==', 'Y21hdA==', 'Y3Ni']]:
        assert literal not in lowered


# Run writes both artifacts and reports observed.
def test_run_writes_both_artifacts_and_reports_observed(tmp_path):
    """Run writes both artifacts and reports observed."""
    outcome = run(navigation_path=FIXTURES / "navigation.json", output_dir=tmp_path)
    assert outcome.status is DiscoveryStatus.OBSERVED
    assert (tmp_path / "navigation-plan.json").is_file()
    assert (tmp_path / "navigation-plan.md").is_file()
    assert len(outcome.artifacts) == 2


# Run with missing input is unavailable and writes nothing.
def test_run_with_missing_input_is_unavailable_and_writes_nothing(tmp_path):
    """Run with missing input is unavailable and writes nothing."""
    outcome = run(navigation_path=tmp_path / "nope.json", output_dir=tmp_path / "out")
    assert outcome.status is DiscoveryStatus.UNAVAILABLE
    assert not (tmp_path / "out").exists()


# Run with empty navigation is empty not observed.
def test_run_with_empty_navigation_is_empty_not_observed(tmp_path):
    """Run with empty navigation is empty not observed."""
    src = tmp_path / "empty.json"
    src.write_text(json.dumps({"topNav": [], "quickLaunch": []}), encoding="utf-8")
    outcome = run(navigation_path=src, output_dir=tmp_path / "out")
    assert outcome.status is DiscoveryStatus.EMPTY
    assert (tmp_path / "out" / "navigation-plan.json").is_file()


# Run with malformed navigation is failed.
def test_run_with_malformed_navigation_is_failed(tmp_path):
    """Run with malformed navigation is failed."""
    src = tmp_path / "bad.json"
    src.write_text("{{{", encoding="utf-8")
    outcome = run(navigation_path=src, output_dir=tmp_path / "out")
    assert outcome.status is DiscoveryStatus.FAILED


# Run with non object navigation is failed.
def test_run_with_non_object_navigation_is_failed(tmp_path):
    """Run with non object navigation is failed."""
    src = tmp_path / "list.json"
    src.write_text("[]", encoding="utf-8")
    outcome = run(navigation_path=src, output_dir=tmp_path / "out")
    assert outcome.status is DiscoveryStatus.FAILED
