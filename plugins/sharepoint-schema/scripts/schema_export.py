"""
schema_export.py
=================

Purpose:
    Load a SharePoint schema export directory (a plain tree of JSON files
    produced by some earlier, out-of-scope extraction step) into an
    in-memory, read-only representation -- with an honest, explicit
    per-section outcome for every section read.

Layer: sharepoint-schema / scripts (plugin-local, offline).

This module never connects to a tenant and never writes anything. It only
reads JSON files that already exist on disk under a caller-supplied root
directory. The on-disk layout (directory/file names, and an optional
top-level `scope` segment) is entirely caller-configurable via
`ExportLayout` -- there is no built-in assumption about where an export
"really" lives.

Section outcomes are reported via `SectionStatus` rather than silently
returning an empty collection for every kind of absence: a missing file
(`UNAVAILABLE`) is not the same as a present-but-empty file (`EMPTY`), an
unreadable file (`FORBIDDEN`) is not the same as a malformed one
(`FAILED`), and a JSON shape this module does not understand
(`NOT_SUPPORTED`) is not silently treated as zero items.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional


class SectionStatus(Enum):
    """Honest outcome vocabulary for a single section read, or for an
    aggregate of several section reads."""

    OBSERVED = "observed"
    EMPTY = "empty"
    FORBIDDEN = "forbidden"
    UNAVAILABLE = "unavailable"
    NOT_SUPPORTED = "not_supported"
    PARTIAL = "partial"
    FAILED = "failed"


@dataclass(frozen=True)
class SectionResult:
    """The outcome of reading one JSON section file."""

    status: SectionStatus
    items: tuple = ()
    detail: str = ""
    ambiguities: tuple = ()


@dataclass(frozen=True)
class ExportLayout:
    """Caller-configurable description of where an export's files live.

    Every path segment has a neutral, project-agnostic default. `scope`
    is an optional extra path segment inserted between the export root
    and everything else (for exports that nest a site/tenant scope one
    level down); it defaults to `None`, i.e. no extra segment.
    """

    scope: Optional[str] = None
    summary_dir: str = "summary"
    site_columns_file: str = "site_columns.json"
    content_types_file: str = "content_types.json"
    lists_file: str = "lists.json"
    lists_dir: str = "lists"
    document_libraries_dir: str = "document_libraries"
    fields_file: str = "fields.json"


@dataclass(frozen=True)
class SchemaExport:
    """The full, read-only picture of one schema export."""

    label: str
    site_columns: SectionResult
    content_types: SectionResult
    lists: SectionResult
    list_fields: dict = field(default_factory=dict)
    status: SectionStatus = SectionStatus.UNAVAILABLE


def _load_section(path: Path, key_property: str) -> SectionResult:
    if not path.is_file():
        return SectionResult(
            status=SectionStatus.UNAVAILABLE,
            items=(),
            detail=f"file not found: {path}",
        )

    try:
        raw = path.read_text(encoding="utf-8")
    except PermissionError:
        return SectionResult(
            status=SectionStatus.FORBIDDEN,
            items=(),
            detail=f"permission denied reading: {path}",
        )

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        return SectionResult(
            status=SectionStatus.FAILED,
            items=(),
            detail=f"malformed json in {path}: {exc}",
        )

    if isinstance(data, list):
        items = data
    elif isinstance(data, dict) and isinstance(data.get("value"), list):
        items = data["value"]
    elif isinstance(data, dict) and isinstance(data.get("results"), list):
        items = data["results"]
    else:
        return SectionResult(
            status=SectionStatus.NOT_SUPPORTED,
            items=(),
            detail=f"unsupported json shape in {path}",
        )

    seen = {}
    for item in items:
        if isinstance(item, dict) and key_property in item:
            key = item[key_property]
            seen[key] = seen.get(key, 0) + 1
    ambiguities = tuple(
        f"duplicate {key_property} {key!r} in {path.name} ({count} occurrences)"
        for key, count in seen.items()
        if count > 1
    )

    status = SectionStatus.OBSERVED if items else SectionStatus.EMPTY
    return SectionResult(status=status, items=tuple(items), detail="", ambiguities=ambiguities)


def _overall_status(statuses) -> SectionStatus:
    statuses = list(statuses)
    if not statuses:
        return SectionStatus.EMPTY
    if all(s is SectionStatus.OBSERVED for s in statuses):
        return SectionStatus.OBSERVED
    if all(s is SectionStatus.UNAVAILABLE for s in statuses):
        return SectionStatus.UNAVAILABLE
    return SectionStatus.PARTIAL


def load_schema_export(root, label: str, layout: Optional[ExportLayout] = None) -> SchemaExport:
    """Load a schema export rooted at `root`. Never writes; never raises
    for ordinary absence/permission/parse failures -- those are reported
    via `SectionStatus` on the returned sections instead."""

    layout = layout or ExportLayout()
    effective_root = Path(root)
    if layout.scope:
        effective_root = effective_root / layout.scope

    if not effective_root.is_dir():
        missing = SectionResult(
            status=SectionStatus.UNAVAILABLE,
            items=(),
            detail=f"export root not found: {effective_root}",
        )
        return SchemaExport(
            label=label,
            site_columns=missing,
            content_types=missing,
            lists=missing,
            list_fields={},
            status=SectionStatus.UNAVAILABLE,
        )

    site_columns = _load_section(
        effective_root / layout.summary_dir / layout.site_columns_file, "InternalName"
    )
    content_types = _load_section(
        effective_root / layout.summary_dir / layout.content_types_file, "Name"
    )
    lists = _load_section(effective_root / layout.summary_dir / layout.lists_file, "Title")

    list_fields: dict = {}
    for group_dir_name in (layout.lists_dir, layout.document_libraries_dir):
        group_dir = effective_root / group_dir_name
        if not group_dir.is_dir():
            continue
        for child in sorted(group_dir.iterdir()):
            if not child.is_dir():
                continue
            key = f"{group_dir_name}/{child.name}"
            list_fields[key] = _load_section(child / layout.fields_file, "InternalName")

    all_statuses = [site_columns.status, content_types.status, lists.status]
    all_statuses.extend(section.status for section in list_fields.values())

    return SchemaExport(
        label=label,
        site_columns=site_columns,
        content_types=content_types,
        lists=lists,
        list_fields=list_fields,
        status=_overall_status(all_statuses),
    )
