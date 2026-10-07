# Acceptance Criteria: content-render-markdown-pages

- Skill slug: `content-render-markdown-pages`.
- Target plugin: `sharepoint-document-conversion`.
- Purpose: Renders an accepted structured content package into a multipage Markdown publication output, one page per chunk with a path-aware index, rewritten media and page-relative links, validated and atomically promoted. Use after the package has been built and validated. Does not extract source documents, determine topic boundaries, assemble the package, or publish to SharePoint.

## Constraints honored

- Consume only an accepted package promoted by the `sharepoint-document-conversion` plugin. Never build or validate a package here.
- A `FAIL` validation never promotes. The prior accepted render under `output_dir` is left untouched and the failed staging directory is kept for diagnosis.
- Out of scope: extracting source documents, topic boundaries, assembling the package, publishing to SharePoint.
- Python standard library only. Run from this skill's root with `scripts/` on `sys.path`.

## Verification passes

- Check `result["promoted"]` is true and the validation report is PASS. If not, report the failures and the retained staging directory; do not present the render as accepted.
- Focused plugin tests for this skill pass.
