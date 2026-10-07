# Acceptance Criteria: workbench-initialize-connection-config

- Skill slug: `workbench-initialize-connection-config`.
- Target plugin: `sharepoint-workbench-setup`.
- Purpose: "Creates the root, git-ignored config.psd1 from the canonical config.psd1.example template: Entra ID app-registration details (TenantId, ClientId, AuthenticationMode) and the target SharePoint site (SiteUrl). Use when setting up a workbench connection for the first time. Generating the file is the default action and never connects to anything; a separate, explicit connector is needed for a read-only connection test. Mandatory answers: SiteUrl, TenantId, ClientId, AuthenticationMode."

## Constraints honored

- Never connect to SharePoint by default. A connection test runs only when the caller explicitly supplies a connector.
- Never overwrite an existing `config.psd1` unless `overwrite=True` is passed explicitly.
- Run from this skill's root. Helpers are `scripts/config_setup.py` and `scripts/psd1_writer.py`; standard library only, no other plugin required.

## Verification passes

- Confirm `config.psd1` exists at the repository root with the supplied values. If a connection test was requested, confirm it used an explicitly supplied connector; invoke the `workbench-validate-sharepoint-connection` skill to supply one.
- Focused plugin tests for this skill pass.
