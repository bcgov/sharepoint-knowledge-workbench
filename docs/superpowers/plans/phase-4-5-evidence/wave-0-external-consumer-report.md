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

## Root `skills-lock.json` inspection (added 2026-08-01, human review correction)

The initial pass reported `no .claude/settings.json` / `no marketplace.json` but did not report a
result for the repository-root `skills-lock.json`, which the raw signals list above shows exists
(`"skills-lock.json"` in `skills_lock_files`). Inspected explicitly below, per reviewer instruction
— not assumed either active or stale without inspection.

- **Path:** `skills-lock.json` (repository root)
- **Tracking status:** tracked on `main` (`git ls-files skills-lock.json` confirms); `git log --follow` shows a single commit, `f86352b` — "Initial commit: manual-conversion-poc setup and CEIS Manual conversion" — never modified since. No `updatedAt` timestamp in any entry postdates 2026-07-25.
- **Purpose (from structure, undocumented elsewhere):** a version-1 lockfile with one top-level `skills` object, each entry recording `source` (a GitHub URL or short source name), `sourceType` (`local` or `github`), `computedHash`, and `installedAt`/`updatedAt` timestamps — this is the install-tracking manifest for **externally-installed marketplace skills** (`obra/superpowers`, `richfrem/agent-plugins-skills`, `anthropics/skills`), not a manifest of this repository's own `plugins/` directory.
- **Entries referencing `docx-to-content`:** none. `grep -n "docx-to-content" skills-lock.json` → no match.
- **Entries referencing the four original skills (`analyze-document`, `convert-document`, `render-content`, `orchestrate-conversion`):** none. `grep -n "analyze-document\|convert-document\|render-content\|orchestrate-conversion" skills-lock.json` → no match.
- **Installed/source path:** not applicable — no relevant entry exists to have one.
- **Version/commit information:** file declares `"version": 1"`; every entry's own `installedAt`/`updatedAt` is 2026-07-25, before Task 18's real CEIS pilot cutover and before Phase 4/4.5 existed.
- **Does it appear current:** yes, as a record of *installed third-party skills* (that mechanism is still in active use — `.agents/skills/` exists and is populated) — but it has never tracked `plugins/docx-to-content` at all, at any point in its history, because that plugin was built directly in this repository (per `CLAUDE.md`'s "Skills in use" section — `docx-to-content` was built from scratch in this repo, not installed via the marketplace mechanism `skills-lock.json` tracks).
- **Active consumer signal:** **no** — structurally, this file cannot be a consumer of `plugins/docx-to-content`'s skill names, because it only ever tracks skills installed through the separate marketplace/plugin-installer mechanism, and `docx-to-content` was never installed that way.

**Classification: `NO_RELEVANT_ENTRY`.**

## Conclusion

`NO_CONSUMER_OBSERVED_IN_INSPECTED_SCOPE` for all three `.worktrees/` entries — each is a broken, unregistered worktree pointer left over from before this repository's rename from `manual-conversion-poc`, not an active external consumer of `plugins/docx-to-content`. Per the plan and `start-here.md`, these directories are **not deleted or repaired** as part of Phase 4.5 planning or execution — that is explicitly out of scope for this plan. The presence of a `skills-lock.json` copy inside each broken worktree is evidence only that the directory exists, not evidence of an active consumer; per the plan, Wave 7 Step 1's content-level skill-name search is the actual check for whether anything inside these directories references the compatibility skills, if that step is ever reached.

The root `skills-lock.json` itself was inspected explicitly (see section above, not assumed) and classified `NO_RELEVANT_ENTRY` — it tracks externally-installed marketplace skills, a structurally separate mechanism from `plugins/docx-to-content`, and has zero entries for the plugin or its four skills at any point in its single-commit history.

No `.claude/settings.json` and no repo-root `marketplace.json` exist — no further external-consumer signal found in the inspected scope. `NO_CONSUMER_OBSERVED_IN_INSPECTED_SCOPE` is now stated only after every signal, including the root lock file, was individually inspected.
