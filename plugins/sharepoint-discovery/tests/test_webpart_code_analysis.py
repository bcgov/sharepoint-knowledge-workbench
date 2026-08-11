"""
test_webpart_code_analysis.py

Purpose:
    Contract, negative, ambiguity, and genericity tests for the web part code
    classifier. The CMAT source of this module carried a hardcoded, site-specific
    knowledge base (named JavaScript helper files and named business-rule heuristics);
    these tests pin the requirement that the shipped default knowledge base is EMPTY and
    that all site knowledge arrives via a caller-supplied file.

Layer: plugins/sharepoint-discovery -- tests
"""

import csv
import json
from pathlib import Path

import pytest

from discovery_inputs import DiscoveryStatus
from webpart_code_analysis import (
    DEFAULT_KNOWLEDGE_BASE,
    KnowledgeBase,
    analyse,
    classify,
    generate_instance_csv,
    generate_report,
    run,
)

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture()
def entries():
    return json.loads((FIXTURES / "webpart-content.json").read_text(encoding="utf-8"))


# -- Genericity ---------------------------------------------------------------

def test_default_knowledge_base_is_empty():
    """No site-specific helper names or business rules ship with this plugin."""
    assert DEFAULT_KNOWLEDGE_BASE.helper_summaries == {}
    assert DEFAULT_KNOWLEDGE_BASE.inline_logic_rules == ()


def test_module_source_contains_no_project_literals():
    source = Path(webpart_source_path()).read_text(encoding="utf-8").lower()
    for literal in ("justin", "ceis", "courthouse", "itau", "pio_cases", "icm_cases", "cmat", "jag.gov.bc.ca"):
        assert literal not in source, f"project literal {literal!r} leaked into the module"


def webpart_source_path():
    import webpart_code_analysis

    return webpart_code_analysis.__file__


# -- Classification -----------------------------------------------------------

def test_empty_content_is_empty_category():
    result = classify({"Content": "", "WebPartTitle": "Banner"}, DEFAULT_KNOWLEDGE_BASE)
    assert result["category"] == "Empty"


def test_empty_script_editor_is_flagged_as_unretrievable_not_empty():
    result = classify({"Content": "", "WebPartTitle": "Script Editor"}, DEFAULT_KNOWLEDGE_BASE)
    assert result["category"] == "ScriptEditorMissing"


def test_inline_script_is_detected():
    result = classify({"Content": "<div><script>alert(1)</script></div>", "WebPartTitle": "X"}, DEFAULT_KNOWLEDGE_BASE)
    assert result["category"] == "InlineLogic"
    assert "alert(1)" in result["inline_script"]


def test_logic_hidden_in_a_display_none_textarea_is_still_detected():
    content = '<textarea style="display:none;">var x = 1;</textarea>'
    result = classify({"Content": content, "WebPartTitle": "X"}, DEFAULT_KNOWLEDGE_BASE)
    assert result["category"] == "InlineLogic"
    assert "var x = 1;" in result["inline_script"]


def test_jquery_reference_alone_does_not_count_as_a_custom_helper():
    content = '<script src="/assets/js/jquery-3.5.0.js"></script><p>Hi</p>'
    result = classify({"Content": content, "WebPartTitle": "X"}, DEFAULT_KNOWLEDGE_BASE)
    assert result["category"] == "TextOnly"
    assert result["external_srcs"] == ["jquery-3.5.0.js"]


def test_external_helper_reference_is_its_own_category():
    content = '<script src="/assets/js/HideGear.js"></script>'
    result = classify({"Content": content, "WebPartTitle": "X"}, DEFAULT_KNOWLEDGE_BASE)
    assert result["category"] == "ExternalHelpersOnly"


def test_identical_inline_logic_groups_together(entries):
    plan = analyse(entries, DEFAULT_KNOWLEDGE_BASE)
    inline_groups = [g for g in plan["groups"] if g["category"] == "InlineLogic"]
    # scripted-a.aspx and scripted-b.aspx carry byte-identical inline logic.
    assert any(g["instanceCount"] == 2 for g in inline_groups)


def test_grouping_signatures_are_stable_across_runs(entries):
    first = [g["signature"] for g in analyse(entries, DEFAULT_KNOWLEDGE_BASE)["groups"]]
    second = [g["signature"] for g in analyse(entries, DEFAULT_KNOWLEDGE_BASE)["groups"]]
    assert first == second


def test_unrecognised_helper_is_surfaced_for_review_not_guessed():
    content = '<script src="/assets/js/SomethingNobodyKnows.js"></script>'
    plan = analyse(
        [{"PageUrl": "/p.aspx", "WebPartId": "1", "WebPartTitle": "X", "Content": content}],
        DEFAULT_KNOWLEDGE_BASE,
    )
    assert "unrecognised" in plan["groups"][0]["summary"].lower()


def test_caller_supplied_knowledge_base_is_applied(tmp_path):
    kb_file = tmp_path / "kb.json"
    kb_file.write_text(
        json.dumps(
            {
                "helperSummaries": {"SomethingNobodyKnows.js": "Renames a button label."},
                "inlineLogicRules": [
                    {
                        "match": ["lockField"],
                        "summary": "Locks a field once a status value is reached.",
                        "modernEquivalent": "Low-code form rule",
                        "effort": "Low",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    kb = KnowledgeBase.from_file(kb_file)
    assert kb.helper_summaries["SomethingNobodyKnows.js"] == "Renames a button label."

    plan = analyse(
        [{"PageUrl": "/p.aspx", "WebPartId": "1", "WebPartTitle": "X",
          "Content": "<script>lockField();</script>"}],
        kb,
    )
    assert "Locks a field" in plan["groups"][0]["summary"]
    assert plan["groups"][0]["effort"] == "Low"


def test_knowledge_base_from_missing_file_is_rejected_not_silently_empty(tmp_path):
    with pytest.raises(FileNotFoundError):
        KnowledgeBase.from_file(tmp_path / "absent.json")


# -- Narrative assessment (businessIntent / enforcementLevel / spfxAssessment) --

def test_text_only_group_gets_generic_display_only_assessment(entries):
    plan = analyse(entries, DEFAULT_KNOWLEDGE_BASE)
    text_group = next(g for g in plan["groups"] if g["category"] == "TextOnly")
    assert "display only" in text_group["enforcementLevel"].lower()
    assert "not required" in text_group["spfxAssessment"].lower()


def test_empty_group_gets_none_needed_assessment():
    plan = analyse(
        [{"PageUrl": "/p.aspx", "WebPartId": "1", "WebPartTitle": "X", "Content": ""}],
        DEFAULT_KNOWLEDGE_BASE,
    )
    group = plan["groups"][0]
    assert group["businessIntent"].startswith("None")
    assert "not required" in group["spfxAssessment"].lower()


def test_unrecognised_inline_logic_is_honest_unknown_not_guessed():
    plan = analyse(
        [{"PageUrl": "/p.aspx", "WebPartId": "1", "WebPartTitle": "X",
          "Content": "<script>doSomethingObscure();</script>"}],
        DEFAULT_KNOWLEDGE_BASE,
    )
    group = plan["groups"][0]
    assert "unknown" in group["businessIntent"].lower()
    assert "unknown" in group["spfxAssessment"].lower()


def test_caller_supplied_business_intent_and_spfx_assessment_are_applied():
    kb = KnowledgeBase.from_dict(
        {
            "inlineLogicRules": [
                {
                    "match": ["lockField"],
                    "summary": "Locks a field once a status value is reached.",
                    "modernEquivalent": "Low-code form rule",
                    "effort": "Low",
                    "businessIntent": "Prevent edits to closed records.",
                    "spfxAssessment": "Not required -- a Power Automate flow covers this.",
                }
            ]
        }
    )
    plan = analyse(
        [{"PageUrl": "/p.aspx", "WebPartId": "1", "WebPartTitle": "X",
          "Content": "<script>lockField();</script>"}],
        kb,
    )
    group = plan["groups"][0]
    assert group["businessIntent"] == "Prevent edits to closed records."
    assert group["spfxAssessment"] == "Not required -- a Power Automate flow covers this."


def test_report_includes_business_intent_and_spfx_assessment(entries):
    report = generate_report(analyse(entries, DEFAULT_KNOWLEDGE_BASE))
    assert "Business intent:" in report
    assert "Actual enforcement level:" in report
    assert "SPFx assessment:" in report


# -- Outputs ------------------------------------------------------------------

def test_instance_csv_has_one_row_per_web_part(entries):
    plan = analyse(entries, DEFAULT_KNOWLEDGE_BASE)
    rows = list(csv.reader(generate_instance_csv(entries, plan).splitlines()))
    assert len(rows) == len(entries) + 1  # + header


def test_report_contains_no_project_literals(entries):
    report = generate_report(analyse(entries, DEFAULT_KNOWLEDGE_BASE)).lower()
    for literal in ("justin", "ceis", "courthouse", "itau", "cmat", "jag.gov.bc.ca"):
        assert literal not in report


def test_run_writes_three_artifacts(tmp_path):
    outcome = run(extract_path=FIXTURES / "webpart-content.json", output_dir=tmp_path)
    # PARTIAL, not OBSERVED: the shared fixture deliberately exercises every
    # category including one ScriptEditorMissing entry (a web part whose content
    # could not be retrieved). Reporting that run as OBSERVED would be exactly the
    # silent-partial-success failure mode spec section 13 forbids, so the honest
    # status is asserted here and the clean-input OBSERVED path is covered by
    # test_run_with_fully_retrievable_input_is_observed below.
    assert outcome.status is DiscoveryStatus.PARTIAL
    assert "could not be retrieved" in outcome.detail
    assert (tmp_path / "webpart-code-groups.json").is_file()
    assert (tmp_path / "webpart-code-analysis.md").is_file()
    assert (tmp_path / "webpart-instance-review.csv").is_file()


def test_run_with_fully_retrievable_input_is_observed(tmp_path):
    """The OBSERVED path: every web part retrievable, nothing unresolved."""
    clean = [
        entry
        for entry in json.loads((FIXTURES / "webpart-content.json").read_text(encoding="utf-8"))
        if (entry.get("Content") or "").strip()
    ]
    src = tmp_path / "clean.json"
    src.write_text(json.dumps(clean), encoding="utf-8")

    outcome = run(extract_path=src, output_dir=tmp_path / "out")

    assert outcome.status is DiscoveryStatus.OBSERVED
    assert "could not be retrieved" not in outcome.detail
    assert (tmp_path / "out" / "webpart-code-groups.json").is_file()


def test_run_with_missing_extract_is_unavailable(tmp_path):
    outcome = run(extract_path=tmp_path / "nope.json", output_dir=tmp_path / "out")
    assert outcome.status is DiscoveryStatus.UNAVAILABLE
    assert not (tmp_path / "out").exists()


def test_run_with_empty_extract_is_empty_not_observed(tmp_path):
    src = tmp_path / "e.json"
    src.write_text("[]", encoding="utf-8")
    outcome = run(extract_path=src, output_dir=tmp_path / "out")
    assert outcome.status is DiscoveryStatus.EMPTY


def test_run_with_missing_knowledge_base_is_unavailable(tmp_path):
    outcome = run(
        extract_path=FIXTURES / "webpart-content.json",
        output_dir=tmp_path / "out",
        knowledge_base_path=tmp_path / "absent-kb.json",
    )
    assert outcome.status is DiscoveryStatus.UNAVAILABLE
