"""
test_validate_rendered_aspx.py
================================

Tests for the ASPX extension of `renderers.validate_rendered` (Phase 6
Task 0.16's `validate-rendered-output` skill, extended to also validate
`render-sharepoint-pages` output -- `validate_aspx_rendered_output` and
`render_and_promote_aspx`). Mirrors `test_validate_rendered.py`'s
pattern: build a synthetic package, produce a real staged ASPX render
via `sharepoint_aspx.render_to_staging`, then corrupt one specific thing
before validating -- proving each detection in isolation.
"""

import json
import shutil
from pathlib import Path

import pytest

import atomic_output
from canonical_schema import canonical_package as ck_contracts
import canonical_package as canonical_package_module
from renderers import sharepoint_aspx as spx
from renderers import validate_rendered as vr

PANDOC_AVAILABLE = shutil.which("pandoc") is not None
requires_pandoc = pytest.mark.skipif(not PANDOC_AVAILABLE, reason="pandoc not on PATH")

FAKE_SHA = "a" * 64
OTHER_SHA = "b" * 64


# ---------------------------------------------------------------------------
# Synthetic CanonicalPackage builder (same pattern as test_sharepoint_aspx.py)
# ---------------------------------------------------------------------------

def _metadata(chunk_id, heading_path, order, content, local_links=None):
    return ck_contracts.ChunkMetadata(
        schema_version=ck_contracts.MANIFEST_SCHEMA_VERSION,
        chunk_id=chunk_id,
        source_order=order,
        source_heading_path=list(heading_path),
        topic=heading_path[-1],
        content_type="reference",
        template_profile="generic",
        source_sha256=FAKE_SHA,
        plan_id="plan-1",
        content_file=f"chunks/{chunk_id}.md",
        content_sha256=FAKE_SHA,
        local_links=list(local_links or []),
        media_refs=[],
    )


def _manifest_chunk(chunk_id, heading_path, order):
    return ck_contracts.ManifestChunk(
        chunk_id=chunk_id,
        content_file=f"chunks/{chunk_id}.md",
        metadata_file=f"chunks/{chunk_id}.meta.json",
        source_order=order,
        source_heading_path=list(heading_path),
    )


def _build_synthetic_package(tmp_path, chunk_specs, with_media=True):
    package_dir = tmp_path / "canonical-content"
    media_dir = package_dir / "media"
    media_dir.mkdir(parents=True)
    media_names = []
    if with_media:
        (media_dir / "diagram.png").write_bytes(b"fake-png-bytes")
        media_names = ["diagram.png"]

    loaded_chunks = []
    manifest_chunks = []
    for idx, (chunk_id, heading_path, content, local_links) in enumerate(chunk_specs):
        meta = _metadata(chunk_id, heading_path, idx, content, local_links)
        loaded_chunks.append(canonical_package_module.LoadedChunk(metadata=meta, content=content))
        manifest_chunks.append(_manifest_chunk(chunk_id, heading_path, idx))

    manifest = ck_contracts.Manifest(
        schema_version=ck_contracts.MANIFEST_SCHEMA_VERSION,
        generator=ck_contracts.ManifestGenerator(plugin="docx-to-content", plugin_version="0.1.0"),
        source=ck_contracts.ManifestSourceFingerprint(path="sourcedocuments/x.docx", sha256=FAKE_SHA),
        plan_id="plan-1",
        content_type="reference",
        template_profile="generic",
        strategy="heading-based",
        chunk_count=len(manifest_chunks),
        chunks=manifest_chunks,
        media=media_names,
        validation_report="validation.json",
    )
    validation_report = ck_contracts.ValidationReport(
        status="PASS", issues=[], source_sha256=FAKE_SHA, plan_id="plan-1"
    )

    return canonical_package_module.CanonicalPackage(
        manifest=manifest,
        validation_report=validation_report,
        chunks=loaded_chunks,
        media_dir=media_dir,
        package_dir=package_dir,
    )


def _staged_render(tmp_path, pkg):
    result, staging_dir = spx.render_to_staging(pkg, tmp_path / "out")
    vr.write_render_result(result, staging_dir)
    return staging_dir


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------

@requires_pandoc
def test_valid_render_passes(tmp_path):
    pkg = _build_synthetic_package(
        tmp_path, [("chunk-a", ["A"], "# A\n\nBody.\n", [])],
    )
    staging_dir = _staged_render(tmp_path, pkg)
    report = vr.validate_aspx_rendered_output(staging_dir, pkg)
    assert report.status == "PASS", report.issues


# ---------------------------------------------------------------------------
# Structural detections
# ---------------------------------------------------------------------------

@requires_pandoc
def test_missing_page_manifest_detected(tmp_path):
    pkg = _build_synthetic_package(
        tmp_path, [("chunk-a", ["A"], "# A\n\nBody.\n", [])],
    )
    staging_dir = _staged_render(tmp_path, pkg)
    (staging_dir / "page-manifest.json").unlink()

    report = vr.validate_aspx_rendered_output(staging_dir, pkg)
    assert report.status == "FAIL"
    assert any(i.code == "missing_page_manifest" for i in report.issues)


@requires_pandoc
def test_missing_pages_dir_detected(tmp_path):
    pkg = _build_synthetic_package(
        tmp_path, [("chunk-a", ["A"], "# A\n\nBody.\n", [])],
    )
    staging_dir = _staged_render(tmp_path, pkg)
    shutil.rmtree(staging_dir / "pages")

    report = vr.validate_aspx_rendered_output(staging_dir, pkg)
    assert report.status == "FAIL"
    assert any(i.code == "missing_pages_dir" for i in report.issues)


@requires_pandoc
def test_missing_page_file_detected(tmp_path):
    pkg = _build_synthetic_package(
        tmp_path,
        [
            ("chunk-a", ["A"], "# A\n\nBody.\n", []),
            ("chunk-b", ["B"], "# B\n\nBody.\n", []),
        ],
    )
    staging_dir = _staged_render(tmp_path, pkg)
    (staging_dir / "pages" / "chunk-b.html").unlink()

    report = vr.validate_aspx_rendered_output(staging_dir, pkg)
    assert report.status == "FAIL"
    assert any(i.code == "missing_page" for i in report.issues)


@requires_pandoc
def test_orphan_page_detected(tmp_path):
    pkg = _build_synthetic_package(
        tmp_path, [("chunk-a", ["A"], "# A\n\nBody.\n", [])],
    )
    staging_dir = _staged_render(tmp_path, pkg)
    (staging_dir / "pages" / "chunk-zzz.html").write_text("<p>orphan</p>")

    report = vr.validate_aspx_rendered_output(staging_dir, pkg)
    assert report.status == "FAIL"
    assert any(i.code == "orphan_page" for i in report.issues)


# ---------------------------------------------------------------------------
# Media / reference detections
# ---------------------------------------------------------------------------

@requires_pandoc
def test_broken_media_reference_detected(tmp_path):
    pkg = _build_synthetic_package(
        tmp_path,
        [("chunk-a", ["A"], "# A\n\n![alt](../media/diagram.png)\n", [])],
    )
    staging_dir = _staged_render(tmp_path, pkg)
    (staging_dir / "media" / "diagram.png").unlink()

    report = vr.validate_aspx_rendered_output(staging_dir, pkg)
    assert report.status == "FAIL"
    assert any(i.code == "broken_media_reference" for i in report.issues)


# ---------------------------------------------------------------------------
# Staleness / traceability
# ---------------------------------------------------------------------------

@requires_pandoc
def test_source_content_stale_detected(tmp_path):
    pkg = _build_synthetic_package(
        tmp_path, [("chunk-a", ["A"], "# A\n\nBody.\n", [])],
    )
    staging_dir = _staged_render(tmp_path, pkg)
    result_path = staging_dir / "render-result.json"
    data = json.loads(result_path.read_text(encoding="utf-8"))
    data["source_content_sha256"] = OTHER_SHA
    result_path.write_text(json.dumps(data))

    report = vr.validate_aspx_rendered_output(staging_dir, pkg)
    assert report.status == "FAIL"
    assert any(i.code == "source_content_stale" for i in report.issues)


@requires_pandoc
def test_tampered_page_content_not_traceable(tmp_path):
    pkg = _build_synthetic_package(
        tmp_path, [("chunk-a", ["A"], "# A\n\nBody.\n", [])],
    )
    staging_dir = _staged_render(tmp_path, pkg)
    page_path = staging_dir / "pages" / "chunk-a.html"
    page_path.write_text(page_path.read_text(encoding="utf-8") + "<p>tampered</p>")

    report = vr.validate_aspx_rendered_output(staging_dir, pkg)
    assert report.status == "FAIL"
    assert any(i.code == "page_content_not_traceable" for i in report.issues)


# ---------------------------------------------------------------------------
# render_and_promote_aspx
# ---------------------------------------------------------------------------

@requires_pandoc
def test_render_and_promote_aspx_promotes_on_pass(tmp_path):
    pkg = _build_synthetic_package(
        tmp_path, [("chunk-a", ["A"], "# A\n\nBody.\n", [])],
    )
    output_root = tmp_path / "out"
    result, report, promoted, final_dir = vr.render_and_promote_aspx(pkg, output_root)

    assert report.status == "PASS"
    assert promoted is True
    assert final_dir == output_root / "rendered-output"
    assert (final_dir / "page-manifest.json").exists()


@requires_pandoc
def test_render_and_promote_aspx_does_not_promote_on_fail(tmp_path, monkeypatch):
    pkg = _build_synthetic_package(
        tmp_path, [("chunk-a", ["A"], "# A\n\nBody.\n", [])],
    )
    output_root = tmp_path / "out"

    original = vr.validate_aspx_rendered_output

    def _always_fail(staging_dir, package):
        report = original(staging_dir, package)
        report.status = "FAIL"
        return report

    monkeypatch.setattr(vr, "validate_aspx_rendered_output", _always_fail)
    result, report, promoted, out_dir = vr.render_and_promote_aspx(pkg, output_root)

    assert promoted is False
    assert not (output_root / "rendered-output").exists()
    assert out_dir.exists()  # staging retained for diagnosis

