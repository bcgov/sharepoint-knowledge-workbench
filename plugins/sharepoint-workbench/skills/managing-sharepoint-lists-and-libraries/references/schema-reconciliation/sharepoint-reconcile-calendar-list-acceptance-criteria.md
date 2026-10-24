# Acceptance Criteria: sharepoint-reconcile-calendar-list

- Skill slug: `sharepoint-reconcile-calendar-list`.
- Target plugin: `sharepoint-site-build-and-publish`.
- Purpose: Plans provisioning of a working modern SharePoint Online calendar list, structurally preventing a real platform bug (Start/End declared as site columns or content-type-linked fields silently breaks calendar view rendering) by refusing any definition that would trigger it and always planning the validated workaround shape. Use when asked for a calendar list. Gates any real write behind dry-run-by-default, an injected executor and a plan-derived confirmation token.

## Constraints honored

- Never plan Start/End as site columns or content-type-linked fields. `CalendarListDef(start_end_site_columns=(...))` raises `StartEndScopeViolation`; there is no supported fix for a list created that way (it must be deleted and recreated).
- Always the Generic List template (100), never the Calendar template (106); Start/End are list-local fields only; the modern calendar view is a REST creation step (`ViewTypeKind=1`, `ViewType2="MODERNCALENDAR"`).
- Same write gates as `sharepoint-reconcile-site-schema`: dry-run by default; an injected executor (else `ExecutorRequired`); `confirm=plan.confirmation_token` (else `ConfirmationRequired`).
- The PowerShell executor `spo-provision-calendar.ps1` ships in this plugin's `scripts/calendar-executor/` namespace and is not part of `sharepoint-apply-provisioning-plan`; delegate execution to it.
- Run from this skill's root with `scripts/` on `sys.path`. Standard library only.

## Verification passes

- A valid plan always has the same three write steps and is never `EMPTY`. After an apply, `OBSERVED` means all three succeeded; treat `PARTIAL`, `FORBIDDEN` and `FAILED` as incomplete.
- Focused plugin tests for this skill pass.
