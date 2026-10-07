# Structured content assembly interface

## Contents

- [Public interface](#public-interface)
- [Inputs and return value](#inputs-and-return-value)
- [Verification and failure behavior](#verification-and-failure-behavior)
- [Contracts](#contracts)
- [External tools](#external-tools)

## Public interface

```python
from structured_content_assembly import build_canonical_package

result = build_canonical_package(analysis_plan, source_dir, output_dir)
# {"manifest": ..., "validation_report": ..., "promoted": bool, "package_dir": str}
```

## Inputs and return value

- `analysis_plan`: a confirmed `analysis-plan` v1 dict (`confirmation.status == "confirmed"`), produced
  by the `sharepoint-document-conversion` plugin's `recommend_from_normalized` plus human confirmation.
- `source_dir`: path to the directory containing the source `.docx` the plan references.
- `output_dir`: path under which the package is staged and, on a PASS validation, atomically promoted.
- Returns the `Manifest` and `ValidationReport` contents, whether promotion happened, and the final
  package directory. For a `strategy: "grouped"` plan it also builds and validates a `publication-map`.

The pipeline is: pandoc extraction, markdown cleanup, heading-based chunking, media
inventory/copy/rewrite, manifest assembly, validation, atomic promotion.

## Verification and failure behavior

- A plan whose `confirmation.status` is not `"confirmed"`, whose source file no longer matches the
  plan's recorded fingerprint, or whose content changed after confirmation raises
  `PlanVerificationError`.
- A `FAIL` validation never promotes. The prior accepted package under `output_dir`, if any, is left
  untouched, and the failed staging directory is retained for diagnosis.
- This skill never constructs or confirms a plan itself.

## Contracts

- `references/contracts/canonical-package.md`: the package layout and manifest contract.
- `references/contracts/publication-map.md`: the publication-map contract for grouped plans.

## External tools

`pandoc` must be on `PATH`. For legacy `.emf` media, LibreOffice's `soffice` must be on `PATH` too. No
other workbench package is required; the plugin has zero dependency on any other distribution.
