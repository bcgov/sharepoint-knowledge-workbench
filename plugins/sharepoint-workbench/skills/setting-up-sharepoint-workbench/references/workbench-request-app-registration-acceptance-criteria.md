# Acceptance Criteria: workbench-request-app-registration

- Skill slug: `workbench-request-app-registration`.
- Target plugin: `sharepoint-workbench-setup`.
- Purpose: Guides the pre-work before any SharePoint use case that connects to a live tenant. Documents the two app-registration types (unattended App-Only/certificate for scheduled jobs, interactive/delegated for human-operator provisioning), generates a filled service-request document for your tenant or cloud administrator, and gives the setup sequence once granted (Entra API permissions, admin consent, Enterprise Application user assignment, and the separate PnP PowerShell site-level grant). Use before initializing config or running live checks. No network I/O; templating and reference data only.

## Constraints honored

- **Do not treat a PnP site-grant tier (`Write`/`Manage`) as a predictor of capability.** Production testing disproved the claim that `Write` blocks list/library creation. A successful `CreateList` does not prove a `Manage` grant.
- Report the stored grant role and the observed capabilities as two separate results, never conflated. Neither unresolved explanation (Microsoft's `write` definition vs. the user-permission intersection) is settled.
- Observe behavior with `scripts/test-pnp-effective-capability-probe.ps1`. It does real tenant I/O and the user runs it; never invoke it automatically.
- Pick the registration type deliberately. The wrong one causes confusing Access Denied errors.
- No network I/O here. Run from this skill's root with `scripts/` on `sys.path`; standard library only. The probe needs `pwsh` and `PnP.PowerShell`.

## Verification passes

- Confirm no `<PLACEHOLDER>` is left, `ClientId` and `TenantId` are in `config.psd1`, and the probe lists the stored grant role and observed capabilities separately.
- Focused plugin tests for this skill pass.
