"""Schema for the `rendered-output-profile` contract — produced by
knowledge-publication's render() (Wave 5 table).

Corresponds to plugins/docx-to-content/scripts/contracts.py's RenderResult.
Minimal schema for Wave 1; full field set finalized when Wave 5 implements
render()."""
from __future__ import annotations

from ._shared import check_schema_version, require

SCHEMA_VERSION = "v1"

_REQUIRED_FIELDS = ("schema_version", "renderer", "page_count", "source_content_sha256")


def validate(data: dict) -> None:
    check_schema_version(data, SCHEMA_VERSION, "rendered-output-profile")
    for field_name in _REQUIRED_FIELDS:
        require(data, field_name)
