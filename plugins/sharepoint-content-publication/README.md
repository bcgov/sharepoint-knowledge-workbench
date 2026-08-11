# sharepoint-content-publication

**Classification: `TRANSITIONAL_HOLDING_LOCATION`** — not a completed Phase 4.5 domain plugin. Do
not count this directory toward Phase 4.5's plugin count or exit criteria.

Phase 3's real SharePoint tenant-pilot tooling (`sharepoint_cli.py`, `sharepoint_dry_run.py`,
`sharepoint_package.py`, `sharepoint_reconcile.py`) — the scripts that published all 25 CEIS
topic pages and 319 media files to the live tenant site `AG-CSB-intranet-dev`, with reconciliation
verified 100% MATCH against `actual-state.csv`. It also contains the tenant-safe
`copy-spo-page-between-sites` skill for building a human-reviewed plan to promote an existing SPO
Site Page between sites without raw `.aspx` upload or automatic tenant writes.

**This is not a Phase 4.5-decomposed plugin.** `sharepoint-content-publication` is explicitly out of
Phase 4.5's scope (see `CLAUDE.md`'s Phase 4.5 note — `knowledge-templates` and
`sharepoint-content-publication` remain deferred until working capabilities exist). This directory exists
only because `plugins/docx-to-content/` was deleted in Phase 4.5 Wave 8 and these scripts needed
somewhere to live rather than being deleted along with it — they were carried over wholesale
(`git mv`, imports unchanged), not re-architected to the four-plugin model.

`sharepoint_package.py` still bare-imports `canonical_package` (now `structured-content-assembly`'s
package) — requires `pip install -e plugins/structured-content-assembly` in whatever environment runs
this plugin's tests, same transition-only dependency pattern used throughout Phase 4.5.

Has a `.claude-plugin/plugin.json`/`plugin.yaml` (so it registers as a Claude Code plugin and
loads without error), a transitional `pyproject.toml`, and skill wrappers for the publication/page
promotion planning surfaces. This is still a holding location, not a completed Phase 4.5 domain
plugin. A future session should either build this out as a real `sharepoint-content-publication`
domain plugin (per `docs/vision/`) or fold it into whatever Phase 5+ plan eventually covers
SharePoint delivery.

## Tests

```bash
cd plugins/sharepoint-content-publication
python3 -m pytest tests/ -v
```

Requires `structured-content-assembly` installed (`pip install -e plugins/structured-content-assembly`) in the
same environment.
