# SharePoint Actual-Library-State CSV Format

`sharepoint_reconcile.load_actual_state_from_csv()` reads a CSV export of
a target document library's default view, with these column headers (exact names,
case-sensitive):

| Column | Type | Notes |
|---|---|---|
| `TopicId` | text | must match the `TopicId` column values as uploaded |
| `Title` | text | |
| `PackageIdentity` | text | |
| `PublicationOrder` | integer | |
| `TopicContentSHA256` | text | |
| `SourceDocumentSHA256` | text | |

## How to produce this file

1. Open the target knowledge library in SharePoint.
2. Ensure the view includes all six columns above (add them to the view
   if not already present — Library Settings > Views).
3. Use "Export to Excel" (or "Export to CSV" if available in the tenant's
   ribbon), save as `.csv`, and ensure the header row matches the table
   above exactly (SharePoint's export sometimes uses internal column
   names — rename the header row if needed before running reconciliation).
4. Pass the resulting file to `sharepoint_cli.py reconcile --actual-state <file>.csv`.
