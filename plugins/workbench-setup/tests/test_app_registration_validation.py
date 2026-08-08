"""
test_app_registration_validation.py
=====================================

Tests for `app_registration_validation` (Phase 9 extraction of CMAT's
`sp-validating-app-registration` skill): a generic Entra ID app-registration
validator built on the device-code OAuth2 flow + `_api/contextinfo` REST
smoke test. Zero tenant I/O by default -- all network-shaped behaviour is
driven through an injected `http_client`, never a live default.
"""

import base64
import json

import pytest

from app_registration_validation import (
    AppRegistrationValidationError,
    build_context_info_request,
    build_device_code_request,
    build_token_poll_request,
    decode_jwt_claims,
    make_device_code_connector,
    validate_app_registration,
    validate_permission_boundary,
)


def _fake_jwt(claims: dict) -> str:
    payload = base64.urlsafe_b64encode(json.dumps(claims).encode()).rstrip(b"=").decode()
    return f"header.{payload}.signature"


CONNECTION = {
    "SiteUrl": "https://example.sharepoint.com/sites/Demo",
    "TenantId": "example-tenant-id",
    "ClientId": "example-client-id",
    "AuthenticationMode": "DeviceCode",
}


class FakeHttpClient:
    """Injected transport double -- no network I/O."""

    def __init__(self, *, token="tok123", claims=None, digest="digest-value", raise_on=None):
        self._token = token
        self._claims = claims if claims is not None else {"upn": "user@example.com", "appid": "app-id-123"}
        self._digest = digest
        self._raise_on = raise_on or {}

    def request_device_code(self, url, body):
        if "device_code" in self._raise_on:
            raise RuntimeError(self._raise_on["device_code"])
        return {"device_code": "dc-abc", "interval": 0, "expires_in": 60, "message": "go authenticate"}

    def poll_for_token(self, url, body):
        if "token" in self._raise_on:
            raise RuntimeError(self._raise_on["token"])
        if self._token is None:
            return {}
        return {"access_token": _fake_jwt(self._claims)}

    def get_context_info(self, url, headers):
        if "context_info" in self._raise_on:
            raise RuntimeError(self._raise_on["context_info"])
        if self._digest is None:
            return {}
        return {"FormDigestValue": self._digest}


# ---------------------------------------------------------------------------
# Pure request-builder / claims-decoding tests (no network)
# ---------------------------------------------------------------------------

def test_build_device_code_request_is_pure_and_generic():
    req = build_device_code_request(CONNECTION)
    assert req["url"] == "https://login.microsoftonline.com/example-tenant-id/oauth2/v2.0/devicecode"
    assert req["body"]["client_id"] == "example-client-id"
    assert req["body"]["scope"] == "https://example.sharepoint.com/sites/Demo/.default"


def test_build_device_code_request_missing_field_raises():
    with pytest.raises(AppRegistrationValidationError):
        build_device_code_request({"TenantId": "t", "ClientId": "c"})


def test_build_token_poll_request():
    req = build_token_poll_request(CONNECTION, "dc-abc")
    assert req["url"].endswith("/token")
    assert req["body"]["device_code"] == "dc-abc"
    assert req["body"]["grant_type"] == "urn:ietf:params:oauth:grant-type:device_code"


def test_build_context_info_request():
    req = build_context_info_request(CONNECTION, "tok123")
    assert req["url"] == "https://example.sharepoint.com/sites/Demo/_api/contextinfo"
    assert req["headers"]["Authorization"] == "Bearer tok123"


def test_decode_jwt_claims_roundtrip():
    token = _fake_jwt({"upn": "user@example.com", "appid": "abc"})
    claims = decode_jwt_claims(token)
    assert claims == {"upn": "user@example.com", "appid": "abc"}


def test_decode_jwt_claims_malformed_raises():
    with pytest.raises(AppRegistrationValidationError):
        decode_jwt_claims("not-a-jwt")


# ---------------------------------------------------------------------------
# validate_app_registration -- normal, negative, permission-denial cases
# ---------------------------------------------------------------------------

def test_validate_app_registration_success():
    result = validate_app_registration(CONNECTION, FakeHttpClient())
    assert result.success is True
    assert result.signed_in_as == "user@example.com"
    assert result.app_id == "app-id-123"


def test_validate_app_registration_missing_config_raises():
    with pytest.raises(AppRegistrationValidationError):
        validate_app_registration({}, FakeHttpClient())


def test_validate_app_registration_device_code_failure_is_honest_partial_result():
    client = FakeHttpClient(raise_on={"device_code": "network unreachable"})
    result = validate_app_registration(CONNECTION, client)
    assert result.success is False
    assert "device code request failed" in result.detail


def test_validate_app_registration_token_failure_is_honest_partial_result():
    client = FakeHttpClient(raise_on={"token": "authorization_declined"})
    result = validate_app_registration(CONNECTION, client)
    assert result.success is False
    assert "token acquisition failed" in result.detail


def test_validate_app_registration_permission_denial_reports_failure_not_empty_success():
    # contextinfo call raises -- e.g. 403 Forbidden -- must not be reported as success.
    client = FakeHttpClient(raise_on={"context_info": "403 Forbidden"})
    result = validate_app_registration(CONNECTION, client)
    assert result.success is False
    assert "contextinfo call failed" in result.detail
    # still surfaces who authenticated, for honest partial reporting
    assert result.signed_in_as == "user@example.com"


def test_validate_app_registration_missing_digest_is_failure():
    client = FakeHttpClient(digest=None)
    result = validate_app_registration(CONNECTION, client)
    assert result.success is False
    assert "FormDigestValue" in result.detail


def test_validate_app_registration_result_has_no_project_literals():
    result = validate_app_registration(CONNECTION, FakeHttpClient())
    blob = str(result.to_dict()).lower()
    for literal in ("bcgov", "jag-csb", "cmat", "justin", "ceis", "ords"):
        assert literal not in blob


# ---------------------------------------------------------------------------
# make_device_code_connector -- config_setup.test_connection() compatibility
# ---------------------------------------------------------------------------

def test_make_device_code_connector_returns_bool_true_on_success():
    connector = make_device_code_connector(FakeHttpClient())
    assert connector(CONNECTION) is True


def test_make_device_code_connector_returns_bool_false_on_failure():
    connector = make_device_code_connector(FakeHttpClient(digest=None))
    assert connector(CONNECTION) is False


def test_connector_wires_into_config_setup_test_connection_opt_in_only():
    """The whole point of the factory: it must satisfy config_setup.
    test_connection's connector(connection) -> bool contract, and test_
    connection must still raise NotImplementedError with no connector
    injected -- no autonomous default connection is introduced."""
    from config_setup import test_connection

    with pytest.raises(NotImplementedError):
        test_connection(CONNECTION)

    connector = make_device_code_connector(FakeHttpClient())
    assert test_connection(CONNECTION, connector=connector) is True


# ---------------------------------------------------------------------------
# validate_permission_boundary -- proves Effective permissions = App ∩ User
# ---------------------------------------------------------------------------

AUTHORIZED_CONNECTION = {
    "SiteUrl": "https://example.sharepoint.com/sites/Authorized",
    "TenantId": "example-tenant-id",
    "ClientId": "example-client-id",
}

UNAUTHORIZED_CONNECTION = {
    "SiteUrl": "https://example.sharepoint.com/sites/Unauthorized",
    "TenantId": "example-tenant-id",
    "ClientId": "example-client-id",
}


class SiteAwareHttpClient:
    """Injected transport double whose get_context_info behaviour depends on
    which site's contextinfo URL is called -- lets one client simulate a
    delegated app registration that succeeds on an authorized site and is
    denied on an unauthorized one, without any real tenant."""

    def __init__(self, *, denied_site_url: str):
        self._denied_site_url = denied_site_url

    def request_device_code(self, url, body):
        return {"device_code": "dc-abc", "interval": 0, "expires_in": 60}

    def poll_for_token(self, url, body):
        return {"access_token": _fake_jwt({"upn": "user@example.com", "appid": "app-id-123"})}

    def get_context_info(self, url, headers):
        if url.startswith(self._denied_site_url):
            raise RuntimeError("403 Access Denied")
        return {"FormDigestValue": "digest-value"}


def test_boundary_proven_when_authorized_succeeds_and_unauthorized_is_denied():
    client = SiteAwareHttpClient(denied_site_url=UNAUTHORIZED_CONNECTION["SiteUrl"])
    result = validate_permission_boundary(AUTHORIZED_CONNECTION, UNAUTHORIZED_CONNECTION, client)
    assert result.boundary_proven is True
    assert result.authorized_result.success is True
    assert result.unauthorized_result.success is False


def test_boundary_not_proven_when_unauthorized_site_unexpectedly_succeeds():
    """If the 'unauthorized' site is actually reachable, the app registration
    grants broader access than intended -- a real security finding, must be
    reported distinctly from a plain test failure, never silently passed."""
    client = SiteAwareHttpClient(denied_site_url="https://nonexistent.example.com/never-called")
    result = validate_permission_boundary(AUTHORIZED_CONNECTION, UNAUTHORIZED_CONNECTION, client)
    assert result.boundary_proven is False
    assert "unauthorized site" in result.detail.lower()


def test_boundary_not_proven_when_authorized_site_unexpectedly_fails():
    """If the 'authorized' site fails too, the registration or the site
    permission is misconfigured -- distinct from the unauthorized-succeeded
    case, and must say so."""
    client = SiteAwareHttpClient(denied_site_url=AUTHORIZED_CONNECTION["SiteUrl"])
    result = validate_permission_boundary(AUTHORIZED_CONNECTION, UNAUTHORIZED_CONNECTION, client)
    assert result.boundary_proven is False
    assert "authorized site" in result.detail.lower()


def test_boundary_result_serializes_both_sub_results():
    client = SiteAwareHttpClient(denied_site_url=UNAUTHORIZED_CONNECTION["SiteUrl"])
    result = validate_permission_boundary(AUTHORIZED_CONNECTION, UNAUTHORIZED_CONNECTION, client)
    as_dict = result.to_dict()
    assert as_dict["boundary_proven"] is True
    assert as_dict["authorized_result"]["success"] is True
    assert as_dict["unauthorized_result"]["success"] is False
