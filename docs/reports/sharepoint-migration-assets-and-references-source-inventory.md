# SharePoint Migration assets/, references/, and top-level tests/ Source Inventory

Source: `jag-csb-cmat-sharepoint-online/plugins/sharepoint-migration/` — `assets/templates/` (17
files), `references/` (14 files), top-level `tests/` (3 real `.py` files). Companion to the
separately-audited `scripts/*.ps1` (147 files) and `skills/`+`agents/` inventories.

**Summary:** Of 34 files, 9 `assets/templates/` markdown report templates are genuinely
placeholder-driven and reusable (`{{SITE_NAME}}`, `{{DATE}}`, `{SiteUrl}`, etc.) — no destination
plugin equivalent exists for any of them today. 1 asset (`webpart-migration-rules.json`) is
confirmed byte-identical to content already ported. 7 `assets/templates/` files are CMAT
production data (real column GUIDs, real choice values, real content-type field maps) and not
portable as-is. Of 14 `references/`, most are CMAT-project-specific runbooks/decision records;
2–3 contain generalizable methodology worth adapting. All 3 top-level tests exercise
scripts/modules already covered by the separate scripts/skills audits — none need separate
porting action; `test_spo_page_copy_plan.py` tests a **Python** `spo_page_copy_plan.py` that the
destination repo has already superseded with a PowerShell rewrite (`spo-page-copy-plan.ps1`, per
current git status in this repo: the old `.py` script/skill/test trio was deleted in favor of a
`.ps1`), so this specific Python test is stale relative to destination and not worth porting.

## webpart-migration-rules.json — verified

`diff` between source
`jag-csb-cmat-sharepoint-online/plugins/sharepoint-migration/assets/templates/webpart-migration-rules.json`
and destination
`sharepoint-knowledge-workbench/plugins/sharepoint-discovery/assets/webpart-migration-rules.json`
produced **zero output / exit code 0** — the files are byte-identical, not just same-named.
CONFIRMED_ALREADY_PORTED. (Also present in `sharepoint-discovery/scripts/assets/` and
`sharepoint-page-modernization/scripts/assets/`, per the task brief.)

## assets/templates/ (17 files)

| File | Type | Already in workbench? | Classification | Target plugin |
|---|---|---|---|---|
| `webpart-migration-rules.json` | rules/config | YES — byte-identical, verified via diff | CONFIRMED_ALREADY_PORTED | n/a |
| `ALL-UNIQUE-LINKS-FOR-REVIEW-template.md` | template (`{{SITE_NAME}}`, `{{DATE}}`, `{{TOTAL_LINKS}}` placeholders) | No | REUSABLE_TEMPLATE_ONBOARD | `sharepoint-link-remediation` |
| `ALL-UNIQUE-WEBPART-CODE-FOR-REVIEW-template.md` | template (placeholders) | No | REUSABLE_TEMPLATE_ONBOARD | `sharepoint-page-modernization` |
| `CUSTOM-FORMS-INVENTORY-REPORT-template.md` | template (placeholders) | No | REUSABLE_TEMPLATE_ONBOARD | `sharepoint-page-modernization` |
| `LEGACY-LINK-INVENTORY-REPORT-template.md` | template (placeholders) | No | REUSABLE_TEMPLATE_ONBOARD | `sharepoint-link-remediation` |
| `MASTER-DISCOVERY-META-REVIEW-template.md` | template (placeholders) | No | REUSABLE_TEMPLATE_ONBOARD | `sharepoint-discovery` |
| `SITE-NAVIGATION-CHROME-SUMMARY-template.md` | template (placeholders) | No | REUSABLE_TEMPLATE_ONBOARD | `sharepoint-discovery` |
| `SPO-GROUP-PROVISIONING-CHECKLIST-template.md` | template (`{SiteName}`, `{PermissionsJsonPath}` placeholders) | No | REUSABLE_TEMPLATE_ONBOARD | `sharepoint-provisioning` |
| `unique-permissions-exception-report-template.md` | template (`{SiteName}`, `{SiteUrl}` placeholders) | No | REUSABLE_TEMPLATE_ONBOARD | `sharepoint-provisioning` |
| `Briefings.json` | CMAT list schema (real "Briefings" list fields, real internal-name GUIDs) | No | PROJECT_SPECIFIC_DATA_NOT_PORTABLE | n/a — not a template, no placeholder skeleton to extract without inventing one speculatively |
| `calculated-columns.json` | real calculated-column formulas for `All_Appearances` etc. | No | PROJECT_SPECIFIC_DATA_NOT_PORTABLE | n/a |
| `calendar-name-overrides.json` | near-empty (`{}`) override file, CMAT-scoped but trivial | No | PROJECT_SPECIFIC_DATA_NOT_PORTABLE | n/a — too thin to generalize into a template |
| `choices-extraction-report.txt` | real scraped choice-field values from CMAT tenant (2423 lines) | No | PROJECT_SPECIFIC_DATA_NOT_PORTABLE | n/a |
| `choices-overrides.json` | real choice-field override values for CMAT lists | No | PROJECT_SPECIFIC_DATA_NOT_PORTABLE | n/a |
| `content-migration-manifest.json` | real CMAT list/library migration manifest with live prod item counts | No | PROJECT_SPECIFIC_DATA_NOT_PORTABLE | `sharepoint-content-migration` could use an empty-manifest placeholder/schema doc, but this file itself is CMAT data |
| `Modern_Manual_Appearances.json` | real CMAT content-type field map | No | PROJECT_SPECIFIC_DATA_NOT_PORTABLE | n/a |
| `Modern_Scheduled_Appearances.json` | real CMAT content-type field map | No | PROJECT_SPECIFIC_DATA_NOT_PORTABLE | n/a |
| `site-columns.json` | real SPO site-column export derived from CMAT prod | No | PROJECT_SPECIFIC_DATA_NOT_PORTABLE | n/a |

## references/ (14 files)

| File | Content summary | Classification | Target plugin (if onboard-worthy) |
|---|---|---|---|
| `appearance-field-mapping.md` | SP2016→SPO field mapping specific to CMAT's `All_Appearances`/`ITAU_Cal_*` lists | PROJECT_SPECIFIC_NOT_PORTABLE | n/a |
| `ASPX-MODERNIZATION-STRATEGY.md` | Generic-shaped framework for deciding OOB vs. SPFx modernization path per web part group | REFERENCE_DOC_ONBOARD (strip CMAT specifics) | `sharepoint-page-modernization` |
| `CALENDAR-OVERLAY-MIGRATION-DECISION.md` | CMAT's specific calendar-overlay decision record (UI-driven setup, approved 2026-07-20) | PROJECT_SPECIFIC_NOT_PORTABLE | n/a |
| `CONTENT-MIGRATION-GUIDE.md` | CMAT-specific run order tied to CMAT's own wave scripts/`test-all.ps1` | PROJECT_SPECIFIC_NOT_PORTABLE | destination's `sharepoint-content-migration` may want its own generic version of this checklist shape, but this file's content is CMAT-bound |
| `CSBC-FOLLOW-UP-CUSTOM-SCRIPT-DENIAL.md` | Real government service-request denial letter re: CMAT's own tenant custom-script setting | PROJECT_SPECIFIC_NOT_PORTABLE | n/a |
| `CSBC-SERVICE-REQUEST-CUSTOM-SCRIPT-ENABLEMENT.md` | Real service-request submission for CMAT's specific SPO site | PROJECT_SPECIFIC_NOT_PORTABLE | n/a |
| `DEPLOYMENT-GUIDE.md` | CMAT-specific v2 wave deployment guide, references CMAT's own matrix file | PROJECT_SPECIFIC_NOT_PORTABLE | n/a |
| `document-sets-feature-gap.md` | Note about enabling Document Sets on CMAT's specific DEV site | PROJECT_SPECIFIC_NOT_PORTABLE | n/a (the underlying "Document Sets feature must be pre-enabled before Wave 0b" gotcha is generic knowledge, but this doc as written is CMAT-scoped) |
| `refactor-plan-schema-driven.md` | Plan to replace CMAT's hardcoded wave scripts with matrix-driven deploy engine; references a local OneDrive path | PROJECT_SPECIFIC_NOT_PORTABLE | n/a |
| `schema-variances.md` | Real SP2016→SPO schema variance log for CMAT's content types/columns | PROJECT_SPECIFIC_NOT_PORTABLE | n/a |
| `self-evolution-profile.md` | CMAT plugin's own self-evolution allowed-edit-directories config | PROJECT_SPECIFIC_NOT_PORTABLE | n/a — this repo has its own `.agent/rules/self-evolution-policy.md`, doesn't need this file |
| `wave-dependency-matrix.json` | Real CMAT wave/object dependency data (list names, field exclusions) | PROJECT_SPECIFIC_DATA_NOT_PORTABLE | n/a |
| `wave-scripts-to-run.md` | CMAT-specific wave run order/orchestrator pointer | PROJECT_SPECIFIC_NOT_PORTABLE | n/a |
| `webpart-analysis-runbook.md` | 4-stage generic-shaped pipeline description (discover→extract→group→analyze ASPX/web parts) | REFERENCE_DOC_ONBOARD (strip CMAT specifics) | `sharepoint-page-modernization` |

## Top-level tests/ (3 files)

| File | What it tests | Already covered? |
|---|---|---|
| `test_analyze_persons_images_gap.py` | `scripts/diagnostics/analyze-persons-images-gap.py` — CMAT-specific "Persons" list image-path gap analysis | Not applicable to destination — CMAT-data-specific diagnostic, no destination equivalent script exists or is needed |
| `test_fix_persons_image_paths_script.py` | Asserts static text/params (`-UseCertificateAuth`, `-ETLClientId`, etc.) exist in `scripts/content-migration/fix-persons-image-paths.ps1`, a CMAT-specific "Persons" list fixer | Not applicable — CMAT-data-specific script, no destination equivalent |
| `test_spo_page_copy_plan.py` | Python `spo_page_copy_plan.py` (`build_copy_page_plan`) — generic tenant-safe SPO page-copy planning logic | YES, superseded — destination `sharepoint-content-publication` plugin's git status shows the old `.py` script/skill/test trio deleted in favor of `spo-page-copy-plan.ps1` (already committed as untracked new files this session); this Python test is stale relative to that rewrite |

## Priority findings

- `webpart-migration-rules.json` is confirmed byte-identical (diff exit 0) to destination copies — no action needed, prior "already ported" claim holds.
- 9 of 17 `assets/templates/` files are genuine placeholder-driven report templates with **no destination equivalent at all** — this is the clearest near-term gap: `sharepoint-discovery`, `sharepoint-link-remediation`, `sharepoint-page-modernization`, and `sharepoint-provisioning` each currently lack template(s) for reports their own scripts likely already generate data for.
- The remaining 7 `assets/templates/` files and nearly all 14 `references/` files are CMAT production data or CMAT-specific runbooks/decision records (real column GUIDs, real service-request letters, real wave dependency data) — correctly excluded from porting; only `ASPX-MODERNIZATION-STRATEGY.md` and `webpart-analysis-runbook.md` contain generalizable methodology worth adapting into `sharepoint-page-modernization` references.
- All 3 top-level `tests/` files are either CMAT-data-specific (2 files, no destination action needed) or already superseded by this session's own `.py`→`.ps1` rewrite of `spo-page-copy-plan` (1 file) — no test-porting action required for this category.
- Net result: of 34 files audited, roughly 11 are reasonable onboarding candidates (9 templates + 2 reference docs), 1 is confirmed already ported, and 22 are correctly project-specific and should stay in the source repo.
