"""
schema_diff.py
===============

Purpose:
    Compare two schema exports (loaded via `schema_export.load_schema_export`)
    -- site columns, content types, lists/libraries, and per-list fields --
    and render the result as deterministic Markdown.

Layer: sharepoint-schema / scripts (plugin-local, offline).

Both exports being compared are caller-labelled; no environment name
(e.g. an assumed "before"/"after" pair) is hardcoded here. Comparisons
surface ambiguity (duplicate or unkeyed items) rather than guessing, and
an unavailable export propagates into the report's own status rather
than silently producing a clean-looking, empty diff.

Key Input Dependencies:
    - Caller-supplied SharePoint discovery exports and the plugin-local schema/analysis modules used by this script.

Function index:
    - Changed
    - NamedSetDiff
    - ListComparison
    - SchemaComparisonReport
    - _index
    - compare_named_sets
    - compare_schema_exports
    - compare_schema_definitions
    - compare_definition_to_export
    - _render_named_set_diff
    - render_markdown
"""

from __future__ import annotations

from dataclasses import dataclass

from schema_definition import SiteSchemaDefinition, generate_schema_definition
from schema_export import SchemaExport, SectionStatus


# Represent a changed schema property and its old and new values.
@dataclass(frozen=True)
class Changed:
    """Represent a changed schema property and its old and new values."""
    key: str
    property: str
    left: object
    right: object


# Represent added, removed, changed, and ambiguous named schema items.
@dataclass(frozen=True)
class NamedSetDiff:
    """Represent added, removed, changed, and ambiguous named schema items."""
    only_left: tuple = ()
    only_right: tuple = ()
    changed: tuple = ()
    ambiguities: tuple = ()


# Represent the field and content-type differences for one list.
@dataclass(frozen=True)
class ListComparison:
    """Represent the field and content-type differences for one list."""
    fields: NamedSetDiff


# Hold the full schema comparison and its evidence status.
@dataclass(frozen=True)
class SchemaComparisonReport:
    """Hold the full schema comparison and its evidence status."""
    left_label: str
    right_label: str
    site_columns: NamedSetDiff
    content_types: NamedSetDiff
    lists: NamedSetDiff
    per_list: dict
    lists_only_left: tuple = ()
    lists_only_right: tuple = ()
    status: SectionStatus = SectionStatus.UNAVAILABLE


# Index named schema items and retain duplicate-key evidence instead of silently collapsing it.
def _index(items, key_property: str):
    """Index named schema items and retain duplicate-key evidence instead of silently collapsing it."""
    index: dict = {}
    duplicates: set = set()
    missing_key = 0
    for item in items:
        if not isinstance(item, dict) or key_property not in item:
            missing_key += 1
            continue
        key = item[key_property]
        if key in index:
            duplicates.add(key)
        else:
            index[key] = item
    return index, duplicates, missing_key


def compare_named_sets(
    left_items=(),
    right_items=(),
    key_property: str = "InternalName",
    compare_properties: tuple = (),
) -> NamedSetDiff:
    """Compare two collections of dict items keyed by `key_property`,
    reporting only-left/only-right keys and, for keys present on both
    sides, per-property value changes for each property named in
    `compare_properties`. Items missing the key, or a key repeated on
    one side, are excluded from the comparison and surfaced as an
    ambiguity instead of being guessed at."""

    left_index, left_dupes, left_missing = _index(left_items, key_property)
    right_index, right_dupes, right_missing = _index(right_items, key_property)

    ambiguities = []
    for key in sorted(left_dupes, key=str):
        ambiguities.append(f"duplicate {key_property} {key!r} on the left side")
    for key in sorted(right_dupes, key=str):
        ambiguities.append(f"duplicate {key_property} {key!r} on the right side")
    if left_missing:
        ambiguities.append(f"{left_missing} left item(s) missing {key_property!r}")
    if right_missing:
        ambiguities.append(f"{right_missing} right item(s) missing {key_property!r}")

    usable_left = set(left_index) - left_dupes
    usable_right = set(right_index) - right_dupes

    only_left = tuple(sorted(usable_left - usable_right, key=str))
    only_right = tuple(sorted(usable_right - usable_left, key=str))

    changed = []
    for key in sorted(usable_left & usable_right, key=str):
        left_item = left_index[key]
        right_item = right_index[key]
        for prop in compare_properties:
            left_val = left_item.get(prop)
            right_val = right_item.get(prop)
            if left_val != right_val:
                changed.append(Changed(key=key, property=prop, left=left_val, right=right_val))

    return NamedSetDiff(
        only_left=only_left, only_right=only_right, changed=tuple(changed), ambiguities=tuple(ambiguities)
    )


def compare_schema_exports(
    left: SchemaExport,
    right: SchemaExport,
    column_properties: tuple = ("TypeAsString",),
    content_type_properties: tuple = (),
    list_properties: tuple = (),
    field_properties: tuple = ("TypeAsString",),
) -> SchemaComparisonReport:
    """Compare two loaded schema exports section by section."""

    site_columns = compare_named_sets(
        left.site_columns.items, right.site_columns.items, "InternalName", column_properties
    )
    content_types = compare_named_sets(
        left.content_types.items, right.content_types.items, "Name", content_type_properties
    )
    lists = compare_named_sets(left.lists.items, right.lists.items, "Title", list_properties)

    left_keys = set(left.list_fields)
    right_keys = set(right.list_fields)
    lists_only_left = tuple(sorted(left_keys - right_keys))
    lists_only_right = tuple(sorted(right_keys - left_keys))

    per_list = {}
    for key in sorted(left_keys | right_keys):
        left_section = left.list_fields.get(key)
        right_section = right.list_fields.get(key)
        left_items = left_section.items if left_section is not None else ()
        right_items = right_section.items if right_section is not None else ()
        fields_diff = compare_named_sets(left_items, right_items, "InternalName", field_properties)
        per_list[key] = ListComparison(fields=fields_diff)

    if left.status is SectionStatus.UNAVAILABLE or right.status is SectionStatus.UNAVAILABLE:
        status = SectionStatus.UNAVAILABLE
    elif left.status is not SectionStatus.OBSERVED or right.status is not SectionStatus.OBSERVED:
        status = SectionStatus.PARTIAL
    else:
        status = SectionStatus.OBSERVED

    return SchemaComparisonReport(
        left_label=left.label,
        right_label=right.label,
        site_columns=site_columns,
        content_types=content_types,
        lists=lists,
        per_list=per_list,
        lists_only_left=lists_only_left,
        lists_only_right=lists_only_right,
        status=status,
    )


def compare_schema_definitions(
    left: SiteSchemaDefinition,
    right: SiteSchemaDefinition,
    left_label: str = None,
    right_label: str = None,
    column_properties: tuple = ("type_as_string",),
    content_type_properties: tuple = (),
    list_properties: tuple = (),
    field_properties: tuple = ("type_as_string",),
) -> SchemaComparisonReport:
    """Compare two declarative `SiteSchemaDefinition` objects (see
    `schema_definition.py`), section by section. Mirrors
    `compare_schema_exports`' semantics exactly -- named-set comparison,
    duplicate/missing-key ambiguity surfaced not guessed, a list present on
    only one side reported not dropped, deterministic output -- over the
    declarative shape instead of a raw export.

    `left_label`/`right_label` default to each definition's own `.label`
    when not supplied, so a caller can still override display labels for a
    report without the definition itself needing to change.

    A `SiteSchemaDefinition` has a single `key` per list (unlike a raw
    export, which has both a title-keyed summary list and a separately
    directory-keyed `list_fields`), so `lists` here is compared by `key` and
    doubles as the only-left/only-right list membership signal;
    `lists_only_left`/`lists_only_right` are populated from the same
    comparison for parity with `compare_schema_exports`' report shape.
    """

    left_label = left.label if left_label is None else left_label
    right_label = right.label if right_label is None else right_label

    site_columns = compare_named_sets(
        [f.to_dict() for f in left.site_columns],
        [f.to_dict() for f in right.site_columns],
        "internal_name",
        column_properties,
    )
    content_types = compare_named_sets(
        [ct.to_dict() for ct in left.content_types],
        [ct.to_dict() for ct in right.content_types],
        "name",
        content_type_properties,
    )
    lists = compare_named_sets(
        [l.to_dict() for l in left.lists],
        [l.to_dict() for l in right.lists],
        "key",
        list_properties,
    )

    left_by_key = {l.key: l for l in left.lists}
    right_by_key = {l.key: l for l in right.lists}
    all_keys = set(left_by_key) | set(right_by_key)

    per_list = {}
    for key in sorted(all_keys, key=str):
        left_list = left_by_key.get(key)
        right_list = right_by_key.get(key)
        left_fields = [f.to_dict() for f in left_list.fields] if left_list is not None else []
        right_fields = [f.to_dict() for f in right_list.fields] if right_list is not None else []
        fields_diff = compare_named_sets(left_fields, right_fields, "internal_name", field_properties)
        per_list[key] = ListComparison(fields=fields_diff)

    if left.status is SectionStatus.UNAVAILABLE or right.status is SectionStatus.UNAVAILABLE:
        status = SectionStatus.UNAVAILABLE
    elif left.status is not SectionStatus.OBSERVED or right.status is not SectionStatus.OBSERVED:
        status = SectionStatus.PARTIAL
    else:
        status = SectionStatus.OBSERVED

    return SchemaComparisonReport(
        left_label=left_label,
        right_label=right_label,
        site_columns=site_columns,
        content_types=content_types,
        lists=lists,
        per_list=per_list,
        lists_only_left=lists.only_left,
        lists_only_right=lists.only_right,
        status=status,
    )


def compare_definition_to_export(
    definition: SiteSchemaDefinition,
    export: SchemaExport,
    definition_label: str = None,
    export_label: str = None,
    column_properties: tuple = ("type_as_string",),
    content_type_properties: tuple = (),
    list_properties: tuple = (),
    field_properties: tuple = ("type_as_string",),
) -> SchemaComparisonReport:
    """Compare a declarative `SiteSchemaDefinition` against a live
    `SchemaExport` -- "what would change if I applied this target
    definition against this current state". Read-only; produces a report,
    never a write/apply plan.

    Implementation choice: the export is first converted to its own
    `SiteSchemaDefinition` via `generate_schema_definition` (a pure,
    already-existing transform -- see `schema_definition.py`), then compared
    via `compare_schema_definitions`. This is the cleanest path because it
    means there is exactly one place (`compare_schema_definitions`) that
    knows how to diff the declarative shape; diffing at a lower level would
    require re-deriving the same named-set/per-list logic a second time
    against export's raw dict items, duplicating -- and risking drift from
    -- the semantics already established for definition-vs-definition
    comparison. `generate_schema_definition` already carries the export's
    honest `SectionStatus` through unchanged, so a degraded export produces
    a degraded definition, and that degradation flows into the comparison
    report exactly as it would for two hand-built definitions.
    """

    export_label = export.label if export_label is None else export_label
    export_as_definition = generate_schema_definition(export, label=export_label)

    definition_label = definition.label if definition_label is None else definition_label

    return compare_schema_definitions(
        definition,
        export_as_definition,
        left_label=definition_label,
        right_label=export_label,
        column_properties=column_properties,
        content_type_properties=content_type_properties,
        list_properties=list_properties,
        field_properties=field_properties,
    )


# Render one named-set comparison, including additions, removals, and ambiguities.
def _render_named_set_diff(diff: NamedSetDiff) -> list:
    """Render one named-set comparison, including additions, removals, and ambiguities."""
    lines = []
    if diff.only_left:
        lines.append(f"- Only on the left: {', '.join(str(v) for v in diff.only_left)}")
    if diff.only_right:
        lines.append(f"- Only on the right: {', '.join(str(v) for v in diff.only_right)}")
    for c in diff.changed:
        lines.append(f"- Changed `{c.key}` ({c.property}): {c.left!r} -> {c.right!r}")
    for a in diff.ambiguities:
        lines.append(f"- Ambiguity: {a}")
    if not (diff.only_left or diff.only_right or diff.changed or diff.ambiguities):
        lines.append("- No differences")
    return lines


def render_markdown(report: SchemaComparisonReport) -> str:
    """Render a deterministic Markdown comparison report. Carries no
    timestamp, host, or tenant-URL information -- only the caller-supplied
    labels and the comparison results themselves."""

    lines = ["# Schema Comparison", ""]
    lines.append(f"- Left: {report.left_label}")
    lines.append(f"- Right: {report.right_label}")
    lines.append(f"- Status: {report.status.value}")
    lines.append("")

    lines.append("## Site Columns")
    lines.extend(_render_named_set_diff(report.site_columns))
    lines.append("")

    lines.append("## Content Types")
    lines.extend(_render_named_set_diff(report.content_types))
    lines.append("")

    lines.append("## Lists And Libraries")
    lines.extend(_render_named_set_diff(report.lists))
    if report.lists_only_left:
        lines.append(f"- Present only on the left: {', '.join(report.lists_only_left)}")
    if report.lists_only_right:
        lines.append(f"- Present only on the right: {', '.join(report.lists_only_right)}")
    lines.append("")

    lines.append("## Per-List Fields")
    if report.per_list:
        for key in sorted(report.per_list):
            lines.append(f"### {key}")
            lines.extend(_render_named_set_diff(report.per_list[key].fields))
    else:
        lines.append("- No lists or libraries to compare")

    return "\n".join(lines) + "\n"
