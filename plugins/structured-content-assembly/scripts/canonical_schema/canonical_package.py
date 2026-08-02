"""Authoritative schema for the `canonical-package` contract: `Manifest`,
`ManifestChunk`, `ManifestGenerator`, `ManifestSourceFingerprint`,
`ChunkMetadata`, and the `ValidationIssue`/`ValidationReport` types used by
this package's own `validation.json`.

`structured-content-assembly` is the sole producer of this contract -- this module
is the single source of truth for its wire format, packaged inside this
plugin so the plugin installs and runs standalone.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from canonical_schema.shared import check_schema_version, require

MANIFEST_SCHEMA_VERSION = "1.0"
CHUNK_METADATA_SCHEMA_VERSION = "1.0"


@dataclass
class ManifestSourceFingerprint:
    """Manifest's `source` block omits `size_bytes`."""

    path: str
    sha256: str

    @classmethod
    def from_dict(cls, data: dict) -> "ManifestSourceFingerprint":
        return cls(path=require(data, "path"), sha256=require(data, "sha256"))

    def to_dict(self) -> dict:
        return {"path": self.path, "sha256": self.sha256}


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
    # Structural-anchor lineage folded into this chunk (the "grouped"
    # strategy only): list of {"stable_key", "source_heading_path",
    # "occurrence", "heading_level"} dicts, one per structural anchor this
    # topic chunk contains, in source order. None for ungrouped
    # ("single"/"chunked") chunks, which map 1:1 to a single structural
    # anchor already identified by chunk_id.
    anchors: Optional[list] = None

    @classmethod
    def from_dict(cls, data: dict) -> "ChunkMetadata":
        schema_version = check_schema_version(data, CHUNK_METADATA_SCHEMA_VERSION, "ChunkMetadata")
        return cls(
            schema_version=schema_version,
            chunk_id=require(data, "chunk_id"),
            source_order=require(data, "source_order"),
            source_heading_path=list(require(data, "source_heading_path")),
            topic=require(data, "topic"),
            content_type=require(data, "content_type"),
            template_profile=require(data, "template_profile"),
            source_sha256=require(data, "source_sha256"),
            plan_id=require(data, "plan_id"),
            content_file=require(data, "content_file"),
            content_sha256=require(data, "content_sha256"),
            local_links=list(require(data, "local_links")),
            media_refs=list(require(data, "media_refs")),
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
            chunk_id=require(data, "chunk_id"),
            content_file=require(data, "content_file"),
            metadata_file=require(data, "metadata_file"),
            source_order=require(data, "source_order"),
            source_heading_path=list(require(data, "source_heading_path")),
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
            plugin=require(data, "plugin"),
            plugin_version=require(data, "plugin_version"),
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
        schema_version = check_schema_version(data, MANIFEST_SCHEMA_VERSION, "Manifest")
        return cls(
            schema_version=schema_version,
            generator=ManifestGenerator.from_dict(require(data, "generator")),
            source=ManifestSourceFingerprint.from_dict(require(data, "source")),
            plan_id=require(data, "plan_id"),
            content_type=require(data, "content_type"),
            template_profile=require(data, "template_profile"),
            strategy=require(data, "strategy"),
            chunk_count=require(data, "chunk_count"),
            chunks=[ManifestChunk.from_dict(c) for c in require(data, "chunks")],
            media=list(require(data, "media")),
            validation_report=require(data, "validation_report"),
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


@dataclass
class ValidationIssue:
    severity: str  # "error" | "warning"
    code: str
    message: str
    path: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "ValidationIssue":
        return cls(
            severity=require(data, "severity"),
            code=require(data, "code"),
            message=require(data, "message"),
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
            status=require(data, "status"),
            issues=[ValidationIssue.from_dict(i) for i in require(data, "issues")],
            source_sha256=require(data, "source_sha256"),
            plan_id=require(data, "plan_id"),
        )

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "issues": [i.to_dict() for i in self.issues],
            "source_sha256": self.source_sha256,
            "plan_id": self.plan_id,
        }


def validate(data: dict) -> None:
    """Validate a raw dict against the canonical-package v1 manifest shape."""
    Manifest.from_dict(data)
