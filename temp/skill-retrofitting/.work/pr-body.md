## Summary
Work-in-progress retrofit of every skill under `plugins/` to the skill authoring standard (`audit-skill` contract v1.0.0). **Draft: please do not merge until all plugins are complete.** Commits are pushed per plugin so nothing is lost.

Tracker: `docs/reports/skill-standard-alignment/tracker.md`. Handoff for another agent: `temp/skill-retrofitting/PLAN.md` and `PROGRESS.md` (force-added, since `temp/` and `docs/reports/` are git-ignored).

## Done so far (9 of 16 plugins, 43 of 104 skills)
`workbench-setup`, `sharepoint-discovery`, `content-assembly`, `content-extraction`, `content-rendering`, `content-structure-analysis`, `sharepoint-content-migration`, `sharepoint-content-publication`, `sharepoint-link-remediation`. Each: `SKILL.md` in the standard layout with Constraints first, detail moved to plugin-root references linked by file-level symlinks, `plugin:` frontmatter corrected, stale install and repo-root paths removed, missing import links added, `task-success.json` added. Strict audit passes in source and installed mode; plugin tests pass.

Also: all 13 audit errors fixed (104 skills pass, 0 fail), `evals.json` + `task-success.json` authored for the 27 skills that had none, marketplace descriptions corrected for `sharepoint-discovery` and `sharepoint-content-publication`, and `sharepoint-link-remediation`'s independence test now exempts the new skill-owned `task-success.json`.

## Caveats
- Authored evals (routing and task-success) are derived from each `SKILL.md`; they have **not** been run against a model.
- Remaining, in order: `sharepoint-migration-planning`, `-page-modernization`, `-page-modernization-execution`, `-provisioning`, `-schema-reconciliation`, `-spfx-authoring`, then `sharepoint-agents-and-skills` last.
- Commits and pushes on this branch use `--no-verify` (authorized by the user) because the new control-plane git guards block non-task branches.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
