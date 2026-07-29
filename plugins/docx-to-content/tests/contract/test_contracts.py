"""
test_contracts.py
==================

Contract tests for the versioned data shapes defined in
docs/superpowers/specs/2026-07-25-docx-to-content-plugin-design-v3-ammendments.md
sections 6 and 8: SourceFingerprint, StructuralAnchor, ConversionPlan,
ChunkMetadata, ManifestChunk, Manifest, ValidationIssue, ValidationReport,
RenderResult.

These tests exercise:
- round-trip to_dict()/from_dict() for every required field,
- strict rejection of dicts missing required fields,
- strict rejection of unsupported/missing schema_version,
- deterministic canonical JSON serialization,
- SHA-256 fingerprint hashing,
- plan_id exclusion of plan_id itself and confirmation.confirmed_at.
"""

import copy

import pytest

from contracts import (
    SourceFingerprint,
    StructuralAnchor,
    ConversionPlan,
    Confirmation,
    ChunkMetadata,
    ManifestChunk,
    ManifestGenerator,
    Manifest,
    ValidationIssue,
    ValidationReport,
    RenderResult,
    SUPPORTED_SCHEMA_VERSION,
)
from hashing import canonical_json_bytes, content_hash, compute_plan_id


# ---------------------------------------------------------------------------
# Fixtures / sample data matching the spec's exact JSON shapes
# ---------------------------------------------------------------------------

def make_plan_dict(confirmed_at="2026-07-25T00:00:00Z"):
    return {
        "schema_version": "1.0",
        "plan_id": "sha256:" + "0" * 64,
        "source": {
            "path": "sourcedocuments/CEIS MANUAL - working version.docx",
            "sha256": "a" * 64,
            "size_bytes": 12345,
        },
        "strategy": "chunked",
        "chunk_level": 2,
        "chunk_anchors": [
            {
                "stable_key": "file-access",
                "heading_text": "FILE ACCESS",
                "heading_level": 2,
                "occurrence": 1,
                "source_heading_path": ["FILE ACCESS"],
            }
        ],
        "content_type": "manual",
        "template_profile": "source-structure-v1",
        "confirmation": {
            "status": "confirmed",
            "confirmed_by": "user-or-supervising-agent",
            "confirmed_at": confirmed_at,
        },
        "analysis_warnings": [],
    }


def make_manifest_dict():
    return {
        "schema_version": "1.0",
        "generator": {"plugin": "docx-to-content", "plugin_version": "0.1.0"},
        "source": {
            "path": "sourcedocuments/CEIS MANUAL - working version.docx",
            "sha256": "a" * 64,
        },
        "plan_id": "sha256:" + "0" * 64,
        "content_type": "manual",
        "template_profile": "source-structure-v1",
        "strategy": "chunked",
        "chunk_count": 1,
        "chunks": [
            {
                "chunk_id": "file-access--a1b2c3d4",
                "content_file": "file-access--a1b2c3d4.md",
                "metadata_file": "file-access--a1b2c3d4.meta.json",
                "source_order": 7,
                "source_heading_path": ["FILE ACCESS"],
            }
        ],
        "media": [],
        "validation_report": "validation.json",
    }


def make_chunk_metadata_dict():
    return {
        "schema_version": "1.0",
        "chunk_id": "file-access--a1b2c3d4",
        "source_order": 7,
        "source_heading_path": ["FILE ACCESS"],
        "topic": "FILE ACCESS",
        "content_type": "manual",
        "template_profile": "source-structure-v1",
        "source_sha256": "a" * 64,
        "plan_id": "sha256:" + "0" * 64,
        "content_file": "file-access--a1b2c3d4.md",
        "content_sha256": "b" * 64,
        "local_links": [],
        "media_refs": [],
    }


# ---------------------------------------------------------------------------
# SourceFingerprint
# ---------------------------------------------------------------------------

class TestSourceFingerprint:
    def test_round_trip(self):
        data = {
            "path": "sourcedocuments/x.docx",
            "sha256": "a" * 64,
            "size_bytes": 100,
        }
        fp = SourceFingerprint.from_dict(data)
        assert fp.to_dict() == data

    def test_missing_required_field_raises(self):
        data = {"path": "x.docx", "sha256": "a" * 64}
        with pytest.raises(ValueError):
            SourceFingerprint.from_dict(data)


# ---------------------------------------------------------------------------
# StructuralAnchor
# ---------------------------------------------------------------------------

class TestStructuralAnchor:
    def test_round_trip(self):
        data = {
            "stable_key": "file-access",
            "heading_text": "FILE ACCESS",
            "heading_level": 2,
            "occurrence": 1,
            "source_heading_path": ["FILE ACCESS"],
        }
        anchor = StructuralAnchor.from_dict(data)
        assert anchor.to_dict() == data

    def test_missing_required_field_raises(self):
        data = {
            "stable_key": "file-access",
            "heading_text": "FILE ACCESS",
            "heading_level": 2,
        }
        with pytest.raises(ValueError):
            StructuralAnchor.from_dict(data)


# ---------------------------------------------------------------------------
# ConversionPlan
# ---------------------------------------------------------------------------

class TestConversionPlan:
    def test_round_trip_all_fields(self):
        data = make_plan_dict()
        plan = ConversionPlan.from_dict(data)
        assert plan.to_dict() == data

    def test_missing_required_field_raises(self):
        data = make_plan_dict()
        del data["strategy"]
        with pytest.raises(ValueError):
            ConversionPlan.from_dict(data)

    def test_missing_schema_version_raises(self):
        data = make_plan_dict()
        del data["schema_version"]
        with pytest.raises(ValueError):
            ConversionPlan.from_dict(data)

    def test_unsupported_schema_version_raises(self):
        data = make_plan_dict()
        data["schema_version"] = "99.9"
        with pytest.raises(ValueError):
            ConversionPlan.from_dict(data)

    def test_supported_schema_version_constant(self):
        assert SUPPORTED_SCHEMA_VERSION == "1.0"

    def test_confirmation_status_values(self):
        data = make_plan_dict()
        data["confirmation"]["status"] = "draft"
        plan = ConversionPlan.from_dict(data)
        assert plan.confirmation.status == "draft"

    def test_nested_source_and_anchors_are_typed(self):
        plan = ConversionPlan.from_dict(make_plan_dict())
        assert isinstance(plan.source, SourceFingerprint)
        assert all(isinstance(a, StructuralAnchor) for a in plan.chunk_anchors)
        assert isinstance(plan.confirmation, Confirmation)


# ---------------------------------------------------------------------------
# ChunkMetadata
# ---------------------------------------------------------------------------

class TestChunkMetadata:
    def test_round_trip(self):
        data = make_chunk_metadata_dict()
        meta = ChunkMetadata.from_dict(data)
        assert meta.to_dict() == data

    def test_missing_required_field_raises(self):
        data = make_chunk_metadata_dict()
        del data["content_sha256"]
        with pytest.raises(ValueError):
            ChunkMetadata.from_dict(data)

    def test_missing_schema_version_raises(self):
        data = make_chunk_metadata_dict()
        del data["schema_version"]
        with pytest.raises(ValueError):
            ChunkMetadata.from_dict(data)


# ---------------------------------------------------------------------------
# ManifestChunk / Manifest
# ---------------------------------------------------------------------------

class TestManifest:
    def test_manifest_chunk_round_trip(self):
        data = make_manifest_dict()["chunks"][0]
        chunk = ManifestChunk.from_dict(data)
        assert chunk.to_dict() == data

    def test_manifest_chunk_missing_field_raises(self):
        data = make_manifest_dict()["chunks"][0]
        del data["source_order"]
        with pytest.raises(ValueError):
            ManifestChunk.from_dict(data)

    def test_manifest_round_trip(self):
        data = make_manifest_dict()
        manifest = Manifest.from_dict(data)
        assert manifest.to_dict() == data

    def test_manifest_missing_field_raises(self):
        data = make_manifest_dict()
        del data["chunk_count"]
        with pytest.raises(ValueError):
            Manifest.from_dict(data)

    def test_manifest_missing_schema_version_raises(self):
        data = make_manifest_dict()
        del data["schema_version"]
        with pytest.raises(ValueError):
            Manifest.from_dict(data)

    def test_manifest_generator_typed(self):
        manifest = Manifest.from_dict(make_manifest_dict())
        assert isinstance(manifest.generator, ManifestGenerator)
        assert all(isinstance(c, ManifestChunk) for c in manifest.chunks)


# ---------------------------------------------------------------------------
# ValidationIssue / ValidationReport
# ---------------------------------------------------------------------------

class TestValidation:
    def test_validation_issue_round_trip(self):
        data = {
            "severity": "error",
            "code": "missing_chunk_file",
            "message": "chunk file not found",
            "path": "chunks/file-access--a1b2c3d4.md",
        }
        issue = ValidationIssue.from_dict(data)
        assert issue.to_dict() == data

    def test_validation_issue_optional_path(self):
        data = {
            "severity": "warning",
            "code": "orphan_media",
            "message": "unused media file",
        }
        issue = ValidationIssue.from_dict(data)
        assert issue.path is None
        assert issue.to_dict()["path"] is None

    def test_validation_issue_missing_required_field_raises(self):
        data = {"severity": "error", "message": "x"}
        with pytest.raises(ValueError):
            ValidationIssue.from_dict(data)

    def test_validation_report_round_trip(self):
        data = {
            "status": "PASS",
            "issues": [],
            "source_sha256": "a" * 64,
            "plan_id": "sha256:" + "0" * 64,
        }
        report = ValidationReport.from_dict(data)
        assert report.to_dict() == data

    def test_validation_report_with_issues(self):
        data = {
            "status": "FAIL",
            "issues": [
                {
                    "severity": "error",
                    "code": "missing_chunk_file",
                    "message": "x",
                    "path": None,
                }
            ],
            "source_sha256": "a" * 64,
            "plan_id": "sha256:" + "0" * 64,
        }
        report = ValidationReport.from_dict(data)
        assert len(report.issues) == 1
        assert isinstance(report.issues[0], ValidationIssue)
        assert report.to_dict() == data

    def test_validation_report_missing_field_raises(self):
        data = {"status": "PASS", "issues": []}
        with pytest.raises(ValueError):
            ValidationReport.from_dict(data)


# ---------------------------------------------------------------------------
# RenderResult
# ---------------------------------------------------------------------------


def test_render_result_uses_source_content_sha256_not_manifest_hash():
    data = {
        "renderer_name": "multipage-markdown",
        "renderer_version": "0.1.0",
        "source_content_sha256": "a" * 64,
        "output_files": [],
        "status": "PASS",
        "errors": [],
        "warnings": [],
    }
    result = RenderResult.from_dict(data)
    assert result.source_content_sha256 == "a" * 64
    assert result.to_dict() == data

class TestRenderResult:
    def test_round_trip(self):
        data = {
            "renderer_name": "multipage-markdown",
            "renderer_version": "0.1.0",
            "source_content_sha256": "sha256:" + "0" * 64,
            "output_files": ["index.md", "file-access--a1b2c3d4.md"],
            "status": "PASS",
            "errors": [],
            "warnings": [],
        }
        result = RenderResult.from_dict(data)
        assert result.to_dict() == data

    def test_missing_required_field_raises(self):
        data = {
            "renderer_name": "multipage-markdown",
            "renderer_version": "0.1.0",
            "source_content_sha256": "sha256:" + "0" * 64,
            "output_files": [],
            "status": "PASS",
        }
        with pytest.raises(ValueError):
            RenderResult.from_dict(data)


# ---------------------------------------------------------------------------
# Canonical JSON / hashing
# ---------------------------------------------------------------------------

class TestCanonicalJson:
    def test_deterministic_regardless_of_key_order(self):
        a = {"b": 1, "a": 2, "c": {"y": 1, "x": 2}}
        b = {"a": 2, "c": {"x": 2, "y": 1}, "b": 1}
        assert canonical_json_bytes(a) == canonical_json_bytes(b)

    def test_stable_across_calls(self):
        payload = make_manifest_dict()
        assert canonical_json_bytes(payload) == canonical_json_bytes(copy.deepcopy(payload))

    def test_content_hash_is_sha256_hex(self):
        digest = content_hash(canonical_json_bytes({"a": 1}))
        assert len(digest) == 64
        int(digest, 16)  # raises if not hex

    def test_content_hash_deterministic(self):
        payload = {"a": 1, "b": [1, 2, 3]}
        h1 = content_hash(canonical_json_bytes(payload))
        h2 = content_hash(canonical_json_bytes(copy.deepcopy(payload)))
        assert h1 == h2

    def test_content_hash_changes_with_content(self):
        h1 = content_hash(canonical_json_bytes({"a": 1}))
        h2 = content_hash(canonical_json_bytes({"a": 2}))
        assert h1 != h2


class TestComputePlanId:
    def test_plan_id_prefixed(self):
        plan = ConversionPlan.from_dict(make_plan_dict())
        plan_id = compute_plan_id(plan)
        assert plan_id.startswith("sha256:")
        assert len(plan_id) == len("sha256:") + 64

    def test_plan_id_excludes_confirmed_at_timestamp(self):
        plan_a = ConversionPlan.from_dict(
            make_plan_dict(confirmed_at="2026-07-25T00:00:00Z")
        )
        plan_b = ConversionPlan.from_dict(
            make_plan_dict(confirmed_at="2030-01-01T12:34:56Z")
        )
        assert compute_plan_id(plan_a) == compute_plan_id(plan_b)

    def test_plan_id_excludes_plan_id_field_itself(self):
        data_a = make_plan_dict()
        data_a["plan_id"] = "sha256:" + "1" * 64
        data_b = make_plan_dict()
        data_b["plan_id"] = "sha256:" + "2" * 64
        plan_a = ConversionPlan.from_dict(data_a)
        plan_b = ConversionPlan.from_dict(data_b)
        assert compute_plan_id(plan_a) == compute_plan_id(plan_b)

    def test_plan_id_changes_with_content(self):
        data_a = make_plan_dict()
        data_b = make_plan_dict()
        data_b["chunk_level"] = 3
        plan_a = ConversionPlan.from_dict(data_a)
        plan_b = ConversionPlan.from_dict(data_b)
        assert compute_plan_id(plan_a) != compute_plan_id(plan_b)
