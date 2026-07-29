"""
publication_map.py
===================

Minimal publication-map contract writer/loader for the "grouped" chunking
strategy (Task 17-topic-grouping). `publication-map.json` references the
canonical package's own identity (not just a bare manifest hash), lists
canonical topic ids in explicit, directory-order-independent sequence, and
supports `parent_topic_id` for future hierarchy.
"""

import json
from pathlib import Path

import contracts

_FILENAME = "publication-map.json"


def build_publication_map(
    topic_boundaries: list,
    topic_chunk_ids: dict,
    package_identity: str,
    parent_topic_ids: dict = None,
) -> contracts.PublicationMap:
    parent_topic_ids = parent_topic_ids or {}
    entries = [
        contracts.PublicationMapEntry(
            topic_id=boundary.topic_id,
            title=boundary.title,
            order=index,
            chunk_id=topic_chunk_ids[boundary.topic_id],
            parent_topic_id=parent_topic_ids.get(boundary.topic_id),
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


def load_publication_map(package_dir):
    path = Path(package_dir) / _FILENAME
    if not path.exists():
        return None
    return contracts.PublicationMap.from_dict(json.loads(path.read_text()))
