# Wave 7 — Compatibility Facade Retirement Record

**Date:** 2026-08-01
**Status:** ✓ COMPLETE (human pre-authorized execution of Waves 5-8 with per-wave commits; direct
execution, not yet independently reviewed).

## Step 1: Re-run external-consumer discovery

Re-checked all three `.worktrees/` entries and `git worktree list` against Wave 0's classification
(`wave-0-external-consumer-report.md`):

```
$ git worktree list
/Users/richardfremmerlid/Projects/sharepoint-knowledge-workbench  101cd20 [phase-4-5-core-plugin-refactoring]
```

Only the current checkout is registered — unchanged from Wave 0. Each `.worktrees/` directory's
`.git` file still points at the same stale, nonexistent `manual-conversion-poc` gitdir path:

- `.worktrees/phase-4-native-sharepoint-skills` → `ORPHANED_BROKEN_WORKTREE` (unchanged)
- `.worktrees/phase-3-governed-sharepoint-pilot` → `ORPHANED_BROKEN_WORKTREE` (unchanged)
- `.worktrees/phase-3-0-tenant-capability-discovery` → `ORPHANED_BROKEN_WORKTREE` (unchanged)

No worktree has changed status since Wave 0. `git -C .worktrees/<name> status` still fails with
`fatal: not a git repository` for all three.

A content-level search for each of the four skill names (`analyze-document`, `convert-document`,
`render-content`, `orchestrate-conversion`) across the repository found references only in: this
repo's own docs (specs, plans, evidence, vision, research notes), the four skills' own
cross-references to each other, and — for `render-content` only — the new
`plugins/knowledge-publication/skills/render-content/` (a different plugin's differently-scoped
skill of the same name, added in Wave 5; not a consumer of `docx-to-content`'s skill).
**`NO_CONSUMER_OBSERVED_IN_INSPECTED_SCOPE`, same conclusion as Wave 0.**

## Step 2: Apply confirmed disposition per skill

Per `wave-1-decisions.json`'s `original_skill_dispositions`, reassessed here using the confirmed
zero-external-consumer finding above:

| Skill | Wave 1 disposition | Wave 7 decision | Rationale |
|---|---|---|---|
| `orchestrate-conversion` | `RETAINED_PUBLIC_ORCHESTRATOR` | **RETAIN** (pre-decided, not reassessed) | Explicitly the intentional public workflow orchestrator per Wave 1's approval; not a candidate for retirement. |
| `analyze-document` | `TEMPORARY_COMPATIBILITY_WRAPPER` | **RETAIN** | See below. |
| `convert-document` | `TEMPORARY_COMPATIBILITY_WRAPPER` | **RETAIN** | See below. |
| `render-content` (docx-to-content's) | `TEMPORARY_COMPATIBILITY_WRAPPER` | **RETAIN** | See below. |

**Why the three "temporary" wrappers are retained, not retired, in Wave 7:**

1. **Nothing is actually broken or dead to retire.** `analyze-document`/`convert-document`/
   `render-content` are pure documentation over `cli.py`'s `analyze`/`confirm`/`convert`/`render`
   subcommands. `cli.py` itself is unchanged by Waves 2-6 in its command surface — every
   subcommand still works exactly as documented, now via compatibility-shim bare imports resolving
   to the four installed real plugins (verified: `docx-to-content`'s full 170/171-test suite,
   including `test_cli.py`, passes end to end through Wave 6). There is no facade pointing at
   something that no longer exists.
2. **`cli.py`'s own compatibility shims are load-bearing, not optional.** `import convert`/
   `import package`/`import canonical_package` (Wave 4) and `from renderers import ...` (Wave 5)
   are how `cli.py`'s `convert`/`render` subcommands function at all post-extraction — `docx-to-
   content` no longer has this code locally. These cannot be "removed" without removing the
   subcommands themselves, which would break `docx-to-content` as a whole before Wave 8's
   decommission decision is made. The plan's Wave 7 "Files" list mentioning
   `plugins/docx-to-content/scripts/*.py` most plausibly describes retiring Python-level shims for
   a skill that is ALSO being retired at the same time (so the shim's only caller disappears with
   it) — since no skill is being retired here, no shim becomes dead code to remove.
3. **`orchestrate-conversion`'s own doc explicitly depends on the other three's continued
   existence**: "It does not replace those three skills or their CLI contract — it is a thin
   sequencing layer over the exact same `python -m scripts.cli` commands they document." Removing
   them would leave `orchestrate-conversion` referencing skills that no longer exist, for zero
   compensating benefit (no external consumer was waiting on their removal; no dead code exists to
   delete).
4. **Per self-evolution-policy.md**, deletions require explicit justification tied to real
   staleness or replacement, not just an original plan label. `TEMPORARY_COMPATIBILITY_WRAPPER`
   described their *origin* (compatibility wrappers written during Phase 1, predating any of this
   plugin-extraction work), not evidence that they are now unused — the zero-external-consumer scan
   confirms no external caller either way, so retention carries no risk and retirement carries no
   benefit until `docx-to-content` itself is decommissioned in Wave 8, at which point all four
   skills (including `orchestrate-conversion`) are removed together as part of that single, larger,
   explicitly-approved deletion.

**Conclusion: no skill file changes in Wave 7.** This is a valid, documented outcome of the
"reassessed... not pre-approved for removal" instruction in `wave-1-decisions.json` — reassessment
can conclude "retain," not only "retire."

## Step 3: Run the complete repository suite

```
source-document-extraction:     78 passed
knowledge-analysis:              70 passed
canonical-knowledge:            173 passed
knowledge-publication:           49 passed
docx-to-content:                170 passed, 1 skipped
repo-root tests/integration/:     1 passed
tools/phase-4-5-core-plugin-refactoring: 42 passed (40 fast + 2 slow, including combined_install_check)
```

All green, unchanged from Wave 6 (no code changed in this wave).

**Wave 7 Gate:** met. Worktree re-classification confirms no `.worktrees/` entry changed status
since Wave 0. All four skill dispositions reassessed using real, re-confirmed consumer evidence
(not merely re-stamping Wave 1's proposal). Complete repository suite green.
