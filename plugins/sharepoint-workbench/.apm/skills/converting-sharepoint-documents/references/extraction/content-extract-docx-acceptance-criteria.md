# Acceptance Criteria: content-extract-docx

- Skill slug: `content-extract-docx`.
- Target plugin: `sharepoint-document-conversion`.
- Purpose: Runs pandoc against a source .docx and produces a normalized-source-document contract (markdown text, media files, heading structure, defect signals, statistics) for downstream structure analysis. Use as the first step when converting a Word document into structured content. Observes the source only; never interprets strategy or writes structured content.

## Constraints honored

- Observe only. Never choose a strategy (single or chunked), propose topic boundaries, or write structured content.
- `pandoc` must be on `PATH`; otherwise `dependencies.MissingDependencyError` is raised. A missing `source` raises `FileNotFoundError`.
- Run from this skill's root with `scripts/` on `sys.path`. No other workbench package is required.

## Verification passes

- Confirm the call returned a dict validated against the bundled schema and that `output_dir/raw/` holds the pandoc output. Report any raw-TOC or defect signals as observed, not as decisions.
- Focused plugin tests for this skill pass.
