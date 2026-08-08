"""
id_mapping.py
===============

Purpose:
    The reusable core of a two-pass content-migration technique: lookup
    columns cannot be populated during a first content-migration pass
    because the destination item IDs they need to reference don't exist
    yet. Instead, the first pass records a source-ID -> destination-ID
    mapping (plus, per lookup field, the raw source IDs it referenced) as
    it migrates each item; a second pass reads that mapping back to
    resolve those source IDs into real destination IDs once the target
    list has been fully migrated.

    Pure functions over a caller-supplied mapping dict -- no file or tenant
    I/O is performed here. The caller owns persistence (write the mapping
    to disk/a database/wherever between passes) and owns fetching the
    lookup source IDs to resolve; this module only does the bookkeeping
    and translation logic itself.

    Mapping shape: ``{list_name: {str(source_id): {"dest_id": int,
    "lookups": {field_name: [source_id, ...]}}}}``.

Layer: sharepoint-content-migration / ID-mapping mechanism

Key Input Dependencies:
    - none (standard library only)
"""

from __future__ import annotations

from typing import Mapping, Sequence


def record_id_mapping(
    mapping: Mapping[str, Mapping[str, dict]],
    *,
    list_name: str,
    source_id: int,
    dest_id: int,
    lookups: Mapping[str, Sequence[int]] | None = None,
) -> dict[str, dict[str, dict]]:
    """Return a NEW mapping with one entry recorded (or overwritten, if
    ``source_id`` was already recorded for ``list_name``). Never mutates
    ``mapping`` -- the caller decides when/whether to persist the result."""
    updated = {name: {sid: dict(entry) for sid, entry in entries.items()} for name, entries in mapping.items()}
    list_entries = dict(updated.get(list_name, {}))
    list_entries[str(source_id)] = {
        "dest_id": dest_id,
        "lookups": {field: list(ids) for field, ids in (lookups or {}).items()},
    }
    updated[list_name] = list_entries
    return updated


def resolve_lookup_ids(
    mapping: Mapping[str, Mapping[str, dict]], *, target_list: str, source_ids: Sequence[int]
) -> list[int]:
    """Resolve a list of source-side lookup IDs (all pointing at
    ``target_list``) to their destination IDs, in the same order as
    ``source_ids``. A source ID with no recorded mapping entry (its own
    item was never migrated, or has not been migrated yet) is silently
    skipped rather than raising -- matches the two-pass technique's own
    "skip unmatched, don't fail the whole batch" behaviour; a caller that
    needs to know about skipped IDs should diff its input against this
    function's output length."""
    target_entries = mapping.get(target_list, {})
    resolved: list[int] = []
    for source_id in source_ids:
        entry = target_entries.get(str(source_id))
        if entry is not None:
            resolved.append(entry["dest_id"])
    return resolved
