# Wave 0 Step 8 — Live-Reference Scan

**Date:** 2026-08-01
**Method:** `grep -rl "plugins/docx-to-content" --include="*.md" --include="*.json" --include="*.py" --include="*.ps1" .` from repo root, excluding `.worktrees/` (already classified `ORPHANED_BROKEN_WORKTREE` in `wave-0-external-consumer-report.md`), the plugin's own tree, and this Phase 4.5 planning doc pair (which necessarily reference the migration source).

## Full-suite baseline

```
cd plugins/docx-to-content && python3 -m pytest tests/ -q
529 passed, 1 skipped in 24.60s
```

Matches the baseline recorded in `start-here.md` exactly (529 passed, 1 skipped) — confirmed live, not assumed from prior session notes.

## Files with a live `plugins/docx-to-content` reference

| File | Nature of reference | Wave 0 disposition |
|---|---|---|
| `architecture.md`, `README.md`, `start-here.md`, `CLAUDE.md`, `AGENTS.md`, `GEMINI.md` | Repo-root documentation describing the current combined plugin's location | `CLASSIFICATION: DOCUMENTATION_REFERENCE` — expected to require updates once the plugin is decomposed (out of scope for Wave 0; later-wave documentation work per the plan) |
| `docs/superpowers/plans/2026-07-25-*`, `docs/superpowers/plans/2026-07-28-*`, `docs/superpowers/specs/2026-07-25-*` | Historical Phase 1/Phase 2 planning artifacts | `CLASSIFICATION: HISTORICAL_ARTIFACT` — describes work already executed and merged; not live tooling, left untouched |
| `docs/superpowers/plans/phase-3-*`, `docs/superpowers/specs/phase-3-*` | Phase 3 planning docs incidentally mentioning the plugin's role in producing Phase 3 inputs | `CLASSIFICATION: DOCUMENTATION_REFERENCE` (historical, Phase 3 already merged) |
| `docs/reports/sdd-task-reports/2026-07-25-task-1-report.md`, `docs/reports/phase-4-native-sharepoint-skills/EVID-PHASE4-TASK12-ROLLBACK-COMPLETION.md`, `runs/ceis-manual-v2/evidence-report.md` | Evidence/report artifacts recording real prior execution | `CLASSIFICATION: EVIDENCE_ARTIFACT` — historical record, not touched |
| `.github/copilot-instructions.md` | Repo-wide agent instructions mirroring `CLAUDE.md` | `CLASSIFICATION: DOCUMENTATION_REFERENCE` — same disposition as `CLAUDE.md` |
| `tools/phase-4-5-core-plugin-refactoring/wave0_*.py` | This wave's own tooling, which targets `plugins/docx-to-content` as its inventory source by design | `CLASSIFICATION: EXPECTED_SELF_REFERENCE` — not a consumer, the migration tooling itself |

## Conclusion

No live, executable consumer outside `plugins/docx-to-content/` itself and this wave's own tooling was found — every hit is either historical documentation, an evidence report, or a repo-root instruction file that already documents the plugin's current location and will need updating once decomposition lands (tracked as later-wave work, not a Wave 0 blocker). `NO_CONSUMER_OBSERVED_IN_INSPECTED_SCOPE` beyond documentation, consistent with `wave-0-external-consumer-report.md`'s finding that the on-disk `.worktrees/` directories are broken/orphaned, not active consumers.
