# Wave 0 Step 7 — External-Consumer Discovery Report

**Date:** 2026-08-01
**Method:** `tools/phase-4-5-core-plugin-refactoring/wave0_external_consumers.py::find_external_consumer_signals`, cross-referenced against `git worktree list` and each on-disk directory's own `.git` pointer.

## Raw signals

```json
{
  "skills_lock_files": [
    "skills-lock.json",
    ".worktrees/phase-4-native-sharepoint-skills/skills-lock.json",
    ".worktrees/phase-3-governed-sharepoint-pilot/skills-lock.json",
    ".worktrees/phase-3-0-tenant-capability-discovery/skills-lock.json"
  ],
  "claude_settings": [],
  "marketplace_files": [
    ".agents/skills/manage-marketplace/examples/marketplace.json"
  ],
  "worktrees": [
    "phase-3-0-tenant-capability-discovery",
    "phase-3-governed-sharepoint-pilot",
    "phase-4-native-sharepoint-skills"
  ]
}
```

`git worktree list` (run from repo root, current branch `phase-4-5-core-plugin-refactoring`):

```
/Users/richardfremmerlid/Projects/sharepoint-knowledge-workbench  98c1943 [phase-4-5-core-plugin-refactoring]
```

Only the current checkout is registered — none of the three `.worktrees/` directories appear.

## Classification

| Signal | Classification | Evidence |
|---|---|---|
| `.worktrees/phase-4-native-sharepoint-skills` | `ORPHANED_BROKEN_WORKTREE` | `.git` file reads `gitdir: /Users/richardfremmerlid/Projects/manual-conversion-poc/.git/worktrees/phase-4-native-sharepoint-skills` — that path does not exist (this repo was previously at `manual-conversion-poc`, before its rename to `sharepoint-knowledge-workbench`; the worktree registration was never updated after the rename). `git -C` into the directory fails with `fatal: not a git repository`. |
| `.worktrees/phase-3-governed-sharepoint-pilot` | `ORPHANED_BROKEN_WORKTREE` | Same pattern — `.git` points at the same stale `manual-conversion-poc` gitdir path. |
| `.worktrees/phase-3-0-tenant-capability-discovery` | `ORPHANED_BROKEN_WORKTREE` | Same pattern. |
| root `skills-lock.json` | Not an external consumer of the old plugin skill names — a normal repository file, not `.worktrees/`-scoped | Present at repo root; unrelated to worktree classification. |
| `.agents/skills/manage-marketplace/examples/marketplace.json` | Not a live-tracked marketplace registration of the `docx-to-content` plugin — an example fixture belonging to an installed third-party skill (`manage-marketplace`), not this repository's own marketplace | Path confirms it lives under an installed skill's `examples/` directory, not a repo-root marketplace manifest. |

## Conclusion

`NO_CONSUMER_OBSERVED_IN_INSPECTED_SCOPE` for all three `.worktrees/` entries — each is a broken, unregistered worktree pointer left over from before this repository's rename from `manual-conversion-poc`, not an active external consumer of `plugins/docx-to-content`. Per the plan and `start-here.md`, these directories are **not deleted or repaired** as part of Phase 4.5 planning or execution — that is explicitly out of scope for this plan. The presence of a `skills-lock.json` copy inside each broken worktree is evidence only that the directory exists, not evidence of an active consumer; per the plan, Wave 7 Step 1's content-level skill-name search is the actual check for whether anything inside these directories references the compatibility skills, if that step is ever reached.

No `.claude/settings.json` and no repo-root `marketplace.json` exist — no further external-consumer signal found in the inspected scope.
