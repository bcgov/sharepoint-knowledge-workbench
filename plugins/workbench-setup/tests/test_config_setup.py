"""
test_config_setup.py
======================

Tests for `config_setup` (Phase 6 Task 0.17's `setup-sharepoint-
connection` skill): creates the root, git-ignored `config.psd1` from
the plugin's canonical `assets/config.psd1.example`. Generating the
file is the default action and never connects to anything -- per
design spec Section 8's corrected behavior, an explicit,
separately-invoked read-only connection test is a distinct opt-in step
(`test_connection`), never triggered as a side effect of writing the
config.
"""

from pathlib import Path

import pytest

import config_setup as cs


# ---------------------------------------------------------------------------
# validate_connection_answers -- mandatory/conditional key checks
# ---------------------------------------------------------------------------

def test_validate_connection_answers_happy_path_interactive():
    issues = cs.validate_connection_answers(
        connection={
            "SiteUrl": "https://tenant.sharepoint.com/sites/site",
            "TenantId": "tenant-id",
            "ClientId": "client-id",
            "AuthenticationMode": "Interactive",
        },
        authentication={},
    )
    assert issues == []


def test_validate_connection_answers_rejects_missing_mandatory_keys():
    issues = cs.validate_connection_answers(
        connection={"SiteUrl": "", "TenantId": "", "ClientId": "", "AuthenticationMode": ""},
        authentication={},
    )
    codes = {issue.code for issue in issues}
    assert {"missing_site_url", "missing_tenant_id", "missing_client_id", "missing_authentication_mode"} <= codes


def test_validate_connection_answers_requires_certificate_thumbprint_for_certificate_mode():
    issues = cs.validate_connection_answers(
        connection={
            "SiteUrl": "https://tenant.sharepoint.com/sites/site",
            "TenantId": "tenant-id",
            "ClientId": "client-id",
            "AuthenticationMode": "Certificate",
        },
        authentication={},
    )
    assert any(issue.code == "missing_certificate_thumbprint" for issue in issues)


def test_validate_connection_answers_certificate_mode_satisfied():
    issues = cs.validate_connection_answers(
        connection={
            "SiteUrl": "https://tenant.sharepoint.com/sites/site",
            "TenantId": "tenant-id",
            "ClientId": "client-id",
            "AuthenticationMode": "Certificate",
        },
        authentication={"CertificateThumbprint": "abc123", "TenantAdminUrl": "https://tenant-admin.sharepoint.com"},
    )
    assert issues == []


def test_validate_connection_answers_interactive_mode_does_not_require_certificate_fields():
    issues = cs.validate_connection_answers(
        connection={
            "SiteUrl": "https://tenant.sharepoint.com/sites/site",
            "TenantId": "tenant-id",
            "ClientId": "client-id",
            "AuthenticationMode": "Interactive",
        },
        authentication={},
    )
    assert not any("certificate" in issue.code for issue in issues)


# ---------------------------------------------------------------------------
# build_config_psd1 -- text generation
# ---------------------------------------------------------------------------

def test_build_config_psd1_contains_mandatory_fields():
    text = cs.build_config_psd1(
        connection={
            "SiteUrl": "https://tenant.sharepoint.com/sites/site",
            "TenantId": "tenant-id",
            "ClientId": "client-id",
            "AuthenticationMode": "Interactive",
        },
        authentication={"CertificateThumbprint": "", "TenantAdminUrl": ""},
        defaults={
            "DefaultHumanPublicationLibrary": "KnowledgePublications",
            "DefaultAgentGroundingLibrary": "AgentGrounding",
            "DefaultAgentAssetsLibrary": "AgentAssets",
            "DefaultSitePagesLibrary": "Site Pages",
        },
    )
    assert '"https://tenant.sharepoint.com/sites/site"' in text
    assert text.strip().startswith("@{")


# ---------------------------------------------------------------------------
# write_config -- default action never connects, refuses silent overwrite
# ---------------------------------------------------------------------------

def test_write_config_creates_file(tmp_path):
    output_path = cs.write_config(
        tmp_path,
        connection={
            "SiteUrl": "https://tenant.sharepoint.com/sites/site",
            "TenantId": "tenant-id",
            "ClientId": "client-id",
            "AuthenticationMode": "Interactive",
        },
        authentication={},
        defaults={},
    )
    assert output_path == tmp_path / "config.psd1"
    assert output_path.exists()
    assert "sites/site" in output_path.read_text()


def test_write_config_rejects_invalid_answers(tmp_path):
    with pytest.raises(cs.ConfigSetupError):
        cs.write_config(
            tmp_path,
            connection={"SiteUrl": "", "TenantId": "", "ClientId": "", "AuthenticationMode": ""},
            authentication={},
            defaults={},
        )
    assert not (tmp_path / "config.psd1").exists()


def test_write_config_refuses_silent_overwrite(tmp_path):
    answers = dict(
        connection={
            "SiteUrl": "https://tenant.sharepoint.com/sites/site",
            "TenantId": "tenant-id",
            "ClientId": "client-id",
            "AuthenticationMode": "Interactive",
        },
        authentication={},
        defaults={},
    )
    cs.write_config(tmp_path, **answers)
    with pytest.raises(cs.ConfigSetupError):
        cs.write_config(tmp_path, **answers)
    cs.write_config(tmp_path, **answers, overwrite=True)


# ---------------------------------------------------------------------------
# test_connection -- explicit opt-in only, never a side effect of writing
# ---------------------------------------------------------------------------

def test_test_connection_requires_explicit_connector():
    with pytest.raises(NotImplementedError):
        cs.test_connection(
            connection={
                "SiteUrl": "https://tenant.sharepoint.com/sites/site",
                "TenantId": "tenant-id",
                "ClientId": "client-id",
                "AuthenticationMode": "Interactive",
            }
        )


def test_test_connection_uses_injected_connector_when_provided():
    calls = []

    def fake_connector(connection):
        calls.append(connection)
        return True

    result = cs.test_connection(
        connection={
            "SiteUrl": "https://tenant.sharepoint.com/sites/site",
            "TenantId": "tenant-id",
            "ClientId": "client-id",
            "AuthenticationMode": "Interactive",
        },
        connector=fake_connector,
    )
    assert result is True
    assert len(calls) == 1


def test_write_config_never_calls_test_connection(tmp_path, monkeypatch):
    called = []
    monkeypatch.setattr(cs, "test_connection", lambda *a, **k: called.append(1))
    cs.write_config(
        tmp_path,
        connection={
            "SiteUrl": "https://tenant.sharepoint.com/sites/site",
            "TenantId": "tenant-id",
            "ClientId": "client-id",
            "AuthenticationMode": "Interactive",
        },
        authentication={},
        defaults={},
    )
    assert called == []


# ---------------------------------------------------------------------------
# Structural guarantee -- zero tenant I/O in this module beyond opt-in test
# ---------------------------------------------------------------------------

def test_module_never_imports_pnp_or_http_clients():
    source = Path(cs.__file__).read_text()
    for forbidden in ("import requests", "PnPOnline", "urllib.request"):
        assert forbidden not in source
