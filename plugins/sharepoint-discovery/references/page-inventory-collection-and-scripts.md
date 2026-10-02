# Page inventory: collection and scripts

## Contents

- [Collecting a fresh export](#collecting-a-fresh-export)
- [Read-only scope](#read-only-scope)
- [Scripts](#scripts)
- [Provenance](#provenance)

## Collecting a fresh export

`collect-sharepoint-page-inventory.ps1` connects interactively (delegated auth, per the
repository's `sharepoint-ps1-authentication-convention.md` rule) to a live site and writes a
`page-inventory.json` in the exact shape `page_inventory_analysis.py` consumes. Any other source
in the same JSON shape also works. It covers the Site Pages library only in this first pass;
list-form (`NewForm`/`EditForm`/`DispForm`) scanning is not implemented (`-IncludeListForms`
currently warns and no-ops).

```bash
pwsh -File scripts/collect-sharepoint-page-inventory.ps1 -SiteUrl "https://tenant.sharepoint.com/sites/Test" -OutputPath page-inventory.json
```

## Read-only scope

`page_inventory_analysis.py` makes no tenant writes and no network access. The collector does
connect to a live tenant but only calls read cmdlets (`Get-PnP*`): zero tenant writes.

## Scripts

- `scripts/collect-sharepoint-page-inventory.ps1`: real, read-only PnP.PowerShell collector.
- `scripts/page_inventory_analysis.py`: `run`, `analyse`, `generate_report`, `load_rules`,
  `compute_complexity`, `disposition_hint`.
- `scripts/discovery_inputs.py`: `DiscoveryStatus`, `DiscoveryOutcome`, `load_json_input`,
  `require_output_dir`.
- Also bundled, not covered by the original documentation: `Get-WorkbenchConnectionConfig.ps1`
  (resolves `config.psd1` into one flat object, dot-sourced by the collectors),
  `analyse_aspx_content.py`, `analyze-aspx-webparts.ps1`, `diagnose-page.ps1`.

## Provenance

Adapted from `sp-discovering-pages` and `sp-analysing-aspx-pages` in the originating SharePoint
migration repository. Source repository only:
`docs/reports/phase-9-reusable-sharepoint-plugin-extraction/provenance.md`.
