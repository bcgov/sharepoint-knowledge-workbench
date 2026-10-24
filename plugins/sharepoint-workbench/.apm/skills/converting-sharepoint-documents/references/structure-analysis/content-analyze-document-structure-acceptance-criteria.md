# Acceptance Criteria: content-analyze-document-structure

- Skill slug: `content-analyze-document-structure`.
- Target plugin: `sharepoint-document-conversion`.
- Purpose: Analyzes normalized extracted document content to identify heading hierarchy, topic boundaries, cross-references, structural deficiencies, and a proposed conversion plan for human review. Use after source-document extraction. Does not parse DOCX files, assemble the structured content package, render outputs, or publish to SharePoint.

## Constraints honored

- Reason about the extraction step's observations only. Never re-parse headings or re-detect defect signals.
- Never write to disk and never mutate the input dict.
- The result is a draft (`confirmation.status == "draft"`). Never confirm a plan; a human does, and only a confirmed plan goes to `sharepoint-document-conversion`.
- Out of scope: parsing DOCX files, assembling the package, rendering, publishing to SharePoint.
- Python standard library only. Run from this skill's root with `scripts/` on `sys.path`.

## Verification passes

- Confirm the result is an `analysis-plan` v1 dict with `confirmation.status == "draft"` and that the input dict is unchanged. Do not treat the plan as final until a human confirms it.
- Focused plugin tests for this skill pass.
