# Acceptance Criteria

- Skill slug: `sharepoint-generate-modernization-report`.
- Target plugin: `sharepoint-site-migration`.
- The renderer reads a manifest conforming to the declared schema and performs no tenant I/O.
- Missing required fields or invalid outcomes fail without writing a report.
- Every manifest gap is represented in the report; an empty gap list is stated explicitly.
- The report includes disposition, component classification, layout, and confidence summaries.
- Focused conversion-report tests pass.
