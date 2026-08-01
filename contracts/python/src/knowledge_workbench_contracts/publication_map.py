"""Schema for the `publication-map` contract — produced by
canonical-knowledge's build_canonical_package(), consumed by
knowledge-publication's render() (Wave 4/5 tables).

Corresponds to plugins/docx-to-content/scripts/contracts.py's
PublicationMapEntry/PublicationMap group. Minimal schema for Wave 1; full
field set finalized when Wave 4 implements build_canonical_package()."""
from __future__ import annotations

from ._shared import check_schema_version, require

SCHEMA_VERSION = "v1"

_REQUIRED_FIELDS = ("schema_version", "entries")


def validate(data: dict) -> None:
    check_schema_version(data, SCHEMA_VERSION, "publication-map")
    for field_name in _REQUIRED_FIELDS:
        require(data, field_name)
