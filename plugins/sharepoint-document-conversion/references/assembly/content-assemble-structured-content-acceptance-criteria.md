# Acceptance Criteria: content-assemble-structured-content

- Skill slug: `content-assemble-structured-content`.
- Target plugin: `sharepoint-document-conversion`.
- Purpose: Assembles a validated structured content package from a human-confirmed conversion plan and its source document, with stable identities, source lineage, hashes, manifests and publication mappings. Use after the conversion plan has been confirmed. Does not extract source documents, make unconfirmed topic decisions, render output formats, or publish to SharePoint.

## Constraints honored

- Consume only a confirmed plan (`confirmation.status == "confirmed"`). Never construct or confirm a plan here; that belongs to the `sharepoint-document-conversion` plugin plus human confirmation.
- A plan that is unconfirmed, whose source fingerprint no longer matches, or that changed after confirmation raises `PlanVerificationError`. Do not work around it.
- A `FAIL` validation never promotes. The prior accepted package is left untouched and the failed staging directory is kept for diagnosis.
- Out of scope: extracting source documents, unconfirmed topic decisions, rendering output formats, publishing to SharePoint.
- `pandoc` (and LibreOffice `soffice` for legacy `.emf` media) must be on `PATH`. Run from this skill's root with `scripts/` on `sys.path`.

## Verification passes

- Check `result["promoted"]` is true and the validation report is PASS. If it is false, report the failures and the retained staging directory; do not present the package as accepted.
- Focused plugin tests for this skill pass.
