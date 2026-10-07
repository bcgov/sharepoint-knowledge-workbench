"""
test_aspx_inventory.py
======================

Stage 1 tests -- parse a classic SharePoint page (plus optional views export
and override hints) into a neutral page inventory.

Semantic-parity oracle: baseline page modernization test suite
(source baseline 78d6bb91a6c3c01208208a8c2a06f241fef9ce9f). Retained
behaviours: ContentEditor detection via the `ms-rtestate-field` class, list
view detection from a views export, consumer-zone creation from override
`knownRelationships`, and never fabricating a zone when evidence is absent.

Every test drives the real CLI over the real filesystem -- no mocks on the
parsing or path-resolution path.

Purpose: Stage 1 tests -- parse a classic SharePoint page (plus optional views export and override hints) into a neutral page inventory.
Key Input Dependencies: outcomes, aspx_inventory.py, classic-page.views.json, classic-page.override.json.
"""

import json
import subprocess
import sys

import pytest


def run_inventory(scripts_dir, tmp_path, *args) -> subprocess.CompletedProcess:
    """Run aspx_inventory.py as a real subprocess and return the completed process."""
    return subprocess.run(
        [sys.executable, str(scripts_dir / "aspx_inventory.py"), *args],
        capture_output=True,
        text=True,
    )


def build(scripts_dir, fixtures_dir, tmp_path, *, views=True, override=True, html=None):
    """Helper: run the inventory stage over the neutral fixtures and load the result."""
    out = tmp_path / "page-inventory.json"
    args = [
        "--source-html", str(html or fixtures_dir / "classic-page.raw.html"),
        "--source-page", "/team/Pages/My_Requests.aspx",
        "--output", str(out),
    ]
    if views:
        args += ["--views-json", str(fixtures_dir / "classic-page.views.json")]
    if override:
        args += ["--override", str(fixtures_dir / "classic-page.override.json")]
    result = run_inventory(scripts_dir, tmp_path, *args)
    assert result.returncode == 0, result.stderr
    return json.loads(out.read_text(encoding="utf-8"))


def test_content_editor_zones_detected_from_rendered_html(scripts_dir, fixtures_dir, tmp_path):
    """Verify content editor zones detected from rendered html."""
    inv = build(scripts_dir, fixtures_dir, tmp_path)
    ce = [z for z in inv["zones"] if z["webPartType"] == "ContentEditor"]
    assert len(ce) == 3
    assert all(z["detectionSource"] == "rendered-html" for z in ce)


def test_list_view_zone_detected_from_views_export(scripts_dir, fixtures_dir, tmp_path):
    """Verify list view zone detected from views export."""
    inv = build(scripts_dir, fixtures_dir, tmp_path)
    lv = [z for z in inv["zones"] if z["webPartType"] == "XsltListView" and not z.get("isConnectedConsumer")]
    assert [z["listName"] for z in lv] == ["Project_Requests"]
    assert lv[0]["viewQuery"].startswith("<OrderBy>")


def test_override_relationships_add_connected_consumer_zones(scripts_dir, fixtures_dir, tmp_path):
    """Verify override relationships add connected consumer zones."""
    inv = build(scripts_dir, fixtures_dir, tmp_path)
    consumers = [z for z in inv["zones"] if z.get("isConnectedConsumer")]
    assert sorted(z["listName"] for z in consumers) == ["Request_Notes", "Request_Tasks"]
    assert inv["hasConnections"] is True
    assert all(z["detectionSource"] == "override-file" for z in consumers)


def test_source_page_is_recorded_from_the_cli_not_inferred(scripts_dir, fixtures_dir, tmp_path):
    """Verify source page is recorded from the cli not inferred."""
    inv = build(scripts_dir, fixtures_dir, tmp_path)
    assert inv["sourcePage"] == "/team/Pages/My_Requests.aspx"


def test_detection_method_is_multi_when_more_than_one_source_contributes(scripts_dir, fixtures_dir, tmp_path):
    """Verify detection method is multi when more than one source contributes."""
    inv = build(scripts_dir, fixtures_dir, tmp_path)
    assert inv["detectionMethod"] == "multi"
    assert set(inv["detectionSources"]) == {"rendered-html", "views-json", "override-file"}


def test_malformed_page_with_no_zones_reports_empty_not_silent_success(scripts_dir, fixtures_dir, tmp_path):
    """A page yielding zero zones must say Empty and warn -- never an unqualified success."""
    inv = build(
        scripts_dir, fixtures_dir, tmp_path,
        views=False, override=False,
        html=fixtures_dir / "malformed-page.raw.html",
    )
    assert inv["zones"] == []
    assert inv["outcome"]["status"] == "Empty"
    assert inv["outcome"]["detail"]
    assert inv["warnings"]


def test_html_only_run_reports_observed(scripts_dir, fixtures_dir, tmp_path):
    """Verify html only run reports observed."""
    inv = build(scripts_dir, fixtures_dir, tmp_path, views=False, override=False)
    assert inv["outcome"]["status"] == "Observed"
    assert inv["outcome"]["counts"]["zones"] == 3


def test_provided_but_empty_views_export_reports_partial(scripts_dir, fixtures_dir, tmp_path):
    """An input that was supplied but contributed nothing is Partial, not Observed."""
    empty_views = tmp_path / "empty.views.json"
    empty_views.write_text("[]", encoding="utf-8")
    out = tmp_path / "inv.json"
    result = run_inventory(
        scripts_dir, tmp_path,
        "--source-html", str(fixtures_dir / "classic-page.raw.html"),
        "--views-json", str(empty_views),
        "--output", str(out),
    )
    assert result.returncode == 0, result.stderr
    inv = json.loads(out.read_text(encoding="utf-8"))
    assert inv["outcome"]["status"] == "Partial"
    assert "views" in inv["outcome"]["detail"].lower()


def test_missing_source_html_fails_honestly_with_nonzero_exit(scripts_dir, tmp_path):
    """Verify missing source html fails honestly with nonzero exit."""
    out = tmp_path / "inv.json"
    result = run_inventory(
        scripts_dir, tmp_path,
        "--source-html", str(tmp_path / "does-not-exist.html"),
        "--output", str(out),
    )
    assert result.returncode != 0
    assert "Unavailable" in result.stderr
    assert not out.exists()


def test_malformed_views_json_fails_honestly(scripts_dir, fixtures_dir, tmp_path):
    """Verify malformed views json fails honestly."""
    bad = tmp_path / "bad.json"
    bad.write_text("{not json", encoding="utf-8")
    out = tmp_path / "inv.json"
    result = run_inventory(
        scripts_dir, tmp_path,
        "--source-html", str(fixtures_dir / "classic-page.raw.html"),
        "--views-json", str(bad),
        "--output", str(out),
    )
    assert result.returncode != 0
    assert "Failed" in result.stderr
    assert not out.exists()


def test_inventory_outcome_validates_against_the_vocabulary(scripts_dir, fixtures_dir, tmp_path):
    """Verify inventory outcome validates against the vocabulary."""
    import outcomes
    inv = build(scripts_dir, fixtures_dir, tmp_path)
    outcomes.validate_outcome(inv["outcome"])
