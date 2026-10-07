# Acceptance Criteria: sharepoint-compare-schema-exports

- Skill slug: `sharepoint-compare-schema-exports`.
- Target plugin: `sharepoint-site-assessment`.
- Purpose: Compares two exported SharePoint schema snapshots (lists, content types, site columns, per-list fields) and reports additions, removals and per-property changes, plus a duplicate-display-name audit. Use to answer what actually differs between two environments before a migration, a promotion or a post-deployment check. Environment labels and compared properties are caller-supplied. Read-only; consumes exports, never contacts a tenant.

## Constraints honored

- Read-only by construction. It consumes exports and never contacts a tenant; there is no remediation or write capability, and a test asserts its absence.
- Absence is never a pass. A missing export makes the report `UNAVAILABLE`. Report `EMPTY`, `PARTIAL` and `UNAVAILABLE` as what they are.
- No environment names are built in. Pass your own `left_label` and `right_label`, and choose the compared properties yourself.
- Run from this skill's root with `scripts/` on `sys.path`.

## Verification passes

- Check the report status is `OBSERVED` before calling the result clean. The markdown output is deterministic, so re-running over the same inputs should diff to nothing.
- Focused plugin tests for this skill pass.
