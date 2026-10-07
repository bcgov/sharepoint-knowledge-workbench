"""Purpose:
    Shared validation helpers for this plugin's own schema module(s).

Key Input Dependencies:
    - typing

Shared validation helpers for this plugin's own schema module(s).

This plugin carries every module its public API needs, including its own
schema/validation code, so it installs and runs standalone with no
dependency on any other workbench package. Not part of this plugin's
public interface -- imported by analysis_plan.py only.

Named `plan_schema` rather than `schema` deliberately: `source-document-
extraction` already installs a top-level `schema` package, and both
plugins are `pip install -e`'d together in `docx-to-content`'s
compatibility-shim environment -- a bare `schema` name here would collide.
See docs/superpowers/plans/phase-4-5-evidence/wave-3-analysis-plan-split-decision.md.

Key Functions Index:
    - require()
    - check_schema_version()"""
from __future__ import annotations

from typing import Any


# Require the supplied value to be present in the supplied mapping.
def require(data: dict, field_name: str) -> Any:
    """Require the supplied value to be present in the supplied mapping."""
    if field_name not in data:
        raise ValueError(f"missing required field: {field_name!r}")
    return data[field_name]


# Require an analysis-plan schema mapping to declare the supported contract version.
def check_schema_version(data: dict, expected_version: str, contract_name: str) -> str:
    """Require an analysis-plan schema mapping to declare the supported contract version."""
    version = require(data, "schema_version")
    if version != expected_version:
        raise ValueError(
            f"unsupported schema_version for {contract_name}: {version!r} "
            f"(supported: {expected_version!r})"
        )
    return version
