# Acceptance Criteria

- Skill slug: `sharepoint-extract-links`.
- Target plugin: `sharepoint-site-migration`.
- Extraction remains offline and read-only; live SharePoint reads are separately invoked by the user.
- Supported HTML and Office document inputs retain source identity and distinguish `OBSERVED`, `EMPTY`, `PARTIAL`, and `FAILED` outcomes.
- Unsupported formats and failed reads are reported rather than treated as complete coverage.
- The shared mapping workflow is linked through a managed, file-level symlink.
- Focused extraction and mapping tests pass, and the plugin audit resolves all links referenced by this skill.
