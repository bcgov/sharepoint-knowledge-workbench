"""Authoritative schema for the `normalized-source-document` contract.

`source-document-extraction` is the PRODUCER of this contract (per
docs/superpowers/plans/phase-4-5-evidence/wave-2-contract-materialization-correction.md)
-- this module is the single source of truth for its wire format, not a
generated copy. Human-readable documentation lives alongside it at
`references/contracts/normalized-source-document.md`.

Consumers (e.g. `knowledge-analysis`) do not import this module or declare
a pip dependency on this plugin. They validate the dict `extract_and_normalize`
returns against their own plugin-local copy of this same schema (`schema_version`
+ required-field check), generated/synced from this file during development
and checked for hash equivalence -- never imported across the plugin
boundary at runtime. See the correction doc for the generation/sync method.
"""
from __future__ import annotations

from ._shared import check_schema_version, require

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
