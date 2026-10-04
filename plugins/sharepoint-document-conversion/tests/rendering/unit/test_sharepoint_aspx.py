"""
test_sharepoint_aspx.py
========================

Tests for `renderers.sharepoint_aspx` (Phase 6 Task 0.16): the second
concrete `Renderer`, producing SharePoint modern-page-ready artifacts
(HTML fragments + a page-manifest.json) rather than a raw `.aspx` file --
see `renderers/sharepoint_aspx.py`'s module docstring for why (Phase 3.0
Sec.15: raw `.aspx` upload is `Access denied`; `Add-PnPPage`/
`Add-PnPPageTextPart` is the confirmed working route).

Mirrors `test_multipage_markdown.py`'s synthetic-package-builder pattern
so these tests run fast and don't need a real .docx/pandoc extraction
pipeline -- only the renderer's own pandoc Markdown->HTML subprocess call
needs a real `pandoc` on PATH (skipped if unavailable).
"""

import dataclasses
import inspect
import json
import shutil
from pathlib import Path
from unittest import mock

import pytest

import atomic_output
import render_result as contracts
from canonical_schema import canonical_package as ck_contracts
from canonical_schema import publication_map as pm_contracts
import canonical_package as canonical_package_module
from renderers import protocol
from renderers import sharepoint_aspx as spx

PANDOC_AVAILABLE = shutil.which("pandoc") is not None
requires_pandoc = pytest.mark.skipif(not PANDOC_AVAILABLE, reason="pandoc not on PATH")

FAKE_SHA = "a" * 64


# ---------------------------------------------------------------------------
# Synthetic CanonicalPackage builder (same shape as test_multipage_markdown.py)
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


def _build_synthetic_grouped_package(tmp_path):
    pkg = _build_synthetic_package(
        tmp_path,
        [
            ("beta--11111111", ["Beta"], "# Beta\n\nBeta body.\n", []),
            ("alpha--22222222", ["Alpha"], "# Alpha\n\nAlpha body.\n", []),
        ],
    )
    pub_map = pm_contracts.PublicationMap(
        schema_version=pm_contracts.PUBLICATION_MAP_SCHEMA_VERSION,
        package_identity="sha256:deadbeef",
        entries=[
            pm_contracts.PublicationMapEntry(
                topic_id="alpha--22222222", title="Alpha", order=0,
                chunk_id="alpha--22222222",
            ),
            pm_contracts.PublicationMapEntry(
                topic_id="beta--11111111", title="Beta", order=1,
                chunk_id="beta--11111111",
            ),
        ],
    )
    grouped_manifest = dataclasses.replace(pkg.manifest, strategy="grouped")
    return dataclasses.replace(pkg, manifest=grouped_manifest, publication_map=pub_map)


# ---------------------------------------------------------------------------
# Protocol conformance
# ---------------------------------------------------------------------------

def test_renderer_satisfies_protocol():
    renderer = spx.SharePointAspxRenderer()
    assert isinstance(renderer, protocol.Renderer)
    assert renderer.name == "sharepoint-aspx"
    assert ck_contracts.MANIFEST_SCHEMA_VERSION in renderer.supported_manifest_versions


def test_render_signature_has_no_docx_or_plan_parameter():
    sig = inspect.signature(spx.SharePointAspxRenderer.render)
    params = list(sig.parameters)
    assert "docx" not in params and "plan" not in params
    assert params[:3] == ["self", "package", "output_dir"]


def test_module_never_imports_docx_or_analysis_modules():
    source = Path(spx.__file__).read_text(encoding="utf-8")
    for forbidden in ("import analyze_structure", "import plans", "import convert"):
        assert forbidden not in source


# ---------------------------------------------------------------------------
# Rendering (requires real pandoc)
# ---------------------------------------------------------------------------

@requires_pandoc
def test_single_chunk_renders_page_and_manifest(tmp_path):
    pkg = _build_synthetic_package(
        tmp_path,
        [("chunk-a", ["Getting Started"], "# Getting Started\n\nHello.\n", [])],
    )
    output_dir = tmp_path / "rendered"
    result = spx.SharePointAspxRenderer().render(pkg, output_dir)

    assert isinstance(result, contracts.RenderResult)
    assert result.status == "PASS"
    assert result.renderer_name == "sharepoint-aspx"
    assert result.source_content_sha256 == FAKE_SHA

    html_path = output_dir / "pages" / "chunk-a.html"
    assert html_path.exists()
    html = html_path.read_text(encoding="utf-8")
    assert "<h1" in html and "Getting Started" in html
    assert "<html" not in html and "<body" not in html  # fragment only

    manifest = json.loads((output_dir / "page-manifest.json").read_text(encoding="utf-8"))
    assert manifest["schema_version"] == "1.0"
    assert manifest["pages"] == [{
        "chunk_id": "chunk-a",
        "title": "Getting Started",
        "html_file": "pages/chunk-a.html",
        "media_refs": [],
    }]


@requires_pandoc
def test_media_copied_into_render_media_dir(tmp_path):
    pkg = _build_synthetic_package(
        tmp_path,
        [("chunk-a", ["Diagrams"], "# Diagrams\n\n![alt](../media/diagram.png)\n", [])],
    )
    output_dir = tmp_path / "rendered"
    spx.SharePointAspxRenderer().render(pkg, output_dir)

    assert (output_dir / "media" / "diagram.png").exists()
    assert (output_dir / "media" / "diagram.png").read_bytes() == b"fake-png-bytes"
    html = (output_dir / "pages" / "chunk-a.html").read_text(encoding="utf-8")
    assert "../media/diagram.png" in html


@requires_pandoc
def test_local_links_rewritten_to_html_not_md(tmp_path):
    pkg = _build_synthetic_package(
        tmp_path,
        [
            ("chunk-a", ["A"], "# A\n\nSee [B](chunks/chunk-b.md).\n", ["chunks/chunk-b.md"]),
            ("chunk-b", ["B"], "# B\n\nBody.\n", []),
        ],
    )
    output_dir = tmp_path / "rendered"
    spx.SharePointAspxRenderer().render(pkg, output_dir)

    html = (output_dir / "pages" / "chunk-a.html").read_text(encoding="utf-8")
    assert "chunk-b.html" in html
    assert "chunks/chunk-b.md" not in html


@requires_pandoc
def test_publication_map_order_overrides_manifest_order(tmp_path):
    pkg = _build_synthetic_grouped_package(tmp_path)
    output_dir = tmp_path / "rendered"
    spx.SharePointAspxRenderer().render(pkg, output_dir)

    manifest = json.loads((output_dir / "page-manifest.json").read_text(encoding="utf-8"))
    assert [p["chunk_id"] for p in manifest["pages"]] == [
        "alpha--22222222", "beta--11111111",
    ]


@requires_pandoc
def test_render_to_staging_leaves_output_unpromoted(tmp_path):
    pkg = _build_synthetic_package(
        tmp_path,
        [("chunk-a", ["A"], "# A\n\nBody.\n", [])],
    )
    output_root = tmp_path / "out"
    result, staging_dir = spx.render_to_staging(pkg, output_root)

    assert result.status == "PASS"
    assert staging_dir.exists()
    assert not (output_root / "rendered-output").exists()


# ---------------------------------------------------------------------------
# pandoc failure handling
# ---------------------------------------------------------------------------

def test_missing_pandoc_raises_conversion_error(tmp_path):
    pkg = _build_synthetic_package(
        tmp_path,
        [("chunk-a", ["A"], "# A\n\nBody.\n", [])],
    )
    output_dir = tmp_path / "rendered"
    with mock.patch("renderers.sharepoint_aspx.subprocess.run", side_effect=FileNotFoundError()):
        with pytest.raises(spx.PandocConversionError):
            spx.SharePointAspxRenderer().render(pkg, output_dir)

