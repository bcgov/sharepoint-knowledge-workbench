# Acceptance Criteria: sharepoint-compare-schema-definitions

- Skill slug: `sharepoint-compare-schema-definitions`.
- Target plugin: `sharepoint-site-build-and-publish`.
- Purpose: Compares schema DEFINITIONS (the declarative SiteSchemaDefinition shape) against each other, or a schema definition against an exported SchemaExport, answering what would change if a target definition were applied against current state. Use after generating or hand-authoring a target definition. Read-only; consumes local files and objects only, never contacts a tenant, never writes an apply plan.

## Constraints honored

- Read-only. Pure comparisons over local files and objects already loaded; never contact a tenant and never produce an apply or write plan, only a diff report.
- A degraded input side is never a clean pass. If either side is `UNAVAILABLE`, the report is `UNAVAILABLE`; if either is short of `OBSERVED`, it is `PARTIAL`.
- Run from this skill's root with `scripts/` on `sys.path`.

## Verification passes

- Check the report status is `OBSERVED` before calling the result clean. Output is deterministic, so identical inputs should diff to nothing.
- Focused plugin tests for this skill pass.
