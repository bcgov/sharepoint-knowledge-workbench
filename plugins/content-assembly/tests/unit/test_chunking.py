"""
test_chunking.py
================

Tests for scripts/chunking.py (Task 8): reconciling a CONFIRMED plan's
`chunk_anchors` (computed during analysis, against RAW pandoc markdown)
against a CLEANED document's actual heading structure, then slicing the
cleaned markdown into per-chunk content using the reconciled positions.

Fixture heading names are synthetic placeholders (e.g. "Section Alpha",
"Widget Setup").
"""

import pytest

import identity_core as identity
from chunking import (
    AmbiguousAnchorError,
    MissingAnchorError,
    ReconciledAnchor,
    parse_headings_with_lines,
    reconcile_anchors,
    reconcile_and_slice,
)
from canonical_schema.analysis_plan import StructuralAnchor


def _anchor_from_heading(h: dict) -> StructuralAnchor:
    return StructuralAnchor(
        stable_key=identity.make_chunk_id(h["path"], h["occurrence"]),
        heading_text=h["text"],
        heading_level=h["level"],
        occurrence=h["occurrence"],
        source_heading_path=list(h["path"]),
    )


def _anchors_for(markdown_text: str) -> list:
    return [_anchor_from_heading(h) for h in parse_headings_with_lines(markdown_text)]


# ---------------------------------------------------------------------------
# Line numbers shift after cleanup, but path/occurrence-based anchors still
# resolve.
# ---------------------------------------------------------------------------

RAW_DOC = (
    "# Section Alpha\n"
    "Some raw noise line one.\n"
    "Some raw noise line two.\n"
    "## Widget Setup\n"
    "Body text for widget setup.\n"
    "# Section Beta\n"
    "Final body text.\n"
)

# Cleanup removed the two "raw noise" lines -- headings now sit on different
# line numbers than they did in the raw document.
CLEANED_DOC = (
    "# Section Alpha\n"
    "## Widget Setup\n"
    "Body text for widget setup.\n"
    "# Section Beta\n"
    "Final body text.\n"
)


def test_anchors_resolve_after_cleanup_shifts_line_numbers():
    anchors = _anchors_for(RAW_DOC)
    reconciled = reconcile_anchors(anchors, CLEANED_DOC)

    assert [r.line for r in reconciled] == [0, 1, 3]
    assert [r.anchor.heading_text for r in reconciled] == [
        "Section Alpha", "Widget Setup", "Section Beta",
    ]


def test_reconcile_and_slice_produces_contiguous_chunks():
    anchors = _anchors_for(RAW_DOC)
    sliced = reconcile_and_slice(anchors, CLEANED_DOC)

    assert len(sliced.chunks) == 3
    assert sliced.chunks[0].content == "# Section Alpha\n"
    assert sliced.chunks[1].content == (
        "## Widget Setup\nBody text for widget setup.\n"
    )
    assert sliced.chunks[2].content == "# Section Beta\nFinal body text.\n"


# ---------------------------------------------------------------------------
# Missing anchor: fails rather than silently truncating.
# ---------------------------------------------------------------------------

def test_missing_anchor_raises_rather_than_truncates():
    anchors = _anchors_for(RAW_DOC)
    # Cleaned doc lost "Widget Setup" entirely (simulating a cleanup defect
    # eating a heading) -- reconciliation must fail loudly, not skip it.
    broken_cleaned = (
        "# Section Alpha\n"
        "# Section Beta\n"
        "Final body text.\n"
    )
    with pytest.raises(MissingAnchorError):
        reconcile_anchors(anchors, broken_cleaned)


# ---------------------------------------------------------------------------
# Duplicate ambiguous anchor: two cleaned headings recompute to the same
# stable_key (identical normalized slug + identical occurrence, achieved
# here via a case-only difference that collapses under slugification while
# each heading's own exact-text occurrence counter independently starts at 1).
# ---------------------------------------------------------------------------

def test_duplicate_ambiguous_anchor_raises():
    raw = (
        "# Overview\n"
        "Body one.\n"
    )
    anchors = _anchors_for(raw)

    ambiguous_cleaned = (
        "# Overview\n"
        "Body one.\n"
        "# OVERVIEW\n"
        "Body two.\n"
    )
    with pytest.raises(AmbiguousAnchorError):
        reconcile_anchors(anchors, ambiguous_cleaned)


# ---------------------------------------------------------------------------
# Changed heading level: matching is path+occurrence based (via stable_key),
# not level based, so a heading whose markdown level shifted (## -> ###)
# still resolves -- level is informational on the anchor, not part of
# identity (identity.make_chunk_id never takes a level argument).
# ---------------------------------------------------------------------------

def test_changed_heading_level_still_resolves_by_path_and_occurrence():
    raw = (
        "# Section Alpha\n"
        "## Widget Setup\n"
        "Body text.\n"
    )
    anchors = _anchors_for(raw)

    # Cleanup (hypothetically) demoted "Widget Setup" from level 2 to level 3.
    level_shifted_cleaned = (
        "# Section Alpha\n"
        "### Widget Setup\n"
        "Body text.\n"
    )
    reconciled = reconcile_anchors(anchors, level_shifted_cleaned)
    assert len(reconciled) == 2
    assert reconciled[1].anchor.heading_text == "Widget Setup"
    assert reconciled[1].line == 1


# ---------------------------------------------------------------------------
# Repeated occurrence resolution: two anchors sharing an identical
# source_heading_path (occurrence=1 and occurrence=2) each match their own
# corresponding instance in the cleaned document, not both to the first.
# ---------------------------------------------------------------------------

def test_repeated_occurrence_anchors_match_distinct_instances():
    raw = (
        "# Section Alpha\n"
        "## Notes\n"
        "First notes body.\n"
        "## Notes\n"
        "Second notes body.\n"
    )
    anchors = _anchors_for(raw)
    notes_anchors = [a for a in anchors if a.heading_text == "Notes"]
    assert len(notes_anchors) == 2
    assert notes_anchors[0].occurrence == 1
    assert notes_anchors[1].occurrence == 2

    # Cleanup shifted line numbers (stripped a blank line) but did not
    # reorder or drop either "Notes" instance.
    cleaned = (
        "# Section Alpha\n"
        "## Notes\n"
        "First notes body.\n"
        "## Notes\n"
        "Second notes body.\n"
        "Trailing cleanup artifact removed above this line.\n"
    )
    reconciled = reconcile_anchors(anchors, cleaned)
    notes_reconciled = [r for r in reconciled if r.anchor.heading_text == "Notes"]
    assert notes_reconciled[0].line == 1
    assert notes_reconciled[1].line == 3
    assert notes_reconciled[0].line != notes_reconciled[1].line


# ---------------------------------------------------------------------------
# Aggregate content-loss/duplication guard: every non-preamble line in the
# cleaned document belongs to exactly one chunk once slices are concatenated
# back together (preamble -- content before the first heading -- is handled
# separately and excluded from this assertion, per the documented choice).
# ---------------------------------------------------------------------------

def test_all_cleaned_lines_reconstructed_with_no_loss_or_duplication():
    anchors = _anchors_for(RAW_DOC)
    sliced = reconcile_and_slice(anchors, CLEANED_DOC)

    reconstructed = sliced.preamble + "".join(c.content for c in sliced.chunks)
    assert reconstructed == CLEANED_DOC


def test_preamble_before_first_heading_is_excluded_from_chunks():
    raw = "# Section Alpha\nBody.\n"
    anchors = _anchors_for(raw)
    cleaned = "Some preamble line kept verbatim.\n# Section Alpha\nBody.\n"

    sliced = reconcile_and_slice(anchors, cleaned)
    assert sliced.preamble == "Some preamble line kept verbatim.\n"
    assert sliced.chunks[0].content == "# Section Alpha\nBody.\n"
    reconstructed = sliced.preamble + "".join(c.content for c in sliced.chunks)
    assert reconstructed == cleaned


# ---------------------------------------------------------------------------
# strategy: "single" -- chunk_anchors is populated identically regardless of
# plan.strategy (analyze_structure.analyze_document builds chunk_anchors
# from ALL parsed headings whether the recommendation is "single" or
# "chunked"), so reconciliation/slicing needs no special-cased branch for a
# single-strategy plan: it is uniformly "chunked with however many anchors
# happen to be recorded", including exactly one.
# ---------------------------------------------------------------------------

def test_single_anchor_plan_handled_uniformly_as_one_chunk():
    raw = "# Only Section\nAll content lives here.\n"
    anchors = _anchors_for(raw)
    assert len(anchors) == 1

    cleaned = "# Only Section\nAll content lives here.\n"
    sliced = reconcile_and_slice(anchors, cleaned)

    assert len(sliced.chunks) == 1
    assert sliced.chunks[0].content == cleaned
    assert sliced.preamble == ""


# ---------------------------------------------------------------------------
# Regression: analysis-time anchor identity must match convert-time
# reconciliation identity even when a heading's raw text is affected by a
# cleanup step that changes heading TEXT itself (not just trailing
# attribute syntax) -- e.g. pandoc.heading_emphasis's whole-heading
# bold/italic stripping. If analysis builds stable_key from the RAW
# (un-normalized) heading text while reconciliation recomputes stable_key
# from the CLEANED (normalized) text, the two will never match and
# reconciliation will raise MissingAnchorError for every affected heading.
# ---------------------------------------------------------------------------

def test_anchor_identity_survives_whole_heading_emphasis_normalization():
    from pandoc_cleanup.heading_emphasis import strip_whole_heading_emphasis

    raw = (
        "# **PROTECTION ORDERS**\n"
        "Intro body text.\n"
        "### **Data Capture Requirements**\n"
        "Body text.\n"
    )
    # Anchors as analysis-time code actually builds them: from RAW,
    # un-cleaned heading text.
    anchors = _anchors_for(raw)
    assert len(anchors) == 2

    # No raw "**" markers may survive into the anchor identity used for
    # reconciliation.
    for anchor in anchors:
        assert "**" not in anchor.stable_key
        assert all("**" not in part for part in anchor.source_heading_path)

    cleaned = strip_whole_heading_emphasis(raw)
    assert "**" not in cleaned  # sanity: cleanup actually stripped the markers

    reconciled = reconcile_anchors(anchors, cleaned)
    assert len(reconciled) == 2
    # Exactly one cleaned heading resolves per anchor -- no ambiguity, no
    # missing match.
    resolved_keys = {r.anchor.stable_key for r in reconciled}
    assert resolved_keys == {a.stable_key for a in anchors}

    sliced = reconcile_and_slice(anchors, cleaned)
    all_content = "".join(c.content for c in sliced.chunks)
    assert "**" not in all_content
    assert "PROTECTION ORDERS" in sliced.chunks[0].content
    assert "Data Capture Requirements" in all_content


# ---------------------------------------------------------------------------
# Regression (Task 18, discovered against a real pilot document): a heading
# with an image glued directly onto its own line has that image stripped by
# convert-time cleanup (pandoc.images.fix_glued_images) before
# reconciliation. Analysis-time identity must strip it too, the same way it
# already had to for whole-heading emphasis stripping above.
# ---------------------------------------------------------------------------

def test_anchor_identity_survives_glued_image_normalization():
    from pandoc_cleanup.images import fix_glued_images

    raw = (
        "# Locate A File\n"
        "Intro body text.\n"
        "### ![](media/image12.png){width=\"5in\"}**Central Divorce**\n"
        "Body text.\n"
    )
    anchors = _anchors_for(raw)
    assert len(anchors) == 2
    for anchor in anchors:
        assert "media/image12.png" not in anchor.stable_key
        assert all("media/image12.png" not in part for part in anchor.source_heading_path)

    cleaned = fix_glued_images(raw)
    reconciled = reconcile_anchors(anchors, cleaned)
    assert len(reconciled) == 2
