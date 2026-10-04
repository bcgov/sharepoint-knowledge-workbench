# Live network and sign-in tools

## Contents

- [Rule for running these](#rule-for-running-these)
- [network_connectivity.py](#network_connectivitypy)
- [test-network-connectivity.ps1](#test-network-connectivityps1)
- [test-spo-connection.ps1](#test-spo-connectionps1)
- [test-pnp-effective-capability-probe.ps1](#test-pnp-effective-capability-probeps1)
- [Config and prerequisites](#config-and-prerequisites)

## Rule for running these

These are the only places in `sharepoint-workbench-setup` that perform live tenant I/O and prompt for
interactive sign-in by default. Run them yourself; no skill invokes them automatically.

## network_connectivity.py

Pure, tested TCP-reachability checklist logic (Entra ID, SharePoint Online, Microsoft Graph,
CRL/OCSP endpoints; no project-specific endpoint). Ships no transport. It requires an
injected `connector(host, port) -> bool`, the same zero-tenant-I/O contract as
`app_registration_validation.py`.

```python
from network_connectivity import check_network_connectivity
result = check_network_connectivity(connection, my_connector)
# NetworkConnectivityResult(success, required_failures, optional_failures, checked)
```

## test-network-connectivity.ps1

The full live tool. Phase 1 runs the network-reachability checklist with a cross-platform TCP
connect (works under macOS and Linux `pwsh`, not only Windows' `Test-NetConnection`). Phase 2
runs a real `Connect-PnPOnline` interactive or device-code sign-in against the site in
`config.psd1` and confirms `Get-PnPWeb` and `CurrentUser` resolve.

```bash
pwsh -File scripts/test-network-connectivity.ps1                  # network + browser sign-in
pwsh -File scripts/test-network-connectivity.ps1 -SkipAuthTest     # network reachability only
pwsh -File scripts/test-network-connectivity.ps1 -DeviceLogin      # device-code sign-in
```

## test-spo-connection.ps1

A minimal connection-only test with no network pre-flight: `Connect-PnPOnline -Interactive`
plus `Get-PnPWeb`. Subsumed by the connectivity script's Phase 2, and kept as a quicker
standalone check.

```bash
pwsh -File scripts/test-spo-connection.ps1
```

## test-pnp-effective-capability-probe.ps1

Observes which operations a given app registration and auth mode can actually perform on
explicit target sites. It does not infer a Write vs Manage tier: that assumption was disproven
against production. `-Sites` is required, with no default. `-AuthMode Interactive` (default)
reflects the intersection of the app's consented scope and the signed-in user's rights.
`-AuthMode Certificate` (needs `-CertThumbprint`) reflects the app grant alone; the two modes
must be tested separately. `-ClientId` and `-TenantId` override `config.psd1`. Read the
script's header before running it. See `effective-permissions-matrix.md` for how to interpret
results.

This replaces the older `test-grant-tier-probe.ps1`, whose tier-inference logic was removed.

## Config and prerequisites

Each PowerShell script reads `SiteUrl`, `ClientId` and `TenantId` from `-ConfigPath` (defaults
to the repository root `config.psd1`), supporting both the nested `Connection = @{...}` schema
and a flat top-level schema. They need `pwsh` and the `PnP.PowerShell` module on PATH; see
`DEPENDENCIES.md`.

Provenance (source repository only): `app_registration_validation.py` supplies the device-code
REST smoke test; `network_connectivity.py` and `test-network-connectivity.ps1` were adapted from
a real project's network script with all project-specific endpoints removed.
