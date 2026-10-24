# List-Scoped Registration

A ListView Command Set becomes available in three separate stages:

1. Upload and deploy the `.sppkg` to the intended App Catalog.
2. Add the app to the target site unless tenant-wide deployment was intentionally used.
3. Create a list `UserCustomAction` with location
   `ClientSideExtension.ListViewCommandSet.CommandBar`.

The command is not associated with a content type. Use the extension manifest `id` as
`-ComponentId`. Use a stable `-Name` for idempotent updates and `-Remove` rollback.

The script accepts either `-SiteUrl`, `-ClientId`, and `-TenantId`, or a PowerShell
data file containing those keys. Run live commands yourself in PowerShell 7 with
PnP.PowerShell installed.

Propagation can take several minutes. After registration, revisit the list, hard-refresh,
and verify the custom action before changing the package or registering duplicates.
