# Acceptance Criteria

- Skill slug: `sharepoint-initialize-migration-project`.
- Target plugin: `sharepoint-site-migration`.
- Setup confirms the repository-root `config.psd1` and never creates or edits a competing config.
- Missing config, connection data, or required project parameters fail before creating directories.
- A valid request creates the documented per-migration working directory and subfolders idempotently.
- The operation performs no tenant I/O.
- Focused migration-project setup tests pass.
