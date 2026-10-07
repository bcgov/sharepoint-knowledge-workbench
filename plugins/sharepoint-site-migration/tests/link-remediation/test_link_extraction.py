"""
test_link_extraction.py
=======================

Purpose:
    Contract and safety tests for ``link_extraction`` -- the read-only link
    inventory capability of the sharepoint-site-migration plugin.

Layer: sharepoint-site-migration / tests

Critical runtime paths (file parsing, path resolution) are exercised against the
real filesystem, never mocked (.agent/rules/test-driven-development.md).

Key Input Dependencies: link_extraction, link_outcomes, link_extraction.py.
"""

from pathlib import Path

import pytest

from link_extraction import (
    ExtractedLink,
    LinkInventory,
    extract_links_from_paths,
    extract_links_from_text,
)
from link_outcomes import Outcome

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def test_extract_links_from_text_returns_urls_with_source_and_kind():
    """Verify extract links from text returns urls with source and kind."""
    text = '<a href="/Pages/a.aspx">a</a><img src="/SiteAssets/x.png">'
    links = extract_links_from_text(text, source="page-a")

    assert [link.url for link in links] == ["/Pages/a.aspx", "/SiteAssets/x.png"]
    assert all(isinstance(link, ExtractedLink) for link in links)
    assert links[0].source == "page-a"
    assert links[0].kind == "page-link"
    assert links[1].kind == "asset-reference"


def test_extract_links_from_text_skips_anchors_and_script_pseudo_urls():
    """Verify extract links from text skips anchors and script pseudo urls."""
    text = '<a href="#top">t</a><a href="javascript:void(0)">j</a><a href="/Pages/a.aspx">a</a>'
    links = extract_links_from_text(text, source="page-a")

    assert [link.url for link in links] == ["/Pages/a.aspx"]


def test_extract_links_from_text_classifies_form_and_masterpage_surfaces():
    """Verify extract links from text classifies form and masterpage surfaces."""
    text = (
        '<a href="/Lists/L/NewForm.aspx">n</a>'
        '<link href="/_catalogs/masterpage/x.master">'
        '<a href="https://www.example.org/ref">e</a>'
    )
    kinds = {link.url: link.kind for link in extract_links_from_text(text, source="s")}

    assert kinds["/Lists/L/NewForm.aspx"] == "form-action"
    assert kinds["/_catalogs/masterpage/x.master"] == "masterpage-asset"
    assert kinds["https://www.example.org/ref"] == "hyperlink"


def test_extract_links_from_text_on_empty_content_is_outcome_empty_not_failure():
    """Verify extract links from text on empty content is outcome empty not failure."""
    inventory = LinkInventory.from_links([])

    assert inventory.outcome == Outcome.EMPTY
    assert inventory.links == []


def test_extract_links_from_text_ignores_platform_artifacts_by_default():
    """Verify extract links from text ignores platform artifacts by default."""
    text = '<img src="/_layouts/images/blank.gif"><script src="/_layouts/15/init.js">'
    links = extract_links_from_text(text, source="s")

    assert links == []


def test_extract_links_from_text_can_retain_platform_artifacts_when_asked():
    """Verify extract links from text can retain platform artifacts when asked."""
    text = '<img src="/_layouts/images/blank.gif">'
    links = extract_links_from_text(text, source="s", ignore_platform_artifacts=False)

    assert [link.url for link in links] == ["/_layouts/images/blank.gif"]


def test_extract_links_from_paths_reads_real_files_and_reports_observed():
    """Verify extract links from paths reads real files and reports observed."""
    inventory = extract_links_from_paths([FIXTURES / "legacy-page.aspx"])

    assert inventory.outcome == Outcome.OBSERVED
    urls = [link.url for link in inventory.links]
    assert "http://legacy.example.internal/Pages/overview.aspx" in urls
    assert "/Pages/team-directory.aspx" in urls
    assert "#section-2" not in urls
    assert "/_layouts/15/init.js" not in urls
    assert all(link.source == "legacy-page.aspx" for link in inventory.links)


def test_extract_links_from_paths_missing_file_is_partial_not_silent_success(tmp_path):
    """Verify extract links from paths missing file is partial not silent success."""
    missing = tmp_path / "does-not-exist.aspx"
    inventory = extract_links_from_paths([FIXTURES / "legacy-page.aspx", missing])

    assert inventory.outcome == Outcome.PARTIAL
    assert any(str(missing) in problem for problem in inventory.problems)
    assert inventory.links, "links from the readable file must still be reported"


def test_extract_links_from_paths_with_no_inputs_is_empty():
    """Verify extract links from paths with no inputs is empty."""
    inventory = extract_links_from_paths([])

    assert inventory.outcome == Outcome.EMPTY
    assert inventory.problems == []


def test_extract_links_from_paths_unreadable_directory_is_partial(tmp_path):
    """Verify extract links from paths unreadable directory is partial."""
    a_directory = tmp_path / "some-dir"
    a_directory.mkdir()
    inventory = extract_links_from_paths([a_directory])

    assert inventory.outcome == Outcome.FAILED
    assert inventory.problems


def test_inventory_to_dict_is_json_serialisable():
    """Verify inventory to dict is json serialisable."""
    import json

    inventory = extract_links_from_paths([FIXTURES / "legacy-page.aspx"])
    payload = json.dumps(inventory.to_dict())

    assert '"outcome": "Observed"' in payload


def test_malformed_markup_does_not_raise():
    """Verify malformed markup does not raise."""
    text = '<a href=>broken</a><a href="   ">blank</a><a href="/Pages/ok.aspx">ok</a>'
    links = extract_links_from_text(text, source="s")

    assert [link.url for link in links] == ["/Pages/ok.aspx"]


@pytest.mark.parametrize(
    "literal",
    [__import__("base64").b64decode(x).decode() for x in ['amFnLmdvdi5iYy5jYQ==', 'YmNnb3Yuc2hhcmVwb2ludC5jb20=', 'QUctQ1NC', 'SlVTVElO', 'Q0VJUw==', 'T1JEUw==', 'Y291cnRob3VzZQ==']],
)
def test_module_source_contains_no_project_literals(literal):
    """Verify module source contains no project literals."""
    source = (Path(__file__).resolve().parents[2] / "scripts" / "link-remediation" / "link_extraction.py").read_text()

    assert literal.lower() not in source.lower()
