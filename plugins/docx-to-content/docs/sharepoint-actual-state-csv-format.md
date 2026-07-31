# SharePoint Actual-Library-State CSV Format

`sharepoint_reconcile.load_actual_state_from_csv()` reads a CSV export of
the `CEIS-Pilot-Knowledge` document library's default view, with these
column headers (exact names, case-sensitive):

| Column | Type | Notes |
|---|---|---|
| `TopicId` | text | must match the `TopicId` column values as uploaded |
| `Title` | text | |
| `PackageIdentity` | text | |
| `PublicationOrder` | integer | |
| `TopicContentSHA256` | text | |
| `SourceDocumentSHA256` | text | |

## How to produce this file (manual, per pilot run)

1. Open the `CEIS-Pilot-Knowledge` library in SharePoint.
2. Ensure the view includes all six columns above (add them to the view
   if not already present — Library Settings > Views).
3. Use "Export to Excel" (or "Export to CSV" if available in the tenant's
   ribbon), save as `.csv`, and ensure the header row matches the table
   above exactly (SharePoint's export sometimes uses internal column
   names — rename the header row if needed before running reconciliation).
4. Pass the resulting file to `sharepoint_cli.py reconcile --actual-state <file>.csv`.

This is the only actual-library-state evidence mechanism confirmed
available during Phase 3.0 tenant-capability discovery (see
`docs/superpowers/specs/phase-3-tenant-capability-report.md`). A future,
more automated reader (Microsoft Graph or PnP PowerShell) is an accepted
open item (`docs/superpowers/specs/phase-3-unresolved-decisions.md`,
item 10) but is not required for this pilot to proceed.
