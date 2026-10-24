# Acceptance Criteria: sharepoint-plan-content-type-changes

- Skill slug: `sharepoint-plan-content-type-changes`.
- Target plugin: `sharepoint-site-build-and-publish`.
- Purpose: Plans create-if-missing SharePoint content-type provisioning from a caller-supplied declarative definition (add, hide, show and unlink field links, with hidden-flag drift against the schema surfaced rather than silently fixed) plus content-type-to-list attach planning. Use when reconciling a content type against current state. Pure planning, read-safe by construction; no write ships in this module.

## Constraints honored

- Read-safe by construction: every function only computes a plan from caller-supplied inputs. Execution goes through `sharepoint-reconcile-site-schema`'s gated `apply_provisioning`, or the `sharepoint-site-build-and-publish` plugin's executors.
- Reconcile, do not recreate: leave an existing content type alone except for the drift the schema calls out. Report a hidden-flag mismatch as drift in the action's `detail`; never correct it silently.
- Unlink a field only if it is currently linked. An already-absent link is neither an error nor a fake success.
- Run from this skill's root with `scripts/` on `sys.path`. Standard library only.

## Verification passes

- Every action shows `step`, `already_correct` and `detail`; drift is named in `detail`. A plan with every action `already_correct` means current state matches the schema.
- Focused plugin tests for this skill pass.
