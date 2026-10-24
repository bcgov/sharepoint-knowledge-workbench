# Bulk page/document link inventory and migration

Keep file and link inventories, with original URLs as identities. Equal page names across
subsites must not be merged. These scripts have local fixture/mock coverage; first live runs
remain pending. No site-wide crawl is required merely to install the capabilities.

1. **Inventory files**: `sharepoint-collect-site-inventory` produces recursive `files.csv` across
   the starting web and descendants. This inventories file names/metadata only.
2. **Download selected static content**: `sharepoint-download-file` uses
   `download-sharepoint-inventory-files.ps1`. Default formats: HTML/HTM/ASPX; select Office files
   explicitly. `downloads.csv` maps FileUrl to LocalPath, and preserves failures.
3. **Export stored Online page fields**: `collect-sharepoint-page-content.ps1` consumes files.csv
   and exports available CanvasContent1, LayoutWebpartsContent, WikiField and PublishingPageContent
   as `.page.json`, plus page-content.csv. It is user-run, read-only PnP with interactive auth.
   Use this for modern pages; raw ASPX downloads do not capture all stored page content.
4. **Extract original links before conversion**: run the Python exporter below, preserving
   original and post-conversion inventories. Extraction leaves sources unchanged.
5. **Analyze/convert**: `sharepoint-analyze-classic-pages` and `sharepoint-analyze-page-inventory`
   analyze structure. `sharepoint-convert-legacy-aspx-to-html` converts one eligible static local
   page; dynamic/active source may be rejected. `sharepoint-convert-page-to-modern` is a separate
   live Online conversion route, not a generic local-file uploader.
6. **Plan rewrites against actual destinations**: `sharepoint-update-page-links` covers page
   content; `sharepoint-update-links-in-documents` covers Office files; rich-text image remediation
   is only for field images. A link CSV does not provide a source-to-target mapping.
7. **Publish and recheck**: use the appropriate publishing/conversion skill with its existing
   gates. Recollect page fields and re-extract links after publication. Page-modernization
   validation checks arrival/metadata; link-integrity validation separately checks destinations
   using an explicit resolver. An unresolved network target must never be assumed valid.

Repository-root commands (installed skills expose the scripts through their spokes):

```powershell
# Offline local-tree analysis.
python plugins/sharepoint-site-migration/scripts/link-remediation/export_link_inventory.py --source-dir ./downloads --base-url https://sharepoint.example.org/ --output-dir ./links-before

# Prefer the source URL mapping in a download manifest.
python plugins/sharepoint-site-migration/scripts/link-remediation/export_link_inventory.py --manifest-csv ./downloads/downloads.csv --output-dir ./links-before

# User-run Online page-field collection, then offline Python extraction.
pwsh -File plugins/sharepoint-site-migration/scripts/link-remediation/collect-sharepoint-page-content.ps1 -InventoryCsv ./inventory/files.csv -ConfigPath ./config.psd1 -OutputDir ./page-fields
python plugins/sharepoint-site-migration/scripts/link-remediation/export_link_inventory.py --manifest-csv ./page-fields/page-content.csv --output-dir ./links-modern
```

| Output | Contents |
| --- | --- |
| links.csv | SourceUrl, WebUrl, LibraryTitle, LocalPath, SourcePart, RawUrl, ResolvedUrl, LinkKind, OccurrenceCount |
| sources.csv | Each attempted source, format, OBSERVED/EMPTY/FAILED/NOT_SUPPORTED, count and error |
| manifest.json | Aggregate outcome, counts, parsing scope and exclusions |

Relative links resolve against the original remote page URL. Without a source mapping/base URL,
relative links stay unresolved. ResolvedUrl is normalization, not proof a destination exists.
HTML entities are decoded; repeated links within one source part are counted. Static files are
parsed as stored UTF-8 markup, never executed. Explicit href/src/action/url attributes are read,
including non-navigation and platform links.

Office coverage is external `.rels` relationship targets in DOCX/XLSX/PPTX, not every URL in text,
fields, macros or embedded binaries. PDFs and legacy DOC/XLS/PPT need additional parsers;
PDF inputs report NOT_SUPPORTED. CSS url(), srcset and script-generated URLs are excluded.
Modern field coverage includes HTML attributes and URL-bearing JSON properties, not a rendered
DOM or every custom web-part schema. Keep unsupported and failed sources visible.

Existing rewrite/conversion/publication gates remain mandatory. Performance and authentication
require first live validation by the user; local tests do not establish full tenant coverage.
