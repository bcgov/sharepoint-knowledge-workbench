"""Purpose:
    Authoritative schema for the `analysis-plan` contract (the draft/ confirmed `ConversionPlan`).

Key Input Dependencies:
    - dataclasses
    - typing
    - plan_schema.shared

Authoritative schema for the `analysis-plan` contract (the draft/
confirmed `ConversionPlan`).

`document-structure-analysis` is the sole producer of this contract -- this module
is the single source of truth for its wire format, packaged inside this
plugin so the plugin installs and runs standalone. Ported from
`docx-to-content/scripts/contracts.py`'s `SourceFingerprint`/
`StructuralAnchor`/`Confirmation`/`ConversionPlan` dataclasses (Phase 4.5
Wave 3) -- see
docs/superpowers/plans/phase-4-5-evidence/wave-3-analysis-plan-split-decision.md.

`structured-content-assembly` (Wave 4, the confirmed-plan consumer) carries its own
plugin-local copy of the subset it needs, generated/synced from this file
-- never imported across the plugin boundary at runtime.

Key Functions Index:
    - SourceFingerprint.from_dict()
    - SourceFingerprint.to_dict()
    - StructuralAnchor.from_dict()
    - StructuralAnchor.to_dict()
    - Confirmation.from_dict()
    - Confirmation.to_dict()
    - ConversionPlan.from_dict()
    - ConversionPlan.to_dict()
    - validate()"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from plan_schema.shared import check_schema_version, require

CONVERSION_PLAN_SCHEMA_VERSION = "1.0"


@dataclass
class SourceFingerprint:
    path: str
    sha256: str
    size_bytes: int

    # Validate and construct a SourceFingerprint record from a mapping.
    @classmethod
    def from_dict(cls, data: dict) -> "SourceFingerprint":
        """Validate and construct a SourceFingerprint record from a mapping."""
        return cls(
            path=require(data, "path"),
            sha256=require(data, "sha256"),
            size_bytes=require(data, "size_bytes"),
        )

    # Serialize a SourceFingerprint record as a JSON-compatible mapping.
    def to_dict(self) -> dict:
        """Serialize a SourceFingerprint record as a JSON-compatible mapping."""
        return {"path": self.path, "sha256": self.sha256, "size_bytes": self.size_bytes}


@dataclass
class StructuralAnchor:
    stable_key: str
    heading_text: str
    heading_level: int
    occurrence: int
    source_heading_path: list

    # Validate and construct a StructuralAnchor record from a mapping.
    @classmethod
    def from_dict(cls, data: dict) -> "StructuralAnchor":
        """Validate and construct a StructuralAnchor record from a mapping."""
        return cls(
            stable_key=require(data, "stable_key"),
            heading_text=require(data, "heading_text"),
            heading_level=require(data, "heading_level"),
            occurrence=require(data, "occurrence"),
            source_heading_path=list(require(data, "source_heading_path")),
        )

    # Serialize a StructuralAnchor record as a JSON-compatible mapping.
    def to_dict(self) -> dict:
        """Serialize a StructuralAnchor record as a JSON-compatible mapping."""
        return {
            "stable_key": self.stable_key,
            "heading_text": self.heading_text,
            "heading_level": self.heading_level,
            "occurrence": self.occurrence,
            "source_heading_path": list(self.source_heading_path),
        }


@dataclass
class Confirmation:
    status: str  # "draft" | "confirmed"
    confirmed_by: str
    confirmed_at: str

    # Validate and construct a Confirmation record from a mapping.
    @classmethod
    def from_dict(cls, data: dict) -> "Confirmation":
        """Validate and construct a Confirmation record from a mapping."""
        return cls(
            status=require(data, "status"),
            confirmed_by=require(data, "confirmed_by"),
            confirmed_at=require(data, "confirmed_at"),
        )

    # Serialize a Confirmation record as a JSON-compatible mapping.
    def to_dict(self) -> dict:
        """Serialize a Confirmation record as a JSON-compatible mapping."""
        return {
            "status": self.status,
            "confirmed_by": self.confirmed_by,
            "confirmed_at": self.confirmed_at,
        }


@dataclass
class ConversionPlan:
    schema_version: str
    plan_id: str
    source: SourceFingerprint
    strategy: str
    chunk_level: int
    chunk_anchors: list  # list[StructuralAnchor]
    content_type: str
    template_profile: str
    confirmation: Confirmation
    analysis_warnings: list = field(default_factory=list)
    # Human-reviewable, confirmed topic-root set for the "grouped" strategy:
    # list of {"source_heading_path": [...], "occurrence": int} dicts
    # identifying which structural anchors are topic-root physical
    # boundaries. None for plans that never proposed/confirmed a root set.
    confirmed_topic_roots: Optional[list] = None
    # Human-reviewable, confirmed media-disposition records (general media
    # classification/disposition mechanism): list of dicts shaped like
    # `{"source_media_id", "source_position", "source_hash", "media_type",
    # "classification", "disposition", "canonical_inclusion",
    # "publication_inclusion", "derived_asset_allowed", "reason",
    # "decision_authority", "requires_alt_text"}`. None for plans that
    # never proposed any.
    media_decisions: Optional[list] = None

    # Validate and construct a ConversionPlan record from a mapping.
    @classmethod
    def from_dict(cls, data: dict) -> "ConversionPlan":
        """Validate and construct a ConversionPlan record from a mapping."""
        schema_version = check_schema_version(data, CONVERSION_PLAN_SCHEMA_VERSION, "ConversionPlan")
        return cls(
            schema_version=schema_version,
            plan_id=require(data, "plan_id"),
            source=SourceFingerprint.from_dict(require(data, "source")),
            strategy=require(data, "strategy"),
            chunk_level=require(data, "chunk_level"),
            chunk_anchors=[StructuralAnchor.from_dict(a) for a in require(data, "chunk_anchors")],
            content_type=require(data, "content_type"),
            template_profile=require(data, "template_profile"),
            confirmation=Confirmation.from_dict(require(data, "confirmation")),
            analysis_warnings=list(require(data, "analysis_warnings")),
            confirmed_topic_roots=data.get("confirmed_topic_roots"),
            media_decisions=data.get("media_decisions"),
        )

    # Serialize a ConversionPlan record as a JSON-compatible mapping.
    def to_dict(self) -> dict:
        """Serialize a ConversionPlan record as a JSON-compatible mapping."""
        result = {
            "schema_version": self.schema_version,
            "plan_id": self.plan_id,
            "source": self.source.to_dict(),
            "strategy": self.strategy,
            "chunk_level": self.chunk_level,
            "chunk_anchors": [a.to_dict() for a in self.chunk_anchors],
            "content_type": self.content_type,
            "template_profile": self.template_profile,
            "confirmation": self.confirmation.to_dict(),
            "analysis_warnings": list(self.analysis_warnings),
        }
        if self.confirmed_topic_roots is not None:
            result["confirmed_topic_roots"] = self.confirmed_topic_roots
        if self.media_decisions is not None:
            result["media_decisions"] = self.media_decisions
        return result


def validate(data: dict) -> None:
    """Validate a raw dict against the analysis-plan v1 wire format
    (round-trips through ConversionPlan.from_dict, which raises ValueError
    on any missing/mismatched required field)."""
    ConversionPlan.from_dict(data)
