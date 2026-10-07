"""Purpose:
    Build device-code OAuth requests and validate SharePoint access through an injected transport.

Key Input Dependencies:
    - Connection mapping containing SiteUrl, TenantId, and ClientId
    - Caller-injected HTTP client implementing the device-code, token, and context-info calls.

app_registration_validation.py
================================

Generic Entra ID app-registration validation for SharePoint Online, providing
from proven device-code REST auth smoke test
(`scripts/diagnostics/test-spo-auth.ps1`): acquire a bearer token via the
OAuth2 device-code flow, decode its claims to confirm who/what authenticated,
then call `_api/contextinfo` against the target site to confirm the token is
actually usable for SharePoint REST operations.

This module provides two things:

1. Pure, network-free helpers (`decode_jwt_claims`, `build_device_code_
   request`, `build_token_poll_request`, `build_context_info_request`) that
   are fully unit-testable without any live tenant.
2. `make_device_code_connector(...)`, a factory that returns a `connector`
   callable compatible with `config_setup.test_connection(connection,
   connector=...)`'s existing contract -- i.e. `connector(connection) ->
   bool`. The factory takes an injected `http_client` (an object exposing
   `.post(url, data, headers) -> Response`-style calls); this module ships
   no live HTTP transport itself, so a caller must inject one to perform a
   real validation. This mirrors `config_setup.test_connection`'s own "zero
   tenant I/O unless the caller explicitly supplies a connector" contract --
   `setup-sharepoint-connection`'s `-TestConnection` path stays opt-in only,
   never wired as a default.

No proprietary tenant URLs, client secrets, or private environment
identifiers appear in this module.

Function Index:
    - AppRegistrationValidationError
    - AppRegistrationValidationResult
    - AppRegistrationValidationResult.to_dict
    - decode_jwt_claims
    - build_device_code_request
    - build_token_poll_request
    - build_context_info_request
    - _require_fields
    - _request_device_code
    - _request_access_token
    - _context_info_result
    - validate_app_registration
    - PermissionBoundaryResult
    - PermissionBoundaryResult.to_dict
    - _permission_boundary_detail
    - validate_permission_boundary
    - make_device_code_connector
    - make_device_code_connector.connector
"""
from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from typing import Callable, Optional, Tuple


class AppRegistrationValidationError(Exception):
    """Raised when app-registration validation cannot proceed (e.g. malformed
    connection input) -- distinct from a validation *failure*, which is
    reported as `AppRegistrationValidationResult(success=False, ...)`."""


# Carry validation success, identity, application ID, and diagnostic details.
@dataclass
class AppRegistrationValidationResult:
    """Carry validation success, identity, application ID, and diagnostic details."""
    success: bool
    signed_in_as: Optional[str] = None
    app_id: Optional[str] = None
    detail: str = ""

    # Serialize this validation result and its public fields as a plain dictionary.
    def to_dict(self) -> dict:
        """Serialize this validation result and its public fields as a plain dictionary."""
        return {
            "success": self.success,
            "signed_in_as": self.signed_in_as,
            "app_id": self.app_id,
            "detail": self.detail,
        }


def decode_jwt_claims(access_token: str) -> dict:
    """Decode a JWT's payload segment without verifying its signature --
    diagnostics only, mirrors standard "no signature validation -
    diagnostics only" comment. Raises `AppRegistrationValidationError` if the
    token is not a well-formed JWT (three dot-separated segments, base64url
    payload)."""
    parts = access_token.split(".")
    if len(parts) != 3:
        raise AppRegistrationValidationError("access_token is not a well-formed JWT (expected 3 segments)")

    payload_segment = parts[1]
    padding = "=" * ((4 - len(payload_segment) % 4) % 4)
    try:
        decoded = base64.urlsafe_b64decode(payload_segment + padding)
        return json.loads(decoded)
    except (ValueError, json.JSONDecodeError) as exc:
        raise AppRegistrationValidationError(f"could not decode JWT payload: {exc}") from exc


def build_device_code_request(connection: dict) -> dict:
    """Build the device-code request (URL + form body) for a given
    connection dict (requires `SiteUrl`, `TenantId`, `ClientId`). Pure -- no
    network I/O."""
    _require_fields(connection, ("SiteUrl", "TenantId", "ClientId"))
    tenant_id = connection["TenantId"]
    client_id = connection["ClientId"]
    scope = f"{connection['SiteUrl']}/.default"
    return {
        "url": f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/devicecode",
        "body": {"client_id": client_id, "scope": scope},
    }


def build_token_poll_request(connection: dict, device_code: str) -> dict:
    """Build the token-polling request for a given connection + device code.
    Pure -- no network I/O."""
    _require_fields(connection, ("TenantId", "ClientId"))
    tenant_id = connection["TenantId"]
    client_id = connection["ClientId"]
    return {
        "url": f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token",
        "body": {
            "client_id": client_id,
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            "device_code": device_code,
        },
    }


def build_context_info_request(connection: dict, access_token: str) -> dict:
    """Build the `_api/contextinfo` REST request that confirms the token is
    usable for SharePoint REST operations. Pure -- no network I/O."""
    _require_fields(connection, ("SiteUrl",))
    return {
        "url": f"{connection['SiteUrl']}/_api/contextinfo",
        "headers": {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json;odata=verbose",
        },
    }


# Raise a validation error when any required connection field is absent or empty.
def _require_fields(connection: dict, fields: tuple) -> None:
    """Raise a validation error when any required connection field is absent or empty."""
    missing = [f for f in fields if not connection.get(f)]
    if missing:
        raise AppRegistrationValidationError(f"connection is missing required field(s): {', '.join(missing)}")


def _request_device_code(
    connection: dict, http_client: object
) -> Tuple[Optional[str], Optional[AppRegistrationValidationResult]]:
    """Request a device code or return an honest failure result."""
    request = build_device_code_request(connection)
    try:
        response = http_client.request_device_code(request["url"], request["body"])
    except Exception as exc:  # noqa: BLE001 -- transport errors are partial results
        return None, AppRegistrationValidationResult(success=False, detail=f"device code request failed: {exc}")

    device_code = response.get("device_code")
    if not device_code:
        return None, AppRegistrationValidationResult(
            success=False, detail="device code response missing device_code"
        )
    return device_code, None


def _request_access_token(
    connection: dict, device_code: str, http_client: object
) -> Tuple[Optional[str], Optional[AppRegistrationValidationResult]]:
    """Poll for an access token or return an honest failure result."""
    request = build_token_poll_request(connection, device_code)
    try:
        response = http_client.poll_for_token(request["url"], request["body"])
    except Exception as exc:  # noqa: BLE001 -- transport errors are partial results
        return None, AppRegistrationValidationResult(success=False, detail=f"token acquisition failed: {exc}")

    access_token = response.get("access_token")
    if not access_token:
        return None, AppRegistrationValidationResult(
            success=False, detail="token response missing access_token"
        )
    return access_token, None


def _context_info_result(
    connection: dict,
    access_token: str,
    signed_in_as: Optional[str],
    app_id: Optional[str],
    http_client: object,
) -> AppRegistrationValidationResult:
    """Verify the token with SharePoint REST and preserve partial identity details."""
    request = build_context_info_request(connection, access_token)
    try:
        response = http_client.get_context_info(request["url"], request["headers"])
    except Exception as exc:  # noqa: BLE001 -- transport errors are partial results
        return AppRegistrationValidationResult(
            success=False,
            signed_in_as=signed_in_as,
            app_id=app_id,
            detail=f"contextinfo call failed (permission denied or auth invalid): {exc}",
        )

    if not response.get("FormDigestValue"):
        return AppRegistrationValidationResult(
            success=False,
            signed_in_as=signed_in_as,
            app_id=app_id,
            detail="contextinfo response missing FormDigestValue -- auth did not grant usable REST access",
        )
    return AppRegistrationValidationResult(
        success=True,
        signed_in_as=signed_in_as,
        app_id=app_id,
        detail="REST auth confirmed via _api/contextinfo digest",
    )


def validate_app_registration(connection: dict, http_client) -> AppRegistrationValidationResult:
    """Run the full device-code auth + `_api/contextinfo` validation against
    `connection`, using the injected `http_client`. Zero tenant I/O unless a
    real `http_client` is supplied -- this function performs no network
    calls of its own beyond what `http_client` does. Returns an honest
    partial result (`success=False`) rather than raising, on the network/API
    failure paths -- only malformed `connection` input raises
    `AppRegistrationValidationError`.

    `http_client` must expose:
      - `request_device_code(url, body) -> dict` (device-code response)
      - `poll_for_token(url, body) -> dict` (token response, or raises on
        `authorization_declined`/`expired_token`/timeout)
      - `get_context_info(url, headers) -> dict` (must contain a truthy
        `FormDigestValue` on success)
    """
    device_code, failure = _request_device_code(connection, http_client)
    if failure:
        return failure

    access_token, failure = _request_access_token(connection, device_code, http_client)
    if failure:
        return failure

    try:
        claims = decode_jwt_claims(access_token)
    except AppRegistrationValidationError as exc:
        claims = {}
        claim_error = str(exc)
    else:
        claim_error = None

    signed_in_as = claims.get("upn") or claims.get("name")
    app_id = claims.get("appid")
    if claim_error:
        result = _context_info_result(connection, access_token, signed_in_as, app_id, http_client)
        if result.success:
            result.detail += f" (token claims could not be decoded: {claim_error})"
        return result
    return _context_info_result(connection, access_token, signed_in_as, app_id, http_client)


@dataclass
class PermissionBoundaryResult:
    """Empirical proof (or disproof) that a delegated app registration's
    effective permissions equal the intersection of its own API permissions
    and the signed-in user's actual SharePoint permissions -- i.e. the
    registration is not a backdoor to sites the user cannot already reach.
    """

    boundary_proven: bool
    authorized_result: AppRegistrationValidationResult
    unauthorized_result: AppRegistrationValidationResult
    detail: str = ""

    # Serialize this validation result and its public fields as a plain dictionary.
    def to_dict(self) -> dict:
        """Serialize this validation result and its public fields as a plain dictionary."""
        return {
            "boundary_proven": self.boundary_proven,
            "authorized_result": self.authorized_result.to_dict(),
            "unauthorized_result": self.unauthorized_result.to_dict(),
            "detail": self.detail,
        }


def _permission_boundary_detail(
    authorized_result: AppRegistrationValidationResult,
    unauthorized_result: AppRegistrationValidationResult,
) -> Tuple[bool, str]:
    """Describe whether the two observed site outcomes prove the permission boundary."""
    if authorized_result.success and not unauthorized_result.success:
        return True, "boundary proven: authorized site succeeded, unauthorized site was denied"
    if not authorized_result.success and not unauthorized_result.success:
        detail = (
            "boundary not proven: the authorized site also failed "
            f"({authorized_result.detail!r}) -- registration or site permission is misconfigured, "
            "not a boundary result"
        )
    elif authorized_result.success and unauthorized_result.success:
        detail = (
            "boundary not proven: the unauthorized site unexpectedly succeeded -- "
            "this registration grants access beyond the signed-in user's actual permissions, "
            "a real security finding, not a test failure"
        )
    else:
        detail = (
            "boundary not proven: the authorized site failed while the unauthorized site "
            f"succeeded ({unauthorized_result.detail!r}) -- results are inverted from expectation"
        )
    return False, detail


def validate_permission_boundary(
    authorized_connection: dict, unauthorized_connection: dict, http_client
) -> PermissionBoundaryResult:
    """Empirically prove the security boundary `Effective permissions = App
    permissions ∩ User permissions` for a delegated app registration, by
    running `validate_app_registration` against two sites with the same
    `ClientId`/`TenantId`: one the signed-in user has access to
    (`authorized_connection`, expected to succeed) and one the user does not
    (`unauthorized_connection`, expected to fail with Access Denied).

    Zero tenant I/O beyond what the injected `http_client` performs -- same
    contract as `validate_app_registration`.

    A proven boundary requires BOTH the authorized site to succeed AND the
    unauthorized site to fail -- either sub-result on its own is
    insufficient and is reported with a distinct, honest `detail` message
    naming which side of the boundary did not behave as expected. An
    unauthorized site unexpectedly succeeding is a security finding (the
    registration grants broader access than intended), never conflated with
    a misconfigured authorized site.
    """
    authorized_result = validate_app_registration(authorized_connection, http_client)
    unauthorized_result = validate_app_registration(unauthorized_connection, http_client)
    boundary_proven, detail = _permission_boundary_detail(authorized_result, unauthorized_result)
    return PermissionBoundaryResult(
        boundary_proven=boundary_proven,
        authorized_result=authorized_result,
        unauthorized_result=unauthorized_result,
        detail=detail,
    )


def make_device_code_connector(http_client) -> "Callable[[dict], bool]":
    """Build a `connector(connection) -> bool` callable compatible with
    `config_setup.test_connection(connection, connector=...)`'s existing
    contract. `http_client` must be supplied explicitly by the caller -- this
    factory does not ship a default live transport, preserving `test_
    connection`'s "no autonomous production tenant writes/connections"
    property; the connector it returns is still opt-in only."""

    # Return validation success through config_setup connector(connection) compatibility.
    def connector(connection: dict) -> bool:
        """Return validation success through config_setup connector(connection) compatibility."""
        result = validate_app_registration(connection, http_client)
        return result.success

    return connector
