"""Shared validation helpers for this plugin's own contract module(s).

Plugin-local by design (Phase 4.5 Wave 2 correction, see
docs/superpowers/plans/phase-4-5-evidence/wave-2-contract-materialization-correction.md):
an independently installed plugin must carry every module its public API
needs, including its own contract types -- no plugin may declare a pip
dependency on another workbench distribution (contracts or runtime) to
function. Not part of the public API of this package -- imported by
normalized_source_document.py only."""
from __future__ import annotations

from typing import Any


def require(data: dict, field_name: str) -> Any:
    if field_name not in data:
        raise ValueError(f"missing required field: {field_name!r}")
    return data[field_name]


def check_schema_version(data: dict, expected_version: str, contract_name: str) -> str:
    version = require(data, "schema_version")
    if version != expected_version:
        raise ValueError(
            f"unsupported schema_version for {contract_name}: {version!r} "
            f"(supported: {expected_version!r})"
        )
    return version
