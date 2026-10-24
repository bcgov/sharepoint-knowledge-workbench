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
| `collect-sharepoint-content-inventory.ps1` | Online or on-prem SP2016, auto-selected by hostname or explicit `-Platform` | New recursive, metadata-only CSV inventory of files across all libraries and descendant subsites, including hidden/system libraries and direct web-root files |
| `collect-sharepoint-inventory.ps1` | Modern SPO, PnP.PowerShell | List/library enumeration (`-Mode Lists`), one list's field values (`-Mode ListFields -ListName -FieldNames`), a library's files (`-Mode LibraryFiles -ListName`) and content-type definitions (`-Mode ContentTypes`); every list, library, field and filter is a parameter, nothing is hardcoded |
| `collect-onprem-sharepoint-inventory.ps1` | On-prem SP2016, NTLM/Kerberos REST | Full crawl (the default mode) or `-QuickCountsOnly`; no hardcoded site URL or output path |
| `collect-onprem-sharepoint-aspx-pages.ps1` | On-prem SP2016, NTLM/Kerberos REST | `extract-all-aspx-pages.ps1` (no hardcoded domain default, no hardcoded `01_source_sharepoint` output path) |
| `collect-sharepoint-schema-export.ps1` | Modern SPO, PnP.PowerShell | Not ported: a new orchestrator. Drives `collect-sharepoint-inventory.ps1` once per mode and per list to assemble `summary/{lists,content_types}.json` and `lists/<name>/{fields,content_types}.json`. It does not produce `summary/site_columns.json`, because `collect-sharepoint-inventory.ps1` has no site-columns-only mode; the orchestrator's header describes the gap. |

## Usage

### All documents, images, pages and other files across subsites

Use `collect-sharepoint-content-inventory.ps1` for a file-level inventory rather than schema
discovery. One script supports both authentication adapters. The user runs it in their terminal.
Validate connection for the selected profile/target first using the workbench connection skill.

From the repository root:

```powershell
# Online: URL and app registration from a specific config profile.
pwsh -File plugins/sharepoint-site-assessment/scripts/collect-sharepoint-content-inventory.ps1 -ConfigPath ./config-spo-prod.psd1 -OutputDir ./temp/content-inventory-spo

# Online: override the profile's target with a different site/subsite.
pwsh -File plugins/sharepoint-site-assessment/scripts/collect-sharepoint-content-inventory.ps1 -ConfigPath ./config-spo-prod.psd1 -SiteUrl https://tenant.sharepoint.com/sites/Example -OutputDir ./temp/content-inventory-spo

# On-prem: explicit target, with an interactive credential prompt.
pwsh -File plugins/sharepoint-site-assessment/scripts/collect-sharepoint-content-inventory.ps1 -SiteUrl https://sharepoint.example.org/sites/Legacy -OutputDir ./temp/content-inventory-onprem

# A config can also supply an on-prem target; SiteUrl always overrides it.
pwsh -File plugins/sharepoint-site-assessment/scripts/collect-sharepoint-content-inventory.ps1 -ConfigPath ./config-spo-prod.psd1 -SiteUrl https://sharepoint.example.org/sites/Legacy -Platform OnPrem -OutputDir ./temp/content-inventory-onprem
```

`-Platform Auto` is the default. A hostname ending in `.sharepoint.com` (including
`tenant.sharepoint.com`), `.sharepoint.us`, `.sharepoint.de` or `.sharepoint.cn` selects Online.
Other hosts select OnPrem. This is a hostname heuristic, not platform verification; override it
with `-Platform Online|OnPrem` for custom hosts. Online uses interactive PnP authentication per
web; on-prem prompts once for Windows credentials (or accepts `-Credential`), never default
session credentials or the Online app registration. A server 401 is reported with authentication
guidance; the script does not blindly retry or claim an empty site.
Configuration uses the shared Workbench helper; parameters override configuration values.

Output files are overwritten on rerun:

| File | Purpose |
| --- | --- |
| `files.csv` | One row per file; no content download |
| `libraries.csv` | One row per discovered library, including empty libraries and collection status |
| `errors.csv` | Web URL, stage, library and error message; headers remain when no errors occurred |
| `manifest.json` | Scope, exclusions, counts and `COMPLETE`, `EMPTY`, `PARTIAL` or `FAILED` status |

File CSV columns:

| Columns | Meaning |
| --- | --- |
| `SourceSiteName`, `SourceSiteUrl` | Title and URL of the starting web |
| `WebTitle`, `WebUrl` | Title and URL of the web/subsite containing the file |
| `ContainerType` | DocumentLibrary, PictureLibrary, WikiPageLibrary, PublishingPageLibrary, AssetLibrary or SiteRoot; determined by library template, not file extension |
| `LibraryTitle`, `LibraryId`, `LibraryBaseTemplate` | Library name, GUID and template ID; blank for site-root files |
| `RelativePath` | Path including filename relative to the starting web, retaining subsite and library segments |
| `LibraryRelativePath` | Path including filename relative to the containing library; blank for site-root files |
| `FolderPath` | Parent folder relative to the starting web |
| `ServerRelativeUrl`, `FileUrl` | Server-relative file path and full URL |
| `FileName`, `FileExtension` | Name and lower-case extension without the dot; blank extension for extensionless files |
| `UniqueId`, `ItemId`, `ContentTypeId` | File identity and library-item metadata where available |
| `SizeBytes`, `Created`, `Modified` | Size and dates where available; unavailable metadata stays blank |

The crawl covers the starting web and descendant subsites, all document-based libraries
(including picture/page/asset and hidden/system libraries), nested library folders, and files
directly in each web root. It excludes ordinary list records and their attachments (including
Links lists), folder rows, historical versions, recycle bins, generated list forms/views,
external URLs/images embedded in content, and files below web-root folders outside libraries.
It does not enumerate other site collections or hub-associated sites. Security-trimmed objects
may be invisible; use an account with access to the full intended scope. A library count is the
observed file count, not its ItemCount, which may include folders.

REST collections follow every `d.__next` page and parse with `ConvertFrom-Json -AsHashtable`
to preserve SP2016 `Id`/`ID` keys. Online uses paged `RecursiveAll` CAML. A failed later page
preserves earlier library rows, records an error and results in `PARTIAL` plus nonzero exit.
Large-library threshold errors are reported rather than treated as an empty library.

API references: [PnP list-item paging and CAML](https://pnp.github.io/powershell/cmdlets/Get-PnPListItem.html),
[PnP subweb discovery](https://pnp.github.io/powershell/cmdlets/Get-PnPSubWeb.html),
[Microsoft file/folder REST](https://learn.microsoft.com/en-us/sharepoint/dev/sp-add-ins/working-with-folders-and-files-with-rest).

Modern SPO: lists/libraries, list fields, library files, content types.

```bash
pwsh -File scripts/collect-sharepoint-inventory.ps1 -SiteUrl "https://contoso.sharepoint.com/sites/Demo" -Mode Lists -OutputPath lists.json
pwsh -File scripts/collect-sharepoint-inventory.ps1 -SiteUrl "https://contoso.sharepoint.com/sites/Demo" -Mode ListFields -ListName "MyList" -FieldNames "Notes" -OutputPath list-fields.json
pwsh -File scripts/collect-sharepoint-inventory.ps1 -SiteUrl "https://contoso.sharepoint.com/sites/Demo" -Mode LibraryFiles -ListName "MyLibrary" -OutputPath library-files.json
pwsh -File scripts/collect-sharepoint-inventory.ps1 -SiteUrl "https://contoso.sharepoint.com/sites/Demo" -Mode ContentTypes -ContentTypeNameFilter "Contoso_*" -ListNames "MyList" -OutputPath schema.json
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
pwsh -File scripts/collect-sharepoint-schema-export.ps1 -SiteUrl "https://contoso.sharepoint.com/sites/Demo" -OutputDir .\schema-export
```

## Provenance

Ported and generalized from `plugins/sharepoint-migration/scripts/{inventory,diagnostics,utilities,content-migration,page-migration}/`
in the originating SharePoint migration repository. All hardcoded site URLs, project codenames and
output-path defaults were removed in favor of explicit parameters.
