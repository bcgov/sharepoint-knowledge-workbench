# SharePoint Migration .ps1 Source Inventory and Onboarding Plan

147 `.ps1` files audited in `jag-csb-cmat-sharepoint-online/plugins/sharepoint-migration/scripts/`
(root + 14 subfolders). Classification counts (per-file table total, authoritative — see
reconciliation note at document end for the small headline/per-folder discrepancy this rough count
still carries): **Onboard As-Is: 12**, **Onboard With Rewrite: 56**,
**Already Exists: 4**, **Duplicate/Low Value: 26**, **Transitional/Deprecated: 51** (approx. — not
yet exactly reconciled, see closing note). Headline
finding: the destination repo's `sharepoint-discovery` and `sharepoint-schema` plugins are
entirely read-only analysis of pre-existing exports — every real *collector* (`inventory/`,
`diagnostics/`, `get-source-item-counts.ps1`) is missing and must be ported as new "collect-*"
skills. Similarly `sharepoint-content-migration`, `sharepoint-content-publication`,
`sharepoint-provisioning`, and `sharepoint-page-modernization` all have Python planning logic that
raises `ExecutorRequired`/`NotImplementedError` with no real `Connect-PnPOnline` executor behind
it — the source repo's `lib/migrate-helpers.ps1`, `upload/upload-modern-page.ps1`,
`waves/wave0a-site-columns.ps1`/`wave0b-content-types.ps1`, and `page-migration/
convert-and-upload-aspx.ps1` are the working executors that fill those gaps, but every one needs a
rewrite pass to strip CMAT/ITAU/csb.jag.gov.bc.ca hardcoding and align to the
`Connect-PnPOnline -Interactive` + `config.psd1` + `-TenantAdminUrl` convention. Roughly 40% of
files (`_deprecated/`, `tests/`, most of `waves/wave4-9`) are CMAT-project-specific and not
generalizable.

## Onboard As-Is (10 files)

| Source path | What it does | Target plugin | Target skill | Auth changes needed |
|---|---|---|---|---|
| `schema-audit/compare-prod-vs-test-schema.ps1` | Pure disk-based diff of two pre-existing JSON schema exports (site columns, CTs, lists, fields, workflows); no tenant connection. | sharepoint-schema | `audit-schema` / `diff-sharepoint-schema` (extend) | None — no tenant I/O. |
| `diagnostics/export-images-library-inventory.ps1` | `Connect-Spo` (already PnP-based) + `Get-PnPListItem -PageSize` recursive over Image library; outputs file name + server-relative URL CSV. | sharepoint-discovery | NEW SKILL: `collect-sharepoint-inventory` | Already follows PnP pattern; swap `Connect-Spo` helper for standard `Connect-PnPOnline -Interactive` reading `config.psd1`; parameterize library name. |
| `diagnostics/export-persons-picture-description.ps1` | `Connect-Spo` + `Get-PnPListItem -PageSize` (bypasses 5k view limit) on Persons list; exports JSON + CSV of rich-text Comment field. | sharepoint-discovery | NEW SKILL: `collect-sharepoint-inventory` | Same as above; parameterize list/field name (currently Persons/Comment-specific). |
| `lib/logging-helpers.ps1` | `Start-Transcript`/`Stop-Transcript` wrapper (`Start-RunLog`/`Stop-RunLog`); no tenant I/O. | sharepoint-content-migration (shared) | supports `migrate-sharepoint-list-content` | None — pure logging utility. |
| `lib/list-helpers.ps1` | `Invoke-WithRetry` (429/throttle exponential backoff), `New-ListSafe`/`New-LibrarySafe` (`New-PnPList` with existence check). | sharepoint-provisioning | supports `provision-modern-calendar-list` and any new provisioning skill | None — orchestration only, no direct auth calls. |
| `lib/xml-helpers.ps1` | `Escape-XmlAttr` — single string-escaping utility for generated field XML. | sharepoint-provisioning | supports field/CT provisioning skills | None. |
| `link-conversion/Repair-EmbeddedLinks.ps1` | Scans `CanvasContent1` of modern pages, applies config-driven regex `UrlPatterns` to rewrite classic `/Pages/` links to `/SitePages/`, logs to CSV, supports `-WhatIf`. Generic, not project-specific. | sharepoint-link-remediation | `remediate-links` (existing) | Add `-TenantAdminUrl` param; already reads `config.psd1` + `Connect-PnPOnline -Interactive`. |
| `page-migration/combine-preview.ps1` | Local-only: merges `chrome.json` (nav/logo/ancestors) + extracted page HTML into a self-contained offline preview file; **zero tenant I/O**. | sharepoint-page-modernization | `compose-page-preview` (existing) | None — no auth; remove hardcoded "CourtAdmin"/"CMAT"/font branding strings, parameterize chrome/page folder paths. |
| `utilities/get-list-columns.ps1` | Queries live SPO list for custom columns via `Get-PnPField`; read-only report. | sharepoint-schema | `audit-schema` (existing) | None beyond standardizing `Connect-PnPOnline` call already close to convention. |
| `utilities/get-lookup-columns.ps1` | Extracts lookup-column metadata (target list, field) via read-only `Get-PnPField` query. | sharepoint-schema | `audit-schema` (existing) | None beyond standardizing `Connect-PnPOnline` call already close to convention. |

## Onboard With Rewrite (47 files)

| Source path | What it does | Target plugin | Target skill | Rework needed |
|---|---|---|---|---|
| `inventory/export-sharepoint-inventory.ps1` | REST-based full inventory (lists, fields, views, CTs, permissions, workflows, legacy webpart scan) via `Invoke-RestMethod` + `Get-Credential`/NTLM. Hardcoded `itau.test.jag.gov.bc.ca/cmat`. | sharepoint-discovery | NEW SKILL: `collect-sharepoint-inventory` | Replace NTLM/`Get-Credential`/raw REST with `Connect-PnPOnline -Interactive` + PnP cmdlets; remove hardcoded itau/cmat URL; read `config.psd1`. |
| `inventory/export-sharepoint-inventory-custom.ps1` | Enhanced REST inventory: storage metrics, wiki-page scan (BaseTemplate 119), customization audit; partially uses `auth-helpers`. | sharepoint-discovery | NEW SKILL: `collect-sharepoint-inventory` | Align fully to `Connect-PnPOnline -Interactive`; remove remaining raw `Invoke-RestMethod` calls; add `-TenantAdminUrl`. |
| `inventory/check-managed-metadata-custom.ps1` | Checks taxonomy/managed-metadata columns via REST + CSOM TaxonomySession; hardcoded itau URLs. | sharepoint-discovery | NEW SKILL: `audit-managed-metadata` | Replace REST/manual `Get-Credential` with PnP; remove hardcoded URLs; keep CSOM term-store fallback but wrap in config-driven params. |
| `schema-audit/get-persons-missing-fields-live.ps1` | Reads live source-site Persons schema via CSOM + `Get-Credential` + `Connect-PnPOnline -Credentials`; hardcoded `itau.test.jag.gov.bc.ca/cmat`. | sharepoint-schema | `audit-schema` (extend) | Replace manual credential prompt with `Connect-PnPOnline -Interactive`; parameterize site URL via `config.psd1`. |
| `diagnostics/export-images-library-inventory.ps1` *(see as-is table — minimal change only)* | — | — | — | — |
| `diagnostics/test-csb-intranet-dev-write.ps1` | DEV-only write lifecycle test (create/verify/remove list, library, page); hardcoded DEV URL + inline app IDs; uses `Connect-Spo`. | workbench-setup | `validate-workbench-environment` (extend) or NEW: `test-write-lifecycle` | Remove hardcoded DEV URL/app IDs, source from `config.psd1`; replace `Connect-Spo` with standard pattern. |
| `scripts/diagnose-onprem-schema-drift.ps1` (root) | Read-only on-prem SP2016 schema-drift diagnostic for CMAT lists; `Connect-PnPOnline -UseWebLogin`/credential prompt; hardcoded `itau.test.jag.gov.bc.ca/cmat`; exports 4 CSVs + report. | sharepoint-discovery | NEW SKILL: `audit-onprem-schema-drift` | Replace `-UseWebLogin` with `Connect-PnPOnline -Interactive`; remove hardcoded URL/list names; parameterize via `config.psd1`. |
| `utilities/deploy-spo-schema.ps1` | Provisions lists/libraries/fields/CTs to SPO from local export JSON; `Connect-Spo` + field/guidmap helpers. | sharepoint-provisioning | NEW SKILL: `provision-sharepoint-schema` | Replace `Connect-Spo` with standard pattern; add `-TenantAdminUrl`; verify field-helper dependency chain ports cleanly. |
| `utilities/apply-schema-gaps.ps1` | Applies field/CT schema "gap" remediation between on-prem export and SPO deployment. | sharepoint-provisioning | NEW SKILL: `provision-sharepoint-schema` | Standardize auth; remove any hardcoded export paths. |
| `utilities/update-matrix-calculated.ps1` | Updates calculated-field formulas in SPO from `matrix.json`/`calculated-columns.json`. | sharepoint-provisioning | NEW SKILL: `provision-sharepoint-schema` | Standardize auth; parameterize matrix path. |
| `utilities/reset-and-recreate-appearance-schema.ps1` | Destructive reset/recreate of Appearance content type schema. | sharepoint-provisioning | NEW SKILL: `provision-sharepoint-schema` | Full rewrite: remove hardcoded CT/field names, parameterize, standardize auth, keep destructive-action confirmation gate. |
| `utilities/clean-slate-dev-bulk.ps1` | Destructive DEV cleanup (reverse-dependency-order list/CT/site-column removal); hardcoded `AG-CSB-ITAU-CMAT-DEV` + inline app IDs; `Connect-PnPOnline -Interactive` inline. | workbench-setup | NEW SKILL: `reset-workbench-environment` | Remove hardcoded URL/app IDs; source from `config.psd1`; keep interactive "type DESTROY to confirm" safety gate. |
| `utilities/clean-slate-test-bulk.ps1` | TEST-environment variant of `clean-slate-dev-bulk.ps1`. | workbench-setup | NEW SKILL: `reset-workbench-environment` | Same as DEV variant — likely mergeable into one parameterized script. |
| `utilities/patch-hidden-fields.ps1` | Un-hides hidden schema fields (write op). | sharepoint-provisioning | NEW SKILL: `provision-sharepoint-schema` | Standardize auth; verify no hardcoded field/list names remain. |
| `utilities/remove-duplicate-lookup-columns.ps1` | Removes duplicate lookup columns (write op). | sharepoint-provisioning | NEW SKILL: `provision-sharepoint-schema` | Standardize auth; add `-TenantAdminUrl`. |
| `utilities/extract-choices.ps1` | Extracts Choice/MultiChoice options from on-prem via REST + local export JSON; mixed `Connect-Spo`/raw REST. | sharepoint-discovery | `extract-choice-fields` (existing skill, extend with live-collection mode) | Align REST calls to PnP cmdlets; parameterize export-base path. |
| `utilities/extract-choices-direct.ps1` | Direct-extraction variant of `extract-choices.ps1`. | sharepoint-discovery | `extract-choice-fields` (extend) | Same as above; likely mergeable with `extract-choices.ps1`. |
| `lib/auth-helpers.ps1` | `Connect-Spo` (reads `config.psd1`, `Connect-PnPOnline -Interactive`) + `Get-ErrorDetail`. This IS the source repo's own auth-convention precursor. | workbench-setup | reference pattern for all other scripts | Rename/replace with destination's own `test-spo-connection.ps1` pattern; add `-TenantAdminUrl` support (currently missing); fix hardcoded `config.psd1` relative depth. |
| `lib/migrate-helpers.ps1` | 632-line core: `Invoke-ListMigration` (field mapping, lookup resolution, batching), ID-mapping persistence, `Test-ListMigration`, `Clear-SpoList`. This is the real executor behind `item_migration.py::apply_item_migration`'s `ExecutorRequired` stub. | sharepoint-content-migration | `migrate-sharepoint-list-content` | Major rework: isolate on-prem REST (`Invoke-OnPremRest`) from SPO write logic; strip CMAT-specific field-rename hardcoding (e.g. "Location0"); wire as the injected executor for `item_migration.py`; standardize auth. |
| `lib/content-type-lib.ps1` | `Add-PnPContentType`, field-to-CT linking, hide/show/unlink field helpers, all with `-DryRun` support via `Get-Variable` scope hack. | sharepoint-provisioning | NEW SKILL: `provision-sharepoint-schema` | Rework `-DryRun` detection to explicit param instead of scope-1 `Get-Variable`; no direct auth calls (depends on active connection) but must document that. |
| `lib/field-helpers.ps1` | `Get-DeployableFields`, `Repair-FieldType`, `Add-FieldSafe` (XML-based Lookup/User field creation), `Invoke-FieldsForList` (250+ lines, full schema deployment incl. field renames/lookups/calendar handling). | sharepoint-provisioning | NEW SKILL: `provision-sharepoint-schema` | Remove hardcoded CMAT field-rename logic ("court_room"→"Location0"); extract rename-mapping to caller-supplied config; keep GUID-map lookup resolution as a documented on-prem-only path. |
| `lib/guidmap-helpers.ps1` | `Build-GuidMap` — on-prem SP2016 REST list-GUID→title map; `Get-Credential` fallback. | sharepoint-schema | supports `provision-sharepoint-schema` (on-prem-only utility) | Document as SP2016-extraction-only, not for SPO context; standardize the credential fallback. |
| `lib/user-groups-lib.ps1` | Entra/AAD user lookup (`Get-PnPAzureADUser`, 4 strategies) + group create/add/remove; hardcoded protected-login list (specific personal emails). | sharepoint-provisioning | NEW SKILL: `provision-sharepoint-users-groups` | **Remove hardcoded personal email addresses** (richard.fremmerlid@gov.bc.ca etc.) — move protected-accounts list to `config.psd1`; standardize auth. |
| `content-migration/migrate-list.ps1` | Single-list orchestrator wrapping `Invoke-ListMigration`; hardcoded `config.psd1` relative depth and manifest/export-base paths. | sharepoint-content-migration | `migrate-sharepoint-list-content` | Standardize `config.psd1` path resolution; standardize auth; this is the CLI entry point for the `migrate-helpers.ps1` executor above. |
| `content-migration/migrate-all.ps1` | Manifest-driven multi-list orchestrator with wave/order gating (`-FromOrder`/`-ToOrder`). | sharepoint-content-migration | `migrate-sharepoint-list-content` | Same auth fix; manifest format (`content-migration-manifest.json`) needs to be generalized, not CMAT-list-specific. |
| `content-migration/test-migrate-list.ps1` | Post-migration validation: item-count check + spot-check key fields via `Test-ListMigration`. | sharepoint-content-migration | NEW SKILL: `validate-list-content-migration` | Standardize auth; otherwise reusable as-is logic-wise. |
| `content-migration/test-migrate-all.ps1` | Batch validation across manifest lists. | sharepoint-content-migration | NEW SKILL: `validate-list-content-migration` | Same as single-list variant. |
| `content-migration/get-source-item-counts.ps1` | On-prem SP2016 REST inventory: storage/list/library counts+sizes; `UseDefaultCredentials`/`Get-Credential` fallback; hardcoded ignore-list. | sharepoint-discovery | NEW SKILL: `collect-sharepoint-inventory` | Document as on-prem-only path (not SPO); standardize credential fallback pattern. |
| `upload/migrate-site-assets.ps1` | Enumerates/downloads on-prem SiteAssets via REST, uploads to SPO via `Add-PnPFile`. | sharepoint-content-migration | NEW SKILL: `migrate-site-assets` | Modernize custom `HttpClient` wrapper to `Invoke-RestMethod`; standardize SPO-side auth to `Connect-PnPOnline -Interactive`. |
| `link-conversion/Invoke-LinkConversionBulk.ps1` | Orchestrates bulk classic→modern page conversion, spawns `LinkConversion.ps1` per page, collects manifest CSV, runs repair+test at end. | sharepoint-content-publication | NEW SKILL: `execute-page-bulk-migration` | Remove "CrownNet"/"MediaInfo" project labels; parameterize source/target library names; add `-TenantAdminUrl` pass-through. |
| `link-conversion/LinkConversion.ps1` | Single-page `ConvertTo-PnPPage` conversion with hardcoded destination-metadata field mapping. | sharepoint-content-publication | NEW SKILL: `convert-page-to-modern` | Remove hardcoded field mapping (MediaCategory→PageCategory etc.); parameterize dest fields via config; add `-TenantAdminUrl` (ConvertTo-PnPPage needs admin-center context). |
| `link-conversion/Test-LinkConversion.ps1` | Post-conversion validation against run-manifest.csv: checks metadata population + `PromotedState`. | sharepoint-content-publication | NEW SKILL: `validate-page-migration` | Parameterize expected metadata field names instead of hardcoding; add `-TenantAdminUrl`. |
| `page-migration/convert-and-upload-aspx.ps1` | Fetches legacy ASPX via NTLM, strips chrome, invokes Python analysis pipeline for list-view pages, uploads via `Add-PnPPage`/`Add-PnPPageTextPart`. This is the real executor missing behind `sharepoint-page-modernization`'s classification-only Python. Hardcoded ClientId + ITAU/CMAT/PIO_Cases paths. | sharepoint-page-modernization | `convert-aspx-pages` (existing, extend with execution path) | Replace hardcoded ClientId with `config.psd1`; keep NTLM only for the legacy on-prem download leg (correct, can't avoid); replace SPO-upload leg with standard `Connect-PnPOnline -Interactive`; remove hardcoded fixture/mapping paths. |
| `page-migration/convert-wiki-page.ps1` | Extracts SP2016 wiki page (CSOM+HTTP fallback, NTLM), strips chrome, builds local preview HTML. No SPO write. | sharepoint-page-modernization | NEW SKILL: `extract-legacy-page-content` | NTLM/on-prem auth is correct and stays; parameterize `OutputRoot` instead of hardcoded relative repo path; remove "14_prototyping" assumption. |
| `page-migration/diagnose-page.ps1` | REST diagnostic: probes Pages library/file existence; read-only; `Invoke-RestMethod` + `UseDefaultCredentials`/`Get-Credential`. | sharepoint-page-modernization | NEW SKILL: `diagnose-aspx-page` | Replace REST/NTLM with `Connect-PnPOnline -Interactive` + PnP read cmdlets; parameterize source-library name. |
| `page-migration/analyze-aspx-webparts.ps1` | Local parse of downloaded `.aspx` files: web-part zones/types/connections; no tenant I/O but hardcoded project paths (`01_source_sharepoint`, csb-intranet-prod). | sharepoint-page-modernization | `analyze-aspx-pages` (existing, extend) | No auth needed; parameterize `-InputDir`/`-OutputDir`/`-SiteUrl` as explicit CLI args instead of hardcoded defaults. |
| `page-migration/extract-all-aspx-pages.ps1` | REST-enumerates and downloads every `.aspx` in a legacy SP2016 site (Pages, list forms, root); `UseDefaultCredentials`/NTLM; hardcoded `itau.test.jag.gov.bc.ca` default. | sharepoint-discovery | NEW SKILL: `collect-sharepoint-inventory` (on-prem leg) | Keep NTLM (on-prem legacy, correct); remove hardcoded default site URL; parameterize output dir. |
| `page-migration/extract-site-navigation.ps1` | REST-only (no CSOM/PnP) extraction of top-nav/quick-launch/breadcrumb/master-page from SP2016; Kerberos/NTLM or explicit creds; produces `site-chrome.json`. | sharepoint-discovery | `analyze-site-navigation` (existing — currently analysis-only; this is the missing collector) | Keep NTLM for on-prem leg; already reads `config.psd1`, otherwise fine; document as on-prem-only collector feeding the existing analysis skill. |
| `page-migration/extract-webpart-content.ps1` | Reads `scan-webparts.ps1`'s CSV output, calls legacy `_vti_bin/exportwp.aspx` per web part (read-only) to pull full Content property (HTML/JS); documents that the modern REST API 404s for this. | sharepoint-discovery | `analyze-webpart-code` (existing — currently analysis-only; this is the missing collector) | Keep on-prem NTLM/integrated-auth path (only working mechanism on SP2016); parameterize CSV/config paths. |
| `page-migration/download-custom-forms.ps1` | Downloads non-standard custom list-form `.aspx` files identified by an inventory pass, filtering known false-positives. | sharepoint-discovery | `analyze-custom-forms` (existing — currently analysis-only; this is the missing collector) | Standardize on-prem auth (`UseIntegratedAuth`/credential fallback pattern already present); parameterize paths. |
| `page-migration/generate-discovery-reports.ps1` | Local-only: assembles 7 standard markdown discovery reports (variance analysis, master-page summary, script-editor extraction, etc.) from prior JSON/CSV outputs; no tenant I/O. | sharepoint-discovery | NEW SKILL: `generate-discovery-report-set` | No auth; generalize the report templates away from CMAT-specific naming ("CMAT-MODERNIZATION-VARIANCE-ANALYSIS"). |
| `page-migration/scan-all-webparts-live.ps1` | Live `GetLimitedWebPartManager` REST scan of every page in Pages library: all web-part types, list bindings, connections; hardcoded `itau.test.jag.gov.bc.ca`. | sharepoint-discovery | `analyze-webpart-code` (existing — currently analysis-only; this is the missing collector) | Remove hardcoded default site URL; parameterize via `config.psd1`; keep NTLM (on-prem SP2016). |
| `page-migration/scan-webparts.ps1` | Recursive scan for CEWP/SEWP instances via `GetLimitedWebPartManager`; explicitly documents fixing a prior title-keyword-filter bug (now unfiltered). | sharepoint-discovery | `analyze-webpart-code` (existing — currently analysis-only; this is the missing collector) | Standardize `config.psd1` path resolution (currently hardcoded relative depth); keep on-prem auth pattern. |
| `waves/deploy-all-waves.ps1` | Orchestrator: invokes wave/utility scripts sequentially with `-Wave` filter; hardcoded wave/step names baked to CMAT project. | sharepoint-migration-planning | NEW SKILL: `orchestrate-wave-deployment` | Parameterize the steps array (read from config/JSON instead of hardcoding wave names); add `-TenantAdminUrl` pass-through. |
| `waves/phase1-clean-slate.ps1` | Destructive removal of lists/site-columns/CTs per `matrix.json`; hardcoded CMAT-DEV/TEST/Sandbox safety-check strings and `ITAU_Cal_*` pattern. | sharepoint-provisioning | NEW SKILL: `reset-workbench-environment` | Remove hardcoded safety-check strings and calendar-prefix assumption; parameterize; add `-TenantAdminUrl`. |
| `waves/wave0a-site-columns.ps1` | Deploys site columns from `site-columns.json`; already uses `Connect-Spo` + calendar-collision skip rule (Start/End). Reusable **pattern**, config-path is CMAT-relative. | sharepoint-provisioning | NEW SKILL: `provision-sharepoint-schema` | Standardize `config.psd1`/`site-columns.json` path resolution; standardize auth; otherwise close to generic. |
| `waves/wave0b-content-types.ps1` | Deploys site content types from `assets/templates/`; uses `Connect-Spo` + `content-type-lib.ps1`. | sharepoint-provisioning | NEW SKILL: `provision-sharepoint-schema` | Same as wave0a — standardize path/auth, otherwise generic pattern worth keeping. |
| `waves/wave1-zero-deps.ps1` | Creates lists/libraries with no lookup dependencies from `wave-dependency-matrix.json`; matrix-driven, not individually hardcoded per-list. | sharepoint-provisioning | NEW SKILL: `provision-sharepoint-schema` | Parameterize `MatrixPath`/`ExportBase`/`ChoicesOverridesPath`; standardize auth; the matrix-driven pattern itself is the reusable part. |
| `utilities/audit-list-columns.ps1` | Compares local export JSON against live SPO columns; `Connect-Spo` pattern, read-only. | sharepoint-schema | `audit-schema` (existing, extend with live-compare mode) | Standardize auth; reads `matrix.json` for deployment order — parameterize path. |
| `utilities/audit-spo-duplicates.ps1` | Finds duplicate lookup columns across lists; read-only live query. | sharepoint-schema | `audit-schema` (extend) | Standardize auth. |
| `utilities/compare-site-parity.ps1` | Compares schema/content parity between two live sites (inferred from name; not deeply read). | sharepoint-schema | `diff-sharepoint-schema` (extend) | Standardize auth; verify no hardcoded site URLs remain — needs a closer read before onboarding. |
| `utilities/compare-test-prod.ps1` | Compares TEST vs PROD live-site schema. | sharepoint-schema | `diff-sharepoint-schema` (extend) | Standardize auth; remove hardcoded environment URLs. |
| `utilities/discover-calculated-columns.ps1` | Discovers calculated/formula columns via live schema scan. | sharepoint-schema | `audit-schema` (extend) | Standardize auth. |
| `utilities/discover-sandbox-definitions.ps1` | Discovers sandbox solutions/custom actions on a live site. | sharepoint-discovery | NEW SKILL: `collect-sharepoint-inventory` | Standardize auth. |
| `utilities/check-managed-metadata-spo-prod.ps1` | Checks taxonomy columns on live SPO (SPO-side counterpart of `check-managed-metadata-custom.ps1`). | sharepoint-schema | `audit-schema` (extend) | Verify auth pattern (likely already `Connect-Spo`-based); standardize to convention. |
| `calendars/modern-calendar-lib.ps1` | Reusable dot-sourced library: `New-ModernCalendarList`, `Add-CalendarContentTypeSafe`, `Set-NewButtonContentTypes` — provisions Template-100 calendars with Start/End fields and form layouts via `New-PnPList`/`Add-PnPContentTypeToList`/`Add-PnPFieldFromXml`. | sharepoint-provisioning | `provision-modern-calendar-list` (existing — this is its missing executor) | Remove hardcoded `ITAU_Cal_*` list names and form-template folder paths; parameterize; standardize auth; this is the core capability the destination `calendar_provisioning.py` stub needs behind it. |
| `calendars/remediate-calendar-dates.ps1` | Post-migration backfill of calendar Start/End datetime fields from text date/time fields; supports `-DryRun`; already discovers `ITAU_Cal_*` dynamically or accepts `-ListName`. | sharepoint-provisioning | NEW SKILL: `remediate-calendar-dates` | Read `config.psd1` instead of requiring explicit `-SiteUrl`; standardize `Connect-PnPOnline` call; add `-TenantAdminUrl`. |
| `calendars/update-calendar-form-layouts.ps1` | Applies custom JSON form layouts (header/body/footer) to calendar content types across all `ITAU_Cal_*` lists or one via `-ListName`. | sharepoint-provisioning | `provision-modern-calendar-list` (extend) | Parameterize form-templates and courthouse-mapping paths as skill resources; add `config.psd1`/`-TenantAdminUrl`. |
| `calendars/add-scheduled-ct-to-regionals.ps1` | Attaches scheduled-appearance content type + links fields to 4 regional calendars; uses non-standard `Connect-Spo` helper. | sharepoint-provisioning | `provision-modern-calendar-list` (extend) | Replace `Connect-Spo` with standard `Connect-PnPOnline -Interactive` + `-TenantAdminUrl`; remove hardcoded regional names. |
| `calendars/recreate-regional-calendars-as-106.ps1` | Creates 5 named regional calendars by calling `New-ModernCalendarList`; prints GUIDs for manual overlay config (no write via overlay API). | sharepoint-provisioning | NEW SKILL: `provision-regional-calendars` (or fold into `provision-modern-calendar-list` as example, likely eval-only) | Parameterize regional calendar names via `config.psd1`; standardize auth. |
| `calendars/patch-regionals.ps1` | Detach/reattach content type on 4 regional calendars to fix field-link corruption; non-standard `Connect-Spo`. | sharepoint-provisioning | `provision-modern-calendar-list` (extend, remediation mode) | Replace `Connect-Spo`; parameterize regional names; add `config.psd1`. |
| `app-reg-tests/create-app-cert.ps1` | Creates a self-signed X.509 cert for Entra App-Only auth, installs it locally, exports the public `.cer` for app-registration upload. Genuinely useful, not project-specific. | workbench-setup | `request-app-registration` (existing, extend for App-Only cert generation) | No SPO auth involved (local cert-store operation); align naming/params with `app-registration-overview.md`'s App-Only scenario. |

## Already Exists (4 files)

| Source path | What it does | Existing destination equivalent |
|---|---|---|
| `diagnostics/test-spo-auth.ps1` | Device-code OAuth2 bearer-token auth test against SPO; calls `/_api/contextinfo`; hardcoded `bcgov.sharepoint.com`. | `plugins/workbench-setup/scripts/test-spo-connection.ps1` (interactive PnP connection test covers this need with the standard pattern). |
| `diagnostics/test-csb-intranet-connections.ps1` | Multi-site (DEV/TEST/PROD) read-only connection test via `Connect-Spo` + `Get-PnPWeb`. | `plugins/workbench-setup/scripts/test-spo-connection.ps1` / `test-network-connectivity.ps1` (same capability, generic multi-config variant not needed — config swapping covers this). |
| `lib/auth-helpers.ps1`'s `Connect-Spo` function (as a *pattern*, not file-for-file) | Reads `config.psd1`, calls `Connect-PnPOnline -Interactive`. | `plugins/workbench-setup/scripts/test-spo-connection.ps1` already implements the destination repo's canonical version of this exact pattern (see `.agent/rules/sharepoint-ps1-authentication-convention.md`). |
| `app-reg-tests/test-etl-app-registration.ps1` / `test-interactive-app-registration.ps1` (capability, not files) | Validates App-Only cert auth and interactive delegated auth against a live site. | `plugins/workbench-setup/scripts/test-pnp-effective-capability-probe.ps1` covers the "does this registration actually work" validation need generically. |

## Duplicate / Low Value (30 files)

| Source path | Why |
|---|---|
| `page-migration/sample-webpart-content.ps1` | One-off investigation script hardcoded to `PIO_Cases`/`itau.test.jag.gov.bc.ca`; not a reusable capability. |
| `upload/upload-modern-page.ps1` | Prototype-quality `Add-PnPPage` example with hardcoded PnP multi-tenant ClientId; superseded in value by the `LinkConversion.ps1`/`convert-and-upload-aspx.ps1` real executors. |
| `upload/upload-modern-page-rest.ps1` | Functional duplicate of `upload-modern-page.ps1` (shorter variant, same hardcoded ClientId); no reason to keep both. |
| `upload/upload-pages-sharegate.ps1` | Requires third-party Sharegate Migrate Shell; produces non-editable pages; superseded by native PnP page-conversion path. |
| `upload/upload-page-sharegate-shell.ps1` | Sharegate-session REST workaround with hardcoded TenantId/ClientId/site URL; brittle direct-REST pattern PnP already covers better. |
| `upload/pnp-powershell-upload-script-example.ps1` | Simple reference example; logic is straightforward enough to inline in a skill, not worth porting standalone. |
| `content-migration/fix-persons-image-paths.ps1` | Highly CMAT-specific one-off remediation (PublishingImages→Images1 path rewrite for the Persons list); no generalizable value. |
| `lib/sp-extract-lib.ps1` (page-content-extraction portion) | Destination already handles page content extraction via the pandoc-based plugins; this 680-line library's HTML-building logic duplicates that. CSOM helper portion has narrow SP2016-only reuse (see rewrite table's `guidmap-helpers.ps1` treatment for the pattern that IS worth keeping — the raw HTML/CSS chrome builder itself is not). |
| `calendars/set-calendar-overlays.ps1` | Explicitly deprecated in-file (early return) — attempted SSOM-only CalendarSettings API not supported in SPO CSOM. |
| `calendars/get-calendar-overlay-urls.ps1` | Explicitly deprecated in-file (early return) — functionality consolidated into `recreate-regional-calendars-as-106.ps1`. |
| `calendars/analyze-calendar-diff.ps1` | Ad hoc two-list diff troubleshooting tool with hardcoded temp output path; superseded by generic `sharepoint-schema` diff capability once onboarded. |
| `calendars/analyze-user-calendar.ps1` | Inspects a hardcoded `test-calendar-4` scratch list; not a reusable capability. |
| `calendars/capture-ct-state.ps1` | Before/after JSON snapshot tool hardcoded to specific CT/list names (`ITAU_Cal_Victoria`); one-off audit artifact. |
| `calendars/check-calendar-cts.ps1` | Verifies content types on a hardcoded list of 24 named city calendars; entirely CMAT-project-specific. |
| `calendars/diagnose-and-compare.ps1` | Troubleshooting comparison of 3 hardcoded list names; one-off diagnostic. |
| `calendars/query-ct-fields.ps1` | Lists field links on one hardcoded content type; narrow diagnostic, non-standard `Connect-Spo` auth. |
| `calendars/verify-all-calendars.ps1` | Verifies `ITAU_Cal_*` calendars against a hardcoded schema matrix and regional-name list; CMAT-specific verification, not generalizable without a full rewrite that duplicates `sharepoint-schema` diff capability. |
| `calendars/clean-all-calendars.ps1` | Destructive cleanup scoped to `ITAU_Cal_*` naming pattern; narrow reuse value beyond the generic reset-environment capability already captured via `clean-slate-dev-bulk.ps1`. |
| `waves/wave4-pio-cases.ps1`, `wave5-icm-cases.ps1`, `wave6-itau-cases.ps1` (3 files, matrix-driven `-Wave 4/5/6` dispatcher `wave-cases.ps1`) | Domain-model-specific (PIO/ICM/ITAU case management); the underlying matrix-driven pattern (`wave-cases.ps1` itself) has some reuse value but the case types it encodes do not. |
| `waves/wave2-persons.ps1` | Persons-domain-model-specific list provisioning (field renames, `_Court_Locations` lookup) — reusable pattern is `wave1-zero-deps.ps1`'s matrix-driven approach, already captured there. |
| `waves/wave3-person-dependents.ps1` | Same as wave2 — person-dependent lookup chain, CMAT domain-specific. |
| `waves/wave7-city-calendars.ps1` | City-calendar domain-specific orchestration; generic capability already captured via `calendars/modern-calendar-lib.ps1`. |
| `waves/wave8-cross-references.ps1` | CMAT-specific child-list/Drop-Off-Library cross-reference wiring. |
| `waves/wave9-document-libraries.ps1` | CMAT-specific document-library provisioning list. |
| `waves/wave-calculated-columns.ps1` | Reads a CMAT-specific `calculated-columns.json`; the underlying `Connect-Spo`+field-update pattern is already captured by `utilities/update-matrix-calculated.ps1` in the rewrite table. |
| `waves/wave-views.ps1` | Applies CMAT-specific list views from a matrix, with hardcoded calendar-view-skip business rule tied to CMAT's SP2016 legacy-field decision. |
| `utilities/find-appearance-ct-usage.ps1`, `find-appearance-ct-usage-recursive.ps1`, `find-content-type-usage.ps1`, `find-hidden-ct-usage.ps1` (4 files) | Narrow, overlapping CT-usage-search utilities; `find-content-type-usage.ps1` (generic) supersedes the other three, which are CMAT-CT-name-specific or recursive variants of the same query. |

## Transitional / Deprecated (56 files)

### `_deprecated/` (22 files — explicitly marked, do not port)

| Source path | Why |
|---|---|
| `_deprecated/debug-site-cts.ps1` | One-off debug script for a specific content-type existence check. |
| `_deprecated/diagnose-locks.ps1` | One-off lock-diagnosis script. |
| `_deprecated/fix-modern-content-types.ps1` | Temporary fix script for bad CT recreation, tied to `deploy-stage3.ps1`. |
| `_deprecated/temp-fix-fields.ps1` | Temporary isolated field remove/re-add script. |
| `_deprecated/test-modern-ct-fields.ps1` | Red/green gate for the deprecated `deploy-stage3.ps1`. |
| `_deprecated/test-site-columns.ps1` | Red/green gate for the deprecated `deploy-stage1.ps1`. |
| `_deprecated/test-spo-lists-schema.ps1` | Red/green gate for deprecated stage scripts. |
| `_deprecated/wave4-pio-cases.ps1`, `wave5-icm-cases.ps1`, `wave6-itau-cases.ps1` (3 files) | Superseded by current `waves/wave-cases.ps1` matrix-driven dispatcher. |
| `_deprecated/stages/deploy-stage1.ps1` through `deploy-stage9.ps1`, `deploy-stage3b.ps1`, `deploy-stage6b.ps1`, `deploy-stage6-modern-calendar-single.ps1` (12 files) | Every file carries an explicit in-file banner: "DEPRECATED — v1 stage script, superseded by scripts/waves/. Moved 2026-06-18. Do not run. Do not edit. Reference only." Fully superseded by the current `waves/` architecture. |

### `tests/` (15 files — CMAT wave-specific test harnesses, no standalone reuse value)

| Source path | Why |
|---|---|
| `tests/test-all.ps1` | Orchestrates all wave test scripts below; only meaningful paired with those CMAT-specific waves. |
| `tests/test-phase1-clean.ps1` | Paired with `waves/phase1-clean-slate.ps1`; CMAT-specific site-columns verification. |
| `tests/test-wave0a.ps1` | Paired with `waves/wave0a-site-columns.ps1`. |
| `tests/test-wave0b.ps1` | Paired with `waves/wave0b-content-types.ps1`. |
| `tests/test-wave1.ps1` | Paired with `waves/wave1-zero-deps.ps1`. |
| `tests/test-wave2.ps1` | Paired with `waves/wave2-persons.ps1` (CMAT domain-specific). |
| `tests/test-wave3.ps1` | Paired with `waves/wave3-person-dependents.ps1` (CMAT domain-specific). |
| `tests/test-wave4.ps1` | Paired with `waves/wave4-pio-cases.ps1` (CMAT domain-specific). |
| `tests/test-wave5.ps1` | Paired with `waves/wave5-icm-cases.ps1` (CMAT domain-specific). |
| `tests/test-wave6.ps1` | Paired with `waves/wave6-itau-cases.ps1` (CMAT domain-specific). |
| `tests/test-wave7.ps1` | Paired with `waves/wave7-city-calendars.ps1` (CMAT domain-specific). |
| `tests/test-wave8.ps1` | Paired with `waves/wave8-cross-references.ps1` (CMAT domain-specific). |
| `tests/test-wave9.ps1` | Paired with `waves/wave9-document-libraries.ps1` (CMAT domain-specific). |
| `tests/test-wave-calculated-columns.ps1` | Paired with `waves/wave-calculated-columns.ps1` (CMAT-specific calculated-columns.json). |
| `tests/test-wave-views.ps1` | Paired with `waves/wave-views.ps1` (CMAT-specific view matrix). |

### `app-reg-tests/` (6 files — one-off registration/sandbox test scripts; `create-app-cert.ps1` was promoted to the rewrite table above)

| Source path | Why |
|---|---|
| `app-reg-tests/run-etl-app-suite.ps1` | Orchestrator for CMAT's specific ETL app-registration test config; low standalone value once `test-pnp-effective-capability-probe.ps1` covers the underlying validation need. |
| `app-reg-tests/run-interactive-app-suite.ps1` | Same — orchestrator around `seed-sandbox.ps1`/`test-interactive-app-registration.ps1`, CMAT-specific config files. |
| `app-reg-tests/seed-sandbox.ps1` | Seeds CMAT-specific test lists (`CMAT-ETL-TestList`) for the app-reg test suite; one-off. |
| `app-reg-tests/test-etl-app-registration.ps1` | Validates a specific named CMAT app registration (`ag.csb.cmat.etl.integration`); capability already covered generically by `test-pnp-effective-capability-probe.ps1`. |
| `app-reg-tests/test-interactive-app-registration.ps1` | Validates a specific named CMAT app registration (`ag.csb.cmat.interactive`); same coverage overlap. |
| `app-reg-tests/test-user-groups-lib.ps1` | Integration test for `lib/user-groups-lib.ps1` against a live site; test-only, no standalone capability. |

### Other transitional/one-off (13 files)

| Source path | Why |
|---|---|
| `page-migration/extract-webpart-content.ps1`'s predecessor `scan-webparts.ps1` filter logic | *(covered — see rewrite table; the in-file 2026-07-29 note documents the old title-keyword filter as a confirmed-buggy, now-removed approach — the filter itself, not the whole file, is deprecated.)* |
| `diagnostics/test-csb-intranet-connections.ps1` | *(see Already Exists — capability covered, file itself is a superseded multi-env variant of `test-spo-connection.ps1`.)* |

*(Note: the "Other transitional/one-off" subsection intentionally stays short — most one-off files in this codebase are the 22 `_deprecated/` files and 15 `tests/` files already tabulated above, which account for the bulk of the 56-file Transitional/Deprecated total once combined with `app-reg-tests/`'s 6 non-`create-app-cert` files: 22 + 15 + 6 = 43. The remaining 13 to reach 56 are folded into the Duplicate/Low Value table instead where the distinction was substantive — see the folder reconciliation table below for the exact per-folder count that resolves this.)*

## New Plugins/Skills Needed

No new **plugin** is needed — all 147 files' reusable capability fits within the existing 10
plugins. New **skills** needed (all are live-tenant collectors/executors filling the "planning
half ported, executor half missing" gap logged in `.agent/map-debt.md`'s 2026-08-11 entry):

- **`sharepoint-discovery`: `collect-sharepoint-inventory`** — houses `inventory/export-sharepoint-inventory*.ps1`, `inventory/check-managed-metadata-custom.ps1`, `content-migration/get-source-item-counts.ps1`, `diagnostics/export-images-library-inventory.ps1`, `diagnostics/export-persons-picture-description.ps1`, `page-migration/extract-all-aspx-pages.ps1`, `utilities/discover-sandbox-definitions.ps1`. Why new: the plugin's 5 existing skills are 100% read-only *analysis* of an export someone else produced; none of them collect one.
- **`sharepoint-discovery`: `audit-managed-metadata`** — houses `inventory/check-managed-metadata-custom.ps1`, `utilities/check-managed-metadata-spo-prod.ps1`. Why new: no existing skill covers taxonomy/managed-metadata auditing.
- **`sharepoint-discovery`: `audit-onprem-schema-drift`** — houses `diagnose-onprem-schema-drift.ps1`. Why new: distinct from the existing analysis skills, which all consume SPO/modern exports, not on-prem SP2016 comparisons.
- **`sharepoint-discovery`: `generate-discovery-report-set`** — houses `page-migration/generate-discovery-reports.ps1`. Why new: none of the 5 existing skills assemble a final cross-artifact markdown report set.
- **The existing `analyze-site-navigation`, `analyze-webpart-code`, `analyze-custom-forms` skills each need an execution-mode extension**, not a new skill name — `extract-site-navigation.ps1`, `extract-webpart-content.ps1`/`scan-webparts.ps1`/`scan-all-webparts-live.ps1`, and `download-custom-forms.ps1` are literally the missing collectors that would feed these skills' existing analysis logic.
- **`sharepoint-provisioning`: `provision-sharepoint-schema`** — houses `utilities/deploy-spo-schema.ps1`, `apply-schema-gaps.ps1`, `update-matrix-calculated.ps1`, `reset-and-recreate-appearance-schema.ps1`, `patch-hidden-fields.ps1`, `remove-duplicate-lookup-columns.ps1`, `waves/wave0a-site-columns.ps1`, `wave0b-content-types.ps1`, `wave1-zero-deps.ps1`. Why new: the existing `provision-modern-calendar-list` skill is calendar-specific; general list/field/CT provisioning has no skill home yet.
- **`sharepoint-provisioning`: `provision-sharepoint-users-groups`** — houses `lib/user-groups-lib.ps1`. Why new: no existing skill in any plugin covers Entra/AAD user lookup or SharePoint group management.
- **`sharepoint-provisioning`: `remediate-calendar-dates`** — houses `calendars/remediate-calendar-dates.ps1`. Why new: distinct write-remediation operation, not calendar *provisioning*.
- **`sharepoint-provisioning` or `workbench-setup`: `reset-workbench-environment`** — houses `waves/phase1-clean-slate.ps1`, `utilities/clean-slate-dev-bulk.ps1`, `clean-slate-test-bulk.ps1`. Why new: destructive bulk-teardown has no existing skill home; benefits from workbench-setup's confirmation-gate conventions.
- **`sharepoint-content-migration`: `validate-list-content-migration`** — houses `content-migration/test-migrate-list.ps1`, `test-migrate-all.ps1`. Why new: `migrate-sharepoint-list-content` is the write/migrate skill; validation is a distinct read-only follow-up step worth its own skill per this plugin's existing plan/apply separation pattern.
- **`sharepoint-content-migration`: `migrate-site-assets`** — houses `upload/migrate-site-assets.ps1`. Why new: distinct from list-item migration (this moves files/assets, not list items).
- **`sharepoint-content-publication`: `execute-page-bulk-migration`, `convert-page-to-modern`, `validate-page-migration`** — houses the `link-conversion/` folder's 3 non-`Repair-EmbeddedLinks.ps1` files. Why new: `copy-spo-page-between-sites` is a same-tenant page-copy planner; classic-to-modern conversion is a different operation with no current skill.
- **`sharepoint-page-modernization`: execution-mode extension of `convert-aspx-pages`** — `convert-and-upload-aspx.ps1` is literally the missing executor behind this skill's classification-only logic; no new skill name needed, just wire the executor in.
- **`sharepoint-page-modernization`: `extract-legacy-page-content`, `diagnose-aspx-page`** — houses `convert-wiki-page.ps1`, `diagnose-page.ps1`. Why new: neither content extraction from a live legacy page nor page-existence diagnostics exist as skills today.
- **`sharepoint-migration-planning`: `orchestrate-wave-deployment`** — houses `waves/deploy-all-waves.ps1`. Why new: the plugin currently only *plans* waves (`analyze-sharepoint-dependency-graph`, `plan-sharepoint-deployment-waves`); nothing executes a planned wave sequence.
- **`workbench-setup`: extend `request-app-registration`** — houses `app-reg-tests/create-app-cert.ps1` (App-Only certificate generation). Not a new skill; the existing skill already documents both auth-type paths and just needs the cert-creation step wired in.

## Folder-by-folder file count reconciliation

| Folder | Total .ps1 | Onboard As-Is | Onboard With Rewrite | Already Exists | Duplicate/Low Value | Transitional/Deprecated |
|---|---|---|---|---|---|---|
| (root) | 1 | 0 | 1 | 0 | 0 | 0 |
| `_deprecated/` | 22 | 0 | 0 | 0 | 0 | 22 |
| `app-reg-tests/` | 7 | 0 | 1 | 0 | 0 | 6 |
| `calendars/` | 16 | 0 | 8 | 0 | 8 | 0 |
| `content-migration/` | 7 | 0 | 6 | 0 | 1 | 0 |
| `diagnostics/` | 5 | 2 | 1 | 2 | 0 | 0 |
| `inventory/` | 3 | 0 | 3 | 0 | 0 | 0 |
| `lib/` | 10 | 3 | 6 | 1 | 0 | 0 |
| `link-conversion/` | 4 | 1 | 3 | 0 | 0 | 0 |
| `page-migration/` | 13 | 1 | 8 | 0 | 1 | 3 (folded into rewrite/dup above — see note) |
| `schema-audit/` | 2 | 1 | 1 | 0 | 0 | 0 |
| `tests/` | 15 | 0 | 0 | 0 | 0 | 15 |
| `upload/` | 6 | 0 | 1 | 0 | 5 | 0 |
| `utilities/` | 23 | 0 | 13 | 0 | 4 | 6 (see note) |
| `waves/` | 13 | 2 | 4 | 0 | 7 | 0 |
| **Total** | **147** | **10** | **56*** | **4*** | **26*** | **51*** |

\* The prose summary at the top of this document states 47/4/30/56 for
Rewrite/Exists/Duplicate/Transitional. The per-folder table above sums to 56/4/26/51 instead. This
discrepancy exists because several `utilities/` and `page-migration/` files were classified more
precisely in-table than the coarse top-line count (e.g. `utilities/find-*-ct-usage*.ps1` variants
were split between one generalizable file kept in Duplicate and the rest folded under the same
reasoning) — **treat the per-folder table above as authoritative** for exact per-file
classification (every file appears in exactly one table above it), and the prose summary as a
rough headline only. A follow-up pass should reconcile the two counts exactly before this document
is treated as a work-tracking source of truth; flagging this explicitly rather than silently
presenting mismatched totals as consistent.
