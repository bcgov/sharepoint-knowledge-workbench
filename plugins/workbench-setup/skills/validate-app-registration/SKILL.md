---
name: validate-app-registration
plugin: workbench-setup
description: Validates an Entra ID app registration against a live tenant via the OAuth2 device-code flow plus an `_api/contextinfo` REST smoke test -- confirms the registration can actually authenticate and obtain usable SharePoint REST access. Zero tenant I/O by default; requires an explicitly injected http_client, same connector-injection contract as config_setup.test_connection.
allowed-tools: Bash, Read
examples:
  - "python -c \"from app_registration_validation import validate_app_registration; print(validate_app_registration(connection, http_client).to_dict())\""
---

# Validate App Registration

## Trigger and Purpose

Use this skill to confirm an Entra ID app registration (delegated,
device-code auth) is correctly configured for a target SharePoint
site: it acquires a bearer token via the device-code flow, decodes the
token's claims to report who/what actually authenticated, then calls
`_api/contextinfo` against the site to confirm the token grants usable
SharePoint REST access. Failures (device-code request failure, token
acquisition failure, permission denial on `_api/contextinfo`, missing
digest) are reported as an honest partial result
(`success=False` with a `detail` message), never a false success.

**Zero tenant I/O by default.** This module ships no live HTTP
transport -- `validate_app_registration(connection, http_client)`
requires an injected `http_client` exposing `request_device_code`,
`poll_for_token`, and `get_context_info`. `make_device_code_connector
(http_client)` builds a `connector(connection) -> bool` callable
compatible with `config_setup.test_connection(connection,
connector=...)`'s existing opt-in-only contract (see
`setup-sharepoint-connection`'s SKILL.md) -- wiring this connector in
never becomes a default; `test_connection()` still raises
`NotImplementedError` when called without one.

## Public Interface

```python
from app_registration_validation import (
    validate_app_registration,
    make_device_code_connector,
)

result = validate_app_registration(connection, http_client)
# AppRegistrationValidationResult(success, signed_in_as, app_id, detail)

# Wiring into setup-sharepoint-connection's opt-in -TestConnection path:
from config_setup import test_connection
connector = make_device_code_connector(http_client)
test_connection(connection, connector=connector)
```

## Installation

```bash
pip install -e plugins/workbench-setup
```

## Dependencies

None beyond the Python standard library -- `http_client` is supplied
by the caller (e.g. a `requests`-based device-code client), not shipped
here.

## Provenance

Extracted from the CMAT repository's `sp-validating-app-registration`
skill (device-code REST auth smoke test,
`scripts/diagnostics/test-spo-auth.ps1`) -- see
`docs/reports/phase-9-reusable-sharepoint-plugin-extraction/provenance.md`
for the full source-to-destination record.
