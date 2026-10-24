# Acceptance Criteria: sharepoint-validate-publication

- Skill slug: `sharepoint-validate-publication`.
- Target plugin: `sharepoint-site-build-and-publish`.
- Purpose: Offline pre-upload schema validation of an UploadPackage against the target library schema, plus a read-only post-deployment presence check (Get-PnPPage or Get-PnPFile) confirming that a PublishPlan's targets landed on the tenant. Use before uploading and again after publishing.

## Constraints honored

- Pre-upload validation is entirely offline (`validate_upload_package`), with zero tenant I/O.
- The post-deployment check is read-only and always live: it never writes, so it has no `-Execute` or token. It checks presence only, not field-level content (use `sharepoint-compare-publication-state` for identity-field reconciliation).
- When running from an installed copy, pass `-ConfigPath` (or `-SiteUrl`, `-ClientId`, `-TenantId`).
- Run Python from this skill's root with `scripts/` on `sys.path`.

## Verification passes

- The offline report has no blocking issues; the post-deployment run reports `OBSERVED` for every target and an overall `PASS`. An `EMPTY` target means it is not on the tenant.
- Focused plugin tests for this skill pass.
