---
name: analyze-permissions
plugin: sharepoint-discovery
description: Analyses an exported classic SharePoint permissions/security snapshot -- deriving groups, evaluated objects, and the subset with broken permission inheritance -- to produce a group provisioning worksheet and a broken-inheritance exception report. Read-only; consumes an export you provide and never contacts a tenant.
allowed-tools: Bash, Read
examples:
  - "python -c \"from permissions_analysis import run; print(run(permissions_path='permissions.json', output_dir='out/').status)\""
---

# Analyze Permissions

## Trigger and Purpose

Use this skill when planning a classic-to-modern SharePoint migration and you
need to know which groups exist and which lists/libraries have broken
permission inheritance that must be explicitly re-provisioned rather than
inherited. It consumes a permissions export already pulled from a tenant.

## Two accepted export shapes

1. A flat JSON array of permission entries, one row per (principal, object)
   pair -- `webUrl`, `principalTitle`, `permissionLevels`, and either
   `objectTitle` or `listName`.
2. A structured JSON object -- `siteUrl`, `groups: [{name, permission}]`,
   `objects: [{title, hasUniqueRoleAssignments, roleAssignments}]`.

Both are accepted by the same `analyse()` entry point; the flat shape has no
explicit inheritance flag, so every derived object is treated as evaluated
(it does not claim to know inheritance state it cannot see).

## Honest outcomes

Every run returns a `DiscoveryOutcome` carrying a `DiscoveryStatus`:
`OBSERVED`, `EMPTY`, `PARTIAL`, `UNAVAILABLE`, `FORBIDDEN`, or `FAILED`.

A missing permissions export is `UNAVAILABLE` and **no output directory is
created** -- this module never fabricates a placeholder group/object list to
appear successful (the source implementation this was extracted from did;
that fallback is removed). An export with no groups or objects is `EMPTY`,
never a pass. An input that is neither a JSON array nor object is `FAILED`.

## Read-only guarantee

No writes to any tenant, no network access. It reads the export path you name
and writes analysis artifacts to the output directory you name.

## Usage

```bash
python -c "
from permissions_analysis import run
outcome = run(permissions_path='permissions.json', output_dir='out/')
print(outcome.status, outcome.detail)
"
```

## Scripts

- `scripts/permissions_analysis.py` -- `run`, `analyse`, `generate_report`
- `scripts/discovery_inputs.py` -- `DiscoveryStatus`, `DiscoveryOutcome`, `load_json_input`, `require_output_dir`

## Provenance

Adapted from `sp-discovering-permissions` in the originating SharePoint
migration repository. See
`docs/reports/phase-9-reusable-sharepoint-plugin-extraction/provenance.md`.
