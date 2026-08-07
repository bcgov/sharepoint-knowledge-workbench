"""
test_link_rules.py
==================

Purpose:
    Contract and safety tests for ``link_rules`` -- the URL rewrite ruleset
    loader. The ruleset is the only place source/target URLs are allowed to
    exist, and it is always caller-supplied: the module ships no built-in
    default rules and no built-in host names.

Layer: sharepoint-link-remediation / tests
"""

import json
from pathlib import Path

import pytest

from link_rules import RewriteRule, RewriteRuleset, RulesetError, load_ruleset

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def test_load_ruleset_reads_a_real_file():
    ruleset = load_ruleset(FIXTURES / "rewrite-rules.json")

    assert isinstance(ruleset, RewriteRuleset)
    assert len(ruleset.rules) == 2
    assert isinstance(ruleset.rules[0], RewriteRule)
    assert ruleset.rules[0].match == "http://legacy.example.internal/Pages/"


def test_rules_are_applied_in_declared_order_most_specific_first():
    ruleset = load_ruleset(FIXTURES / "rewrite-rules.json")
    rewritten, applied = ruleset.apply("http://legacy.example.internal/Pages/overview.aspx")

    assert rewritten == "https://example.sharepoint.com/sites/Demo/SitePages/overview.aspx"
    assert [rule.match for rule in applied] == ["http://legacy.example.internal/Pages/"]


def test_apply_returns_input_unchanged_when_no_rule_matches():
    ruleset = load_ruleset(FIXTURES / "rewrite-rules.json")
    rewritten, applied = ruleset.apply("https://www.example.org/reference")

    assert rewritten == "https://www.example.org/reference"
    assert applied == []


def test_matching_is_case_insensitive():
    ruleset = RewriteRuleset.from_dict({"rules": [{"match": "/pages/", "replacement": "/SitePages/"}]})
    rewritten, applied = ruleset.apply("/PAGES/a.aspx")

    assert rewritten == "/SitePages/a.aspx"
    assert applied


def test_match_is_a_literal_not_a_regex():
    ruleset = RewriteRuleset.from_dict({"rules": [{"match": "a.b", "replacement": "X"}]})

    assert ruleset.apply("axb")[0] == "axb"
    assert ruleset.apply("a.b")[0] == "X"


def test_missing_ruleset_file_raises_rulesetError(tmp_path):
    with pytest.raises(RulesetError) as excinfo:
        load_ruleset(tmp_path / "nope.json")

    assert "not found" in str(excinfo.value).lower()


def test_malformed_json_raises_rulesetError(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("{ not json ")

    with pytest.raises(RulesetError):
        load_ruleset(bad)


def test_empty_ruleset_is_rejected(tmp_path):
    empty = tmp_path / "empty.json"
    empty.write_text(json.dumps({"rules": []}))

    with pytest.raises(RulesetError) as excinfo:
        load_ruleset(empty)

    assert "at least one" in str(excinfo.value).lower()


@pytest.mark.parametrize(
    "rule",
    [
        {"replacement": "/SitePages/"},
        {"match": "/Pages/"},
        {"match": "", "replacement": "/SitePages/"},
        {"match": 7, "replacement": "/SitePages/"},
    ],
)
def test_malformed_rule_entries_are_rejected(rule):
    with pytest.raises(RulesetError):
        RewriteRuleset.from_dict({"rules": [rule]})


def test_module_ships_no_default_rules_and_no_urls():
    source = (Path(__file__).resolve().parents[1] / "scripts" / "link_rules.py").read_text()

    assert "http://" not in source
    assert "https://" not in source
    assert ".sharepoint.com" not in source
