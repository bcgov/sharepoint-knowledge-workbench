# Rendering template profiles

## Contents

- [What a rendering template is](#what-a-rendering-template-is)
- [Profiles](#profiles)
- [Files and placeholders](#files-and-placeholders)
- [Validation rules](#validation-rules)
- [Errors](#errors)

## What a rendering template is

A rendering template defines page and document layout: headings, body, metadata placement and media
placement. It is distinct from the agent and native-skill template system (agent instructions, answer
formatting). The two are never merged.

## Profiles

- `generic`: the plugin's default page shape.
- `standard-manual`: the standard-manual variant.
  - Markdown: a level-2 heading directly followed by body content, no front matter, structurally
    confirmed against real rendered Standard Manual output.
  - ASPX: a heading followed directly by body content with no `<html>`, `<head>` or `<body>` wrapper,
    the shape `Add-PnPPageTextPart` consumes, confirmed by the Phase 3.0 tenant experiment. Raw wrapped
    `.aspx` upload to Site Pages is a confirmed `Access denied` platform boundary; this template family
    never produces that shape.

Formats are `markdown` and `aspx`.

## Files and placeholders

`create_rendering_template(profile, fmt, output_path)` writes `output_path` (the template text) and a
`<output_path>.meta.json` sidecar recording `schema_version`, `profile` and `format`. The sidecar lets
`load_rendering_template` and the validator recover them without re-parsing the body. It returns a
`RenderingTemplate(schema_version, profile, format, content, path)`.

Allowed placeholders are `{{title}}`, `{{body}}` and `{{media_dir}}`. `{{title}}` and `{{body}}` are
required.

## Validation rules

`validate_rendering_template(template)` returns `TemplateValidationReport(status="PASS"|"FAIL", issues=[...])`
and checks:

- known `profile` and `format`;
- the required placeholders are present;
- no unknown placeholder tokens (anything outside the three above);
- `{{title}}` sits inside a real heading construct (a markdown `#`-prefixed line, or an ASPX `<h1>` to
  `<h6>` tag), not a bare unheaded placeholder;
- ASPX only: no full-page `<html>`/`<head>`/`<body>` wrapper.

Every issue is `severity="error"`, so status is always `PASS` or `FAIL`, never `WARN`. This validates the
template definition, not rendered output.

## Errors

`create_rendering_template` raises `UnknownTemplateProfileError` or `UnknownTemplateFormatError` for an
unrecognized `profile` or `fmt`.
