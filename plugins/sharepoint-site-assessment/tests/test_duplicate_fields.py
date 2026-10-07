"""
test_duplicate_fields.py -- contract and safety tests for duplicate-column auditing.

Purpose:
    Prove duplicate display-name detection works on an offline schema export,
    excludes SharePoint built-in and read-only columns, treats a repeated
    internal name as an ambiguity rather than a duplicate finding, and offers
    no remediation/write path of any kind.

Layer: sharepoint-schema / plugin-local tests

Key Input Dependencies:
    - duplicate_fields, schema_export (modules under test)

Function index:
    - _export
    - _load
    - test_detects_two_internal_names_sharing_one_display_name
    - test_single_internal_name_repeated_is_ambiguity_not_a_duplicate
    - test_builtin_columns_are_excluded
    - test_builtin_exclusion_list_is_caller_configurable
    - test_read_only_columns_are_excluded
    - test_fields_without_a_display_name_are_surfaced_not_guessed
    - test_missing_export_reports_unavailable_not_a_clean_pass
    - test_unreadable_list_yields_partial
    - test_module_exposes_no_remediation_or_write_capability
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import duplicate_fields as duplicate_fields_module  # noqa: E402
from duplicate_fields import find_duplicate_fields  # noqa: E402
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


# Detects two internal names sharing one display name.
def test_detects_two_internal_names_sharing_one_display_name(tmp_path):
    """Detects two internal names sharing one display name."""
    report = find_duplicate_fields(_load(tmp_path, "a", {
        "Records": [
            {"InternalName": "issued", "Title": "Issued", "ReadOnlyField": False},
            {"InternalName": "issued0", "Title": "Issued", "ReadOnlyField": False},
        ]
    }))
    assert len(report.groups) == 1
    group = report.groups[0]
    assert group.list_key == "lists/Records"
    assert group.display_name == "Issued"
    assert group.internal_names == ("issued", "issued0")


# Single internal name repeated is ambiguity not a duplicate.
def test_single_internal_name_repeated_is_ambiguity_not_a_duplicate(tmp_path):
    """Single internal name repeated is ambiguity not a duplicate."""
    report = find_duplicate_fields(_load(tmp_path, "b", {
        "Records": [
            {"InternalName": "issued", "Title": "Issued", "ReadOnlyField": False},
            {"InternalName": "issued", "Title": "Issued", "ReadOnlyField": False},
        ]
    }))
    assert report.groups == ()
    assert report.ambiguities


# Builtin columns are excluded.
def test_builtin_columns_are_excluded(tmp_path):
    """Builtin columns are excluded."""
    report = find_duplicate_fields(_load(tmp_path, "c", {
        "Records": [
            {"InternalName": "Title", "Title": "Name", "ReadOnlyField": False},
            {"InternalName": "Author", "Title": "Name", "ReadOnlyField": False},
        ]
    }))
    assert report.groups == ()


# Builtin exclusion list is caller configurable.
def test_builtin_exclusion_list_is_caller_configurable(tmp_path):
    """Builtin exclusion list is caller configurable."""
    export = _load(tmp_path, "d", {
        "Records": [
            {"InternalName": "Title", "Title": "Name", "ReadOnlyField": False},
            {"InternalName": "custom", "Title": "Name", "ReadOnlyField": False},
        ]
    })
    assert find_duplicate_fields(export).groups == ()
    assert find_duplicate_fields(export, builtin_internal_names=()).groups


# Read only columns are excluded.
def test_read_only_columns_are_excluded(tmp_path):
    """Read only columns are excluded."""
    report = find_duplicate_fields(_load(tmp_path, "e", {
        "Records": [
            {"InternalName": "calc", "Title": "Total", "ReadOnlyField": True},
            {"InternalName": "total", "Title": "Total", "ReadOnlyField": False},
        ]
    }))
    assert report.groups == ()


# Fields without a display name are surfaced not guessed.
def test_fields_without_a_display_name_are_surfaced_not_guessed(tmp_path):
    """Fields without a display name are surfaced not guessed."""
    report = find_duplicate_fields(_load(tmp_path, "f", {
        "Records": [{"InternalName": "orphan", "ReadOnlyField": False}]
    }))
    assert report.groups == ()
    assert report.ambiguities


# Missing export reports unavailable not a clean pass.
def test_missing_export_reports_unavailable_not_a_clean_pass(tmp_path):
    """Missing export reports unavailable not a clean pass."""
    report = find_duplicate_fields(load_schema_export(tmp_path / "gone", label="gone"))
    assert report.status is SectionStatus.UNAVAILABLE
    assert report.groups == ()


# Unreadable list yields partial.
def test_unreadable_list_yields_partial(tmp_path):
    """Unreadable list yields partial."""
    root = _export(tmp_path / "g", {"Ok": [{"InternalName": "a", "Title": "A"}]})
    bad = root / "lists" / "Bad" / "fields.json"
    bad.parent.mkdir(parents=True, exist_ok=True)
    bad.write_text("{{{", encoding="utf-8")
    report = find_duplicate_fields(load_schema_export(root, label="g"))
    assert report.status is SectionStatus.PARTIAL


def test_module_exposes_no_remediation_or_write_capability():
    """Legacy source script had a `-Cleanup` switch calling Remove-PnPField.

    That write path is deliberately not ported. Nothing in this module may
    delete, remove, or otherwise mutate a field.
    """
    exported = [n for n in dir(duplicate_fields_module) if not n.startswith("_")]
    forbidden = ("cleanup", "remove", "delete", "fix", "repair", "apply")
    assert not [n for n in exported if any(f in n.lower() for f in forbidden)]

    source = Path(duplicate_fields_module.__file__).read_text(encoding="utf-8")
    for token in ("Remove-PnPField", "os.remove", "shutil.rmtree", "unlink(", "write_text("):
        assert token not in source, f"write/delete path {token!r} present in duplicate_fields.py"
