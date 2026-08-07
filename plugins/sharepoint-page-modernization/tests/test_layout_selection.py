"""
test_layout_selection.py
========================

Stage 3 tests -- data-driven modern layout selection.

Semantic-parity oracle: CMAT `tests/test_select_layout.py`. Retained
behaviours: LR-001..LR-004 rule outcomes, first-match-wins ordering, the
DEFAULT fallback, and the presence of `ruleApplied`/`pnpFlag`/`rationale` on
every decision.

Intentional improvement: CMAT evaluated rule conditions with `eval()` and
silently swallowed any rule that raised. This port uses a restricted AST
evaluator and records every rejected rule in `skippedRules` with a reason --
a malformed rule must be visible, not invisible.
"""

import json
import subprocess
import sys


def run_layout(scripts_dir, assets_dir, components, tmp_path, rules_path=None) -> dict:
    model_file = tmp_path / "component-model.json"
    model_file.write_text(json.dumps({"components": components}), encoding="utf-8")
    out_file = tmp_path / "layout-decision.json"
    args = [sys.executable, str(scripts_dir / "layout_selection.py"),
            "--input", str(model_file), "--output", str(out_file)]
    if rules_path is not None:
        args += ["--rules", str(rules_path)]
    result = subprocess.run(args, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    return json.loads(out_file.read_text(encoding="utf-8"))


def test_one_primary_few_secondary_is_one_column(scripts_dir, assets_dir, tmp_path):
    d = run_layout(scripts_dir, assets_dir, [
        {"role": "Banner", "type": "ContentEditor"},
        {"role": "Primary", "type": "XsltListView"},
        {"role": "Child", "type": "XsltListView"},
    ], tmp_path)
    assert (d["selectedLayout"], d["sectionTemplate"], d["ruleApplied"]) == ("Home", "OneColumn", "LR-001")


def test_one_primary_three_secondary_is_two_column(scripts_dir, assets_dir, tmp_path):
    d = run_layout(scripts_dir, assets_dir, [
        {"role": "Primary", "type": "XsltListView"},
        {"role": "Secondary", "type": "XsltListView"},
        {"role": "Secondary", "type": "XsltListView"},
        {"role": "Secondary", "type": "XsltListView"},
    ], tmp_path)
    assert (d["sectionTemplate"], d["ruleApplied"]) == ("TwoColumn", "LR-002")


def test_content_only_page_is_article(scripts_dir, assets_dir, tmp_path):
    d = run_layout(scripts_dir, assets_dir, [
        {"role": "Banner", "type": "ContentEditor"},
        {"role": "Banner", "type": "ContentEditor"},
    ], tmp_path)
    assert (d["selectedLayout"], d["ruleApplied"]) == ("Article", "LR-003")


def test_summary_links_only_page_matches_lr004(scripts_dir, assets_dir, tmp_path):
    d = run_layout(scripts_dir, assets_dir, [{"role": "Secondary", "type": "SummaryLinks"}], tmp_path)
    assert (d["selectedLayout"], d["sectionTemplate"], d["ruleApplied"]) == ("Home", "OneColumn", "LR-004")


def test_first_matching_rule_wins(scripts_dir, assets_dir, tmp_path):
    d = run_layout(scripts_dir, assets_dir, [
        {"role": "Primary", "type": "XsltListView"},
        {"role": "Banner", "type": "SummaryLinks"},
    ], tmp_path)
    assert d["ruleApplied"] == "LR-001"


def test_decision_carries_rule_pnp_flag_and_rationale(scripts_dir, assets_dir, tmp_path):
    d = run_layout(scripts_dir, assets_dir, [{"role": "Primary", "type": "XsltListView"}], tmp_path)
    assert d["ruleApplied"].startswith("LR-") or d["ruleApplied"] == "DEFAULT"
    assert d["pnpFlag"].startswith("-LayoutType")
    assert isinstance(d["rationale"], str) and d["rationale"]


def test_empty_component_list_falls_back_to_default_and_reports_empty(scripts_dir, assets_dir, tmp_path):
    d = run_layout(scripts_dir, assets_dir, [], tmp_path)
    assert d["selectedLayout"] == "Home"
    assert d["ruleApplied"] == "DEFAULT"
    assert d["outcome"]["status"] == "Empty"


def test_packaged_rules_are_used_when_no_rules_flag_is_given(scripts_dir, assets_dir, tmp_path):
    """The plugin ships its own layout rules; a caller must not have to locate them."""
    d = run_layout(scripts_dir, assets_dir, [{"role": "Primary", "type": "XsltListView"}], tmp_path)
    assert d["rulesSource"].endswith("layout-rules.json")


def test_malformed_rule_condition_is_recorded_not_silently_skipped(scripts_dir, assets_dir, tmp_path):
    bad_rules = tmp_path / "bad-rules.json"
    bad_rules.write_text(json.dumps({"version": "test", "rules": [
        {"id": "BAD-001", "condition": "__import__('os').system('true')", "layout": "Home",
         "sectionTemplate": "OneColumn", "rationale": "hostile"},
        {"id": "LR-001", "condition": "primaryCount == 1", "layout": "Home",
         "sectionTemplate": "OneColumn", "rationale": "ok"},
    ]}), encoding="utf-8")
    d = run_layout(scripts_dir, assets_dir, [{"role": "Primary", "type": "XsltListView"}],
                   tmp_path, rules_path=bad_rules)
    assert d["ruleApplied"] == "LR-001"
    assert any(s["id"] == "BAD-001" for s in d["skippedRules"])
    assert d["outcome"]["status"] == "Partial"


def test_rule_condition_cannot_execute_arbitrary_code(scripts_dir, assets_dir, tmp_path):
    """A rules file is data, not code: a call expression must never be evaluated."""
    marker = tmp_path / "pwned.txt"
    hostile = tmp_path / "hostile-rules.json"
    hostile.write_text(json.dumps({"version": "test", "rules": [
        {"id": "EVIL", "condition": f"open({str(marker)!r}, 'w').write('x') or primaryCount == 1",
         "layout": "Home", "sectionTemplate": "OneColumn", "rationale": "hostile"},
    ]}), encoding="utf-8")
    d = run_layout(scripts_dir, assets_dir, [{"role": "Primary", "type": "XsltListView"}],
                   tmp_path, rules_path=hostile)
    assert not marker.exists()
    assert d["ruleApplied"] == "DEFAULT"


def test_missing_rules_file_fails_honestly(scripts_dir, tmp_path):
    model_file = tmp_path / "m.json"
    model_file.write_text(json.dumps({"components": []}), encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(scripts_dir / "layout_selection.py"),
         "--input", str(model_file), "--rules", str(tmp_path / "nope.json"),
         "--output", str(tmp_path / "o.json")],
        capture_output=True, text=True,
    )
    assert result.returncode != 0
    assert "Unavailable" in result.stderr
