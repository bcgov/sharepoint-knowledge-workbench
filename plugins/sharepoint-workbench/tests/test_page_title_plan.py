"""Tests for new-page-migration-dry-run.ps1: the plan must carry PageTitle (the SPO page Title field).

Purpose: Without plan.PageTitle the published page keeps its file name as Title ("CCA",
"Bill-C-78---...") while the banner shows the real title. The publisher sets the Title field only
from Target.PageTitle, which the package step copies from plan.PageTitle.

Key Input Dependencies: pwsh, scripts/new-page-migration-dry-run.ps1 in modernizing-sharepoint-pages
and its copy in publishing-sharepoint-pages (real planner, real fixtures, no mocks).
Usage: python -m pytest plugins/sharepoint-workbench/tests/test_page_title_plan.py

Function index: run_planner, test_* cases (banner title, Operations band, plain page, copies in sync).
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

ACCORDION = (
    '<div class="panel-group" id="accordion"><div class="panel panel-default"><div class="panel-heading">'
    '<h4 class="panel-title"><a class="collapsed" href="#collapse1" data-toggle="collapse">Panel one</a></h4></div>'
    '<div class="panel-collapse collapse" id="collapse1"><div class="panel-body"><p>One body</p></div></div></div></div>'
)


def run_planner(planner: Path, tmp_path: Path, **params) -> dict:
    """Run New-SpPageWave1DryRun on a one-page fixture and return the written plan.json."""
    page_url = "https://csb.jag.gov.bc.ca/CourtAdmin/Pages/CCA.aspx"
    (tmp_path / "page.json").write_text(json.dumps({
        "SiteName": "CourtAdmin", "ServerRelativeUrl": "/CourtAdmin/Pages/CCA.aspx", "Url": page_url,
        "Title": "CCA", "Layout": "One-Column"}), encoding="utf-8")
    (tmp_path / "webparts.json").write_text(json.dumps([
        {"PageUrl": page_url, "WebPartId": "ce", "WebPartTitle": "Content Editor", "ZoneID": "MainZone",
         "PartOrder": 0, "Content": "<p>Intro text.</p>"},
        {"PageUrl": page_url, "WebPartId": "acc", "WebPartTitle": "Accordion", "ZoneID": "MainZone",
         "PartOrder": 1, "Content": ACCORDION}]), encoding="utf-8")
    raw = tmp_path / "raw"
    raw.mkdir(exist_ok=True)
    for name, order in (("ce", 0), ("acc", 1)):
        (raw / f"page_{name}.xml").write_text(
            '<WebPart xmlns="http://schemas.microsoft.com/WebPart/v2"><ZoneID>MainZone</ZoneID>'
            f"<PartOrder>{order}</PartOrder></WebPart>", encoding="utf-8")
    out = tmp_path / "plan.json"
    splat = " ".join(f"-{k} '{v}'" for k, v in params.items())
    runner = tmp_path / "run.ps1"
    runner.write_text(
        f". '{planner}'\n"
        f"New-SpPageWave1DryRun -SourcePagePath '{tmp_path / 'page.json'}' "
        f"-WebpartContentPath '{tmp_path / 'webparts.json'}' -RawExportDirectory '{raw}' "
        f"-TargetEnvironment dev -OutputPath '{out}' {splat} | Out-Null\n", encoding="utf-8")
    done = subprocess.run([PWSH, "-NoProfile", "-File", str(runner)], capture_output=True, text=True)
    assert done.returncode == 0, done.stdout + done.stderr
    return json.loads(out.read_text(encoding="utf-8"))


@pytest.mark.parametrize("planner", PLANNERS, ids=["modernizing", "publishing"])
def test_title_banner_sets_page_title(planner, tmp_path):
    """-PageTitle with the Administration banner sets plan.PageTitle equal to the banner title."""
    plan = run_planner(planner, tmp_path, PageHeaderStyle="Administration", PageTitle="Court Services Branch Foundations")
    assert plan["PageHeader"]["Title"] == "Court Services Branch Foundations"
    assert plan["PageTitle"] == "Court Services Branch Foundations"


@pytest.mark.parametrize("planner", PLANNERS, ids=["modernizing", "publishing"])
def test_operations_band_sets_page_title_from_header_text(planner, tmp_path):
    """The Sheriff/Operations band has no PageHeader; Title 1 (-HeaderText) becomes the page Title."""
    plan = run_planner(planner, tmp_path, AccordionOutput="Spfx", HeaderText="BC Sheriff Service 3.1 and 3.2 Committees")
    assert "PageHeader" not in plan
    assert plan["PageTitle"] == "BC Sheriff Service 3.1 and 3.2 Committees"


@pytest.mark.parametrize("planner", PLANNERS, ids=["modernizing", "publishing"])
def test_explicit_page_title_wins_over_header_text(planner, tmp_path):
    """An explicit -PageTitle is the page Title even when a band title is also given."""
    plan = run_planner(planner, tmp_path, AccordionOutput="Spfx", HeaderText="Band line one", PageTitle="Explicit page title")
    assert plan["PageTitle"] == "Explicit page title"


@pytest.mark.parametrize("planner", PLANNERS, ids=["modernizing", "publishing"])
def test_no_title_inputs_leave_page_title_absent(planner, tmp_path):
    """No -PageTitle and no band: the plan has no PageTitle, so the publisher keeps its default."""
    plan = run_planner(planner, tmp_path)
    assert "PageTitle" not in plan


def test_planner_copies_stay_identical():
    """The two shipped planner copies must not drift."""
    assert PLANNERS[0].read_bytes() == PLANNERS[1].read_bytes()
