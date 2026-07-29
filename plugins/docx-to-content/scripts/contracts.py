"""
contracts.py
============

Versioned data contracts shared across the docx-to-content plugin's
analyze/convert/render pipeline. These are plain stdlib dataclasses (no
pydantic/third-party validation deps) with strict `from_dict`/`to_dict`
round-tripping, matching the JSON shapes in
docs/superpowers/specs/2026-07-25-docx-to-content-plugin-design-v3-ammendments.md
sections 6 (Package Contracts) and 8 (Renderer Protocol).

Design rules enforced here:
- Every `from_dict` rejects a dict missing any required field (no silent
  defaulting) via `_require`.
- Every contract that carries a `schema_version` field rejects a
  missing/unsupported version via `_check_schema_version`.
- `to_dict` always returns plain dicts/lists/str/int/None — safe to pass
  straight into `hashing.canonical_json_bytes`.
"""

from dataclasses import dataclass, field
from typing import Any, Optional


SUPPORTED_SCHEMA_VERSION = "1.0"


def _require(data: dict, field_name: str) -> Any:
    if field_name not in data:
        raise ValueError(f"missing required field: {field_name!r}")
    return data[field_name]


def _check_schema_version(data: dict) -> str:
    version = _require(data, "schema_version")
    if version != SUPPORTED_SCHEMA_VERSION:
        raise ValueError(
            f"unsupported schema_version: {version!r} "
            f"(supported: {SUPPORTED_SCHEMA_VERSION!r})"
        )
    return version


# ---------------------------------------------------------------------------
# Shared nested types
# ---------------------------------------------------------------------------

@dataclass
class SourceFingerprint:
    path: str
    sha256: str
    size_bytes: int

    @classmethod
    def from_dict(cls, data: dict) -> "SourceFingerprint":
        return cls(
            path=_require(data, "path"),
            sha256=_require(data, "sha256"),
            size_bytes=_require(data, "size_bytes"),
        )

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "sha256": self.sha256,
            "size_bytes": self.size_bytes,
        }


@dataclass
class ManifestSourceFingerprint:
    """Manifest's `source` block (Section 6.4) omits `size_bytes`."""

    path: str
    sha256: str

    @classmethod
    def from_dict(cls, data: dict) -> "ManifestSourceFingerprint":
        return cls(path=_require(data, "path"), sha256=_require(data, "sha256"))

    def to_dict(self) -> dict:
        return {"path": self.path, "sha256": self.sha256}


@dataclass
class StructuralAnchor:
    stable_key: str
    heading_text: str
    heading_level: int
    occurrence: int
    source_heading_path: list

    @classmethod
    def from_dict(cls, data: dict) -> "StructuralAnchor":
        return cls(
            stable_key=_require(data, "stable_key"),
            heading_text=_require(data, "heading_text"),
            heading_level=_require(data, "heading_level"),
            occurrence=_require(data, "occurrence"),
            source_heading_path=list(_require(data, "source_heading_path")),
        )

    def to_dict(self) -> dict:
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

    @classmethod
    def from_dict(cls, data: dict) -> "Confirmation":
        return cls(
            status=_require(data, "status"),
            confirmed_by=_require(data, "confirmed_by"),
            confirmed_at=_require(data, "confirmed_at"),
        )

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "confirmed_by": self.confirmed_by,
            "confirmed_at": self.confirmed_at,
        }


# ---------------------------------------------------------------------------
# Section 6.2 — ConversionPlan
# ---------------------------------------------------------------------------

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
    # Human-reviewable, confirmed topic-root set for the "grouped" strategy
    # (Task 18 mixed-level logical-root detection): list of
    # {"source_heading_path": [...], "occurrence": int} dicts identifying
    # which structural anchors are topic-root physical boundaries. None
    # for plans that never proposed/confirmed a root set (ungrouped
    # strategies, or older plans predating this field) -- convert falls
    # back to recomputing the default heuristic in that case. When
    # present, convert MUST consume this set as-is rather than
    # independently re-deriving root classification from heading levels.
    confirmed_topic_roots: Optional[list] = None
    # Human-reviewable, confirmed media-disposition records (general media
    # classification/disposition mechanism, Task 18): list of dicts shaped
    # like `{"source_media_id", "source_position", "source_hash",
    # "media_type", "classification", "disposition", "canonical_inclusion",
    # "publication_inclusion", "derived_asset_allowed", "reason",
    # "decision_authority", "requires_alt_text"}` -- see
    # scripts/media_disposition.py for the classification/disposition
    # vocabularies and `plans.apply_media_decision` for how a proposed
    # ("requires-human-review") record becomes a confirmed one before
    # `confirm_plan`. None for plans that never proposed any (e.g. a
    # document with no preamble media, or a plan predating this field).
    media_decisions: Optional[list] = None

    @classmethod
    def from_dict(cls, data: dict) -> "ConversionPlan":
        schema_version = _check_schema_version(data)
        return cls(
            schema_version=schema_version,
            plan_id=_require(data, "plan_id"),
            source=SourceFingerprint.from_dict(_require(data, "source")),
            strategy=_require(data, "strategy"),
            chunk_level=_require(data, "chunk_level"),
            chunk_anchors=[
                StructuralAnchor.from_dict(a) for a in _require(data, "chunk_anchors")
            ],
            content_type=_require(data, "content_type"),
            template_profile=_require(data, "template_profile"),
            confirmation=Confirmation.from_dict(_require(data, "confirmation")),
            analysis_warnings=list(_require(data, "analysis_warnings")),
            confirmed_topic_roots=data.get("confirmed_topic_roots"),
            media_decisions=data.get("media_decisions"),
        )

    def to_dict(self) -> dict:
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


# ---------------------------------------------------------------------------
# Section 6.5 — ChunkMetadata
# ---------------------------------------------------------------------------

@dataclass
class ChunkMetadata:
    schema_version: str
    chunk_id: str
    source_order: int
    source_heading_path: list
    topic: str
    content_type: str
    template_profile: str
    source_sha256: str
    plan_id: str
    content_file: str
    content_sha256: str
    local_links: list = field(default_factory=list)
    media_refs: list = field(default_factory=list)
    # Structural-anchor lineage folded into this chunk (Task 17-topic-
    # grouping's "grouped" strategy only): list of {"stable_key",
    # "source_heading_path", "occurrence", "heading_level"} dicts, one per
    # structural anchor this topic chunk contains, in source order. None
    # for ungrouped ("single"/"chunked") chunks, which map 1:1 to a
    # single structural anchor already identified by chunk_id.
    anchors: Optional[list] = None

    @classmethod
    def from_dict(cls, data: dict) -> "ChunkMetadata":
        schema_version = _check_schema_version(data)
        return cls(
            schema_version=schema_version,
            chunk_id=_require(data, "chunk_id"),
            source_order=_require(data, "source_order"),
            source_heading_path=list(_require(data, "source_heading_path")),
            topic=_require(data, "topic"),
            content_type=_require(data, "content_type"),
            template_profile=_require(data, "template_profile"),
            source_sha256=_require(data, "source_sha256"),
            plan_id=_require(data, "plan_id"),
            content_file=_require(data, "content_file"),
            content_sha256=_require(data, "content_sha256"),
            local_links=list(_require(data, "local_links")),
            media_refs=list(_require(data, "media_refs")),
            anchors=data.get("anchors"),
        )

    def to_dict(self) -> dict:
        result = {
            "schema_version": self.schema_version,
            "chunk_id": self.chunk_id,
            "source_order": self.source_order,
            "source_heading_path": list(self.source_heading_path),
            "topic": self.topic,
            "content_type": self.content_type,
            "template_profile": self.template_profile,
            "source_sha256": self.source_sha256,
            "plan_id": self.plan_id,
            "content_file": self.content_file,
            "content_sha256": self.content_sha256,
            "local_links": list(self.local_links),
            "media_refs": list(self.media_refs),
        }
        if self.anchors is not None:
            result["anchors"] = self.anchors
        return result


# ---------------------------------------------------------------------------
# Section 6.4 — Manifest / ManifestChunk
# ---------------------------------------------------------------------------

@dataclass
class ManifestChunk:
    chunk_id: str
    content_file: str
    metadata_file: str
    source_order: int
    source_heading_path: list

    @classmethod
    def from_dict(cls, data: dict) -> "ManifestChunk":
        return cls(
            chunk_id=_require(data, "chunk_id"),
            content_file=_require(data, "content_file"),
            metadata_file=_require(data, "metadata_file"),
            source_order=_require(data, "source_order"),
            source_heading_path=list(_require(data, "source_heading_path")),
        )

    def to_dict(self) -> dict:
        return {
            "chunk_id": self.chunk_id,
            "content_file": self.content_file,
            "metadata_file": self.metadata_file,
            "source_order": self.source_order,
            "source_heading_path": list(self.source_heading_path),
        }


@dataclass
class ManifestGenerator:
    plugin: str
    plugin_version: str

    @classmethod
    def from_dict(cls, data: dict) -> "ManifestGenerator":
        return cls(
            plugin=_require(data, "plugin"),
            plugin_version=_require(data, "plugin_version"),
        )

    def to_dict(self) -> dict:
        return {"plugin": self.plugin, "plugin_version": self.plugin_version}


@dataclass
class Manifest:
    schema_version: str
    generator: ManifestGenerator
    source: ManifestSourceFingerprint
    plan_id: str
    content_type: str
    template_profile: str
    strategy: str
    chunk_count: int
    chunks: list  # list[ManifestChunk]
    media: list
    validation_report: str

    @classmethod
    def from_dict(cls, data: dict) -> "Manifest":
        schema_version = _check_schema_version(data)
        return cls(
            schema_version=schema_version,
            generator=ManifestGenerator.from_dict(_require(data, "generator")),
            source=ManifestSourceFingerprint.from_dict(_require(data, "source")),
            plan_id=_require(data, "plan_id"),
            content_type=_require(data, "content_type"),
            template_profile=_require(data, "template_profile"),
            strategy=_require(data, "strategy"),
            chunk_count=_require(data, "chunk_count"),
            chunks=[ManifestChunk.from_dict(c) for c in _require(data, "chunks")],
            media=list(_require(data, "media")),
            validation_report=_require(data, "validation_report"),
        )

    def to_dict(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "generator": self.generator.to_dict(),
            "source": self.source.to_dict(),
            "plan_id": self.plan_id,
            "content_type": self.content_type,
            "template_profile": self.template_profile,
            "strategy": self.strategy,
            "chunk_count": self.chunk_count,
            "chunks": [c.to_dict() for c in self.chunks],
            "media": list(self.media),
            "validation_report": self.validation_report,
        }


# ---------------------------------------------------------------------------
# Section 9 — ValidationIssue / ValidationReport
# ---------------------------------------------------------------------------

@dataclass
class ValidationIssue:
    severity: str  # "error" | "warning"
    code: str
    message: str
    path: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "ValidationIssue":
        return cls(
            severity=_require(data, "severity"),
            code=_require(data, "code"),
            message=_require(data, "message"),
            path=data.get("path"),
        )

    def to_dict(self) -> dict:
        return {
            "severity": self.severity,
            "code": self.code,
            "message": self.message,
            "path": self.path,
        }


@dataclass
class ValidationReport:
    status: str  # "PASS" | "WARN" | "FAIL"
    issues: list  # list[ValidationIssue]
    source_sha256: str
    plan_id: str

    @classmethod
    def from_dict(cls, data: dict) -> "ValidationReport":
        return cls(
            status=_require(data, "status"),
            issues=[ValidationIssue.from_dict(i) for i in _require(data, "issues")],
            source_sha256=_require(data, "source_sha256"),
            plan_id=_require(data, "plan_id"),
        )

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "issues": [i.to_dict() for i in self.issues],
            "source_sha256": self.source_sha256,
            "plan_id": self.plan_id,
        }


# ---------------------------------------------------------------------------
# publication-map.json (Task 17-topic-grouping) — minimal publication order
# contract for the "grouped" strategy.
# ---------------------------------------------------------------------------

@dataclass
class PublicationMapEntry:
    topic_id: str
    title: str
    order: int
    chunk_id: str
    parent_topic_id: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "PublicationMapEntry":
        return cls(
            topic_id=_require(data, "topic_id"),
            title=_require(data, "title"),
            order=_require(data, "order"),
            chunk_id=_require(data, "chunk_id"),
            parent_topic_id=data.get("parent_topic_id"),
        )

    def to_dict(self) -> dict:
        return {
            "topic_id": self.topic_id,
            "title": self.title,
            "order": self.order,
            "chunk_id": self.chunk_id,
            "parent_topic_id": self.parent_topic_id,
        }


@dataclass
class PublicationMap:
    schema_version: str
    package_identity: str
    entries: list  # list[PublicationMapEntry]

    @classmethod
    def from_dict(cls, data: dict) -> "PublicationMap":
        schema_version = _check_schema_version(data)
        return cls(
            schema_version=schema_version,
            package_identity=_require(data, "package_identity"),
            entries=[
                PublicationMapEntry.from_dict(e) for e in _require(data, "entries")
            ],
        )

    def to_dict(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "package_identity": self.package_identity,
            "entries": [e.to_dict() for e in self.entries],
        }


# ---------------------------------------------------------------------------
# Section 8 — RenderResult
# ---------------------------------------------------------------------------

@dataclass
class RenderResult:
    renderer_name: str
    renderer_version: str
    source_content_sha256: str
    output_files: list
    status: str  # "PASS" | "WARN" | "FAIL"
    errors: list
    warnings: list

    @classmethod
    def from_dict(cls, data: dict) -> "RenderResult":
        return cls(
            renderer_name=_require(data, "renderer_name"),
            renderer_version=_require(data, "renderer_version"),
            source_content_sha256=_require(data, "source_content_sha256"),
            output_files=list(_require(data, "output_files")),
            status=_require(data, "status"),
            errors=list(_require(data, "errors")),
            warnings=list(_require(data, "warnings")),
        )

    def to_dict(self) -> dict:
        return {
            "renderer_name": self.renderer_name,
            "renderer_version": self.renderer_version,
            "source_content_sha256": self.source_content_sha256,
            "output_files": list(self.output_files),
            "status": self.status,
            "errors": list(self.errors),
            "warnings": list(self.warnings),
        }
