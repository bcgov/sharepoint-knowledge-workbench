"""
contracts.py
============

Versioned data contracts shared across the docx-to-content plugin's
render pipeline. These are plain stdlib dataclasses (no pydantic/third-
party validation deps) with strict `from_dict`/`to_dict` round-tripping,
matching the JSON shapes in
docs/superpowers/specs/2026-07-25-docx-to-content-plugin-design-v3-ammendments.md
section 8 (Renderer Protocol).

SourceFingerprint/StructuralAnchor/Confirmation/ConversionPlan moved to
knowledge-analysis's plan_schema/analysis_plan.py (Phase 4.5 Wave 3).
ManifestSourceFingerprint/ChunkMetadata/ManifestChunk/ManifestGenerator/
Manifest/ValidationIssue/ValidationReport/PublicationMapEntry/
PublicationMap moved to canonical-knowledge's canonical_schema/ (Phase
4.5 Wave 4) -- see
docs/superpowers/plans/phase-4-5-evidence/wave-4-canonical-knowledge-split-decision.md.
Only `RenderResult` (knowledge-publication's future contract, Wave 5,
unmoved for now) remains here.

Design rules enforced here:
- Every `from_dict` rejects a dict missing any required field (no silent
  defaulting) via `_require`.
- `to_dict` always returns plain dicts/lists/str/int/None.
"""

from dataclasses import dataclass
from typing import Any


MANIFEST_SCHEMA_VERSION = "1.0"

# Backward-compatible alias: pre-Phase-2 code (and any external caller)
# that referenced one shared SUPPORTED_SCHEMA_VERSION still resolves to a
# valid value. Anchors to MANIFEST_SCHEMA_VERSION since every remaining
# caller of this alias tests Manifest/renderer schema versions.
SUPPORTED_SCHEMA_VERSION = MANIFEST_SCHEMA_VERSION


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
