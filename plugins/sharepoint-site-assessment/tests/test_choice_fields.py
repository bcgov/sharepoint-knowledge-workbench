"""
test_choice_fields.py -- contract tests for Choice/MultiChoice field inventory.

Purpose:
    Prove the choice-field inventory is derived from an offline schema export
    (no live tenant call, no hardcoded list names), that the field-group filter
    is a caller parameter with no project-specific default, and that fields
    whose option set is absent are reported as unknown rather than as empty.

Layer: sharepoint-schema / plugin-local tests

Key Input Dependencies:
    - choice_fields, schema_export (modules under test)
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from choice_fields import inventory_choice_fields, to_overrides_mapping  # noqa: E402
from schema_export import SectionStatus, load_schema_export  # noqa: E402


def _load(tmp_path, name, list_fields):
    root = tmp_path / name
    for list_name, fields in list_fields.items():
        path = root / "lists" / list_name / "fields.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(fields), encoding="utf-8")
    return load_schema_export(root, label=name)


def test_inventories_choice_and_multichoice_fields(tmp_path):
    inventory = inventory_choice_fields(_load(tmp_path, "a", {
        "Records": [
            {"InternalName": "status", "TypeAsString": "Choice", "Choices": ["Open", "Closed"]},
            {"InternalName": "tags", "TypeAsString": "MultiChoice", "Choices": ["X"]},
            {"InternalName": "note", "TypeAsString": "Text"},
        ]
    }))
    assert [f.internal_name for f in inventory.fields] == ["status", "tags"]
    assert inventory.fields[0].choices == ("Open", "Closed")
    assert inventory.status is SectionStatus.OBSERVED


def test_odata_results_envelope_for_choices_is_supported(tmp_path):
    inventory = inventory_choice_fields(_load(tmp_path, "b", {
        "Records": [{"InternalName": "status", "TypeAsString": "Choice",
                     "Choices": {"results": ["Open"]}}]
    }))
    assert inventory.fields[0].choices == ("Open",)


def test_field_without_a_choices_property_is_reported_unknown_not_empty(tmp_path):
    inventory = inventory_choice_fields(_load(tmp_path, "c", {
        "Records": [{"InternalName": "status", "TypeAsString": "Choice"}]
    }))
    assert inventory.fields[0].choices_known is False
    assert inventory.fields[0].choices == ()
    assert inventory.ambiguities
    assert inventory.status is SectionStatus.PARTIAL


def test_empty_choice_list_is_distinct_from_unknown(tmp_path):
    inventory = inventory_choice_fields(_load(tmp_path, "d", {
        "Records": [{"InternalName": "status", "TypeAsString": "Choice", "Choices": []}]
    }))
    assert inventory.fields[0].choices_known is True
    assert inventory.fields[0].choices == ()


def test_group_filter_is_opt_in_with_no_default(tmp_path):
    export = _load(tmp_path, "e", {
        "Records": [
            {"InternalName": "a", "TypeAsString": "Choice", "Choices": ["1"], "Group": "Custom Columns"},
            {"InternalName": "b", "TypeAsString": "Choice", "Choices": ["2"], "Group": "Core Document Columns"},
        ]
    })
    assert len(inventory_choice_fields(export).fields) == 2
    filtered = inventory_choice_fields(export, group="Custom Columns")
    assert [f.internal_name for f in filtered.fields] == ["a"]


def test_overrides_mapping_is_keyed_by_list_and_internal_name(tmp_path):
    inventory = inventory_choice_fields(_load(tmp_path, "f", {
        "Records": [{"InternalName": "status", "TypeAsString": "Choice", "Choices": ["Open"]}]
    }))
    assert to_overrides_mapping(inventory) == {"lists/Records.status": ["Open"]}


def test_overrides_mapping_omits_unknown_option_sets(tmp_path):
    inventory = inventory_choice_fields(_load(tmp_path, "g", {
        "Records": [{"InternalName": "status", "TypeAsString": "Choice"}]
    }))
    assert to_overrides_mapping(inventory) == {}


def test_missing_export_is_unavailable_not_an_empty_success(tmp_path):
    inventory = inventory_choice_fields(load_schema_export(tmp_path / "none", label="none"))
    assert inventory.status is SectionStatus.UNAVAILABLE
    assert inventory.fields == ()


def test_no_choice_fields_present_is_empty(tmp_path):
    inventory = inventory_choice_fields(_load(tmp_path, "h", {
        "Records": [{"InternalName": "note", "TypeAsString": "Text"}]
    }))
    assert inventory.status is SectionStatus.EMPTY
