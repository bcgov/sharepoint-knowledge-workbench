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

The full-pipeline end-to-end tests (using analyze_structure/convert/plans
to build a real accepted package) moved to docx-to-content's
tests/unit/test_renderer_protocol_integration.py (Phase 4.5 Wave 5): those
modules are not installable dependencies of this plugin -- see
docs/superpowers/plans/phase-4-5-evidence/wave-5-structured-content-rendering-split-decision.md.
"""

import inspect
from pathlib import Path

import pytest

import render_result as contracts
import canonical_package
from renderers import protocol


class _ListChunksTestRenderer:
    """Minimal fake renderer built only to prove the protocol shape works
    end to end. Writes a single file listing chunk IDs. Must only ever
    touch the `CanonicalPackage` object it is handed -- never
    sourcedocuments/, analysis/, or plan files directly."""

    name = "test-list-chunks"
    supported_manifest_versions = frozenset({contracts.SUPPORTED_SCHEMA_VERSION})

    def render(self, package_obj: "canonical_package.CanonicalPackage", output_dir: Path) -> contracts.RenderResult:
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
    sig = inspect.signature(canonical_package.CanonicalPackage.load)
    param_names = set(sig.parameters) - {"cls"}
    assert param_names == {"package_dir"}
    for forbidden in ("source", "docx", "analysis", "plan"):
        assert forbidden not in param_names


def test_registry_register_and_get_renderer_round_trip():
    registry = protocol.RendererRegistry()
    renderer = _ListChunksTestRenderer()
    registry.register(renderer)

    assert registry.get_renderer("test-list-chunks") is renderer


def test_registry_rejects_unknown_renderer_name():
    registry = protocol.RendererRegistry()
    with pytest.raises(protocol.UnknownRendererError):
        registry.get_renderer("does-not-exist")
