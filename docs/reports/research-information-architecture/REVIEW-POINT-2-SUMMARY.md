# Review Point 2 — Migration Implementation Preparation

**Purpose:** Orientation for reviewing the migration Python implementation against the approved corpus manifest. Not a duplicate source of truth — `research-migration-manifest.json` is authoritative for the "what," `migrate.py` is authoritative for the "how."

**Status: EXECUTION NOT AUTHORIZED. Tests pass; dry-run succeeds against the real repository; zero corpus files touched.**

---

## 1. What Changed Since Review Point 1

- **vis-004 read in full** (982 lines) and compared section-by-section against vis-003. Confirmed strict content subset — zero unique content requires extraction before archiving.
- **9 architecture decisions resolved** with documented evidence and rationale (see manifest's `architecture_decisions_resolved` block).
- **All 56 entries assigned an operation, destination, and filename** — but not all reach `approved` status. Destination status is honest, not inflated:

| destination_status | Count | Meaning |
|---|---|---|
| `approved` | 10 | Execution-ready — all 10 are `retain` (no filesystem action). **Zero moves are currently approved.** |
| `recommended` | 30 | High-confidence proposal, not yet approved for execution |
| `tentative` | 16 | Lower-confidence (mostly <20%-read entries), explicitly flagged |

**This is deliberate, not a shortfall to apologize for.** Per your instruction — "No null or tentative destination values for entries proposed for execution" — the execution set is strictly `approved` only. The migration tool enforces this at runtime (`build_plan(require_approved=True)`), tested explicitly.

---

## 2. Real Bug Found and Fixed

The dry-run against the real repository caught a genuine defect on its **first run**: `arch-011` (`templates/components/README.md`) collided case-insensitively with `arch-001` (the legacy folder's own `README.md`) because I had flattened all legacy files into one destination folder without preserving the original `templates/components/`, `templates/content/`, `templates/examples/` subfolder structure. Fixed; second dry-run succeeds. This is exactly the validation working as designed.

---

## 3. Migration Tool

`temp/research-ia-migration-tool/migrate.py` — subcommands: `validate`, `dry-run`, `execute`, `verify`, `rollback`.

**Safety properties, all tested:**
- Dry-run is the default expectation; `execute` requires explicit invocation
- Preflight fails closed: missing source, hash mismatch, or destination collision (case-insensitive) all raise `MigrationError` before any change — no partial continuation
- Only `destination_status == "approved"` entries enter the execution set — tested with both `recommended` and `tentative` inputs to confirm exclusion
- Excluded trees (`docs/superpowers/`, `docs/reports/`, `plugins/`) cannot be touched even if a manifest entry somehow targeted them — tested
- `execute` uses `git mv`, verifies pre/post hash equality (aborts if a "move" silently changed content), generates a rollback map
- `rollback` reverses using that map
- `verify` checks a completed execution's report against the actual filesystem state

**Known limitation — explicitly documented and tested, not hidden:** reference rewriting (Markdown links, `SKILL.md` citations, `CLAUDE.md` sections) is **not yet implemented**. `test_reference_updates_point_to_final_paths` currently asserts this gap directly rather than pretending it's solved. **This must be built before any real move/rename entry is promoted to `approved`.**

---

## 4. Test Results

```
16/16 passed (temp/research-ia-migration-tool/tests/test_migrate.py)
```

Run against throwaway git fixture repositories created per-test — never the real corpus. Covers: dry-run causes zero changes, hash-mismatch/missing-source/collision all stop processing, unapproved and incomplete entries rejected, excluded paths protected, moves preserve content+hash, second run fails closed (doesn't duplicate), execution report matches operations, verify passes post-execute, rollback restores original location.

---

## 5. Dry-Run Result Against the Real Repository

```
Total entries in manifest: 56
Entries with destination_status='approved' (execution set): 10
  [retain] arch-015, arch-016, arch-017, diag-001..005, diag-010, vis-011
```

All 10 are `retain` — the dry-run correctly reports **zero filesystem operations** since no moves are approved. `git status --short` confirms zero corpus files touched (only this session's own IA-artifact edits appear).

---

## 6. Unresolved Decisions Requiring Your Approval

1. **Promote which `recommended`/`tentative` entries to `approved`?** This is the actual next decision — nothing moves until you do this. The disposition report (`file-by-file-disposition-report.md`) lists all 56 with their current status and confidence basis.
2. **Reference-rewriting implementation** — must be built and tested before any move/rename entry is approved; not yet scoped in detail.
3. **`docs/diagrams/` split execution** — decision made (split 06-08→near vis-009, 09→near vis-010), but the exact target paths within `docs/vision/` weren't finalized (subfolder? flat? prefixed filename?).
4. **`docs/research/` subject-folder population** — 6 domains proposed; `strategic-planning-vision` was tentatively used for `res-004` but is not one of the original 6 `docs/research/` subfolders — flagged as unresolved during the assignment pass, not silently forced into a slot.
5. **`arch-007`/`arch-008` stub disposition** — delete vs. complete, unresolved, out of migration scope.
6. **`vis-009`/`vis-010` filename-prefix correction** — not executed.
7. **CLAUDE.md Section 0 defect** (points at vis-002's superseded body text) — documented, not fixed.
8. **2 broken references** (`.agent/rules/plugin-architecture-policy.md`, `vis-006`) — documented, not fixed.
9. **`res-012` and `arch-005`** — lowest-confidence, highest-impact entries (4% read each); explicitly held at `tentative` rather than rushed to `approved` given `res-012`'s 2 live plugin dependents.

---

## 7. What Has NOT Been Done

- No files moved, renamed, archived, or consolidated in the real repository
- No references updated
- No source document content edited
- No directories created
- No branch push, no PR
- No entry promoted to `approved` beyond the 10 already-safe `retain` confirmations

