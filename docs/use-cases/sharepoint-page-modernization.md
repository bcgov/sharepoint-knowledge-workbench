# Use Case: Classic-to-Modern Page Conversion

Analyze legacy classic SharePoint pages and convert them into modern-page conversion manifests,
with an offline preview of the result before anything touches a live tenant.

## When to use this

You have classic ASPX pages (web-part zones, classic layouts) that need to become modern
SharePoint pages, and you want a reviewable manifest — not a black-box automatic conversion.

## Workflow at a glance

Four stages, each a real script behind a skill:

1. `analyze-aspx-pages` — parses classic page content, classifies each web part's role/type/variant.
2. `convert-aspx-pages` — data-driven layout selection and component mapping to modern sections,
   with explicit gap notices for anything that can't be mapped automatically.
3. `compose-page-preview` — composes an offline chrome+content preview of the converted result, so
   you can review before publishing.

## Full detail

[`plugins/sharepoint-page-modernization/README.md`](../../plugins/sharepoint-page-modernization/README.md)
