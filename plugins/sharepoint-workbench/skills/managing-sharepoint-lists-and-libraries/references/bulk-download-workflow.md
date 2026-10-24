# Bulk download for offline link analysis

Use `sharepoint-download-file` with the inventory-driven wrapper. No new skill identity is required.

```powershell
# Local preview only; ConfigPath is required.
pwsh -File plugins/sharepoint-site-build-and-publish/scripts/content-publication/download-sharepoint-inventory-files.ps1 -InventoryCsv ./inventory/files.csv -ConfigPath ./config.psd1 -OutputDir ./downloads

# User-run live download after reviewing downloads.csv.
pwsh -File plugins/sharepoint-site-build-and-publish/scripts/content-publication/download-sharepoint-inventory-files.ps1 -InventoryCsv ./inventory/files.csv -ConfigPath ./config.psd1 -OutputDir ./downloads -Execute -ConfirmToken DOWNLOAD-SHAREPOINT-INVENTORY-FILES
```

`-Extensions` is a comma-separated list; default `html,htm,aspx`. Online uses browser-based
authentication; on-prem prompts for a domain account once or takes an explicit PSCredential.
Standard Online hostnames are detected automatically; `-Platform Online|OnPrem` overrides it.
Each row supplies WebUrl; config supplies Online app registration. No default session credentials
are used in the bulk workflow.

`downloads.csv` records FileUrl, WebUrl, LibraryTitle, original FileName/RelativePath, LocalPath,
Status and Message. Hash directories preserve distinct source files with equal basenames.
Local filenames have a safe prefix; original identity remains in the manifest. Existing files
are protected unless `-Overwrite` is explicit. Failures remain in the manifest and cause nonzero exit.
The wrapper reuses the canonical single-file downloader, including per-file connection overhead.
Prefer a selected sample for first live validation; performance has not been live-tested.

On-prem files are retrieved through REST `$value` with `-RawFile`, retaining stored bytes.
Do not mistake ASPX source for rendered content or modern-page canvas data. Modern pages need
`collect-sharepoint-page-content.ps1` from `sharepoint-extract-links`, which exports stored fields.
Planning performs no tenant I/O; executing is the user's responsibility.

Python extraction uses `sharepoint-extract-links` and `export_link_inventory.py` with
`--manifest-csv downloads/downloads.csv --output-dir links`. Extraction does not rewrite files.
