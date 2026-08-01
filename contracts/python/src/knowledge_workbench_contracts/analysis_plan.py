"""Schema for the `analysis-plan` contract — produced by knowledge-analysis's
recommend_from_normalized(), consumed by canonical-knowledge's
build_canonical_package() (Wave 3/4 tables).

Corresponds to plugins/docx-to-content/scripts/contracts.py's
SourceFingerprint/ManifestSourceFingerprint/StructuralAnchor/Confirmation/
ConversionPlan group (see wave-1-shared-contract-decision.md's mapping
table). Minimal schema for Wave 1; full field set finalized when Wave 3
implements recommend_from_normalized()."""
from __future__ import annotations

from ._shared import check_schema_version, require

SCHEMA_VERSION = "v1"

_REQUIRED_FIELDS = ("schema_version", "plan_id", "strategy", "structural_anchors", "confirmation")


def validate(data: dict) -> None:
    check_schema_version(data, SCHEMA_VERSION, "analysis-plan")
    for field_name in _REQUIRED_FIELDS:
        require(data, field_name)
