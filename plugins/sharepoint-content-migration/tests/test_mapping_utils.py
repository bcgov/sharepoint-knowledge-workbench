"""Tests for mapping_utils.py -- field name mapping and value coercion/transforms."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from mapping_utils import map_field_names, transform_item_values


class TestMapFieldNames:
    def test_maps_specified_fields(self):
        fields = {"OldCol": "Val1", "Unchanged": "Val2"}
        mapped = map_field_names(fields, {"OldCol": "NewCol"})
        assert mapped == {"NewCol": "Val1", "Unchanged": "Val2"}

    def test_empty_map_returns_copy(self):
        fields = {"Col1": "1", "Col2": "2"}
        mapped = map_field_names(fields, {})
        assert mapped == fields
        assert mapped is not fields


class TestTransformItemValues:
    def test_applies_transformations(self):
        fields = {"Amount": "100", "Title": "hello"}
        result = transform_item_values(
            fields,
            {"Amount": int, "Title": str.upper},
        )
        assert result == {"Amount": 100, "Title": "HELLO"}

    def test_ignores_missing_transforms(self):
        fields = {"ColA": "123"}
        result = transform_item_values(fields, {"ColB": int})
        assert result == {"ColA": "123"}
