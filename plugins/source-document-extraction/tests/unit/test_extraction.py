"""
Unit/integration tests for extraction.extract_and_normalize
(Phase 4.5 Wave 2): real pandoc invocation against synthetic .docx
fixtures and the source-level observations (heading structure, image
stats, defect signals, statistics) `extract_and_normalize` produces.

Ported from docx-to-content's tests/unit/test_analyze_structure.py per
the Wave 0 test ledger's SOURCE_DOCUMENT_EXTRACTION-tagged entries,
adapted to `extract_and_normalize`'s normalized-source-document dict
shape (the orchestration-level `analyze_document`/`AnalysisResult` this
file used to test no longer exists here -- that composition now lives in
`knowledge-analysis` and the compatibility orchestrator).

Fixtures live in tests/fixtures/:
    small_single.docx        -> no repeated headings, no images
    repeated_headings.docx   -> repeated heading texts, one image
"""

from pathlib import Path

import pytest

from extraction import extract_and_normalize
from heading_parsing import (
    compute_statistics,
    detect_defect_signals,
    detect_raw_toc,
)

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"
SMALL_SINGLE = FIXTURES / "small_single.docx"
REPEATED_HEADINGS = FIXTURES / "repeated_headings.docx"


# ---------------------------------------------------------------------------
# Raw pandoc invocation into raw/ (transitory)
# ---------------------------------------------------------------------------

def test_analyze_runs_pandoc_into_transitory_raw_folder(tmp_path):
    output_dir = tmp_path / "analysis"
    result = extract_and_normalize(SMALL_SINGLE, output_dir)

    raw_md = output_dir / "raw" / "extracted.md"
    raw_media = output_dir / "raw" / "media"
    assert raw_md.exists()
    assert raw_media.exists()
    assert raw_md.read_text().strip() != ""
    assert result["markdown_text"].strip() != ""


def test_analyze_never_writes_canonical_content_folder(tmp_path):
    output_dir = tmp_path / "analysis"
    extract_and_normalize(REPEATED_HEADINGS, output_dir)
    assert not (output_dir / "canonical-content").exists()
    assert not any(p.name == "canonical-content" for p in output_dir.rglob("*"))


# ---------------------------------------------------------------------------
# Structural analysis: heading counts / paths / repeats / images
# ---------------------------------------------------------------------------

def test_heading_counts_by_level_small_single(tmp_path):
    result = extract_and_normalize(SMALL_SINGLE, tmp_path / "analysis")
    counts = result["heading_counts_by_level"]
    # small_single.md has one level-1 and two level-2 headings.
    assert counts.get(1) == 1
    assert counts.get(2) == 2


def test_heading_paths_reconstructed_repeated_headings(tmp_path):
    result = extract_and_normalize(REPEATED_HEADINGS, tmp_path / "analysis")
    paths = [h["path"] for h in result["headings"]]
    joined = [" > ".join(p) for p in paths]
    assert "Gadget Alpha Module > Getting Started" in joined
    assert "Gadget Beta Module > Getting Started" in joined
    assert "Gadget Alpha Module > Configuration > Advanced Options" in joined


def test_repeated_heading_paths_detected(tmp_path):
    result = extract_and_normalize(REPEATED_HEADINGS, tmp_path / "analysis")
    repeated = result["repeated_heading_texts"]
    assert "Getting Started" in repeated
    assert repeated["Getting Started"] >= 3  # Alpha, Beta, Gamma


def test_no_repeated_headings_in_small_single(tmp_path):
    result = extract_and_normalize(SMALL_SINGLE, tmp_path / "analysis")
    assert result["repeated_heading_texts"] == {}


def test_image_counts_and_formats(tmp_path):
    result = extract_and_normalize(REPEATED_HEADINGS, tmp_path / "analysis")
    images = result["images"]
    assert images["count"] == 1
    assert "png" in images["formats"]


def test_no_images_in_small_single(tmp_path):
    result = extract_and_normalize(SMALL_SINGLE, tmp_path / "analysis")
    assert result["images"]["count"] == 0


# ---------------------------------------------------------------------------
# Raw TOC evidence / known defect signals (reused from pandoc)
# ---------------------------------------------------------------------------

def test_raw_toc_evidence_absent_in_synthetic_fixtures(tmp_path):
    result = extract_and_normalize(SMALL_SINGLE, tmp_path / "analysis")
    assert result["defect_signals"]["raw_toc_detected"] is False


def test_raw_toc_evidence_detected_when_present():
    # Inject a raw Word TOC field dump directly into already-extracted
    # markdown text and run detection directly (rather than requiring a
    # real Word-generated TOC docx, which pandoc-from-markdown cannot
    # produce).
    from pandoc.toc import strip_raw_toc

    text = "[]{#_Toc1}\n[Intro](#_Toc123456)\n\n# Real Heading\n"
    cleaned = strip_raw_toc(text)
    assert cleaned != text  # detection reused correctly proves a TOC was found
    assert detect_raw_toc(text) is True
    assert detect_raw_toc("# Just a heading\n") is False


def test_raw_toc_evidence_detected_for_slug_anchor_shape():
    # Real-world shape (CEIS Manual): nested slug-anchor TOC links, not
    # `_Toc`-bookmark links.
    text = (
        "**Table of Contents**\n\n"
        "[Section Alpha [1](#section-alpha)](#section-alpha)\n\n"
        "[Section Beta [2](#section-beta)](#section-beta)\n\n"
        "# Section Alpha\n\nBody.\n"
    )
    assert detect_raw_toc(text) is True
    assert detect_defect_signals(text)["raw_toc_detected"] is True


def test_known_defect_signal_glued_image_detected():
    text = "## Heading ![](media/image1.png)\n"
    assert detect_defect_signals(text)["glued_images"] is True
    assert detect_defect_signals("## Heading\n\n![](media/image1.png)\n")["glued_images"] is False


def test_known_defect_signal_leading_glued_image_detected():
    # Real-world shape (CEIS Manual): image glued to the START of the
    # heading text.
    text = "### ![](media/image12.png){width=\"5.45in\"}**Central Divorce**\n"
    assert detect_defect_signals(text)["glued_images"] is True


def test_known_defect_signal_bold_wrapped_heading_detected():
    text = "# **PROTECTION ORDERS**\n\nBody.\n"
    assert detect_defect_signals(text)["bold_wrapped_headings"] is True
    assert detect_defect_signals("# Plain Heading\n")["bold_wrapped_headings"] is False
    # Partial emphasis inside heading text must NOT trigger the signal.
    assert detect_defect_signals("# Getting **Started** Quickly\n")["bold_wrapped_headings"] is False


def test_known_defect_signal_pandoc_attrs_detected():
    text = "![](media/image1.png){width=\"624\" height=\"325\"}\n"
    assert detect_defect_signals(text)["pandoc_attrs"] is True
    assert detect_defect_signals("plain text\n")["pandoc_attrs"] is False


# ---------------------------------------------------------------------------
# Extended analysis statistics
# ---------------------------------------------------------------------------

def test_extended_statistics_present_in_report(tmp_path):
    result = extract_and_normalize(SMALL_SINGLE, tmp_path / "analysis")
    stats = result["statistics"]
    for key in (
        "table_count",
        "footnote_reference_count",
        "footnote_definition_count",
        "local_link_count",
        "image_reference_count",
        "generated_toc_entries_detected",
    ):
        assert key in stats


def test_extended_statistics_counts_are_measured_for_synthetic_text():
    text = (
        "# Heading\n\n"
        "| a | b |\n| --- | --- |\n| 1 | 2 |\n\n"
        "See [Other Heading](#other-heading).\n\n"
        "A footnote reference[^1].\n\n"
        "[^1]: A footnote definition.\n\n"
        "![alt](media/image1.png)\n"
    )
    stats = compute_statistics(text)
    assert stats["table_count"] == 1
    assert stats["footnote_reference_count"] == 1
    assert stats["footnote_definition_count"] == 1
    assert stats["local_link_count"] == 1
    assert stats["image_reference_count"] == 1


def test_table_count_excludes_non_table_horizontal_rule_dash_lines():
    # A dash-only horizontal-rule-shaped line (no pipe characters at all,
    # as pandoc sometimes emits for a Word horizontal-rule or divider) must
    # not be counted as a table separator row -- only genuine pipe-
    # delimited `| --- | --- |` rows count as tables.
    text = (
        "Some prose line.\n\n"
        "  ----------------------------------------------------------------\n\n"
        "More prose after a divider, not a table.\n\n"
        "| a | b |\n| --- | --- |\n| 1 | 2 |\n"
    )
    stats = compute_statistics(text)
    assert stats["table_count"] == 1


def test_table_count_detects_pandoc_grid_tables():
    # Pandoc emits grid tables (bounded by `+---+`/`+===+` lines) for
    # complex/merged-cell Word tables -- these must be counted too, not
    # just GFM-style `| --- | --- |` pipe tables.
    text = (
        "+------+------+\n"
        "| A    | B    |\n"
        "+======+======+\n"
        "| val1 | val2 |\n"
        "+------+------+\n"
    )
    stats = compute_statistics(text)
    assert stats["table_count"] == 1


# ---------------------------------------------------------------------------
# normalized-source-document contract shape
# ---------------------------------------------------------------------------

def test_source_not_found_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        extract_and_normalize(tmp_path / "nope.docx", tmp_path / "analysis")


def test_extract_and_normalize_matches_normalized_source_document_contract(tmp_path):
    result = extract_and_normalize(SMALL_SINGLE, tmp_path / "analysis")
    from schema.normalized_source_document import validate

    validate(result)  # raises if required fields are missing
    assert len(result["source_content_sha256"]) == 64
