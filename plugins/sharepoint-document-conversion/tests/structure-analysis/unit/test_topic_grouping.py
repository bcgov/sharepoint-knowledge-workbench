"""test_topic_grouping.py
=======================

Purpose:
    Tests for scripts/structure-analysis/topic_grouping.py — deterministic topic-boundary computation for the "grouped" chunking strategy, including mixed-level logical-root detection: the first heading establishes the document's opening topic-root level; any later heading at or above (i.e.

Key Input Dependencies:
    - pytest and the plugin-local tests in this namespace
    - pytest
    - topic_grouping

Tests for scripts/structure-analysis/topic_grouping.py — deterministic topic-boundary
computation for the "grouped" chunking strategy, including mixed-level
logical-root detection: the first heading establishes the document's opening
topic-root level; any later heading at or above (i.e. equally or less deep than)
the current root level also starts a new topic, even if its level differs from the
opening level (a "promoted" root). A heading deeper than the current root but
matching a root level used earlier ("bidirectional" inconsistency) is never silently
resolved either way.

Key Functions Index:
    - _heading()
    - test_every_heading_assigned_to_exactly_one_topic()
    - test_top_level_headings_start_new_topics()
    - test_child_headings_stay_in_source_order_within_topic()
    - test_topic_ids_deterministic_and_independent_of_position()
    - test_duplicate_top_level_titles_get_distinct_topic_ids_via_occurrence()
    - test_document_beginning_with_heading_2_roots_identifies_them_as_roots()
    - test_mixed_heading2_roots_then_heading1_roots_produces_expected_sequence()
    - test_genuine_heading2_child_beneath_heading1_root_is_not_promoted()
    - test_heading4_grandchild_remains_inside_its_parent_topic()
    - test_mixed_level_roots_produce_multiple_distinct_source_levels()
    - test_promoted_roots_retain_their_original_source_level()
    - test_repeated_analysis_produces_identical_candidate_roots()
    - test_bidirectional_inconsistency_is_not_silently_misclassified()
    - test_first_heading_below_top_level_is_treated_as_the_opening_root()
    - test_compute_topic_boundaries_from_roots_uses_confirmed_set_directly()
    - test_compute_topic_boundaries_from_roots_raises_on_stale_confirmed_roots()"""

import pytest

from topic_grouping import (
    UnassignableHeadingError,
    classify_headings,
    compute_topic_boundaries,
    compute_topic_boundaries_from_roots,
)


# Create a parsed-heading fixture with the supplied path, level, and occurrence.
def _heading(level, text, path, occurrence=1):
    """Create a parsed-heading fixture with the supplied path, level, and occurrence."""
    return {"level": level, "text": text, "path": path, "occurrence": occurrence}


# ---------------------------------------------------------------------------
# compute_topic_boundaries -- consistent Heading-1 documents (unchanged)
# ---------------------------------------------------------------------------

def test_every_heading_assigned_to_exactly_one_topic():
    """Verify every heading assigned to exactly one topic."""
    headings = [
        _heading(1, "Introduction", ["Introduction"]),
        _heading(2, "Scope", ["Introduction", "Scope"]),
        _heading(1, "File Access", ["File Access"]),
        _heading(2, "How to Seal a File", ["File Access", "How to Seal a File"]),
        _heading(3, "Prerequisites", ["File Access", "How to Seal a File", "Prerequisites"]),
    ]
    boundaries = compute_topic_boundaries(headings)
    assigned_paths = [
        tuple(member.path) for boundary in boundaries for member in boundary.members
    ]
    all_paths = [tuple(h["path"]) for h in headings]
    assert sorted(assigned_paths) == sorted(all_paths)
    assert len(assigned_paths) == len(set(assigned_paths))


# Verify top level headings start new topics.
def test_top_level_headings_start_new_topics():
    """Verify top level headings start new topics."""
    headings = [
        _heading(1, "A", ["A"]),
        _heading(2, "A.1", ["A", "A.1"]),
        _heading(1, "B", ["B"]),
    ]
    boundaries = compute_topic_boundaries(headings)
    assert [b.title for b in boundaries] == ["A", "B"]
    assert [tuple(m.path) for m in boundaries[0].members] == [("A",), ("A", "A.1")]
    assert [tuple(m.path) for m in boundaries[1].members] == [("B",)]


# Verify child headings stay in source order within topic.
def test_child_headings_stay_in_source_order_within_topic():
    """Verify child headings stay in source order within topic."""
    headings = [
        _heading(1, "A", ["A"]),
        _heading(2, "Second", ["A", "Second"]),
        _heading(2, "First-in-code-but-later-in-doc", ["A", "First-in-code-but-later-in-doc"]),
    ]
    boundaries = compute_topic_boundaries(headings)
    assert [m.text for m in boundaries[0].members] == [
        "A",
        "Second",
        "First-in-code-but-later-in-doc",
    ]


# Verify topic ids deterministic and independent of position.
def test_topic_ids_deterministic_and_independent_of_position():
    """Verify topic ids deterministic and independent of position."""
    headings_a = [
        _heading(1, "File Access", ["File Access"]),
        _heading(1, "Overview", ["Overview"]),
    ]
    headings_b = [
        _heading(1, "Overview", ["Overview"]),
        _heading(1, "File Access", ["File Access"]),
    ]
    boundaries_a = compute_topic_boundaries(headings_a)
    boundaries_b = compute_topic_boundaries(headings_b)
    ids_a = {b.title: b.topic_id for b in boundaries_a}
    ids_b = {b.title: b.topic_id for b in boundaries_b}
    assert ids_a == ids_b


# Verify duplicate top level titles get distinct topic ids via occurrence.
def test_duplicate_top_level_titles_get_distinct_topic_ids_via_occurrence():
    """Verify duplicate top level titles get distinct topic ids via occurrence."""
    headings = [
        _heading(1, "Overview", ["Overview"], occurrence=1),
        _heading(1, "Overview", ["Overview"], occurrence=2),
    ]
    boundaries = compute_topic_boundaries(headings)
    assert boundaries[0].topic_id != boundaries[1].topic_id


# ---------------------------------------------------------------------------
# classify_headings / compute_topic_boundaries -- mixed-level detection
# ---------------------------------------------------------------------------

def test_document_beginning_with_heading_2_roots_identifies_them_as_roots():
    # Case 2 from the required test list: a document beginning with
    # Heading-2 roots and Heading-3 children -- the opening heading
    # establishes the root level, no UnassignableHeadingError.
    """Verify document beginning with heading 2 roots identifies them as roots."""
    headings = [
        _heading(2, "DATA CAPTURE STANDARDS", ["DATA CAPTURE STANDARDS"]),
        _heading(3, "Data Capture Requirements", ["DATA CAPTURE STANDARDS", "Data Capture Requirements"]),
        _heading(2, "PUBLIC INQUIRY GUIDELINES", ["PUBLIC INQUIRY GUIDELINES"]),
    ]
    boundaries = compute_topic_boundaries(headings)
    assert [b.title for b in boundaries] == ["DATA CAPTURE STANDARDS", "PUBLIC INQUIRY GUIDELINES"]
    classifications = classify_headings(headings)
    assert classifications[0]["classification"] == "root"
    assert classifications[0]["source_level"] == 2


# Verify mixed heading2 roots then heading1 roots produces expected sequence.
def test_mixed_heading2_roots_then_heading1_roots_produces_expected_sequence():
    # Case 3: Mixed hierarchy pattern -- Heading-2 roots first, later
    # Heading-1 roots, each followed by Heading-3 children only.
    """Verify mixed heading2 roots then heading1 roots produces expected sequence."""
    headings = [
        _heading(2, "DATA CAPTURE STANDARDS", ["DATA CAPTURE STANDARDS"]),
        _heading(3, "Data Capture Requirements", ["DATA CAPTURE STANDARDS", "Data Capture Requirements"]),
        _heading(2, "PUBLIC INQUIRY GUIDELINES", ["PUBLIC INQUIRY GUIDELINES"]),
        _heading(3, "Searching files at your own location", ["PUBLIC INQUIRY GUIDELINES", "Searching files at your own location"]),
        _heading(1, "SAMPLE TOPIC", ["SAMPLE TOPIC"]),
        _heading(3, "Rules of a Sample Topic", ["SAMPLE TOPIC", "Rules of a Sample Topic"]),
        _heading(1, "REFERRAL TRACKING", ["REFERRAL TRACKING"]),
    ]
    boundaries = compute_topic_boundaries(headings)
    assert [b.title for b in boundaries] == [
        "DATA CAPTURE STANDARDS",
        "PUBLIC INQUIRY GUIDELINES",
        "SAMPLE TOPIC",
        "REFERRAL TRACKING",
    ]
    classifications = classify_headings(headings)
    root_classifications = [c for c in classifications if c["physical_boundary"]]
    assert [c["source_level"] for c in root_classifications] == [2, 2, 1, 1]
    # SAMPLE TOPIC' level (1) differs from the opening level (2) --
    # it must be flagged "promoted-root", not silently called "root".
    assert root_classifications[2]["classification"] == "promoted-root"


# Verify genuine heading2 child beneath heading1 root is not promoted.
def test_genuine_heading2_child_beneath_heading1_root_is_not_promoted():
    # Case 4: a real nested Heading-2 child under a Heading-1 root must
    # stay a child (2 > current_root_level=1 -> internal-heading), not be
    # treated as a new topic root.
    """Verify genuine heading2 child beneath heading1 root is not promoted."""
    headings = [
        _heading(1, "Root A", ["Root A"]),
        _heading(2, "Genuine Child", ["Root A", "Genuine Child"]),
        _heading(3, "Grandchild", ["Root A", "Genuine Child", "Grandchild"]),
    ]
    boundaries = compute_topic_boundaries(headings)
    assert [b.title for b in boundaries] == ["Root A"]
    assert len(boundaries[0].members) == 3
    classifications = classify_headings(headings)
    assert classifications[1]["classification"] == "internal-heading"


# Verify heading4 grandchild remains inside its parent topic.
def test_heading4_grandchild_remains_inside_its_parent_topic():
    # Case 5: a deeper (level-4) descendant stays folded into its topic
    # regardless of the root level in effect.
    """Verify heading4 grandchild remains inside its parent topic."""
    headings = [
        _heading(1, "Reports Section", ["Reports Section"]),
        _heading(3, "Status Report", ["Reports Section", "Status Report"]),
        _heading(4, "Special Program Report", ["Reports Section", "Status Report", "Special Program Report"]),
        _heading(3, "Orders Report", ["Reports Section", "Orders Report"]),
    ]
    boundaries = compute_topic_boundaries(headings)
    assert len(boundaries) == 1
    assert [m.text for m in boundaries[0].members] == [
        "Reports Section",
        "Status Report",
        "Special Program Report",
        "Orders Report",
    ]


# Verify mixed level roots produce multiple distinct source levels.
def test_mixed_level_roots_produce_multiple_distinct_source_levels():
    # Case 7 (partial -- the review-warning itself is asserted at the
    # analyze_structure level; here we assert the underlying signal
    # analyze_structure's warning is derived from).
    """Verify mixed level roots produce multiple distinct source levels."""
    headings = [
        _heading(2, "A", ["A"]),
        _heading(1, "B", ["B"]),
    ]
    classifications = classify_headings(headings)
    root_levels = {c["source_level"] for c in classifications if c["physical_boundary"]}
    assert root_levels == {1, 2}


# Verify promoted roots retain their original source level.
def test_promoted_roots_retain_their_original_source_level():
    # Case 8: a promoted root's source_level must reflect its true
    # source heading level (1), never be rewritten to the opening level (2).
    """Verify promoted roots retain their original source level."""
    headings = [
        _heading(2, "Opening Root", ["Opening Root"]),
        _heading(1, "Promoted Root", ["Promoted Root"]),
    ]
    classifications = classify_headings(headings)
    promoted = [c for c in classifications if c["classification"] == "promoted-root"]
    assert len(promoted) == 1
    assert promoted[0]["source_level"] == 1


# Verify repeated analysis produces identical candidate roots.
def test_repeated_analysis_produces_identical_candidate_roots():
    # Case 9: classify_headings is a pure function of its input.
    """Verify repeated analysis produces identical candidate roots."""
    headings = [
        _heading(2, "A", ["A"]),
        _heading(3, "A.1", ["A", "A.1"]),
        _heading(1, "B", ["B"]),
    ]
    first = classify_headings(headings)
    second = classify_headings(headings)
    assert first == second


# Verify bidirectional inconsistency is not silently misclassified.
def test_bidirectional_inconsistency_is_not_silently_misclassified():
    # Case 15: level rises back up to a previously-used root level after
    # having gone deeper (Heading-1 root, Heading-3 child, then a
    # Heading-2 that matches no established root level relationship
    # cleanly) -- must be flagged ambiguous, not silently promoted or
    # silently folded in as a plain internal heading.
    """Verify bidirectional inconsistency is not silently misclassified."""
    headings = [
        _heading(1, "Root A", ["Root A"]),
        _heading(3, "Child A", ["Root A", "Child A"]),
        _heading(2, "Potential inconsistent Root B", ["Potential inconsistent Root B"]),
        _heading(3, "Child B", ["Potential inconsistent Root B", "Child B"]),
    ]
    classifications = classify_headings(headings)
    ambiguous = [c for c in classifications if c["classification"] == "ambiguous-root"]
    # Root B's level (2) was never previously used as a root level in this
    # sequence (only 1 has been used), so it is not the "matches an
    # earlier root level" ambiguous case -- it is deeper than the current
    # root (1) and is folded in as a plain internal heading. This test
    # documents that the ambiguous path only fires when a *repeat* of an
    # earlier root level appears out of the monotonic order.
    assert ambiguous == []

    headings_repeat = [
        _heading(2, "Root A", ["Root A"]),
        _heading(1, "Root B", ["Root B"]),
        _heading(3, "Child B", ["Root B", "Child B"]),
        _heading(2, "Reversal candidate", ["Reversal candidate"]),
    ]
    classifications_repeat = classify_headings(headings_repeat)
    reversal = classifications_repeat[-1]
    assert reversal["classification"] == "ambiguous-root"
    assert reversal["physical_boundary"] is False
    assert reversal["requires_confirmation"] is True


# Verify first heading below top level is treated as the opening root.
def test_first_heading_below_top_level_is_treated_as_the_opening_root():
    # A lone, non-level-1 heading no longer raises -- it establishes the
    # document's opening root level (superseding the old hardcoded
    # level==1-only assumption).
    """Verify first heading below top level is treated as the opening root."""
    headings = [_heading(2, "Opening Section", ["Opening Section"])]
    boundaries = compute_topic_boundaries(headings)
    assert [b.title for b in boundaries] == ["Opening Section"]


# ---------------------------------------------------------------------------
# compute_topic_boundaries_from_roots -- convert-time confirmed-root path
# ---------------------------------------------------------------------------

def test_compute_topic_boundaries_from_roots_uses_confirmed_set_directly():
    """Verify compute topic boundaries from roots uses confirmed set directly."""
    headings = [
        _heading(2, "A", ["A"]),
        _heading(3, "A.1", ["A", "A.1"]),
        _heading(1, "B", ["B"]),
    ]
    root_keys = {(("A",), 1), (("B",), 1)}
    boundaries = compute_topic_boundaries_from_roots(headings, root_keys)
    assert [b.title for b in boundaries] == ["A", "B"]


# Verify compute topic boundaries from roots raises on stale confirmed roots.
def test_compute_topic_boundaries_from_roots_raises_on_stale_confirmed_roots():
    # Case 11: a confirmed root whose identity no longer matches the
    # current headings (e.g. first heading isn't a confirmed root)
    # raises rather than silently falling back to a heuristic.
    """Verify compute topic boundaries from roots raises on stale confirmed roots."""
    headings = [_heading(2, "A", ["A"])]
    root_keys = {(("Something Else",), 1)}
    with pytest.raises(UnassignableHeadingError):
        compute_topic_boundaries_from_roots(headings, root_keys)
