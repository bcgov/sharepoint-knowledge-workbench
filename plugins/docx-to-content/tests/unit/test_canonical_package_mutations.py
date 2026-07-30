"""
test_canonical_package_mutations.py
======================================

Layer-2 mutation suite (Phase 2, spec Section 5.1): CanonicalPackage.load()
is itself a validator (schema loading, content-hash verification, media
existence) and must be proven to reject corruption introduced AFTER
promotion -- this is the exact path a tampered/corrupted-on-disk package
would be caught (or not) through, independent of whatever
validate_canonical.py already recorded in validation.json at convert time.
"""

import json

import pytest

# The loader lives in package.CanonicalPackage in this codebase.
from canonical_package import CanonicalPackage, CanonicalPackageIntegrityError, CanonicalPackageValidationError
from tests.unit.test_validate_canonical import _build_minimal_valid_package


def test_load_rejects_media_deleted_after_promotion(tmp_path):
    package_dir = _build_minimal_valid_package(tmp_path, with_media=True, validated=True)
    media_file = next((package_dir / "media").iterdir())
    media_file.unlink()

    with pytest.raises(CanonicalPackageIntegrityError):
        CanonicalPackage.load(package_dir)


def test_load_rejects_chunk_content_altered_after_promotion(tmp_path):
    package_dir = _build_minimal_valid_package(tmp_path, validated=True)
    chunk_path = next((package_dir / "chunks").glob("*.md"))
    chunk_path.write_text(chunk_path.read_text() + "\ntampered\n")

    with pytest.raises(CanonicalPackageIntegrityError):
        CanonicalPackage.load(package_dir)


def test_load_rejects_fail_status_validation_report(tmp_path):
    package_dir = _build_minimal_valid_package(tmp_path, validated=True)
    validation_path = package_dir / "validation.json"
    data = json.loads(validation_path.read_text())
    data["status"] = "FAIL"
    data["issues"] = [{"severity": "error", "code": "x", "message": "x", "path": None}]
    validation_path.write_text(json.dumps(data))

    with pytest.raises(CanonicalPackageValidationError):
        CanonicalPackage.load(package_dir)


def test_load_rejects_malformed_manifest(tmp_path):
    package_dir = _build_minimal_valid_package(tmp_path, validated=True)
    (package_dir / "manifest.json").write_text("{not valid json")

    with pytest.raises(CanonicalPackageValidationError):
        CanonicalPackage.load(package_dir)


def test_load_rejects_validation_report_plan_id_not_matching_manifest(tmp_path):
    """Round-3 review (GPT 5.6 blocking #5): a PASS report copied from a
    different package must not silently authorize this one -- Task 8's
    load() now re-derives this instead of trusting validation.json's
    status alone."""
    package_dir = _build_minimal_valid_package(tmp_path, validated=True)
    validation_path = package_dir / "validation.json"
    data = json.loads(validation_path.read_text())
    data["plan_id"] = "sha256:" + "9" * 64
    validation_path.write_text(json.dumps(data))

    with pytest.raises(CanonicalPackageIntegrityError):
        CanonicalPackage.load(package_dir)


def test_load_rejects_validation_report_source_sha256_not_matching_manifest(tmp_path):
    package_dir = _build_minimal_valid_package(tmp_path, validated=True)
    validation_path = package_dir / "validation.json"
    data = json.loads(validation_path.read_text())
    data["source_sha256"] = "8" * 64
    validation_path.write_text(json.dumps(data))

    with pytest.raises(CanonicalPackageIntegrityError):
        CanonicalPackage.load(package_dir)


def test_load_rejects_grouped_package_missing_publication_map_after_promotion(tmp_path):
    """Round-3 review (GPT 5.6 blocking #4): validate_canonical.py already
    rejects this at CONVERT time, but load() must re-check independently,
    since the file could be deleted after promotion -- Layer 2 exists
    precisely to catch what happens between promotion and render time."""
    package_dir = _build_minimal_valid_package(tmp_path, strategy="grouped", validated=True)
    (package_dir / "publication-map.json").unlink()

    with pytest.raises(CanonicalPackageValidationError):
        CanonicalPackage.load(package_dir)


def test_load_rejects_publication_map_identity_mismatch_after_promotion(tmp_path):
    package_dir = _build_minimal_valid_package(tmp_path, strategy="grouped", validated=True)
    pub_map_path = package_dir / "publication-map.json"
    data = json.loads(pub_map_path.read_text())
    data["package_identity"] = "sha256:" + "7" * 64
    pub_map_path.write_text(json.dumps(data))

    with pytest.raises(CanonicalPackageIntegrityError):
        CanonicalPackage.load(package_dir)


def test_load_rejects_publication_map_chunk_id_altered_after_promotion(tmp_path):
    package_dir = _build_minimal_valid_package(tmp_path, strategy="grouped", validated=True)
    pub_map_path = package_dir / "publication-map.json"
    data = json.loads(pub_map_path.read_text())
    data["entries"][0]["chunk_id"] = "nonexistent-chunk-id"
    pub_map_path.write_text(json.dumps(data))

    with pytest.raises(CanonicalPackageIntegrityError):
        CanonicalPackage.load(package_dir)


def test_load_rejects_unexpected_publication_map_on_non_grouped_package(tmp_path):
    package_dir = _build_minimal_valid_package(tmp_path, strategy="chunked", validated=True)
    (package_dir / "publication-map.json").write_text(json.dumps({
        "schema_version": "1.0",
        "package_identity": "sha256:" + "a" * 64,
        "entries": [],
    }))

    with pytest.raises(CanonicalPackageValidationError):
        CanonicalPackage.load(package_dir)


def test_load_rejects_malformed_publication_map_on_non_grouped_package(tmp_path):
    package_dir = _build_minimal_valid_package(tmp_path, strategy="chunked", validated=True)
    # publication-map.json exists but is malformed JSON
    (package_dir / "publication-map.json").write_text("{not valid json")

    with pytest.raises(CanonicalPackageValidationError):
        CanonicalPackage.load(package_dir)
