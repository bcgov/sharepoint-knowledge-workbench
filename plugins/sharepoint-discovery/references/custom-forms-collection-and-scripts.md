# Custom forms: collection, outcomes and scripts

## Contents

- [Honest outcomes](#honest-outcomes)
- [Collecting a fresh export](#collecting-a-fresh-export)
- [Scripts](#scripts)
- [Provenance](#provenance)

## Honest outcomes

Every run returns a `DiscoveryOutcome` carrying a `DiscoveryStatus`: `OBSERVED`, `EMPTY`,
`PARTIAL`, `UNAVAILABLE`, `FORBIDDEN` or `FAILED`.

A missing forms export or rules file is `UNAVAILABLE` and no output directory is created. An
empty forms export is `EMPTY`, never a pass. An input that isn't a JSON array is `FAILED`.

## Collecting a fresh export

`collect-sharepoint-custom-forms.ps1` connects to a live on-prem SharePoint 2016 site (REST plus
NTLM/Kerberos, no PnP/CSOM; see the repository's `sharepoint-ps1-authentication-convention.md`
rule), checks every list and library's `Forms` folder for non-standard `.aspx` files, downloads
them, and does a best-effort classification (inline `<script>` present -> `hasScript`;
InfoPath/XSN markers -> `formType: InfoPath`). It writes `forms.json` in the exact
`[{listName, isCustomized, hasScript, formType}]` shape `forms_analysis.py` consumes. This
classification is a heuristic starting point, not a substitute for the rules-driven analysis.
Read-only: REST GETs only, zero writes to the tenant.

```bash
pwsh -File scripts/collect-sharepoint-custom-forms.ps1 -SiteUrl "https://sp2016.example.org/sites/Legacy" -OutputDir ./forms-export -UseDefaultCredentials
```

## Scripts

- `scripts/collect-sharepoint-custom-forms.ps1`: real, read-only on-prem REST collector.
- `scripts/forms_analysis.py`: `run`, `analyse`, `generate_report`, `load_rules`.
- `scripts/discovery_inputs.py`: `DiscoveryStatus`, `DiscoveryOutcome`, `load_json_input`,
  `require_output_dir`.
- `scripts/generate-deep-forms-analysis.py`: parses custom-form extractions and writes a deterministic
  `CUSTOM-FORMS-INVENTORY-REPORT.md` (form inventory and modernization dispositions).

## Provenance

Adapted from `sp-discovering-forms` in the originating SharePoint migration repository. Source
repository only: `docs/reports/phase-9-reusable-sharepoint-plugin-extraction/provenance.md`.
