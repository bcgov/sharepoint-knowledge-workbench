"""Purpose:
    Verify app-registration request construction, token diagnostics, validation results, and permission boundaries.

Key Input Dependencies:
    - app_registration_validation pure request builders and validator
    - Injected fake HTTP clients; no network access.

test_app_registration_validation.py
=====================================

Tests for `app_registration_validation` (Phase 9 extraction of enterprise
`sp-validating-app-registration` skill): a generic Entra ID app-registration
validator built on the device-code OAuth2 flow + `_api/contextinfo` REST
smoke test. Zero tenant I/O by default -- all network-shaped behaviour is
driven through an injected `http_client`, never a live default.

Function Index:
    - _fake_jwt
    - FakeHttpClient
    - FakeHttpClient.__init__
    - FakeHttpClient.request_device_code
    - FakeHttpClient.poll_for_token
    - FakeHttpClient.get_context_info
    - test_build_device_code_request_is_pure_and_generic
    - test_build_device_code_request_missing_field_raises
    - test_build_token_poll_request
    - test_build_context_info_request
    - test_decode_jwt_claims_roundtrip
    - test_decode_jwt_claims_malformed_raises
    - test_validate_app_registration_success
    - test_validate_app_registration_missing_config_raises
    - test_validate_app_registration_device_code_failure_is_honest_partial_result
    - test_validate_app_registration_token_failure_is_honest_partial_result
    - test_validate_app_registration_permission_denial_reports_failure_not_empty_success
    - test_validate_app_registration_missing_digest_is_failure
    - test_validate_app_registration_result_has_no_project_literals
    - test_make_device_code_connector_returns_bool_true_on_success
    - test_make_device_code_connector_returns_bool_false_on_failure
    - test_connector_wires_into_config_setup_test_connection_opt_in_only
    - SiteAwareHttpClient
    - SiteAwareHttpClient.__init__
    - SiteAwareHttpClient.request_device_code
    - SiteAwareHttpClient.poll_for_token
    - SiteAwareHttpClient.get_context_info
    - test_boundary_proven_when_authorized_succeeds_and_unauthorized_is_denied
    - test_boundary_not_proven_when_unauthorized_site_unexpectedly_succeeds
    - test_boundary_not_proven_when_authorized_site_unexpectedly_fails
    - test_boundary_result_serializes_both_sub_results
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


# Encode the supplied claims into a structurally valid JWT for decoder tests.
def _fake_jwt(claims: dict) -> str:
    """Encode the supplied claims into a structurally valid JWT for decoder tests."""
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

    # Store the configured fake token, claims, digest, and simulated failures.
    def __init__(self, *, token="tok123", claims=None, digest="digest-value", raise_on=None):
        """Store the configured fake token, claims, digest, and simulated failures."""
        self._token = token
        self._claims = claims if claims is not None else {"upn": "user@example.com", "appid": "app-id-123"}
        self._digest = digest
        self._raise_on = raise_on or {}

    # Return a deterministic device-code response without contacting an identity service.
    def request_device_code(self, url, body):
        """Return a deterministic device-code response without contacting an identity service."""
        if "device_code" in self._raise_on:
            raise RuntimeError(self._raise_on["device_code"])
        return {"device_code": "dc-abc", "interval": 0, "expires_in": 60, "message": "go authenticate"}

    # Return a fabricated token response or raise the configured acquisition failure.
    def poll_for_token(self, url, body):
        """Return a fabricated token response or raise the configured acquisition failure."""
        if "token" in self._raise_on:
            raise RuntimeError(self._raise_on["token"])
        if self._token is None:
            return {}
        return {"access_token": _fake_jwt(self._claims)}

    # Return the configured form digest or raise the simulated context-info failure.
    def get_context_info(self, url, headers):
        """Return the configured form digest or raise the simulated context-info failure."""
        if "context_info" in self._raise_on:
            raise RuntimeError(self._raise_on["context_info"])
        if self._digest is None:
            return {}
        return {"FormDigestValue": self._digest}


# ---------------------------------------------------------------------------
# Pure request-builder / claims-decoding tests (no network)
# ---------------------------------------------------------------------------

# Verify that build device code request is pure and generic.
def test_build_device_code_request_is_pure_and_generic():
    """Verify that build device code request is pure and generic."""
    req = build_device_code_request(CONNECTION)
    assert req["url"] == "https://login.microsoftonline.com/example-tenant-id/oauth2/v2.0/devicecode"
    assert req["body"]["client_id"] == "example-client-id"
    assert req["body"]["scope"] == "https://example.sharepoint.com/sites/Demo/.default"


# Verify that build device code request missing field raises.
def test_build_device_code_request_missing_field_raises():
    """Verify that build device code request missing field raises."""
    with pytest.raises(AppRegistrationValidationError):
        build_device_code_request({"TenantId": "t", "ClientId": "c"})


# Verify that build token poll request.
def test_build_token_poll_request():
    """Verify that build token poll request."""
    req = build_token_poll_request(CONNECTION, "dc-abc")
    assert req["url"].endswith("/token")
    assert req["body"]["device_code"] == "dc-abc"
    assert req["body"]["grant_type"] == "urn:ietf:params:oauth:grant-type:device_code"


# Verify that build context info request.
def test_build_context_info_request():
    """Verify that build context info request."""
    req = build_context_info_request(CONNECTION, "tok123")
    assert req["url"] == "https://example.sharepoint.com/sites/Demo/_api/contextinfo"
    assert req["headers"]["Authorization"] == "Bearer tok123"


# Verify that decode jwt claims roundtrip.
def test_decode_jwt_claims_roundtrip():
    """Verify that decode jwt claims roundtrip."""
    token = _fake_jwt({"upn": "user@example.com", "appid": "abc"})
    claims = decode_jwt_claims(token)
    assert claims == {"upn": "user@example.com", "appid": "abc"}


# Verify that decode jwt claims malformed raises.
def test_decode_jwt_claims_malformed_raises():
    """Verify that decode jwt claims malformed raises."""
    with pytest.raises(AppRegistrationValidationError):
        decode_jwt_claims("not-a-jwt")


# ---------------------------------------------------------------------------
# validate_app_registration -- normal, negative, permission-denial cases
# ---------------------------------------------------------------------------

# Verify that validate app registration success.
def test_validate_app_registration_success():
    """Verify that validate app registration success."""
    result = validate_app_registration(CONNECTION, FakeHttpClient())
    assert result.success is True
    assert result.signed_in_as == "user@example.com"
    assert result.app_id == "app-id-123"


# Verify that validate app registration missing config raises.
def test_validate_app_registration_missing_config_raises():
    """Verify that validate app registration missing config raises."""
    with pytest.raises(AppRegistrationValidationError):
        validate_app_registration({}, FakeHttpClient())


# Verify that validate app registration device code failure is honest partial result.
def test_validate_app_registration_device_code_failure_is_honest_partial_result():
    """Verify that validate app registration device code failure is honest partial result."""
    client = FakeHttpClient(raise_on={"device_code": "network unreachable"})
    result = validate_app_registration(CONNECTION, client)
    assert result.success is False
    assert "device code request failed" in result.detail


# Verify that validate app registration token failure is honest partial result.
def test_validate_app_registration_token_failure_is_honest_partial_result():
    """Verify that validate app registration token failure is honest partial result."""
    client = FakeHttpClient(raise_on={"token": "authorization_declined"})
    result = validate_app_registration(CONNECTION, client)
    assert result.success is False
    assert "token acquisition failed" in result.detail


# Verify that validate app registration permission denial reports failure not empty success.
def test_validate_app_registration_permission_denial_reports_failure_not_empty_success():
    # contextinfo call raises -- e.g. 403 Forbidden -- must not be reported as success.
    """Verify that validate app registration permission denial reports failure not empty success."""
    client = FakeHttpClient(raise_on={"context_info": "403 Forbidden"})
    result = validate_app_registration(CONNECTION, client)
    assert result.success is False
    assert "contextinfo call failed" in result.detail
    # still surfaces who authenticated, for honest partial reporting
    assert result.signed_in_as == "user@example.com"


# Verify that validate app registration missing digest is failure.
def test_validate_app_registration_missing_digest_is_failure():
    """Verify that validate app registration missing digest is failure."""
    client = FakeHttpClient(digest=None)
    result = validate_app_registration(CONNECTION, client)
    assert result.success is False
    assert "FormDigestValue" in result.detail


# Verify that validate app registration result has no project literals.
def test_validate_app_registration_result_has_no_project_literals():
    """Verify that validate app registration result has no project literals."""
    result = validate_app_registration(CONNECTION, FakeHttpClient())
    blob = str(result.to_dict()).lower()
    for literal in [__import__("base64").b64decode(x).decode() for x in ['YmNnb3Y=', 'amFnLWNzYg==', 'Y21hdA==', 'anVzdGlu', 'Y2Vpcw==', 'b3Jkcw==']]:
        assert literal not in blob


# ---------------------------------------------------------------------------
# make_device_code_connector -- config_setup.test_connection() compatibility
# ---------------------------------------------------------------------------

# Verify that make device code connector returns bool true on success.
def test_make_device_code_connector_returns_bool_true_on_success():
    """Verify that make device code connector returns bool true on success."""
    connector = make_device_code_connector(FakeHttpClient())
    assert connector(CONNECTION) is True


# Verify that make device code connector returns bool false on failure.
def test_make_device_code_connector_returns_bool_false_on_failure():
    """Verify that make device code connector returns bool false on failure."""
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

    # Store the site URL whose context-info request should be denied.
    def __init__(self, *, denied_site_url: str):
        """Store the site URL whose context-info request should be denied."""
        self._denied_site_url = denied_site_url

    # Return a deterministic device-code response without contacting an identity service.
    def request_device_code(self, url, body):
        """Return a deterministic device-code response without contacting an identity service."""
        return {"device_code": "dc-abc", "interval": 0, "expires_in": 60}

    # Return a fabricated token response or raise the configured acquisition failure.
    def poll_for_token(self, url, body):
        """Return a fabricated token response or raise the configured acquisition failure."""
        return {"access_token": _fake_jwt({"upn": "user@example.com", "appid": "app-id-123"})}

    # Deny the configured site and return a digest for other context-info requests.
    def get_context_info(self, url, headers):
        """Deny the configured site and return a digest for other context-info requests."""
        if url.startswith(self._denied_site_url):
            raise RuntimeError("403 Access Denied")
        return {"FormDigestValue": "digest-value"}


# Verify that boundary proven when authorized succeeds and unauthorized is denied.
def test_boundary_proven_when_authorized_succeeds_and_unauthorized_is_denied():
    """Verify that boundary proven when authorized succeeds and unauthorized is denied."""
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


# Verify that boundary result serializes both sub results.
def test_boundary_result_serializes_both_sub_results():
    """Verify that boundary result serializes both sub results."""
    client = SiteAwareHttpClient(denied_site_url=UNAUTHORIZED_CONNECTION["SiteUrl"])
    result = validate_permission_boundary(AUTHORIZED_CONNECTION, UNAUTHORIZED_CONNECTION, client)
    as_dict = result.to_dict()
    assert as_dict["boundary_proven"] is True
    assert as_dict["authorized_result"]["success"] is True
    assert as_dict["unauthorized_result"]["success"] is False
