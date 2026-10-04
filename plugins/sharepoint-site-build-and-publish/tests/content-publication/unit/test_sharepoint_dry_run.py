"""
test_sharepoint_dry_run.py
============================

Tests for scripts/content-publication/sharepoint_dry_run.py -- the pre-upload validator that
runs entirely offline against an UploadPackage, with zero SharePoint
tenant I/O. Phase 3 plan Task 3.2.2.
"""

from pathlib import Path

import sharepoint_dry_run as dr
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


def _package(tmp_path, entries):
    for e in entries:
        p = tmp_path / e.content_path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("content")
    return UploadPackage(
        schema_version="1.0",
        package_identity="sha256:deadbeef",
        source_document_sha256="d" * 64,
        entries=entries,
        root_dir=tmp_path,
    )


def test_pass_for_a_well_formed_single_entry_package(tmp_path):
    pkg = _package(tmp_path, [_entry()])
    report = dr.validate_upload_package(pkg)
    assert report.status == "PASS"
    assert report.issues == []


def test_fails_on_empty_title(tmp_path):
    pkg = _package(tmp_path, [_entry(title="")])
    report = dr.validate_upload_package(pkg)
    assert report.status == "FAIL"
    assert any(i.code == "EMPTY_TITLE" for i in report.issues)


def test_fails_on_title_over_255_chars(tmp_path):
    pkg = _package(tmp_path, [_entry(title="x" * 256)])
    report = dr.validate_upload_package(pkg)
    assert report.status == "FAIL"
    assert any(i.code == "TITLE_TOO_LONG" for i in report.issues)


def test_fails_on_duplicate_order(tmp_path):
    e1 = _entry(topic_id="a--1111", content_path="topics/a--1111.md", order=0)
    e2 = _entry(topic_id="b--2222", content_path="topics/b--2222.md", order=0)
    pkg = _package(tmp_path, [e1, e2])
    report = dr.validate_upload_package(pkg)
    assert report.status == "FAIL"
    assert any(i.code == "DUPLICATE_ORDER" for i in report.issues)


def test_fails_on_duplicate_topic_id(tmp_path):
    e1 = _entry(order=0, content_path="topics/a.md")
    e2 = _entry(order=1, content_path="topics/b.md")
    pkg = _package(tmp_path, [e1, e2])
    report = dr.validate_upload_package(pkg)
    assert report.status == "FAIL"
    assert any(i.code == "DUPLICATE_TOPIC_ID" for i in report.issues)


def test_fails_on_missing_content_file(tmp_path):
    e = _entry(content_path="topics/does-not-exist.md")
    pkg = UploadPackage(
        schema_version="1.0", package_identity="sha256:deadbeef",
        source_document_sha256="d" * 64, entries=[e], root_dir=tmp_path,
    )
    report = dr.validate_upload_package(pkg)
    assert report.status == "FAIL"
    assert any(i.code == "MISSING_CONTENT_FILE" for i in report.issues)


def test_fails_on_empty_package(tmp_path):
    pkg = UploadPackage(
        schema_version="1.0", package_identity="sha256:deadbeef",
        source_document_sha256="d" * 64, entries=[], root_dir=tmp_path,
    )
    report = dr.validate_upload_package(pkg)
    assert report.status == "FAIL"
    assert any(i.code == "EMPTY_PACKAGE" for i in report.issues)
