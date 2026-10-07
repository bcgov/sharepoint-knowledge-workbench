"""Purpose: Verify specification parsing, TypeScript generation, and output files.

Key Input Dependencies:
    - scripts/scaffold_spfx_master_detail.py
    - JSON specifications and temporary output directories.

Function Index:
    - sample_spec
    - test_generate_spfx_ts_code_contains_primary_and_child_lists
    - test_generate_spfx_manifest_has_valid_guid
    - test_generate_spfx_ts_code_preserves_template_marker_text_in_values
    - test_scaffold_master_detail_webpart_creates_files
"""

# Purpose: Unit test for scaffold_spfx_master_detail generator script.
# Key Input Dependencies: JSON specifications and temporary output directories.
# Function Index: sample_spec; test_generate_spfx_ts_code_contains_primary_and_child_lists;
# test_generate_spfx_manifest_has_valid_guid; test_generate_spfx_ts_code_preserves_template_marker_text_in_values;
# test_scaffold_master_detail_webpart_creates_files.
# Layer: Plugin Verification / TDD
import json
import sys
from pathlib import Path

# Bootstrap sys.path for plugin-local script imports
PLUGIN_ROOT = Path(__file__).resolve().parent.parent
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

import pytest
from scripts.scaffold_spfx_master_detail import (
    generate_spfx_ts_code,
    generate_spfx_manifest,
    scaffold_master_detail_webpart,
)


# Supplies representative input configuration to generator behavior tests.
@pytest.fixture
def sample_spec() -> dict:
    """Provides a sample dossier web part specification dictionary."""
    return {
        "webPartName": "AuthorBriefing",
        "title": "Author Briefing Dashboard",
        "primaryList": "Authors",
        "lookupList": "Authors",
        "childLists": [
            {"title": "Events", "listName": "All_Events", "filterField": "RelatedAuthorId"},
            {"title": "Reviews", "listName": "Example_Items", "filterField": "RelatedAuthorId"}
        ],
        "imageLibrary": "Images"
    }


# Verifies configured list names and shared source-generation helpers appear in TypeScript output.
def test_generate_spfx_ts_code_contains_primary_and_child_lists(sample_spec: dict) -> None:
    """Verifies that generated TypeScript contains references to configured primary and child lists."""
    ts_code = generate_spfx_ts_code(sample_spec)
    assert "AuthorBriefingWebPart" in ts_code
    assert "Authors" in ts_code
    assert "All_Events" in ts_code
    assert "Example_Items" in ts_code
    assert "_api/web/lists/getbytitle" in ts_code
    assert "_escapeHtml" in ts_code


# Verifies the generated manifest includes required metadata and a GUID-shaped identifier.
def test_generate_spfx_manifest_has_valid_guid(sample_spec: dict) -> None:
    """Verifies that generated SPFx manifest contains expected web part name and valid GUID."""
    manifest = generate_spfx_manifest(sample_spec)
    assert manifest["alias"] == "AuthorBriefingWebPart"
    assert manifest["componentType"] == "WebPart"
    assert "id" in manifest
    assert len(manifest["id"]) == 36


# Verifies the template refactor does not reinterpret marker-shaped user-provided values.
def test_generate_spfx_ts_code_preserves_template_marker_text_in_values() -> None:
    """Ensures marker-like strings in configured titles remain literal in generated TypeScript."""
    title = "Literal @@PRIMARY_LIST@@ and @@IMAGE_LIBRARY@@ values"
    ts_code = generate_spfx_ts_code({"title": title})

    assert f"<h1>{title}</h1>" in ts_code


# Verifies the public scaffolder writes all expected web-part artifacts to the requested directory.
def test_scaffold_master_detail_webpart_creates_files(tmp_path: Path, sample_spec: dict) -> None:
    """Verifies end-to-end scaffolding writes TypeScript, SCSS, and Manifest files to output directory."""
    spec_path = tmp_path / "spec.json"
    spec_path.write_text(json.dumps(sample_spec), encoding="utf-8")

    output_dir = tmp_path / "out"
    created_files = scaffold_master_detail_webpart(spec_path, output_dir)

    assert len(created_files) == 3
    assert (output_dir / "AuthorBriefingWebPart.ts").exists()
    assert (output_dir / "AuthorBriefingWebPart.module.scss").exists()
    assert (output_dir / "AuthorBriefingWebPart.manifest.json").exists()
