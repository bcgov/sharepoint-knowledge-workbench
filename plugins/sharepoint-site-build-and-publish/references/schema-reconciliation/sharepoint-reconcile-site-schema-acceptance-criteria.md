# Acceptance Criteria: sharepoint-reconcile-site-schema

- Skill slug: `sharepoint-reconcile-site-schema`.
- Target plugin: `sharepoint-site-build-and-publish`.
- Purpose: Reconciles a whole declarative SharePoint provisioning schema (site columns, content types, target lists) against caller-supplied current state, detects duplicate-titled lists before any delete, and gates any real write behind dry-run-by-default, an explicitly injected executor and a plan-derived confirmation token. Use for whole-schema reconciliation and the gated apply.

## Constraints honored

- Four write gates, structural not advisory: dry-run by default; an `executor(step, detail)` must be injected (else `ExecutorRequired`); a real apply needs `confirm=plan.confirmation_token` (else `ConfirmationRequired`); and duplicate-titled lists unconditionally block execution (`DuplicateListsBlockProvisioning`, whatever the token).
- Never assume a delete worked: `verify_deletion_complete` raises `DeletionVerificationFailed` if a deleted object still exists.
- Apply only after the user reviews the plan and any blocking findings are resolved. The real executor is the `sharepoint-site-build-and-publish` plugin's `spo-provision-list.ps1`; this skill ships no tenant transport.
- Run from this skill's root with `scripts/` on `sys.path`. Standard library only.

## Verification passes

- The plan outcome is `OBSERVED` (changes planned) or `EMPTY` (already matches); `FAILED` with a blocking finding means it cannot be applied. After an apply, confirm the outcome and that each deleted object is gone.
- Focused plugin tests for this skill pass.
