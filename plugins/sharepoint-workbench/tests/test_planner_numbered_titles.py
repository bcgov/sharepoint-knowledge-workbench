"""Tests for new-page-migration-dry-run.ps1 with SP2016 auto-numbered web part titles.

Purpose: SP2016 names a second Content Editor "Content Editor 2". The planner emitted an <h3> with that title
(a stray heading on the published page) and, for a leading banner image, the injected <h3> made
Split-SpPageLeadingImage fail with "does not start with a single image block". A zero-width space before the
image must keep working (the plain-text helper already strips it); that case is a regression guard.

Key Input Dependencies: pwsh, scripts/new-page-migration-dry-run.ps1 in modernizing-sharepoint-pages and its
copy in publishing-sharepoint-pages (real planner, real fixtures, no mocks).
Usage: python -m pytest plugins/sharepoint-workbench/tests/test_planner_numbered_titles.py

Function index: run_planner, test_* cases.
"""
import json
import shutil
import subprocess
from pathlib import Path

import pytest

PLUGIN = Path(__file__).resolve().parents[1]
SKILLS = PLUGIN / ".apm" / "skills"
PLANNERS = [
    SKILLS / "modernizing-sharepoint-pages" / "scripts" / "new-page-migration-dry-run.ps1",
    SKILLS / "publishing-sharepoint-pages" / "scripts" / "new-page-migration-dry-run.ps1",
]
PWSH = shutil.which("pwsh")
pytestmark = pytest.mark.skipif(PWSH is None, reason="pwsh is required")
IDS = ["modernizing", "publishing"]

BANNER = '<div style="text-align: center;">{zw}<img src="/PublishingImages/Header%20Image/Banner.png" alt="" style="margin: 5px; width: 1234px;"/> </div><p>&#160;</p>Body text of the page.'
LINKS = '<ul><li><a href="https://example.org/x">A link</a></li></ul>'


def run_planner(planner: Path, tmp_path: Path, parts: list, **params) -> dict:
    """Run New-SpPageWave1DryRun on a fixture with the given web parts and return plan.json."""
    page_url = "https://csb.jag.gov.bc.ca/Sheriff/Pages/ITAU.aspx"
    (tmp_path / "page.json").write_text(json.dumps({
        "SiteName": "Sheriff", "ServerRelativeUrl": "/Sheriff/Pages/ITAU.aspx", "Url": page_url,
        "Title": "ITAU", "Layout": "One-Column"}), encoding="utf-8")
    (tmp_path / "webparts.json").write_text(json.dumps([
        {"PageUrl": page_url, "WebPartId": wid, "WebPartTitle": title, "ZoneID": "MainZone", "PartOrder": order, "Content": html}
        for order, (wid, title, html) in enumerate(parts)]), encoding="utf-8")
    raw = tmp_path / "raw"
    raw.mkdir(exist_ok=True)
    for order, (wid, _title, _html) in enumerate(parts):
        (raw / f"page_{wid}.xml").write_text(
            '<WebPart xmlns="http://schemas.microsoft.com/WebPart/v2"><ZoneID>MainZone</ZoneID>'
            f"<PartOrder>{order}</PartOrder></WebPart>", encoding="utf-8")
    out = tmp_path / "plan.json"
    splat = " ".join(f"-{k} '{v}'" for k, v in params.items())
    runner = tmp_path / "run.ps1"
    runner.write_text(
        f". '{planner}'\n"
        f"New-SpPageWave1DryRun -SourcePagePath '{tmp_path / 'page.json'}' -WebpartContentPath '{tmp_path / 'webparts.json'}' "
        f"-RawExportDirectory '{raw}' -TargetEnvironment dev -OutputPath '{out}' {splat} | Out-Null\n", encoding="utf-8")
    done = subprocess.run([PWSH, "-NoProfile", "-File", str(runner)], capture_output=True, text=True)
    assert done.returncode == 0, done.stdout + done.stderr
    return json.loads(out.read_text(encoding="utf-8"))


def html_of(plan: dict) -> str:
    return " ".join(c.get("Html", "") for c in plan["Components"] if isinstance(c, dict))


BAND = dict(AccordionOutput="Spfx", HeaderText="Central Programs")


@pytest.mark.parametrize("planner", PLANNERS, ids=IDS)
def test_numbered_content_editor_titles_add_no_heading(planner, tmp_path):
    """"Content Editor 2" is a default SP2016 name, not a heading to show on the page."""
    plan = run_planner(planner, tmp_path, [("a1", "Content Editor 2", LINKS)])
    assert "Content Editor" not in html_of(plan)


@pytest.mark.parametrize("planner", PLANNERS, ids=IDS)
def test_numbered_title_does_not_break_leading_image_split(planner, tmp_path):
    """A banner image in "Content Editor 1" is split off and dropped, the body text is kept."""
    plan = run_planner(planner, tmp_path, [("b1", "Content Editor 1", BANNER.format(zw=""))], LeadingImageWebPartIds="b1", **BAND)
    assert "Body text of the page." in html_of(plan)
    assert "Content Editor" not in html_of(plan)


@pytest.mark.parametrize("planner", PLANNERS, ids=IDS)
def test_zero_width_space_before_banner_image_still_splits(planner, tmp_path):
    """Regression guard: U+200B before the image is invisible and must not stop the split."""
    plan = run_planner(planner, tmp_path, [("c1", "Content Editor", BANNER.format(zw="\u200b"))], LeadingImageWebPartIds="c1", **BAND)
    assert "Body text of the page." in html_of(plan)


@pytest.mark.parametrize("planner", PLANNERS, ids=IDS)
def test_custom_titles_keep_their_heading(planner, tmp_path):
    """A real author-chosen title still becomes a heading (existing behaviour)."""
    plan = run_planner(planner, tmp_path, [("d1", "Quick Links", LINKS)])
    assert "<h3>Quick Links</h3>" in html_of(plan)
