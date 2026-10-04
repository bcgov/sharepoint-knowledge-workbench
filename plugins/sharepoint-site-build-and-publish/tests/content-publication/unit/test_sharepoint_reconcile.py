"""
test_sharepoint_reconcile.py
===============================

Tests for scripts/content-publication/sharepoint_reconcile.py -- diffs an UploadPackage
(expected state) against an ActualLibraryState (evidence captured from
the real SharePoint library, currently via CSV export -- see
docs/content-publication/sharepoint-actual-state-csv-format.md). Phase 3 plan Task 3.3.1.
"""

from pathlib import Path

import sharepoint_reconcile as rec
from sharepoint_package import UploadEntry, UploadPackage


def _entry(**overrides):
    base = dict(
        topic_id="widget-setup--aaaa1111",
        title="WIDGET SETUP",
        order=0,
        package_identity="sha256:deadbeef",
        topic_content_sha256="c" * 64,
        source_document_sha256="d" * 64,
        content_path="topics/widget-setup--aaaa1111.md",
    )
    base.update(overrides)
    return UploadEntry(**base)


def _package(entries):
    return UploadPackage(
        schema_version="1.0", package_identity="sha256:deadbeef",
        source_document_sha256="d" * 64, entries=entries, root_dir=Path("/unused"),
    )


def _actual(**overrides):
    base = dict(
        topic_id="widget-setup--aaaa1111", title="WIDGET SETUP",
        package_identity="sha256:deadbeef", publication_order=0,
        topic_content_sha256="c" * 64, source_document_sha256="d" * 64,
    )
    base.update(overrides)
    return rec.ActualLibraryItem(**base)


def test_match_when_package_and_library_agree():
    pkg = _package([_entry()])
    report = rec.reconcile(pkg, [_actual()])
    assert report.status == "MATCH"
    assert report.issues == []


def test_missing_in_library():
    pkg = _package([_entry()])
    report = rec.reconcile(pkg, [])
    assert report.status == "MISMATCH"
    assert any(i.code == "MISSING_IN_LIBRARY" for i in report.issues)


def test_unexpected_in_library():
    pkg = _package([])
    report = rec.reconcile(pkg, [_actual()])
    assert report.status == "MISMATCH"
    assert any(i.code == "UNEXPECTED_IN_LIBRARY" for i in report.issues)


def test_duplicate_in_library():
    pkg = _package([_entry()])
    report = rec.reconcile(pkg, [_actual(), _actual()])
    assert report.status == "MISMATCH"
    assert any(i.code == "DUPLICATE_IN_LIBRARY" for i in report.issues)


def test_field_mismatch_on_content_hash_drift():
    pkg = _package([_entry()])
    report = rec.reconcile(pkg, [_actual(topic_content_sha256="f" * 64)])
    assert report.status == "MISMATCH"
    mismatch = next(i for i in report.issues if i.code == "FIELD_MISMATCH")
    assert "topic_content_sha256" in mismatch.message


def test_csv_loader_reads_expected_columns(tmp_path):
    csv_path = tmp_path / "actual-state.csv"
    csv_path.write_text(
        "TopicId,Title,PackageIdentity,PublicationOrder,"
        "TopicContentSHA256,SourceDocumentSHA256\n"
        "widget-setup--aaaa1111,WIDGET SETUP,sha256:deadbeef,0,"
        + "c" * 64 + "," + "d" * 64 + "\n"
    )
    items = rec.load_actual_state_from_csv(csv_path)
    assert len(items) == 1
    assert items[0].topic_id == "widget-setup--aaaa1111"
    assert items[0].publication_order == 0
