# Schema reconciliation: pipeline, write safety and where the executors live

## Contents

- [The pipeline](#the-pipeline)
- [Write safety](#write-safety)
- [Honest outcomes](#honest-outcomes)
- [Where the executors live](#where-the-executors-live)
- [Zero tenant I/O](#zero-tenant-io)

## The pipeline

Declarative, JSON-schema-driven reconciliation of site columns, content types and lists. Reconcile, do not recreate: existing objects are left alone except for drift the schema calls out.

`sharepoint-provision-fields` and `sharepoint-provision-content-types` plan per-object changes; `sharepoint-provision-list` aggregates them into a whole-schema `ProvisioningPlan` and gates any
real apply; `sharepoint-provision-modern-calendar-list` plans a calendar list that avoids a platform bug. All planning is pure computation over caller-supplied inputs.

## Write safety

Per Phase 9 spec section 13, no autonomous production write is reachable. The modules that can apply a plan (`list_provisioning.apply_provisioning`, `calendar_provisioning.apply_calendar_list`) share these gates:

1. **Dry-run is the default.** `apply_*(plan)` with no further arguments changes nothing.
2. **An executor must be injected.** The modules ship no tenant transport. Without an `executor(step, detail)` callable, a real apply raises `ExecutorRequired` rather than silently no-op'ing or faking success.
3. **A confirmation token is required.** `dry_run=False` additionally requires `confirm=plan.confirmation_token`, derived from the plan's own content. A stale or absent token raises
   `ConfirmationRequired`, so a plan cannot be applied after the underlying schema or observed state changes.
4. **Duplicate-titled lists unconditionally block execution** (`list_provisioning` only). If `detect_duplicate_lists` found more than one live object sharing a `recreate=True` list's exact title,
   `apply_provisioning` raises `DuplicateListsBlockProvisioning` regardless of the token. A real incident (a stray duplicate list silently resolved to the wrong one) is why this gate exists.

This mirrors `sharepoint-link-remediation`'s write-safety model.

## Honest outcomes

| Outcome | Meaning |
|---|---|
| `OBSERVED` | All intended steps succeeded (or, for a plan, real changes are planned) |
| `EMPTY` | Nothing to do: schema and current state already match |
| `PARTIAL` | Some steps succeeded, some failed; both lists populated |
| `FORBIDDEN` | The executor raised `PermissionError` |
| `FAILED` | Every step failed, or the plan carries a blocking duplicate finding |

`verify_deletion_complete(title, still_exists=...)` raises `DeletionVerificationFailed` if an object expected to be gone after a delete step is still observed to exist; never assume a delete succeeded.

## Where the executors live

This plugin plans; it does not execute. The real, tested PnP.PowerShell executors that these plans are meant to be submitted to belong to the `sharepoint-provisioning` plugin, through its
`sharepoint-apply-provisioning-plan` skill:

- fields: `spo-provision-site-columns.ps1`, `spo-update-site-column.ps1`, `spo-remove-site-column.ps1`;
- content types: `spo-provision-content-types.ps1`, `spo-update-content-type.ps1`, `spo-remove-content-type.ps1`, `spo-detach-content-type-from-list.ps1`;
- lists: `spo-provision-list.ps1`, which consumes `ProvisioningPlan.to_dict()` output verbatim (see that script's header for the exact field-name match).

The calendar executor, `spo-provision-calendar.ps1`, is a script of the `sharepoint-migration-planning` plugin, not of `sharepoint-provisioning`; it is not part of `sharepoint-apply-provisioning-plan`'s
executor table. Delegate to those plugins' skills rather than importing or copying their scripts.

## Zero tenant I/O

No tenant I/O ships in this plugin, and a test (`tests/test_plugin_independence.py`) enforces it.
