# sharepoint-discovery

Read-only analysis of exported classic SharePoint inventories: per-page
migration complexity scoring, functional grouping of web-part code, site
navigation depth analysis, custom-form classification, and permissions
auditing.

**Zero SharePoint tenant I/O.** Every skill in this plugin reads an export
you already have and writes analysis artifacts to a directory you name. It
does not connect to a tenant, and nothing collects the exports it consumes —
see `docs/architecture/sharepoint-engineering-plugin-set.md` for the
end-to-end flow and the collection gap this implies.

```
plugins/sharepoint-discovery/
├── scripts/
│   ├── discovery_inputs.py         # shared DiscoveryStatus/DiscoveryOutcome vocabulary
│   ├── page_inventory_analysis.py
│   ├── webpart_code_analysis.py
│   ├── navigation_analysis.py
│   ├── forms_analysis.py
│   ├── permissions_analysis.py
│   └── assets/
│       ├── webpart-migration-rules.json
│       └── form-classification-rules.json
├── skills/
│   ├── analyze-page-inventory/
│   ├── analyze-webpart-code/
│   ├── analyze-site-navigation/
│   ├── analyze-custom-forms/
│   └── analyze-permissions/
└── tests/
```

## Honest outcomes

Every skill reports one of: `OBSERVED`, `EMPTY`, `PARTIAL`, `UNAVAILABLE`,
`FORBIDDEN`, `FAILED`. A missing input is `UNAVAILABLE` and no output
directory is created; an empty result is `EMPTY`, never a silent pass.

## Coverage

5 of 7 implemented discovery capabilities in the source repository this
plugin was extracted from. `sp-discovering-site-structure` was **not**
extracted — its backing scripts are live-tenant collectors, out of scope for
a read-only, disk-only plugin. `sp-synthesizing-discovery` was **not**
extracted — its source hardcodes fabricated headline metrics. See
`docs/reports/phase-9-reusable-sharepoint-plugin-extraction/
remaining-capability-roadmap.md` for the full disposition of every source
capability, and `provenance.md` in the same directory for what was extracted
and how.

## Install

```bash
pip install -e plugins/sharepoint-discovery
python3 -m pytest plugins/sharepoint-discovery/tests/ -q
```
