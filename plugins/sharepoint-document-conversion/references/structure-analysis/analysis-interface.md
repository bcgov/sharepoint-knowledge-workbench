# Document structure analysis interface

## Contents

- [Public interface](#public-interface)
- [Input and output](#input-and-output)
- [Guarantees](#guarantees)
- [What the plan contains](#what-the-plan-contains)
- [Next step](#next-step)

## Public interface

```python
from document_structure_analysis import recommend_from_normalized

analysis_plan = recommend_from_normalized(normalized_source_document)
```

## Input and output

- `normalized_source_document`: a `normalized-source-document` v1 dict, produced by the
  `sharepoint-document-conversion` plugin's `extract_and_normalize`.
- Returns an `analysis-plan` v1 dict, validated against this plugin's own bundled schema.
  `references/structure-analysis/contracts/analysis-plan.md` describes it. No repository-root or sibling-plugin lookup is required.

## Guarantees

- Never writes to disk and never mutates its input. The caller persists the result.
- Never re-parses headings or re-detects defect signals. Those are the extraction step's job and are already on
  the input dict; this skill reasons about those observations only.
- Python standard library only; no other workbench package is required.

## What the plan contains

A chunking-strategy recommendation, a topic-boundary preview, structural anchors (stable chunk identity, never
raw line offsets) and a draft `ConversionPlan` with `confirmation.status == "draft"`.

## Next step

The plan is a draft for human review. A human confirms it, and only the confirmed plan goes to the
`sharepoint-document-conversion` plugin's `build_canonical_package`. This skill never confirms a plan itself.
