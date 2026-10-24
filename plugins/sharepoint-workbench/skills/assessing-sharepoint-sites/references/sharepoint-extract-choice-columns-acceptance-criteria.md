# Acceptance Criteria: sharepoint-extract-choice-columns

- Skill slug: `sharepoint-extract-choice-columns`.
- Target plugin: `sharepoint-site-assessment`.
- Purpose: Inventories Choice and MultiChoice fields from an exported SharePoint schema and renders them as a list and internal-name keyed overrides mapping, distinguishing "no options defined" from "options unknown". Use when you need the real option sets behind a site's Choice columns for migration mapping, validation rules or seeding a provisioning template. Read-only; the group filter is opt-in with no default.

## Constraints honored

- Unknown is not empty. An empty choice list means no options are defined; a field with no `Choices` property is `UNKNOWN`. `to_overrides_mapping` omits unknown option sets rather than emitting an empty list for them.
- The group filter is an explicit caller parameter with no default. Exclude nothing silently.
- A missing export is `UNAVAILABLE`, never an empty success. An export with no choice fields is `EMPTY`.
- Read-only. Run from this skill's root with `scripts/` on `sys.path`.

## Verification passes

- Check `inv.status`, and that every field missing a `Choices` property is reported as unknown rather than empty. Both the plain array and the OData `{"results": [...]}` forms are accepted.
- Focused plugin tests for this skill pass.
