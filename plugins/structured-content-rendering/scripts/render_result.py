"""
render_result.py
=================

Authoritative schema for the `rendered-output-profile` contract's
`RenderResult` type (see
docs/superpowers/specs/2026-07-25-docx-to-content-plugin-design-v3-ammendments.md
section 8, Renderer Protocol). `structured-content-rendering` is the sole
producer of this contract.

Renamed from docx-to-content's `contracts.py` (Phase 4.5 Wave 5) --
SourceFingerprint/StructuralAnchor/Confirmation/ConversionPlan moved to
document-structure-analysis's plan_schema/analysis_plan.py (Wave 3);
ManifestSourceFingerprint/ChunkMetadata/ManifestChunk/ManifestGenerator/
Manifest/ValidationIssue/ValidationReport/PublicationMapEntry/
PublicationMap moved to structured-content-assembly's canonical_schema/ (Wave 4).
See
docs/superpowers/plans/phase-4-5-evidence/wave-5-structured-content-rendering-split-decision.md.

Design rules enforced here:
- Every `from_dict` rejects a dict missing any required field (no silent
  defaulting) via `_require`.
- `to_dict` always returns plain dicts/lists/str/int/None.
"""

from dataclasses import dataclass
from typing import Any


RENDER_RESULT_SCHEMA_VERSION = "1.0"

# Backward-compatible alias: pre-Phase-2 code (and any external caller)
# that referenced one shared SUPPORTED_SCHEMA_VERSION still resolves to a
# valid value.
SUPPORTED_SCHEMA_VERSION = RENDER_RESULT_SCHEMA_VERSION


def _require(data: dict, field_name: str) -> Any:
    if field_name not in data:
        raise ValueError(f"missing required field: {field_name!r}")
    return data[field_name]


# ---------------------------------------------------------------------------
# Section 8 — RenderResult
# ---------------------------------------------------------------------------

@dataclass
class RenderResult:
    renderer_name: str
    renderer_version: str
    source_content_sha256: str
    output_files: list
    status: str  # "PASS" | "WARN" | "FAIL"
    errors: list
    warnings: list

    @classmethod
    def from_dict(cls, data: dict) -> "RenderResult":
        return cls(
            renderer_name=_require(data, "renderer_name"),
            renderer_version=_require(data, "renderer_version"),
            source_content_sha256=_require(data, "source_content_sha256"),
            output_files=list(_require(data, "output_files")),
            status=_require(data, "status"),
            errors=list(_require(data, "errors")),
            warnings=list(_require(data, "warnings")),
        )

    def to_dict(self) -> dict:
        return {
            "renderer_name": self.renderer_name,
            "renderer_version": self.renderer_version,
            "source_content_sha256": self.source_content_sha256,
            "output_files": list(self.output_files),
            "status": self.status,
            "errors": list(self.errors),
            "warnings": list(self.warnings),
        }
