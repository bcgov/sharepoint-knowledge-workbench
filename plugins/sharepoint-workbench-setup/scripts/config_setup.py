"""Purpose:
    Validate connection answers and write the root SharePoint configuration without implicit tenant access.

Key Input Dependencies:
    - Caller-provided connection, authentication, and defaults mappings
    - assets/config.psd1.example as the configuration schema
    - psd1_writer.render_document

config_setup.py
=================

Phase 6 Task 0.17 -- the `setup-sharepoint-connection` skill's logic.
Creates the root, git-ignored `config.psd1` from this plugin's canonical
`assets/config.psd1.example` (Layer 1 schema, design spec Section 1),
reusing `document_workflow.py`'s `.psd1` text renderer.

**Corrected behavior (design spec Section 8, 2026-08-02 external
review):** generating the config file is the default action and never
connects to anything. A separate, explicit `test_connection()` call
performs a read-only validation only after opt-in -- and even then,
this module deliberately does not embed a live SharePoint SDK/PnP
connector itself (that would be real tenant I/O shipped inside a
config-generation module). `test_connection()` requires an injected
`connector` callable; without one it raises `NotImplementedError` with
a clear message, rather than silently no-op'ing or faking success. A
future, separately-authorized version may wire in a real PnP-backed
connector as the default; this version's contract is: **zero tenant
I/O unless the caller explicitly supplies a connector.**

Function Index:
    - ConfigSetupError
    - ConfigIssue
    - validate_connection_answers
    - _to_snake_case
    - build_config_psd1
    - write_config
    - test_connection
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

from psd1_writer import render_document

MANDATORY_CONNECTION_KEYS = ("SiteUrl", "TenantId", "ClientId", "AuthenticationMode")

# Auth modes that require Authentication.* fields, and which ones.
_CONDITIONAL_AUTH_FIELDS = {
    "Certificate": ("CertificateThumbprint", "TenantAdminUrl"),
}


class ConfigSetupError(Exception):
    """Raised for any validation failure while building or writing
    `config.psd1`."""


# Represent one connection-answer validation issue with a stable code and explanation.
@dataclass
class ConfigIssue:
    """Represent one connection-answer validation issue with a stable code and explanation."""
    code: str
    message: str


VALID_AUTHENTICATION_MODES = ("Interactive", "Certificate", "DeviceCode")


def validate_connection_answers(connection: dict, authentication: dict) -> list:
    """Validate `connection`/`authentication` answers against design
    spec Section 1's mandatory/conditional key rules. Returns a list of
    `ConfigIssue` (empty means valid)."""
    issues = []

    field_to_code = {
        "SiteUrl": "missing_site_url",
        "TenantId": "missing_tenant_id",
        "ClientId": "missing_client_id",
        "AuthenticationMode": "missing_authentication_mode",
    }
    for field in MANDATORY_CONNECTION_KEYS:
        if not connection.get(field):
            issues.append(ConfigIssue(field_to_code[field], f"Connection.{field} is required"))

    mode = connection.get("AuthenticationMode")
    if mode and mode not in VALID_AUTHENTICATION_MODES:
        issues.append(ConfigIssue(
            "invalid_authentication_mode",
            f"Connection.AuthenticationMode must be one of {VALID_AUTHENTICATION_MODES}, got {mode!r}"
        ))

    for required_field in _CONDITIONAL_AUTH_FIELDS.get(mode, ()):
        if not authentication.get(required_field):
            code = f"missing_{_to_snake_case(required_field)}"
            issues.append(ConfigIssue(
                code, f"Authentication.{required_field} is required when AuthenticationMode={mode!r}"
            ))

    return issues


# Convert a mixed-case field name to the snake_case used in validation issue codes.
def _to_snake_case(name: str) -> str:
    """Convert a mixed-case field name to the snake_case used in validation issue codes."""
    out = []
    for i, ch in enumerate(name):
        if ch.isupper() and i > 0:
            out.append("_")
        out.append(ch.lower())
    return "".join(out)


def build_config_psd1(connection: dict, authentication: dict, defaults: dict) -> str:
    """Render the Layer 1 root connection config to PowerShell hashtable
    (`.psd1`) text. Does not validate -- call `validate_connection_
    answers` first (`write_config` does this for you)."""
    payload = {
        "Connection": dict(connection),
        "Authentication": dict(authentication),
        "Defaults": dict(defaults),
    }
    return render_document(payload)


def write_config(
    root: "Path | str",
    connection: dict,
    authentication: dict,
    defaults: dict,
    *,
    overwrite: bool = False,
) -> Path:
    """Write `config.psd1` under `root`. Validates first (raises
    `ConfigSetupError` and writes nothing on failure). Refuses to
    silently overwrite an existing `config.psd1` unless
    `overwrite=True`. Never calls `test_connection` -- writing the file
    is the only action this function performs."""
    issues = validate_connection_answers(connection, authentication)
    if issues:
        raise ConfigSetupError(
            "invalid connection answers: " + "; ".join(f"{i.code}: {i.message}" for i in issues)
        )

    root = Path(root)
    output_path = root / "config.psd1"
    if output_path.exists() and not overwrite:
        raise ConfigSetupError(
            f"{output_path} already exists -- pass overwrite=True to replace it explicitly"
        )

    root.mkdir(parents=True, exist_ok=True)
    output_path.write_text(build_config_psd1(connection, authentication, defaults))
    return output_path


def test_connection(connection: dict, connector: "Optional[Callable[[dict], bool]]" = None) -> bool:
    """Perform a read-only connection validation -- explicit, opt-in
    only, never called as a side effect of `write_config`. Requires an
    injected `connector` callable (`connection -> bool`); without one,
    raises `NotImplementedError` rather than silently no-op'ing or
    faking a result, since this module ships no live SharePoint SDK/PnP
    connector itself."""
    if connector is None:
        raise NotImplementedError(
            "test_connection() requires a live SharePoint connector to be injected "
            "explicitly via connector=... -- this module does not ship one "
            "(zero tenant I/O by default, per design spec Section 8)"
        )
    return connector(connection)
