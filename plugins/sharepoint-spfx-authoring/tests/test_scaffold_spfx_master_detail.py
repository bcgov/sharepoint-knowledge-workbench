# Purpose: Unit test for scaffold_spfx_master_detail generator script.
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


"""
Unit tests for the SPFx Master-Detail Web Part generator module.
Verifies spec parsing, TypeScript code generation, manifest synthesis, and directory output.
"""


@pytest.fixture
def sample_spec() -> dict:
    """Provides a sample dossier web part specification dictionary."""
    return {
        "webPartName": "PersonBriefing",
        "title": "Case Management And Tracking Dossier",
        "primaryList": "Persons",
        "lookupList": "Authors",
        "childLists": [
            {"title": "Appearances", "listName": "All_Appearances", "filterField": "RelatedAuthorId"},
            {"title": "Narratives", "listName": "PIO_Narratives", "filterField": "RelatedAuthorId"}
        ],
        "imageLibrary": "Images"
    }


def test_generate_spfx_ts_code_contains_primary_and_child_lists(sample_spec: dict) -> None:
    """Verifies that generated TypeScript contains references to configured primary and child lists."""
    ts_code = generate_spfx_ts_code(sample_spec)
    assert "PersonBriefingWebPart" in ts_code
    assert "Persons" in ts_code
    assert "All_Appearances" in ts_code
    assert "PIO_Narratives" in ts_code
    assert "_api/web/lists/getbytitle" in ts_code


def test_generate_spfx_manifest_has_valid_guid(sample_spec: dict) -> None:
    """Verifies that generated SPFx manifest contains expected web part name and valid GUID."""
    manifest = generate_spfx_manifest(sample_spec)
    assert manifest["alias"] == "PersonBriefingWebPart"
    assert manifest["componentType"] == "WebPart"
    assert "id" in manifest
    assert len(manifest["id"]) == 36


def test_scaffold_master_detail_webpart_creates_files(tmp_path: Path, sample_spec: dict) -> None:
    """Verifies end-to-end scaffolding writes TypeScript, SCSS, and Manifest files to output directory."""
    spec_path = tmp_path / "spec.json"
    spec_path.write_text(json.dumps(sample_spec), encoding="utf-8")

    output_dir = tmp_path / "out"
    created_files = scaffold_master_detail_webpart(spec_path, output_dir)

    assert len(created_files) == 3
    assert (output_dir / "PersonBriefingWebPart.ts").exists()
    assert (output_dir / "PersonBriefingWebPart.module.scss").exists()
    assert (output_dir / "PersonBriefingWebPart.manifest.json").exists()
