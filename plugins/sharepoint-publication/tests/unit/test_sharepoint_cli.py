"""
test_sharepoint_cli.py
=======================

Tests for scripts/sharepoint_cli.py -- the human-facing CLI wrapping
sharepoint_package/sharepoint_dry_run/sharepoint_reconcile. Phase 3 plan
Task 3.3.6.
"""

import json
from pathlib import Path

import sharepoint_cli as cli


def test_dry_run_subcommand_exits_zero_on_pass(tmp_path, capsys):
    topics_dir = tmp_path / "pkg" / "topics"
    topics_dir.mkdir(parents=True)
    (topics_dir / "a--1111.md").write_text("content")
    manifest = {
        "schema_version": "1.0",
        "package_identity": "sha256:deadbeef",
        "source_document_sha256": "d" * 64,
        "entries": [{
            "topic_id": "a--1111", "title": "A", "order": 0,
            "package_identity": "sha256:deadbeef",
            "topic_content_sha256": "c" * 64,
            "source_document_sha256": "d" * 64,
            "content_path": "topics/a--1111.md",
        }],
    }
    (tmp_path / "pkg" / "upload-manifest.json").write_text(json.dumps(manifest))

    exit_code = cli.main(["dry-run", "--package-dir", str(tmp_path / "pkg")])

    assert exit_code == 0
    out = capsys.readouterr().out
    assert '"status": "PASS"' in out


def test_dry_run_subcommand_exits_one_on_fail(tmp_path, capsys):
    manifest = {
        "schema_version": "1.0",
        "package_identity": "sha256:deadbeef",
        "source_document_sha256": "d" * 64,
        "entries": [],
    }
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "upload-manifest.json").write_text(json.dumps(manifest))

    exit_code = cli.main(["dry-run", "--package-dir", str(tmp_path / "pkg")])

    assert exit_code == 1
    out = capsys.readouterr().out
    assert '"status": "FAIL"' in out
