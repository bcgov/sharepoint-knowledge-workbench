"""
choice_fields.py
=================

Purpose:
    Inventory Choice/MultiChoice fields from an already-loaded, offline
    schema export (see `schema_export.load_schema_export`) and offer a
    convenience mapping into an "overrides" shape (list/field -> option
    list) that a downstream caller can use as input to its own process.

Layer: sharepoint-schema / scripts (plugin-local, offline).

This module makes no live tenant call and has no hardcoded list or field
name -- every field it reports comes from the export already loaded by
the caller. A field whose `Choices` property is entirely absent has an
unknown option set and is reported as such (`choices_known is False`,
with an ambiguity recorded) rather than being silently treated as having
zero choices.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from schema_export import SchemaExport, SectionStatus

_CHOICE_TYPES = ("Choice", "MultiChoice")


@dataclass(frozen=True)
class ChoiceField:
    list_key: str
    internal_name: str
    type_as_string: str
    choices: tuple
    choices_known: bool


@dataclass(frozen=True)
class ChoiceFieldInventory:
    fields: tuple = ()
    ambiguities: tuple = ()
    status: SectionStatus = SectionStatus.UNAVAILABLE


def _extract_choices(item: dict):
    if "Choices" not in item:
        return (), False
    raw = item["Choices"]
    if isinstance(raw, list):
        return tuple(raw), True
    if isinstance(raw, dict) and isinstance(raw.get("results"), list):
        return tuple(raw["results"]), True
    return (), False


def inventory_choice_fields(export: SchemaExport, group: Optional[str] = None) -> ChoiceFieldInventory:
    """Inventory Choice/MultiChoice fields across every list/library in
    `export`. `group` is an opt-in filter on the field's `Group`
    property; when omitted (the default), no group filtering happens --
    there is no project-specific default group."""

    if export.status is SectionStatus.UNAVAILABLE:
        return ChoiceFieldInventory(fields=(), ambiguities=(), status=SectionStatus.UNAVAILABLE)

    fields = []
    ambiguities = []
    for list_key in sorted(export.list_fields):
        section = export.list_fields[list_key]
        for item in section.items:
            if not isinstance(item, dict):
                continue
            if item.get("TypeAsString") not in _CHOICE_TYPES:
                continue
            if group is not None and item.get("Group") != group:
                continue
            internal_name = item.get("InternalName")
            choices, choices_known = _extract_choices(item)
            if not choices_known:
                ambiguities.append(
                    f"{list_key}: choices unknown for field {internal_name!r} "
                    f"(no 'Choices' property present)"
                )
            fields.append(
                ChoiceField(
                    list_key=list_key,
                    internal_name=internal_name,
                    type_as_string=item.get("TypeAsString"),
                    choices=choices,
                    choices_known=choices_known,
                )
            )

    if not fields:
        status = SectionStatus.EMPTY
    elif any(not f.choices_known for f in fields):
        status = SectionStatus.PARTIAL
    else:
        status = SectionStatus.OBSERVED

    return ChoiceFieldInventory(fields=tuple(fields), ambiguities=tuple(ambiguities), status=status)


def to_overrides_mapping(inventory: ChoiceFieldInventory) -> dict:
    """Reduce an inventory to a flat `{"<list_key>.<internal_name>":
    [choice, ...]}` mapping, keyed by list and internal name. Fields
    whose option set is unknown are omitted -- they must never be
    silently represented as having zero choices."""

    return {
        f"{field.list_key}.{field.internal_name}": list(field.choices)
        for field in inventory.fields
        if field.choices_known
    }
