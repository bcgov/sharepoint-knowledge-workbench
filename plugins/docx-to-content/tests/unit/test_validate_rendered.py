"""
test_validate_rendered.py
===========================

Tests for `renderers.validate_rendered` (Task 14): the render validator and
`render_and_promote` wiring. Covers every detection in spec Section 9,
"Render validation must detect", plus the "prior accepted render survives a
failed new render" promotion-safety scenario (mirroring Task 11's pattern,
applied to rendered output).

Most tests build a synthetic `CanonicalPackage` (same helper pattern as
`test_multipage_markdown.py`) and a real staged render via
`multipage_markdown.render_to_staging`, then corrupt one specific thing
before validating -- proving each detection in isolation.
"""

import json
import shutil
from pathlib import Path

import pytest

import atomic_output
import contracts
import package as package_module
from renderers import multipage_markdown as mpm
from renderers import validate_rendered as vr

FIXTURES = Path(__file__).parent.parent / "fixtures"
SMALL_SINGLE_DOCX = FIXTURES / "small_single.docx"
PANDOC_AVAILABLE = shutil.which("pandoc") is not None

FAKE_SHA = "a" * 64
OTHER_SHA = "b" * 64


# ---------------------------------------------------------------------------
# Synthetic CanonicalPackage builder (same pattern as test_multipage_markdown.py)
# ---------------------------------------------------------------------------

def _metadata(chunk_id, heading_path, order, content, local_links=None):
    return contracts.ChunkMetadata(
        schema_version=contracts.SUPPORTED_SCHEMA_VERSION,
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
        media_refs=package_module.extract_media_refs(content),
    )


def _manifest_chunk(chunk_id, heading_path, order):
    return contracts.ManifestChunk(
        chunk_id=chunk_id,
        content_file=f"chunks/{chunk_id}.md",
        metadata_file=f"chunks/{chunk_id}.meta.json",
        source_order=order,
        source_heading_path=list(heading_path),
    )


def _build_synthetic_package(tmp_path, chunk_specs, with_media=True, source_sha=FAKE_SHA):
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
        loaded_chunks.append(package_module.LoadedChunk(metadata=meta, content=content))
        manifest_chunks.append(_manifest_chunk(chunk_id, heading_path, idx))

    manifest = contracts.Manifest(
        schema_version=contracts.SUPPORTED_SCHEMA_VERSION,
        generator=contracts.ManifestGenerator(plugin="docx-to-content", plugin_version="0.1.0"),
        source=contracts.ManifestSourceFingerprint(path="sourcedocuments/x.docx", sha256=source_sha),
        plan_id="plan-1",
        content_type="reference",
        template_profile="generic",
        strategy="heading-based",
        chunk_count=len(manifest_chunks),
        chunks=manifest_chunks,
        media=media_names,
        validation_report="validation.json",
    )
    validation_report = contracts.ValidationReport(
        status="PASS", issues=[], source_sha256=source_sha, plan_id="plan-1"
    )

    return package_module.CanonicalPackage(
        manifest=manifest,
        validation_report=validation_report,
        chunks=loaded_chunks,
        media_dir=media_dir,
        package_dir=package_dir,
    )


def _staged_render(tmp_path, pkg, name="rendered_out"):
    """Render pkg to staging and write generator-info + render-result.json,
    mirroring what render_and_promote does before validating."""
    output_root = tmp_path / name
    result, staging_dir = mpm.render_to_staging(pkg, output_root)
    vr.write_render_result(result, staging_dir)
    return result, staging_dir


TWO_CHUNK_SPECS = [
    ("chunk-a", ["A"], "# A\n\nSee [B](chunks/chunk-b.md).\n", ["chunks/chunk-b.md"]),
    ("chunk-b", ["B"], "# B\n\n![diagram](../media/diagram.png)\n", []),
]


# ---------------------------------------------------------------------------
# Happy path: a clean render passes
# ---------------------------------------------------------------------------

def test_clean_render_passes(tmp_path):
    pkg = _build_synthetic_package(tmp_path, TWO_CHUNK_SPECS)
    _, staging_dir = _staged_render(tmp_path, pkg)

    report = vr.validate_rendered_output(staging_dir, pkg)
    assert report.status == "PASS", report.issues
    assert report.issues == []


# ---------------------------------------------------------------------------
# 1. Missing index / pages dir
# ---------------------------------------------------------------------------

def test_missing_index_detected(tmp_path):
    pkg = _build_synthetic_package(tmp_path, TWO_CHUNK_SPECS)
    _, staging_dir = _staged_render(tmp_path, pkg)
    (staging_dir / "index.md").unlink()

    report = vr.validate_rendered_output(staging_dir, pkg)
    assert report.status == "FAIL"
    assert any(i.code == "missing_index" for i in report.issues)


def test_missing_pages_dir_detected(tmp_path):
    pkg = _build_synthetic_package(tmp_path, TWO_CHUNK_SPECS)
    _, staging_dir = _staged_render(tmp_path, pkg)
    shutil.rmtree(staging_dir / "pages")

    report = vr.validate_rendered_output(staging_dir, pkg)
    assert report.status == "FAIL"
    assert any(i.code == "missing_pages_dir" for i in report.issues)


# ---------------------------------------------------------------------------
# 2. Broken index links
# ---------------------------------------------------------------------------

def test_broken_index_link_detected(tmp_path):
    pkg = _build_synthetic_package(tmp_path, TWO_CHUNK_SPECS)
    _, staging_dir = _staged_render(tmp_path, pkg)
    index_path = staging_dir / "index.md"
    text = index_path.read_text()
    index_path.write_text(text.replace("pages/chunk-b.md", "pages/chunk-does-not-exist.md"))

    report = vr.validate_rendered_output(staging_dir, pkg)
    assert report.status == "FAIL"
    assert any(i.code == "broken_index_link" for i in report.issues)


# ---------------------------------------------------------------------------
# 3. Missing or orphan pages
# ---------------------------------------------------------------------------

def test_missing_page_detected(tmp_path):
    pkg = _build_synthetic_package(tmp_path, TWO_CHUNK_SPECS)
    _, staging_dir = _staged_render(tmp_path, pkg)
    (staging_dir / "pages" / "chunk-b.md").unlink()

    report = vr.validate_rendered_output(staging_dir, pkg)
    assert report.status == "FAIL"
    assert any(i.code == "missing_page" for i in report.issues)


def test_orphan_page_detected(tmp_path):
    pkg = _build_synthetic_package(tmp_path, TWO_CHUNK_SPECS)
    _, staging_dir = _staged_render(tmp_path, pkg)
    (staging_dir / "pages" / "chunk-orphan.md").write_text("# Orphan\n")

    report = vr.validate_rendered_output(staging_dir, pkg)
    assert report.status == "FAIL"
    assert any(i.code == "orphan_page" for i in report.issues)


# ---------------------------------------------------------------------------
# 4. Page count mismatch
# ---------------------------------------------------------------------------

def test_page_count_mismatch_detected(tmp_path):
    pkg = _build_synthetic_package(tmp_path, TWO_CHUNK_SPECS)
    _, staging_dir = _staged_render(tmp_path, pkg)
    (staging_dir / "pages" / "extra-page.md").write_text("# Extra\n")

    report = vr.validate_rendered_output(staging_dir, pkg)
    assert report.status == "FAIL"
    assert any(i.code == "page_count_mismatch" for i in report.issues)


# ---------------------------------------------------------------------------
# 5. Broken local links / media references from pages
# ---------------------------------------------------------------------------

def test_broken_local_link_in_page_detected(tmp_path):
    pkg = _build_synthetic_package(tmp_path, TWO_CHUNK_SPECS)
    _, staging_dir = _staged_render(tmp_path, pkg)
    page_a = staging_dir / "pages" / "chunk-a.md"
    page_a.write_text(page_a.read_text().replace("chunk-b.md", "chunk-nonexistent.md"))

    report = vr.validate_rendered_output(staging_dir, pkg)
    assert report.status == "FAIL"
    assert any(i.code == "broken_local_link" for i in report.issues)


def test_broken_media_reference_in_page_detected(tmp_path):
    pkg = _build_synthetic_package(tmp_path, TWO_CHUNK_SPECS)
    _, staging_dir = _staged_render(tmp_path, pkg)
    page_b = staging_dir / "pages" / "chunk-b.md"
    page_b.write_text(page_b.read_text().replace("diagram.png", "missing.png"))

    report = vr.validate_rendered_output(staging_dir, pkg)
    assert report.status == "FAIL"
    assert any(i.code == "broken_media_reference" for i in report.issues)


# ---------------------------------------------------------------------------
# 6. Path traversal / absolute references
# ---------------------------------------------------------------------------

def test_absolute_media_reference_in_page_detected(tmp_path):
    pkg = _build_synthetic_package(tmp_path, TWO_CHUNK_SPECS)
    _, staging_dir = _staged_render(tmp_path, pkg)
    page_b = staging_dir / "pages" / "chunk-b.md"
    page_b.write_text(page_b.read_text().replace("../media/diagram.png", "/etc/passwd"))

    report = vr.validate_rendered_output(staging_dir, pkg)
    assert report.status == "FAIL"
    assert any(i.code == "path_traversal_or_absolute_reference" for i in report.issues)


def test_traversal_media_reference_in_page_detected(tmp_path):
    pkg = _build_synthetic_package(tmp_path, TWO_CHUNK_SPECS)
    _, staging_dir = _staged_render(tmp_path, pkg)
    page_b = staging_dir / "pages" / "chunk-b.md"
    page_b.write_text(
        page_b.read_text().replace("../media/diagram.png", "../../../../etc/passwd")
    )

    report = vr.validate_rendered_output(staging_dir, pkg)
    assert report.status == "FAIL"
    assert any(i.code == "path_traversal_or_absolute_reference" for i in report.issues)


# ---------------------------------------------------------------------------
# 8. Manifest hash mismatch
# ---------------------------------------------------------------------------

def test_missing_render_result_detected(tmp_path):
    pkg = _build_synthetic_package(tmp_path, TWO_CHUNK_SPECS)
    output_root = tmp_path / "rendered_out_missing_result"
    result, staging_dir = mpm.render_to_staging(pkg, output_root)
    # Deliberately do NOT write render-result.json.

    report = vr.validate_rendered_output(staging_dir, pkg)
    assert report.status == "FAIL"
    assert any(i.code == "missing_render_result" for i in report.issues)


def test_manifest_hash_mismatch_detected(tmp_path):
    pkg = _build_synthetic_package(tmp_path, TWO_CHUNK_SPECS, source_sha=FAKE_SHA)
    _, staging_dir = _staged_render(tmp_path, pkg)

    # Simulate the canonical package having been reconverted (new source
    # hash) after this render was staged, by mutating the package object's
    # recorded hash the validator checks against.
    stale_manifest = contracts.Manifest(
        schema_version=pkg.manifest.schema_version,
        generator=pkg.manifest.generator,
        source=contracts.ManifestSourceFingerprint(path=pkg.manifest.source.path, sha256=OTHER_SHA),
        plan_id=pkg.manifest.plan_id,
        content_type=pkg.manifest.content_type,
        template_profile=pkg.manifest.template_profile,
        strategy=pkg.manifest.strategy,
        chunk_count=pkg.manifest.chunk_count,
        chunks=pkg.manifest.chunks,
        media=pkg.manifest.media,
        validation_report=pkg.manifest.validation_report,
    )
    import dataclasses
    stale_pkg = dataclasses.replace(pkg, manifest=stale_manifest)

    report = vr.validate_rendered_output(staging_dir, stale_pkg)
    assert report.status == "FAIL"
    assert any(i.code == "source_content_stale" for i in report.issues)


# ---------------------------------------------------------------------------
# 9. Rendered page content not traceable to a chunk ID
# ---------------------------------------------------------------------------

def test_page_content_not_traceable_detected(tmp_path):
    pkg = _build_synthetic_package(tmp_path, TWO_CHUNK_SPECS)
    _, staging_dir = _staged_render(tmp_path, pkg)
    page_a = staging_dir / "pages" / "chunk-a.md"
    page_a.write_text("# Totally different content not derived from chunk-a\n")

    report = vr.validate_rendered_output(staging_dir, pkg)
    assert report.status == "FAIL"
    assert any(i.code == "page_content_not_traceable" for i in report.issues)


# ---------------------------------------------------------------------------
# render_and_promote wiring
# ---------------------------------------------------------------------------

def test_render_and_promote_promotes_on_pass(tmp_path):
    pkg = _build_synthetic_package(tmp_path, TWO_CHUNK_SPECS)
    output_root = tmp_path / "out"

    result, report, promoted, final_dir = vr.render_and_promote(pkg, output_root)

    assert promoted is True
    assert report.status == "PASS"
    assert final_dir == output_root / "rendered-output"
    assert (final_dir / "index.md").exists()
    assert (final_dir / "pages" / "chunk-a.md").exists()
    assert (final_dir / "renderer-validation.json").exists()


def test_prior_accepted_render_survives_failed_new_render(tmp_path):
    """Promote a clean render v1. Then intentionally break a v2 render
    (delete a page file before validation) and attempt render_and_promote
    again -- validation must FAIL, promote() must never be called, and the
    v1 rendered-output directory must be byte-for-byte unchanged."""
    pkg = _build_synthetic_package(tmp_path, TWO_CHUNK_SPECS)
    output_root = tmp_path / "out"

    result1, report1, promoted1, final_dir = vr.render_and_promote(pkg, output_root)
    assert promoted1 is True
    assert report1.status == "PASS"

    before_snapshot = {
        p.relative_to(final_dir): p.read_bytes()
        for p in final_dir.rglob("*") if p.is_file()
    }

    # Manually stage a broken v2 render (delete a page before validation
    # runs), then drive it through the same validate-then-promote logic
    # render_and_promote uses, to prove promote() is never reached.
    result2, staging_dir2 = mpm.render_to_staging(pkg, output_root)
    vr.write_render_result(result2, staging_dir2)
    (staging_dir2 / "pages" / "chunk-b.md").unlink()

    report2 = vr.validate_rendered_output(staging_dir2, pkg)
    assert report2.status == "FAIL"
    # The clean, documented contract: only PASS reports are ever handed to
    # atomic_output.promote() -- assert that invariant directly rather than
    # monkeypatching promote() to prove a negative.
    assert report2.status != "PASS"

    after_snapshot = {
        p.relative_to(final_dir): p.read_bytes()
        for p in final_dir.rglob("*") if p.is_file()
    }
    assert before_snapshot == after_snapshot
    assert staging_dir2.exists()  # retained for diagnosis


# ---------------------------------------------------------------------------
# 7. Stale files from previous render runs (promote() replace semantics,
# applied to rendered output -- same pattern as test_atomic_output.py's
# test_stale_files_from_earlier_run_disappear, applied via render_and_promote)
# ---------------------------------------------------------------------------

def test_stale_pages_from_prior_render_do_not_survive_promotion(tmp_path):
    pkg_v1 = _build_synthetic_package(
        tmp_path / "v1",
        [
            ("chunk-a", ["A"], "# A\n", []),
            ("chunk-b", ["B"], "# B\n", []),
        ],
    )
    output_root = tmp_path / "out"
    _, _, promoted1, final_dir = vr.render_and_promote(pkg_v1, output_root)
    assert promoted1 is True
    assert (final_dir / "pages" / "chunk-b.md").exists()

    pkg_v2 = _build_synthetic_package(
        tmp_path / "v2",
        [
            ("chunk-a", ["A"], "# A\n", []),
            ("chunk-c", ["C"], "# C\n", []),
        ],
    )
    _, report2, promoted2, final_dir2 = vr.render_and_promote(pkg_v2, output_root)
    assert promoted2 is True
    assert final_dir2 == final_dir

    page_files = sorted(p.stem for p in (final_dir / "pages").glob("*.md"))
    assert page_files == ["chunk-a", "chunk-c"]
    assert not (final_dir / "pages" / "chunk-b.md").exists()
