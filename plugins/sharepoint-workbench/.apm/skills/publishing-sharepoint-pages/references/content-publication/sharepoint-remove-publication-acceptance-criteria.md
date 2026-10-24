# Acceptance Criteria: sharepoint-remove-publication

- Skill slug: `sharepoint-remove-publication`.
- Target plugin: `sharepoint-site-build-and-publish`.
- Purpose: Builds a rollback plan reversing a prior publication's exact actions, scoped to one document, then a real PnP executor removes each target (Remove-PnPPage or Remove-PnPFile) with fail-loud removal verification. Use to undo a publication. Dry-run by default.

## Constraints honored

- Package-scoped: only reverse the named `document_id`'s own actions. A `document_id` that does not match the supplied plan's own raises `PlanError`; never roll back the wrong document.
- Planning performs zero tenant I/O. The executor `scripts/spo-rollback-publication.ps1` is dry-run by default and deletes nothing without `-Execute -ConfirmToken ROLLBACK-SPO-PLAN`. A real run is a destructive live tenant write that the user runs.
- Verify each removal. The executor throws if a target is still present afterwards; never report an unverified delete as success.
- When running from an installed copy, pass `-ConfigPath` (or `-SiteUrl`, `-ClientId`, `-TenantId`).

## Verification passes

- Confirm the dry run lists exactly the targets the original plan created, then that every target reports absent after the real run.
- Focused plugin tests for this skill pass.
