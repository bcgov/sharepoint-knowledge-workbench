# Acceptance Criteria: content-render-sharepoint-pages

- Skill slug: `content-render-sharepoint-pages`.
- Target plugin: `sharepoint-document-conversion`.
- Purpose: Renders an accepted structured content package into SharePoint modern-page-ready artifacts (an HTML fragment per chunk plus a page-manifest.json) for the confirmed Add-PnPPage and Add-PnPPageTextPart route. Use when preparing content for SharePoint publication. Does not upload to SharePoint, does not attempt raw .aspx upload (confirmed Access denied), and does not extract source documents or determine topic boundaries.

## Constraints honored

- Zero SharePoint tenant I/O. Never upload, and never produce a raw `.aspx` file for direct upload: that is a confirmed `Access denied` platform boundary. Uploading belongs to `sharepoint-plan-page-publication`.
- Consume only an already-loaded `CanonicalPackage` from an accepted package.
- A pandoc failure raises `PandocConversionError`; never return a partial render.
- `pandoc` must be on `PATH`. Run from this skill's root with `scripts/` on `sys.path`.

## Verification passes

- Confirm `page-manifest.json` lists every chunk in order and each referenced HTML fragment exists. Run the validation skill before treating the render as accepted.
- Focused plugin tests for this skill pass.
