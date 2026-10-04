"""
mapping_utils.py
================

Purpose:
    Core utility functions for mapping item field names and transforming/coercing
    field values across source and target schemas during SharePoint migration passes.

Layer: sharepoint-site-migration / mapping utilities
"for utils"

"""

from __future__ import annotations

from typing import Any, Callable, Mapping


def map_field_names(
    item_fields: Mapping[str, Any], field_name_map: Mapping[str, str]
) -> dict[str, Any]:
    """Map source field names to target field names based on field_name_map.
    Unmapped fields are retained unchanged."""
    mapped: dict[str, Any] = {}
    for k, v in item_fields.items():
        target_name = field_name_map.get(k, k)
        mapped[target_name] = v
    return mapped



def transform_item_values(
    item_fields: Mapping[str, Any],
    transforms: Mapping[str, Callable[[Any], Any]] | None = None,
) -> dict[str, Any]:
    """Apply transformation functions to specific fields.
    Each transform is a callable taking old value and returning new value."""
    result = dict(item_fields)
    if not transforms:
        return result
    for field, func in transforms.items():
        if field in result and callable(func):
            result[field] = func(result[field])
    return result
