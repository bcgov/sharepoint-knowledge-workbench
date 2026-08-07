---
name: analyze-page-inventory
plugin: sharepoint-discovery
description: Analyses an exported classic SharePoint page inventory -- scoring per-page migration complexity, classifying web-part categories, and emitting a disposition hint per page -- using a caller-supplied rules file. Read-only; consumes an export you provide and never contacts a tenant.
allowed-tools: Bash, Read
examples:
  - "python -c \"from page_inventory_analysis import run; print(run(inventory_path='inv.json', rules_path='rules.json', output_dir='out/').status)\""
---

# Analyze Page Inventory

## Trigger and Purpose

Use this skill when planning a classic-to-modern SharePoint migration and you
need to know which pages are cheap to move and which are hard. It consumes a
page inventory already exported from a tenant and produces a scored,
prioritised analysis.

It answers: how complex is each page, which web-part categories appear, and
what is the suggested disposition (migrate as-is, rebuild, retire).

## Rules are data, not code

`load_rules(path)` reads a caller-supplied JSON rules file. Complexity
weights, category classifications, and disposition thresholds are **all**
supplied by you -- **no site-specific migration judgement is built in.** The
source implementation this was extracted from embedded one organisation's
thresholds directly; those are removed.

## Honest outcomes

Every run returns a `DiscoveryOutcome` carrying a `DiscoveryStatus`:
`OBSERVED`, `EMPTY`, `PARTIAL`, `UNAVAILABLE`, `FORBIDDEN`, or `FAILED`.

A missing input file is `UNAVAILABLE` and **no output directory is created** --
the run does not fabricate defaults to appear successful. An empty inventory
is `EMPTY`, never a pass.

## Read-only guarantee

No writes to any tenant, no network access. It reads the export path you name
and writes analysis artifacts to the output directory you name.

## Usage

```bash
python -c "
from page_inventory_analysis import run
outcome = run(inventory_path='page-inventory.json', rules_path='rules.json', output_dir='out/')
print(outcome.status, outcome.detail)
"
```

## Scripts

- `../../scripts/page_inventory_analysis.py` -- `run`, `analyse`, `generate_report`, `load_rules`, `compute_complexity`, `disposition_hint`
- `../../scripts/discovery_inputs.py` -- `DiscoveryStatus`, `DiscoveryOutcome`, `load_json_input`, `require_output_dir`

## Provenance

Adapted from `sp-discovering-pages` / `sp-analysing-aspx-pages` in the
originating SharePoint migration repository. See
`docs/reports/phase-9-reusable-sharepoint-plugin-extraction/provenance.md`.
