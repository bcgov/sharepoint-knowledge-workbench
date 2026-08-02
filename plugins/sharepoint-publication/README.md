# sharepoint-publication (relocated, not yet a real Phase 4.5 domain plugin)

Phase 3's real SharePoint tenant-pilot tooling (`sharepoint_cli.py`, `sharepoint_dry_run.py`,
`sharepoint_package.py`, `sharepoint_reconcile.py`) — the scripts that published all 25 CEIS
topic pages and 319 media files to the live tenant site `AG-CSB-intranet-dev`, with reconciliation
verified 100% MATCH against `actual-state.csv`.

**This is not a Phase 4.5-decomposed plugin.** `sharepoint-publication` is explicitly out of
Phase 4.5's scope (see `CLAUDE.md`'s Phase 4.5 note — `knowledge-templates` and
`sharepoint-publication` remain deferred until working capabilities exist). This directory exists
only because `plugins/docx-to-content/` was deleted in Phase 4.5 Wave 8 and these scripts needed
somewhere to live rather than being deleted along with it — they were carried over wholesale
(`git mv`, imports unchanged), not re-architected to the four-plugin model.

`sharepoint_package.py` still bare-imports `canonical_package` (now `canonical-knowledge`'s
package) — requires `pip install -e plugins/canonical-knowledge` in whatever environment runs
this plugin's tests, same transition-only dependency pattern used throughout Phase 4.5.

Has a `.claude-plugin/plugin.json`/`plugin.yaml` (so it registers as a Claude Code plugin and
loads without error), but no `pyproject.toml` and no `skills/` — this is a holding location for
the raw scripts, not an installable Python package or a skill-wrapped plugin yet. A future session
should either build this out as a real `sharepoint-publication` domain plugin (per `docs/vision/`)
or fold it into whatever Phase 5+ plan eventually covers SharePoint delivery.

## Tests

```bash
cd plugins/sharepoint-publication
python3 -m pytest tests/ -v
```

Requires `canonical-knowledge` installed (`pip install -e plugins/canonical-knowledge`) in the
same environment.
