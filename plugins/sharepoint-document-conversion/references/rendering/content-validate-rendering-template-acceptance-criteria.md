# Acceptance Criteria: content-validate-rendering-template

- Skill slug: `content-validate-rendering-template`.
- Target plugin: `sharepoint-document-conversion`.
- Purpose: Validates a RenderingTemplate (from the Markdown or ASPX template-creation skills) for schema, placeholder, required-section and format-profile correctness. Use before relying on a template. Checks the template definition itself, not rendered output, which content-validate-rendered-output handles.

## Constraints honored

- Validate the template definition only. Rendered-output checks (broken links, missing pages, stale source hash) belong to `content-validate-rendered-output`.
- Status is always `PASS` or `FAIL`, never `WARN`; every issue is an error.
- ASPX templates must be bare fragments: a full-page `<html>`/`<head>`/`<body>` wrapper fails validation.
- Python standard library only. Run from this skill's root with `scripts/` on `sys.path`.

## Verification passes

- Status must be `PASS`. A `FAIL` lists the cause: unknown profile or format, a missing required placeholder, an unknown placeholder, `{{title}}` outside a heading construct, or an ASPX wrapper tag.
- Focused plugin tests for this skill pass.
