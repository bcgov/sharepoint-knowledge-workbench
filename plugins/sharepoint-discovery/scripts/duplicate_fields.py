"""
duplicate_fields.py
====================

Purpose:
    Detect display-name collisions between distinct internal field names
    within one list/library, from an already-loaded, offline schema
    export (see `schema_export.load_schema_export`).

Layer: sharepoint-schema / scripts (plugin-local, offline).

This module is strictly read-only and offers no remediation path: it
never removes, renames, or otherwise mutates a field, and it never
connects to a tenant. It only reports what it finds. Built-in SharePoint
columns and read-only fields are excluded from consideration, using a
caller-configurable list rather than a hardcoded name check -- and a
display name repeated under a single internal name is treated as an
ambiguity to surface, not as a duplicate finding (a duplicate requires
at least two distinct internal names sharing one display name).
"""

from __future__ import annotations

from dataclasses import dataclass

from schema_export import SchemaExport, SectionStatus

DEFAULT_BUILTIN_INTERNAL_NAMES = (
    "Title",
    "Author",
    "Editor",
    "Created",
    "Modified",
    "ID",
    "ContentType",
    "ContentTypeId",
    "Attachments",
    "Order",
    "GUID",
    "FileLeafRef",
    "FileRef",
    "FileDirRef",
    "Owshiddenversion",
    "_UIVersionString",
    "AppAuthor",
    "AppEditor",
)


@dataclass(frozen=True)
class DuplicateFieldGroup:
    list_key: str
    display_name: str
    internal_names: tuple


@dataclass(frozen=True)
class DuplicateFieldsReport:
    groups: tuple = ()
    ambiguities: tuple = ()
    status: SectionStatus = SectionStatus.UNAVAILABLE


def find_duplicate_fields(
    export: SchemaExport, builtin_internal_names: tuple = DEFAULT_BUILTIN_INTERNAL_NAMES
) -> DuplicateFieldsReport:
    """Find, per list/library, sets of two or more distinct internal
    field names sharing one display name (`Title`). `builtin_internal_names`
    is an opt-out exclusion list, caller-configurable with no hidden
    project-specific defaults added on top."""

    if export.status is SectionStatus.UNAVAILABLE:
        return DuplicateFieldsReport(groups=(), ambiguities=(), status=SectionStatus.UNAVAILABLE)

    groups = []
    ambiguities = []
    list_statuses = [section.status for section in export.list_fields.values()]

    for list_key in sorted(export.list_fields):
        section = export.list_fields[list_key]
        by_display_name: dict = {}
        for item in section.items:
            if not isinstance(item, dict):
                continue
            internal_name = item.get("InternalName")
            if internal_name is None:
                continue
            if internal_name in builtin_internal_names:
                continue
            if item.get("ReadOnlyField"):
                continue
            title = item.get("Title")
            if title is None:
                ambiguities.append(
                    f"{list_key}: field {internal_name!r} has no display name (Title)"
                )
                continue
            by_display_name.setdefault(title, []).append(internal_name)

        for display_name, internal_names in by_display_name.items():
            distinct = []
            for name in internal_names:
                if name not in distinct:
                    distinct.append(name)
            if len(distinct) > 1:
                groups.append(
                    DuplicateFieldGroup(
                        list_key=list_key, display_name=display_name, internal_names=tuple(distinct)
                    )
                )
            elif len(internal_names) > 1:
                ambiguities.append(
                    f"{list_key}: internal name {distinct[0]!r} repeated "
                    f"for display name {display_name!r}"
                )

    if not list_statuses:
        status = SectionStatus.EMPTY
    elif all(s in (SectionStatus.OBSERVED, SectionStatus.EMPTY) for s in list_statuses):
        status = SectionStatus.OBSERVED
    else:
        status = SectionStatus.PARTIAL

    return DuplicateFieldsReport(groups=tuple(groups), ambiguities=tuple(ambiguities), status=status)
