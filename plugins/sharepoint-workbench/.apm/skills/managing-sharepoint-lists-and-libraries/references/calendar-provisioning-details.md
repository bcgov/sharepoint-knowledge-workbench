# Modern calendar list provisioning details

## Contents

- [The platform bug](#the-platform-bug)
- [The workaround, encoded structurally](#the-workaround-encoded-structurally)
- [Outcomes](#outcomes)
- [Usage](#usage)
- [Executor](#executor)
- [Scripts](#scripts)
- [Provenance](#provenance)

## The platform bug

If a calendar list's Start and End date fields are declared as site columns (or linked to the list through a content type) before the list is created, SharePoint Online creates the list without error but its calendar
view silently never renders events correctly. There is no supported fix once a list is in that state: it must be deleted and recreated correctly.

## The workaround, encoded structurally

`plan_calendar_list` makes the mistake unrepresentable:

1. A Generic List template (100), never the Calendar template (106).
2. Start and End are always planned as list-local fields only: never site columns, never content-type-linked.
3. The modern calendar view is always planned as a REST creation step (`ViewTypeKind=1`, `ViewType2="MODERNCALENDAR"`), not left to whatever view a template would provision.

If a caller passes `CalendarListDef(start_end_site_columns=(...))`, which declares the exact trigger, `plan_calendar_list` raises `StartEndScopeViolation` immediately. No code path produces a plan matching the broken shape.

## Outcomes

`OBSERVED` (all three steps: list creation, list-local fields, view creation, succeeded), `PARTIAL`, `FORBIDDEN` (the executor raised `PermissionError`), `FAILED` (every step failed). A valid plan is never `EMPTY`: a calendar
list always has the same three write steps. The write gates are in `schema-reconciliation-pipeline.md`.

## Usage

```python
from calendar_provisioning import plan_calendar_list, CalendarListDef
plan = plan_calendar_list(CalendarListDef(title='Team Calendar'))
print(plan.outcome, plan.to_dict())
```

Apply only after reviewing the plan, with a real executor and the plan's own confirmation token: `apply_calendar_list(plan, executor=..., dry_run=False, confirm=plan.confirmation_token)`.

## Executor

A tested PowerShell executor, `spo-provision-calendar.ps1`, ships in this plugin's `scripts/calendar-executor/` namespace, separate from the zero-tenant-I/O schema planner namespace (`scripts/schema-reconciliation/`). It is not part of `sharepoint-apply-provisioning-plan`'s executor table, so
calendar provisioning is not yet a fully integrated workflow: treat this skill as planning plus a gated Python apply, and delegate execution to the migration-planning plugin's script.

## Scripts

`scripts/schema-reconciliation/calendar_provisioning.py`: `CalendarListDef`, `plan_calendar_list`, `apply_calendar_list`, `StartEndScopeViolation`, `ExecutorRequired`, `ConfirmationRequired`. `scripts/schema-reconciliation/provisioning_outcomes.py`: the shared `Outcome` vocabulary.

## Provenance

Generalized from a source-repository calendar-provisioning helper's `Add-CalendarContentTypeSafe`, `Set-NewButtonContentTypes`, `Add-ListFieldToContentTypeSafe` and `New-ModernCalendarList` functions, identified in the Phase 9
exhaustive source audit (`temp/phase9-source-audit/file-tracking.json`) as a genuine, validated platform-bug workaround applicable to any SPO tenant, not the project-specific bulk calendar provisioning that consumed it in the
source repo. The three-gate write safety matches `sharepoint-reconcile-site-schema`'s pattern, a deliberate improvement over the source. Source repository only.
