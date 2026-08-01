"""Shared validation helpers, matching the pattern already established in
plugins/docx-to-content/scripts/contracts.py (_require/_check_schema_version).
Not part of the public API of this distribution — imported by the five
contract modules only."""
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
