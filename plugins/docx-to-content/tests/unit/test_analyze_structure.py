"""
Unit/integration tests for scripts/analyze_structure.py and scripts/plans.py
(Task 6): real pandoc invocation against synthetic .docx fixtures, structural
analysis, and draft ConversionPlan generation.

Fixtures live in tests/fixtures/:
    small_single.md / small_single.docx        -> expected strategy "single"
    repeated_headings.md / repeated_headings.docx -> expected strategy "chunked"

Both fixtures were generated with:
    pandoc -f markdown -t docx --resource-path=. <name>.md -o <name>.docx
"""

from pathlib import Path

import pytest

import analyze_structure
import contracts

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"
SMALL_SINGLE = FIXTURES / "small_single.docx"
REPEATED_HEADINGS = FIXTURES / "repeated_headings.docx"


# ---------------------------------------------------------------------------
# Raw pandoc invocation into analysis/raw/ (transitory)
# ---------------------------------------------------------------------------

def test_analyze_runs_pandoc_into_transitory_raw_folder(tmp_path):
    output_dir = tmp_path / "analysis"
    result = analyze_structure.analyze_document(SMALL_SINGLE, output_dir)

    raw_md = output_dir / "raw" / "extracted.md"
    raw_media = output_dir / "raw" / "media"
    assert raw_md.exists()
    assert raw_media.exists()
    assert raw_md.read_text().strip() != ""

    # The raw folder must be visibly marked transitory/disposable somewhere
    # in the analysis report, not silently treated as permanent.
    assert "raw" in result.report
    assert result.report["raw"].get("transitory") is True


def test_analyze_never_writes_canonical_content_folder(tmp_path):
    output_dir = tmp_path / "analysis"
    analyze_structure.analyze_document(REPEATED_HEADINGS, output_dir)
    assert not (output_dir / "canonical-content").exists()
    # search recursively too
    assert not any(p.name == "canonical-content" for p in output_dir.rglob("*"))


# ---------------------------------------------------------------------------
# Structural analysis: heading counts / depth / paths / repeats / images
# ---------------------------------------------------------------------------

def test_heading_counts_by_level_small_single(tmp_path):
    result = analyze_structure.analyze_document(SMALL_SINGLE, tmp_path / "analysis")
    counts = result.report["headings"]["counts_by_level"]
    # small_single.md has one level-1 and two level-2 headings.
    assert counts.get("1") == 1 or counts.get(1) == 1
    assert counts.get("2") == 2 or counts.get(2) == 2


def test_heading_paths_reconstructed_repeated_headings(tmp_path):
    result = analyze_structure.analyze_document(REPEATED_HEADINGS, tmp_path / "analysis")
    paths = result.report["headings"]["paths"]
    joined = [" > ".join(p) for p in paths]
    assert "Gadget Alpha Module > Getting Started" in joined
    assert "Gadget Beta Module > Getting Started" in joined
    assert "Gadget Alpha Module > Configuration > Advanced Options" in joined


def test_repeated_heading_paths_detected(tmp_path):
    result = analyze_structure.analyze_document(REPEATED_HEADINGS, tmp_path / "analysis")
    repeated = result.report["headings"]["repeated_heading_texts"]
    assert "Getting Started" in repeated
    assert repeated["Getting Started"] >= 3  # Alpha, Beta, Gamma


def test_no_repeated_headings_in_small_single(tmp_path):
    result = analyze_structure.analyze_document(SMALL_SINGLE, tmp_path / "analysis")
    repeated = result.report["headings"]["repeated_heading_texts"]
    assert repeated == {}


def test_image_counts_and_formats(tmp_path):
    result = analyze_structure.analyze_document(REPEATED_HEADINGS, tmp_path / "analysis")
    images = result.report["images"]
    assert images["count"] == 1
    assert "png" in images["formats"]


def test_no_images_in_small_single(tmp_path):
    result = analyze_structure.analyze_document(SMALL_SINGLE, tmp_path / "analysis")
    assert result.report["images"]["count"] == 0


# ---------------------------------------------------------------------------
# Raw TOC evidence / known defect signals (reused from pandoc_fixes)
# ---------------------------------------------------------------------------

def test_raw_toc_evidence_absent_in_synthetic_fixtures(tmp_path):
    result = analyze_structure.analyze_document(SMALL_SINGLE, tmp_path / "analysis")
    assert result.report["defect_signals"]["raw_toc_detected"] is False


def test_raw_toc_evidence_detected_when_present(tmp_path):
    # Inject a raw Word TOC field dump directly into an already-extracted
    # markdown file and run the detection function directly (rather than
    # requiring a real Word-generated TOC docx, which pandoc-from-markdown
    # cannot produce).
    from pandoc_fixes.toc import strip_raw_toc

    text = "[]{#_Toc1}\n[Intro](#_Toc123456)\n\n# Real Heading\n"
    cleaned = strip_raw_toc(text)
    assert cleaned != text  # detection reused correctly proves a TOC was found
    assert analyze_structure.detect_raw_toc(text) is True
    assert analyze_structure.detect_raw_toc("# Just a heading\n") is False


def test_known_defect_signal_glued_image_detected():
    text = "## Heading ![](media/image1.png)\n"
    assert analyze_structure.detect_defect_signals(text)["glued_images"] is True
    assert analyze_structure.detect_defect_signals("## Heading\n\n![](media/image1.png)\n")["glued_images"] is False


def test_known_defect_signal_pandoc_attrs_detected():
    text = "![](media/image1.png){width=\"624\" height=\"325\"}\n"
    assert analyze_structure.detect_defect_signals(text)["pandoc_attrs"] is True
    assert analyze_structure.detect_defect_signals("plain text\n")["pandoc_attrs"] is False


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


def test_recommendation_constants_are_named_and_configurable():
    assert isinstance(analyze_structure.MIN_HEADINGS_FOR_CHUNKING, int)
    assert isinstance(analyze_structure.MIN_LINES_FOR_CHUNKING, int)


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


def test_source_not_found_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        analyze_structure.analyze_document(tmp_path / "nope.docx", tmp_path / "analysis")
