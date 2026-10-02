# Inventory collectors: scripts, usage and provenance

## Contents

- [Which script subsumes which source](#which-script-subsumes-which-source)
- [Usage](#usage)
- [Provenance](#provenance)

## Which script subsumes which source

Three scripts consolidate seven source collectors from the originating migration repository. Nothing
was silently dropped; see each script's own header for the per-source mapping. A fourth script,
`collect-sharepoint-schema-export.ps1`, is this plugin's own orchestrator (not ported from a source
collector) that assembles the directory-tree shape the schema analysis tools expect out of several
`collect-sharepoint-inventory.ps1` invocations.

| Script | Target | Subsumes (source file) |
| --- | --- | --- |
| `collect-sharepoint-inventory.ps1` | Modern SPO, PnP.PowerShell | `export-sharepoint-inventory.ps1` / `-custom.ps1` (list/library enumeration only, `-Mode Lists`); `export-persons-picture-description.ps1` (`-Mode ListFields`, generalized from hardcoded Persons/Comment); `export-images-library-inventory.ps1` (`-Mode LibraryFiles`, generalized from hardcoded Images1); `discover-sandbox-definitions.ps1` (`-Mode ContentTypes`, generalized from hardcoded Sandbox/NTT site URLs and list names) |
| `collect-onprem-sharepoint-inventory.ps1` | On-prem SP2016, NTLM/Kerberos REST | `export-sharepoint-inventory.ps1` and `export-sharepoint-inventory-custom.ps1` (full crawl, the default mode, no hardcoded site URL or output path); `get-source-item-counts.ps1` (`-QuickCountsOnly`, no hardcoded config-only SiteUrl) |
| `collect-onprem-sharepoint-aspx-pages.ps1` | On-prem SP2016, NTLM/Kerberos REST | `extract-all-aspx-pages.ps1` (no hardcoded domain default, no hardcoded `01_source_sharepoint` output path) |
| `collect-sharepoint-schema-export.ps1` | Modern SPO, PnP.PowerShell | Not ported: a new orchestrator. Drives `collect-sharepoint-inventory.ps1` once per mode and per list to assemble `summary/{lists,content_types}.json` and `lists/<name>/{fields,content_types}.json`. It does not produce `summary/site_columns.json`, because `collect-sharepoint-inventory.ps1` has no site-columns-only mode; the orchestrator's header describes the gap. |

## Usage

Modern SPO: lists/libraries, list fields, library files, content types.

```bash
pwsh -File scripts/collect-sharepoint-inventory.ps1 -SiteUrl "https://tenant.sharepoint.com/sites/Test" -Mode Lists -OutputPath lists.json
pwsh -File scripts/collect-sharepoint-inventory.ps1 -SiteUrl "https://tenant.sharepoint.com/sites/Test" -Mode ListFields -ListName "Persons" -FieldNames "Comment" -OutputPath persons-comment.json
pwsh -File scripts/collect-sharepoint-inventory.ps1 -SiteUrl "https://tenant.sharepoint.com/sites/Test" -Mode LibraryFiles -ListName "Images1" -OutputPath images1-files.json
pwsh -File scripts/collect-sharepoint-inventory.ps1 -SiteUrl "https://tenant.sharepoint.com/sites/Test" -Mode ContentTypes -ContentTypeNameFilter "Modern_*" -ListNames "MyList" -OutputPath schema.json
```

On-prem SP2016: full crawl or quick counts.

```bash
pwsh -File scripts/collect-onprem-sharepoint-inventory.ps1 -SiteUrl "https://sp2016.example.org/sites/Legacy" -OutputDir .\inventory -UseDefaultCredentials
pwsh -File scripts/collect-onprem-sharepoint-inventory.ps1 -SiteUrl "https://sp2016.example.org/sites/Legacy" -OutputDir .\quick-counts.csv -QuickCountsOnly -UseDefaultCredentials
```

On-prem SP2016: bulk `.aspx` page download.

```bash
pwsh -File scripts/collect-onprem-sharepoint-aspx-pages.ps1 -SiteUrl "https://sp2016.example.org/sites/Legacy" -UseDefaultCredentials
```

Modern SPO: full schema-export directory tree for the schema skills.

```bash
pwsh -File scripts/collect-sharepoint-schema-export.ps1 -SiteUrl "https://tenant.sharepoint.com/sites/Test" -OutputDir .\schema-export
```

## Provenance

Ported and generalized from `plugins/sharepoint-migration/scripts/{inventory,diagnostics,utilities,content-migration,page-migration}/`
in the originating SharePoint migration repository. All hardcoded site URLs, project codenames and
output-path defaults were removed in favor of explicit parameters.
