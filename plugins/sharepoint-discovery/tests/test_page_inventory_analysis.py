"""
test_page_inventory_analysis.py

Purpose:
    Contract, negative, and genericity tests for the classic-page inventory analyser.
    Uses real fixture files on a real filesystem (no mocking of path resolution or
    file parsing, per `.agent/rules/test-driven-development.md`).

Layer: plugins/sharepoint-discovery -- tests
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


@pytest.fixture()
def rules():
    return load_rules(DEFAULT_RULES_PATH)


@pytest.fixture()
def inventory():
    return json.loads((FIXTURES / "page-inventory.json").read_text(encoding="utf-8"))


def test_default_rules_asset_is_packaged_and_loadable(rules):
    assert DEFAULT_RULES_PATH.is_file()
    assert {r["category"] for r in rules["webPartRules"]} >= {"CEWP", "SEWP", "Other"}


def test_complexity_escalates_with_script_editor_and_connections(inventory, rules):
    plan = analyse(inventory, rules)
    by_name = {p["fileName"]: p for p in plan["pages"]}
    assert by_name["simple.aspx"]["complexityLabel"] == "Low"
    assert by_name["scripted.aspx"]["complexityScore"] > by_name["simple.aspx"]["complexityScore"]
    assert by_name["scripted.aspx"]["hasCustomException"] is True


def test_dependency_matrix_is_sorted_by_complexity_descending(inventory, rules):
    plan = analyse(inventory, rules)
    scores = [p["complexityScore"] for p in plan["dependencyMatrix"]]
    assert scores == sorted(scores, reverse=True)


def test_unknown_web_part_category_falls_back_to_other_not_a_crash(rules):
    plan = analyse(
        [{"FileName": "odd.aspx", "Category": "SitePage", "WebParts": [{"Category": "NoSuchThing"}]}],
        rules,
    )
    assert plan["pages"][0]["webParts"][0]["approach"] == "custom-exception"


def test_stats_account_for_every_page(inventory, rules):
    plan = analyse(inventory, rules)
    by_complexity = plan["stats"]["byComplexity"]
    assert sum(by_complexity.values()) == plan["stats"]["totalPages"] == len(inventory)


def test_report_contains_no_project_literals(inventory, rules):
    report = generate_report(analyse(inventory, rules))
    lowered = report.lower()
    for literal in [__import__("base64").b64decode(x).decode() for x in ['anVzdGlu', 'Y2Vpcw==', 'Y291cnRob3VzZQ==', 'aXRhdQ==', 'amFnLmdvdi5iYy5jYQ==', 'Y21hdA==']]:
        assert literal not in lowered


def test_run_writes_both_artifacts_and_reports_observed(tmp_path, rules):
    outcome = run(
        inventory_path=FIXTURES / "page-inventory.json",
        rules_path=DEFAULT_RULES_PATH,
        output_dir=tmp_path,
    )
    assert outcome.status is DiscoveryStatus.OBSERVED
    assert (tmp_path / "page-inventory-plan.json").is_file()
    assert (tmp_path / "page-inventory-plan.md").is_file()
    assert len(outcome.artifacts) == 2


def test_run_with_missing_inventory_is_unavailable_and_writes_nothing(tmp_path):
    outcome = run(
        inventory_path=tmp_path / "nope.json",
        rules_path=DEFAULT_RULES_PATH,
        output_dir=tmp_path / "out",
    )
    assert outcome.status is DiscoveryStatus.UNAVAILABLE
    # Stronger than "no artifacts": the output directory is never even created.
    assert not (tmp_path / "out").exists()


def test_run_with_missing_rules_is_unavailable(tmp_path):
    outcome = run(
        inventory_path=FIXTURES / "page-inventory.json",
        rules_path=tmp_path / "no-rules.json",
        output_dir=tmp_path / "out",
    )
    assert outcome.status is DiscoveryStatus.UNAVAILABLE


def test_run_with_empty_inventory_is_empty_not_observed(tmp_path):
    src = tmp_path / "empty.json"
    src.write_text("[]", encoding="utf-8")
    outcome = run(inventory_path=src, rules_path=DEFAULT_RULES_PATH, output_dir=tmp_path / "out")
    assert outcome.status is DiscoveryStatus.EMPTY
    assert (tmp_path / "out" / "page-inventory-plan.json").is_file()


def test_run_with_malformed_inventory_is_failed(tmp_path):
    src = tmp_path / "bad.json"
    src.write_text("{{{", encoding="utf-8")
    outcome = run(inventory_path=src, rules_path=DEFAULT_RULES_PATH, output_dir=tmp_path / "out")
    assert outcome.status is DiscoveryStatus.FAILED
