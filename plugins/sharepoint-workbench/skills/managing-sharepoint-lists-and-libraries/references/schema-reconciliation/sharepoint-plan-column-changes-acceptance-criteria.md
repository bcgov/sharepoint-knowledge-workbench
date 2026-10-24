# Acceptance Criteria: sharepoint-plan-column-changes

- Skill slug: `sharepoint-plan-column-changes`.
- Target plugin: `sharepoint-site-build-and-publish`.
- Purpose: Filters an exported field set down to deployable fields, detects live-type drift against a declared schema, and builds raw Field XML for column types a typed field-creation API cannot express (Calculated has no formula parameter; Lookup and LookupMulti; User and UserMulti). Use when planning site-column provisioning. Pure planning; no write ships in this module.

## Constraints honored

- Planning only, zero tenant I/O. Nothing this skill returns has been executed; execution goes through the `sharepoint-site-build-and-publish` plugin's `sharepoint-apply-provisioning-plan` skill.
- Raw Field XML is the only route for a Calculated column. `build_calculated_field_xml` escapes every caller-supplied string; a non-Calculated `FieldDef` or a missing formula raises `FieldDefinitionError`. Never emit hand-built XML around it.
- Deploy nothing silently: hidden and read-only fields are excluded unless the caller opts them in by name.
- Run from this skill's root with `scripts/` on `sys.path`. Standard library only.

## Verification passes

- Each field has an explicit action; XML builders either returned escaped XML or raised `FieldDefinitionError`. Report any `repair` (type drift) to the user rather than fixing it silently.
- Focused plugin tests for this skill pass.
