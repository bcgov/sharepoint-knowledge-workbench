"""Tests for content_type_provisioning.py -- create-if-missing content-type
planning, field-link add/hide/show/unlink reconciliation (drift detection,
not silent fix), and content-type-to-list attach planning. Pure planning,
no writes.
Purpose:
    Verify content-type plans create, link, hide, show, unlink, and attach as declared.

Key Input Dependencies:
    - content_type_provisioning declarations and caller-supplied live-state fixtures.

Function Index:
    test_plan_content_type_creates_when_missing, test_plan_content_type_reports_already_exists, test_plan_content_type_links_new_field_when_content_type_missing, test_plan_content_type_links_and_hides_field_marked_hidden, test_plan_content_type_skips_link_when_field_already_linked_and_correct, test_plan_content_type_detects_hidden_flag_drift_and_reports_not_silently_fixes, test_plan_content_type_unlinks_field_no_longer_declared, test_plan_content_type_does_not_unlink_field_that_is_not_linked, test_plan_add_content_type_to_list_attaches_when_missing, test_plan_add_content_type_to_list_reports_already_attached
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts" / "schema-reconciliation"))

from content_type_provisioning import (
    ContentTypeDef,
    ContentTypeFieldSpec,
    ContentTypeState,
    plan_add_content_type_to_list,
    plan_content_type,
)


# Verify the contract that plan content type creates when missing.
def test_plan_content_type_creates_when_missing():
    """Verify the contract that plan content type creates when missing."""
    ct = ContentTypeDef(name="Demo_Item", parent="Item", fields=())
    actions = plan_content_type(ct, current=None)
    create_actions = [a for a in actions if a.step == "create_content_type"]
    assert len(create_actions) == 1
    assert create_actions[0].already_correct is False
    assert "Demo_Item" in create_actions[0].detail


# Verify the contract that plan content type reports already exists.
def test_plan_content_type_reports_already_exists():
    """Verify the contract that plan content type reports already exists."""
    ct = ContentTypeDef(name="Demo_Item", parent="Item", fields=())
    current = ContentTypeState(name="Demo_Item", exists=True, field_links={})
    actions = plan_content_type(ct, current=current)
    create_actions = [a for a in actions if a.step == "create_content_type"]
    assert create_actions[0].already_correct is True


# Verify the contract that plan content type links new field when content type missing.
def test_plan_content_type_links_new_field_when_content_type_missing():
    """Verify the contract that plan content type links new field when content type missing."""
    ct = ContentTypeDef(
        name="Demo_Item",
        fields=(ContentTypeFieldSpec(field_name="Widget_Count"),),
    )
    actions = plan_content_type(ct, current=None)
    link_actions = [a for a in actions if a.step == "link_field"]
    assert len(link_actions) == 1
    assert "Widget_Count" in link_actions[0].detail


# Verify the contract that plan content type links and hides field marked hidden.
def test_plan_content_type_links_and_hides_field_marked_hidden():
    """Verify the contract that plan content type links and hides field marked hidden."""
    ct = ContentTypeDef(
        name="Demo_Item",
        fields=(ContentTypeFieldSpec(field_name="Internal_Id", hidden=True),),
    )
    actions = plan_content_type(ct, current=None)
    steps = [a.step for a in actions]
    assert "link_field" in steps
    assert "hide_field" in steps


# Verify the contract that plan content type skips link when field already linked and correct.
def test_plan_content_type_skips_link_when_field_already_linked_and_correct():
    """Verify the contract that plan content type skips link when field already linked and correct."""
    ct = ContentTypeDef(
        name="Demo_Item",
        fields=(ContentTypeFieldSpec(field_name="Widget_Count", hidden=False),),
    )
    current = ContentTypeState(
        name="Demo_Item", exists=True, field_links={"Widget_Count": False}
    )
    actions = plan_content_type(ct, current=current)
    link_actions = [a for a in actions if a.step == "link_field"]
    assert link_actions == []
    show_actions = [a for a in actions if a.step == "show_field"]
    assert len(show_actions) == 1
    assert show_actions[0].already_correct is True


def test_plan_content_type_detects_hidden_flag_drift_and_reports_not_silently_fixes():
    """A field linked but with hidden=True live while the schema declares
    hidden=False must be surfaced as drift, not silently corrected without
    being named in the plan."""
    ct = ContentTypeDef(
        name="Demo_Item",
        fields=(ContentTypeFieldSpec(field_name="Widget_Count", hidden=False),),
    )
    current = ContentTypeState(
        name="Demo_Item", exists=True, field_links={"Widget_Count": True}
    )
    actions = plan_content_type(ct, current=current)
    show_actions = [a for a in actions if a.step == "show_field"]
    assert len(show_actions) == 1
    assert show_actions[0].already_correct is False
    assert "drift" in show_actions[0].detail.lower()
    assert "was True" in show_actions[0].detail or "True" in show_actions[0].detail


# Verify the contract that plan content type unlinks field no longer declared.
def test_plan_content_type_unlinks_field_no_longer_declared():
    """Verify the contract that plan content type unlinks field no longer declared."""
    ct = ContentTypeDef(
        name="Demo_Item",
        fields=(),
        unlink_fields=("Deprecated_Field",),
    )
    current = ContentTypeState(
        name="Demo_Item", exists=True, field_links={"Deprecated_Field": False}
    )
    actions = plan_content_type(ct, current=current)
    unlink_actions = [a for a in actions if a.step == "unlink_field"]
    assert len(unlink_actions) == 1
    assert "Deprecated_Field" in unlink_actions[0].detail


# Verify the contract that plan content type does not unlink field that is not linked.
def test_plan_content_type_does_not_unlink_field_that_is_not_linked():
    """Verify the contract that plan content type does not unlink field that is not linked."""
    ct = ContentTypeDef(name="Demo_Item", fields=(), unlink_fields=("Never_Linked",))
    current = ContentTypeState(name="Demo_Item", exists=True, field_links={})
    actions = plan_content_type(ct, current=current)
    assert [a for a in actions if a.step == "unlink_field"] == []


# Verify the contract that plan add content type to list attaches when missing.
def test_plan_add_content_type_to_list_attaches_when_missing():
    """Verify the contract that plan add content type to list attaches when missing."""
    action = plan_add_content_type_to_list("Demo_List", "Demo_Item", current_list_content_types=())
    assert action.step == "attach_content_type"
    assert action.already_correct is False


# Verify the contract that plan add content type to list reports already attached.
def test_plan_add_content_type_to_list_reports_already_attached():
    """Verify the contract that plan add content type to list reports already attached."""
    action = plan_add_content_type_to_list(
        "Demo_List", "Demo_Item", current_list_content_types=("Demo_Item",)
    )
    assert action.already_correct is True
