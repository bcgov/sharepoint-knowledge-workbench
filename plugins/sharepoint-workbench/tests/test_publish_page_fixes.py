"""Tests for the page planner and publisher fixes found in the CSB news-message pilot.

Purpose: planner must not re-map image sources it already pointed at an uploaded asset, and must let a caller drop the
BC design-token wrapper; the publisher must read SharePoint's `&#58;` style colons and must refuse to "recover" a page
whose only component is an empty shell.

Key Input Dependencies: pwsh, scripts/new-page-migration-dry-run.ps1 (modernizing and publishing copies) and
scripts/publish-spo-page.ps1 in publishing-sharepoint-pages (real scripts, no tenant access).
Usage: python -m pytest plugins/sharepoint-workbench/tests/test_publish_page_fixes.py

Function index: run_planner_with_images, run_publisher_snippet, test_* cases.
"""
import json
import subprocess
from pathlib import Path

import pytest

from test_planner_numbered_titles import IDS, PLANNERS, PWSH, SKILLS, run_planner

PUBLISHER = SKILLS / "publishing-sharepoint-pages" / "scripts" / "publish-spo-page.ps1"
pytestmark = pytest.mark.skipif(PWSH is None, reason="pwsh is required")

BODY = '<p>Hello</p><img src="/PublishingImages/a.png" alt="a" />'
DESTINATION = "SiteAssets/Sheriff/a.png"


def run_planner_with_images(planner: Path, tmp_path: Path, **params) -> dict:
    """Plan a page whose image is in the manifest and whose library map also covers the page folder."""
    (tmp_path / "images.json").write_text(json.dumps([{
        "SourceWebPartId": "wp1", "SourceUrl": "https://csb.jag.gov.bc.ca/PublishingImages/a.png",
        "DestinationRelativePath": DESTINATION, "OutputFileName": "a.png"}]), encoding="utf-8")
    (tmp_path / "map.csv").write_text(
        "source_prefix,dest_prefix,status\n/Sheriff/Pages/,/sites/AG-CSB-INTRANET-DEV/SitePages/Sheriff/,planned\n",
        encoding="utf-8")
    return run_planner(
        planner, tmp_path, [("wp1", "Body", BODY)],
        ImageManifestPath=tmp_path / "images.json", LibraryPathMapPath=tmp_path / "map.csv",
        SourceHost="csb.jag.gov.bc.ca", TargetSitePath="/sites/AG-CSB-INTRANET-DEV", **params)


def run_publisher_snippet(snippet: str) -> subprocess.CompletedProcess:
    script = f". '{PUBLISHER}'\n{snippet}\n"
    return subprocess.run([PWSH, "-NoProfile", "-Command", script], capture_output=True, text=True)


@pytest.mark.parametrize("planner", PLANNERS, ids=IDS)
def test_manifest_image_destination_is_not_link_mapped(planner, tmp_path):
    plan = run_planner_with_images(planner, tmp_path)
    html = " ".join(c["Html"] for c in plan["Components"])
    assert f'src="{DESTINATION}"' in html, html


@pytest.mark.parametrize("planner", PLANNERS, ids=IDS)
def test_design_token_wrapper_is_on_by_default(planner, tmp_path):
    plan = run_planner_with_images(planner, tmp_path)
    assert "data-sp-bc-tokens" in " ".join(c["Html"] for c in plan["Components"])


@pytest.mark.parametrize("planner", PLANNERS, ids=IDS)
def test_design_token_wrapper_can_be_disabled(planner, tmp_path):
    plan = run_planner_with_images(planner, tmp_path, NoBcDesignTokens="true")
    html = " ".join(c["Html"] for c in plan["Components"])
    assert "data-sp-bc-tokens" not in html and "BC Sans" not in html, html


def test_inline_image_dimensions_read_encoded_colon():
    done = run_publisher_snippet(
        "$d = Get-SpoInlineImageDimensions -ImageTag '<img src=\"a.png\" style=\"width&#58; 120px; height&#58; 60px;\" />'\n"
        "\"$($d.Width)x$($d.Height)\"")
    assert done.returncode == 0, done.stderr
    assert done.stdout.strip() == "120x60"


def test_inline_image_alignment_reads_encoded_colon():
    html = '<div style="text-align&#58;center;"><img src="a.png" /></div>'
    done = run_publisher_snippet(
        f"$h = '{html}'\nGet-SpoInlineImageAlignment -Html $h -ImageIndex $h.IndexOf('<img')")
    assert done.returncode == 0, done.stderr
    assert done.stdout.strip() == "Center"


@pytest.mark.parametrize("page_path, expected_value", [
    ("/SitePages/CourtAdmin/Youth Court.aspx", "/sites/X/SitePages/CourtAdmin/Youth Court.aspx"),
    ("/SitePages/Incidents-&-Reporting.aspx", "/sites/X/SitePages/Incidents-&amp;-Reporting.aspx"),
    ("/SitePages/Rules-(Child,-Family).aspx", "/sites/X/SitePages/Rules-(Child,-Family).aspx"),
])
def test_site_pages_fileref_query_uses_decoded_xml_escaped_path(page_path, expected_value):
    done = run_publisher_snippet(
        f"Get-SpoSitePageFileRefQuery -SiteUrl 'https://t.sharepoint.com/sites/X' -PageServerRelativeUrl '{page_path}'")
    assert done.returncode == 0, done.stderr
    assert f"<Value Type='Text'>{expected_value}</Value>" in done.stdout
    assert "%20" not in done.stdout


@pytest.mark.parametrize("existing, ok", [
    ("[pscustomobject]@{ Text = '' }", False),
    ("[pscustomobject]@{ Text = '<p>&#160;</p>' }", False),
    ("[pscustomobject]@{ Text = '<div><h2>Title</h2></div>' }", True),
])
def test_recovery_requires_existing_text_part_with_content(existing, ok):
    done = run_publisher_snippet(
        f"Assert-SpoRecoverableComponent -ExistingComponents @({existing}) "
        "-FirstPackageComponent ([pscustomobject]@{ OutputType = 'TextWebPart' })\n'passed'")
    if ok:
        assert done.returncode == 0 and done.stdout.strip() == "passed", done.stderr
    else:
        assert done.returncode != 0 and "empty" in (done.stdout + done.stderr).lower()


def test_recovery_refuses_wrong_component_count():
    done = run_publisher_snippet(
        "Assert-SpoRecoverableComponent -ExistingComponents @() "
        "-FirstPackageComponent ([pscustomobject]@{ OutputType = 'TextWebPart' })")
    assert done.returncode != 0 and "exactly one" in (done.stdout + done.stderr)
