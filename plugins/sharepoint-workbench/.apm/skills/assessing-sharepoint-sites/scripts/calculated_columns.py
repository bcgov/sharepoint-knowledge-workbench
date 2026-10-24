"""
calculated_columns.py
======================

Purpose:
    Find calculated-type fields across an already-loaded, offline schema
    export (see `schema_export.load_schema_export`) and report each one's
    formula and the field names it references.

Layer: sharepoint-schema / scripts (plugin-local, offline).

This module is strictly read-only: it never connects to a tenant and never
mutates a field definition. It only reads what a prior, out-of-scope
collection step already exported to `fields.json` files. A field's
`TypeAsString` must equal "Calculated" (the exact convention already used by
this plugin's own export fixtures/tests) to be reported.

Not every collector captures a calculated field's `Formula` -- some
SharePoint REST exports omit it. When `Formula` is absent from the exported
record, this module reports the field with `formula=None` and an ambiguity
entry rather than fabricating a formula or silently dropping the field.
Referenced field names are extracted from `[FieldName]` bracket syntax in the
formula string, SharePoint's own calculated-column reference syntax; a
formula with no bracketed references (e.g. one calling only built-in
functions) legitimately yields an empty tuple, not an error.

Key Input Dependencies:
    - Caller-supplied SharePoint discovery exports and the plugin-local schema/analysis modules used by this script.

Function index:
    - CalculatedColumn
    - CalculatedColumnsReport
    - _referenced_fields
    - find_calculated_columns
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from schema_export import SchemaExport, SectionStatus

_FIELD_REFERENCE_PATTERN = re.compile(r"\[([^\]]+)\]")


# Represent a calculated field with its list, internal name, formula, and referenced columns.
@dataclass(frozen=True)
class CalculatedColumn:
    """Represent a calculated field with its list, internal name, formula, and referenced columns."""
    list_key: str
    internal_name: str
    display_name: str
    formula: str | None
    referenced_fields: tuple = ()


# Report calculated fields, unresolved formulas, and the source export outcome.
@dataclass(frozen=True)
class CalculatedColumnsReport:
    """Report calculated fields, unresolved formulas, and the source export outcome."""
    columns: tuple = ()
    ambiguities: tuple = ()
    status: SectionStatus = SectionStatus.UNAVAILABLE


# Extract unique bracketed field references from a calculated-column formula in first-seen order.
def _referenced_fields(formula: str) -> tuple:
    """Extract unique bracketed field references from a calculated-column formula in first-seen order."""
    return tuple(_FIELD_REFERENCE_PATTERN.findall(formula))


def find_calculated_columns(export: SchemaExport) -> CalculatedColumnsReport:
    """Find, per list/library, every field whose `TypeAsString` is
    "Calculated", reporting its `Formula` and any `[FieldName]`-style
    referenced field names. A field present without a `Formula` is surfaced
    via `ambiguities`, not silently skipped or given a fabricated value."""

    if export.status is SectionStatus.UNAVAILABLE:
        return CalculatedColumnsReport(columns=(), ambiguities=(), status=SectionStatus.UNAVAILABLE)

    columns = []
    ambiguities = []
    list_statuses = [section.status for section in export.list_fields.values()]

    for list_key in sorted(export.list_fields):
        section = export.list_fields[list_key]
        for item in section.items:
            if not isinstance(item, dict):
                continue
            if item.get("TypeAsString") != "Calculated":
                continue

            internal_name = item.get("InternalName")
            display_name = item.get("Title")
            formula = item.get("Formula")

            if formula is None:
                ambiguities.append(
                    f"{list_key}: calculated field {internal_name!r} has no Formula in this export"
                )
                referenced = ()
            else:
                referenced = _referenced_fields(formula)

            columns.append(
                CalculatedColumn(
                    list_key=list_key,
                    internal_name=internal_name,
                    display_name=display_name,
                    formula=formula,
                    referenced_fields=referenced,
                )
            )

    if not list_statuses:
        status = SectionStatus.EMPTY
    elif all(s in (SectionStatus.OBSERVED, SectionStatus.EMPTY) for s in list_statuses):
        status = SectionStatus.OBSERVED
    else:
        status = SectionStatus.PARTIAL

    return CalculatedColumnsReport(columns=tuple(columns), ambiguities=tuple(ambiguities), status=status)
