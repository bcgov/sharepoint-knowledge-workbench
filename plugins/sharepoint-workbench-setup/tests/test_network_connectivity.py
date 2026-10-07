"""Purpose:
    Verify endpoint checklist construction and injected-connector reachability outcomes.

Key Input Dependencies:
    - network_connectivity pure checklist and injected-connector functions
    - No network transport.

test_network_connectivity.py
==============================

Tests for `network_connectivity`: a generic TCP-reachability pre-flight
check for Entra ID, SharePoint Online, Microsoft Graph, and CRL/OCSP
revocation endpoints, adapted from a enterprise repository network-connectivity
script. Zero network I/O by default -- all reachability behaviour is driven
through an injected `connector(host, port) -> bool` callable, never a live
default. No deployment-specific endpoint is included --
this module is tenant-agnostic beyond the SharePoint site's own hostname.

Function Index:
    - test_build_endpoint_checklist_derives_tenant_from_site_url
    - test_build_endpoint_checklist_depends_only_on_the_site_hostname
    - test_build_endpoint_checklist_marks_entra_and_spo_as_required
    - test_build_endpoint_checklist_marks_crl_ocsp_as_informational
    - test_build_endpoint_checklist_raises_on_missing_site_url
    - test_check_network_connectivity_all_required_reachable_passes
    - test_check_network_connectivity_all_required_reachable_passes.connector
    - test_check_network_connectivity_required_failure_fails
    - test_check_network_connectivity_required_failure_fails.connector
    - test_check_network_connectivity_optional_failure_does_not_fail_result
    - test_check_network_connectivity_optional_failure_does_not_fail_result.connector
    - test_check_network_connectivity_connector_exception_counts_as_unreachable
    - test_check_network_connectivity_connector_exception_counts_as_unreachable.connector
"""

import pytest

from network_connectivity import (
    build_endpoint_checklist,
    check_network_connectivity,
)


CONNECTION = {"SiteUrl": "https://example.sharepoint.com/sites/Demo"}


# The endpoint checklist derives the SharePoint host from SiteUrl and includes shared Microsoft endpoints.
def test_build_endpoint_checklist_derives_tenant_from_site_url():
    """The endpoint checklist derives the SharePoint host from SiteUrl and includes shared Microsoft endpoints."""
    checklist = build_endpoint_checklist(CONNECTION)
    hosts = {e["host"] for e in checklist}
    expected = {"example.sharepoint.com", "login.microsoftonline.com", "graph.microsoft.com"}
    assert expected <= hosts        # exact host names, not substrings of some URL


def test_build_endpoint_checklist_depends_only_on_the_site_hostname():
    """No endpoint is specific to any one deployment: changing the site URL changes only the tenant's own hosts."""
    first = {e["host"] for e in build_endpoint_checklist(CONNECTION)}
    second = {e["host"] for e in build_endpoint_checklist({"SiteUrl": "https://other.sharepoint.com/sites/Other"})}
    assert first - second == {"example.sharepoint.com"}
    assert second - first == {"other.sharepoint.com"}


# Entra ID, SharePoint Online, and Graph endpoints are marked required.
def test_build_endpoint_checklist_marks_entra_and_spo_as_required():
    """Entra ID, SharePoint Online, and Graph endpoints are marked required."""
    checklist = build_endpoint_checklist(CONNECTION)
    by_host = {e["host"]: e for e in checklist if e["port"] == 443}
    assert by_host["login.microsoftonline.com"]["required"] is True
    assert by_host["example.sharepoint.com"]["required"] is True
    assert by_host["graph.microsoft.com"]["required"] is True


# CRL and OCSP endpoints are informational rather than required.
def test_build_endpoint_checklist_marks_crl_ocsp_as_informational():
    """CRL and OCSP endpoints are informational rather than required."""
    checklist = build_endpoint_checklist(CONNECTION)
    crl_entries = [e for e in checklist if "crl" in e["host"].lower() or "ocsp" in e["host"].lower()]
    assert crl_entries, "expected at least one CRL/OCSP entry"
    assert all(e["required"] is False for e in crl_entries)


# Checklist construction raises ValueError when SiteUrl is absent.
def test_build_endpoint_checklist_raises_on_missing_site_url():
    """Checklist construction raises ValueError when SiteUrl is absent."""
    with pytest.raises(ValueError):
        build_endpoint_checklist({})


# Reachability of all required endpoints produces a successful result.
def test_check_network_connectivity_all_required_reachable_passes():
    # Report each requested endpoint as reachable for the connectivity check.
    """Reachability of all required endpoints produces a successful result."""
    def connector(host, port):
        """Report each requested endpoint as reachable for the connectivity check."""
        return True

    result = check_network_connectivity(CONNECTION, connector)
    assert result.success is True
    assert result.required_failures == []


# An unreachable required endpoint makes the connectivity result fail.
def test_check_network_connectivity_required_failure_fails():
    # Mark the Entra ID HTTPS endpoint unreachable and allow other endpoints.
    """An unreachable required endpoint makes the connectivity result fail."""
    def connector(host, port):
        """Mark the Entra ID HTTPS endpoint unreachable and allow other endpoints."""
        return not (host == "login.microsoftonline.com" and port == 443)

    result = check_network_connectivity(CONNECTION, connector)
    assert result.success is False
    assert any(f["host"] == "login.microsoftonline.com" for f in result.required_failures)


# Unreachable informational endpoints do not fail an otherwise successful check.
def test_check_network_connectivity_optional_failure_does_not_fail_result():
    # Mark only informational CRL and OCSP endpoints unreachable.
    """Unreachable informational endpoints do not fail an otherwise successful check."""
    def connector(host, port):
        """Mark only informational CRL and OCSP endpoints unreachable."""
        return "crl" not in host.lower() and "ocsp" not in host.lower()

    result = check_network_connectivity(CONNECTION, connector)
    assert result.success is True
    assert result.required_failures == []
    assert result.optional_failures != []


# A connector exception is reported as an unreachable endpoint rather than escaping.
def test_check_network_connectivity_connector_exception_counts_as_unreachable():
    # Raise a timeout for the Entra endpoint and report other endpoints reachable.
    """A connector exception is reported as an unreachable endpoint rather than escaping."""
    def connector(host, port):
        """Raise a timeout for the Entra endpoint and report other endpoints reachable."""
        if host == "login.microsoftonline.com":
            raise TimeoutError("network unreachable")
        return True

    result = check_network_connectivity(CONNECTION, connector)
    assert result.success is False
    assert any(f["host"] == "login.microsoftonline.com" for f in result.required_failures)
