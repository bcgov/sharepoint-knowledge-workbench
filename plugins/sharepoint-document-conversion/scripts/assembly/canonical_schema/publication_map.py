"""Purpose:
    Authoritative schema for the `publication-map` contract: minimal publication order for the "grouped" chunking strategy.

Key Input Dependencies:
    - dataclasses
    - canonical_schema.shared

Authoritative schema for the `publication-map` contract: minimal
publication order for the "grouped" chunking strategy.

`structured-content-assembly` is the sole producer of this contract.

Key Functions Index:
    - PublicationMapEntry.from_dict()
    - PublicationMapEntry.to_dict()
    - PublicationMap.from_dict()
    - PublicationMap.to_dict()
    - validate()"""
from __future__ import annotations

from dataclasses import dataclass

from canonical_schema.shared import check_schema_version, require

PUBLICATION_MAP_SCHEMA_VERSION = "1.0"


@dataclass
class PublicationMapEntry:
    topic_id: str
    title: str
    order: int
    chunk_id: str

    # Validate and construct a PublicationMapEntry record from a mapping.
    @classmethod
    def from_dict(cls, data: dict) -> "PublicationMapEntry":
        """Validate and construct a PublicationMapEntry record from a mapping."""
        return cls(
            topic_id=require(data, "topic_id"),
            title=require(data, "title"),
            order=require(data, "order"),
            chunk_id=require(data, "chunk_id"),
        )

    # Serialize a PublicationMapEntry record as a JSON-compatible mapping.
    def to_dict(self) -> dict:
        """Serialize a PublicationMapEntry record as a JSON-compatible mapping."""
        return {
            "topic_id": self.topic_id,
            "title": self.title,
            "order": self.order,
            "chunk_id": self.chunk_id,
        }


@dataclass
class PublicationMap:
    schema_version: str
    package_identity: str
    entries: list  # list[PublicationMapEntry]

    # Validate and construct a PublicationMap record from a mapping.
    @classmethod
    def from_dict(cls, data: dict) -> "PublicationMap":
        """Validate and construct a PublicationMap record from a mapping."""
        schema_version = check_schema_version(data, PUBLICATION_MAP_SCHEMA_VERSION, "PublicationMap")
        return cls(
            schema_version=schema_version,
            package_identity=require(data, "package_identity"),
            entries=[PublicationMapEntry.from_dict(e) for e in require(data, "entries")],
        )

    # Serialize a PublicationMap record as a JSON-compatible mapping.
    def to_dict(self) -> dict:
        """Serialize a PublicationMap record as a JSON-compatible mapping."""
        return {
            "schema_version": self.schema_version,
            "package_identity": self.package_identity,
            "entries": [e.to_dict() for e in self.entries],
        }


def validate(data: dict) -> None:
    """Validate a raw dict against the publication-map v1 shape."""
    PublicationMap.from_dict(data)
