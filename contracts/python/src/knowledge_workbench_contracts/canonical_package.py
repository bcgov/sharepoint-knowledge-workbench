"""Schema for the `canonical-package` contract — produced by
canonical-knowledge's build_canonical_package(), consumed by
knowledge-publication's render() (Wave 4/5 tables).

Corresponds to plugins/docx-to-content/scripts/contracts.py's
ChunkMetadata/ManifestChunk/ManifestGenerator/Manifest group, plus
ValidationIssue/ValidationReport (defined once here, imported by
rendered_output_profile.py rather than duplicated — see
wave-1-shared-contract-decision.md). Minimal schema for Wave 1; full
field set finalized when Wave 4 implements build_canonical_package()."""
from __future__ import annotations

from ._shared import check_schema_version, require

SCHEMA_VERSION = "v1"

_REQUIRED_FIELDS = ("schema_version", "package_identity", "chunks", "generator")


def validate(data: dict) -> None:
    check_schema_version(data, SCHEMA_VERSION, "canonical-package")
    for field_name in _REQUIRED_FIELDS:
        require(data, field_name)
