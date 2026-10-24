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

Key Input Dependencies:
    - Caller-supplied SharePoint discovery exports and the plugin-local schema/analysis modules used by this script.

Function index:
    - DuplicateFieldGroup
    - DuplicateFieldsReport
    - _collect_list_fields
    - _duplicate_groups_for_list
    - _aggregate_status
    - find_duplicate_fields
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


# Represent distinct internal field names sharing one display name in a list.
@dataclass(frozen=True)
class DuplicateFieldGroup:
    """Represent distinct internal field names sharing one display name in a list."""
    list_key: str
    display_name: str
    internal_names: tuple


# Hold duplicate-field groups, ambiguities, and their evidence status.
@dataclass(frozen=True)
class DuplicateFieldsReport:
    """Hold duplicate-field groups, ambiguities, and their evidence status."""
    groups: tuple = ()
    ambiguities: tuple = ()
    status: SectionStatus = SectionStatus.UNAVAILABLE


def _collect_list_fields(
    list_key: str, section, builtin_internal_names: tuple
) -> tuple[dict, list[str]]:
    """Group eligible fields by display name and report fields without titles."""
    by_display_name = {}
    ambiguities = []
    for item in section.items:
        if not isinstance(item, dict):
            continue
        internal_name = item.get("InternalName")
        if internal_name is None or internal_name in builtin_internal_names or item.get("ReadOnlyField"):
            continue
        title = item.get("Title")
        if title is None:
            ambiguities.append(
                f"{list_key}: field {internal_name!r} has no display name (Title)"
            )
            continue
        by_display_name.setdefault(title, []).append(internal_name)
    return by_display_name, ambiguities


def _duplicate_groups_for_list(list_key: str, by_display_name: dict) -> tuple[list, list[str]]:
    """Separate true display-name collisions from repeated-name ambiguities."""
    groups = []
    ambiguities = []
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
    return groups, ambiguities


def _aggregate_status(list_statuses: list[SectionStatus]) -> SectionStatus:
    """Return the honest combined status for the list-field sections."""
    if not list_statuses:
        return SectionStatus.EMPTY
    if all(status in (SectionStatus.OBSERVED, SectionStatus.EMPTY) for status in list_statuses):
        return SectionStatus.OBSERVED
    return SectionStatus.PARTIAL


def find_duplicate_fields(
    export: SchemaExport, builtin_internal_names: tuple = DEFAULT_BUILTIN_INTERNAL_NAMES
) -> DuplicateFieldsReport:
    """Find, per list/library, distinct internal names sharing a display name.

    `builtin_internal_names` is a caller-configurable exclusion list; no
    project-specific defaults are added beyond the module's neutral defaults.
    """
    if export.status is SectionStatus.UNAVAILABLE:
        return DuplicateFieldsReport(groups=(), ambiguities=(), status=SectionStatus.UNAVAILABLE)

    groups = []
    ambiguities = []
    list_statuses = [section.status for section in export.list_fields.values()]
    for list_key in sorted(export.list_fields):
        by_display_name, list_ambiguities = _collect_list_fields(
            list_key, export.list_fields[list_key], builtin_internal_names
        )
        list_groups, repeated_name_ambiguities = _duplicate_groups_for_list(
            list_key, by_display_name
        )
        groups.extend(list_groups)
        ambiguities.extend(list_ambiguities)
        ambiguities.extend(repeated_name_ambiguities)

    return DuplicateFieldsReport(
        groups=tuple(groups),
        ambiguities=tuple(ambiguities),
        status=_aggregate_status(list_statuses),
    )
