---
name: upload-content
description: Executes a PublishPlan (built by publish-aspx-to-sharepoint or publish-markdown-to-sharepoint) via an explicitly injected uploader -- zero SharePoint tenant I/O by default, matching this plugin's Phase 3 package-only architecture.
---

# upload-content

## Purpose

Executes a `PublishPlan`'s actions -- created a modern page or uploaded a
site asset per action -- via an injected `uploader` callable. This is the
execution primitive that would consume `publish-aspx-to-sharepoint`'s or
`publish-markdown-to-sharepoint`'s plans once Stage 3.4.3 (approved-write-
identity) authorizes real tenant writes; today it still requires an explicit
`uploader` to be supplied by the caller and raises `NotImplementedError`
without one, so no autonomous production tenant write is introduced by
adding this skill.

## Real platform constraint recorded

Same confirmed mechanism as `publish-aspx-to-sharepoint`'s SKILL.md: the
`Add-PnPPage`/`Add-PnPPageTextPart`/`Publish-PnPPage` modern-page-creation
call pattern is the only confirmed-working mechanism on this tenant (raw
`.aspx` upload is blocked). Any real `uploader` a caller injects should
follow that pattern (or the equivalent SharePoint REST calls), not attempt
raw file upload.

## Input boundaries

- A `PublishPlan` (from `sharepoint_publish_plan.py`).
- An `uploader(action) -> UploadResult` callable, supplied by the caller.
  Without one, `upload_pages()` raises `NotImplementedError` -- this module
  ships no live PnP/REST client itself.

## Prohibited scope

- Zero tenant I/O unless the caller explicitly injects a real `uploader`.
- Stops on the first failed action rather than reporting partial success as
  full success.

## Scripts

- `../../scripts/sharepoint_upload.py` (`upload_pages`, `UploadResult`, `UploadError`)

## Tests

- `../../tests/unit/test_sharepoint_upload.py`

## Provenance

Extracted from the CMAT repository's `sp-uploading-content` skill
(`scripts/upload/upload-modern-page.ps1`,
`scripts/upload/upload-modern-page-rest.ps1`) -- see
`docs/reports/phase-9-reusable-sharepoint-plugin-extraction/provenance.md`
for the full source-to-destination record.
