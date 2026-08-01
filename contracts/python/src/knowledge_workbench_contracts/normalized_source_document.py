"""Schema for the `normalized-source-document` contract — produced by
source-document-extraction's extract_and_normalize(), consumed by
knowledge-analysis's recommend_from_normalized() (Wave 2/3 tables).

New contract, not lifted from an existing plugins/docx-to-content/scripts/
class — the monolithic plugin never separated "extracted, normalized
markdown" as its own artifact; that concept is introduced by Phase 4.5's
four-way split. Minimal schema for Wave 1; full field set finalized when
Wave 2 actually implements extract_and_normalize()."""
from __future__ import annotations

from ._shared import check_schema_version, require

SCHEMA_VERSION = "v1"

_REQUIRED_FIELDS = ("schema_version", "source_content_sha256", "markdown_text", "media_files")


def validate(data: dict) -> None:
    check_schema_version(data, SCHEMA_VERSION, "normalized-source-document")
    for field_name in _REQUIRED_FIELDS:
        require(data, field_name)
