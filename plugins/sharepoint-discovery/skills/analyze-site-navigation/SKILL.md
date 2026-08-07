---
name: analyze-site-navigation
plugin: sharepoint-discovery
description: Analyses an exported classic SharePoint site navigation tree (top nav and quick launch) -- flattening it with per-node depth and child counts, and computing max-depth statistics -- to produce a navigation architecture summary. Read-only; consumes an export you provide and never contacts a tenant.
allowed-tools: Bash, Read
examples:
  - "python -c \"from navigation_analysis import run; print(run(navigation_path='nav.json', output_dir='out/').status)\""
---

# Analyze Site Navigation

## Trigger and Purpose

Use this skill when planning a classic-to-modern SharePoint migration and you
need to understand how deep and how wide a site's navigation chrome is before
mapping it onto modern hub/global navigation. It consumes a navigation export
already pulled from a tenant (top navigation bar and quick launch, each an
arbitrarily nested tree) and produces a flattened, depth-annotated summary.

It answers: how many top-level nodes exist, how deep does each tree nest, and
what does the full node list look like with depth and child counts.

## Honest outcomes

Every run returns a `DiscoveryOutcome` carrying a `DiscoveryStatus`:
`OBSERVED`, `EMPTY`, `PARTIAL`, `UNAVAILABLE`, `FORBIDDEN`, or `FAILED`.

A missing input file is `UNAVAILABLE` and **no output directory is created**.
An export with no navigation nodes at all is `EMPTY`, never a pass. An input
that isn't a JSON object (e.g. an array or a scalar) is `FAILED`, since it
cannot be the expected `{topNav, quickLaunch}` shape.

## Read-only guarantee

No writes to any tenant, no network access. It reads the export path you name
and writes analysis artifacts to the output directory you name.

## Usage

```bash
python -c "
from navigation_analysis import run
outcome = run(navigation_path='navigation.json', output_dir='out/')
print(outcome.status, outcome.detail)
"
```

## Scripts

- `../../scripts/navigation_analysis.py` -- `run`, `analyse`, `generate_report`
- `../../scripts/discovery_inputs.py` -- `DiscoveryStatus`, `DiscoveryOutcome`, `load_json_input`, `require_output_dir`

## Provenance

Adapted from `sp-discovering-navigation` in the originating SharePoint
migration repository. See
`docs/reports/phase-9-reusable-sharepoint-plugin-extraction/provenance.md`.
