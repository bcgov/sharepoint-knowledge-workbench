# Acceptance Criteria

- Skill slug: `sharepoint-convert-page-to-modern`.
- Target plugin: `sharepoint-site-migration`.
- Dry-run mode performs no tenant writes; live conversion requires `-Execute` and the documented token.
- Conversion is limited to one page in the same site and uses caller-supplied field mappings and literal values.
- Same-site conversion does not claim to rewrite embedded links.
- The result identifies the converted page and the metadata applied.
- Focused single-page conversion tests pass.
