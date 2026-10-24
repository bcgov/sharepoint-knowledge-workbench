# Evolution Log — sharepoint-site-migration

Append-only record of every self-evolution event. Written by the `self-evolution` skill.
Do not edit manually except to correct a factual error.

| Date | Tier | Friction / Failure | Patch | Edit Type | Outcome |
|------|------|-------------------|-------|-----------|---------|
# Bulk content/link inventory — 2026-10-05

- Status: RESOLVED — Added the offline Python CSV exporter for static pages, Office external relationships and stored modern-page fields, plus the Online page-field collector. Preserves original URLs, local paths and per-source coverage; PDFs and other parsing gaps remain explicit. Updated existing extraction, conversion, rewrite and validation skills; no new skill identities.
- Verification: link-remediation namespace 195 passed, including fixture-based extraction and mocked page-field export. First live content collection remains pending. Workflow contract: `references/link-remediation/bulk-content-link-workflow.md`.

# Link inventory path resolution and format filtering — 2026-10-06

- Status: RESOLVED — Added `--local-root`, `--path-column`, auto-resolution of `RelativePath`/`LibraryRelativePath`/`ServerRelativeUrl`, `--formats` filtering, `--skip-unsupported` handling, and self-contained `sys.path` bootstrap in `export_link_inventory.py`.
- Verification: bulk link inventory tests (4 passed) and full link test suite (227 passed) verified clean execution.

# Web part XML/JSON extraction, URL unescaping, and host location metadata — 2026-10-06

- Status: RESOLVED — Added support for `.webpart`/`.dwp` XML and `webpart-content.json` extraction, robust SharePoint URL normalization (handling Unicode `\u002f` and HTML entities `&#58;`), CSS `url(...)` background image extraction, and preserved `RelativePath` and `ServerRelativeUrl` hosting coordinates on every `links.csv` record for downstream URL rewriting. Fixed template syntax in `wave-script-template.example.py` resolving CodeQL extraction errors.
- Verification: bulk link inventory tests (5 passed) and full link test suite (228 passed) clean.

# File destination mapping and link rewrite plan generation — 2026-10-06

- Status: RESOLVED — Added `map_file_destinations.py` (authoritative 1:1 destination mapping applying container and folder restructuring rules) and `generate_link_rewrite_plan.py` (cross-referencing extracted links against destination mapping to emit deterministic rewrite plans). Added comprehensive reference document `link-extraction-and-mapping-pipeline.md` and wired symlinks into `sharepoint-update-page-links` and `sharepoint-extract-links`.
- Verification: destination mapping and rewrite planning unit tests (1 passed) and full link test suite (229 passed) clean.

# Mapping safety and rewrite fidelity — 2026-10-06

- Status: RESOLVED — The mapper and planner now reject output paths that alias their input files. Rewrite planning preserves query strings and fragments from the original link when the resolved URL omits them. Refactored the new parser and mapping orchestration to meet hard complexity limits, generalized the pipeline and skill examples, and documented that custom list-item fields require a separate export.
- Verification: link-related plugin tests (237 passed), Python compilation, and local mapping of the supplied library inventory (1,461 files; 140 ASPX files renamed; 1,461 unique source paths; all targets under the requested library/folder path). Symlink diagnosis reported all links OK. No SharePoint writes were performed.
- Audit limitations: the workspace conventions audit still reports pre-existing violations across all seven plugins; the changed mapper/planner have no hard-limit errors (only soft-threshold warnings). The plugin audit utility stopped before auditing because its installed skill is missing `references/skill-authoring-contract.json`.

# Plugin audit acceptance criteria and link fixes — 2026-10-06

- Status: RESOLVED — Added per-skill acceptance criteria references for the audited skills and registered their file-level spokes in `symlinks.json`. Corrected the inventory schema reference and stale table-of-contents anchor, and added the plugin README file tree.
- Verification: canonical plugin audit passed, symlink audit reported all links OK, focused link tests passed (237 passed), and `git diff --check` passed.
