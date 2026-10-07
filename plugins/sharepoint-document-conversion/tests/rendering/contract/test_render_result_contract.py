"""test_render_result_contract.py
================================

Purpose:
    Contract tests for this plugin's own produced contract: RenderResult (see docs/superpowers/specs/2026-07-25-docx-to-content-plugin-design-v3-ammendments.md section 8), plus the SUPPORTED_SCHEMA_VERSION constant.

Key Input Dependencies:
    - pytest and the plugin-local tests in this namespace
    - pytest
    - render_result

Contract tests for this plugin's own produced contract: RenderResult (see
docs/superpowers/specs/2026-07-25-docx-to-content-plugin-design-v3-ammendments.md
section 8), plus the SUPPORTED_SCHEMA_VERSION constant.

Moved wholesale from docx-to-content's tests/contract/test_contracts.py in
Phase 4.5 Wave 5 -- see
docs/superpowers/plans/phase-4-5-evidence/wave-5-structured-content-rendering-split-decision.md.

Key Functions Index:
    - test_supported_schema_version_constant()
    - test_render_result_uses_source_content_sha256_not_manifest_hash()
    - TestRenderResult.test_round_trip()
    - TestRenderResult.test_missing_required_field_raises()"""

import pytest

from render_result import RenderResult, SUPPORTED_SCHEMA_VERSION


# Verify supported schema version constant.
def test_supported_schema_version_constant():
    """Verify supported schema version constant."""
    assert SUPPORTED_SCHEMA_VERSION == "1.0"


# Verify render result uses source content SHA-256 not manifest hash.
def test_render_result_uses_source_content_sha256_not_manifest_hash():
    """Verify render result uses source content SHA-256 not manifest hash."""
    data = {
        "renderer_name": "multipage-markdown",
        "renderer_version": "0.1.0",
        "source_content_sha256": "a" * 64,
        "output_files": [],
        "status": "PASS",
        "errors": [],
        "warnings": [],
    }
    result = RenderResult.from_dict(data)
    assert result.source_content_sha256 == "a" * 64
    assert result.to_dict() == data


class TestRenderResult:
    # Verify round trip.
    def test_round_trip(self):
        """Verify round trip."""
        data = {
            "renderer_name": "multipage-markdown",
            "renderer_version": "0.1.0",
            "source_content_sha256": "sha256:" + "0" * 64,
            "output_files": ["index.md", "file-access--a1b2c3d4.md"],
            "status": "PASS",
            "errors": [],
            "warnings": [],
        }
        result = RenderResult.from_dict(data)
        assert result.to_dict() == data

    # Verify missing required field raises.
    def test_missing_required_field_raises(self):
        """Verify missing required field raises."""
        data = {
            "renderer_name": "multipage-markdown",
            "renderer_version": "0.1.0",
            "source_content_sha256": "sha256:" + "0" * 64,
            "output_files": [],
            "status": "PASS",
        }
        with pytest.raises(ValueError):
            RenderResult.from_dict(data)
