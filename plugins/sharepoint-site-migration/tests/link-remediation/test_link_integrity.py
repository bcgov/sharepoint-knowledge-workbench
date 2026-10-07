"""
test_link_integrity.py
======================

Purpose:
    Contract and safety tests for ``link_integrity`` -- the read-only
    post-remediation verification capability. It answers one question only:
    "does this link inventory still contain links that the rewrite ruleset says
    should have been rewritten, or that do not resolve?" It performs no tenant
    I/O and owns no publication-map reconciliation (that responsibility belongs
    to the sharepoint-site-build-and-publish plugin and is deliberately not
    duplicated here).

Layer: sharepoint-site-migration / tests

Key Input Dependencies: link_extraction, link_integrity, link_outcomes, link_rules, rewrite-rules.json, link_integrity.py.
"""

from pathlib import Path

import pytest

from link_extraction import ExtractedLink, LinkInventory, extract_links_from_paths
from link_integrity import LinkStatus, make_local_path_resolver, validate_link_integrity
from link_outcomes import Outcome
from link_rules import load_ruleset

FIXTURES = Path(__file__).resolve().parent / "fixtures"


@pytest.fixture()
def ruleset():
    """Pytest fixture providing ruleset."""
    return load_ruleset(FIXTURES / "rewrite-rules.json")


def _inventory(*urls):
    """Test helper: inventory."""
    return LinkInventory.from_links(
        [ExtractedLink(source="page", url=url, kind="hyperlink") for url in urls]
    )


def test_a_link_a_rule_still_matches_is_reported_as_residual_legacy(ruleset):
    """Verify a link a rule still matches is reported as residual legacy."""
    report = validate_link_integrity(_inventory("/Pages/team.aspx"), ruleset)

    assert report.outcome == Outcome.FAILED
    assert report.findings[0].status == LinkStatus.RESIDUAL_LEGACY
    assert report.findings[0].expected == "/SitePages/team.aspx"


def test_a_fully_rewritten_inventory_passes(ruleset):
    """Verify a fully rewritten inventory passes."""
    report = validate_link_integrity(_inventory("/SitePages/team.aspx"), ruleset)

    assert report.outcome == Outcome.OBSERVED
    assert report.findings[0].status == LinkStatus.OK


def test_a_mixed_inventory_is_partial(ruleset):
    """Verify a mixed inventory is partial."""
    report = validate_link_integrity(_inventory("/SitePages/a.aspx", "/Pages/b.aspx"), ruleset)

    assert report.outcome == Outcome.PARTIAL
    assert report.residual_count == 1


def test_an_empty_inventory_is_empty_not_a_pass(ruleset):
    """Verify an empty inventory is empty not a pass."""
    report = validate_link_integrity(_inventory(), ruleset)

    assert report.outcome == Outcome.EMPTY
    assert report.findings == []


@pytest.mark.parametrize("url", ["   ", "http://", "://broken", "ht tp://x"])
def test_malformed_urls_are_reported_not_silently_passed(ruleset, url):
    """Verify malformed urls are reported not silently passed."""
    report = validate_link_integrity(_inventory(url), ruleset)

    assert report.findings[0].status == LinkStatus.MALFORMED
    assert report.outcome == Outcome.FAILED


def test_without_a_resolver_resolution_is_reported_as_not_supported(ruleset):
    """Verify without a resolver resolution is reported as not supported."""
    report = validate_link_integrity(_inventory("/SitePages/a.aspx"), ruleset)

    assert report.resolution_outcome == Outcome.NOT_SUPPORTED


def test_with_a_real_filesystem_resolver_unresolvable_links_are_reported(tmp_path, ruleset):
    """Verify with a real filesystem resolver unresolvable links are reported."""
    (tmp_path / "SitePages").mkdir()
    (tmp_path / "SitePages" / "a.aspx").write_text("ok")
    resolver = make_local_path_resolver(tmp_path)

    report = validate_link_integrity(
        _inventory("/SitePages/a.aspx", "/SitePages/missing.aspx"), ruleset, resolver=resolver
    )

    assert report.resolution_outcome == Outcome.PARTIAL
    statuses = {finding.url: finding.status for finding in report.findings}
    assert statuses["/SitePages/a.aspx"] == LinkStatus.OK
    assert statuses["/SitePages/missing.aspx"] == LinkStatus.UNRESOLVABLE
    assert report.outcome == Outcome.PARTIAL


def test_local_path_resolver_does_not_escape_its_root(tmp_path, ruleset):
    """Verify local path resolver does not escape its root."""
    resolver = make_local_path_resolver(tmp_path)

    assert resolver("/../../etc/hosts") is False


def test_resolver_permission_denial_is_forbidden_not_a_pass(ruleset):
    """Verify resolver permission denial is forbidden not a pass."""
    def forbidding_resolver(url):
        """Test double for forbidding resolver used by the enclosing test."""
        raise PermissionError("denied")

    report = validate_link_integrity(
        _inventory("/SitePages/a.aspx"), ruleset, resolver=forbidding_resolver
    )

    assert report.resolution_outcome == Outcome.FORBIDDEN
    assert report.findings[0].status == LinkStatus.FORBIDDEN


def test_resolver_transport_error_is_unavailable_not_a_pass(ruleset):
    """Verify resolver transport error is unavailable not a pass."""
    def broken_resolver(url):
        """Test double for broken resolver used by the enclosing test."""
        raise RuntimeError("target system unreachable")

    report = validate_link_integrity(
        _inventory("/SitePages/a.aspx"), ruleset, resolver=broken_resolver
    )

    assert report.resolution_outcome == Outcome.UNAVAILABLE
    assert report.findings[0].status == LinkStatus.UNAVAILABLE


def test_external_links_are_skipped_by_resolution_but_still_reported(ruleset, tmp_path):
    """Verify external links are skipped by resolution but still reported."""
    resolver = make_local_path_resolver(tmp_path)
    report = validate_link_integrity(_inventory("https://www.example.org/ref"), ruleset, resolver=resolver)

    assert report.findings[0].status == LinkStatus.EXTERNAL
    assert report.outcome == Outcome.OBSERVED


def test_report_over_a_real_extracted_file_flags_the_legacy_links(ruleset):
    """Verify report over a real extracted file flags the legacy links."""
    inventory = extract_links_from_paths([FIXTURES / "legacy-page.aspx"])
    report = validate_link_integrity(inventory, ruleset)

    residual = {finding.url for finding in report.findings if finding.status == LinkStatus.RESIDUAL_LEGACY}
    assert "http://legacy.example.internal/Pages/overview.aspx" in residual
    assert "/Pages/team-directory.aspx" in residual
    assert report.outcome == Outcome.PARTIAL


def test_report_is_json_serialisable_evidence(ruleset):
    """Verify report is json serialisable evidence."""
    import json

    report = validate_link_integrity(_inventory("/Pages/a.aspx"), ruleset)
    payload = json.loads(json.dumps(report.to_dict()))

    assert payload["outcome"] == "Failed"
    assert payload["findings"][0]["status"] == "ResidualLegacy"


def test_integrity_module_performs_no_writes_and_no_tenant_io():
    """Verify integrity module performs no writes and no tenant io."""
    source = (Path(__file__).resolve().parents[2] / "scripts" / "link-remediation" / "link_integrity.py").read_text()

    for forbidden in ("write_text", "import requests", "urllib.request", "subprocess", "open("):
        assert forbidden not in source


@pytest.mark.parametrize(
    "literal",
    [__import__("base64").b64decode(x).decode() for x in ['amFnLmdvdi5iYy5jYQ==', 'YmNnb3Yuc2hhcmVwb2ludC5jb20=', 'QUctQ1NC', 'Q3Jvd25OZXQ=', 'SlVTVElO', 'Q0VJUw==', 'T1JEUw==', 'Y291cnRob3VzZQ==']],
)
def test_module_source_contains_no_project_literals(literal):
    """Verify module source contains no project literals."""
    source = (Path(__file__).resolve().parents[2] / "scripts" / "link-remediation" / "link_integrity.py").read_text()

    assert literal.lower() not in source.lower()
