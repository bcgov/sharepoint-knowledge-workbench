"""
test_independent_fixture.py
==============================

Phase 2, spec Section 5.3: proves the renderer and validators work against
a canonical package that was NEVER produced by running the real DOCX
pipeline -- constructed directly to match the documented contract shape.
This is necessary but, per the round-1 Opus review, insufficient alone: it
proves the shape is readable, not that corruption is caught (that's what
the mutation suites in Tasks 10-12 are for).
"""

import json
import base64
from pathlib import Path

import contracts
import hashing
import validate_canonical
import canonical_package as canonical_package_module
from renderers.multipage_markdown import MultipageMarkdownRenderer

# Compatibility shim (Phase 4.5 Wave 3, retire per wave-1-decisions.json):
# ConversionPlan/StructuralAnchor/SourceFingerprint/Confirmation and
# compute_plan_id now live in the installed `knowledge-analysis` package --
# see docs/superpowers/plans/phase-4-5-evidence/wave-3-analysis-plan-split-decision.md.
from plan_schema import analysis_plan as plan_contracts  # noqa: E402
import plan_hashing  # noqa: E402

# 1x1 transparent PNG (base64) -> bytes
_ONE_PX_PNG = base64.b64decode(
    b"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGNgYAAAAAMAASsJTYQAAAAASUVORK5CYII="
)

_FIXTURE_SOURCE_SHA256 = "2" * 64


def _build_fixture_plan() -> "plan_contracts.ConversionPlan":
    anchor = plan_contracts.StructuralAnchor(
        stable_key="intro--abc12345",
        heading_text="Introduction",
        heading_level=1,
        occurrence=1,
        source_heading_path=["Introduction"],
    )
    plan = plan_contracts.ConversionPlan(
        schema_version=plan_contracts.CONVERSION_PLAN_SCHEMA_VERSION,
        plan_id="",
        source=plan_contracts.SourceFingerprint(
            path="hand-authored", sha256=_FIXTURE_SOURCE_SHA256, size_bytes=0
        ),
        strategy="chunked",
        chunk_level=1,
        chunk_anchors=[anchor],
        content_type="manual",
        template_profile="source-structure-v1",
        confirmation=plan_contracts.Confirmation(
            status="confirmed",
            confirmed_by="fixture",
            confirmed_at="2026-01-01T00:00:00Z",
        ),
    )
    plan.plan_id = plan_hashing.compute_plan_id(plan)
    return plan


def _build_independent_fixture(tmp_path: Path) -> Path:
    package_dir = tmp_path / "independent-canonical-package"
    chunks_dir = package_dir / "chunks"
    media_dir = package_dir / "media"
    chunks_dir.mkdir(parents=True)
    media_dir.mkdir(parents=True)

    (media_dir / "diagram.png").write_bytes(_ONE_PX_PNG)

    chunk_content = (
        "# Introduction\n\n"
        "This is a hand-authored canonical chunk, never produced by the "
        "real DOCX conversion pipeline.\n\n"
        "![a small diagram](../media/diagram.png)\n"
    )
    (chunks_dir / "intro--abc12345.md").write_text(chunk_content)
    content_sha256 = hashing.content_hash(chunk_content.encode("utf-8"))

    plan = _build_fixture_plan()
    meta = contracts.ChunkMetadata(
        schema_version=contracts.CHUNK_METADATA_SCHEMA_VERSION,
        chunk_id="intro--abc12345",
        source_order=0,
        source_heading_path=["Introduction"],
        topic="Introduction",
        content_type="manual",
        template_profile="source-structure-v1",
        source_sha256=_FIXTURE_SOURCE_SHA256,
        plan_id=plan.plan_id,
        content_file="chunks/intro--abc12345.md",
        content_sha256=content_sha256,
        local_links=[],
        media_refs=["../media/diagram.png"],
    )
    (chunks_dir / "intro--abc12345.meta.json").write_text(json.dumps(meta.to_dict()))

    manifest = contracts.Manifest(
        schema_version=contracts.MANIFEST_SCHEMA_VERSION,
        generator=contracts.ManifestGenerator(plugin="hand-authored-fixture", plugin_version="0.1.0"),
        source=contracts.ManifestSourceFingerprint(path="hand-authored", sha256=_FIXTURE_SOURCE_SHA256),
        plan_id=plan.plan_id,
        content_type="manual",
        template_profile="source-structure-v1",
        strategy="chunked",
        chunk_count=1,
        chunks=[
            contracts.ManifestChunk(
                chunk_id="intro--abc12345",
                content_file="chunks/intro--abc12345.md",
                metadata_file="chunks/intro--abc12345.meta.json",
                source_order=0,
                source_heading_path=["Introduction"],
            )
        ],
        media=["diagram.png"],
        validation_report="validation.json",
    )
    (package_dir / "manifest.json").write_text(json.dumps(manifest.to_dict()))

    report = validate_canonical.validate_canonical_package(package_dir, plan, source_path=None)
    validate_canonical.write_validation_report(report, package_dir)
    assert report.status == "PASS", (
        f"fixture must be genuinely valid, not merely accepted by accident: {report.issues}"
    )

    return package_dir


def test_independent_fixture_loads_successfully(tmp_path):
    package_dir = _build_independent_fixture(tmp_path)
    package = canonical_package_module.CanonicalPackage.load(package_dir)
    assert package.manifest.chunk_count == 1
    assert package.chunks[0].metadata.chunk_id == "intro--abc12345"
    assert package.manifest.generator.plugin == "hand-authored-fixture"


def test_independent_fixture_renders_successfully_with_no_docx_side_code_invoked(tmp_path):
    package_dir = _build_independent_fixture(tmp_path)
    package = canonical_package_module.CanonicalPackage.load(package_dir)

    renderer = MultipageMarkdownRenderer()
    output_dir = tmp_path / "rendered-output"
    result = renderer.render(package, output_dir)

    assert result.status == "PASS"
    assert (output_dir / "index.md").exists()
    assert (output_dir / "pages" / "intro--abc12345.md").exists()
    assert (output_dir / "media" / "diagram.png").exists()
