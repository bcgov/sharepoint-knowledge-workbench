# sharepoint-provisioning

Declarative, JSON-schema-driven SharePoint site-column, content-type, and
list/library provisioning. **Zero SharePoint tenant I/O.** Every column,
content type, and target object comes from a caller-supplied schema; this
plugin reads a schema and a caller-supplied observation of current state,
plans what would need to change, and once approved, submits that plan to
`sharepoint-migration-planning`'s `apply-sharepoint-provisioning-plan` skill
for real execution. It never fetches tenant state itself.

```
plugins/sharepoint-provisioning/
├── scripts/
│   ├── provisioning_outcomes.py     # shared Outcome vocabulary
│   ├── field_provisioning.py        # deployable-field filtering, type-repair
│   │                                 # detection, raw Field XML construction
│   ├── content_type_provisioning.py # create-if-missing content types,
│   │                                 # field-link add/hide/show/unlink
│   ├── list_provisioning.py         # schema reconciliation, duplicate
│   │                                 # detection, the three-gate write apply
│   └── calendar_provisioning.py     # modern-calendar-list provisioning,
│                                     # structurally prevents the Start/End
│                                     # platform bug
├── skills/
│   ├── provision-content-types/
│   ├── provision-fields/
│   ├── provision-list/
│   └── provision-modern-calendar-list/
├── rules/
│   └── schema-driven-sharepoint-deployment.md  # schema/dependency-graph
│                                                 # deployment convention
└── tests/
```

## Honest outcomes

`Outcome`: `OBSERVED` / `EMPTY` / `PARTIAL` / `FORBIDDEN` / `UNAVAILABLE` /
`NOT_SUPPORTED` / `FAILED`. A plan with nothing to do is `EMPTY`, never a
silent pass on a schema that was actually skipped. A partly-failed apply is
`PARTIAL` with both the succeeded and failed steps listed. An executor
raising `PermissionError` is `FORBIDDEN`, never flattened into a generic
failure. A plan carrying a duplicate-title finding is `FAILED` — it can
never be executed, not even a partial subset of it.

## Reconcile, not recreate

- **Fields and content types are create-if-missing.** An existing field or
  content type is left untouched except for the specific drift the schema
  calls out.
- **Drift is surfaced, not silently fixed.** If a content-type field link's
  hidden flag differs from the schema, the plan reports it as drift
  (`"reconcile hidden=... (drift: was ...)"`) rather than just applying the
  fix invisibly — the confirmation step is meant to be an informed one.
- **Undeclared fields are explicitly unlinked**, not left as orphaned live
  state, via `ContentTypeDef.unlink_fields`.
- **Lists are untouched unless `recreate=True`.** Provisioning a list target
  is create-if-missing by default; only a list explicitly opted into
  `recreate=True` is ever considered for deletion, and only after passing
  duplicate-title detection.

## The calculated-column XML workaround

Typed field-creation APIs generally have no way to express a formula.
`field_provisioning.build_calculated_field_xml` builds the raw Field XML a
Calculated column requires instead, with all caller-supplied text escaped —
attribute values (display name, static name, group) via the full XML
attribute-escaping set (`&`, `<`, `>`, `"`, `'`), and the formula body
(element text, not an attribute) via the text-escaping subset (`&`, `<`,
`>`). `build_lookup_field_xml` and `build_user_field_xml` cover the other
two field types the same typed-API limitation affects (Lookup/LookupMulti,
User/UserMulti).

## Duplicate-title detection before any delete

`list_provisioning.detect_duplicate_lists` checks, for every list declared
with `recreate=True`, whether the caller's `ListState.matching_count` shows
more than one live object sharing that exact title — never a single
identity lookup, which can silently resolve to the wrong object when
duplicates exist. Any duplicate becomes a `blocking_findings` entry on the
plan; `apply_provisioning` refuses to execute a plan carrying one, even with
an otherwise-valid confirmation token (`DuplicateListsBlockProvisioning`).

## Write safety — three independent gates

Per Phase 9 spec section 13, no autonomous production write is reachable,
mirroring `sharepoint-link-remediation`'s `remediate-links` exactly:

1. **Dry-run is the default.** `apply_provisioning(plan)` with no arguments
   changes nothing.
2. **An executor must be injected.** This module ships no tenant transport.
   Without an `executor` callable, a real apply raises `ExecutorRequired`
   rather than silently no-op'ing or faking success.
3. **A confirmation token is required.** `dry_run=False` additionally
   requires `confirm=plan.confirmation_token`, derived from the plan's own
   content. A stale or absent token raises `ConfirmationRequired`, so a plan
   cannot be applied after the underlying schema or observed state has
   changed.

A fourth, unconditional gate sits above all three: a plan with duplicate-
title blocking findings can never be executed.

## Fail-loud deletion verification

`verify_deletion_complete(title, still_exists=...)` raises
`DeletionVerificationFailed` if an object expected to be gone after a
delete step is still observed to exist. It performs no check itself — it
enforces the honest-outcome contract against whatever fresh observation the
caller supplies after actually deleting.

## Deliberate scope limits

- **No tenant I/O of any kind ships in this plugin** — no PnP, no CSOM, no
  raw network call, enforced by
  `test_no_live_pnp_or_csom_or_network_transport_ships`.
- Field-value resolution (e.g. resolving a `lookup_list_key` to a real live
  lookup-list id) is the caller's responsibility, not this module's — that
  resolution is itself tenant I/O.
- This plugin does not collect current tenant state; see
  `docs/reports/phase-9-reusable-sharepoint-plugin-extraction/remaining-capability-roadmap.md`
  Rank 1 for the (not-yet-designed) collection gap this plugin's
  `CurrentState` input assumes is filled by the caller.

## Provenance

Adapted from an originating SharePoint migration repository's shared field/
content-type/list helper libraries, plus the reconcile/duplicate-detection/
fail-loud *pattern* (not any project content) of a separate reset-and-
provision script. See
`docs/reports/phase-9-reusable-sharepoint-plugin-extraction/provenance.md`
for the full record, including what was deliberately not ported.

## Install

```bash
pip install -e plugins/sharepoint-provisioning
python3 -m pytest plugins/sharepoint-provisioning/tests/ -q
```
