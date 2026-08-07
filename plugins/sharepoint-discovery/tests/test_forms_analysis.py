"""
test_forms_analysis.py

Purpose:
    Contract, negative, and genericity tests for the custom list form inventory
    analyser. Uses real fixture files on a real filesystem per
    `.agent/rules/test-driven-development.md`.

Layer: plugins/sharepoint-discovery -- tests
"""

import json
from pathlib import Path

import pytest

from discovery_inputs import DiscoveryStatus
from forms_analysis import DEFAULT_RULES_PATH, analyse, generate_report, load_rules, run

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture()
def rules():
    return load_rules(DEFAULT_RULES_PATH)


@pytest.fixture()
def forms():
    return json.loads((FIXTURES / "forms.json").read_text(encoding="utf-8"))


def test_default_rules_asset_is_packaged_and_loadable(rules):
    assert DEFAULT_RULES_PATH.is_file()
    assert {"outOfBox", "script", "infopath"} <= set(rules["strategies"].keys())


def test_classifies_script_infopath_and_out_of_box(forms, rules):
    plan = analyse(forms, rules)
    assert plan["stats"]["totalForms"] == 3
    assert plan["stats"]["outOfBoxForms"] == 1
    assert plan["stats"]["scriptForms"] == 1
    assert plan["stats"]["infopathForms"] == 1


def test_custom_items_carry_a_caller_supplied_strategy(forms, rules):
    plan = analyse(forms, rules)
    by_name = {i["listName"]: i for i in plan["customItems"]}
    assert by_name["Requests"]["formKind"] == "script"
    assert by_name["Requests"]["strategy"] == rules["strategies"]["script"]
    assert by_name["Feedback"]["formKind"] == "infopath"


def test_out_of_box_forms_are_not_in_custom_items(forms, rules):
    plan = analyse(forms, rules)
    names = {i["listName"] for i in plan["customItems"]}
    assert "Announcements" not in names


def test_report_contains_no_project_literals(forms, rules):
    report = generate_report(analyse(forms, rules))
    lowered = report.lower()
    for literal in ("justin", "ceis", "courthouse", "itau", "jag.gov.bc.ca", "cmat", "csb"):
        assert literal not in lowered


def test_run_writes_artifact_and_reports_observed(tmp_path, rules):
    outcome = run(forms_path=FIXTURES / "forms.json", rules_path=DEFAULT_RULES_PATH, output_dir=tmp_path)
    assert outcome.status is DiscoveryStatus.OBSERVED
    assert (tmp_path / "forms-plan.json").is_file()
    assert (tmp_path / "forms-plan.md").is_file()


def test_run_with_missing_forms_is_unavailable_and_writes_nothing(tmp_path):
    outcome = run(forms_path=tmp_path / "nope.json", rules_path=DEFAULT_RULES_PATH, output_dir=tmp_path / "out")
    assert outcome.status is DiscoveryStatus.UNAVAILABLE
    assert not (tmp_path / "out").exists()


def test_run_with_missing_rules_is_unavailable(tmp_path):
    outcome = run(forms_path=FIXTURES / "forms.json", rules_path=tmp_path / "no-rules.json", output_dir=tmp_path / "out")
    assert outcome.status is DiscoveryStatus.UNAVAILABLE


def test_run_with_empty_forms_is_empty_not_observed(tmp_path):
    src = tmp_path / "empty.json"
    src.write_text("[]", encoding="utf-8")
    outcome = run(forms_path=src, rules_path=DEFAULT_RULES_PATH, output_dir=tmp_path / "out")
    assert outcome.status is DiscoveryStatus.EMPTY
    assert (tmp_path / "out" / "forms-plan.json").is_file()


def test_run_with_malformed_forms_is_failed(tmp_path):
    src = tmp_path / "bad.json"
    src.write_text("{{{", encoding="utf-8")
    outcome = run(forms_path=src, rules_path=DEFAULT_RULES_PATH, output_dir=tmp_path / "out")
    assert outcome.status is DiscoveryStatus.FAILED


def test_run_with_non_array_forms_is_failed(tmp_path):
    src = tmp_path / "obj.json"
    src.write_text("{}", encoding="utf-8")
    outcome = run(forms_path=src, rules_path=DEFAULT_RULES_PATH, output_dir=tmp_path / "out")
    assert outcome.status is DiscoveryStatus.FAILED
