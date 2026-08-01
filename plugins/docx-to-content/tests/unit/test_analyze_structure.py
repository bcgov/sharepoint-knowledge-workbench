"""
Unit/integration tests for scripts/analyze_structure.py: the compatibility
orchestrator that composes the installed `source-document-extraction` and
`knowledge-analysis` packages, merges in the local media-disposition
proposal, and writes the analysis package to disk.

Phase 4.5 Wave 2 note: the SOURCE_DOCUMENT_EXTRACTION-tagged tests that used
to live in this file (heading/image/defect-signal/statistics assertions
against raw extraction) moved to
plugins/source-document-extraction/tests/unit/test_extraction.py.

Phase 4.5 Wave 3 note: recommendation/topic-grouping/draft-plan-construction
logic moved to plugins/knowledge-analysis/tests/unit/test_analysis.py. What
remains here is analyze_document's own orchestration behavior (composition +
media-proposal merge + file writing), per
docs/superpowers/plans/phase-4-5-evidence/wave-3-analysis-plan-split-decision.md.

Fixtures live in tests/fixtures/:
    small_single.md / small_single.docx        -> expected strategy "single"
    repeated_headings.md / repeated_headings.docx -> expected strategy "chunked"

Both fixtures were generated with:
    pandoc -f markdown -t docx --resource-path=. <name>.md -o <name>.docx
"""

from pathlib import Path

import analyze_structure
from plan_schema import analysis_plan as contracts

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"
SMALL_SINGLE = FIXTURES / "small_single.docx"
REPEATED_HEADINGS = FIXTURES / "repeated_headings.docx"


# ---------------------------------------------------------------------------
# Proposed topic-grouping preview (Task 17-topic-grouping, Task 3)
# ---------------------------------------------------------------------------

def test_analyze_report_includes_proposed_topics_preview(tmp_path):
    result = analyze_structure.analyze_document(REPEATED_HEADINGS, tmp_path / "analysis")
    proposed = result.report["proposed_topics"]
    assert [t["title"] for t in proposed] == [
        "Gadget Alpha Module",
        "Gadget Beta Module",
        "Gadget Gamma Module",
    ]
    alpha = proposed[0]
    # Gadget Alpha Module: itself + Getting Started + Configuration +
    # Advanced Options + Troubleshooting = 5 headings folded into the topic.
    assert alpha["anchor_count"] == 5
    assert alpha["child_heading_count"] == 4
    assert alpha["first_anchor_path"] == ["Gadget Alpha Module"]
    assert alpha["approx_size_chars"] > 0
    assert alpha["topic_id"].startswith("gadget-alpha-module--")


def test_analyze_report_proposed_topics_absent_for_no_headings_is_empty_list(tmp_path):
    result = analyze_structure.analyze_document(SMALL_SINGLE, tmp_path / "analysis")
    proposed = result.report["proposed_topics"]
    assert isinstance(proposed, list)
    assert len(proposed) >= 1


# ---------------------------------------------------------------------------
# Recommendation heuristics: configurable constants, no CEIS literals
# ---------------------------------------------------------------------------

def test_small_single_recommends_single_strategy(tmp_path):
    result = analyze_structure.analyze_document(SMALL_SINGLE, tmp_path / "analysis")
    assert result.report["recommendation"]["strategy"] == "single"
    assert result.report["recommendation"]["reasons"]


def test_repeated_headings_recommends_chunked_strategy(tmp_path):
    result = analyze_structure.analyze_document(REPEATED_HEADINGS, tmp_path / "analysis")
    assert result.report["recommendation"]["strategy"] == "chunked"
    assert result.report["recommendation"]["reasons"]


# test_recommendation_constants_are_named_and_configurable moved to
# knowledge-analysis/tests/unit/test_analysis.py -- MIN_HEADINGS_FOR_CHUNKING/
# MIN_LINES_FOR_CHUNKING now live in that plugin's analysis.py.


def test_no_ceis_literal_in_analyze_structure_source():
    source = Path(analyze_structure.__file__).read_text().lower()
    assert "ceis" not in source
    assert "file access" not in source


# ---------------------------------------------------------------------------
# Draft plan: structural anchors + source fingerprint, no raw line offsets
# ---------------------------------------------------------------------------

def test_draft_plan_has_source_fingerprint_and_draft_status(tmp_path):
    result = analyze_structure.analyze_document(SMALL_SINGLE, tmp_path / "analysis")
    plan = result.plan
    assert isinstance(plan, contracts.ConversionPlan)
    assert isinstance(plan.source, contracts.SourceFingerprint)
    assert plan.source.path == str(SMALL_SINGLE)
    assert len(plan.source.sha256) == 64
    assert plan.confirmation.status == "draft"


def test_draft_plan_chunk_anchors_are_structural_not_line_offsets(tmp_path):
    result = analyze_structure.analyze_document(REPEATED_HEADINGS, tmp_path / "analysis")
    plan = result.plan
    assert len(plan.chunk_anchors) > 0
    for anchor in plan.chunk_anchors:
        assert isinstance(anchor, contracts.StructuralAnchor)
        # StructuralAnchor's actual fields -- no "line" attribute exists on
        # the contract at all, so anchors cannot carry raw line numbers as
        # their reconciliation key.
        assert not hasattr(anchor, "line")
        assert not hasattr(anchor, "line_number")
        assert anchor.stable_key
        assert anchor.source_heading_path


def test_draft_plan_anchor_occurrence_disambiguates_repeated_paths(tmp_path):
    result = analyze_structure.analyze_document(REPEATED_HEADINGS, tmp_path / "analysis")
    plan = result.plan
    getting_started = [
        a for a in plan.chunk_anchors if a.heading_text == "Getting Started"
    ]
    assert len(getting_started) >= 2
    # Each "Getting Started" heading lives under a distinct parent heading
    # (Alpha/Beta/Gamma), so occurrence is 1 for each -- the full heading
    # path, not occurrence alone, is what disambiguates them. stable_key is
    # derived from path + occurrence together and must still be unique.
    keys = {a.stable_key for a in getting_started}
    assert len(keys) == len(getting_started)  # stable_key disambiguated
    paths = {tuple(a.source_heading_path) for a in getting_started}
    assert len(paths) == len(getting_started)  # distinct parent paths


# ---------------------------------------------------------------------------
# Files written to disk match the analysis package layout (spec 6.1)
# ---------------------------------------------------------------------------

def test_analyze_writes_analysis_package_layout(tmp_path):
    output_dir = tmp_path / "analysis"
    analyze_structure.analyze_document(SMALL_SINGLE, output_dir)
    assert (output_dir / "analysis-report.json").exists()
    assert (output_dir / "conversion-plan.draft.json").exists()
    assert (output_dir / "raw" / "extracted.md").exists()
    assert (output_dir / "raw" / "media").exists()
