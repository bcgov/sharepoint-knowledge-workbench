# Provisioning executors: safety contract, tokens and plan shapes

## Contents

- [Safety contract](#safety-contract)
- [Two different tokens](#two-different-tokens)
- [Connection and config](#connection-and-config)
- [Plan JSON shapes](#plan-json-shapes)
- [Results and verification](#results-and-verification)
- [Executor table](#executor-table)
- [List provisioning notes](#list-provisioning-notes)

## Safety contract

Every `spo-*.ps1` executor in this plugin follows the same contract:

- **Dry run by default.** Without `-Execute` it prints a structured JSON action summary (including the exact PnP cmdlet it would run) and modifies nothing.
- **Confirmation gated.** A real write needs `-Execute` and the script's own exact `-ConfirmToken`. A wrong or missing token throws (`-Execute requires -ConfirmToken <TOKEN>.`).
- A real run is a live tenant write. The user runs it; do not run it unprompted.
- It needs PnP.PowerShell with the specific cmdlet available, and throws if it is missing.

## Two different tokens

A plan JSON carries its own `confirmation_token` field (for example `REMOVE-2-abcdef0123456789`), derived by the Python planning modules and echoed in the dry-run summary. The
`-ConfirmToken` you pass is a different, fixed per-script string from the table below (for example `REMOVE-SPO-SITE-COLUMNS`). Pass the fixed string to `-ConfirmToken`; do not paste the plan's
`confirmation_token` there.

## Connection and config

Each script dot-sources `Get-WorkbenchConnectionConfig.ps1` and connects with `Connect-PnPOnline -Interactive` (see the repository's `sharepoint-ps1-authentication-convention.md` rule). Override the
connection with `-SiteUrl`, `-ClientId`, `-TenantId` and `-TenantAdminUrl`. `-ConfigPath` defaults to three directories above the script (the repository root `config.psd1`); that default does not
resolve from an installed skill, so pass `-ConfigPath`, or the explicit connection parameters, when running an installed copy.

## Plan JSON shapes

Every executor reads a plan JSON (`-PlanPath`). Each script documents the shape in its own `.DESCRIPTION` under "Plan JSON shape" (all 28 have one). Read that block, and do not invent keys. Cross-check
it against the code: `spo-trigger-reindex.ps1`'s header shows the update-site-column shape (a copy-paste), while its code actually reads `actions` entries with an optional `list_title`
(`Request-PnPReIndexList` for a list, `Request-PnPReIndexWeb` otherwise).

## Results and verification

Executors report an outcome: for example `spo-remove-site-column.ps1` returns `OBSERVED`, `PARTIAL` or `FAILED` with `removed` and `failed` lists, and an optional `-OutputPath`. Verification of the write itself varies:
`spo-provision-list.ps1` re-checks with `Get-PnPList` after creating and after deleting a list and fails loud if a deleted list still exists, whereas `spo-remove-site-column.ps1` records each column as removed or failed and
does no separate re-check. The content-type, site-column and list-column removal executors do not check whether the object is still in use, so confirm there are no dependents before a real removal.

## Executor table

Tokens are the exact strings enforced by each script. "Skill" is the dedicated skill, if any; the rest are driven through `sharepoint-apply-provisioning-plan`.

| Script | `-ConfirmToken` | PnP cmdlets | Skill |
|---|---|---|---|
| `spo-provision-list.ps1` | `PROVISION-SPO-LIST` | New-PnPList, Remove-PnPList | `sharepoint-create-list`, `sharepoint-create-document-library`, `sharepoint-remove-list` |
| `spo-update-list.ps1` | `UPDATE-SPO-LIST` | Set-PnPList | `sharepoint-update-list-settings` |
| `spo-configure-library-settings.ps1` | `CONFIGURE-SPO-LIBRARY-SETTINGS` | Set-PnPList (versioning, approval) | `sharepoint-configure-library-settings` |
| `spo-provision-site-columns.ps1` | `PROVISION-SPO-SITE-COLUMNS` | Add-PnPField, Add-PnPFieldFromXml | `sharepoint-create-site-column` |
| `spo-update-site-column.ps1` | `UPDATE-SPO-SITE-COLUMNS` | Set-PnPField | `sharepoint-update-site-column` |
| `spo-remove-site-column.ps1` | `REMOVE-SPO-SITE-COLUMNS` | Remove-PnPField | `sharepoint-remove-site-column` |
| `spo-add-list-column.ps1` | `ADD-SPO-LIST-COLUMN` | Add-PnPField (list scoped) | `sharepoint-add-list-column` |
| `spo-update-list-column.ps1` | `UPDATE-SPO-LIST-COLUMN` | Set-PnPField (list scoped) | `sharepoint-update-list-column` |
| `spo-remove-list-column.ps1` | `REMOVE-SPO-LIST-COLUMN` | Remove-PnPField (list scoped) | `sharepoint-remove-list-column` |
| `spo-configure-column-formatting.ps1` | `CONFIGURE-SPO-COLUMN-FORMATTING` | Set-PnPField -Values CustomFormatter | `sharepoint-configure-column-formatting` |
| `spo-provision-content-types.ps1` | `PROVISION-SPO-CONTENT-TYPES` | Add-PnPContentType, Add-PnPFieldToContentType, Remove-PnPFieldFromContentType, Add-PnPContentTypeToList | `sharepoint-create-content-type` |
| `spo-update-content-type.ps1` | `UPDATE-SPO-CONTENT-TYPES` | Set-PnPContentType | `sharepoint-update-content-type` |
| `spo-remove-content-type.ps1` | `REMOVE-SPO-CONTENT-TYPES` | Remove-PnPContentType | `sharepoint-remove-content-type` |
| `spo-detach-content-type-from-list.ps1` | `DETACH-SPO-CONTENT-TYPE` | Remove-PnPContentTypeFromList | `sharepoint-detach-content-type` |
| `spo-provision-list-view.ps1` | `PROVISION-SPO-LIST-VIEW` | Add-PnPView | `sharepoint-create-list-view` |
| `spo-add-list-item.ps1` | `ADD-SPO-LIST-ITEM` | Add-PnPListItem | `sharepoint-add-list-item` |
| `spo-provision-site.ps1` | `PROVISION-SPO-SITE` | New-PnPSite, Set-PnPRegionalSettings | via `sharepoint-apply-provisioning-plan` |
| `spo-provision-branding.ps1` | `PROVISION-SPO-BRANDING` | Set-PnPWebTheme, Set-PnPSite -LogoFilePath | via `sharepoint-apply-provisioning-plan` |
| `spo-manage-hub-site.ps1` | `MANAGE-SPO-HUB-SITE` | Register-PnPHubSite, Add-PnPHubSiteAssociation | via `sharepoint-apply-provisioning-plan` |
| `spo-create-modern-page.ps1` | `CREATE-SPO-MODERN-PAGE` | Add-PnPPage, Add-PnPPageSection | via `sharepoint-apply-provisioning-plan` |
| `spo-add-page-section.ps1` | `ADD-SPO-PAGE-SECTION` | Add-PnPPage, Add-PnPPageSection | via `sharepoint-apply-provisioning-plan` |
| `spo-configure-webparts.ps1` | `CONFIGURE-SPO-WEBPARTS` | Add-PnPPageWebPart | via `sharepoint-apply-provisioning-plan` |
| `spo-remove-page-webpart.ps1` | `REMOVE-SPO-PAGE-WEBPART` | Remove-PnPPageComponent | via `sharepoint-apply-provisioning-plan` |
| `spo-provision-permissions.ps1` | `PROVISION-SPO-PERMISSIONS` | New-PnPGroup, Set-PnPGroupPermissions, Add-PnPUserToGroup | via `sharepoint-apply-provisioning-plan` |
| `spo-configure-item-permissions.ps1` | `CONFIGURE-SPO-ITEM-PERMISSIONS` | Set-PnPListItemPermission | via `sharepoint-apply-provisioning-plan` |
| `spo-provision-navigation.ps1` | `PROVISION-SPO-NAVIGATION` | Add-PnPNavigationNode | via `sharepoint-apply-provisioning-plan` |
| `spo-provision-term-set.ps1` | `PROVISION-SPO-TERM-SET` | New-PnPTermGroup, New-PnPTermSet, New-PnPTerm | via `sharepoint-apply-provisioning-plan` |
| `spo-trigger-reindex.ps1` | `TRIGGER-SPO-REINDEX` | Request-PnPReIndexWeb, Request-PnPReIndexList | via `sharepoint-apply-provisioning-plan` |

## List provisioning notes

- **Duplicate-title gate.** `spo-provision-list.ps1` checks the plan's `blocking_findings` before processing any `list_deletions` entry and refuses the whole run if it is non-empty (a whole-plan refusal,
  not a per-item skip), mirroring the Python planning module's rule that a plan with a duplicate-title finding can never be executed. Read the script header for the exact scope.
- **Default `Title` column rule.** When provisioning custom join tables, lookup mappings or user preference lists (such as `My Favourite Apps`), standard generic lists automatically create a default
  `Title` column set to `Required = $true`.
