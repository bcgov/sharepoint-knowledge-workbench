# Acceptance Criteria

- Skill slug: `sharepoint-create-page-preview`.
- Target plugin: `sharepoint-site-migration`.
- The preview is composed only from the supplied page and site-chrome files; no network or tenant I/O occurs.
- Missing required input files produce `Unavailable` and no output file.
- Missing optional chrome is named in the outcome; no logo, navigation, or breadcrumb is fabricated.
- `Observed`, `Partial`, `Empty`, and `Unavailable` outcomes match the input coverage.
- Focused preview-composition tests pass.
