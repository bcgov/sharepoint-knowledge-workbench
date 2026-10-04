"""Tests for field_provisioning.py -- deployable-field filtering, type-repair
detection, raw Field XML construction (the Add-PnPField -Formula workaround),
and per-field create/exist/repair planning. Real dataclasses, no mocks."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts" / "schema-reconciliation"))

import pytest

from field_provisioning import (
    FieldDef,
    FieldDefinitionError,
    build_calculated_field_xml,
    build_lookup_field_xml,
    build_user_field_xml,
    field_needs_type_repair,
    filter_deployable_fields,
    plan_field_action,
)


# ---------------------------------------------------------------------------
# filter_deployable_fields
# ---------------------------------------------------------------------------

def _raw_field(**overrides):
    base = {
        "InternalName": "Widget_Count",
        "Title": "Widget Count",
        "TypeAsString": "Number",
        "Group": "Custom Columns",
        "Hidden": False,
        "ReadOnlyField": False,
    }
    base.update(overrides)
    return base


def test_filter_deployable_fields_keeps_visible_writable_custom_field():
    fields = [_raw_field()]
    result = filter_deployable_fields(fields)
    assert len(result) == 1
    assert result[0]["InternalName"] == "Widget_Count"


def test_filter_deployable_fields_excludes_non_custom_group():
    fields = [_raw_field(Group="Core Contact and Calendar Columns")]
    assert filter_deployable_fields(fields) == []


def test_filter_deployable_fields_excludes_skip_types():
    fields = [_raw_field(TypeAsString="Calculated")]
    assert filter_deployable_fields(fields) == []


def test_filter_deployable_fields_excludes_title():
    fields = [_raw_field(InternalName="Title")]
    assert filter_deployable_fields(fields) == []


def test_filter_deployable_fields_excludes_hidden_by_default():
    fields = [_raw_field(Hidden=True)]
    assert filter_deployable_fields(fields) == []


def test_filter_deployable_fields_excludes_readonly_by_default():
    fields = [_raw_field(ReadOnlyField=True)]
    assert filter_deployable_fields(fields) == []


def test_filter_deployable_fields_force_include_overrides_hidden_readonly():
    fields = [_raw_field(Hidden=True, ReadOnlyField=True)]
    result = filter_deployable_fields(fields, force_include_names=["Widget_Count"])
    assert len(result) == 1


def test_filter_deployable_fields_explicit_exclude_names_wins():
    fields = [_raw_field()]
    result = filter_deployable_fields(fields, exclude_names=["Widget_Count"])
    assert result == []


# ---------------------------------------------------------------------------
# field_needs_type_repair
# ---------------------------------------------------------------------------

def test_field_needs_type_repair_true_on_mismatch():
    assert field_needs_type_repair("Text", "Number") is True


def test_field_needs_type_repair_false_on_match():
    assert field_needs_type_repair("Number", "Number") is False


def test_field_needs_type_repair_false_when_no_current_field():
    assert field_needs_type_repair(None, "Number") is False


# ---------------------------------------------------------------------------
# calculated-column raw Field XML construction (the non-obvious technique)
# ---------------------------------------------------------------------------

def test_build_calculated_field_xml_happy_path():
    fd = FieldDef(
        internal_name="Full_Label",
        display_name="Full Label",
        type="Calculated",
        formula="=[Prefix]&\" \"&[Suffix]",
        result_type="Text",
        field_refs=("Prefix", "Suffix"),
        group="Demo Columns",
    )
    xml = build_calculated_field_xml(fd, field_id="11111111-2222-3333-4444-555555555555")
    assert xml.startswith("<Field ")
    assert "Type='Calculated'" in xml
    assert "ReadOnly='TRUE'" in xml
    assert "ID='{11111111-2222-3333-4444-555555555555}'" in xml
    assert "StaticName='Full_Label'" in xml
    assert "<FieldRef Name='Prefix'/>" in xml
    assert "<FieldRef Name='Suffix'/>" in xml
    assert "<Formula>" in xml and "</Formula>" in xml


def test_build_calculated_field_xml_requires_formula():
    fd = FieldDef(internal_name="X", display_name="X", type="Calculated")
    with pytest.raises(FieldDefinitionError):
        build_calculated_field_xml(fd, field_id="abc")


def test_build_calculated_field_xml_rejects_non_calculated_type():
    fd = FieldDef(internal_name="X", display_name="X", type="Text", formula="=1")
    with pytest.raises(FieldDefinitionError):
        build_calculated_field_xml(fd, field_id="abc")


def test_build_calculated_field_xml_escapes_ampersand_lt_gt_in_display_name():
    fd = FieldDef(
        internal_name="X",
        display_name='Widgets & "Gadgets" <Beta>',
        type="Calculated",
        formula="=1",
    )
    xml = build_calculated_field_xml(fd, field_id="abc")
    assert 'DisplayName=' in xml
    assert "&amp;" in xml
    assert "&quot;" in xml
    assert "&lt;Beta&gt;" in xml
    # raw unescaped characters must never survive into the XML
    assert "Widgets & " not in xml
    assert '"Gadgets"' not in xml


def test_build_calculated_field_xml_escapes_formula_body():
    fd = FieldDef(
        internal_name="X",
        display_name="X",
        type="Calculated",
        formula="=[A]<[B]&[C]>0",
    )
    xml = build_calculated_field_xml(fd, field_id="abc")
    formula_segment = xml.split("<Formula>")[1].split("</Formula>")[0]
    assert "&lt;" in formula_segment
    assert "&gt;" in formula_segment
    assert "&amp;" in formula_segment
    assert "<" not in formula_segment.replace("&lt;", "").replace("&amp;", "")


def test_build_calculated_field_xml_no_field_refs_when_none_declared():
    fd = FieldDef(internal_name="X", display_name="X", type="Calculated", formula="=1")
    xml = build_calculated_field_xml(fd, field_id="abc")
    assert "FieldRefs" not in xml


# ---------------------------------------------------------------------------
# lookup / user raw Field XML construction
# ---------------------------------------------------------------------------

def test_build_lookup_field_xml_single_value():
    fd = FieldDef(
        internal_name="Related_Item",
        display_name="Related Item",
        type="Lookup",
        lookup_list_key="target-list-guid",
        lookup_field="Title",
    )
    xml = build_lookup_field_xml(fd, field_id="abc", lookup_list_id="target-list-guid")
    assert "Type='Lookup'" in xml
    assert "List='{target-list-guid}'" in xml
    assert "ShowField='Title'" in xml
    assert "Mult=" not in xml


def test_build_lookup_field_xml_multi_value():
    fd = FieldDef(
        internal_name="Related_Items",
        display_name="Related Items",
        type="LookupMulti",
        lookup_list_key="k",
        lookup_field="Title",
    )
    xml = build_lookup_field_xml(fd, field_id="abc", lookup_list_id="target-guid")
    assert "Mult='TRUE'" in xml


def test_build_lookup_field_xml_requires_lookup_list_id():
    fd = FieldDef(internal_name="X", display_name="X", type="Lookup")
    with pytest.raises(FieldDefinitionError):
        build_lookup_field_xml(fd, field_id="abc", lookup_list_id=None)


def test_build_user_field_xml_multi_value():
    fd = FieldDef(internal_name="Reviewers", display_name="Reviewers", type="UserMulti")
    xml = build_user_field_xml(fd, field_id="abc")
    assert "Type='UserMulti'" in xml
    assert "Mult='TRUE'" in xml
    assert "UserSelectionMode='0'" in xml


def test_build_user_field_xml_rejects_wrong_type():
    fd = FieldDef(internal_name="X", display_name="X", type="Text")
    with pytest.raises(FieldDefinitionError):
        build_user_field_xml(fd, field_id="abc")


# ---------------------------------------------------------------------------
# plan_field_action
# ---------------------------------------------------------------------------

def test_plan_field_action_create_when_no_current_field():
    fd = FieldDef(internal_name="New_Field", display_name="New Field", type="Text")
    action = plan_field_action(fd, existing_type=None)
    assert action.action == "create"
    assert action.internal_name == "New_Field"


def test_plan_field_action_exists_when_type_matches():
    fd = FieldDef(internal_name="F", display_name="F", type="Text")
    action = plan_field_action(fd, existing_type="Text")
    assert action.action == "exists"


def test_plan_field_action_repair_when_type_differs():
    fd = FieldDef(internal_name="F", display_name="F", type="Number")
    action = plan_field_action(fd, existing_type="Text")
    assert action.action == "repair"
    assert "Text" in action.reason and "Number" in action.reason


def test_plan_field_action_choice_without_choices_is_an_error():
    fd = FieldDef(internal_name="F", display_name="F", type="Choice", choices=())
    with pytest.raises(FieldDefinitionError):
        plan_field_action(fd, existing_type=None)


def test_plan_field_action_choice_with_choices_creates():
    fd = FieldDef(internal_name="F", display_name="F", type="Choice", choices=("A", "B"))
    action = plan_field_action(fd, existing_type=None)
    assert action.action == "create"


def test_plan_field_action_calculated_create_includes_xml_when_id_supplied():
    fd = FieldDef(internal_name="Calc", display_name="Calc", type="Calculated", formula="=1")
    action = plan_field_action(fd, existing_type=None, field_id="11111111-1111-1111-1111-111111111111")
    assert action.action == "create"
    assert action.xml is not None
    assert "Type='Calculated'" in action.xml


def test_plan_field_action_calculated_create_requires_field_id():
    fd = FieldDef(internal_name="Calc", display_name="Calc", type="Calculated", formula="=1")
    with pytest.raises(FieldDefinitionError):
        plan_field_action(fd, existing_type=None, field_id=None)


def test_field_def_to_dict_round_trips_core_fields():
    fd = FieldDef(internal_name="F", display_name="Field", type="Text", required=True)
    d = fd.to_dict()
    assert d["internal_name"] == "F"
    assert d["required"] is True
