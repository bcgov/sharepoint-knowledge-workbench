# Wave 6 — Final Fixture Migration Ledger and Evidence-Safety Classification

**Date:** 2026-08-01

## Fixture migration

Each plugin's `tests/fixtures/` directory carries only the small, synthetic `.docx` fixtures
(`small_single.docx`, `repeated_headings.docx`, etc.) that its own moved test files reference —
these moved wholesale alongside their consuming test files in Waves 2-5 (`git mv`, no separate
fixture-only step was needed since fixtures live under each plugin's own `tests/` tree already).
No fixture was duplicated across plugins: every plugin's `tests/fixtures/` contains exactly the
files its own tests import, confirmed by grep during each wave's test-migration pass.

## Evidence-safety classification (Step 2)

The real CEIS manual evidence (`runs/ceis-manual-v2/`, ~248MB tracked, `intake/CEIS MANUAL -
working version.docx`, ~92MB) is **not duplicated** anywhere by this refactor:

- `tests/golden-master/ceis/manifest.json` (new, Wave 6) references `runs/ceis-manual-v2/` **by
  path and content-hash only** — it records the source docx's sha256 and two tree-hashes computed
  over that existing evidence directory, never a copy of the directory's contents.
- `tests/integration/test_full_ceis_pipeline_across_plugins.py` reads `intake/CEIS MANUAL -
  working version.docx` directly (the existing tracked source) and writes its own conversion
  output to `tmp_path` (pytest's ephemeral temp directory, never committed) — it does not write
  into or duplicate `runs/`.
- `docs/superpowers/plans/phase-4-5-evidence/wave-6-golden-master-manifest.json` is the
  authoritative copy of the same hash record; `tests/golden-master/ceis/manifest.json` is a
  test-local copy of the same values (small, hashes only, not evidence) kept alongside the test
  that consumes it, per the plan's own Step 5 file list.

No new large binary evidence was added to git by this wave.
