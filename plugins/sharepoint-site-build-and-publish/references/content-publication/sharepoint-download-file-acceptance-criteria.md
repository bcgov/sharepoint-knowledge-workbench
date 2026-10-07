# Acceptance Criteria: sharepoint-download-file

- Skill slug: `sharepoint-download-file`.
- Target plugin: `sharepoint-site-build-and-publish`.
- Purpose: Use when downloading SharePoint Online or on-prem SP2016 files for inspection, offline analysis or migration. Supports one file, or bulk HTML/HTM/ASPX and selected document downloads from a recursive files.csv inventory, preserving source URLs and local paths for Python link extraction. Zero tenant writes; dry-run by default.

## Constraints honored

- Zero tenant writes: downloads content only; never modifies tenant state.
- Dry-run by default: running without `-Execute` validates connection configuration and prints the planned local destination path without downloading.
- Real execution requires `-Execute -ConfirmToken DOWNLOAD-SPO-FILE`.
- By default does not overwrite existing local files unless `-Overwrite` is passed.
- Requires PnP.PowerShell module with delegated/interactive or app-only authentication configured.
- Bulk route: `download-sharepoint-inventory-files.ps1 -InventoryCsv <files.csv> -ConfigPath <profile.psd1> -OutputDir <folder>`. Default extensions: `html,htm,aspx`; `-Extensions 'html,htm,aspx,docx,xlsx,pptx,pdf'` selects more formats.
- Bulk execution requires `-Execute -ConfirmToken DOWNLOAD-SHAREPOINT-INVENTORY-FILES`. Preview writes only `downloads.csv`; live calls are user-run. Online signs in interactively; on-prem prompts once (or accepts `-Credential`); bulk never uses default session credentials.
- Bulk preserves remote identity in `downloads.csv` and uses hash directories to prevent duplicate filenames colliding. On-prem `-RawFile` downloads stored bytes through REST. Downloaded `.aspx` files alone do not export modern-page stored fields.

## Verification passes

- Check local file arrival and size:
- Focused plugin tests for this skill pass.
