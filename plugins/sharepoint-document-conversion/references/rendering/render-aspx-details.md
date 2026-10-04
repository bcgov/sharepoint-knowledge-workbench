# SharePoint ASPX rendering details

## Contents

- [Why fragments, not .aspx files](#why-fragments-not-aspx-files)
- [Interface](#interface)
- [Output layout](#output-layout)
- [Failure and dependencies](#failure-and-dependencies)

## Why fragments, not .aspx files

The renderer stages artifacts for SharePoint's supported modern-page creation API: one HTML fragment per
chunk (suitable for a single `Add-PnPPageTextPart` call), a `page-manifest.json` describing page order,
titles and media, and a local copy of the package's media.

It never uploads anything and never produces a raw `.aspx` file for direct upload. The Phase 3.0 tenant
experiment confirmed raw `.aspx` upload to Site Pages is `Access denied` (a platform boundary, not a
permissions gap), while `Add-PnPPage` plus `Add-PnPPageTextPart` with generated HTML pushed and rendered
correctly. Source-repository evidence only:
`docs/research/research-experimentation/tenant-discovery/field-note-sharepoint-write-capability-discovery.md`
section 15 and `tools/phase-3-sharepoint-discovery/push-aspx-experiment.ps1`.

Uploading the artifacts and calling the page-creation API is a separate, later skill
(`sharepoint-plan-page-publication` in `sharepoint-site-build-and-publish`). This skill performs zero
SharePoint tenant I/O.

## Interface

```python
from renderers.sharepoint_aspx import SharePointAspxRenderer, render_to_staging

renderer = SharePointAspxRenderer()
result = renderer.render(package, output_dir)
# RenderResult: {renderer_name: "sharepoint-aspx", ..., output_files: [...]}

# Or stage without promoting (mirrors content-render-markdown-pages):
result, staging_dir = render_to_staging(package, output_root)
```

- `package`: an already-loaded `CanonicalPackage` (the `sharepoint-document-conversion` plugin's
  `build_canonical_package` output, loaded with `canonical_package.CanonicalPackage.load()`).
- `output_dir`: the path under which the render is staged.

## Output layout

```
rendered-output/
  page-manifest.json   # ordered list of {chunk_id, title, html_file, media_refs}
  pages/
    <chunk_id>.html      # one HTML fragment per chunk
  media/
    <asset files>        # copied from the package's media
```

## Failure and dependencies

A failure (pandoc unavailable or erroring) raises `PandocConversionError` rather than returning a partial
render. `pandoc` must be on `PATH`; it converts each chunk's canonical Markdown to an HTML fragment. No
other dependency beyond the Python standard library.
