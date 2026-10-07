# Acceptance Criteria: workbench-resolve-document-paths

- Skill slug: `workbench-resolve-document-paths`.
- Target plugin: `sharepoint-workbench-setup`.
- Purpose: Resolves a DocumentId plus already-parsed connection, document-workflow and publication-profile dicts into the concrete export paths and arguments the two SharePoint analysis plugins (sharepoint-site-assessment, sharepoint-site-migration) need, checks each path against the real filesystem, and prints the resolved invocations. Use when preparing to run those plugins for a document. Never executes a downstream plugin; print, don't execute.

## Constraints honored

- Print, don't execute. Never launch a subprocess, import a downstream plugin module, or run anything on the user's behalf.
- Resolution flows downward only. Never make a downstream plugin read `sharepoint-workbench-setup` config.
- No conditional orchestration: no branching on profile contents beyond the `DocumentId` identity check, no execution ordering.
- Never fabricate a path. An absent file is reported `UNAVAILABLE`.
- Run from this skill's root with `scripts/` on `sys.path`; helper is `scripts/path_resolution.py`. Standard library only.

## Verification passes

- Check `result.overall_status` (`PASS`, `PARTIAL` or `EMPTY`) and each invocation's `status` and `missing` list. A `DocumentId` mismatch against the profiles raises `ValueError`; do not work around it.
- Focused plugin tests for this skill pass.
