"""
test_navigation_analysis.py

Purpose:
    Contract, negative, and genericity tests for the site navigation analyser.
    Uses real fixture files on a real filesystem per
    `.agent/rules/test-driven-development.md`.

Layer: plugins/sharepoint-discovery -- tests
"""

import json
from pathlib import Path

import pytest

from discovery_inputs import DiscoveryStatus
from navigation_analysis import analyse, generate_report, run

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture()
def nav_data():
    return json.loads((FIXTURES / "navigation.json").read_text(encoding="utf-8"))


def test_counts_top_level_nodes_only(nav_data):
    plan = analyse(nav_data)
    assert plan["stats"]["topNavCount"] == 2
    assert plan["stats"]["quickLaunchCount"] == 2


def test_max_depth_reflects_deepest_child_chain(nav_data):
    plan = analyse(nav_data)
    # Home(0) / Departments(0) -> Finance/HR(1) -> Benefits(2)
    assert plan["stats"]["topNavMaxDepth"] == 2
    assert plan["stats"]["quickLaunchMaxDepth"] == 0


def test_flattened_nodes_carry_depth_and_child_count(nav_data):
    plan = analyse(nav_data)
    by_title = {n["title"]: n for n in plan["topNav"]}
    assert by_title["Departments"]["depth"] == 0
    assert by_title["Departments"]["childCount"] == 2
    assert by_title["Finance"]["depth"] == 1
    assert by_title["Benefits"]["depth"] == 2


def test_missing_children_key_does_not_crash():
    plan = analyse({"topNav": [{"title": "Odd", "url": "/odd"}], "quickLaunch": []})
    assert plan["stats"]["topNavCount"] == 1


def test_report_contains_no_project_literals(nav_data):
    report = generate_report(analyse(nav_data))
    lowered = report.lower()
    for literal in ("justin", "ceis", "courthouse", "itau", "jag.gov.bc.ca", "cmat", "csb"):
        assert literal not in lowered


def test_run_writes_both_artifacts_and_reports_observed(tmp_path):
    outcome = run(navigation_path=FIXTURES / "navigation.json", output_dir=tmp_path)
    assert outcome.status is DiscoveryStatus.OBSERVED
    assert (tmp_path / "navigation-plan.json").is_file()
    assert (tmp_path / "navigation-plan.md").is_file()
    assert len(outcome.artifacts) == 2


def test_run_with_missing_input_is_unavailable_and_writes_nothing(tmp_path):
    outcome = run(navigation_path=tmp_path / "nope.json", output_dir=tmp_path / "out")
    assert outcome.status is DiscoveryStatus.UNAVAILABLE
    assert not (tmp_path / "out").exists()


def test_run_with_empty_navigation_is_empty_not_observed(tmp_path):
    src = tmp_path / "empty.json"
    src.write_text(json.dumps({"topNav": [], "quickLaunch": []}), encoding="utf-8")
    outcome = run(navigation_path=src, output_dir=tmp_path / "out")
    assert outcome.status is DiscoveryStatus.EMPTY
    assert (tmp_path / "out" / "navigation-plan.json").is_file()


def test_run_with_malformed_navigation_is_failed(tmp_path):
    src = tmp_path / "bad.json"
    src.write_text("{{{", encoding="utf-8")
    outcome = run(navigation_path=src, output_dir=tmp_path / "out")
    assert outcome.status is DiscoveryStatus.FAILED


def test_run_with_non_object_navigation_is_failed(tmp_path):
    src = tmp_path / "list.json"
    src.write_text("[]", encoding="utf-8")
    outcome = run(navigation_path=src, output_dir=tmp_path / "out")
    assert outcome.status is DiscoveryStatus.FAILED
