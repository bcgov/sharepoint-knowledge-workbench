# Acceptance Criteria

- Skill slug: `sharepoint-migrate-list-content`.
- Target plugin: `sharepoint-site-migration`.
- List schemas and target lists must already exist; the skill does not provision them.
- Lookup content is applied in two passes using source-to-destination ID mappings.
- Unresolved lookup IDs are reported and quarantined rather than silently dropped.
- Dry-run is the default; real writes require an injected executor and the plan-derived confirmation token.
- Outcomes distinguish complete, partial, failed, and empty runs.
- Focused item-migration tests pass.
