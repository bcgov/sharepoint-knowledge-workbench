"""
test_calculated_columns.py -- contract and safety tests for calculated-column
discovery.

Purpose:
    Prove calculated-field discovery works on an offline schema export, only
    matches fields typed "Calculated", reports each field's Formula and any
    referenced field names (extracted from `[FieldName]` bracket syntax),
    honestly surfaces fields where the Formula is absent from the export
    rather than fabricating one, and offers no remediation/write path.

Layer: sharepoint-schema / plugin-local tests

Key Input Dependencies:
    - calculated_columns, schema_export (modules under test)

Function index:
    - _export
    - _load
    - test_finds_calculated_field_with_formula_and_referenced_fields
    - test_non_calculated_fields_are_ignored
    - test_missing_formula_is_surfaced_not_fabricated
    - test_formula_with_no_bracketed_references_yields_empty_tuple
    - test_missing_export_reports_unavailable_not_a_clean_pass
    - test_unreadable_list_yields_partial
    - test_module_exposes_no_remediation_or_write_capability
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import calculated_columns as calculated_columns_module  # noqa: E402
from calculated_columns import find_calculated_columns  # noqa: E402
from schema_export import SectionStatus, load_schema_export  # noqa: E402


# Create and return a neutral schema-export fixture at the requested test path.
def _export(root: Path, list_fields):
    """Create and return a neutral schema-export fixture at the requested test path."""
    for name, fields in list_fields.items():
        path = root / "lists" / name / "fields.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(fields), encoding="utf-8")
    return root


# Load a schema export fixture with the test label and default layout.
def _load(tmp_path, name, list_fields):
    """Load a schema export fixture with the test label and default layout."""
    return load_schema_export(_export(tmp_path / name, list_fields), label=name)


# Finds calculated field with formula and referenced fields.
def test_finds_calculated_field_with_formula_and_referenced_fields(tmp_path):
    """Finds calculated field with formula and referenced fields."""
    report = find_calculated_columns(_load(tmp_path, "a", {
        "Records": [
            {"InternalName": "total", "Title": "Total", "TypeAsString": "Calculated",
             "Formula": "=[Quantity]*[UnitPrice]"},
            {"InternalName": "qty", "Title": "Quantity", "TypeAsString": "Number"},
        ]
    }))
    assert len(report.columns) == 1
    column = report.columns[0]
    assert column.list_key == "lists/Records"
    assert column.internal_name == "total"
    assert column.display_name == "Total"
    assert column.formula == "=[Quantity]*[UnitPrice]"
    assert column.referenced_fields == ("Quantity", "UnitPrice")


# Non calculated fields are ignored.
def test_non_calculated_fields_are_ignored(tmp_path):
    """Non calculated fields are ignored."""
    report = find_calculated_columns(_load(tmp_path, "b", {
        "Records": [
            {"InternalName": "qty", "Title": "Quantity", "TypeAsString": "Number"},
            {"InternalName": "note", "Title": "Note", "TypeAsString": "Text"},
        ]
    }))
    assert report.columns == ()


# Missing formula is surfaced not fabricated.
def test_missing_formula_is_surfaced_not_fabricated(tmp_path):
    """Missing formula is surfaced not fabricated."""
    report = find_calculated_columns(_load(tmp_path, "c", {
        "Records": [
            {"InternalName": "total", "Title": "Total", "TypeAsString": "Calculated"},
        ]
    }))
    assert len(report.columns) == 1
    column = report.columns[0]
    assert column.formula is None
    assert column.referenced_fields == ()
    assert report.ambiguities


# Formula with no bracketed references yields empty tuple.
def test_formula_with_no_bracketed_references_yields_empty_tuple(tmp_path):
    """Formula with no bracketed references yields empty tuple."""
    report = find_calculated_columns(_load(tmp_path, "d", {
        "Records": [
            {"InternalName": "today", "Title": "Today", "TypeAsString": "Calculated",
             "Formula": "=TODAY()"},
        ]
    }))
    assert report.columns[0].referenced_fields == ()


# Missing export reports unavailable not a clean pass.
def test_missing_export_reports_unavailable_not_a_clean_pass(tmp_path):
    """Missing export reports unavailable not a clean pass."""
    report = find_calculated_columns(load_schema_export(tmp_path / "gone", label="gone"))
    assert report.status is SectionStatus.UNAVAILABLE
    assert report.columns == ()


# Unreadable list yields partial.
def test_unreadable_list_yields_partial(tmp_path):
    """Unreadable list yields partial."""
    root = _export(tmp_path / "e", {"Ok": [{"InternalName": "a", "Title": "A", "TypeAsString": "Text"}]})
    bad = root / "lists" / "Bad" / "fields.json"
    bad.parent.mkdir(parents=True, exist_ok=True)
    bad.write_text("{{{", encoding="utf-8")
    report = find_calculated_columns(load_schema_export(root, label="e"))
    assert report.status is SectionStatus.PARTIAL


def test_module_exposes_no_remediation_or_write_capability():
    """This module only reads already-exported fields.json files.

    It never connects to a tenant and never mutates a field definition.
    """
    exported = [n for n in dir(calculated_columns_module) if not n.startswith("_")]
    forbidden = ("cleanup", "remove", "delete", "fix", "repair", "apply")
    assert not [n for n in exported if any(f in n.lower() for f in forbidden)]

    source = Path(calculated_columns_module.__file__).read_text(encoding="utf-8")
    for token in ("Remove-PnPField", "os.remove", "shutil.rmtree", "unlink(", "write_text("):
        assert token not in source, f"write/delete path {token!r} present in calculated_columns.py"
