# Page modernization executors: gates, tokens and config

## Contents

- [The four executors](#the-four-executors)
- [Dry run by default](#dry-run-by-default)
- [Connection and config](#connection-and-config)
- [Same-site conversion does not rewrite links](#same-site-conversion-does-not-rewrite-links)

## The four executors

| Script | Skill | Does | Write gate |
|---|---|---|---|
| `spo-convert-page-to-modern.ps1` | `sharepoint-convert-page-to-modern` | `ConvertTo-PnPPage` for one classic page, then stamps caller-supplied field values | `-Execute -ConfirmToken CONVERT-SPO-PAGE` |
| `spo-convert-pages-bulk.ps1` | `sharepoint-convert-page-library-to-modern` | one `spo-convert-page-to-modern.ps1` subprocess per page, with a manifest, resume and throttle, then validation | `-Execute -ConfirmToken CONVERT-SPO-PAGES-BULK` |
| `spo-validate-page-conversion.ps1` | `sharepoint-validate-page-modernization` | read-only re-query of the live site against a run manifest | none (read-only) |
| `spo-page-copy-plan.ps1` | `sharepoint-copy-page-between-sites` | builds a page copy plan; with `-Execute`, runs `Copy-PnPFile` (and `Rename-PnPFile` cross-site) | `-Execute -ConfirmToken COPY-SPO-PAGE` |

Common parameters: `-SiteUrl`, `-ConfigPath`, `-ClientId`, `-TenantId`, `-TenantAdminUrl` (the copy script takes full page URLs instead of `-SiteUrl`). The conversion, bulk and validation
scripts also take `-TargetLibrary` (default `Site Pages`), `-FieldMapping` and `-LiteralFieldValues`.

## Dry run by default

Every writing executor prints its plan and makes zero tenant writes unless `-Execute` and the exact `-ConfirmToken` are both supplied. A wrong or missing token makes an `-Execute` run
throw (`-Execute requires -ConfirmToken <TOKEN>.`). A real run is a live tenant write that the user runs.

## Connection and config

All scripts dot-source `Get-WorkbenchConnectionConfig.ps1` and use the interactive `Connect-PnPOnline` convention (see the repository's `sharepoint-ps1-authentication-convention.md` rule).
`-ConfigPath` defaults to three directories above the script (the repository root `config.psd1`). That default does not resolve from an installed skill, so pass `-ConfigPath`, or
`-SiteUrl`, `-ClientId` and `-TenantId`, explicitly.

## Same-site conversion does not rewrite links

`ConvertTo-PnPPage`'s `-UrlMappingFile` and `-SkipUrlRewriting` parameters apply only to cross-site transformations. Converting within one site does not rewrite embedded links in the page
body; run a link remediation pass separately with the `sharepoint-site-migration` skills if the source content has links that need fixing.
