"""
test_contracts.py
==================

Contract tests for docx-to-content's own remaining local contract:
RenderResult (see docs/superpowers/specs/2026-07-25-docx-to-content-plugin-design-v3-ammendments.md
section 8), plus the SUPPORTED_SCHEMA_VERSION constant.

ChunkMetadata/ManifestChunk/Manifest/ValidationIssue/ValidationReport and
canonical-JSON hashing moved to canonical-knowledge's own contract test
suite (tests/contract/test_canonical_package_contract.py) in Phase 4.5
Wave 4 -- see
docs/superpowers/plans/phase-4-5-evidence/wave-4-canonical-knowledge-split-decision.md.

SourceFingerprint/StructuralAnchor/ConversionPlan/Confirmation and
compute_plan_id moved to knowledge-analysis's own contract test suite
(tests/contract/test_analysis_plan_contract.py) in Phase 4.5 Wave 3 -- see
docs/superpowers/plans/phase-4-5-evidence/wave-3-analysis-plan-split-decision.md.
"""

import pytest

from contracts import RenderResult, SUPPORTED_SCHEMA_VERSION


def test_supported_schema_version_constant():
    assert SUPPORTED_SCHEMA_VERSION == "1.0"


def test_render_result_uses_source_content_sha256_not_manifest_hash():
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
    def test_round_trip(self):
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

    def test_missing_required_field_raises(self):
        data = {
            "renderer_name": "multipage-markdown",
            "renderer_version": "0.1.0",
            "source_content_sha256": "sha256:" + "0" * 64,
            "output_files": [],
            "status": "PASS",
        }
        with pytest.raises(ValueError):
            RenderResult.from_dict(data)
