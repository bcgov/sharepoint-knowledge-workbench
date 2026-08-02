# Wave 8 — Removal Gate Checklist

**Date:** 2026-08-01

- [x] `wave-6-final-test-migration-ledger.md` / fixture ledger: zero unresolved entries.
- [x] Contract distribution tests pass in isolation — N/A: no shared contracts distribution exists
      under the corrected model (see `wave-2-contract-materialization-correction.md`); each
      plugin's own contract module is tested as part of that plugin's own suite.
- [x] Combined four-distribution install still passes (`combined_install_check.py` re-run):
      `{'source-document-extraction': 0, 'knowledge-analysis': 0, 'canonical-knowledge': 0, 'knowledge-publication': 0}`.
- [x] Golden-master integration test passes with zero skips, real hashes recorded (unchanged since
      Wave 6 — `wave-6-golden-master-manifest.json`; re-run to confirm: PASSED).
- [x] Four plugin wheels build and install cleanly, each with zero upstream-plugin cross-installs
      (`isolated_install_check.py`, one run per plugin, this wave — all four PASS with correct
      import-package names: `extraction`, `analysis`, `canonical_knowledge`, `knowledge_publication`).
- [x] `wave-0-live-reference-report.md` re-scanned: only historical/planning-doc references to
      `plugins/docx-to-content` remain (specs, plans, evidence docs, the target-architecture
      diagram's as-built description of the now-removed transitional layer, and
      `sharepoint-publication/README.md`'s own historical note about where it came from) — no
      live, executable reference. Six stale docstring pytest-invocation paths in
      `source-document-extraction/tests/unit/*.py` fixed to their real current location.
- [x] Wave 7 external-consumer re-scan: zero unaccounted-for consumers, including the three
      `.worktrees/` entries (still `ORPHANED_BROKEN_WORKTREE`, unchanged since Wave 0/7).
- [x] No package `pyproject.toml`/metadata references `plugins/docx-to-content`.

## A real, unplanned discovery: `sharepoint_*.py` was not migration-covered

`plugins/docx-to-content/scripts/sharepoint_cli.py`/`sharepoint_dry_run.py`/`sharepoint_package.py`/
`sharepoint_reconcile.py` — the real Phase 3 SharePoint tenant-pilot tooling (verified 100% MATCH
reconciliation against a live tenant) — were never part of the four-plugin Phase 4.5 Known File
Inventory (`sharepoint-publication` is explicitly deferred per `CLAUDE.md`). A literal
`git rm -r plugins/docx-to-content/` would have deleted this working code with nowhere for it to
land. Flagged to the human before proceeding; human chose to relocate first. The four
`sharepoint_*.py` scripts, their four test files, and `docs/sharepoint-actual-state-csv-format.md`
were moved wholesale (`git mv`) to a new `plugins/sharepoint-publication/` holding location —
**not** a real Phase 4.5 domain plugin (no `pyproject.toml`/`.claude-plugin/` yet, documented
explicitly in its own README as out of Phase 4.5's scope) — before the remainder of
`plugins/docx-to-content/` was removed. 20/20 of its tests still pass (requires
`canonical-knowledge` installed, same transition-only dependency pattern as everywhere else in
Phase 4.5).

Non-contract reference documentation with no natural per-plugin home
(`content-authoring-guide.md`, `extraction-triggers.md`, `future-output-profiles.md`,
`generated-elements.md`, `known-pandoc-gaps.md`, `pandoc-docx-setup.md`,
`supported-markdown-profile.md`, plus the pre-Wave-4 `canonical-contract.md`/
`publication-map-contract.md` and the `templates/` directory) was moved to
`docs/architecture/docx-to-content-legacy-references/` rather than deleted, per
`self-evolution-policy.md`'s no-autonomous-deletion rule — nothing was lost, only relocated.

`tests/contract/test_future_output_profiles.py` was retired (removed with the rest of
`docx-to-content/tests/`, not relocated): it asserted structural/purity properties of the
now-removed transitional plugin's own `scripts/`/`cli.py`/`renderers/` layout and registry
contents — properties that no longer have a subject to assert about once that plugin is gone. Its
target document (`future-output-profiles.md`) is preserved at the legacy-references location
above; only the plugin-structure assertions were retired.
