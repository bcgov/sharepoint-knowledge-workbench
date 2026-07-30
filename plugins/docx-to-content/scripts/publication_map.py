"""
publication_map.py
===================

Minimal publication-map contract writer/loader for the "grouped" chunking
strategy (Task 17-topic-grouping). `publication-map.json` references the
canonical package's own identity (not just a bare manifest hash), lists
canonical topic ids in explicit, directory-order-independent sequence.
It no longer includes `parent_topic_id` (removed in Task 4).
"""

import json
from pathlib import Path

import contracts

_FILENAME = "publication-map.json"


def build_publication_map(
    topic_boundaries: list,
    topic_chunk_ids: dict,
    package_identity: str,
) -> contracts.PublicationMap:
    entries = [
        contracts.PublicationMapEntry(
            topic_id=boundary.topic_id,
            title=boundary.title,
            order=index,
            chunk_id=topic_chunk_ids[boundary.topic_id],
        )
        for index, boundary in enumerate(topic_boundaries)
    ]
    return contracts.PublicationMap(
        schema_version=contracts.PUBLICATION_MAP_SCHEMA_VERSION,
        package_identity=package_identity,
        entries=entries,
    )


def write_publication_map(pub_map: contracts.PublicationMap, output_dir) -> Path:
    output_path = Path(output_dir) / _FILENAME
    output_path.write_text(json.dumps(pub_map.to_dict(), indent=2, sort_keys=True))
    return output_path


class MalformedPublicationMapError(Exception):
    """publication-map.json exists but is malformed JSON, missing a
    required field, or an unsupported schema version -- raised as a
    controlled exception so callers (validate_canonical.py) can report it
    as a ValidationIssue instead of letting a raw json/ValueError escape."""


def load_publication_map(package_dir):
    path = Path(package_dir) / _FILENAME
    if not path.exists():
        return None
    try:
        raw = json.loads(path.read_text())
        return contracts.PublicationMap.from_dict(raw)
    except (json.JSONDecodeError, ValueError) as exc:
        raise MalformedPublicationMapError(
            f"{path} is malformed: {exc}"
        ) from exc
