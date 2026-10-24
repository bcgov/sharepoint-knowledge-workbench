# Acceptance Criteria: sharepoint-plan-page-publication

- Skill slug: `sharepoint-plan-page-publication`.
- Target plugin: `sharepoint-site-build-and-publish`.
- Purpose: Builds a human-actionable publish plan (a PublishPlan) for rendered content as SharePoint modern pages. Use after rendering, before uploading. Performs no tenant writes and never attempts raw .aspx upload (blocked); execution belongs to sharepoint-apply-page-publication-plan.

## Constraints honored

- Zero tenant I/O. This skill only builds the plan.
- Never plan or attempt raw `.aspx` file upload: it is confirmed `Access denied`. The only working mechanism is the modern-page API (`Add-PnPPage` / `Add-PnPPageTextPart` / `Publish-PnPPage`).
- The input is the `content-render-sharepoint-pages` output directory: `page-manifest.json` (schema 1.0) plus the HTML fragments it lists. Refuse a missing directory, a missing or unsupported manifest, an empty page list, duplicate page identities, paths outside the directory, missing or unlisted fragments. Markdown renderer output is not page content: publish it with `sharepoint-publish-markdown-files` instead.
- Page order is the manifest order; each page's identity is its `chunk_id` (`<chunk_id>.aspx`). Media a fragment references is recorded per action (`media_refs`) but not uploaded or rewritten by this skill or by the executor: do that before publishing.
- Run from this skill's root with `scripts/` on `sys.path`.

## Verification passes

- Confirm the plan lists every page in the manifest, in manifest order, with its HTML fragment and target page name, and that nothing was written to a tenant. The older `build_aspx_publish_plan` (Markdown files to page names) is kept for compatibility, is tagged `source_format: markdown`, and is refused by the HTML executor.
- Focused plugin tests for this skill pass.
