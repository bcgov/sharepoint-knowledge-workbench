# Acceptance Criteria: workbench-validate-sharepoint-connection

- Skill slug: `workbench-validate-sharepoint-connection`.
- Target plugin: `sharepoint-workbench-setup`.
- Purpose: Confirms the app registration and connection work against a live tenant. Validates config and profile correctness (always PASS or FAIL), validates the Entra ID app registration (device-code auth plus an _api/contextinfo REST smoke test and a permission-boundary proof), and provides network-reachability and interactive sign-in scripts. Use before another plugin or a live tenant operation relies on the workbench environment.

## Constraints honored

- Zero tenant I/O by default. `validate_app_registration`, `check_network_connectivity` and `test_connection` need an injected `http_client` or `connector`; this skill ships none.
- Never report a false success. Failures return `success=False` with a `detail` message.
- Config and profile validation returns only `PASS` or `FAIL`, never `WARN`.
- The PowerShell tools perform live tenant I/O and prompt for sign-in. The user runs them; no skill invokes them automatically.
- Run from this skill's root with `scripts/` on `sys.path`. Python is standard library only; the `.ps1` tools need `pwsh` and the `PnP.PowerShell` module.

## Verification passes

- Confirm each layer's result: `ValidationReport.status`, `AppRegistrationValidationResult.success`, `PermissionBoundaryResult.boundary_proven` (true only when the authorized site succeeds and the unauthorized site is denied), and `NetworkConnectivityResult.success`. An unauthorized site unexpectedly succeeding is a security finding, not a pass.
- Focused plugin tests for this skill pass.
