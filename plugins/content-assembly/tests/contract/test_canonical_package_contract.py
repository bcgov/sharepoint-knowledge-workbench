"""
test_canonical_package_contract.py
====================================

Contract tests for the `canonical-package` wire shape: ChunkMetadata,
ManifestChunk, ManifestGenerator, Manifest, ValidationIssue,
ValidationReport (see canonical_schema/canonical_package.py), plus this
plugin's own canonical-JSON hashing (hashing.py).

Split out of docx-to-content's tests/contract/test_contracts.py during
Phase 4.5 Wave 4 -- this plugin is now the sole producer/owner of this
contract. See
docs/superpowers/plans/phase-4-5-evidence/wave-4-structured-content-assembly-split-decision.md.
"""

import copy

import pytest

from canonical_schema.canonical_package import (
    ChunkMetadata,
    ManifestChunk,
    ManifestGenerator,
    Manifest,
    ValidationIssue,
    ValidationReport,
    MANIFEST_SCHEMA_VERSION,
    CHUNK_METADATA_SCHEMA_VERSION,
)
from hashing import canonical_json_bytes, content_hash


def make_manifest_dict():
    return {
        "schema_version": "1.0",
        "generator": {"plugin": "structured-content-assembly", "plugin_version": "0.1.0"},
        "source": {
            "path": "sourcedocuments/sample-manual.docx",
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


def test_schema_version_constants_are_independent_per_contract():
    assert MANIFEST_SCHEMA_VERSION == "1.0"
    assert CHUNK_METADATA_SCHEMA_VERSION == "1.0"

    with pytest.raises(ValueError, match="schema_version"):
        Manifest.from_dict({
            "schema_version": "9.9",
            "generator": {"plugin": "p", "plugin_version": "0.1.0"},
            "source": {"path": "x", "sha256": "a" * 64},
            "plan_id": "sha256:" + "a" * 64,
            "content_type": "manual",
            "template_profile": "t",
            "strategy": "chunked",
            "chunk_count": 0,
            "chunks": [],
            "media": [],
            "validation_report": "validation.json",
        })
