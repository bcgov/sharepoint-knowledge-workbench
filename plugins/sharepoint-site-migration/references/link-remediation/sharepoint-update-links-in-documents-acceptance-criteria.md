# Acceptance Criteria

- Skill slug: `sharepoint-update-links-in-documents`.
- Target plugin: `sharepoint-site-migration`.
- Office relationship rewriting uses the standard library and preserves document package validity.
- PDF input is `NOT_SUPPORTED` unless a caller supplies a PDF handler; binary PDF data is never text-substituted.
- Dry-run is the default; applying changes requires an injected executor and the plan confirmation token.
- Partial and failed processing is reported honestly, and originals remain available for comparison.
- Focused document-link remediation tests pass.
