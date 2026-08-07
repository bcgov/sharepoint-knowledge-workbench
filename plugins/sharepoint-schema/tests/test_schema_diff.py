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
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from schema_diff import (  # noqa: E402
    compare_named_sets,
    compare_schema_exports,
    render_markdown,
)
from schema_export import SectionStatus, load_schema_export  # noqa: E402


def _write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _export(root: Path, columns, lists, list_fields):
    _write_json(root / "summary" / "site_columns.json", columns)
    _write_json(root / "summary" / "content_types.json", [])
    _write_json(root / "summary" / "lists.json", lists)
    for name, fields in list_fields.items():
        _write_json(root / "lists" / name / "fields.json", fields)
    return root


def test_compare_named_sets_reports_both_sides_and_changes():
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


def test_compare_named_sets_surfaces_duplicate_keys_as_ambiguity():
    diff = compare_named_sets(
        left_items=[{"InternalName": "A", "TypeAsString": "Text"},
                    {"InternalName": "A", "TypeAsString": "Note"}],
        right_items=[{"InternalName": "A", "TypeAsString": "Text"}],
        key_property="InternalName",
        compare_properties=("TypeAsString",),
    )
    assert diff.ambiguities
    assert any("A" in a for a in diff.ambiguities)


def test_compare_named_sets_skips_items_missing_the_key_and_records_it():
    diff = compare_named_sets(
        left_items=[{"TypeAsString": "Text"}],
        right_items=[],
        key_property="InternalName",
    )
    assert diff.only_left == ()
    assert diff.ambiguities


def test_labels_are_caller_supplied_not_hardcoded_environment_names(tmp_path):
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


def test_per_list_field_and_content_type_variances_are_reported(tmp_path):
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


def test_list_present_on_only_one_side_is_not_silently_dropped(tmp_path):
    left = load_schema_export(
        _export(tmp_path / "l2", [], [], {"OnlyLeft": [{"InternalName": "A"}]}), label="l2")
    right = load_schema_export(_export(tmp_path / "r2", [], [], {}), label="r2")
    report = compare_schema_exports(left, right)
    assert "lists/OnlyLeft" in report.lists_only_left


def test_missing_export_makes_the_report_unavailable_not_a_clean_pass(tmp_path):
    left = load_schema_export(_export(tmp_path / "l3", [], [], {}), label="l3")
    right = load_schema_export(tmp_path / "nowhere", label="r3")
    report = compare_schema_exports(left, right)
    assert report.status in (SectionStatus.UNAVAILABLE, SectionStatus.PARTIAL)
    assert "unavailable" in render_markdown(report).lower()


def test_render_markdown_is_deterministic(tmp_path):
    left = load_schema_export(
        _export(tmp_path / "d1", [{"InternalName": "B"}, {"InternalName": "A"}], [], {}), label="x")
    right = load_schema_export(_export(tmp_path / "d2", [], [], {}), label="y")
    assert render_markdown(compare_schema_exports(left, right)) == render_markdown(
        compare_schema_exports(left, right))


def test_render_markdown_carries_no_timestamp_or_host_identifiers(tmp_path):
    left = load_schema_export(_export(tmp_path / "t1", [], [], {}), label="x")
    right = load_schema_export(_export(tmp_path / "t2", [], [], {}), label="y")
    markdown = render_markdown(compare_schema_exports(left, right))
    assert "sharepoint.com" not in markdown
    assert "https://" not in markdown


def test_compare_properties_are_caller_configurable(tmp_path):
    left = load_schema_export(
        _export(tmp_path / "c1", [{"InternalName": "A", "Hidden": True}], [], {}), label="x")
    right = load_schema_export(
        _export(tmp_path / "c2", [{"InternalName": "A", "Hidden": False}], [], {}), label="y")
    assert compare_schema_exports(left, right, column_properties=()).site_columns.changed == ()
    assert compare_schema_exports(
        left, right, column_properties=("Hidden",)).site_columns.changed
