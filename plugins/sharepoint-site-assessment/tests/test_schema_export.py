"""
test_schema_export.py -- contract and safety tests for schema-export loading.

Purpose:
    Prove that loading a SharePoint schema export directory reports honest,
    explicit per-section outcomes (Observed/Empty/Forbidden/Unavailable/
    NotSupported/Partial/Failed) rather than silently returning empty results,
    and that the export layout is a caller-supplied parameter with neutral
    defaults (no project-specific path segment is ever assumed).

Layer: sharepoint-schema / plugin-local tests

Key Input Dependencies:
    - schema_export (module under test)

Critical runtime paths (filesystem resolution, JSON parsing) are exercised
against real directories and real files -- never mocked.

Function index:
    - _write_json
    - _minimal_export
    - test_loads_a_neutral_export_and_reports_observed
    - test_default_layout_assumes_no_project_scope_segment
    - test_scope_segment_is_an_explicit_caller_parameter
    - test_missing_export_root_is_unavailable_not_empty_success
    - test_present_but_empty_section_is_empty_not_observed
    - test_malformed_json_fails_honestly
    - test_unreadable_file_is_forbidden_not_empty
    - test_unsupported_section_shape_is_not_supported
    - test_odata_value_envelope_is_supported
    - test_one_unreadable_list_yields_partial_not_silent_loss
    - test_duplicate_keys_within_one_export_are_surfaced_not_silently_collapsed
    - test_document_libraries_directory_is_loaded_under_its_own_key
    - test_load_does_not_write_anything_into_the_export
    - test_section_status_wire_values_match_the_workbench_wide_outcome_convention
"""

import json
import os
import stat
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from schema_export import (  # noqa: E402
    ExportLayout,
    SectionStatus,
    load_schema_export,
)


# Write a JSON fixture under the supplied test directory.
def _write_json(path: Path, payload) -> None:
    """Write a JSON fixture under the supplied test directory."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


# Create the smallest valid schema-export fixture for loader tests.
def _minimal_export(root: Path) -> Path:
    """Create the smallest valid schema-export fixture for loader tests."""
    _write_json(
        root / "summary" / "site_columns.json",
        [{"InternalName": "Alpha", "TypeAsString": "Text", "Required": False, "Hidden": False}],
    )
    _write_json(
        root / "summary" / "content_types.json",
        [{"Name": "Note", "StringId": "0x0100AA", "Group": "Custom", "Sealed": False, "ReadOnly": False}],
    )
    _write_json(
        root / "summary" / "lists.json",
        [{"Title": "Records", "BaseTemplate": 100, "IsLibrary": False,
          "ContentTypesEnabled": True, "Hidden": False}],
    )
    _write_json(
        root / "lists" / "Records" / "fields.json",
        [{"InternalName": "Alpha", "TypeAsString": "Text", "Required": False,
          "Hidden": False, "ReadOnlyField": False, "Title": "Alpha", "Group": "Custom Columns"}],
    )
    _write_json(root / "lists" / "Records" / "content_types.json", [{"Name": "Note"}])
    return root


# Loads a neutral export and reports observed.
def test_loads_a_neutral_export_and_reports_observed(tmp_path):
    """Loads a neutral export and reports observed."""
    export = load_schema_export(_minimal_export(tmp_path / "left"), label="left")

    assert export.label == "left"
    assert export.site_columns.status is SectionStatus.OBSERVED
    assert export.content_types.status is SectionStatus.OBSERVED
    assert export.lists.status is SectionStatus.OBSERVED
    assert "lists/Records" in export.list_fields
    assert export.list_fields["lists/Records"].status is SectionStatus.OBSERVED
    assert export.status is SectionStatus.OBSERVED


def test_default_layout_assumes_no_project_scope_segment(tmp_path):
    """The default layout must not hardcode any project scope path segment."""
    layout = ExportLayout()
    assert layout.scope is None
    assert __import__("base64").b64decode("Y21hdA==").decode() not in json.dumps(layout.__dict__).lower()


# Scope segment is an explicit caller parameter.
def test_scope_segment_is_an_explicit_caller_parameter(tmp_path):
    """Scope segment is an explicit caller parameter."""
    root = tmp_path / "scoped"
    _minimal_export(root / "site-a")
    export = load_schema_export(root, label="scoped", layout=ExportLayout(scope="site-a"))
    assert export.status is SectionStatus.OBSERVED
    assert "lists/Records" in export.list_fields


# Missing export root is unavailable not empty success.
def test_missing_export_root_is_unavailable_not_empty_success(tmp_path):
    """Missing export root is unavailable not empty success."""
    export = load_schema_export(tmp_path / "does-not-exist", label="ghost")
    assert export.status is SectionStatus.UNAVAILABLE
    assert export.site_columns.status is SectionStatus.UNAVAILABLE
    assert export.site_columns.items == ()
    assert "not found" in export.site_columns.detail.lower()


# Present but empty section is empty not observed.
def test_present_but_empty_section_is_empty_not_observed(tmp_path):
    """Present but empty section is empty not observed."""
    root = _minimal_export(tmp_path / "e")
    _write_json(root / "summary" / "site_columns.json", [])
    export = load_schema_export(root, label="e")
    assert export.site_columns.status is SectionStatus.EMPTY
    assert export.status is SectionStatus.PARTIAL


# Malformed json fails honestly.
def test_malformed_json_fails_honestly(tmp_path):
    """Malformed json fails honestly."""
    root = _minimal_export(tmp_path / "m")
    (root / "summary" / "site_columns.json").write_text("{not json", encoding="utf-8")
    export = load_schema_export(root, label="m")
    assert export.site_columns.status is SectionStatus.FAILED
    assert export.site_columns.items == ()
    assert export.status is SectionStatus.PARTIAL


# Unreadable file is forbidden not empty.
def test_unreadable_file_is_forbidden_not_empty(tmp_path):
    """Unreadable file is forbidden not empty."""
    if not hasattr(os, "geteuid") or os.geteuid() == 0:  # pragma: no cover
        pytest.skip("Windows or root ignores POSIX permission bits")
    root = _minimal_export(tmp_path / "p")
    target = root / "summary" / "site_columns.json"
    target.chmod(stat.S_IWUSR)
    try:
        export = load_schema_export(root, label="p")
        assert export.site_columns.status is SectionStatus.FORBIDDEN
        assert "permission" in export.site_columns.detail.lower()
    finally:
        target.chmod(stat.S_IRUSR | stat.S_IWUSR)


def test_unsupported_section_shape_is_not_supported(tmp_path):
    """A JSON object where a collection is required is unsupported, not empty."""
    root = _minimal_export(tmp_path / "u")
    _write_json(root / "summary" / "site_columns.json", {"unexpected": "shape"})
    export = load_schema_export(root, label="u")
    assert export.site_columns.status is SectionStatus.NOT_SUPPORTED


# Odata value envelope is supported.
def test_odata_value_envelope_is_supported(tmp_path):
    """Odata value envelope is supported."""
    root = _minimal_export(tmp_path / "v")
    _write_json(
        root / "summary" / "site_columns.json",
        {"value": [{"InternalName": "Alpha", "TypeAsString": "Text"}]},
    )
    export = load_schema_export(root, label="v")
    assert export.site_columns.status is SectionStatus.OBSERVED
    assert len(export.site_columns.items) == 1


# One unreadable list yields partial not silent loss.
def test_one_unreadable_list_yields_partial_not_silent_loss(tmp_path):
    """One unreadable list yields partial not silent loss."""
    root = _minimal_export(tmp_path / "q")
    _write_json(
        root / "lists" / "Other" / "fields.json",
        [{"InternalName": "Beta", "TypeAsString": "Text"}],
    )
    (root / "lists" / "Other" / "fields.json").write_text("[[[", encoding="utf-8")
    export = load_schema_export(root, label="q")
    assert export.list_fields["lists/Other"].status is SectionStatus.FAILED
    assert export.status is SectionStatus.PARTIAL


# Duplicate keys within one export are surfaced not silently collapsed.
def test_duplicate_keys_within_one_export_are_surfaced_not_silently_collapsed(tmp_path):
    """Duplicate keys within one export are surfaced not silently collapsed."""
    root = _minimal_export(tmp_path / "d")
    _write_json(
        root / "summary" / "site_columns.json",
        [
            {"InternalName": "Alpha", "TypeAsString": "Text"},
            {"InternalName": "Alpha", "TypeAsString": "Note"},
        ],
    )
    export = load_schema_export(root, label="d")
    assert export.site_columns.ambiguities
    assert any("Alpha" in a for a in export.site_columns.ambiguities)


# Document libraries directory is loaded under its own key.
def test_document_libraries_directory_is_loaded_under_its_own_key(tmp_path):
    """Document libraries directory is loaded under its own key."""
    root = _minimal_export(tmp_path / "lib")
    _write_json(
        root / "document_libraries" / "Docs" / "fields.json",
        [{"InternalName": "Gamma", "TypeAsString": "Text"}],
    )
    export = load_schema_export(root, label="lib")
    assert "document_libraries/Docs" in export.list_fields


# Load does not write anything into the export.
def test_load_does_not_write_anything_into_the_export(tmp_path):
    """Load does not write anything into the export."""
    root = _minimal_export(tmp_path / "ro")
    before = sorted(p.relative_to(root).as_posix() for p in root.rglob("*"))
    load_schema_export(root, label="ro")
    after = sorted(p.relative_to(root).as_posix() for p in root.rglob("*"))
    assert before == after


def test_section_status_wire_values_match_the_workbench_wide_outcome_convention():
    """External review (2026-08-08) found this enum's serialized values had
    silently forked to lowercase ("observed") while every other plugin's
    honest-outcome vocabulary uses capitalized values ("Observed") -- a
    cross-plugin consumer pattern-matching the wire string would silently
    miss this plugin's output. Pins the values to the shared convention so
    they cannot drift back without this test failing."""
    expected = {
        "OBSERVED": "Observed",
        "EMPTY": "Empty",
        "FORBIDDEN": "Forbidden",
        "UNAVAILABLE": "Unavailable",
        "NOT_SUPPORTED": "NotSupported",
        "PARTIAL": "Partial",
        "FAILED": "Failed",
    }
    actual = {member.name: member.value for member in SectionStatus}
    assert actual == expected
