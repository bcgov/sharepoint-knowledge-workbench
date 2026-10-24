# Acceptance Criteria: content-validate-rendered-output

- Skill slug: `content-validate-rendered-output`.
- Target plugin: `sharepoint-document-conversion`.
- Purpose: Validates a staged rendered-output directory (Markdown or ASPX) against the canonical package it was rendered from, and promotes it atomically on PASS. Use after rendering and before accepting or publishing a render. Detects missing or orphan pages, broken links and media references, path traversal, stale source content, and content not traceable to its source chunk. Always PASS or FAIL, never WARN.

## Constraints honored

- Run against a staged rendered-output directory, not an already-promoted one.
- Status is always `PASS` or `FAIL`, never `WARN`; every issue is an error.
- A `FAIL` never promotes. The prior accepted render under `output_root / "rendered-output"` is left untouched and the failed staging directory is kept for diagnosis.
- A pandoc failure while re-deriving ASPX page content means "cannot verify", not a `page_content_not_traceable` finding.
- Run from this skill's root with `scripts/` on `sys.path`.

## Verification passes

- Confirm the report is PASS and `promoted` is true. On FAIL, list each issue (missing or orphan page, broken link, path traversal, stale `source_content_sha256`, untraceable content) and the retained staging directory.
- Focused plugin tests for this skill pass.
