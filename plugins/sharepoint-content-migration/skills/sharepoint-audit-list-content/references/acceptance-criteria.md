# Acceptance Criteria

- Skill slug: `sharepoint-audit-list-content`.
- Target plugin: `sharepoint-content-migration`.
- The skill audits item values and lookup pointers, not schema provisioning.
- Canonical resources reside in `plugins/sharepoint-content-migration/scripts/content-audit`.
- Skill-local resources are symbolic links registered in `symlinks.json`.
- Source and target exports remain in the designated PII scratch directory.
- Published summary metrics and narrative reports contain no PII.
- Deterministic extraction runs before interpretive variance analysis.
- Lookup reconciliation uses verified source-to-target identity mapping.
- Any healing operation is explicitly separated from read-only auditing and starts with a dry run.
