"""publication_map.py
===================

Purpose:
    Minimal publication-map contract writer/loader for the "grouped" chunking strategy (Task 17-topic-grouping).

Key Input Dependencies:
    - json
    - pathlib
    - canonical_schema

Minimal publication-map contract writer/loader for the "grouped" chunking
strategy (Task 17-topic-grouping). `publication-map.json` references the
canonical package's own identity (not just a bare manifest hash), lists
canonical topic ids in explicit, directory-order-independent sequence.
It no longer includes `parent_topic_id` (removed in Task 4).

Key Functions Index:
    - build_publication_map()
    - write_publication_map()
    - load_publication_map()"""

import json
from pathlib import Path

from canonical_schema import publication_map as contracts

_FILENAME = "publication-map.json"


# Build an ordered publication map that binds grouped package topics to their canonical chunk IDs.
def build_publication_map(
    topic_boundaries: list,
    topic_chunk_ids: dict,
    package_identity: str,
) -> contracts.PublicationMap:
    """Build an ordered publication map that binds grouped package topics to their canonical chunk IDs."""
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


# Serialize the publication map to publication-map.json in the package directory.
def write_publication_map(pub_map: contracts.PublicationMap, output_dir) -> Path:
    """Serialize the publication map to publication-map.json in the package directory."""
    output_path = Path(output_dir) / _FILENAME
    output_path.write_text(json.dumps(pub_map.to_dict(), indent=2, sort_keys=True))
    return output_path


class MalformedPublicationMapError(Exception):
    """publication-map.json exists but is malformed JSON, missing a
    required field, or an unsupported schema version -- raised as a
    controlled exception so callers (validate_canonical.py) can report it
    as a ValidationIssue instead of letting a raw json/ValueError escape."""


# Load publication-map.json, validate its schema and entries, or return None when the file is absent.
def load_publication_map(package_dir):
    """Load publication-map.json, validate its schema and entries, or return None when the file is absent."""
    path = Path(package_dir) / _FILENAME
    if not path.exists():
        return None
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        return contracts.PublicationMap.from_dict(raw)
    except (json.JSONDecodeError, ValueError) as exc:
        raise MalformedPublicationMapError(
            f"{path} is malformed: {exc}"
        ) from exc

