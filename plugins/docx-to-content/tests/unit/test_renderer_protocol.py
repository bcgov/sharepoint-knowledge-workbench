"""
test_renderer_protocol.py
==========================

Tests for `renderers.protocol` (Task 12): the `Renderer` structural
protocol, the renderer registry, and the manifest-schema-version gate that
runs before any renderer's `render()` is invoked.

Also carries the brief's "renderer code has no DOCX/raw-analysis input"
structural test: proves at the *signature* level (not just by convention)
that `CanonicalPackage.load()` and `Renderer.render()` cannot accept a
source .docx path, an analysis directory, or a conversion plan.
"""

import inspect
import json
import shutil
from pathlib import Path

import pytest

import analyze_structure
import contracts
import convert
import package
import plans
from renderers import protocol

FIXTURES = Path(__file__).parent.parent / "fixtures"
SMALL_SINGLE_DOCX = FIXTURES / "small_single.docx"

PANDOC_AVAILABLE = shutil.which("pandoc") is not None


def _confirmed_plan(tmp_path):
    analysis_dir = tmp_path / "analysis"
    analyze_structure.analyze_document(SMALL_SINGLE_DOCX, analysis_dir)
    draft = contracts.ConversionPlan.from_dict(
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
    return final_dir


class _ListChunksTestRenderer:
    """Minimal fake renderer built only to prove the protocol shape works
    end to end. Writes a single file listing chunk IDs. Must only ever
    touch the `CanonicalPackage` object it is handed -- never
    sourcedocuments/, analysis/, or plan files directly."""

    name = "test-list-chunks"
    supported_manifest_versions = frozenset({contracts.SUPPORTED_SCHEMA_VERSION})

    def render(self, package_obj: "package.CanonicalPackage", output_dir: Path) -> contracts.RenderResult:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        listing_path = output_dir / "chunk-listing.txt"
        listing_path.write_text(
            "\n".join(chunk.metadata.chunk_id for chunk in package_obj.chunks)
        )
        return contracts.RenderResult(
            renderer_name=self.name,
            renderer_version="0.1.0",
            source_content_sha256=package_obj.manifest.source.sha256,
            output_files=[str(listing_path)],
            status="PASS",
            errors=[],
            warnings=[],
        )


def test_renderer_protocol_shape_is_structural_typing():
    # isinstance against a runtime_checkable Protocol only checks the
    # declared attribute/method names exist -- proving _ListChunksTestRenderer
    # satisfies Renderer without inheriting from it.
    renderer = _ListChunksTestRenderer()
    assert isinstance(renderer, protocol.Renderer)


def test_render_signature_has_no_docx_or_analysis_or_plan_parameter():
    sig = inspect.signature(protocol.Renderer.render)
    param_names = set(sig.parameters) - {"self"}
    assert param_names == {"package", "output_dir"}
    for forbidden in ("source", "docx", "analysis", "plan"):
        assert forbidden not in param_names


def test_canonical_package_load_signature_only_accepts_package_dir():
    sig = inspect.signature(package.CanonicalPackage.load)
    param_names = set(sig.parameters) - {"cls"}
    assert param_names == {"package_dir"}
    for forbidden in ("source", "docx", "analysis", "plan"):
        assert forbidden not in param_names


@pytest.mark.skipif(not PANDOC_AVAILABLE, reason="pandoc not available on PATH")
def test_registry_register_and_get_renderer_round_trip():
    registry = protocol.RendererRegistry()
    renderer = _ListChunksTestRenderer()
    registry.register(renderer)

    assert registry.get_renderer("test-list-chunks") is renderer


def test_registry_rejects_unknown_renderer_name():
    registry = protocol.RendererRegistry()
    with pytest.raises(protocol.UnknownRendererError):
        registry.get_renderer("does-not-exist")


@pytest.mark.skipif(not PANDOC_AVAILABLE, reason="pandoc not available on PATH")
def test_dispatch_render_end_to_end_with_test_renderer(tmp_path):
    final_dir = _accepted_package_dir(tmp_path)
    loaded = package.CanonicalPackage.load(final_dir)

    registry = protocol.RendererRegistry()
    renderer = _ListChunksTestRenderer()
    registry.register(renderer)

    output_dir = tmp_path / "rendered"
    result = protocol.dispatch_render(registry.get_renderer("test-list-chunks"), loaded, output_dir)

    assert isinstance(result, contracts.RenderResult)
    assert result.status == "PASS"
    assert (output_dir / "chunk-listing.txt").exists()
    listed_ids = (output_dir / "chunk-listing.txt").read_text().splitlines()
    assert listed_ids == [c.metadata.chunk_id for c in loaded.chunks]


@pytest.mark.skipif(not PANDOC_AVAILABLE, reason="pandoc not available on PATH")
def test_dispatch_render_rejects_unsupported_manifest_version(tmp_path):
    final_dir = _accepted_package_dir(tmp_path)
    loaded = package.CanonicalPackage.load(final_dir)

    class _FutureOnlyRenderer(_ListChunksTestRenderer):
        name = "future-only"
        supported_manifest_versions = frozenset({"2.0"})

    renderer = _FutureOnlyRenderer()
    with pytest.raises(protocol.UnsupportedManifestVersionError):
        protocol.dispatch_render(renderer, loaded, tmp_path / "out2")
