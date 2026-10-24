# Acceptance Criteria

- Skill slug: `sharepoint-audit-list-migration`.
- Target plugin: `sharepoint-site-migration`.
- The skill audits item values and lookup pointers, not schema provisioning.
- Canonical resources reside in `plugins/sharepoint-site-migration/scripts/content-migration/content-audit`.
- Skill-local resources are symbolic links registered in `symlinks.json`.
- Source and target exports remain in the designated PII scratch directory.
- Published summary metrics and narrative reports contain no PII.
- Deterministic extraction runs before interpretive variance analysis.
- Lookup reconciliation uses verified source-to-target identity mapping.
- The audit never writes to a tenant. The preserved repair script is documented as a separate, ungated live-write capability that needs an explicit human decision, and its dry run (`-DryRun`) comes first.
