# Acceptance Criteria: content-compare-rendered-output

- Skill slug: `content-compare-rendered-output`.
- Target plugin: `sharepoint-document-conversion`.
- Purpose: Compares a freshly produced rendered-output tree (Markdown or ASPX) against a recorded golden-master baseline for byte-identical fidelity, checking file-set completeness and byte-for-byte content while excluding run-specific files. Use to prove a refactor or re-render reproduces known-good output. A standalone, reusable golden-master comparison primitive.

## Constraints honored

- Format-agnostic: both renderers' output (`index.md` and `pages/*.md`, or `page-manifest.json` and `pages/*.html`) is just a directory of files, so no format-specific logic applies.
- `generator-info.json` and `render-result.json` are excluded by default because they carry run-specific fields. Override only deliberately with `excluded_filenames=frozenset(...)`.
- Read-only comparison. Standard library only. Run from this skill's root with `scripts/` on `sys.path`.

## Verification passes

- `status` must be `MATCH` with no issues for byte-identical fidelity. Any `MISMATCH` is a real difference; do not widen `excluded_filenames` to make it pass.
- Focused plugin tests for this skill pass.
