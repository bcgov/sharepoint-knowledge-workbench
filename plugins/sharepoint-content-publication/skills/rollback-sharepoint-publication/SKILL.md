---
name: rollback-sharepoint-publication
description: Builds a human-actionable rollback plan reversing a prior publication's exact actions, package-scoped to one document. Performs no tenant writes.
---

# rollback-sharepoint-publication

## Purpose

Given a prior `PublishPlan`, produces a `RollbackPlan` — the exact set of targets to remove — for
a human to execute manually. **Does not delete anything itself.** Package-scoped: only reverses
the named `document_id`'s own actions, never another document's — rejects a mismatched
`document_id` rather than silently rolling back the wrong document.

## Why this skill produces a plan instead of executing a rollback

Same architectural reason as `publish-markdown-to-sharepoint`/`publish-aspx-to-sharepoint`: this
plugin's Phase 3 design is package-only/zero-tenant-I/O, and real tenant writes (including
deletions) remain gated behind Stage 3.4.3's unapproved write-identity decision.

## Input boundaries

- `document_id` must match the supplied `PublishPlan`'s own `document_id` exactly — a mismatch
  raises `PlanError` rather than producing a plan for the wrong document.

## Prohibited scope

- Zero tenant I/O.
- Does not perform the removal — a human (or a future, separately-authorized skill) executes the
  plan, matching `rollback-sharepoint-native-skill`'s safety-first pattern in
  `sharepoint-agents-and-skills` (dry-run/plan-first, confirmation before any actual deletion).

## Scripts

- `../../scripts/sharepoint_publish_plan.py` (`build_rollback_plan`)

## Tests

- `../../tests/unit/test_sharepoint_publish_plan.py` — includes the cross-document-mismatch
  rejection test (a real safety property, not a hypothetical edge case).
