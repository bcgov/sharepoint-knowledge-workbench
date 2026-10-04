# App-registration validation

## Contents

- [What it confirms](#what-it-confirms)
- [Zero tenant I/O by default](#zero-tenant-io-by-default)
- [Interface](#interface)
- [Permission boundary](#permission-boundary)

## What it confirms

Confirms an Entra ID app registration (delegated, device-code auth) is correctly configured
for a target SharePoint site. It acquires a bearer token via the device-code flow, decodes
the token's claims to report who and what actually authenticated, then calls
`_api/contextinfo` against the site to confirm the token grants usable SharePoint REST
access. Failures (device-code request failure, token acquisition failure, permission denial
on `_api/contextinfo`, missing digest) are reported as an honest partial result
(`success=False` with a `detail` message), never a false success.

## Zero tenant I/O by default

The module ships no live HTTP transport. `validate_app_registration(connection, http_client)`
requires an injected `http_client` exposing `request_device_code`, `poll_for_token` and
`get_context_info`. `make_device_code_connector(http_client)` builds a
`connector(connection) -> bool` compatible with `config_setup.test_connection(connection,
connector=...)`'s opt-in-only contract. Wiring it in never becomes a default;
`test_connection()` still raises `NotImplementedError` when called without a connector.

## Interface

```python
from app_registration_validation import (
    validate_app_registration,
    make_device_code_connector,
    validate_permission_boundary,
)

result = validate_app_registration(connection, http_client)
# AppRegistrationValidationResult(success, signed_in_as, app_id, detail)

from config_setup import test_connection
connector = make_device_code_connector(http_client)
test_connection(connection, connector=connector)
```

## Permission boundary

```python
boundary = validate_permission_boundary(authorized_connection, unauthorized_connection, http_client)
# PermissionBoundaryResult(boundary_proven, authorized_result, unauthorized_result, detail)
```

`validate_permission_boundary` runs `validate_app_registration` against two connections that
share `ClientId` and `TenantId` but differ in `SiteUrl`: one the signed-in user can reach, one
they cannot. `boundary_proven` is `True` only when the authorized site succeeds and the
unauthorized site is denied. An unauthorized site unexpectedly succeeding is reported as a
security finding in `detail`, not a pass. No PowerShell tool here proves the boundary; they
show only that a given site connects. The full method is in
`delegated-permission-boundary-test.md`.
