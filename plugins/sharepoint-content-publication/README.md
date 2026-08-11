# sharepoint-content-publication

SharePoint tenant publication and page-promotion tooling: packages a
rendered publication output, dry-runs/executes the upload plan, reconciles
it against live tenant state, copies/promotes SPO Site Pages between sites,
and converts classic pages to modern pages (single-page or bulk, with
post-run validation).

**Originally a Phase 4.5 transitional holding location** (Phase 3's
tenant-pilot scripts carried over wholesale when `plugins/docx-to-content/`
was deleted in Wave 8) — since built out into a real domain plugin across
several sessions, most recently 2026-08-11.

```
plugins/sharepoint-content-publication/
├── scripts/
│   ├── canonical_package.py / dispositions.py / hashing.py / publication_map.py  # symlinked from structured-content-assembly
│   ├── sharepoint_cli.py / sharepoint_dry_run.py / sharepoint_package.py /
│   │   sharepoint_publish_plan.py / sharepoint_reconcile.py / sharepoint_upload.py  # planning-only Python
│   ├── spo-page-copy-plan.ps1           # real executor: Copy-PnPFile + Rename-PnPFile
│   ├── spo-upload-plan.ps1              # real executor: Add-PnPPage/Add-PnPPageTextPart/Publish-PnPPage
│   ├── spo-convert-page-to-modern.ps1   # real executor: ConvertTo-PnPPage + caller-supplied field mapping
│   ├── spo-convert-pages-bulk.ps1       # real executor: subprocess-per-page orchestrator, resumable manifest
│   └── spo-validate-page-conversion.ps1 # real, read-only post-run validator
├── agents/
│   └── sharepoint-validation-agent.md
└── skills/
    ├── copy-spo-page-between-sites/    # + real executor (spo-page-copy-plan.ps1)
    ├── upload-content/                 # + real executor (spo-upload-plan.ps1, page-creation path only)
    ├── convert-page-to-modern/         # new
    ├── execute-page-bulk-migration/    # new
    ├── validate-page-migration/        # new
    ├── publish-aspx-to-sharepoint/
    ├── publish-markdown-to-sharepoint/
    ├── reconcile-sharepoint-publication/
    ├── rollback-sharepoint-publication/
    └── validate-sharepoint-publication/
```

## What's real vs. planning-only

Several `.py` modules (`sharepoint_publish_plan.py`, `sharepoint_package.py`,
`sharepoint_upload.py`) are deliberately planning-only -- they build a plan
JSON but perform zero tenant I/O, matching this plugin's plan/apply safety
split. The `.ps1` scripts listed above are the real executors: dry-run by
default, real writes gated behind `-Execute` plus a script-specific
confirmation token (e.g. `COPY-SPO-PAGE`, `UPLOAD-SPO-PLAN`,
`CONVERT-SPO-PAGE`, `CONVERT-SPO-PAGES-BULK`).

**Still planning-only, not yet built**: raw file/asset upload to a document
library (`Add-PnPFile`, distinct from page creation) -- `sharepoint_upload.py`
covers this conceptually but has no real executor behind it yet. See
`.agent/map-debt.md`'s 2026-08-11 entries for the full history.

## Real platform constraints recorded

- `Copy-PnPPage`'s `-SourceSite`/`-DestinationSite` parameter set does not
  exist in current PnP.PowerShell, and cross-site-collection copy via that
  cmdlet requires SharePoint Administrator/admin-center access that
  `Copy-PnPFile` does not. `spo-page-copy-plan.ps1` uses `Copy-PnPFile` +
  `Rename-PnPFile` instead, confirmed against the real installed module's
  `Get-Help` output, not assumed.
- `ConvertTo-PnPPage`'s `-UrlMappingFile`/`-SkipUrlRewriting` only apply to
  cross-site transformations; same-site conversion (this plugin's scope)
  does not rewrite embedded links -- run `sharepoint-link-remediation`
  separately afterward if needed.

## Tests

```bash
cd plugins/sharepoint-content-publication
python3 -m pytest tests/ -v
```

Requires `structured-content-assembly` installed
(`pip install -e plugins/structured-content-assembly`) in the same
environment. `.ps1` scripts are verified via PowerShell AST parse-check and
dry-run (no live tenant needed) rather than pytest -- see each script's own
`.EXAMPLE` block.
