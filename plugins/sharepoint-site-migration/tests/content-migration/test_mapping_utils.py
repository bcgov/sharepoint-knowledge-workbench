"""Tests for mapping_utils.py -- field name mapping and value coercion/transforms.

Purpose:
    Verify field renaming and configured per-field value transformations.

Key Input Dependencies:
    - mapping_utils.py in the plugin's content-migration scripts directory.
    - In-memory field mappings and transformation callables supplied by tests.

Function Index:
    TestMapFieldNames.test_maps_specified_fields,
    TestMapFieldNames.test_empty_map_returns_copy,
    TestTransformItemValues.test_applies_transformations,
    TestTransformItemValues.test_ignores_missing_transforms
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts" / "content-migration"))

from mapping_utils import map_field_names, transform_item_values


class TestMapFieldNames:
    def test_maps_specified_fields(self):
        """Rename configured keys while preserving fields without a mapping."""
        fields = {"OldCol": "Val1", "Unchanged": "Val2"}
        mapped = map_field_names(fields, {"OldCol": "NewCol"})
        assert mapped == {"NewCol": "Val1", "Unchanged": "Val2"}

    def test_empty_map_returns_copy(self):
        """Return an equal but independent dictionary when no renames are configured."""
        fields = {"Col1": "1", "Col2": "2"}
        mapped = map_field_names(fields, {})
        assert mapped == fields
        assert mapped is not fields


class TestTransformItemValues:
    def test_applies_transformations(self):
        """Apply each configured converter to the corresponding field value."""
        fields = {"Amount": "100", "Title": "hello"}
        result = transform_item_values(
            fields,
            {"Amount": int, "Title": str.upper},
        )
        assert result == {"Amount": 100, "Title": "HELLO"}

    def test_ignores_missing_transforms(self):
        """Leave field values unchanged when transformations name absent fields."""
        fields = {"ColA": "123"}
        result = transform_item_values(fields, {"ColB": int})
        assert result == {"ColA": "123"}
