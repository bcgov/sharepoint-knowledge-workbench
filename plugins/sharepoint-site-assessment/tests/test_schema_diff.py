"""
test_schema_diff.py -- contract tests for the two-export schema comparison.

Purpose:
    Prove the schema differ compares two arbitrary, caller-labelled schema
    exports (site columns, content types, lists/libraries, per-list fields and
    content-type assignments), surfaces ambiguity rather than guessing, and
    propagates honest partial-failure status into the report.

Layer: sharepoint-schema / plugin-local tests

Key Input Dependencies:
    - schema_diff, schema_export (modules under test)

Function index:
    - _write_json
    - _export
    - test_compare_named_sets_reports_both_sides_and_changes
    - test_compare_named_sets_surfaces_duplicate_keys_as_ambiguity
    - test_compare_named_sets_skips_items_missing_the_key_and_records_it
    - test_labels_are_caller_supplied_not_hardcoded_environment_names
    - test_per_list_field_and_content_type_variances_are_reported
    - test_list_present_on_only_one_side_is_not_silently_dropped
    - test_missing_export_makes_the_report_unavailable_not_a_clean_pass
    - test_render_markdown_is_deterministic
    - test_render_markdown_carries_no_timestamp_or_host_identifiers
    - test_compare_schema_definitions_reports_differences
    - test_definition_generated_from_export_compares_identical_to_that_export
    - test_degraded_definition_side_is_reported_honestly_not_a_clean_pass
    - test_compare_definition_to_export_propagates_export_degradation
    - test_compare_properties_are_caller_configurable
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from schema_diff import (  # noqa: E402
    compare_definition_to_export,
    compare_named_sets,
    compare_schema_definitions,
    compare_schema_exports,
    render_markdown,
)
from schema_definition import generate_schema_definition  # noqa: E402
from schema_export import SectionStatus, load_schema_export  # noqa: E402


# Write a JSON fixture under the supplied test directory.
def _write_json(path: Path, payload) -> None:
    """Write a JSON fixture under the supplied test directory."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


# Create and return a neutral schema-export fixture at the requested test path.
def _export(root: Path, columns, lists, list_fields):
    """Create and return a neutral schema-export fixture at the requested test path."""
    _write_json(root / "summary" / "site_columns.json", columns)
    _write_json(root / "summary" / "content_types.json", [])
    _write_json(root / "summary" / "lists.json", lists)
    for name, fields in list_fields.items():
        _write_json(root / "lists" / name / "fields.json", fields)
    return root


# Compare named sets reports both sides and changes.
def test_compare_named_sets_reports_both_sides_and_changes():
    """Compare named sets reports both sides and changes."""
    diff = compare_named_sets(
        left_items=[{"InternalName": "A", "TypeAsString": "Text"},
                    {"InternalName": "B", "TypeAsString": "Text"}],
        right_items=[{"InternalName": "B", "TypeAsString": "Note"},
                     {"InternalName": "C", "TypeAsString": "Text"}],
        key_property="InternalName",
        compare_properties=("TypeAsString",),
    )
    assert diff.only_left == ("A",)
    assert diff.only_right == ("C",)
    assert len(diff.changed) == 1
    assert diff.changed[0].key == "B"
    assert diff.changed[0].left == "Text"
    assert diff.changed[0].right == "Note"


# Compare named sets surfaces duplicate keys as ambiguity.
def test_compare_named_sets_surfaces_duplicate_keys_as_ambiguity():
    """Compare named sets surfaces duplicate keys as ambiguity."""
    diff = compare_named_sets(
        left_items=[{"InternalName": "A", "TypeAsString": "Text"},
                    {"InternalName": "A", "TypeAsString": "Note"}],
        right_items=[{"InternalName": "A", "TypeAsString": "Text"}],
        key_property="InternalName",
        compare_properties=("TypeAsString",),
    )
    assert diff.ambiguities
    assert any("A" in a for a in diff.ambiguities)


# Compare named sets skips items missing the key and records it.
def test_compare_named_sets_skips_items_missing_the_key_and_records_it():
    """Compare named sets skips items missing the key and records it."""
    diff = compare_named_sets(
        left_items=[{"TypeAsString": "Text"}],
        right_items=[],
        key_property="InternalName",
    )
    assert diff.only_left == ()
    assert diff.ambiguities


# Labels are caller supplied not hardcoded environment names.
def test_labels_are_caller_supplied_not_hardcoded_environment_names(tmp_path):
    """Labels are caller supplied not hardcoded environment names."""
    left = load_schema_export(
        _export(tmp_path / "a", [{"InternalName": "A"}], [], {}), label="baseline")
    right = load_schema_export(
        _export(tmp_path / "b", [{"InternalName": "A"}], [], {}), label="candidate")
    report = compare_schema_exports(left, right)
    assert report.left_label == "baseline"
    assert report.right_label == "candidate"
    markdown = render_markdown(report)
    assert "baseline" in markdown and "candidate" in markdown
    assert "PROD" not in markdown and "TEST" not in markdown


# Per list field and content type variances are reported.
def test_per_list_field_and_content_type_variances_are_reported(tmp_path):
    """Per list field and content type variances are reported."""
    left = load_schema_export(
        _export(
            tmp_path / "l",
            [],
            [{"Title": "Records", "IsLibrary": False}],
            {"Records": [{"InternalName": "Alpha", "TypeAsString": "Text"},
                         {"InternalName": "Beta", "TypeAsString": "Text"}]},
        ),
        label="l",
    )
    right = load_schema_export(
        _export(
            tmp_path / "r",
            [],
            [{"Title": "Records", "IsLibrary": False}],
            {"Records": [{"InternalName": "Alpha", "TypeAsString": "Note"}]},
        ),
        label="r",
    )
    report = compare_schema_exports(left, right)
    per_list = report.per_list["lists/Records"]
    assert per_list.fields.only_left == ("Beta",)
    assert [v.key for v in per_list.fields.changed] == ["Alpha"]


# List present on only one side is not silently dropped.
def test_list_present_on_only_one_side_is_not_silently_dropped(tmp_path):
    """List present on only one side is not silently dropped."""
    left = load_schema_export(
        _export(tmp_path / "l2", [], [], {"OnlyLeft": [{"InternalName": "A"}]}), label="l2")
    right = load_schema_export(_export(tmp_path / "r2", [], [], {}), label="r2")
    report = compare_schema_exports(left, right)
    assert "lists/OnlyLeft" in report.lists_only_left


# Missing export makes the report unavailable not a clean pass.
def test_missing_export_makes_the_report_unavailable_not_a_clean_pass(tmp_path):
    """Missing export makes the report unavailable not a clean pass."""
    left = load_schema_export(_export(tmp_path / "l3", [], [], {}), label="l3")
    right = load_schema_export(tmp_path / "nowhere", label="r3")
    report = compare_schema_exports(left, right)
    assert report.status in (SectionStatus.UNAVAILABLE, SectionStatus.PARTIAL)
    assert "unavailable" in render_markdown(report).lower()


# Render markdown is deterministic.
def test_render_markdown_is_deterministic(tmp_path):
    """Render markdown is deterministic."""
    left = load_schema_export(
        _export(tmp_path / "d1", [{"InternalName": "B"}, {"InternalName": "A"}], [], {}), label="x")
    right = load_schema_export(_export(tmp_path / "d2", [], [], {}), label="y")
    assert render_markdown(compare_schema_exports(left, right)) == render_markdown(
        compare_schema_exports(left, right))


# Render markdown carries no timestamp or host identifiers.
def test_render_markdown_carries_no_timestamp_or_host_identifiers(tmp_path):
    """Render markdown carries no timestamp or host identifiers."""
    left = load_schema_export(_export(tmp_path / "t1", [], [], {}), label="x")
    right = load_schema_export(_export(tmp_path / "t2", [], [], {}), label="y")
    markdown = render_markdown(compare_schema_exports(left, right))
    assert "sharepoint.com" not in markdown
    assert "https://" not in markdown


# Compare schema definitions reports differences.
def test_compare_schema_definitions_reports_differences(tmp_path):
    """Compare schema definitions reports differences."""
    left = generate_schema_definition(
        load_schema_export(
            _export(
                tmp_path / "dl",
                [{"InternalName": "A", "TypeAsString": "Text"},
                 {"InternalName": "B", "TypeAsString": "Text"}],
                [{"Title": "Records", "IsLibrary": False}],
                {"Records": [{"InternalName": "Alpha", "TypeAsString": "Text"}]},
            ),
            label="dl",
        ),
        label="left-def",
    )
    right = generate_schema_definition(
        load_schema_export(
            _export(
                tmp_path / "dr",
                [{"InternalName": "B", "TypeAsString": "Note"},
                 {"InternalName": "C", "TypeAsString": "Text"}],
                [{"Title": "Records", "IsLibrary": False}],
                {"Records": [{"InternalName": "Alpha", "TypeAsString": "Note"}]},
            ),
            label="dr",
        ),
        label="right-def",
    )

    report = compare_schema_definitions(left, right, left_label="baseline", right_label="candidate")

    assert report.left_label == "baseline"
    assert report.right_label == "candidate"
    assert report.site_columns.only_left == ("A",)
    assert report.site_columns.only_right == ("C",)
    assert [c.key for c in report.site_columns.changed] == ["B"]
    assert report.per_list["lists/Records"].fields.changed
    assert report.status is SectionStatus.PARTIAL


# Definition generated from export compares identical to that export.
def test_definition_generated_from_export_compares_identical_to_that_export(tmp_path):
    """Definition generated from export compares identical to that export."""
    export = load_schema_export(
        _export(
            tmp_path / "eq",
            [{"InternalName": "A", "TypeAsString": "Text"}],
            [{"Title": "Records", "IsLibrary": False}],
            {"Records": [{"InternalName": "Alpha", "TypeAsString": "Text"}]},
        ),
        label="export-side",
    )
    definition = generate_schema_definition(export, label="definition-side")

    report = compare_definition_to_export(definition, export)

    assert report.site_columns.only_left == () and report.site_columns.only_right == ()
    assert report.site_columns.changed == ()
    assert report.lists.only_left == () and report.lists.only_right == ()
    assert report.per_list["lists/Records"].fields.only_left == ()
    assert report.per_list["lists/Records"].fields.only_right == ()
    assert report.per_list["lists/Records"].fields.changed == ()
    assert report.status is SectionStatus.PARTIAL


# Degraded definition side is reported honestly not a clean pass.
def test_degraded_definition_side_is_reported_honestly_not_a_clean_pass(tmp_path):
    """Degraded definition side is reported honestly not a clean pass."""
    clean_export = load_schema_export(
        _export(tmp_path / "clean", [{"InternalName": "A"}], [], {}), label="clean"
    )
    clean_definition = generate_schema_definition(clean_export, label="clean-def")

    missing_export = load_schema_export(tmp_path / "does-not-exist", label="missing")
    degraded_definition = generate_schema_definition(missing_export, label="missing-def")
    assert degraded_definition.status is SectionStatus.UNAVAILABLE

    report = compare_schema_definitions(clean_definition, degraded_definition)

    assert report.status is SectionStatus.UNAVAILABLE
    assert "unavailable" in render_markdown(report).lower()


# Compare definition to export propagates export degradation.
def test_compare_definition_to_export_propagates_export_degradation(tmp_path):
    """Compare definition to export propagates export degradation."""
    clean_export = load_schema_export(
        _export(tmp_path / "clean2", [{"InternalName": "A"}], [], {}), label="clean2"
    )
    clean_definition = generate_schema_definition(clean_export, label="clean2-def")

    missing_export = load_schema_export(tmp_path / "still-nowhere", label="missing2")

    report = compare_definition_to_export(clean_definition, missing_export)

    assert report.status is SectionStatus.UNAVAILABLE
    assert "unavailable" in render_markdown(report).lower()


# Compare properties are caller configurable.
def test_compare_properties_are_caller_configurable(tmp_path):
    """Compare properties are caller configurable."""
    left = load_schema_export(
        _export(tmp_path / "c1", [{"InternalName": "A", "Hidden": True}], [], {}), label="x")
    right = load_schema_export(
        _export(tmp_path / "c2", [{"InternalName": "A", "Hidden": False}], [], {}), label="y")
    assert compare_schema_exports(left, right, column_properties=()).site_columns.changed == ()
    assert compare_schema_exports(
        left, right, column_properties=("Hidden",)).site_columns.changed
