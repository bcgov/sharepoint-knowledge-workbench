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


