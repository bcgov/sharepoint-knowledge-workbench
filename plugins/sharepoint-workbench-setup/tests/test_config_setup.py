"""Purpose:
    Verify connection validation and configuration writing remain explicit and tenant-I/O-free by default.

Key Input Dependencies:
    - config_setup module and psd1_writer
    - Temporary filesystem paths provided by pytest.

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

Function Index:
    - test_validate_connection_answers_happy_path_interactive
    - test_validate_connection_answers_rejects_missing_mandatory_keys
    - test_validate_connection_answers_requires_certificate_thumbprint_for_certificate_mode
    - test_validate_connection_answers_certificate_mode_satisfied
    - test_validate_connection_answers_interactive_mode_does_not_require_certificate_fields
    - test_build_config_psd1_contains_mandatory_fields
    - test_write_config_creates_file
    - test_write_config_rejects_invalid_answers
    - test_write_config_refuses_silent_overwrite
    - test_test_connection_requires_explicit_connector
    - test_test_connection_uses_injected_connector_when_provided
    - test_test_connection_uses_injected_connector_when_provided.fake_connector
    - test_write_config_never_calls_test_connection
    - test_module_never_imports_pnp_or_http_clients
"""

from pathlib import Path

import pytest

import config_setup as cs


# ---------------------------------------------------------------------------
# validate_connection_answers -- mandatory/conditional key checks
# ---------------------------------------------------------------------------

# A complete interactive connection configuration passes answer validation.
def test_validate_connection_answers_happy_path_interactive():
    """A complete interactive connection configuration passes answer validation."""
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


# Missing mandatory connection keys produce their corresponding validation issues.
def test_validate_connection_answers_rejects_missing_mandatory_keys():
    """Missing mandatory connection keys produce their corresponding validation issues."""
    issues = cs.validate_connection_answers(
        connection={"SiteUrl": "", "TenantId": "", "ClientId": "", "AuthenticationMode": ""},
        authentication={},
    )
    codes = {issue.code for issue in issues}
    assert {"missing_site_url", "missing_tenant_id", "missing_client_id", "missing_authentication_mode"} <= codes


# Certificate authentication requires a certificate thumbprint.
def test_validate_connection_answers_requires_certificate_thumbprint_for_certificate_mode():
    """Certificate authentication requires a certificate thumbprint."""
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


# Certificate authentication passes when its conditional fields are supplied.
def test_validate_connection_answers_certificate_mode_satisfied():
    """Certificate authentication passes when its conditional fields are supplied."""
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


# Interactive authentication does not require certificate-only fields.
def test_validate_connection_answers_interactive_mode_does_not_require_certificate_fields():
    """Interactive authentication does not require certificate-only fields."""
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

# Verify that build config psd1 contains mandatory fields.
def test_build_config_psd1_contains_mandatory_fields():
    """Verify that build config psd1 contains mandatory fields."""
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

# Verify that write config creates file.
def test_write_config_creates_file(tmp_path):
    """Verify that write config creates file."""
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


# Verify that write config rejects invalid answers.
def test_write_config_rejects_invalid_answers(tmp_path):
    """Verify that write config rejects invalid answers."""
    with pytest.raises(cs.ConfigSetupError):
        cs.write_config(
            tmp_path,
            connection={"SiteUrl": "", "TenantId": "", "ClientId": "", "AuthenticationMode": ""},
            authentication={},
            defaults={},
        )
    assert not (tmp_path / "config.psd1").exists()


# Verify that write config refuses silent overwrite.
def test_write_config_refuses_silent_overwrite(tmp_path):
    """Verify that write config refuses silent overwrite."""
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

# Verify that test connection requires explicit connector.
def test_test_connection_requires_explicit_connector():
    """Verify that test connection requires explicit connector."""
    with pytest.raises(NotImplementedError):
        cs.test_connection(
            connection={
                "SiteUrl": "https://tenant.sharepoint.com/sites/site",
                "TenantId": "tenant-id",
                "ClientId": "client-id",
                "AuthenticationMode": "Interactive",
            }
        )


# Verify that test connection uses injected connector when provided.
def test_test_connection_uses_injected_connector_when_provided():
    """Verify that test connection uses injected connector when provided."""
    calls = []

    # Record the received connection and return a successful validation result.
    def fake_connector(connection):
        """Record the received connection and return a successful validation result."""
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


# Verify that write config never calls test connection.
def test_write_config_never_calls_test_connection(tmp_path, monkeypatch):
    """Verify that write config never calls test connection."""
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

# Verify that module never imports pnp or http clients.
def test_module_never_imports_pnp_or_http_clients():
    """Verify that module never imports pnp or http clients."""
    source = Path(cs.__file__).read_text()
    for forbidden in ("import requests", "PnPOnline", "urllib.request"):
        assert forbidden not in source
