# Link integrity validation details

## Contents

- [Resolver injection](#resolver-injection)
- [Statuses and outcomes](#statuses-and-outcomes)
- [Usage](#usage)
- [Relationship to sharepoint-site-build-and-publish](#relationship-to-sharepoint-site-build-and-publish)
- [Provenance](#provenance)

## Resolver injection

`validate_link_integrity(inventory, resolver)` takes a `LinkInventory` from `sharepoint-extract-links` and a resolver, and returns an `IntegrityReport` of
`LinkFinding` records. The module ships no HTTP or tenant transport; you inject the resolver, which makes the trust boundary explicit:

- `make_local_path_resolver(root)` is built in; it validates server-relative links against an exported local tree, with no network access.
- A custom resolver is any callable you supply for live checking.

Without a resolver, links are reported `UNRESOLVABLE`, never assumed good. That is the deliberate distinction between "verified present" and "not checked".

## Statuses and outcomes

| Status | Meaning |
|---|---|
| `RESOLVED` | Target confirmed to exist |
| `BROKEN` | Target confirmed absent |
| `UNRESOLVABLE` | Could not be determined; NOT counted as passing |
| `SKIPPED` | Out of scope for the resolver (for example `mailto:` and anchors) |

The report-level `outcome` is `OBSERVED`, `EMPTY`, `PARTIAL` or `FAILED`. An empty inventory reports `EMPTY`, never a pass: validating nothing is not
validating successfully (Phase 9 spec section 13).

## Usage

```python
from link_extraction import extract_links_from_paths
from link_integrity import validate_link_integrity, make_local_path_resolver
report = validate_link_integrity(extract_links_from_paths(["export/page.aspx"]), make_local_path_resolver("export/"))
print(report.outcome, [f.status for f in report.findings])
```

## Relationship to sharepoint-site-build-and-publish

That plugin's `sharepoint-compare-publication-state` and `sharepoint-validate-publication` skills reconcile a publication map against a target library,
a different question from whether individual hyperlinks inside content resolve. They are complementary, not duplicates.

## Provenance

Adapted from `sp-validating-link-integrity` in the originating SharePoint migration repository (source repository only:
`docs/reports/phase-9-reusable-sharepoint-plugin-extraction/provenance.md`).
