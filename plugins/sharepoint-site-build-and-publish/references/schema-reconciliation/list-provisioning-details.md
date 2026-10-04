# List provisioning details

## Contents

- [Stage and scope](#stage-and-scope)
- [Usage](#usage)
- [Scripts](#scripts)
- [Provenance](#provenance)

## Stage and scope

Reconciles a whole declarative schema (site columns, content types and target list or library objects) against a caller-supplied observation of current live state, and, only after explicit review, applies the resulting
plan through your own injected executor. Stage: `sharepoint-plan-content-type-changes` and `sharepoint-plan-column-changes` (per-object planning) feed `sharepoint-reconcile-site-schema` (whole-schema reconciliation and gated apply). The
four write gates, honest outcomes and fail-loud deletion verification are in `schema-reconciliation-pipeline.md`.

## Usage

```python
# 1. Plan (always safe: pure computation over caller-supplied inputs)
from list_provisioning import plan_provisioning
plan = plan_provisioning(schema, current_state)
print(plan.outcome, plan.to_dict())
```

Apply only after reviewing the plan, with a real executor and the plan's own confirmation token, and only once any blocking findings are resolved: `apply_provisioning(plan, executor=..., dry_run=False,
confirm=plan.confirmation_token)`.

## Scripts

- `scripts/schema-reconciliation/list_provisioning.py`: `ProvisioningSchema`, `CurrentState`, `ListDef`, `ListState`, `plan_provisioning`, `detect_duplicate_lists`, `apply_provisioning`, `verify_deletion_complete`, and the safety errors.
- `scripts/schema-reconciliation/field_provisioning.py`, `scripts/schema-reconciliation/content_type_provisioning.py`: the per-object planning this module aggregates.
- `scripts/schema-reconciliation/provisioning_outcomes.py`: the shared `Outcome` vocabulary.

## Provenance

Adapted from `list-helpers.ps1` (`Invoke-WithRetry`, `New-ListSafe`, `New-LibrarySafe`) plus the reconcile-schema, duplicate-detection and fail-loud pattern (not any project-specific content) of
`reset-and-provision-etl-target-schema.ps1`. The three-gate write-safety hardening (dry-run default, injected executor, confirmation token) is a deliberate improvement over the source, which had no confirmation-token gate.
Source repository only: `docs/reports/phase-9-reusable-sharepoint-plugin-extraction/provenance.md`.
