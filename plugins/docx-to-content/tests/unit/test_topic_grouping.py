"""
test_topic_grouping.py
=======================

Tests for scripts/topic_grouping.py — deterministic topic-boundary
computation for the "grouped" chunking strategy (Task 17-topic-grouping).
Every level-1 heading starts a new topic; every heading at level 2+ belongs
to the most recently seen level-1 topic.
"""

import pytest

from topic_grouping import UnassignableHeadingError, compute_topic_boundaries


def _heading(level, text, path, occurrence=1):
    return {"level": level, "text": text, "path": path, "occurrence": occurrence}


def test_every_heading_assigned_to_exactly_one_topic():
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


def test_top_level_headings_start_new_topics():
    headings = [
        _heading(1, "A", ["A"]),
        _heading(2, "A.1", ["A", "A.1"]),
        _heading(1, "B", ["B"]),
    ]
    boundaries = compute_topic_boundaries(headings)
    assert [b.title for b in boundaries] == ["A", "B"]
    assert [tuple(m.path) for m in boundaries[0].members] == [("A",), ("A", "A.1")]
    assert [tuple(m.path) for m in boundaries[1].members] == [("B",)]


def test_child_headings_stay_in_source_order_within_topic():
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


def test_topic_ids_deterministic_and_independent_of_position():
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


def test_duplicate_top_level_titles_get_distinct_topic_ids_via_occurrence():
    headings = [
        _heading(1, "Overview", ["Overview"], occurrence=1),
        _heading(1, "Overview", ["Overview"], occurrence=2),
    ]
    boundaries = compute_topic_boundaries(headings)
    assert boundaries[0].topic_id != boundaries[1].topic_id


def test_heading_below_top_level_before_any_top_level_heading_raises():
    headings = [_heading(2, "Orphan", ["Orphan"])]
    with pytest.raises(UnassignableHeadingError):
        compute_topic_boundaries(headings)
