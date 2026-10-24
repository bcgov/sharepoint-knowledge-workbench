# Permissions: export shapes, collection and scripts

## Contents

- [Two accepted export shapes](#two-accepted-export-shapes)
- [Collecting a fresh export](#collecting-a-fresh-export)
- [Read-only scope](#read-only-scope)
- [Scripts](#scripts)
- [Provenance](#provenance)

## Two accepted export shapes

1. A flat JSON array of permission entries, one row per (principal, object) pair: `webUrl`,
   `principalTitle`, `permissionLevels`, and either `objectTitle` or `listName`.
2. A structured JSON object: `siteUrl`, `groups: [{name, permission}]`,
   `objects: [{title, hasUniqueRoleAssignments, roleAssignments}]`.

Both go through the same `analyse()` entry point. The flat shape has no explicit inheritance flag,
so every derived object is treated as evaluated; it does not claim to know inheritance state it
cannot see.

## Collecting a fresh export

`collect-sharepoint-permissions.ps1` connects via Windows-credential/NTLM REST (works against
legacy on-prem SharePoint 2016 and SharePoint Online, since both expose the same REST surface)
and writes a flat JSON array in shape 1. It queries the site's own role assignments plus every
non-hidden list/library where `HasUniqueRoleAssignments` is true (inherited-permission lists have
nothing of their own to report).

```bash
pwsh -File scripts/collect-sharepoint-permissions.ps1 -SiteUrl "https://tenant.example.com/sites/Team" -OutputPath permissions.json -UseDefaultCredentials
```

## Read-only scope

`permissions_analysis.py` makes no tenant writes and no network access. The collector only calls
REST GET (`_api/web/roleassignments`): zero tenant writes.

## Scripts

- `scripts/collect-sharepoint-permissions.ps1`: real, read-only NTLM/REST collector.
- `scripts/permissions_analysis.py`: `run`, `analyse`, `generate_report`.
- `scripts/discovery_inputs.py`: `DiscoveryStatus`, `DiscoveryOutcome`, `load_json_input`,
  `require_output_dir`.
- `scripts/generate-deep-permissions-analysis.py`: parses permissions extractions and writes
  `SPO-GROUP-PROVISIONING-CHECKLIST.md`, `unique-permissions-exception-report.md` and
  `security-analysis-summary.md`.

## Provenance

Adapted from `sp-discovering-permissions` in the originating SharePoint migration repository.
Source repository only: `docs/reports/phase-9-reusable-sharepoint-plugin-extraction/provenance.md`.
