# Acceptance Criteria

- Skill slug: `sharepoint-update-page-links`.
- Target plugin: `sharepoint-site-migration`.
- Destination mapping and rewrite planning are local, offline operations; no tenant write occurs.
- Every mapping run requires explicit source and target parameters and does not infer same-library destinations.
- Optional workbook validation is read-only and rejects missing, ambiguous, or mismatched mapping rows.
- Mapping validates path boundaries, duplicate destinations, output/input collisions, and configured scope/count guards.
- Rewrite planning preserves original query and fragment data when the resolved destination omits them and reports distinct review outcomes.
- Canonical scripts and references are exposed through managed, file-level symlinks.
- Focused mapping and rewrite tests pass, and the plugin audit resolves all links referenced by this skill.
