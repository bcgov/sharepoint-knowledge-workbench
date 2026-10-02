# SPFx scripts: which write to the tenant, and what gates them

## Contents

- [Gate summary](#gate-summary)
- [Script table](#script-table)
- [Connection and config](#connection-and-config)

## Gate summary

These scripts do **not** share one safety model. Do not assume a dry run exists.

- **No gate: writes immediately.** `deploy-spfx-package.ps1`, `publish-spfx-package.ps1` and `provision-sample-dossier-schema.ps1` perform live tenant writes as soon as they run. The user runs them, with the right
  target confirmed first.
- **`-WhatIf` / `-Confirm` (PowerShell `ShouldProcess`).** `register-listview-command-set.ps1` supports them, but there is no `-Execute` switch: without `-WhatIf` it writes.
- **`-Execute` gate (dry run by default).** `associate-form-customizer.ps1` and `remove-form-customizer-association.ps1` print an analysis and change nothing unless `-Execute` is passed.
- **Read-only or local.** `validate-form-customizer-association.ps1` and `verify-app-catalog.ps1` read; `package-spfx-solution.ps1`, `check-spfx-toolchain.ps1` and `setup-spfx-workbench.ps1` work locally.

## Script table

| Script | Does | Key parameters | Gate |
|---|---|---|---|
| `deploy-spfx-package.ps1` | Uploads/publishes a `.sppkg` (`Add-PnPApp`); optionally ensures a site App Catalog (`Add-PnPSiteCollectionAppCatalog`) and installs it (`Install-PnPApp -Scope Site`) | `-PackagePath`, `-Scope Site\|Tenant`, `-Install`, `-EnsureSiteAppCatalog`, `-SkipFeatureDeployment`, `-SiteUrl`, `-TenantAdminUrl`, `-ClientId`, `-TenantId`, `-ConfigPath` | none |
| `publish-spfx-package.ps1` | Same publish flow with `config.psd1`-driven connection and catalog readback via `Get-PnPApp` | same parameters as above | none |
| `verify-app-catalog.ps1` | Confirms a site's Site Collection App Catalog | `-SiteUrl`, `-AdminUrl`, `-ClientId` | read-only |
| `package-spfx-solution.ps1` | Runs the production Heft build and checks a non-empty `.sppkg` exists | `-SolutionPath` | local |
| `check-spfx-toolchain.ps1` | Checks Node (18 or 22), npm, `yo`, `@microsoft/generator-sharepoint`; exits non-zero on a missing required dependency | none | local |
| `setup-spfx-workbench.ps1` | Validates the project, optionally trusts the dev certificate, prints local and hosted workbench URLs | `-ProjectPath`, `-SiteUrl`, `-DebugPort` (4321), `-SkipToolchainCheck`, `-SkipCertInstall` | local |
| `register-listview-command-set.ps1` | Registers or removes a list-scoped ListView Command Set custom action | `-ListName`, `-Name`, `-Title`, `-ComponentId`, `-ComponentProperties`, `-Sequence`, `-Remove`, `-ConfigPath`, `-SiteUrl`, `-ClientId`, `-TenantId` | `-WhatIf` / `-Confirm` |
| `associate-form-customizer.ps1` | Associates a Form Customizer component ID with a list content type | `-ListName`, `-ContentTypeName` (default `Item`), `-ComponentId`, `-ComponentProperties`, `-Modes New\|Edit\|Display\|All`, `-Execute` | `-Execute` |
| `remove-form-customizer-association.ps1` | Removes that association | `-ListName`, `-ContentTypeName`, `-Modes`, `-Execute` | `-Execute` |
| `validate-form-customizer-association.ps1` | Audits the association state | `-ListName`, `-ContentTypeName`, `-ExpectedComponentId`, `-OutputJson` | read-only |
| `provision-sample-dossier-schema.ps1` | Idempotently creates sample lists, lookups, Picture columns, sample records and a test page for validating Master-Detail web parts | `-SiteUrl`, `-ClientId`, `-TenantId`, `-TenantAdminUrl`, `-ConfigPath`, `-PageName` (default `master-detail-dossier-poc`) | none |

## Connection and config

Scripts connect with `Connect-PnPOnline -Interactive`. Connection comes from `config.psd1` (`-ConfigPath`) or explicit `-SiteUrl`, `-ClientId`, `-TenantId` (and `-TenantAdminUrl` for tenant scope). Where
`-ConfigPath` defaults to a path relative to the script, that default does not resolve from an installed skill, so pass `-ConfigPath` or the explicit parameters.
