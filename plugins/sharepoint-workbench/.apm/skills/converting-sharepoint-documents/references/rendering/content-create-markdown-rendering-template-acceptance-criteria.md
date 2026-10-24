# Acceptance Criteria: content-create-markdown-rendering-template

- Skill slug: `content-create-markdown-rendering-template`.
- Target plugin: `sharepoint-document-conversion`.
- Purpose: Instantiates a new local Markdown rendering (page-structure) template file on disk from the plugin's canonical generic or standard-manual starter, with heading, body and media placeholders. Use when you need a new page layout template for Markdown output. Not an agent or native-skill instruction template.

## Constraints honored

- This is a rendering (page layout) template. Never mix it with the agent or native-skill template system.
- Only the `generic` and `standard-manual` profiles exist; an unknown `profile` or `fmt` raises `UnknownTemplateProfileError` or `UnknownTemplateFormatError`.
- Placeholders are limited to `{{title}}`, `{{body}}` and `{{media_dir}}`.
- Python standard library only. Run from this skill's root with `scripts/` on `sys.path`.

## Verification passes

- Confirm both the template file and its `.meta.json` sidecar exist, then validate the template.
- Focused plugin tests for this skill pass.
