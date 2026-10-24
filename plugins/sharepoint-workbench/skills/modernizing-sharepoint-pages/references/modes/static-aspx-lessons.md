# Static ASPX migration: lessons from the pilot

Source: pilot `awards/criteria_processes.aspx` to DEV `Operations/Administration Documents/awards`.
Each item is something that went wrong or was wrong, and the rule that follows.

| # | Issue | Rule |
|---|---|---|
| 1 | `sharepoint-convert-legacy-aspx-to-html` dropped all 11 tables. | Convert by hand, preserving structure. Compare table, row, cell, list and link counts with the source. Never publish the converter output unchecked. |
| 2 | Tenant-level shared assets need a tenant admin and the CDN. | Shared assets are site-level: `SiteAssets/standard-design-system`. |
| 3 | Token CSS and a footer were not "aligned": the header and breadcrumb were missing. | Every page uses the full [page chrome](../bc-design-system-page-chrome.md). |
| 4 | The upload plan builder emits `\` and `/` mixed on Windows. | Normalize to `/` before running `spo-upload-file.ps1`. |
| 5 | `spo-provision-list.ps1` printed FAILED (`The property 'Count' cannot be found`) after creating the library. | Re-check the library with `Get-PnPList` before retrying. Upstream bug, to be fixed in `sharepoint-knowledge-workbench`. |
| 6 | `spo-upload-file.ps1` fails when overwriting: `Set-PnPFileCheckedOut -Url` rejects the site-relative path. | Upstream bug. The workaround used on DEV was one inline `Add-PnPFile` to the same target, after checking the config URL is DEV. Record every use. Never use it on TEST or PROD. |
| 7 | The library preview showed the page with no CSS (Times serif, no borders). | Open the file directly to adjudicator rendering. The viewer sandboxes pages (see `spfx/html/README.md`); if the CSS is stripped, inline the CSS and fonts (tokens, `@font-face` with absolute site URLs) so the page is self-contained. Whether linked same-site CSS is blocked was not isolated; the inlined page is the safe default. A POC page that rendered fine used only inline CSS. |
| 8 | Validator flagged chrome links as source-parity failures and a literal `#fff`. | Parity must exclude the header, breadcrumb and footer links. Use tokens for all colours. |
| 9 | Relative links (`../../../public/...`, `.doc`, `.pdf`, `.xls`) will 404 on DEV. | Classify with `sharepoint-extract-links` and get a disposition for each. Never guess. |
| 10 | The target folder was typed as `administrative documents`; the source library is `Administration Documents`. | Take the target folder from the inventory `LibraryTitle` (the ledger script does); never retype or paraphrase names. |

Run order that worked: download, convert, validate with
`scripts/validate_design_system_page.py`, verify assets, create the library and folder,
dry-run, upload, verify.
