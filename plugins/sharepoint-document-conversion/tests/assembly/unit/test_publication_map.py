"""test_publication_map.py
========================

Purpose:
    Tests for scripts/contracts.py's PublicationMap/PublicationMapEntry contract and scripts/assembly/publication_map.py's build/write/load functions (Task 17-topic-grouping, Task 4).

Key Input Dependencies:
    - pytest and the plugin-local tests in this namespace
    - json
    - pytest
    - canonical_schema
    - publication_map
    - topic_boundary_core

Tests for scripts/contracts.py's PublicationMap/PublicationMapEntry
contract and scripts/assembly/publication_map.py's build/write/load functions
(Task 17-topic-grouping, Task 4).

Key Functions Index:
    - _boundary()
    - test_publication_map_round_trips_through_json()
    - test_publication_map_order_is_explicit_not_positional()
    - test_publication_map_entry_omits_parent_topic_id()
    - test_load_publication_map_returns_none_when_absent()
    - test_load_publication_map_round_trips()
    - test_load_publication_map_raises_controlled_error_on_malformed_json()
    - test_load_publication_map_raises_controlled_error_on_missing_field()"""

import json

import pytest

from canonical_schema import publication_map as contracts
import publication_map
import topic_boundary_core as topic_grouping


# Build a topic-boundary fixture from member anchors and its title.
def _boundary(topic_id, title, member_paths):
    """Build a topic-boundary fixture from member anchors and its title."""
    members = [
        topic_grouping.TopicMember(level=1 if i == 0 else 2, text=p[-1], path=p, occurrence=1)
        for i, p in enumerate(member_paths)
    ]
    return topic_grouping.TopicBoundary(topic_id=topic_id, title=title, members=members)


# Verify publication map round trips through JSON.
def test_publication_map_round_trips_through_json():
    """Verify publication map round trips through JSON."""
    boundaries = [
        _boundary("file-access--aaaaaaaa", "File Access", [["File Access"]]),
        _boundary("overview--bbbbbbbb", "Overview", [["Overview"]]),
    ]
    chunk_ids = {
        "file-access--aaaaaaaa": "chunks/file-access--aaaaaaaa.md",
        "overview--bbbbbbbb": "chunks/overview--bbbbbbbb.md",
    }
    pub_map = publication_map.build_publication_map(
        boundaries, chunk_ids, package_identity="sha256:deadbeef"
    )
    as_dict = pub_map.to_dict()
    restored = contracts.PublicationMap.from_dict(as_dict)
    assert restored == pub_map


# Verify publication map order is explicit not positional.
def test_publication_map_order_is_explicit_not_positional(tmp_path):
    """Verify publication map order is explicit not positional."""
    boundaries = [
        _boundary("b--11111111", "B", [["B"]]),
        _boundary("a--22222222", "A", [["A"]]),
    ]
    chunk_ids = {"b--11111111": "chunks/b.md", "a--22222222": "chunks/a.md"}
    pub_map = publication_map.build_publication_map(
        boundaries, chunk_ids, package_identity="sha256:deadbeef"
    )
    orders = [entry.order for entry in pub_map.entries]
    assert orders == [0, 1]
    written = publication_map.write_publication_map(pub_map, tmp_path)
    on_disk = json.loads(written.read_text())
    assert [e["order"] for e in on_disk["entries"]] == [0, 1]


# Verify publication map entry omits parent topic ID.
def test_publication_map_entry_omits_parent_topic_id():
    """Verify publication map entry omits parent topic ID."""
    boundaries = [_boundary("a--11111111", "A", [["A"]])]
    chunk_ids = {"a--11111111": "chunks/a.md"}
    pub_map = publication_map.build_publication_map(
        boundaries, chunk_ids, package_identity="sha256:deadbeef"
    )
    # parent_topic_id removed from the contract; ensure it's not present in the serialized dict
    as_dict = pub_map.to_dict()
    assert "parent_topic_id" not in as_dict["entries"][0]


# Verify load publication map returns none when absent.
def test_load_publication_map_returns_none_when_absent(tmp_path):
    """Verify load publication map returns none when absent."""
    assert publication_map.load_publication_map(tmp_path) is None


# Verify load publication map round trips.
def test_load_publication_map_round_trips(tmp_path):
    """Verify load publication map round trips."""
    boundaries = [_boundary("a--11111111", "A", [["A"]])]
    chunk_ids = {"a--11111111": "chunks/a.md"}
    pub_map = publication_map.build_publication_map(
        boundaries, chunk_ids, package_identity="sha256:deadbeef"
    )
    publication_map.write_publication_map(pub_map, tmp_path)
    loaded = publication_map.load_publication_map(tmp_path)
    assert loaded == pub_map


# Verify load publication map raises controlled error on malformed JSON.
def test_load_publication_map_raises_controlled_error_on_malformed_json(tmp_path):
    """Verify load publication map raises controlled error on malformed JSON."""
    (tmp_path / "publication-map.json").write_text("{not valid json")

    with pytest.raises(publication_map.MalformedPublicationMapError):
        publication_map.load_publication_map(tmp_path)


# Verify load publication map raises controlled error on missing field.
def test_load_publication_map_raises_controlled_error_on_missing_field(tmp_path):
    """Verify load publication map raises controlled error on missing field."""
    (tmp_path / "publication-map.json").write_text(json.dumps({"schema_version": "1.0"}))

    with pytest.raises(publication_map.MalformedPublicationMapError):
        publication_map.load_publication_map(tmp_path)
