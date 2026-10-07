# Acceptance Criteria: sharepoint-publish-html-page

- Skill slug: `sharepoint-publish-html-page`.
- Target plugin: `sharepoint-site-build-and-publish`.
- Purpose: Publishes an HTML page (.html) to a SharePoint Online document library or Site Pages library (SitePages/) with checkout/checkin discipline and post-upload presence verification. Supports native SharePoint HTML page rendering (M365 Roadmap ID 569208). Dry-run by default; real writes require -Execute and confirmation token PUBLISH-SPO-HTML.

## Constraints honored

- Dry-run by default: running without `-Execute` prints the target server-relative URL and upload plan without modifying tenant state.
- Real writes require `-Execute -ConfirmToken PUBLISH-SPO-HTML`.
- Enforces `.html` or `.htm` file extensions.
- Uses checkout/checkin discipline (`Set-PnPFileCheckedOut` / `Set-PnPFileCheckedIn -CheckinType MajorCheckIn`) when replacing existing files.
- Verifies post-upload presence and outputs the clean browser URL.

## Verification passes

- Check file presence via PnP.PowerShell:
- Focused plugin tests for this skill pass.
