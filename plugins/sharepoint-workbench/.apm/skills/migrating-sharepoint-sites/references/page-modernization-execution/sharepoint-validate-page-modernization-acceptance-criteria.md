# Acceptance Criteria

- Skill slug: `sharepoint-validate-page-modernization`.
- Target plugin: `sharepoint-site-migration`.
- Validation is read-only and checks every manifest page against the target library.
- The same field mapping and literal-value files used by conversion are used for validation.
- Missing pages, empty mapped values, or mismatched literal values fail the run and appear in the report.
- The command exits non-zero for any validation failure and does not rely on the conversion run's exit code.
- Focused page-validation tests pass.
