# Acceptance Criteria: content-create-sharepoint-rendering-template

- Skill slug: `content-create-sharepoint-rendering-template`.
- Target plugin: `sharepoint-document-conversion`.
- Purpose: Instantiates a new local SharePoint modern-page (ASPX) rendering (page-structure) template file on disk from the plugin's canonical generic or standard-manual starter, backed by the confirmed Add-PnPPage and Add-PnPPageTextPart fragment shape. Use when you need a new page layout template for SharePoint modern pages. Not an agent or native-skill instruction template, and never a raw wrapped .aspx page (confirmed Access denied).

## Constraints honored

- Produce a bare fragment: a heading followed by body, with no `<html>`, `<head>` or `<body>` wrapper. That is the shape `Add-PnPPageTextPart` consumes. Raw wrapped `.aspx` upload to Site Pages is a confirmed `Access denied` platform boundary and this skill never produces it.
- This is a rendering (page layout) template. Never mix it with the agent or native-skill template system.
- An unknown `profile` or `fmt` raises `UnknownTemplateProfileError` or `UnknownTemplateFormatError`.
- Python standard library only. Run from this skill's root with `scripts/` on `sys.path`.

## Verification passes

- Confirm the fragment and its `.meta.json` sidecar exist and that the fragment has no full-page wrapper tags.
- Focused plugin tests for this skill pass.
