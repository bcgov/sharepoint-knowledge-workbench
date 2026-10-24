"""
schema_definition.py
=====================

Purpose:
    Transform an already-loaded `SchemaExport` (see `schema_export.py`) into
    a declarative, JSON-serializable schema definition -- site columns,
    content types, and lists (each with its own fields) -- suitable for
    later comparison or (in a future, separate step, not built here)
    provisioning-input translation.

Layer: sharepoint-schema / scripts (plugin-local, offline, pure transform).

This module performs no tenant I/O. `generate_schema_definition` is a pure
function over an in-memory `SchemaExport`; it never touches disk. The only
I/O in this module is the optional `save`/`load` convenience for reading and
writing a schema-definition JSON file at a caller-supplied path -- still
strictly local-disk, never a tenant call.

Honest outcomes: this module reuses `schema_export.SectionStatus` rather than
inventing a second status vocabulary. A `SchemaExport` whose overall status
is not `OBSERVED` (e.g. `UNAVAILABLE`, `FORBIDDEN`, `FAILED`, `PARTIAL`) never
produces a definition that looks like a clean, empty, successful schema --
the same status is carried onto the resulting `SiteSchemaDefinition`, and any
section that could not be read honestly contributes nothing to that
definition's collections rather than being silently treated as "confirmed
empty".

Key Input Dependencies:
    - Caller-supplied SharePoint discovery exports and the plugin-local schema/analysis modules used by this script.

Function index:
    - FieldDefinition
    - FieldDefinition.to_dict
    - FieldDefinition.from_dict
    - ContentTypeDefinition
    - ContentTypeDefinition.to_dict
    - ContentTypeDefinition.from_dict
    - ListDefinition
    - ListDefinition.to_dict
    - ListDefinition.from_dict
    - SiteSchemaDefinition
    - SiteSchemaDefinition.to_dict
    - SiteSchemaDefinition.from_dict
    - SiteSchemaDefinition.save
    - SiteSchemaDefinition.load
    - _field_from_item
    - _content_type_from_item
    - _fields_from_section
    - _list_key_for_title
    - _list_from_item
    - generate_schema_definition
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from schema_export import SchemaExport, SectionResult, SectionStatus


@dataclass(frozen=True)
class FieldDefinition:
    """One field (site column or list field), described declaratively."""

    internal_name: str
    display_name: str = ""
    type_as_string: str = ""
    required: bool = False
    hidden: bool = False
    read_only: bool = False
    group: str = ""

    # Serialize the field's generic schema properties for comparison or publication.
    def to_dict(self) -> dict:
        """Serialize field names, type, and behavioral flags as JSON-compatible values."""
        return {
            "internal_name": self.internal_name,
            "display_name": self.display_name,
            "type_as_string": self.type_as_string,
            "required": self.required,
            "hidden": self.hidden,
            "read_only": self.read_only,
            "group": self.group,
        }

    # Reconstruct a field from its serialized schema properties.
    @staticmethod
    def from_dict(payload: dict) -> "FieldDefinition":
        """Restore a field definition and default optional metadata absent from older payloads."""
        return FieldDefinition(
            internal_name=payload["internal_name"],
            display_name=payload.get("display_name", ""),
            type_as_string=payload.get("type_as_string", ""),
            required=payload.get("required", False),
            hidden=payload.get("hidden", False),
            read_only=payload.get("read_only", False),
            group=payload.get("group", ""),
        )


@dataclass(frozen=True)
class ContentTypeDefinition:
    """A content type, described declaratively."""

    name: str
    string_id: str = ""
    group: str = ""
    sealed: bool = False
    read_only: bool = False

    # Serialize the content type's generic schema properties for comparison or publication.
    def to_dict(self) -> dict:
        """Serialize the content-type name, identifier, group, and flags."""
        return {
            "name": self.name,
            "string_id": self.string_id,
            "group": self.group,
            "sealed": self.sealed,
            "read_only": self.read_only,
        }

    # Reconstruct a content type from its serialized schema properties.
    @staticmethod
    def from_dict(payload: dict) -> "ContentTypeDefinition":
        """Restore a content-type definition with neutral defaults for optional metadata."""
        return ContentTypeDefinition(
            name=payload["name"],
            string_id=payload.get("string_id", ""),
            group=payload.get("group", ""),
            sealed=payload.get("sealed", False),
            read_only=payload.get("read_only", False),
        )


@dataclass(frozen=True)
class ListDefinition:
    """A list or document library, with its own fields, described
    declaratively.

    `key` is the export-relative key the fields were loaded under (e.g.
    ``"lists/Records"`` or ``"document_libraries/Docs"``) -- carried through
    unchanged so a later diff/provisioning step can tell a list from a
    document library without re-deriving it.
    """

    key: str
    title: str
    base_template: int = 0
    is_library: bool = False
    content_types_enabled: bool = False
    hidden: bool = False
    fields: tuple = ()
    fields_status: SectionStatus = SectionStatus.UNAVAILABLE

    # Serialize list metadata, nested fields, and their observed section status.
    def to_dict(self) -> dict:
        """Serialize list identity, template flags, fields, and field-section status."""
        return {
            "key": self.key,
            "title": self.title,
            "base_template": self.base_template,
            "is_library": self.is_library,
            "content_types_enabled": self.content_types_enabled,
            "hidden": self.hidden,
            "fields": [f.to_dict() for f in self.fields],
            "fields_status": self.fields_status.value,
        }

    # Reconstruct a list and its nested definitions from serialized values.
    @staticmethod
    def from_dict(payload: dict) -> "ListDefinition":
        """Restore list metadata and nested fields while preserving field-section status."""
        return ListDefinition(
            key=payload["key"],
            title=payload.get("title", ""),
            base_template=payload.get("base_template", 0),
            is_library=payload.get("is_library", False),
            content_types_enabled=payload.get("content_types_enabled", False),
            hidden=payload.get("hidden", False),
            fields=tuple(FieldDefinition.from_dict(f) for f in payload.get("fields", ())),
            fields_status=SectionStatus(payload.get("fields_status", SectionStatus.UNAVAILABLE.value)),
        )


@dataclass(frozen=True)
class SiteSchemaDefinition:
    """The full, declarative picture of one site's schema."""

    label: str
    site_columns: tuple = ()
    content_types: tuple = ()
    lists: tuple = ()
    status: SectionStatus = SectionStatus.UNAVAILABLE

    # Serialize the complete schema and its overall observation status.
    def to_dict(self) -> dict:
        """Serialize schema metadata, site columns, content types, and lists."""
        return {
            "label": self.label,
            "site_columns": [f.to_dict() for f in self.site_columns],
            "content_types": [ct.to_dict() for ct in self.content_types],
            "lists": [l.to_dict() for l in self.lists],
            "status": self.status.value,
        }

    # Reconstruct the complete schema definition from serialized collections.
    @staticmethod
    def from_dict(payload: dict) -> "SiteSchemaDefinition":
        """Restore nested schema definitions and retain the serialized observation outcome."""
        return SiteSchemaDefinition(
            label=payload["label"],
            site_columns=tuple(FieldDefinition.from_dict(f) for f in payload.get("site_columns", ())),
            content_types=tuple(
                ContentTypeDefinition.from_dict(ct) for ct in payload.get("content_types", ())
            ),
            lists=tuple(ListDefinition.from_dict(l) for l in payload.get("lists", ())),
            status=SectionStatus(payload.get("status", SectionStatus.UNAVAILABLE.value)),
        )

    def save(self, path) -> None:
        """Write this definition to `path` as JSON. Local-disk only."""
        import json

        Path(path).write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")

    @staticmethod
    def load(path) -> "SiteSchemaDefinition":
        """Read a definition previously written by `save`. Local-disk only."""
        import json

        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        return SiteSchemaDefinition.from_dict(payload)


# Convert one exported field record to a portable field definition.
def _field_from_item(item: dict) -> FieldDefinition:
    """Convert one exported field record into its neutral declarative representation."""
    return FieldDefinition(
        internal_name=item.get("InternalName", ""),
        display_name=item.get("Title", ""),
        type_as_string=item.get("TypeAsString", ""),
        required=bool(item.get("Required", False)),
        hidden=bool(item.get("Hidden", False)),
        read_only=bool(item.get("ReadOnlyField", False)),
        group=item.get("Group", ""),
    )


# Convert one exported content-type record to a portable definition.
def _content_type_from_item(item: dict) -> ContentTypeDefinition:
    """Convert one exported content-type record into a portable definition."""
    return ContentTypeDefinition(
        name=item.get("Name", ""),
        string_id=item.get("StringId", ""),
        group=item.get("Group", ""),
        sealed=bool(item.get("Sealed", False)),
        read_only=bool(item.get("ReadOnly", False)),
    )


# Convert valid field records from a schema section while retaining their order.
def _fields_from_section(section: SectionResult) -> tuple:
    """Convert valid field records from an observed schema section in source order."""
    return tuple(_field_from_item(item) for item in section.items if isinstance(item, dict))


def _list_key_for_title(list_fields: dict, title: str) -> Optional[str]:
    """`list_fields` is keyed by `"lists/<Name>"`/`"document_libraries/<Name>"`,
    not by list title directly -- match on the trailing path segment."""
    for key in list_fields:
        if key.rsplit("/", 1)[-1] == title:
            return key
    return None


# Build one list or library definition and attach its field-section evidence.
def _list_from_item(item: dict, list_fields: dict) -> ListDefinition:
    """Build one list or library definition and attach its field-section outcome."""
    title = item.get("Title", "")
    key = _list_key_for_title(list_fields, title)
    fields_section = list_fields.get(key) if key else None

    if fields_section is None:
        fields: tuple = ()
        fields_status = SectionStatus.UNAVAILABLE
    else:
        fields_status = fields_section.status
        fields = _fields_from_section(fields_section) if fields_status is SectionStatus.OBSERVED else ()

    return ListDefinition(
        key=key or title,
        title=title,
        base_template=item.get("BaseTemplate", 0),
        is_library=bool(item.get("IsLibrary", False)),
        content_types_enabled=bool(item.get("ContentTypesEnabled", False)),
        hidden=bool(item.get("Hidden", False)),
        fields=fields,
        fields_status=fields_status,
    )


def generate_schema_definition(export: SchemaExport, label: str) -> SiteSchemaDefinition:
    """Transform a loaded `SchemaExport` into a declarative
    `SiteSchemaDefinition`. Pure function -- no file I/O.

    A section that was not cleanly `OBSERVED` contributes nothing to the
    corresponding collection (never a guessed or partial reconstruction),
    and `export.status` is carried through unchanged onto the result so a
    caller can never mistake a degraded export for a clean one.
    """

    site_columns = (
        _fields_from_section(export.site_columns)
        if export.site_columns.status is SectionStatus.OBSERVED
        else ()
    )
    content_types = (
        tuple(_content_type_from_item(item) for item in export.content_types.items if isinstance(item, dict))
        if export.content_types.status is SectionStatus.OBSERVED
        else ()
    )
    lists = (
        tuple(_list_from_item(item, export.list_fields) for item in export.lists.items if isinstance(item, dict))
        if export.lists.status is SectionStatus.OBSERVED
        else ()
    )

    return SiteSchemaDefinition(
        label=label,
        site_columns=site_columns,
        content_types=content_types,
        lists=lists,
        status=export.status,
    )
