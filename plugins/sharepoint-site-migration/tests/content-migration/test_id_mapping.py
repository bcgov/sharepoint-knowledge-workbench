"""Tests for id_mapping.py -- the reusable core of the two-pass lookup
re-link content-migration technique: record a source-ID -> destination-ID
mapping (plus per-lookup-field source-ID lists) during a content-migration
pass, then resolve those source IDs to destination IDs in a second pass
once all target lists have been migrated. Pure functions over a
caller-supplied mapping dict -- no file or tenant I/O baked in here."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts" / "content-migration"))

from id_mapping import record_id_mapping, resolve_lookup_ids


class TestRecordIdMapping:
    def test_records_a_new_entry(self):
        mapping = record_id_mapping({}, list_name="Authors", source_id=10320, dest_id=201)
        assert mapping == {"Authors": {"10320": {"dest_id": 201, "lookups": {}}}}

    def test_records_lookup_field_source_ids(self):
        mapping = record_id_mapping(
            {}, list_name="Authors", source_id=10320, dest_id=201,
            lookups={"RelatedAuthors": [10322, 14647]},
        )
        assert mapping["Authors"]["10320"]["lookups"] == {"RelatedAuthors": [10322, 14647]}

    def test_does_not_mutate_the_input_mapping(self):
        original = {}
        record_id_mapping(original, list_name="Authors", source_id=1, dest_id=2)
        assert original == {}

    def test_accumulates_across_multiple_calls_for_the_same_list(self):
        mapping = record_id_mapping({}, list_name="Authors", source_id=1, dest_id=101)
        mapping = record_id_mapping(mapping, list_name="Authors", source_id=2, dest_id=102)
        assert set(mapping["Authors"].keys()) == {"1", "2"}

    def test_re_recording_the_same_source_id_overwrites_not_duplicates(self):
        mapping = record_id_mapping({}, list_name="Authors", source_id=1, dest_id=101)
        mapping = record_id_mapping(mapping, list_name="Authors", source_id=1, dest_id=999)
        assert mapping["Authors"]["1"]["dest_id"] == 999


class TestResolveLookupIds:
    def test_resolves_known_source_ids_to_dest_ids(self):
        mapping = {"Authors": {"10322": {"dest_id": 55, "lookups": {}}, "14647": {"dest_id": 56, "lookups": {}}}}
        result = resolve_lookup_ids(mapping, target_list="Authors", source_ids=[10322, 14647])
        assert result == [55, 56]

    def test_unknown_target_list_returns_empty(self):
        result = resolve_lookup_ids({}, target_list="Authors", source_ids=[1])
        assert result == []

    def test_unresolvable_source_id_is_skipped_not_erroring(self):
        """A source ID with no mapping entry (e.g. a Known Associates row that
        was itself never migrated) is quarantined by omission, not a crash --
        matches the source technique's 'skip unmatched, don't fail the batch'
        behaviour."""
        mapping = {"Authors": {"10322": {"dest_id": 55, "lookups": {}}}}
        result = resolve_lookup_ids(mapping, target_list="Authors", source_ids=[10322, 99999])
        assert result == [55]

    def test_preserves_input_order(self):
        mapping = {"Authors": {"1": {"dest_id": 10, "lookups": {}}, "2": {"dest_id": 20, "lookups": {}}}}
        result = resolve_lookup_ids(mapping, target_list="Authors", source_ids=[2, 1])
        assert result == [20, 10]
