"""
field_provisioning.py
======================

Purpose:
    Caller-declared site/list field provisioning: deployable-field filtering,
    field-type-repair detection, raw Field XML construction for field types
    a typed cmdlet API cannot express (Calculated -- no ``-Formula``
    parameter exists; Lookup/LookupMulti; User/UserMulti), and per-field
    create/exist/repair planning.

    Pure planning only. This module ships no transport, no client, no
    credentials, and performs no write of any kind -- see ``list_provisioning``
    for the gated apply step that actually executes a plan.

Layer: sharepoint-provisioning / field planning

Key Input Dependencies:
    - none (standard library only)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

# Field types that are never "deployable" from an exported field set: computed/
# system-managed types, or types requiring a separate provisioning path
# (Calculated fields need raw Field XML -- see build_calculated_field_xml --
# and are provisioned explicitly by the caller, not swept up here).
SKIP_FIELD_TYPES = frozenset(
    {
        "Counter",
        "Computed",
        "Calculated",
        "WorkflowStatus",
        "Attachments",
        "AllDayEvent",
        "FreeBusy",
        "Overbook",
        "Recurrence",
        "Facilities",
        "RelatedItems",
        "CrossProjectLink",
        "TaxonomyFieldType",
        "TaxonomyFieldTypeMulti",
    }
)

# Field types PnP's typed field-creation API cannot express and which require
# raw Field XML construction instead.
RAW_XML_FIELD_TYPES = frozenset({"Calculated", "Lookup", "LookupMulti", "User", "UserMulti"})

_SIMPLE_TEXT_LIKE_TYPES = frozenset(
    {"Text", "Note", "DateTime", "Boolean", "Number", "Integer", "Currency", "URL"}
)
_CHOICE_TYPES = frozenset({"Choice", "MultiChoice"})
_LOOKUP_TYPES = frozenset({"Lookup", "LookupMulti"})
_USER_TYPES = frozenset({"User", "UserMulti"})


class FieldDefinitionError(ValueError):
    """Raised when a field cannot be planned/rendered as declared."""


@dataclass(frozen=True)
class FieldDef:
    """A caller-declared field. No live SharePoint identifier (site/tenant
    URL, GUID) is ever a default here -- ``lookup_list_key`` is the caller's
    own identifier for a target list, resolved to a real lookup list id by
    the caller before ``build_lookup_field_xml`` is called."""

    internal_name: str
    display_name: str
    type: str
    required: bool = False
    hidden: bool = False
    choices: Sequence[str] = field(default_factory=tuple)
    lookup_list_key: str | None = None
    lookup_field: str = "Title"
    formula: str | None = None
    result_type: str = "Text"
    field_refs: Sequence[str] = field(default_factory=tuple)
    group: str = "Custom Columns"

    def to_dict(self) -> dict[str, Any]:
        return {
            "internal_name": self.internal_name,
            "display_name": self.display_name,
            "type": self.type,
            "required": self.required,
            "hidden": self.hidden,
            "choices": list(self.choices),
            "lookup_list_key": self.lookup_list_key,
            "lookup_field": self.lookup_field,
            "formula": self.formula,
            "result_type": self.result_type,
            "field_refs": list(self.field_refs),
            "group": self.group,
        }


@dataclass(frozen=True)
class FieldAction:
    """One planned action for one field. Never itself performs a write."""

    internal_name: str
    action: str  # "create" | "exists" | "repair"
    reason: str
    xml: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "internal_name": self.internal_name,
            "action": self.action,
            "reason": self.reason,
            "xml": self.xml,
        }


def filter_deployable_fields(
    fields: Sequence[Mapping[str, Any]],
    *,
    exclude_names: Sequence[str] = (),
    force_include_names: Sequence[str] = (),
) -> list[dict[str, Any]]:
    """Filter an exported field set down to fields worth deploying.

    A field is deployable if it belongs to the "Custom Columns" group, is not
    a skip-listed system/computed type, is not ``Title``, is not explicitly
    excluded, and is either explicitly force-included or both visible and
    writable (not hidden, not read-only).
    """
    exclude = set(exclude_names)
    force_include = set(force_include_names)
    result = []
    for raw in fields:
        internal_name = raw.get("InternalName")
        if raw.get("Group") != "Custom Columns":
            continue
        if raw.get("TypeAsString") in SKIP_FIELD_TYPES:
            continue
        if internal_name == "Title":
            continue
        if internal_name in exclude:
            continue
        forced = internal_name in force_include
        visible_writable = raw.get("Hidden") is False and raw.get("ReadOnlyField") is False
        if forced or visible_writable:
            result.append(dict(raw))
    return result


def field_needs_type_repair(current_type: str | None, expected_type: str) -> bool:
    """True when a live field exists with a type that does not match the
    declared schema -- the create-if-missing/repair-if-wrong-type case."""
    if current_type is None:
        return False
    return current_type != expected_type


def _escape_xml_attr(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def _escape_xml_text(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_calculated_field_xml(field_def: FieldDef, *, field_id: str) -> str:
    """Build raw Field XML for a Calculated column.

    A typed field-creation API has no way to express a formula, so a
    Calculated column must be created via raw Field XML instead. All
    caller-supplied text is escaped: attribute values via the full XML
    attribute-escaping set (& < > " '), and the formula body (element text,
    not an attribute) via the text-escaping subset (& < >).
    """
    if field_def.type != "Calculated":
        raise FieldDefinitionError(
            f"build_calculated_field_xml requires type='Calculated', got {field_def.type!r}"
        )
    if not field_def.formula:
        raise FieldDefinitionError(
            f"Calculated field '{field_def.internal_name}' has no formula; "
            "populate FieldDef.formula before rendering"
        )

    field_refs_xml = ""
    if field_def.field_refs:
        refs = "".join(f"<FieldRef Name='{_escape_xml_attr(r)}'/>" for r in field_def.field_refs)
        field_refs_xml = f"<FieldRefs>{refs}</FieldRefs>"

    return (
        f"<Field Type='Calculated' DisplayName='{_escape_xml_attr(field_def.display_name)}' "
        f"ResultType='{_escape_xml_attr(field_def.result_type)}' ReadOnly='TRUE' "
        f"ID='{{{field_id}}}' StaticName='{_escape_xml_attr(field_def.internal_name)}' "
        f"Name='{_escape_xml_attr(field_def.internal_name)}' "
        f"Group='{_escape_xml_attr(field_def.group)}'>"
        f"<Formula>{_escape_xml_text(field_def.formula)}</Formula>{field_refs_xml}</Field>"
    )


def build_lookup_field_xml(field_def: FieldDef, *, field_id: str, lookup_list_id: str | None) -> str:
    """Build raw Field XML for a Lookup/LookupMulti column.

    ``lookup_list_id`` is a real target-list identifier the caller has
    already resolved -- this module never resolves a lookup-list key to a
    live id itself (that would be tenant I/O)."""
    if field_def.type not in ("Lookup", "LookupMulti"):
        raise FieldDefinitionError(
            f"build_lookup_field_xml requires type in Lookup/LookupMulti, got {field_def.type!r}"
        )
    if not lookup_list_id:
        raise FieldDefinitionError(
            f"Lookup field '{field_def.internal_name}' has no resolved lookup_list_id"
        )
    mult = " Mult='TRUE'" if field_def.type == "LookupMulti" else ""
    required = "TRUE" if field_def.required else "FALSE"
    return (
        f"<Field Type='{field_def.type}' DisplayName='{_escape_xml_attr(field_def.display_name)}' "
        f"Required='{required}' List='{{{lookup_list_id}}}' "
        f"ShowField='{_escape_xml_attr(field_def.lookup_field)}'{mult} "
        f"Group='{_escape_xml_attr(field_def.group)}' ID='{{{field_id}}}' "
        f"StaticName='{_escape_xml_attr(field_def.internal_name)}' "
        f"Name='{_escape_xml_attr(field_def.internal_name)}' />"
    )


def build_user_field_xml(field_def: FieldDef, *, field_id: str) -> str:
    """Build raw Field XML for a User/UserMulti column."""
    if field_def.type not in ("User", "UserMulti"):
        raise FieldDefinitionError(
            f"build_user_field_xml requires type in User/UserMulti, got {field_def.type!r}"
        )
    mult = " Mult='TRUE'" if field_def.type == "UserMulti" else ""
    required = "TRUE" if field_def.required else "FALSE"
    return (
        f"<Field Type='{field_def.type}' DisplayName='{_escape_xml_attr(field_def.display_name)}' "
        f"Required='{required}'{mult} Group='{_escape_xml_attr(field_def.group)}' "
        f"UserSelectionMode='0' ID='{{{field_id}}}' "
        f"StaticName='{_escape_xml_attr(field_def.internal_name)}' "
        f"Name='{_escape_xml_attr(field_def.internal_name)}' />"
    )


def plan_field_action(
    field_def: FieldDef,
    *,
    existing_type: str | None,
    field_id: str | None = None,
    lookup_list_id: str | None = None,
) -> FieldAction:
    """Plan the single action for one declared field against one caller-
    supplied observation of its current live type (``None`` if the field
    does not currently exist)."""
    if field_def.type in _CHOICE_TYPES and not field_def.choices:
        raise FieldDefinitionError(
            f"'{field_def.internal_name}' ({field_def.type}) has no choices declared"
        )

    if existing_type is not None:
        if field_needs_type_repair(existing_type, field_def.type):
            return FieldAction(
                internal_name=field_def.internal_name,
                action="repair",
                reason=f"live type {existing_type!r} does not match declared type {field_def.type!r}",
            )
        return FieldAction(
            internal_name=field_def.internal_name,
            action="exists",
            reason=f"already present with declared type {field_def.type!r}",
        )

    xml: str | None = None
    if field_def.type == "Calculated":
        if not field_id:
            raise FieldDefinitionError(
                f"Calculated field '{field_def.internal_name}' requires a caller-supplied field_id"
            )
        xml = build_calculated_field_xml(field_def, field_id=field_id)
    elif field_def.type in _LOOKUP_TYPES:
        if not field_id:
            raise FieldDefinitionError(
                f"Lookup field '{field_def.internal_name}' requires a caller-supplied field_id"
            )
        xml = build_lookup_field_xml(field_def, field_id=field_id, lookup_list_id=lookup_list_id)
    elif field_def.type in _USER_TYPES:
        if not field_id:
            raise FieldDefinitionError(
                f"User field '{field_def.internal_name}' requires a caller-supplied field_id"
            )
        xml = build_user_field_xml(field_def, field_id=field_id)
    elif field_def.type in _CHOICE_TYPES or field_def.type in _SIMPLE_TEXT_LIKE_TYPES:
        xml = None
    else:
        raise FieldDefinitionError(f"unsupported field type '{field_def.type}'")

    return FieldAction(
        internal_name=field_def.internal_name,
        action="create",
        reason=f"declared but not present (type {field_def.type!r})",
        xml=xml,
    )
