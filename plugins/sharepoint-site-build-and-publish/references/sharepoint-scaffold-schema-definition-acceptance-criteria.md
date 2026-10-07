# Acceptance Criteria: sharepoint-scaffold-schema-definition

- Skill slug: `sharepoint-scaffold-schema-definition`.
- Target plugin: `sharepoint-site-build-and-publish`.
- Purpose: Scaffolds a declarative SiteSchemaDefinition JSON structure from scratch or from input parameters, without a live tenant connection. Use to author or bootstrap a new SharePoint site schema definition locally before diffing it with sharepoint-site-build-and-publish or provisioning it with sharepoint-site-build-and-publish.

## Constraints honored

- Local only. No tenant connection and no tenant writes; the output is a JSON file you name.
- The CLI (`--label`, `--output` required) writes an empty definition with status `OBSERVED` and no columns, content types or lists. Populate it with `scaffold_schema(...)`, not by hand-editing.
- Diffing and provisioning are other skills' jobs: hand the result to `sharepoint-site-build-and-publish` or `sharepoint-site-build-and-publish`.
- Run from this skill's root. Standard library only.

## Verification passes

- Confirm the file exists, loads with `SiteSchemaDefinition.load`, and its section counts match the input.
- Focused plugin tests for this skill pass.
