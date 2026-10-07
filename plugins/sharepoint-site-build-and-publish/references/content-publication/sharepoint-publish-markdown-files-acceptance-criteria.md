# Acceptance Criteria: sharepoint-publish-markdown-files

- Skill slug: `sharepoint-publish-markdown-files`.
- Target plugin: `sharepoint-site-build-and-publish`.
- Purpose: Builds a human-actionable publish plan mapping rendered Markdown and media files to an exact SharePoint library and folder, then a real PnP executor uploads it with Add-PnPFile and checkout/checkin discipline. Use to publish rendered Markdown output to a document library. Dry-run by default.

## Constraints honored

- Planning performs zero tenant I/O. The executor `scripts/spo-publish-markdown-plan.ps1` is dry-run by default and writes nothing without `-Execute -ConfirmToken PUBLISH-SPO-MARKDOWN`. A real run is a live tenant write that the user runs.
- Overwriting an existing file uses `Set-PnPFileCheckedOut` / `Set-PnPFileCheckedIn -CheckinType MajorCheckIn` around `Add-PnPFile`.
- Require an explicit target library and folder; there is no default target. Refuse a missing or empty source directory.
- When running from an installed copy, pass `-ConfigPath` (or `-SiteUrl`, `-ClientId`, `-TenantId`); the default config path does not resolve there.

## Verification passes

- Confirm the dry run lists every expected source-to-target mapping. After a real run, validate with `sharepoint-validate-publication`; roll back with `sharepoint-remove-publication` if needed.
- Focused plugin tests for this skill pass.
