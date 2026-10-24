# Single-page web-part content extraction

How `sp-dynamic-aspx-page-migration` gets one page's web-part content. The installed skill
`sharepoint-analyze-webpart-behavior` and its `webpart-analysis-runbook.md` describe the
site-wide process (collect pages, scan, extract, group, report, review). This reference adapts
that process to one page. Read the runbook first; do not rediscover it.

## Why not run Scan

`collect-sharepoint-webpart-content.ps1 -Mode Scan` enumerates the whole `Pages` library and has
no single-page option. On a REST failure it prints `Total pages to scan: 0` and reports success
(errors show only with `-Verbose`). For one page, skip Scan and build the one-row scan CSV.

Exception: when the cached scan is stale for the page (next section), Scan is the only way to
discover the `WebPartId` of web parts added since. Run it site-wide, check that it did not print
`Total pages to scan: 0`, and keep only this page's rows.

## The cached scan is a snapshot, not the live page

`legacy_webparts_scan_results.csv` and every extract under `analysis\` are point-in-time. A page
edited afterwards can have web parts the scan never saw, and `batch-extract-webpart-content.ps1`
builds `webpart-scan.csv` from that cache without querying the live page, so it silently omits
them. A one-row scan CSV for a page that has three web parts produces a package that is missing
two thirds of the page and still passes every package-level check.

Completeness gate, run for every page BEFORE conversion (the orchestrator, not a sub-agent):

1. Compare the page's inventory `Modified` date with the scan CSV's file date. Later means stale.
2. Compare the inventory `Webpart` field and the user's live web part list (`...?contents=1`, or
   `/_layouts/15/spcontnt.aspx?&url=<ServerRelativeUrl>`) with the rows in `webpart-scan.csv`:
   same count, same titles. Any web part missing from the scan is extracted before conversion.
3. Ask the user for a full-page screenshot of the live page and confirm that every visible
   section, panel, image and profile exists in the extracted HTML. Text visible on screen but
   absent from every extract means the extract is incomplete.
4. Any mismatch blocks the page. It is not a caveat on the hand-off.

## Prior analysis to read first

Folder: `portal-workspace-prod\01_source_sharepoint\analysis\` (the site-wide runbook output).

| File | Use for this page |
|---|---|
| `legacy_webparts_scan_results.csv` | Page URL, web part title and `WebPartId` (source of the scan CSV row) |
| `webpart-instance-solution-mapping.csv` | Prior classification and proposed solution (a starting point, not the answer) |
| `webpart-instance-review.csv` | Prior group and migration effort |
| `links\ALL-UNIQUE-LINKS-FOR-REVIEW.md` | The page's link and asset rows |
| `webpart_content_extract.csv` | Prior extract, to compare against the fresh one |

## Steps

1. Find the page's rows in the files above and show the user what the prior review decided.
2. Write `<dir>\webpart-scan.csv`, one row per web part. Columns: `PageUrl` (server-relative,
   such as `/Pages/<leaf>.aspx`), `WebPartId`, `WebPartTitle`, `TypeName`, `Category`, `ListName`,
   `ViewGuid`, `Zone`, `ZoneIndex`. If the page is absent from the prior analysis, run Scan and
   keep only that page's rows.
3. Extract fresh, from `.agents\skills\sharepoint-analyze-webpart-behavior`:

   ```powershell
   pwsh -File scripts\collect-sharepoint-webpart-content.ps1 -SiteUrl "<source-site-url>" -OutputDir "<dir>" -Mode ExtractContent
   ```

   Output: `<dir>\webpart-content.json` and `<dir>\raw-export\` (raw `exportwp.aspx` XML).
4. Compare the fresh extract with the prior one (length and content). If the live page changed,
   tell the user what changed and ask which version to migrate. Never call the prior extract
   stale without evidence.

## Authentication

Force explicit credentials: omit `-UseDefaultCredentials` so the script prompts for the
`corp_id\` account. The runbook examples show `-UseDefaultCredentials`; do not copy that. Add it
only if the user asks.

## Worked example (BC-Operations-Service-Division, 2026-10)

Cached scan (2026-09-10) listed one Content Editor. The live page, edited 2026-10-08, has three
web parts (Content Editor, Two Column Accordion, Content Editor). A sub-agent converted the
one-part extract and reported success; the missing "BCSS Operations" / "BCSS Central Programs"
accordion and the Operations header band were found only when the user compared the live page. The
page record's `Webpart` field ("Accordion, Content Editor") and a `?contents=1` listing would
have shown it up front.

## Worked example (Headquarters-Division)

Page `/Pages/Headquarters-Division.aspx`, one Content Editor web part
`d61d7525-37c0-42c3-be90-2a8646edbb58`. The prior analysis classified it `TextOnly` (Staff Bio
Directory Table, `APPROVED_NATIVE`, SPO Text web part) with an 11,337-character extract. The fresh
extract on 2026-10-15 was 2,938 characters, so the live page had changed.
