# Acceptance Criteria: sharepoint-generate-schema-definition-from-export

- Skill slug: `sharepoint-generate-schema-definition-from-export`.
- Target plugin: `sharepoint-site-build-and-publish`.
- Purpose: Transforms an already-loaded SharePoint schema export (site columns, content types, lists with fields) into a declarative, JSON-serializable schema definition. Use when you need a definition suitable for later comparison or provisioning-input translation. A pure, read-only transform; consumes an export, never contacts a tenant.

## Constraints honored

- Pure and read-only. Never contact a tenant, never provision or write anything, and do not compare two exports (that is `sharepoint-compare-schema-exports`).
- A degraded export never produces a clean-looking definition. The definition carries the export's overall status unchanged, with only the `OBSERVED` sections populated. A list whose `fields.json` could not be read keeps an honest `fields_status` and empty `fields`.
- Run from this skill's root with `scripts/` on `sys.path`.

## Verification passes

- Check `definition.status` is `OBSERVED` before treating the definition as complete. Round-trip it with `SiteSchemaDefinition.load` to confirm it parses.
- Focused plugin tests for this skill pass.
