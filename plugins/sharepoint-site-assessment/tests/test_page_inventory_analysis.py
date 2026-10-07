"""
test_page_inventory_analysis.py

Purpose:
    Contract, negative, and genericity tests for the classic-page inventory analyser.
    Uses real fixture files on a real filesystem (no mocking of path resolution or
    file parsing, per `.agent/rules/test-driven-development.md`).

Layer: plugins/sharepoint-site-assessment -- tests

Key Input Dependencies:
    - pytest, the plugin module under test, and temporary JSON fixtures created by the test cases.

Function index:
    - rules
    - inventory
    - test_default_rules_asset_is_packaged_and_loadable
    - test_complexity_escalates_with_script_editor_and_connections
    - test_dependency_matrix_is_sorted_by_complexity_descending
    - test_unknown_web_part_category_falls_back_to_other_not_a_crash
    - test_stats_account_for_every_page
    - test_report_contains_no_project_literals
    - test_run_writes_both_artifacts_and_reports_observed
    - test_run_with_missing_inventory_is_unavailable_and_writes_nothing
    - test_run_with_missing_rules_is_unavailable
    - test_run_with_empty_inventory_is_empty_not_observed
    - test_run_with_malformed_inventory_is_failed
"""

import json
from pathlib import Path

import pytest

from discovery_inputs import DiscoveryStatus
from page_inventory_analysis import (
    DEFAULT_RULES_PATH,
    analyse,
    generate_report,
    load_rules,
    run,
)

FIXTURES = Path(__file__).parent / "fixtures"


# Load the neutral form-analysis rules fixture used by these tests.
@pytest.fixture()
def rules():
    """Load the neutral form-analysis rules fixture used by these tests."""
    return load_rules(DEFAULT_RULES_PATH)


# Inventory.
@pytest.fixture()
def inventory():
    """Inventory."""
    return json.loads((FIXTURES / "page-inventory.json").read_text(encoding="utf-8"))


# Default rules asset is packaged and loadable.
def test_default_rules_asset_is_packaged_and_loadable(rules):
    """Default rules asset is packaged and loadable."""
    assert DEFAULT_RULES_PATH.is_file()
    assert {r["category"] for r in rules["webPartRules"]} >= {"CEWP", "SEWP", "Other"}


# Complexity escalates with script editor and connections.
def test_complexity_escalates_with_script_editor_and_connections(inventory, rules):
    """Complexity escalates with script editor and connections."""
    plan = analyse(inventory, rules)
    by_name = {p["fileName"]: p for p in plan["pages"]}
    assert by_name["simple.aspx"]["complexityLabel"] == "Low"
    assert by_name["scripted.aspx"]["complexityScore"] > by_name["simple.aspx"]["complexityScore"]
    assert by_name["scripted.aspx"]["hasCustomException"] is True


# Dependency matrix is sorted by complexity descending.
def test_dependency_matrix_is_sorted_by_complexity_descending(inventory, rules):
    """Dependency matrix is sorted by complexity descending."""
    plan = analyse(inventory, rules)
    scores = [p["complexityScore"] for p in plan["dependencyMatrix"]]
    assert scores == sorted(scores, reverse=True)


# Unknown web part category falls back to other not a crash.
def test_unknown_web_part_category_falls_back_to_other_not_a_crash(rules):
    """Unknown web part category falls back to other not a crash."""
    plan = analyse(
        [{"FileName": "odd.aspx", "Category": "SitePage", "WebParts": [{"Category": "NoSuchThing"}]}],
        rules,
    )
    assert plan["pages"][0]["webParts"][0]["approach"] == "custom-exception"


# Stats account for every page.
def test_stats_account_for_every_page(inventory, rules):
    """Stats account for every page."""
    plan = analyse(inventory, rules)
    by_complexity = plan["stats"]["byComplexity"]
    assert sum(by_complexity.values()) == plan["stats"]["totalPages"] == len(inventory)


# Report contains no project literals.
def test_report_contains_no_project_literals(inventory, rules):
    """Report contains no project literals."""
    report = generate_report(analyse(inventory, rules))
    lowered = report.lower()
    for literal in [__import__("base64").b64decode(x).decode() for x in ['anVzdGlu', 'Y2Vpcw==', 'Y291cnRob3VzZQ==', 'aXRhdQ==', 'amFnLmdvdi5iYy5jYQ==', 'Y21hdA==']]:
        assert literal not in lowered


# Run writes both artifacts and reports observed.
def test_run_writes_both_artifacts_and_reports_observed(tmp_path, rules):
    """Run writes both artifacts and reports observed."""
    outcome = run(
        inventory_path=FIXTURES / "page-inventory.json",
        rules_path=DEFAULT_RULES_PATH,
        output_dir=tmp_path,
    )
    assert outcome.status is DiscoveryStatus.OBSERVED
    assert (tmp_path / "page-inventory-plan.json").is_file()
    assert (tmp_path / "page-inventory-plan.md").is_file()
    assert len(outcome.artifacts) == 2


# Run with missing inventory is unavailable and writes nothing.
def test_run_with_missing_inventory_is_unavailable_and_writes_nothing(tmp_path):
    """Run with missing inventory is unavailable and writes nothing."""
    outcome = run(
        inventory_path=tmp_path / "nope.json",
        rules_path=DEFAULT_RULES_PATH,
        output_dir=tmp_path / "out",
    )
    assert outcome.status is DiscoveryStatus.UNAVAILABLE
    # Stronger than "no artifacts": the output directory is never even created.
    assert not (tmp_path / "out").exists()


# Run with missing rules is unavailable.
def test_run_with_missing_rules_is_unavailable(tmp_path):
    """Run with missing rules is unavailable."""
    outcome = run(
        inventory_path=FIXTURES / "page-inventory.json",
        rules_path=tmp_path / "no-rules.json",
        output_dir=tmp_path / "out",
    )
    assert outcome.status is DiscoveryStatus.UNAVAILABLE


# Run with empty inventory is empty not observed.
def test_run_with_empty_inventory_is_empty_not_observed(tmp_path):
    """Run with empty inventory is empty not observed."""
    src = tmp_path / "empty.json"
    src.write_text("[]", encoding="utf-8")
    outcome = run(inventory_path=src, rules_path=DEFAULT_RULES_PATH, output_dir=tmp_path / "out")
    assert outcome.status is DiscoveryStatus.EMPTY
    assert (tmp_path / "out" / "page-inventory-plan.json").is_file()


# Run with malformed inventory is failed.
def test_run_with_malformed_inventory_is_failed(tmp_path):
    """Run with malformed inventory is failed."""
    src = tmp_path / "bad.json"
    src.write_text("{{{", encoding="utf-8")
    outcome = run(inventory_path=src, rules_path=DEFAULT_RULES_PATH, output_dir=tmp_path / "out")
    assert outcome.status is DiscoveryStatus.FAILED
