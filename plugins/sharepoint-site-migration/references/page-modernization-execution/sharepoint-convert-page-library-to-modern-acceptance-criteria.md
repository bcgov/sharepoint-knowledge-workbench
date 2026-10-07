# Acceptance Criteria

- Skill slug: `sharepoint-convert-page-library-to-modern`.
- Target plugin: `sharepoint-site-migration`.
- Dry-run mode produces a plan without starting per-page subprocesses or writing to SharePoint.
- Execution requires the documented `-Execute` flag and confirmation token.
- Each page result is recorded in the manifest; one page failure does not erase prior results or stop later pages.
- Resume mode skips pages already recorded as successful, and validation runs unless explicitly skipped.
- Any page failure or validation failure produces a non-zero exit.
- Focused bulk-conversion tests pass.
