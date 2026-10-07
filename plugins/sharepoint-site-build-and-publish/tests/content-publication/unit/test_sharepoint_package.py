"""
test_sharepoint_package.py
===========================

Tests for scripts/content-publication/sharepoint_package.py — assembles an UploadPackage
(SharePoint-ready topic files + manifest) from an already-promoted
CanonicalPackage and its rendered-output sibling. Package-only: this
module never talks to a SharePoint tenant. Task 3.2.1 (Phase 3 plan).

Purpose:
    Verify canonical and rendered content is assembled into an ordered upload package.

Key Input Dependencies:
    - Canonical package fixtures, rendered pages, and upload-package builder modules.

Function Index:
    test_upload_entry_round_trips_through_dict, test_upload_package_to_dict_has_schema_version_and_entries,
    _write_grouped_fixture, _write_grouped_canonical_artifacts,
    _write_grouped_validation_and_publication_map,
    test_build_upload_package_produces_one_entry_per_topic,
    test_build_upload_package_rejects_non_grouped_strategy,
    test_build_upload_package_raises_on_missing_rendered_page
"""

import json
from pathlib import Path

import pytest

import sharepoint_package as sp


# Verify the contract that upload entry round trips through dict.
def test_upload_entry_round_trips_through_dict():
    """Verify the contract that upload entry round trips through dict."""
    entry = sp.UploadEntry(
        topic_id="widget-setup--aaaa1111",
        title="WIDGET SETUP",
        order=0,
        package_identity="sha256:deadbeef",
        topic_content_sha256="cccc2222",
        source_document_sha256="dddd3333",
        content_path="topics/widget-setup--aaaa1111.md",
    )
    data = entry.to_dict()
    assert sp.UploadEntry.from_dict(data) == entry


# Verify the contract that upload package to dict has schema version and entries.
def test_upload_package_to_dict_has_schema_version_and_entries():
    """Verify the contract that upload package to dict has schema version and entries."""
    entry = sp.UploadEntry(
        topic_id="widget-setup--aaaa1111",
        title="WIDGET SETUP",
        order=0,
        package_identity="sha256:deadbeef",
        topic_content_sha256="cccc2222",
        source_document_sha256="dddd3333",
        content_path="topics/widget-setup--aaaa1111.md",
    )
    pkg = sp.UploadPackage(
        schema_version=sp.UPLOAD_MANIFEST_SCHEMA_VERSION,
        package_identity="sha256:deadbeef",
        source_document_sha256="dddd3333",
        entries=[entry],
        root_dir=Path("/tmp/does-not-matter"),
    )
    data = pkg.to_dict()
    assert data["schema_version"] == sp.UPLOAD_MANIFEST_SCHEMA_VERSION
    assert data["entries"] == [entry.to_dict()]


def _write_grouped_fixture(tmp_path):
    """Fabricates a minimal grouped CanonicalPackage + matching rendered
    render_dir (grouped strategy, topic_id == chunk_id, page file <topic_id>.md)."""
    canonical_dir = tmp_path / "canonical-content"
    render_dir = tmp_path / "render" / "rendered-output"
    (canonical_dir / "chunks").mkdir(parents=True)
    (canonical_dir / "media").mkdir(parents=True)
    (render_dir / "pages").mkdir(parents=True)
    (render_dir / "media").mkdir(parents=True)

    source_sha = "d" * 64
    chunk_id = "widget-setup--aaaa1111"
    content = "# Widget Setup\n\nHow to set up a widget.\n"
    content_sha = __import__("hashlib").sha256(content.encode()).hexdigest()
    _write_grouped_canonical_artifacts(canonical_dir, chunk_id, source_sha, content, content_sha)
    (render_dir / "pages" / f"{chunk_id}.md").write_text(
        "# WIDGET SETUP\n\nHow to set up a widget.\n"
    )
    return canonical_dir, render_dir, chunk_id


# Write a self-consistent canonical package for the upload package tests.
def _write_grouped_canonical_artifacts(
    canonical_dir: Path, chunk_id: str, source_sha: str, content: str, content_sha: str
) -> None:
    """Write chunk content and the canonical package manifest fixture."""
    (canonical_dir / "chunks" / f"{chunk_id}.md").write_text(content)
    (canonical_dir / "chunks" / f"{chunk_id}.json").write_text(json.dumps({
        "schema_version": "1.0",
        "chunk_id": chunk_id,
        "source_order": 0,
        "source_heading_path": ["Widget Setup"],
        "topic": "Widget Setup",
        "content_type": "procedure",
        "template_profile": "default",
        "source_sha256": source_sha,
        "plan_id": "sha256:" + "e" * 64,
        "content_file": f"chunks/{chunk_id}.md",
        "content_sha256": content_sha,
        "local_links": [],
        "media_refs": [],
    }))
    (canonical_dir / "manifest.json").write_text(json.dumps({
        "schema_version": "1.0",
        "generator": {"plugin": "docx-to-content", "plugin_version": "test"},
        "source": {"path": "intake/widget.docx", "sha256": source_sha},
        "plan_id": "sha256:" + "e" * 64,
        "content_type": "manual",
        "template_profile": "default",
        "strategy": "grouped",
        "chunk_count": 1,
        "chunks": [{
            "chunk_id": chunk_id,
            "content_file": f"chunks/{chunk_id}.md",
            "metadata_file": f"chunks/{chunk_id}.json",
            "source_order": 0,
            "source_heading_path": ["Widget Setup"],
        }],
        "media": [],
        "validation_report": "validation.json",
    }))

    _write_grouped_validation_and_publication_map(canonical_dir, chunk_id, source_sha)


# Write the validation report and mapping that make the package publishable.
def _write_grouped_validation_and_publication_map(
    canonical_dir: Path, chunk_id: str, source_sha: str
) -> None:
    """Write passing validation and the topic-to-chunk publication mapping."""
    (canonical_dir / "validation.json").write_text(json.dumps({
        "status": "PASS",
        "issues": [],
        "source_sha256": source_sha,
        "plan_id": "sha256:" + "e" * 64,
    }))
    (canonical_dir / "publication-map.json").write_text(json.dumps({
        "schema_version": "1.0",
        "package_identity": "sha256:" + "e" * 64,
        "entries": [{
            "chunk_id": chunk_id, "title": "WIDGET SETUP", "order": 0, "topic_id": chunk_id,
        }],
    }))


# Verify the contract that build upload package produces one entry per topic.
def test_build_upload_package_produces_one_entry_per_topic(tmp_path):
    """Verify the contract that build upload package produces one entry per topic."""
    canonical_dir, render_dir, chunk_id = _write_grouped_fixture(tmp_path)
    output_dir = tmp_path / "upload-package"

    pkg = sp.build_upload_package(canonical_dir, render_dir, output_dir)

    assert len(pkg.entries) == 1
    entry = pkg.entries[0]
    assert entry.topic_id == chunk_id
    assert entry.title == "WIDGET SETUP"
    assert entry.order == 0
    assert entry.package_identity == pkg.package_identity
    assert (output_dir / "topics" / f"{chunk_id}.md").exists()
    assert (output_dir / "upload-manifest.json").exists()

    reloaded = sp.UploadPackage.load(output_dir)
    assert reloaded.entries[0].topic_id == chunk_id


# Verify the contract that build upload package rejects non grouped strategy.
def test_build_upload_package_rejects_non_grouped_strategy(tmp_path):
    """Verify the contract that build upload package rejects non grouped strategy."""
    canonical_dir, render_dir, chunk_id = _write_grouped_fixture(tmp_path)
    manifest_path = canonical_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["strategy"] = "single"
    manifest_path.write_text(json.dumps(manifest))
    (canonical_dir / "publication-map.json").unlink()

    with pytest.raises(sp.SharePointPackageError, match="grouped"):
        sp.build_upload_package(canonical_dir, render_dir, tmp_path / "out")


# Verify the contract that build upload package raises on missing rendered page.
def test_build_upload_package_raises_on_missing_rendered_page(tmp_path):
    """Verify the contract that build upload package raises on missing rendered page."""
    canonical_dir, render_dir, chunk_id = _write_grouped_fixture(tmp_path)
    (render_dir / "pages" / f"{chunk_id}.md").unlink()

    with pytest.raises(sp.SharePointPackageError, match="rendered page"):
        sp.build_upload_package(canonical_dir, render_dir, tmp_path / "out")
