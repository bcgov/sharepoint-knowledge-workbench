"""
test_conversion_report.py
==========================

Tests for rendering a human-readable Markdown disposition report from a
PageConversionManifest-shaped dict (conforming to
`scripts/page-modernization/assets/manifest-schema.json`). Pure function: no I/O, no tenant
contact -- every test drives `render_conversion_report` directly in-process.

Purpose: Tests for rendering a human-readable Markdown disposition report from a PageConversionManifest-shaped dict (conforming to `scripts/page-modernization/assets/manifest-schema.json`).
Key Input Dependencies: conversion_report, conversion-manifest.json.
"""

import copy
import json

import pytest

import conversion_report


@pytest.fixture
def manifest(fixtures_dir):
    """Pytest fixture providing manifest."""
    return json.loads((fixtures_dir / "conversion-manifest.json").read_text(encoding="utf-8"))


def test_full_manifest_reports_observed_or_partial_and_renders(manifest):
    """Verify full manifest reports observed or partial and renders."""
    report, outcome = conversion_report.render_conversion_report(manifest)
    assert report is not None
    assert outcome["status"] == "Partial"
    assert manifest["sourcePage"] in report
    assert manifest["convertedAt"] in report


def test_every_gap_named_none_dropped(manifest):
    """Verify every gap named none dropped."""
    report, _ = conversion_report.render_conversion_report(manifest)
    for gap in manifest["gaps"]:
        assert gap in report


def test_classification_table_row_count_matches_webparts_count(manifest):
    """Verify classification table row count matches webparts count."""
    report, _ = conversion_report.render_conversion_report(manifest)
    for web_part in manifest["webParts"]:
        assert web_part["type"] in report
    # 3 web parts + 1 header row + 1 separator row = 5 table lines
    table_lines = [line for line in report.splitlines() if line.strip().startswith("|")]
    assert len(table_lines) == 2 + len(manifest["webParts"])


def test_layout_and_confidence_rendered(manifest):
    """Verify layout and confidence rendered."""
    report, _ = conversion_report.render_conversion_report(manifest)
    assert manifest["layout"]["template"] in report
    assert manifest["layout"]["mappedTo"] in report
    assert str(manifest["confidence"]["componentsMapped"]) in report


def test_no_gaps_renders_explicit_none_recorded(manifest):
    """Verify no gaps renders explicit none recorded."""
    clean = copy.deepcopy(manifest)
    clean["gaps"] = []
    clean["outcome"] = {"status": "Observed", "detail": "All components mapped", "counts": None}
    report, outcome = conversion_report.render_conversion_report(clean)
    assert report is not None
    assert outcome["status"] == "Observed"
    assert "No gaps recorded" in report


def test_missing_required_field_reports_unavailable_not_blank_render(manifest):
    """Verify missing required field reports unavailable not blank render."""
    broken = copy.deepcopy(manifest)
    del broken["webParts"]
    report, outcome = conversion_report.render_conversion_report(broken)
    assert report is None
    assert outcome["status"] == "Unavailable"
    assert "webParts" in outcome["detail"]


def test_invalid_outcome_status_reports_failed(manifest):
    """Verify invalid outcome status reports failed."""
    broken = copy.deepcopy(manifest)
    broken["outcome"] = {"status": "NotARealStatus", "detail": "bogus"}
    report, outcome = conversion_report.render_conversion_report(broken)
    assert report is None
    assert outcome["status"] == "Failed"


def test_empty_manifest_reports_unavailable(manifest):
    """Verify empty manifest reports unavailable."""
    report, outcome = conversion_report.render_conversion_report({})
    assert report is None
    assert outcome["status"] == "Unavailable"
