"""Purpose:
    Build endpoint checks and report reachability using an explicitly injected connector.

Key Input Dependencies:
    - Connection mapping with SiteUrl
    - Caller-injected connector(host, port) function; no built-in network transport.

network_connectivity.py
=========================

Generic TCP-reachability pre-flight check for the Microsoft endpoints an
interactive (delegated) SharePoint Online connection needs: Entra ID token
acquisition, SharePoint Online itself, Microsoft Graph, and certificate
revocation checking (CRL/OCSP). Validates standard Microsoft endpoints;
this module is tenant-agnostic beyond the SharePoint site's own hostname, derived from
`connection["SiteUrl"]` (the same `config.psd1` shape `config_setup.py`
already builds at this repository's root).

Ships no live network transport itself -- a caller must inject a
`connector(host, port) -> bool` callable (e.g. wrapping
`socket.create_connection`), mirroring `config_setup.test_connection`'s and
`app_registration_validation`'s "zero tenant I/O unless the caller
explicitly supplies a connector" contract. A connector that raises is
treated the same as one that returns `False` -- an honest unreachable
result, not a crash.

Purpose split from `validate-sharepoint-connection`'s existing
`workflow_validation.py`: that module validates already-parsed
connection/workflow/publication dicts and is deliberately pure (no I/O
at all). This module answers a different, complementary question --
"can this host even reach Microsoft's endpoints" -- and is opt-in, gated
behind an injected connector, the same way `validate-app-registration`'s
live-tenant check is opt-in. Both live in the `validate-workbench-
environment` skill as companion capabilities, not merged into the same
always-pure function.

Function Index:
    - NetworkConnectivityError
    - build_endpoint_checklist
    - NetworkConnectivityResult
    - NetworkConnectivityResult.to_dict
    - check_network_connectivity
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable
from urllib.parse import urlparse


class NetworkConnectivityError(Exception):
    """Raised when the checklist cannot be built (e.g. malformed
    connection input) -- distinct from a reachability *failure*, which is
    reported as `NetworkConnectivityResult(success=False, ...)`."""


def build_endpoint_checklist(connection: dict) -> list:
    """Build the list of (host, port, group, required) endpoint checks for
    `connection`. Pure -- no network I/O. Raises `ValueError` if
    `connection` has no usable `SiteUrl`."""
    site_url = connection.get("SiteUrl")
    if not site_url:
        raise ValueError("connection is missing required field: SiteUrl")

    tenant_host = urlparse(site_url).hostname
    if not tenant_host:
        raise ValueError(f"connection SiteUrl is not a parseable URL: {site_url!r}")

    return [
        # Entra ID token acquisition
        {"group": "Entra ID token acquisition", "host": "login.microsoftonline.com", "port": 443, "required": True},
        {"group": "Entra ID token acquisition", "host": "login.microsoftonline.com", "port": 80, "required": True},
        {"group": "Entra ID token acquisition", "host": "login.windows.net", "port": 443, "required": True},
        {"group": "Entra ID token acquisition", "host": "device.login.microsoftonline.com", "port": 443, "required": True},
        {"group": "Entra ID token acquisition", "host": "autologon.microsoftazuread-sso.com", "port": 443, "required": True},
        {"group": "Entra ID token acquisition", "host": "enterpriseregistration.windows.net", "port": 443, "required": True},
        # SharePoint Online
        {"group": "SharePoint Online", "host": tenant_host, "port": 443, "required": True},
        {"group": "SharePoint Online", "host": tenant_host, "port": 80, "required": True},
        {"group": "SharePoint Online", "host": "spoprod-a.akamaihd.net", "port": 443, "required": True},
        # Microsoft Graph
        {"group": "Microsoft Graph", "host": "graph.microsoft.com", "port": 443, "required": True},
        {"group": "Microsoft Graph", "host": "graph.microsoft.com", "port": 80, "required": True},
        # CRL/OCSP revocation checking -- informational only; observed to
        # soft-fail (auth still succeeds) rather than hard-block when a
        # responder is unreachable.
        {"group": "CRL/OCSP revocation checking (informational)", "host": "crl.microsoft.com", "port": 80, "required": False},
        {"group": "CRL/OCSP revocation checking (informational)", "host": "mscrl.microsoft.com", "port": 80, "required": False},
        {"group": "CRL/OCSP revocation checking (informational)", "host": "ocsp.msocsp.com", "port": 80, "required": False},
        {"group": "CRL/OCSP revocation checking (informational)", "host": "oneocsp.microsoft.com", "port": 80, "required": False},
        {"group": "CRL/OCSP revocation checking (informational)", "host": "crl3.digicert.com", "port": 80, "required": False},
        {"group": "CRL/OCSP revocation checking (informational)", "host": "ocsp.digicert.com", "port": 80, "required": False},
        {"group": "CRL/OCSP revocation checking (informational)", "host": "crl.globalsign.com", "port": 80, "required": False},
        {"group": "CRL/OCSP revocation checking (informational)", "host": "crl.identrust.com", "port": 80, "required": False},
    ]


# Summarize endpoint-check counts, required failures, optional failures, and overall reachability.
@dataclass
class NetworkConnectivityResult:
    """Summarize endpoint-check counts, required failures, optional failures, and overall reachability."""
    success: bool
    required_failures: list = field(default_factory=list)
    optional_failures: list = field(default_factory=list)
    checked: int = 0

    # Serialize this validation result and its public fields as a plain dictionary.
    def to_dict(self) -> dict:
        """Serialize this validation result and its public fields as a plain dictionary."""
        return {
            "success": self.success,
            "required_failures": self.required_failures,
            "optional_failures": self.optional_failures,
            "checked": self.checked,
        }


def check_network_connectivity(
    connection: dict, connector: "Callable[[str, int], bool]"
) -> NetworkConnectivityResult:
    """Run `build_endpoint_checklist(connection)` through `connector(host,
    port) -> bool`, reporting an honest pass/fail per endpoint. Zero
    network I/O beyond what `connector` performs -- this function ships no
    transport of its own. A `connector` exception is treated as an honest
    unreachable result for that endpoint, not a crash. `success` is `True`
    iff every *required* endpoint is reachable; optional (informational)
    failures never affect `success`, matching this repository's other
    validators' "always an honest PASS/FAIL, no silent WARN masking a real
    failure" convention."""
    checklist = build_endpoint_checklist(connection)

    required_failures = []
    optional_failures = []

    for entry in checklist:
        try:
            reachable = connector(entry["host"], entry["port"])
        except Exception as exc:  # noqa: BLE001 -- honest unreachable result, not a crash
            reachable = False
            failure = {"host": entry["host"], "port": entry["port"], "group": entry["group"], "detail": str(exc)}
        else:
            failure = {"host": entry["host"], "port": entry["port"], "group": entry["group"], "detail": "unreachable"}

        if reachable:
            continue

        if entry["required"]:
            required_failures.append(failure)
        else:
            optional_failures.append(failure)

    return NetworkConnectivityResult(
        success=not required_failures,
        required_failures=required_failures,
        optional_failures=optional_failures,
        checked=len(checklist),
    )
