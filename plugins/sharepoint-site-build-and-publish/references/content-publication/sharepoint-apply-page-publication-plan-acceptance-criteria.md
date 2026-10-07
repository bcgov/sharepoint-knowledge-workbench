# Acceptance Criteria: sharepoint-apply-page-publication-plan

- Skill slug: `sharepoint-apply-page-publication-plan`.
- Target plugin: `sharepoint-site-build-and-publish`.
- Purpose: Executes a PublishPlan (built by sharepoint-plan-page-publication or sharepoint-publish-markdown-files) either through an explicitly injected Python uploader or through a real PnP executor that creates and publishes modern pages. Use to carry out a page-publication plan. Zero tenant I/O by default.

## Constraints honored

- Zero tenant I/O unless the caller explicitly injects a real `uploader`. `upload_pages` raises `NotImplementedError` without one, and stops on the first failed action rather than reporting partial success.
- The real executor `scripts/spo-upload-plan.ps1` is dry-run by default and writes nothing without `-Execute -ConfirmToken UPLOAD-SPO-PLAN`. A real run is a live tenant write that the user runs.
- Never attempt raw `.aspx` upload (blocked). Create pages with `Add-PnPPage` / `Add-PnPPageTextPart` / `Publish-PnPPage`.
- Page creation from pre-rendered HTML fragments only (the `content-render-sharepoint-pages` skill's output, planned by `sharepoint-plan-page-publication`). The executor refuses a plan tagged `source_format: markdown`; a plan with no tag is accepted as before. File and asset upload to a library is `sharepoint-publish-markdown-files`'s job.
- When running from an installed copy, pass `-ConfigPath` (or `-SiteUrl`, `-ClientId`, `-TenantId`).

## Verification passes

- Confirm each planned page was created and published, then check with `sharepoint-validate-publication`.
- Focused plugin tests for this skill pass.
