"""
test_package_load.py
=====================

Tests for `package.CanonicalPackage.load()` (Task 12): the renderer-side
loader that re-validates an already-accepted canonical package before
handing it to any renderer.

Builds a real ACCEPTED package via `convert.convert_and_promote` (same
helper `tests/integration/test_atomic_promotion.py` uses) against the real
`small_single.docx` fixture, then tampers with the on-disk package to prove
each of `load()`'s five checks (schema, validation status, hash integrity,
media-reference integrity) actually runs rather than being trusted from the
original convert-time validation.
"""

import json
import shutil
from pathlib import Path

import pytest

import analyze_structure
from canonical_schema import canonical_package as contracts
from plan_schema import analysis_plan as plan_contracts
import convert
import package
import canonical_package
import plans


def test_canonical_package_importable_from_new_module():
    from canonical_package import CanonicalPackage
    assert hasattr(CanonicalPackage, "load")


def test_canonical_package_no_longer_defined_in_package_module():
    import package
    assert not hasattr(package, "CanonicalPackage")


FIXTURES = Path(__file__).parent.parent / "fixtures"
SMALL_SINGLE_DOCX = FIXTURES / "small_single.docx"

PANDOC_AVAILABLE = shutil.which("pandoc") is not None
pytestmark = pytest.mark.skipif(not PANDOC_AVAILABLE, reason="pandoc not available on PATH")


def _confirmed_plan(tmp_path):
    analysis_dir = tmp_path / "analysis"
    analyze_structure.analyze_document(SMALL_SINGLE_DOCX, analysis_dir)
    draft = plan_contracts.ConversionPlan.from_dict(
        json.loads((analysis_dir / "conversion-plan.draft.json").read_text())
    )
    return plans.confirm_plan(draft, confirmed_by="test-suite")


def _accepted_package_dir(tmp_path) -> Path:
    confirmed = _confirmed_plan(tmp_path)
    output_root = tmp_path / "out"
    manifest, report, promoted, final_dir = convert.convert_and_promote(
        SMALL_SINGLE_DOCX, confirmed, output_root
    )
    assert promoted is True
    assert report.status == "PASS"
    return final_dir


REPEATED_HEADINGS_DOCX = FIXTURES / "repeated_headings.docx"


def test_load_attaches_publication_map_for_grouped(tmp_path):
    import dataclasses

    analysis_dir = tmp_path / "analysis"
    result = analyze_structure.analyze_document(REPEATED_HEADINGS_DOCX, analysis_dir)
    grouped_draft = dataclasses.replace(result.plan, strategy="grouped")
    confirmed = plans.confirm_plan(grouped_draft, confirmed_by="test-suite")

    output_root = tmp_path / "out"
    manifest, report, promoted, final_dir = convert.convert_and_promote(
        REPEATED_HEADINGS_DOCX, confirmed, output_root
    )
    assert promoted is True, report.issues
    assert manifest.strategy == "grouped"

    loaded = canonical_package.CanonicalPackage.load(final_dir)
    assert loaded.publication_map is not None
    assert len(loaded.publication_map.entries) == manifest.chunk_count


def test_load_returns_package_with_manifest_chunks_and_media(tmp_path):
    final_dir = _accepted_package_dir(tmp_path)

    loaded = canonical_package.CanonicalPackage.load(final_dir)

    assert isinstance(loaded, canonical_package.CanonicalPackage)
    assert loaded.manifest.schema_version == contracts.MANIFEST_SCHEMA_VERSION
    assert len(loaded.chunks) == loaded.manifest.chunk_count
    assert loaded.media_dir == final_dir / "media"
    assert loaded.package_dir == final_dir
    assert loaded.publication_map is None
    # Every chunk's content and metadata was actually loaded into memory.
    for chunk in loaded.chunks:
        assert isinstance(chunk.content, str)
        assert isinstance(chunk.metadata, contracts.ChunkMetadata)


def test_load_rejects_missing_manifest(tmp_path):
    final_dir = _accepted_package_dir(tmp_path)
    (final_dir / "manifest.json").unlink()

    with pytest.raises(canonical_package.CanonicalPackageError):
        canonical_package.CanonicalPackage.load(final_dir)


def test_load_rejects_malformed_manifest_schema(tmp_path):
    final_dir = _accepted_package_dir(tmp_path)
    manifest_data = json.loads((final_dir / "manifest.json").read_text())
    manifest_data.pop("chunk_count")  # required field
    (final_dir / "manifest.json").write_text(json.dumps(manifest_data))

    with pytest.raises(canonical_package.CanonicalPackageError):
        canonical_package.CanonicalPackage.load(final_dir)


def test_load_rejects_fail_status(tmp_path):
    final_dir = _accepted_package_dir(tmp_path)
    validation_data = json.loads((final_dir / "validation.json").read_text())
    validation_data["status"] = "FAIL"
    (final_dir / "validation.json").write_text(json.dumps(validation_data))

    with pytest.raises(canonical_package.CanonicalPackageValidationError):
        canonical_package.CanonicalPackage.load(final_dir)


def test_load_rejects_warn_status_without_disposition_file(tmp_path):
    final_dir = _accepted_package_dir(tmp_path)
    validation_data = json.loads((final_dir / "validation.json").read_text())
    validation_data["status"] = "WARN"
    validation_data["issues"] = [
        {"severity": "warning", "code": "some_check", "message": "msg", "path": "chunks/x.md"}
    ]
    (final_dir / "validation.json").write_text(json.dumps(validation_data))
    # No warning-disposition.json present.

    with pytest.raises(canonical_package.CanonicalPackageValidationError):
        canonical_package.CanonicalPackage.load(final_dir)


def test_load_accepts_warn_status_with_complete_disposition_file(tmp_path):
    final_dir = _accepted_package_dir(tmp_path)
    validation_data = json.loads((final_dir / "validation.json").read_text())
    validation_data["status"] = "WARN"
    validation_data["issues"] = [
        {"severity": "warning", "code": "some_check", "message": "msg", "path": "chunks/x.md"}
    ]
    (final_dir / "validation.json").write_text(json.dumps(validation_data))
    (final_dir / "warning-disposition.json").write_text(json.dumps({
        "dispositions": {
            "some_check|chunks/x.md": {
                "status": "accepted",
                "note": "reviewed",
                "by": "test-suite",
                "at": "2026-07-27T00:00:00Z",
            }
        }
    }))

    loaded = canonical_package.CanonicalPackage.load(final_dir)
    assert loaded.validation_report.status == "WARN"


def test_load_rejects_tampered_chunk_content_hash_mismatch(tmp_path):
    final_dir = _accepted_package_dir(tmp_path)
    manifest_data = json.loads((final_dir / "manifest.json").read_text())
    first_chunk = manifest_data["chunks"][0]
    content_path = final_dir / first_chunk["content_file"]
    content_path.write_text(content_path.read_text() + "\n\ntampered content\n")

    with pytest.raises(canonical_package.CanonicalPackageIntegrityError):
        canonical_package.CanonicalPackage.load(final_dir)


def test_load_rejects_missing_media_reference(tmp_path):
    final_dir = _accepted_package_dir(tmp_path)
    media_dir = final_dir / "media"
    media_files = list(media_dir.glob("*")) if media_dir.exists() else []
    if not media_files:
        pytest.skip("small_single.docx fixture has no media references to tamper with")
    media_files[0].unlink()

    with pytest.raises(canonical_package.CanonicalPackageIntegrityError):
        canonical_package.CanonicalPackage.load(final_dir)
