# Site navigation: collection, template and scripts

## Contents

- [Collecting a fresh export](#collecting-a-fresh-export)
- [Summary template](#summary-template)
- [Scripts](#scripts)
- [Provenance](#provenance)

## Collecting a fresh export

`collect-sharepoint-site-navigation.ps1` connects to a live on-prem SharePoint 2016 site (REST
plus NTLM/Kerberos, no PnP/CSOM; the repository's `sharepoint-ps1-authentication-convention.md`
rule explains why on-prem uses this instead of `Connect-PnPOnline`). It writes a
`navigation.json` in the exact `{topNav, quickLaunch}` shape `navigation_analysis.py` consumes,
each node shaped `{title, url, children}`. It also writes a fuller `site-chrome.json` (site
title, logo URL, master page path, locale, breadcrumb ancestor chain) for reference and
reporting; `navigation_analysis.py` reads `navigation.json` only. Read-only: REST GETs only,
zero writes to the tenant.

```bash
pwsh -File scripts/collect-sharepoint-site-navigation.ps1 -SiteUrl "https://sp2016.example.org/sites/Legacy" -OutputDir ./nav-export -UseDefaultCredentials
```

## Summary template

`assets/site-navigation-chrome-summary-template.md` is a Markdown template for writing up the
collected data as a reviewer-facing architecture summary (top nav table, quick launch, master
page chrome). Fill its `{{...}}` placeholders from `site-chrome.json` and `navigation-plan.json`.

## Scripts

- `scripts/collect-sharepoint-site-navigation.ps1`: real, read-only on-prem REST collector.
- `scripts/navigation_analysis.py`: `run`, `analyse`, `generate_report`.
- `scripts/discovery_inputs.py`: `DiscoveryStatus`, `DiscoveryOutcome`, `load_json_input`,
  `require_output_dir`.

## Provenance

Adapted from `sp-discovering-navigation` in the originating SharePoint migration repository.
Source repository only: `docs/reports/phase-9-reusable-sharepoint-plugin-extraction/provenance.md`.
