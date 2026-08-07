"""
app_registration_validation.py
================================

Phase 9 extraction (source: CMAT repository `sp-validating-app-registration`
skill, commit `78d6bb91a6c3c01208208a8c2a06f241fef9ce9f` -- see
`docs/reports/phase-9-reusable-sharepoint-plugin-extraction/provenance.md`).

Generic Entra ID app-registration validation for SharePoint Online, adapted
from CMAT's proven device-code REST auth smoke test
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

No BC Government tenant URLs, GUIDs, app-registration values, or CMAT/ORDS/
JUSTIN/CEIS literals appear anywhere in this module -- see the genericity
contract in `docs/superpowers/specs/
phase-9-reusable-sharepoint-plugin-extraction-spec.md` Section 9.
"""
from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from typing import Callable, Optional


class AppRegistrationValidationError(Exception):
    """Raised when app-registration validation cannot proceed (e.g. malformed
    connection input) -- distinct from a validation *failure*, which is
    reported as `AppRegistrationValidationResult(success=False, ...)`."""


@dataclass
class AppRegistrationValidationResult:
    success: bool
    signed_in_as: Optional[str] = None
    app_id: Optional[str] = None
    detail: str = ""

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "signed_in_as": self.signed_in_as,
            "app_id": self.app_id,
            "detail": self.detail,
        }


def decode_jwt_claims(access_token: str) -> dict:
    """Decode a JWT's payload segment without verifying its signature --
    diagnostics only, mirrors CMAT's own "no signature validation -
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


def _require_fields(connection: dict, fields: tuple) -> None:
    missing = [f for f in fields if not connection.get(f)]
    if missing:
        raise AppRegistrationValidationError(f"connection is missing required field(s): {', '.join(missing)}")


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
    dc_request = build_device_code_request(connection)
    try:
        device_code_response = http_client.request_device_code(dc_request["url"], dc_request["body"])
    except Exception as exc:  # noqa: BLE001 -- honest partial result, not a crash
        return AppRegistrationValidationResult(success=False, detail=f"device code request failed: {exc}")

    device_code = device_code_response.get("device_code")
    if not device_code:
        return AppRegistrationValidationResult(success=False, detail="device code response missing device_code")

    token_request = build_token_poll_request(connection, device_code)
    try:
        token_response = http_client.poll_for_token(token_request["url"], token_request["body"])
    except Exception as exc:  # noqa: BLE001
        return AppRegistrationValidationResult(success=False, detail=f"token acquisition failed: {exc}")

    access_token = token_response.get("access_token")
    if not access_token:
        return AppRegistrationValidationResult(success=False, detail="token response missing access_token")

    try:
        claims = decode_jwt_claims(access_token)
    except AppRegistrationValidationError as exc:
        claims = {}
        claim_error = str(exc)
    else:
        claim_error = None

    signed_in_as = claims.get("upn") or claims.get("name")
    app_id = claims.get("appid")

    context_request = build_context_info_request(connection, access_token)
    try:
        context_response = http_client.get_context_info(context_request["url"], context_request["headers"])
    except Exception as exc:  # noqa: BLE001
        return AppRegistrationValidationResult(
            success=False, signed_in_as=signed_in_as, app_id=app_id,
            detail=f"contextinfo call failed (permission denied or auth invalid): {exc}",
        )

    digest = context_response.get("FormDigestValue")
    if not digest:
        return AppRegistrationValidationResult(
            success=False, signed_in_as=signed_in_as, app_id=app_id,
            detail="contextinfo response missing FormDigestValue -- auth did not grant usable REST access",
        )

    detail = "REST auth confirmed via _api/contextinfo digest"
    if claim_error:
        detail += f" (token claims could not be decoded: {claim_error})"

    return AppRegistrationValidationResult(success=True, signed_in_as=signed_in_as, app_id=app_id, detail=detail)


def make_device_code_connector(http_client) -> "Callable[[dict], bool]":
    """Build a `connector(connection) -> bool` callable compatible with
    `config_setup.test_connection(connection, connector=...)`'s existing
    contract. `http_client` must be supplied explicitly by the caller -- this
    factory does not ship a default live transport, preserving `test_
    connection`'s "no autonomous production tenant writes/connections"
    property; the connector it returns is still opt-in only."""

    def connector(connection: dict) -> bool:
        result = validate_app_registration(connection, http_client)
        return result.success

    return connector
