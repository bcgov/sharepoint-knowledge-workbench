"""Tests for inventory_validation.py -- stage 2 (discover-sharepoint-site-inventory),
scoped to its buildable half: validates/normalizes an already-produced export
directory's shape, preserving Lookup-field targets so stage 3a can build
dependsOn edges. No live-tenant I/O, no data fabrication."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from inventory_validation import validate_export_directory
from provisioning_outcomes import Outcome


def _write_inventory(export_dir: Path, data: dict) -> None:
    export_dir.mkdir(parents=True, exist_ok=True)
    (export_dir / "site-inventory.json").write_text(json.dumps(data))


class TestValidateExportDirectory:
    def test_missing_file_is_unavailable(self, tmp_path):
        result = validate_export_directory(tmp_path)
        assert result.outcome == Outcome.UNAVAILABLE
        assert any("site-inventory.json" in issue for issue in result.issues)

    def test_malformed_json_is_failed(self, tmp_path):
        tmp_path.mkdir(parents=True, exist_ok=True)
        (tmp_path / "site-inventory.json").write_text("{not valid json")
        result = validate_export_directory(tmp_path)
        assert result.outcome == Outcome.FAILED

    def test_missing_lists_key_is_failed(self, tmp_path):
        _write_inventory(tmp_path, {"foo": []})
        result = validate_export_directory(tmp_path)
        assert result.outcome == Outcome.FAILED
        assert any("lists" in issue for issue in result.issues)

    def test_empty_lists_is_empty_outcome(self, tmp_path):
        _write_inventory(tmp_path, {"lists": []})
        result = validate_export_directory(tmp_path)
        assert result.outcome == Outcome.EMPTY
        assert result.matrix_objects == ()

    def test_valid_export_produces_matrix_objects_with_lookup_dependency(self, tmp_path):
        _write_inventory(
            tmp_path,
            {
                "lists": [
                    {"name": "Customers", "fields": [{"name": "Title", "type": "Text"}]},
                    {
                        "name": "Orders",
                        "fields": [
                            {"name": "Title", "type": "Text"},
                            {"name": "CustomerLookup", "type": "Lookup", "lookupList": "Customers"},
                        ],
                    },
                ]
            },
        )
        result = validate_export_directory(tmp_path)
        assert result.outcome == Outcome.OBSERVED
        assert result.issues == ()
        by_name = {obj["name"]: obj for obj in result.matrix_objects}
        assert by_name["Customers"]["dependsOn"] == []
        assert by_name["Orders"]["dependsOn"] == ["Customers"]
        assert by_name["Orders"]["objectType"] == "List"

    def test_lookup_field_without_lookup_list_target_is_failed_not_fabricated(self, tmp_path):
        _write_inventory(
            tmp_path,
            {
                "lists": [
                    {
                        "name": "Orders",
                        "fields": [{"name": "CustomerLookup", "type": "Lookup"}],
                    }
                ]
            },
        )
        result = validate_export_directory(tmp_path)
        assert result.outcome == Outcome.FAILED
        assert any("lookupList" in issue for issue in result.issues)
        assert result.matrix_objects == ()

    def test_duplicate_list_name_is_failed(self, tmp_path):
        _write_inventory(
            tmp_path,
            {
                "lists": [
                    {"name": "Orders", "fields": []},
                    {"name": "Orders", "fields": []},
                ]
            },
        )
        result = validate_export_directory(tmp_path)
        assert result.outcome == Outcome.FAILED
        assert any("duplicate" in issue.lower() for issue in result.issues)

    def test_list_missing_fields_key_is_failed(self, tmp_path):
        _write_inventory(tmp_path, {"lists": [{"name": "Orders"}]})
        result = validate_export_directory(tmp_path)
        assert result.outcome == Outcome.FAILED
        assert any("fields" in issue for issue in result.issues)
