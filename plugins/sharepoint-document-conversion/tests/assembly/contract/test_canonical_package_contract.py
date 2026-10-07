"""test_canonical_package_contract.py
====================================

Purpose:
    Contract tests for the `canonical-package` wire shape: ChunkMetadata, ManifestChunk, ManifestGenerator, Manifest, ValidationIssue, ValidationReport (see canonical_schema/canonical_package.py), plus this plugin's own canonical-JSON hashing (hashing.py).

Key Input Dependencies:
    - pytest and the plugin-local tests in this namespace
    - copy
    - pytest
    - canonical_schema.canonical_package
    - hashing

Contract tests for the `canonical-package` wire shape: ChunkMetadata,
ManifestChunk, ManifestGenerator, Manifest, ValidationIssue,
ValidationReport (see canonical_schema/canonical_package.py), plus this
plugin's own canonical-JSON hashing (hashing.py).

Split out of docx-to-content's tests/contract/test_contracts.py during
Phase 4.5 Wave 4 -- this plugin is now the sole producer/owner of this
contract. See
docs/superpowers/plans/phase-4-5-evidence/wave-4-structured-content-assembly-split-decision.md.

Key Functions Index:
    - make_manifest_dict()
    - make_chunk_metadata_dict()
    - TestChunkMetadata.test_round_trip()
    - TestChunkMetadata.test_missing_required_field_raises()
    - TestChunkMetadata.test_missing_schema_version_raises()
    - TestManifest.test_manifest_chunk_round_trip()
    - TestManifest.test_manifest_chunk_missing_field_raises()
    - TestManifest.test_manifest_round_trip()
    - TestManifest.test_manifest_missing_field_raises()
    - TestManifest.test_manifest_missing_schema_version_raises()
    - TestManifest.test_manifest_generator_typed()
    - TestValidation.test_validation_issue_round_trip()
    - TestValidation.test_validation_issue_optional_path()
    - TestValidation.test_validation_issue_missing_required_field_raises()
    - TestValidation.test_validation_report_round_trip()
    - TestValidation.test_validation_report_with_issues()
    - TestValidation.test_validation_report_missing_field_raises()
    - TestCanonicalJson.test_deterministic_regardless_of_key_order()
    - TestCanonicalJson.test_stable_across_calls()
    - TestCanonicalJson.test_content_hash_is_sha256_hex()
    - TestCanonicalJson.test_content_hash_deterministic()
    - TestCanonicalJson.test_content_hash_changes_with_content()
    - test_schema_version_constants_are_independent_per_contract()"""

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


# Build a manifest mapping with all required fields for canonical-package contract tests.
def make_manifest_dict():
    """Build a manifest mapping with all required fields for canonical-package contract tests."""
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


# Build a chunk-sidecar mapping with valid metadata for canonical-package contract tests.
def make_chunk_metadata_dict():
    """Build a chunk-sidecar mapping with valid metadata for canonical-package contract tests."""
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
    # Verify round trip.
    def test_round_trip(self):
        """Verify round trip."""
        data = make_chunk_metadata_dict()
        meta = ChunkMetadata.from_dict(data)
        assert meta.to_dict() == data

    # Verify missing required field raises.
    def test_missing_required_field_raises(self):
        """Verify missing required field raises."""
        data = make_chunk_metadata_dict()
        del data["content_sha256"]
        with pytest.raises(ValueError):
            ChunkMetadata.from_dict(data)

    # Verify missing schema version raises.
    def test_missing_schema_version_raises(self):
        """Verify missing schema version raises."""
        data = make_chunk_metadata_dict()
        del data["schema_version"]
        with pytest.raises(ValueError):
            ChunkMetadata.from_dict(data)


class TestManifest:
    # Verify manifest chunk round trip.
    def test_manifest_chunk_round_trip(self):
        """Verify manifest chunk round trip."""
        data = make_manifest_dict()["chunks"][0]
        chunk = ManifestChunk.from_dict(data)
        assert chunk.to_dict() == data

    # Verify manifest chunk missing field raises.
    def test_manifest_chunk_missing_field_raises(self):
        """Verify manifest chunk missing field raises."""
        data = make_manifest_dict()["chunks"][0]
        del data["source_order"]
        with pytest.raises(ValueError):
            ManifestChunk.from_dict(data)

    # Verify manifest round trip.
    def test_manifest_round_trip(self):
        """Verify manifest round trip."""
        data = make_manifest_dict()
        manifest = Manifest.from_dict(data)
        assert manifest.to_dict() == data

    # Verify manifest missing field raises.
    def test_manifest_missing_field_raises(self):
        """Verify manifest missing field raises."""
        data = make_manifest_dict()
        del data["chunk_count"]
        with pytest.raises(ValueError):
            Manifest.from_dict(data)

    # Verify manifest missing schema version raises.
    def test_manifest_missing_schema_version_raises(self):
        """Verify manifest missing schema version raises."""
        data = make_manifest_dict()
        del data["schema_version"]
        with pytest.raises(ValueError):
            Manifest.from_dict(data)

    # Verify manifest generator typed.
    def test_manifest_generator_typed(self):
        """Verify manifest generator typed."""
        manifest = Manifest.from_dict(make_manifest_dict())
        assert isinstance(manifest.generator, ManifestGenerator)
        assert all(isinstance(c, ManifestChunk) for c in manifest.chunks)


class TestValidation:
    # Verify validation issue round trip.
    def test_validation_issue_round_trip(self):
        """Verify validation issue round trip."""
        data = {
            "severity": "error",
            "code": "missing_chunk_file",
            "message": "chunk file not found",
            "path": "chunks/file-access--a1b2c3d4.md",
        }
        issue = ValidationIssue.from_dict(data)
        assert issue.to_dict() == data

    # Verify validation issue optional path.
    def test_validation_issue_optional_path(self):
        """Verify validation issue optional path."""
        data = {
            "severity": "warning",
            "code": "orphan_media",
            "message": "unused media file",
        }
        issue = ValidationIssue.from_dict(data)
        assert issue.path is None
        assert issue.to_dict()["path"] is None

    # Verify validation issue missing required field raises.
    def test_validation_issue_missing_required_field_raises(self):
        """Verify validation issue missing required field raises."""
        data = {"severity": "error", "message": "x"}
        with pytest.raises(ValueError):
            ValidationIssue.from_dict(data)

    # Verify validation report round trip.
    def test_validation_report_round_trip(self):
        """Verify validation report round trip."""
        data = {
            "status": "PASS",
            "issues": [],
            "source_sha256": "a" * 64,
            "plan_id": "sha256:" + "0" * 64,
        }
        report = ValidationReport.from_dict(data)
        assert report.to_dict() == data

    # Verify validation report with issues.
    def test_validation_report_with_issues(self):
        """Verify validation report with issues."""
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

    # Verify validation report missing field raises.
    def test_validation_report_missing_field_raises(self):
        """Verify validation report missing field raises."""
        data = {"status": "PASS", "issues": []}
        with pytest.raises(ValueError):
            ValidationReport.from_dict(data)


class TestCanonicalJson:
    # Verify deterministic regardless of key order.
    def test_deterministic_regardless_of_key_order(self):
        """Verify deterministic regardless of key order."""
        a = {"b": 1, "a": 2, "c": {"y": 1, "x": 2}}
        b = {"a": 2, "c": {"x": 2, "y": 1}, "b": 1}
        assert canonical_json_bytes(a) == canonical_json_bytes(b)

    # Verify stable across calls.
    def test_stable_across_calls(self):
        """Verify stable across calls."""
        payload = make_manifest_dict()
        assert canonical_json_bytes(payload) == canonical_json_bytes(copy.deepcopy(payload))

    # Verify content hash is SHA-256 hex.
    def test_content_hash_is_sha256_hex(self):
        """Verify content hash is SHA-256 hex."""
        digest = content_hash(canonical_json_bytes({"a": 1}))
        assert len(digest) == 64
        int(digest, 16)  # raises if not hex

    # Verify content hash deterministic.
    def test_content_hash_deterministic(self):
        """Verify content hash deterministic."""
        payload = {"a": 1, "b": [1, 2, 3]}
        h1 = content_hash(canonical_json_bytes(payload))
        h2 = content_hash(canonical_json_bytes(copy.deepcopy(payload)))
        assert h1 == h2

    # Verify content hash changes with content.
    def test_content_hash_changes_with_content(self):
        """Verify content hash changes with content."""
        h1 = content_hash(canonical_json_bytes({"a": 1}))
        h2 = content_hash(canonical_json_bytes({"a": 2}))
        assert h1 != h2


# Verify schema version constants are independent per contract.
def test_schema_version_constants_are_independent_per_contract():
    """Verify schema version constants are independent per contract."""
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
