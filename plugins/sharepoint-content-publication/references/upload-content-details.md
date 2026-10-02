# Upload content: execution paths and scope

## Contents

- [Two execution paths](#two-execution-paths)
- [Real executor](#real-executor)
- [Scope and what it is not](#scope-and-what-it-is-not)

## Two execution paths

1. `sharepoint_upload.py::upload_pages(plan, uploader)`: a Python plan-execution loop that requires an injected
   `uploader(action) -> UploadResult` callable. It has zero tenant I/O of its own and raises `NotImplementedError` without one.
   It stops on the first failed action rather than reporting partial success as full success.
2. `scripts/spo-upload-plan.ps1`: a real PowerShell executor that reads a `PublishPlan` JSON file directly and creates and
   publishes each page, gated behind `-Execute -ConfirmToken UPLOAD-SPO-PLAN`.

The PowerShell script is not wired in as `upload_pages`' injected `uploader`: Python cannot call a PowerShell script as an
in-process callback, so the two paths are used independently.

## Real executor

`spo-upload-plan.ps1` reads a `PublishPlan.to_dict()`-shaped JSON file and, per action, creates a modern page with
`Add-PnPPage`, injects the `source_path` file's content with `Add-PnPPageTextPart`, and publishes with `Publish-PnPPage`. Dry
run by default.

```bash
pwsh -File scripts/spo-upload-plan.ps1 -PlanPath plan.json -SiteUrl "https://tenant.sharepoint.com/sites/Test" -Execute -ConfirmToken UPLOAD-SPO-PLAN
```

## Scope and what it is not

Page creation from pre-rendered HTML only: `source_path` should point at an HTML fragment file, matching the
`content-render-sharepoint-aspx` skill's output. Uploading raw files and assets to a document library (`Add-PnPFile` with
checkout and checkin discipline) is `sharepoint-publish-markdown-to-sharepoint`'s executor, `spo-publish-markdown-plan.ps1`.
