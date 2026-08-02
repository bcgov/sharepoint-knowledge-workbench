# Phase 4.5 Exit Statement

**Date:** 2026-08-01 (updated 2026-08-02, Wave 9 — see below)
**Branch:** `phase-4-5-core-plugin-refactoring` (not merged to `main` by this plan — merge is a
separate, explicit human decision).

> **2026-08-02 update:** human review of the merged Wave 1-8 result found real hand-maintained
> editable-source duplication across `canonical-knowledge`/`knowledge-publication` that this
> statement's original text below did not adequately flag as a defect. A follow-up remediation
> (Wave 9) replaced every true duplicate family with managed cross-plugin file-level symlinks
> (source-document-extraction/knowledge-analysis own the canonical files; canonical-knowledge/
> knowledge-publication consume them via `symlink_manager.py`, recorded in `symlinks.json`) and
> extracted the three subset-reimplementation families (`identity`/`chunk_identity`,
> `topic_grouping`/`chunk_grouping`, `plans`/`plan_verification`) into granular canonical modules
> (`identity_core.py`, `topic_boundary_core.py`, `plan_verification_core.py`) also consumed via
> managed symlink. Zero hand-maintained editable-source duplicates remain. See
> `docs/superpowers/plans/phase-4-5-evidence/wave-9-duplication-remediation-report.md` for the
> full before/after audit and verification evidence. The original "Phase 4.5 is complete"
> statement below was premature in exactly the way that review identified — passing tests and
> passing wave gates do not by themselves prove the architecture matches the intended
> zero-hand-duplication model.

The former combined `plugins/docx-to-content/` implementation has been decomposed into four
independently installable, independently testable, domain-scoped plugins
(`source-document-extraction`, `knowledge-analysis`, `canonical-knowledge`,
`knowledge-publication`), each carrying its own materialized contract/schema code rather than
depending on a shared distribution (the original Wave 1 shared-contracts model was corrected
mid-Wave-2; no shared distribution was ever published). The established CEIS workflow
(analyze → confirm → convert → render) is preserved with byte-identical accepted outputs
(`wave-6-golden-master-manifest.json`). Dependency direction is enforced (zero cross-plugin
implementation imports among the four real domain plugins, verified by `dependency_boundary.py`
every wave). Every test and fixture has been dispositioned (`wave-6-final-test-migration-ledger.md`,
`wave-6-final-fixture-migration-ledger.md`). Documentation matches the implemented architecture
(`docs/architecture/phase-4-5-target-architecture.md`, `CLAUDE.md`/`AGENTS.md`/`GEMINI.md`/
`.github/copilot-instructions.md`/`README.md`/`architecture.md`/`start-here.md`, all updated this
wave). The obsolete combined plugin has been removed with explicit human approval (Wave 8 Step 2 —
the user's session-level pre-authorization to execute Waves 5-8 and commit per wave). **Phase 4.5
is complete.**

## Deviations from the original plan, all documented in-line at the wave they occurred

1. No shared `knowledge-workbench-contracts`/`knowledge-workbench-runtime` distribution was ever
   built or published — corrected mid-Wave-2 to each producer plugin materializing its own
   contract; see `wave-2-contract-materialization-correction.md`.
2. Flat `scripts/` layout (bare module names), not `src/<import_name>/` nesting — corrected the
   same session; see `wave-2-flat-scripts-correction.md`.
3. Real cross-plugin-dependency violations found and fixed at Waves 4/5 via local duplication
   (never a shared distribution) — see `wave-4-canonical-knowledge-split-decision.md` and
   `wave-5-knowledge-publication-split-decision.md`. **Superseded in Wave 9**: local
   hand-duplication was itself replaced with managed cross-plugin file-level symlinks — see the
   2026-08-02 update above and `wave-9-duplication-remediation-report.md`.
4. A real bug in `combined_install_check.py` itself (Wave 6) — `build_wheel()`'s
   alphabetical-last-wheel-in-shared-directory selection silently returned the same wheel four
   times — found and fixed before the combined-install gate could be trusted.
5. **`sharepoint_*.py`** (Phase 3's real, tenant-verified SharePoint publication tooling) was
   discovered during Wave 8 to be outside the four-plugin Known File Inventory entirely
   (`sharepoint-publication` is explicitly deferred per `CLAUDE.md`). Flagged to the human before
   deletion; relocated wholesale to a new, explicitly-provisional `plugins/sharepoint-publication/`
   holding location rather than lost — see `wave-8-removal-gate-checklist.md`.
6. Several non-contract reference docs (`content-authoring-guide.md`, `future-output-profiles.md`,
   etc.) had no natural per-plugin home in the four-way split; relocated to
   `docs/architecture/docx-to-content-legacy-references/` rather than deleted.

## Final state (end of Wave 8)

| Plugin | Tests | Isolated-install proof |
|---|---|---|
| `source-document-extraction` | 78 | PASS (`--import-package extraction`) |
| `knowledge-analysis` | 70 | PASS (`--import-package analysis`) |
| `canonical-knowledge` | 173 | PASS (`--import-package canonical_knowledge`) |
| `knowledge-publication` | 49 | PASS (`--import-package knowledge_publication`) |
| `sharepoint-publication` (provisional, not Phase-4.5-scoped) | 20 | not applicable (no `pyproject.toml` yet) |
| `tools/phase-4-5-core-plugin-refactoring` | 42 (40 fast + 2 slow) | — |
| repository-root `tests/integration/` | 1 (golden-master, zero skips) | — |

Combined four-distribution install: zero collisions, all four plugins' own suites pass in the
shared environment.

## Next steps (not part of this plan)

- Build out `sharepoint-publication` as a real Phase 4.5-style domain plugin, or fold it into
  whatever Phase 5+ plan covers SharePoint delivery.
- `knowledge-templates` remains deferred, per `CLAUDE.md`.
- This branch is not merged to `main` by this plan — that is a separate, explicit human decision,
  following the Per-Phase Git & Session Workflow in
  `docs/vision/master-initiative-plan-workstreams-and-phases.md`.
