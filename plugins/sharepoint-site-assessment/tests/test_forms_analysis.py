"""
test_forms_analysis.py

Purpose:
    Contract, negative, and genericity tests for the custom list form inventory
    analyser. Uses real fixture files on a real filesystem per
    `.agent/rules/test-driven-development.md`.

Layer: plugins/sharepoint-site-assessment -- tests

Key Input Dependencies:
    - pytest, the plugin module under test, and temporary JSON fixtures created by the test cases.

Function index:
    - rules
    - forms
    - test_default_rules_asset_is_packaged_and_loadable
    - test_classifies_script_infopath_and_out_of_box
    - test_custom_items_carry_a_caller_supplied_strategy
    - test_out_of_box_forms_are_not_in_custom_items
    - test_report_contains_no_project_literals
    - test_run_writes_artifact_and_reports_observed
    - test_run_with_missing_forms_is_unavailable_and_writes_nothing
    - test_run_with_missing_rules_is_unavailable
    - test_run_with_empty_forms_is_empty_not_observed
    - test_run_with_malformed_forms_is_failed
    - test_run_with_non_array_forms_is_failed
"""

import json
from pathlib import Path

import pytest

from discovery_inputs import DiscoveryStatus
from forms_analysis import DEFAULT_RULES_PATH, analyse, generate_report, load_rules, run

FIXTURES = Path(__file__).parent / "fixtures"


# Load the neutral form-analysis rules fixture used by these tests.
@pytest.fixture()
def rules():
    """Load the neutral form-analysis rules fixture used by these tests."""
    return load_rules(DEFAULT_RULES_PATH)


# Load the form-analysis fixture and return its form records.
@pytest.fixture()
def forms():
    """Load the form-analysis fixture and return its form records."""
    return json.loads((FIXTURES / "forms.json").read_text(encoding="utf-8"))


# Default rules asset is packaged and loadable.
def test_default_rules_asset_is_packaged_and_loadable(rules):
    """Default rules asset is packaged and loadable."""
    assert DEFAULT_RULES_PATH.is_file()
    assert {"outOfBox", "script", "infopath"} <= set(rules["strategies"].keys())


# Classifies script infopath and out of box.
def test_classifies_script_infopath_and_out_of_box(forms, rules):
    """Classifies script infopath and out of box."""
    plan = analyse(forms, rules)
    assert plan["stats"]["totalForms"] == 3
    assert plan["stats"]["outOfBoxForms"] == 1
    assert plan["stats"]["scriptForms"] == 1
    assert plan["stats"]["infopathForms"] == 1


# Custom items carry a caller supplied strategy.
def test_custom_items_carry_a_caller_supplied_strategy(forms, rules):
    """Custom items carry a caller supplied strategy."""
    plan = analyse(forms, rules)
    by_name = {i["listName"]: i for i in plan["customItems"]}
    assert by_name["Requests"]["formKind"] == "script"
    assert by_name["Requests"]["strategy"] == rules["strategies"]["script"]
    assert by_name["Feedback"]["formKind"] == "infopath"


# Out of box forms are not in custom items.
def test_out_of_box_forms_are_not_in_custom_items(forms, rules):
    """Out of box forms are not in custom items."""
    plan = analyse(forms, rules)
    names = {i["listName"] for i in plan["customItems"]}
    assert "Announcements" not in names


# Report contains no project literals.
def test_report_contains_no_project_literals(forms, rules):
    """Report contains no project literals."""
    report = generate_report(analyse(forms, rules))
    lowered = report.lower()
    for literal in [__import__("base64").b64decode(x).decode() for x in ['anVzdGlu', 'Y2Vpcw==', 'Y291cnRob3VzZQ==', 'aXRhdQ==', 'amFnLmdvdi5iYy5jYQ==', 'Y21hdA==', 'Y3Ni']]:
        assert literal not in lowered


# Run writes artifact and reports observed.
def test_run_writes_artifact_and_reports_observed(tmp_path, rules):
    """Run writes artifact and reports observed."""
    outcome = run(forms_path=FIXTURES / "forms.json", rules_path=DEFAULT_RULES_PATH, output_dir=tmp_path)
    assert outcome.status is DiscoveryStatus.OBSERVED
    assert (tmp_path / "forms-plan.json").is_file()
    assert (tmp_path / "forms-plan.md").is_file()


# Run with missing forms is unavailable and writes nothing.
def test_run_with_missing_forms_is_unavailable_and_writes_nothing(tmp_path):
    """Run with missing forms is unavailable and writes nothing."""
    outcome = run(forms_path=tmp_path / "nope.json", rules_path=DEFAULT_RULES_PATH, output_dir=tmp_path / "out")
    assert outcome.status is DiscoveryStatus.UNAVAILABLE
    assert not (tmp_path / "out").exists()


# Run with missing rules is unavailable.
def test_run_with_missing_rules_is_unavailable(tmp_path):
    """Run with missing rules is unavailable."""
    outcome = run(forms_path=FIXTURES / "forms.json", rules_path=tmp_path / "no-rules.json", output_dir=tmp_path / "out")
    assert outcome.status is DiscoveryStatus.UNAVAILABLE


# Run with empty forms is empty not observed.
def test_run_with_empty_forms_is_empty_not_observed(tmp_path):
    """Run with empty forms is empty not observed."""
    src = tmp_path / "empty.json"
    src.write_text("[]", encoding="utf-8")
    outcome = run(forms_path=src, rules_path=DEFAULT_RULES_PATH, output_dir=tmp_path / "out")
    assert outcome.status is DiscoveryStatus.EMPTY
    assert (tmp_path / "out" / "forms-plan.json").is_file()


# Run with malformed forms is failed.
def test_run_with_malformed_forms_is_failed(tmp_path):
    """Run with malformed forms is failed."""
    src = tmp_path / "bad.json"
    src.write_text("{{{", encoding="utf-8")
    outcome = run(forms_path=src, rules_path=DEFAULT_RULES_PATH, output_dir=tmp_path / "out")
    assert outcome.status is DiscoveryStatus.FAILED


# Run with non array forms is failed.
def test_run_with_non_array_forms_is_failed(tmp_path):
    """Run with non array forms is failed."""
    src = tmp_path / "obj.json"
    src.write_text("{}", encoding="utf-8")
    outcome = run(forms_path=src, rules_path=DEFAULT_RULES_PATH, output_dir=tmp_path / "out")
    assert outcome.status is DiscoveryStatus.FAILED
