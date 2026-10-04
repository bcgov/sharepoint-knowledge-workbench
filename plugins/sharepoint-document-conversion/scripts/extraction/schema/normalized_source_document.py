"""Authoritative schema for the `normalized-source-document` contract.

`source-document-extraction` is the sole producer of this contract -- this
module is the single source of truth for its wire format, packaged inside
this plugin so the plugin installs and runs standalone. Human-readable
documentation lives alongside it at
`references/extraction/contracts/normalized-source-document.md`.

Consumer plugins (e.g. `document-structure-analysis`) never import this module or
declare a dependency on this plugin. Each consumer validates the dict
`extraction.extract_and_normalize` returns against its own plugin-local
schema check (`schema_version` + required-field check) -- never across the
plugin boundary at runtime.
"""
from __future__ import annotations

from schema.shared import check_schema_version, require

SCHEMA_VERSION = "v1"

_REQUIRED_FIELDS = (
    "schema_version",
    "source_content_sha256",
    "markdown_text",
    "media_files",
    "source_path",
    "source_size_bytes",
    "dependencies",
    "headings",
    "heading_counts_by_level",
    "repeated_heading_texts",
    "repeated_heading_paths",
    "images",
    "raw_toc_detected",
    "defect_signals",
    "statistics",
)


def validate(data: dict) -> None:
    check_schema_version(data, SCHEMA_VERSION, "normalized-source-document")
    for field_name in _REQUIRED_FIELDS:
        require(data, field_name)
