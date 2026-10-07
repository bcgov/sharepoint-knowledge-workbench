"""
sharepoint_package.py
======================

Purpose:
Assembles a package-only SharePoint UploadPackage from an already
ACCEPTED Phase 2 canonical-content package plus its rendered-output
sibling. Never performs any SharePoint tenant I/O -- output is a plain
directory a human uploads through the SharePoint UI. Phase 3 plan Task
3.2.1. See docs/superpowers/specs/phase-3-governed-sharepoint-knowledge-pilot-spec.md
Section 6 (target schema) and Section 8 (package-only deployment contract).

Key Input Dependencies:
    - accepted canonical package directory readable by canonical_package
    - rendered pages/<topic_id>.md and optional media/ sibling directory
    - standard-library json, shutil, dataclasses, and pathlib

Function Index:
    UploadEntry.from_dict, UploadEntry.to_dict, UploadPackage.to_dict,
    UploadPackage.load, build_upload_package, _copy_topic_pages
"""

import json
import shutil
from dataclasses import dataclass
from pathlib import Path

import canonical_package

UPLOAD_MANIFEST_SCHEMA_VERSION = "1.0"


class SharePointPackageError(Exception):
    """Raised when the source canonical/rendered pair cannot be assembled
    into an UploadPackage (wrong strategy, missing rendered page, etc.)."""


@dataclass
class UploadEntry:
    """A single topic entry in an UploadPackage.
    
    Note: content_path is deserialized without validation from upload-manifest.json.
    This is safe because the manifest is only ever generated internally by
    build_upload_package(), never supplied externally by users. The manifest is a
    trust boundary artifact, so validated relative-path resolution is not needed.
    """
    topic_id: str
    title: str
    order: int
    package_identity: str
    topic_content_sha256: str
    source_document_sha256: str
    content_path: str

    @classmethod
    def from_dict(cls, data: dict) -> "UploadEntry":
        """Create an upload entry from its persisted manifest fields."""
        return cls(
            topic_id=data["topic_id"],
            title=data["title"],
            order=data["order"],
            package_identity=data["package_identity"],
            topic_content_sha256=data["topic_content_sha256"],
            source_document_sha256=data["source_document_sha256"],
            content_path=data["content_path"],
        )

    def to_dict(self) -> dict:
        """Serialize an entry using the upload-manifest field names."""
        return {
            "topic_id": self.topic_id,
            "title": self.title,
            "order": self.order,
            "package_identity": self.package_identity,
            "topic_content_sha256": self.topic_content_sha256,
            "source_document_sha256": self.source_document_sha256,
            "content_path": self.content_path,
        }


@dataclass
class UploadPackage:
    schema_version: str
    package_identity: str
    source_document_sha256: str
    entries: list  # list[UploadEntry], in publication order
    root_dir: Path

    def to_dict(self) -> dict:
        """Serialize package metadata and entries without local root_dir."""
        return {
            "schema_version": self.schema_version,
            "package_identity": self.package_identity,
            "source_document_sha256": self.source_document_sha256,
            "entries": [e.to_dict() for e in self.entries],
        }

    @classmethod
    def load(cls, root_dir: Path) -> "UploadPackage":
        """Load upload-manifest.json and resolve its package root directory."""
        root_dir = Path(root_dir)
        manifest_path = root_dir / "upload-manifest.json"
        data = json.loads(manifest_path.read_text())
        return cls(
            schema_version=data["schema_version"],
            package_identity=data["package_identity"],
            source_document_sha256=data["source_document_sha256"],
            entries=[UploadEntry.from_dict(e) for e in data["entries"]],
            root_dir=root_dir,
        )


# Assemble rendered topic pages and metadata without accessing SharePoint.
def build_upload_package(canonical_dir: Path, render_dir: Path, output_dir: Path) -> UploadPackage:
    """Assemble an UploadPackage at output_dir from an already-ACCEPTED
    canonical package at canonical_dir and its rendered-output sibling at
    render_dir (the render/rendered-output directory, containing
    pages/<topic_id>.md and media/). Raises SharePointPackageError if the
    canonical package isn't the grouped, publication-map-backed strategy
    this pilot targets, or if a topic's rendered page is missing.
    
    Note: The caller is responsible for supplying a clean/empty output_dir.
    Repeated calls to the same output_dir will silently overwrite previous
    contents via shutil.copyfile/shutil.copytree(dirs_exist_ok=True). This
    idempotent rebuild behavior is intentional; callers needing a strict
    clean-directory guarantee should remove output_dir first.
    """
    canonical_dir = Path(canonical_dir)
    render_dir = Path(render_dir)
    output_dir = Path(output_dir)

    loaded = canonical_package.CanonicalPackage.load(canonical_dir)
    if loaded.manifest.strategy != "grouped" or loaded.publication_map is None:
        raise SharePointPackageError(
            f"{canonical_dir} has strategy={loaded.manifest.strategy!r} -- "
            "the Phase 3 pilot only supports the grouped, "
            "publication-map-backed strategy"
        )

    topics_dir = output_dir / "topics"
    media_dir = output_dir / "media"
    topics_dir.mkdir(parents=True, exist_ok=True)

    entries = _copy_topic_pages(loaded, render_dir, output_dir)
    render_media_dir = render_dir / "media"
    if render_media_dir.exists():
        shutil.copytree(render_media_dir, media_dir, dirs_exist_ok=True)

    pkg = UploadPackage(
        schema_version=UPLOAD_MANIFEST_SCHEMA_VERSION,
        package_identity=loaded.publication_map.package_identity,
        source_document_sha256=loaded.manifest.source.sha256,
        entries=entries,
        root_dir=output_dir,
    )
    (output_dir / "upload-manifest.json").write_text(
        json.dumps(pkg.to_dict(), indent=2, sort_keys=True)
    )
    return pkg


# Copy ordered topic files and return the matching upload-manifest entries.
def _copy_topic_pages(loaded: canonical_package.CanonicalPackage, render_dir: Path, output_dir: Path) -> list[UploadEntry]:
    """Copy publication-ordered rendered topics and assemble their manifest records."""
    chunks_by_id = {chunk.metadata.chunk_id: chunk for chunk in loaded.chunks}
    entries = []
    for pub_entry in sorted(loaded.publication_map.entries, key=lambda e: e.order):
        chunk = chunks_by_id.get(pub_entry.chunk_id)
        if chunk is None:
            raise SharePointPackageError(
                f"publication-map.json references chunk_id "
                f"{pub_entry.chunk_id!r} not present in manifest.json"
            )

        rendered_page = render_dir / "pages" / f"{pub_entry.topic_id}.md"
        if not rendered_page.exists():
            raise SharePointPackageError(
                f"topic {pub_entry.topic_id!r}: missing rendered page "
                f"{rendered_page}"
            )

        dest_content_path = f"topics/{pub_entry.topic_id}.md"
        shutil.copyfile(rendered_page, output_dir / dest_content_path)

        entries.append(UploadEntry(
            topic_id=pub_entry.topic_id,
            title=pub_entry.title,
            order=pub_entry.order,
            package_identity=loaded.publication_map.package_identity,
            topic_content_sha256=chunk.metadata.content_sha256,
            source_document_sha256=loaded.manifest.source.sha256,
            content_path=dest_content_path,
        ))
    return entries
