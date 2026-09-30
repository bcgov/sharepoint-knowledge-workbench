# Problematic Web Parts Summary — ASPX Pages with Custom Code

**Source Data**: legacy_webparts_scan_results.csv (119 web parts scanned)  
**Analysis Date**: 2026-07-15  
**Scope**: SP2016 CMAT site — pages containing Script Editor and Content Editor web parts

---

## Executive Summary

**Total problematic web parts found**: 118 out of 119
- **Script Editor Web Parts (CRITICAL — contains custom code)**: 3
- **Content Editor Web Parts (REQUIRES ANALYSIS)**: 115

**Pages requiring code analysis**: 49 unique ASPX pages
- **Pages with Script Editors**: 3 (Edit forms on case lists)
- **Pages with Content Editors**: 46 (Mix of list forms and publishing pages)

---

## Tooling — How This Data Was Produced (and What's Still Missing)

All scripts live in `plugins/sharepoint-migration/scripts/page-migration/` (relative to repo root).

| Script | What it does | What it captures | Gap |
|---|---|---|---|
| [`scan-webparts.ps1`](../../plugins/sharepoint-migration/scripts/page-migration/scan-webparts.ps1) | Recursively walks every list/library/folder on the live site, calls the `GetLimitedWebPartManager` REST API per page, flags any web part titled "Content Editor" or "Script Editor" | `PageUrl`, `WebPartTitle`, `WebPartId` → produces `legacy_webparts_scan_results.csv` (the 119-row source data for this document) | **Does not capture the actual Content property** — no HTML/JS payload, just the fact that a CEWP/SEWP exists. Also: WebPartIds go stale if the page is re-saved or the web part removed/re-added — re-run before every extraction pass, not just once. |
| [`analyze-aspx-webparts.ps1`](../../plugins/sharepoint-migration/scripts/page-migration/analyze-aspx-webparts.ps1) | Parses locally-downloaded `.aspx` files, extracts web part XML including CEWP `<Content>` text | CEWP content, but **truncated to 300 chars**; only works when the web part is inline in the raw file | **No SEWP content extraction at all**; misses any web part added via browser UI (content-database-only, not in the raw file) |
| [`download-custom-forms.ps1`](../../plugins/sharepoint-migration/scripts/page-migration/download-custom-forms.ps1) | Downloads non-standard/custom-named list forms (from a separate `lists_with_custom_forms.csv` inventory) | Raw `.aspx` file bytes for oddly-named forms (e.g. `NewForm_Original.aspx`) | Different dataset — not the 119 CEWP/SEWP pages; doesn't touch Script Editor content |
| [`diagnose-page.ps1`](../../plugins/sharepoint-migration/scripts/page-migration/diagnose-page.ps1) | Connectivity/URL-resolution diagnostic — confirms a page exists and lists library contents | Nothing content-related; pure troubleshooting aid | N/A — not intended for content extraction |
| [`extract-webpart-content.ps1`](../../plugins/sharepoint-migration/scripts/page-migration/extract-webpart-content.ps1) *(NEW — 2026-07-15)* | Reads `legacy_webparts_scan_results.csv`, then for each page/WebPartId calls the legacy `_vti_bin/exportwp.aspx` handler (plain HTTP GET) against SP2016 on-prem (read-only) to pull the full **.webpart XML export**, and extracts the `<Content>` element (CEWP/SEWP payload) | Full HTML/JS payload for all 118 web parts found on the current scan | Closes the gap left by `scan-webparts.ps1` and `analyze-aspx-webparts.ps1` — this is the script that answers "what does the Script Editor code actually do" |
| [`analyze-webpart-code.py`](../../plugins/sharepoint-migration/scripts/page-migration/analyze-webpart-code.py) *(NEW — 2026-07-15)* | Reads `webpart_content_extract.json`, resolves external `<script src>` references against locally-downloaded JS files (`14_prototyping/aspx_conversions/site-assets/JS/`), groups instances that do the same thing, and classifies each group | `webpart-code-groups.json` (structured) + `webpart-code-analysis.md` (human-readable) — unique functional groups, what each does, which pages/web parts share it, and an SPO OOB vs. SPFx recommendation per group | None currently known — see Section 6 below for interpretation notes |

### Important correction (2026-07-15): `ExportWebPart` REST method does not exist on SP2016

An earlier version of `extract-webpart-content.ps1` attempted `/_api/.../GetLimitedWebPartManager(scope=1)/ExportWebPart(webPartId=guid'...')` — this 404s **universally**, regardless of URL/verb/GUID formatting, because the REST wrapper for `LimitedWebPartManager` never publishes that method on SharePoint 2016. The only working mechanism is the legacy classic-ASP.NET handler `_vti_bin/exportwp.aspx?pageurl=<absolute-page-url>&guidstring=<webpartid>`, called via plain `GET` (no form digest required). The script now uses this correctly. If a future attempt to extract web part content 404s against `/_api/...`, this is why — don't re-attempt the REST route.

### Running the pipeline (in order)

Both scripts are config-driven: `StructureSourceUrl` comes from `config.psd1`, and `-UseIntegratedAuth` tries Kerberos/NTLM first, then Windows Credential Manager (`SPCredTarget`), then an interactive prompt. Read-only against SP2016 on-prem; never writes (per project HARD RULE).

```powershell
cd plugins\sharepoint-migration\scripts\page-migration

# 1. Refresh the web part inventory (WebPartIds go stale — always re-run this first)
.\scan-webparts.ps1 -UseIntegratedAuth

# 2. Extract full content for every web part in the refreshed inventory
.\extract-webpart-content.ps1 -UseIntegratedAuth

# 3. Group and classify the extracted content (Python, no SharePoint connection needed)
python -B analyze-webpart-code.py `
    --extract    ..\..\..\..\01_source_sharepoint\analysis\webpart_content_extract.json `
    --js-dir     ..\..\..\..\14_prototyping\aspx_conversions\site-assets\JS `
    --output-dir ..\..\..\..\01_source_sharepoint\analysis\
```

**Outputs** (written to `01_source_sharepoint/analysis/`):
- `webpart_content_extract.csv` — one row per web part, 200-char preview, for quick scanning
- `webpart_content_extract.json` — full untruncated content for all web parts, single file
- `webpart_content/*.txt` — one file per web part (`{page}_{WebPartId}.txt`), full untruncated content, for direct diffing/review
- `webpart_raw_export/*.xml` — raw, unparsed `exportwp.aspx` response per web part (saved regardless of parse success — use this to debug if content ever comes back empty unexpectedly)
- `webpart-code-groups.json` — structured groups: signature, member pages/WebPartIds, classification, SPO recommendation
- `webpart-code-analysis.md` — human-readable report, see Section 6 below for the current findings

**"Web Part is not on this page" errors**: this means the WebPartId is stale (the web part was removed/re-added or the page re-saved since the last scan). Re-run `scan-webparts.ps1` to refresh IDs, then re-run extraction. This affected all 3 Script Editors on first extraction attempt (2026-07-15) — see Section 6.

---

## 1. Pages with Script Editor Web Parts ⚠️ CRITICAL

These pages contain **custom JavaScript code** embedded in Script Editor web parts. These are the highest-priority items for modernization.

### Script Editor Inventory (3 total)

| Page URL | List | Form Type | Web Part ID | Notes |
|----------|------|-----------|-------------|-------|
| `/cmat/Lists/PIO_Cases/EditForm.aspx` | PIO_Cases | Edit Form | `b7573f07-4bdd-449a-ba1b-4615f5f329d1` | Custom JS on case edit form |
| `/cmat/Lists/ITAU_Cases/EditForm.aspx` | ITAU_Cases | Edit Form | `b9a499e8-db7f-4c48-a5a8-8aa4f059c438` | Custom JS on case edit form |
| `/cmat/Lists/ICM_Cases/EditForm.aspx` | ICM_Cases | Edit Form | `6b043258-3cc3-42be-a618-3df278d84c5c` | Custom JS on case edit form |

### Analysis Required for Script Editors

**Questions to answer for each**:
1. What does the custom JavaScript do? (validation, auto-fill, filtering, styling?)
2. Is the functionality essential or nice-to-have?
3. Can it be rebuilt in Power Apps forms or modern list item forms?
4. Any external dependencies (APIs, jQuery plugins)?

**Modernization Path**: Power Apps forms with Power Fx formulas or canvas app logic

---

## 2. Pages with Content Editor Web Parts

Content Editors are **lower risk** than Script Editors — most contain trivial rich text (instructions, banners). However, some may contain embedded CSS/styling that needs analysis.

### Content Editor Inventory by Category

#### A. List Form Pages (24 Content Editors on 10 unique pages)

| Page | List | Count | Priority |
|------|------|-------|----------|
| `/cmat/Lists/PIO_Cases/DispForm.aspx` | PIO_Cases | 1 | LOW |
| `/cmat/Lists/ICM_Case_Tasks/NewForm.aspx` | ICM_Case_Tasks | 1 | LOW |
| `/cmat/Lists/ICM_Approval_Requests/NewForm.aspx` | ICM_Approval_Requests | 1 | LOW |
| `/cmat/Lists/PIO_Approval_Requests/NewForm.aspx` | PIO_Approval_Requests | 1 | LOW |
| `/cmat/Lists/PIO_Approval_Requests/DispForm.aspx` | PIO_Approval_Requests | 1 | LOW |
| `/cmat/Lists/PIO_Approval_Requests/PIO_Approval_Requests_Mgrs.aspx` | PIO_Approval_Requests | 1 | LOW |
| `/cmat/Lists/ITAU_Case_Tasks/AllItems.aspx` | ITAU_Case_Tasks | 1 | LOW |
| `/cmat/Lists/ITAU_Case_Tasks/NewForm.aspx` | ITAU_Case_Tasks | 1 | LOW |
| `/cmat/Lists/ITAU_Narratives/NewForm.aspx` | ITAU_Narratives | 1 | LOW |
| `/cmat/Lists/PIOs_Narrative/NewForm.aspx` | PIOs_Narrative | 1 | LOW |
| `/cmat/Lists/PIO_Log_Entries/NewForm.aspx` | PIO_Log_Entries | 1 | LOW |
| `/cmat/Lists/PIO_Log_Entries/DispForm.aspx` | PIO_Log_Entries | 1 | LOW |
| `/cmat/Lists/Persons/DispForm.aspx` | Persons | 1 | LOW |
| `/cmat/Lists/ICM_Narratives/NewForm.aspx` | ICM_Narratives | 1 | LOW |
| `/cmat/Lists/PIO_Case_Tasks/NewForm.aspx` | PIO_Case_Tasks | 1 | LOW |
| `/cmat/Lists/ITAU_Log_Entries/NewForm.aspx` | ITAU_Log_Entries | 1 | LOW |
| `/cmat/Lists/ICM_Log_Entries/NewForm.aspx` | ICM_Log_Entries | 1 | LOW |
| `/cmat/Lists/Briefings/DispForm.aspx` | Briefings | 1 | LOW |
| `/cmat/Lists/ITAU_Cal_Abbotsford/DispForm.aspx` | ITAU_Cal_Abbotsford | 1 | LOW |
| `/cmat/Lists/Security_Alerts/DispForm.aspx` | Security_Alerts | 1 | LOW |
| `/cmat/Lists/ITAU_Approval_Requests/NewForm.aspx` | ITAU_Approval_Requests | 1 | LOW |

**Expected Content**: Instruction banners (e.g., "Note: When Adding a New Case make sure all Subjects and Affected Persons are already in the ITAU Persons Database")  
**Modernization Path**: Replace with static text in form instructions or modern form header text

---

#### B. Publishing Pages (91 Content Editors on 36 unique pages)

**List of pages with Content Editors (in order of appearance in CSV)**:

| Page | Web Part Count | Priority |
|------|---|---|
| `/cmat/Pages/My_ICM_Cases.aspx` | 2 | HIGH |
| `/cmat/Pages/ICM_Documents.aspx` | 1 | MEDIUM |
| `/cmat/Pages/ICM_Cases.aspx` | 2 | HIGH |
| `/cmat/Pages/Orphan_Approval_Requests.aspx` | 1 | LOW |
| `/cmat/Pages/Appearing_Persons_Briefing.aspx` | 1 | MEDIUM |
| `/cmat/Pages/ICM_My_Tasks.aspx` | 4 | HIGH |
| `/cmat/Pages/ICM_All_Approval_Requests.aspx` | 5 | HIGH |
| `/cmat/Pages/ICM_My_Approval_Requests.aspx` | 5 | HIGH |
| `/cmat/Pages/PIO_Cases.aspx` | 3 | HIGH |
| `/cmat/Pages/All_Briefings_and_Security_Alerts.aspx` | 1 | MEDIUM |
| `/cmat/Pages/All_Appearances.aspx` | 1 | MEDIUM |
| `/cmat/Pages/All_Cases.aspx` | 1 | MEDIUM |
| `/cmat/Pages/all_progress_logs.aspx` | 1 | MEDIUM |
| `/cmat/Pages/Orphan_Progress_Logs.aspx` | 1 | LOW |
| `/cmat/Pages/Orphan_Tasks.aspx` | 1 | LOW |
| `/cmat/Pages/portal.aspx` | 1 | HIGH |
| `/cmat/Pages/Persons_PIO.aspx` | 2 | HIGH |
| `/cmat/Pages/Add_Edit_Persons.aspx` | 2 | MEDIUM |
| `/cmat/Pages/All_Tasks.aspx` | 1 | MEDIUM |
| `/cmat/Pages/PIO_My_Tasks.aspx` | 3 | MEDIUM |
| `/cmat/Pages/Approval_Requests_for_Supervisors.aspx` | 2 | MEDIUM |
| `/cmat/Pages/ITAU_My_Tasks.aspx` | 3 | MEDIUM |
| `/cmat/Pages/Manage_Security_Alerts.aspx` | 2 | MEDIUM |
| `/cmat/Pages/ITAU_Documents.aspx` | 1 | MEDIUM |
| `/cmat/Pages/My_PIO_Cases.aspx` | 3 | HIGH |
| `/cmat/Pages/ITAU_All_Tasks.aspx` | 2 | MEDIUM |
| `/cmat/Pages/ITAU_All_Approval_Requests.aspx` | 4 | HIGH |
| `/cmat/Pages/Manage_Reference_and_Templates.aspx` | 1 | MEDIUM |
| `/cmat/Pages/All_Approval_Requests.aspx` | 1 | MEDIUM |
| `/cmat/Pages/Judiciary_Crown_Related_Cases.aspx` | 1 | MEDIUM |
| `/cmat/Pages/Unfiled_Documents.aspx` | 1 | MEDIUM |
| `/cmat/Pages/Briefings_and_Security_Alerts.aspx` | 2 | MEDIUM |
| `/cmat/Pages/Orphan_Appearances.aspx` | 1 | LOW |
| `/cmat/Pages/ITAU_Cases.aspx` | 4 | HIGH |
| `/cmat/Pages/PIO_Documents.aspx` | 1 | MEDIUM |
| `/cmat/Pages/PIO_My_Approval_Requests.aspx` | 3 | MEDIUM |
| `/cmat/Pages/ICM_All_Tasks.aspx` | 3 | MEDIUM |
| `/cmat/Pages/PIO_All_Tasks.aspx` | 2 | MEDIUM |
| `/cmat/Pages/Persons_ICM.aspx` | 2 | HIGH |
| `/cmat/Pages/My_ITAU_Cases.aspx` | 4 | HIGH |
| `/cmat/Pages/All_Persons.aspx` | 2 | MEDIUM |
| `/cmat/Pages/Persons_ITAU.aspx` | 2 | HIGH |
| `/cmat/Pages/All_Case_Documents.aspx` | 1 | MEDIUM |
| `/cmat/Pages/ITAU_My_Approval_Requests.aspx` | 5 | HIGH |
| `/cmat/Pages/PIO_All_Approval_Requests.aspx` | 2 | MEDIUM |

---

## 3. Unique Web Parts Requiring Independent Analysis

### Unique Web Part Types (2)

| Web Part Type | Count | Severity | Action |
|---|---|---|---|
| **Script Editor** | 3 | 🔴 CRITICAL | Inspect code; rebuild in Power Apps/Power Fx |
| **Content Editor** | 115 | 🟡 MEDIUM | Inspect; most trivial; replace with rich text or static text |

### Analysis Approach by Web Part Type

#### Script Editor Web Parts (3)

These web parts contain custom JavaScript code and require detailed code inspection:

**For each Script Editor**:
1. Access the page in SharePoint and view the web part code
2. Document what the JavaScript does
3. Determine if it's:
   - Form validation logic
   - Auto-fill/cascading dropdowns
   - UI styling/hiding fields
   - External API calls
   - Other business logic
4. Decide modernization approach:
   - **Power Apps form** with Power Fx formulas
   - **Modern form customizations** via form layout
   - **SPFx form customizer** (if complex)

---

#### Content Editor Web Parts (115)

Most are trivial and need only basic migration steps:

**Fast-path approach**:
1. **Assume trivial** (instruction text) unless investigation shows otherwise
2. **For list forms (24 instances)**: Replace with form header instruction text
3. **For publishing pages (91 instances)**: 
   - If static text only: Inline into page using modern rich text section
   - If styled (CSS): Recreate styling with BC Design System / modern themes
   - If contains embedded scripts: Flag for closer review

**Content Editor Analysis Questions** (only if non-trivial):
- Does it contain HTML/CSS beyond basic rich text?
- Does it embed external content (images, iframes)?
- Does it contain JavaScript or jQuery?
- Does it reference external libraries or CDNs?

---

## 4. Pages Requiring Code Analysis Summary

### HIGH PRIORITY (Script Editors present, or complex dashboard pages)

**Script Editor Pages (3)**:
- `PIO_Cases/EditForm.aspx` — Custom JS on case edit form
- `ITAU_Cases/EditForm.aspx` — Custom JS on case edit form
- `ICM_Cases/EditForm.aspx` — Custom JS on case edit form

**Complex Dashboard Pages (11)**:
- `My_ICM_Cases.aspx` — Master-detail dashboard (~40 child views)
- `ICM_Cases.aspx` — All-cases view (multi-LVWP)
- `ICM_My_Tasks.aspx` — Task dashboard (4 CEWPs)
- `ICM_All_Approval_Requests.aspx` — Approval queue (5 CEWPs)
- `ICM_My_Approval_Requests.aspx` — My approvals (5 CEWPs)
- `PIO_Cases.aspx` — PIO cases (3 CEWPs)
- `My_PIO_Cases.aspx` — My PIO cases (3 CEWPs)
- `ITAU_Cases.aspx` — All ITAU cases (4 CEWPs)
- `ITAU_All_Approval_Requests.aspx` — ITAU approvals (4 CEWPs)
- `Persons_ICM.aspx` — Person detail page (~40 LVWPs, 2 CEWPs)
- `My_ITAU_Cases.aspx` — My ITAU cases (4 CEWPs)
- `ITAU_My_Approval_Requests.aspx` — My ITAU approvals (5 CEWPs)
- `Persons_ITAU.aspx` — Person detail ITAU view (2 CEWPs)

### MEDIUM PRIORITY (Publishing pages with 1–3 CEWPs)

~20 pages with 1–3 Content Editors; mostly trivial instruction text

### LOW PRIORITY (Orphan admin pages)

- `Orphan_Approval_Requests.aspx` — Admin data quality
- `Orphan_Progress_Logs.aspx` — Admin data quality
- `Orphan_Tasks.aspx` — Admin data quality
- `Orphan_Appearances.aspx` — Admin data quality

---

## 5. Unique Web Parts Needing Independent Analysis

| Web Part Type | Count | Pages | Analysis Status |
|---|---|---|---|
| **Script Editor** | 3 | 3 unique pages (all case list edit forms) | 🔴 PENDING — Inspect JS code in each |
| **Content Editor** | 115 | 46 unique pages | 🟡 PENDING — Categorize by trivial vs. complex |

### Next Steps

1. **Script Editors (Immediate)**: 
   - Access each case list edit form (PIO_Cases, ITAU_Cases, ICM_Cases EditForm.aspx)
   - View the Script Editor web part properties and code
   - Document what the JavaScript does
   - Plan Power Apps form rebuild

2. **Content Editors (Phased)**:
   - HIGH priority pages: Inspect for embedded CSS/JS
   - MEDIUM/LOW priority pages: Assume trivial, inspect only if modernization attempt fails

3. **Documentation**:
   - Create a per-web-part analysis sheet with code snippets + modernization plan
   - Update ASPX-MODERNIZATION-STRATEGY.md with findings

---

## 6. Code Analysis Findings (2026-07-15, FINAL — all 121 web parts resolved) — Answering "how many unique code instances do we have?"

`analyze-webpart-code.py` grouped all 121 web part instances by what they actually **do** (not just where they sit), resolving external `<script src>` references against locally downloaded JS helper files in `14_prototyping/aspx_conversions/site-assets/JS/`.

**Note on the process**: the first extraction pass (against a stale `legacy_webparts_scan_results.csv` from weeks earlier) failed on all 3 Script Editors with `"The operation could not be completed because the Web Part is not on this page"` — the recorded WebPartIds no longer matched what's live on those pages. Re-running `scan-webparts.ps1` to refresh WebPartIds, then re-running `extract-webpart-content.ps1`, resolved all 3 (see Tooling section above for the full pipeline and the "Important correction" note about `exportwp.aspx`).

### Headline result: 121 web part instances → 38 unique functional groups

| Category | Instances | Meaning |
|---|---:|---|
| Empty / hidden placeholder | 31 | No content — safe to ignore, do not migrate |
| Static rich-text banner (no code) | 17 | Plain instruction/banner text — copy-paste into modern Text web part |
| External helper script(s), no additional inline logic | 51 | Loads one or more of the 26 known `.js` helper files (see below), no custom logic beyond that |
| Custom inline JavaScript logic | 22 | Contains actual inline `<script>` business logic beyond just loading a helper |

### The 3 Script Editors: resolved — here's what they actually do

All 3 (`PIO_Cases/EditForm.aspx`, `ITAU_Cases/EditForm.aspx`, `ICM_Cases/EditForm.aspx`) run **byte-for-byte identical inline jQuery** (1682 chars): a case-status-driven field lock.

- Watches the `Status` dropdown on the case Edit form
- When `Status = "Closed"` (on page load, or live when the user changes it): auto-sets `Case Closed Date` to today's date, disables that field, and hides its date-picker icon
- Reverting `Status` away from `"Closed"` unlocks the field again
- Contains **commented-out (disabled)** code that would have additionally locked `Brief Description` and `Open Date` the same way — evidently scoped back at some point, left in place

**SPO recommendation**: **Native Power Apps equivalent — no SPFx needed.** Rebuild the case Edit form as a Power Apps customized SharePoint form:
- `Case Closed Date` DataCard's `DisplayMode` formula: `If(Status.Selected.Value = "Closed", DisplayMode.View, DisplayMode.Edit)`
- `Case Closed Date` field's `Default` value formula: conditionally `Today()` when transitioning to Closed

This is a standard, well-supported Power Apps pattern. **Effort: Low.**

### Unique external JS helper files referenced (26 total, all already downloaded locally)

Every `.js` file referenced by any web part is already available at `14_prototyping/aspx_conversions/site-assets/JS/` — no further downloading needed. Full descriptions per file are embedded in `analyze-webpart-code.py`'s `KNOWN_JS_SUMMARIES` dict and in the generated report. Categories of what these files do:

- **jQuery libraries** (3 versions: 1.4.4, 1.7.2, 3.5.0) — third-party dependency, not custom logic
- **UI hiding/renaming helpers** (`HideLinksInDisplayForm.js`, `HideLinksToPersons.js`, `HideLinksToListForm.js`, `HideGear.js`, several `*HeadingChanger.js` files) — DOM manipulation to hide links/buttons or rename default SharePoint labels
- **Parent-child form auto-fill** (`RLHelper-ChildNewForm.js` / `RLHelper-ParentDisplayForm.js`) — passes a parent item's ID via query string so a child New form can auto-populate its "Related to Case"/"Related to Person" lookup field
- **Conditional formatting** (`ConditionalColoring.js`) — row/cell coloring based on column values
- **Misc utility** (`showattachmentname.js`, `makehyperlink.js`, `linkCase.js`, `linkPIOCase.js`, `sputility.js`, calendar-related helpers, `Greeting.js`)

### SPO migration recommendation by group type

| Group type | SPO recommendation | Effort |
|---|---|---|
| Empty/placeholder | Do not migrate | None |
| Static text banner | Direct copy-paste into modern Text web part | Trivial |
| External helpers only (no inline logic) | **No SPFx needed for most.** Recreate the effect using modern List View **Column/Row Formatting** (JSON-based conditional styling, no code) wherever the helper is just hiding/coloring/renaming. A small SPFx Application Customizer only if formatting JSON can't achieve the exact effect. | Low–Medium |
| Inline logic: `fillfromParent()` pattern | **Native SPO equivalent exists** — a Power Automate flow triggered on form load, or a Power Apps customized form reading the `Param()` function, can pre-populate the lookup field from a query-string parameter. **No SPFx required.** | Low–Medium |
| Inline logic: case-status field lock (the 3 Script Editors — see above) | **Native Power Apps equivalent** — `DisplayMode`/`Default` formulas on the customized form. **No SPFx required.** | Low |
| Inline logic: case-status-based button/icon hiding (dashboard pages like `My_ICM_Cases.aspx` / `ICM_Cases.aspx` / `PIO_Cases.aspx`) | Achievable via an SPFx **List View Command Set** (conditionally disable/hide commands), or simpler: enforce via item-level permissions/workflow when a case is closed if the real goal is preventing edits rather than just hiding UI | Medium |
| Inline logic: unrecognized/other | Requires manual code read (full content is in `webpart_content_extract.json`) before a path can be chosen | Medium–High |

### Key takeaway

**Almost none of this requires SPFx.** Of 121 web part instances (99 = 82%):
- **99 instances (82%)** are either empty, trivial text, or external-helper-only — achievable with modern SPO Column/Row Formatting, no code
- A meaningful chunk of the remaining 22 "inline logic" instances have **native, no-code SPO equivalents**:
  - `fillfromParent` pattern → Power Automate / Power Apps `Param()`
  - **The 3 Script Editors (case-status field lock)** → Power Apps `DisplayMode`/`Default` formulas
- Only the dashboard-page "hide buttons when case closed" pattern and any remaining unrecognized instances likely need a small SPFx Command Set or manual review

Full per-group detail (every page + WebPartId in each group, exact code-derived summary, exact recommendation) is in [`webpart-code-analysis.md`](./webpart-code-analysis.md); structured data in [`webpart-code-groups.json`](./webpart-code-groups.json).

---

## 7. Manual Code Review (2026-07-15) — Reading All 38 Groups Directly, Not Just Heuristics

The automated classification in Section 6 is heuristic-based (keyword/pattern matching in `analyze-webpart-code.py`). To get a genuinely reliable answer, every one of the 38 groups' actual source was consolidated into one file and read directly, one at a time, rather than trusting the script's categorization alone. Consolidated source: [`ALL-UNIQUE-WEBPART-CODE-FOR-REVIEW.md`](./ALL-UNIQUE-WEBPART-CODE-FOR-REVIEW.md) (one representative code sample per group, in fenced code blocks, with all member pages/WebPartIds listed).

### Byte-identical duplicate count

Of 121 total web parts, there are only **67 distinct byte-identical content strings**:
- **20 content strings repeat verbatim** across 2+ pages
- **47 content strings are unique** (appear once)
- Largest duplicate cluster: **12 identical copies** of a trivial CSS-only title-styling block

### Key correction from manual review: the "hide buttons when case closed" pattern is ONE behavior, not six

Groups 22–27 in `webpart-code-groups.json` (6 separate singleton groups, all `InlineLogic`) were split apart by the automated grouping purely because of **incidental per-page noise**:
- Each page's copy hardcodes a different auto-generated jQuery selector ID (`#scriptWPQ4`, `#scriptWPQ7`, `#scriptWPQ9`, `#scriptWPQ3`, etc. — SharePoint's per-instance List View Web Part DOM IDs, baked into the script when it was copy-pasted onto each page)
- One copy (`ICM_Cases.aspx`) is additionally corrupted by rich-text-editor spell-check artifacts (`ms-rtegenerate-skip` spans wrapping nearly every identifier), making it look textually very different from the others despite running identical logic

**Reading all 6 side-by-side confirms they are the same behavior**: find the `Status` column value in a list view's rendered table; if it equals `"Closed"`, hide that web part zone's "New Item" hero command button and row action icons. Appears on `My_ICM_Cases.aspx`, `ICM_Cases.aspx`, `PIO_Cases.aspx` (×2 instances), `My_PIO_Cases.aspx`, `ITAU_Cases.aspx` (×2 instances) — always paired with loading `linkPIOCase.js`. **6 instances, 1 true pattern.**

This means the automated tool's group count (38) slightly overstates true behavioral diversity — **the real number of distinct behaviors is ~33**, matching the byte-duplicate analysis above once this one pattern is correctly merged.

### Full confirmed inventory of all 38 groups (manually verified)

| # | Category | Instances | Confirmed behavior |
|---|---|---:|---|
| 1 | Empty | 31 | Mostly true empty `<Content/>`; one instance is a real CSS rule hiding SharePoint's "People also viewed" recommendations panel |
| 2 | ExternalHelpersOnly | 14 | `ConditionalColoring.js` + `HideLinksToPersons.js` combo |
| 3 | ExternalHelpersOnly | 11 | Same combo + `NewItemToAddNewHeadingChanger.js` |
| 4 | InlineLogic | 10 | `fillfromParent("Related to Case")` — auto-fill lookup from parent |
| 5 | ExternalHelpersOnly | 7 | Coloring + hide-links + heading-rename + `showattachmentname.js` |
| 6 | ExternalHelpersOnly | 6 | Coloring + hide-links + rename + `RLHelper-ParentDisplayForm.js` + `showattachmentname.js` |
| 7 | ExternalHelpersOnly | 3 | `HideLinksInDisplayForm.js` only (DispForm pages) |
| 8 | InlineLogic | 3 | **The 3 Script Editors** — case-status field lock on Case Closed Date (see Section 6) |
| 9 | InlineLogic | 3 | `fillfromParent("Related to Person")` — same auto-fill mechanism, different target field |
| 10 | ExternalHelpersOnly | 2 | Coloring + rename + hide-links + `showattachmentname.js` (Briefings/Security Alerts pages) |
| 11–13 | TextOnly | 2 each | "Add case → check Persons DB first" reminder banners (2 near-identical variants) |
| 14–21 | ExternalHelpersOnly | 1 each | Various single-page helper combinations (link-case builders, makehyperlink, purge planning coloring, etc.) |
| **22–27** | **InlineLogic** | **1 each (6 total)** | **Confirmed identical: "hide buttons when case closed" pattern — see correction above** |
| 28–29, 32–33, 36–38 | TextOnly | 1 each | "Covering for someone? Click here to see all tasks/approvals" banners — per-section variants (ICM/PIO/ITAU) |
| 30 | TextOnly | 1 | Reference Material and Templates link list |
| 31 | TextOnly | 1 | Portal homepage: CMAT support contact + F11/navigation tips |
| 34 | TextOnly | 1 | "Security Alerts can have pdf attachments" note |
| 35 | TextOnly | 1 | Briefings/Security Alerts usage notes (4-item bullet list) |

### Revised bottom line

**~33 truly distinct behaviors across 121 web part instances**, none requiring anything beyond:
- Direct copy-paste (empty/text banners — the large majority)
- Modern List View Column/Row Formatting, no code (external-helper-only combinations)
- Native Power Automate/Power Apps features, no SPFx (`fillfromParent`, the 3 Script Editors' field-lock)
- One small SPFx Command Set (or a permissions-based no-code alternative) for the single "hide buttons when case closed" pattern, deployed identically across 6 dashboard pages

---

## 8. External JS Helper File Analysis (2026-07-15) — Reading All 23 Files Directly

Section 6's `KNOWN_JS_SUMMARIES` dict in `analyze-webpart-code.py` was built from filenames and prior assumptions, not actual code review. Every one of the 23 non-jQuery `.js` files at `14_prototyping/aspx_conversions/site-assets/JS/` was read directly to confirm what each does and flag anything more substantial than "hide a link" / "recolor text".

### Files with genuine, non-trivial logic (flagged for closer migration attention)

| File | Referenced by CEWP/SEWP? | What it actually does | Migration note |
|---|:---:|---|---|
| **linkCase.js** | Yes (indirectly — via `JSLink`-style field rendering, not `<script src>`) | Uses `SPClientTemplates.TemplateManager.RegisterTemplateOverrides` to override rendering of the **"Case" field** in list views. Hardcodes 3 SharePoint **View GUIDs** (one per ITAU_Cases/PIO_Cases/ICM_Cases) and builds a link to that case's detail view with `SelectedID` set. | This is a JSLink field customizer, not a simple DOM-hider. **Hardcoded View GUIDs are fragile** — they won't exist in SPO and must be re-derived per view. Modern equivalent: SPFx Field Customizer, or (simpler) a calculated/formatted column using modern column formatting JSON with `$"[$Case_ID]"`-style expressions if the target view GUID can be parameterized differently in SPO. |
| **linkPIOCase.js** | Yes | Same JSLink field-override mechanism, applied to the `RelatedPIOCases` lookup field. Also hardcodes a View GUID. | Same note as `linkCase.js`. |
| **makehyperlink.js** | No (not referenced by any of the 121 scanned CEWP/SEWP; likely used via list-level JSLink settings, out of CEWP/SEWP scan scope) | JSLink field override on a `link_to_print_appearance` field — renders a link to `Appearing_Persons_Briefing.aspx` (the printable briefing view) using the item's `ID` and a hardcoded View GUID. | Same fragile-GUID concern as above. Confirm whether this is still wired up anywhere (JSLink settings aren't visible via the CEWP/SEWP scan — would need a separate JSLink audit). |
| **showattachmentname.js** | Yes | JSLink override on the **Attachments** field. Makes a **synchronous** (`async: false`) AJAX call to `_api/web/lists/getbytitle(...)/items(...)/AttachmentFiles` and renders each attachment as a clickable link, inline in the list view. | Real REST-based attachments renderer — more than "displays a name." The `async: false` blocking call is a genuine performance anti-pattern (blocks the browser UI thread per row rendered) — worth flagging as technical debt regardless of migration path. Modern equivalent: native SPO list views already render attachment icons/links OOB — this custom code may be fully unnecessary in SPO. |
| **RLHelper-ChildNewForm.js** / **RLHelper-ParentDisplayForm.js** | Yes (13 instances via `fillfromParent()`) | Public domain snippet ("SharePoint 2010 Related List Pre-fill v1.2", from a Google Code project). Detects if the New form was opened as a **modal dialog** (`IsDlg=1` query param) from a parent item, extracts the parent's numeric ID from `SelectedID`, and sets a lookup dropdown's value to that ID. | Confirms Section 6/7's `fillfromParent` description with the precise trigger condition (must be opened via dialog with `IsDlg=1`). Native SPO/Power Apps equivalent already documented in Section 6 — no change to that recommendation. |
| **Greeting.js** *(not referenced by any of the 121 scanned web parts)* | No | Uses the **client-side object model** (`SP.ClientContext`, not jQuery) to fetch the current user's title/display name and inject a time-of-day greeting ("Good Morning/Afternoon/Evening, {FirstName}") into an element with id `userTitle`. | Likely used on the classic portal homepage (outside CEWP/SEWP scope, or on a page not currently having an active web part reference). Trivial to replicate with an SPFx web part or even a Power Apps/Viva Connections greeting card — this exact pattern is a common OOB Viva Connections/SharePoint home site feature in modern SPO. |
| **OpenCalendarItemModal.js** *(not referenced)* | No | Substantial: hooks `SP.UI.ApplicationPages.CalendarStateHandler.prototype.onItemsSucceed` (patches the SharePoint calendar's client-side rendering pipeline) to rewrite every calendar item link to open in a **modal dialog** (`SP.UI.ModalDialog.showModalDialog`) instead of navigating away, and re-applies itself after the "Show n more items" expander is clicked. | Genuinely non-trivial JS — patches a SharePoint internal prototype method. Not found on any currently-scanned CEWP/SEWP, so likely applied via calendar list/view JSLink settings rather than a Content Editor, or it's for a calendar page category outside this scan's scope (only 1 CEWP was found on any `ITAU_Cal_*` calendar, and it was empty). **Recommend a separate audit of calendar list JSLink/view settings** before assuming this is dead code — modern SPO calendars have no modal-dialog equivalent by default; if this behavior is still wanted, it needs an SPFx Application Customizer. |
| **calendar-month-backlink.js** *(not referenced)* | No | Substantial: on a calendar item's Display form, parses a hidden field-metadata HTML comment to extract the `EventDate`, computes month/year, builds a "back to month view" link, **and rewrites the Close button's `onclick` handler** to redirect to that computed calendar URL instead of the default close behavior. | Same status as `OpenCalendarItemModal.js` — real logic, not found in the current CEWP/SEWP scan, likely calendar-list-specific and outside scan scope. Needs the same separate calendar JSLink audit. |
| **sputility.js** *(not referenced)* | No | **Full third-party library** — "SPUtility.js" v0.14.2 by Kit Menke (MIT license, sputility.codeplex.com, built 2016). ~2,000 lines providing a complete field-abstraction API (`SPField`, `SPTextField`, `SPChoiceField`, `SPDateTimeField`, `SPUserField`, etc.) for getting/setting/showing/hiding any classic SharePoint form field client-side. | Not referenced by any of the 121 scanned web parts — likely a vendored dependency for other custom scripts not captured by this scan (or a leftover/unused library). If any page turns out to depend on it (would need a broader JSLink/master-page audit), each dependent script's logic would need individual review since this library enables arbitrary field manipulation. |
| **HideGear.js** *(not referenced)* | No | Continuously polls (every 500ms via `setInterval`, indefinitely) to hide the O365 top-nav Settings gear icon for users without `ManageWeb` permission. | Cosmetic only (not a real permission/security boundary — the gear is still functionally accessible via URL). The `setInterval` polling loop never clears itself — minor performance concern. Not found in current CEWP/SEWP scope. |
| **default_All_Day_Event.js** *(not referenced)* | No | Trivial: auto-checks the "All Day Event" checkbox on calendar New-item forms. | Straightforward — modern SPO calendar column default values can replicate this without code. |
| **connect_to_Outlook-hold.js** *(not referenced)* | No | Calls `ExportHailStorm(...)` (the classic "Connect to Outlook" iCal export handler) with **hardcoded parameters pointing to `https://itau.dev.jag.gov.bc.ca`** (DEV environment) and a list named `Security_Events` — note this list name doesn't match any list documented elsewhere in this project (`Security_Alerts` is the actual CMAT list name). | **Likely broken/stale reference** — points to DEV, not PROD, and references a list name (`Security_Events`) not found in the CMAT schema (`Security_Alerts` is the real list). File name itself (`-hold`) suggests it was already put on hold/disabled. Flag as probable dead code; do not carry forward into SPO migration without confirming with SMEs whether this was ever live. |

### Files confirmed trivial as originally assumed

`ConditionalColoring.js`, `HideLinksInDisplayForm.js`, `HideLinksToListForm.js`, `HideLinksToPersons.js`, `ItemToCaseHeadingChanger.js`, `ItemToPersonHeadingChanger.js`, `NewItemToAddNewHeadingChanger.js`, `NewTaskToAddNewHeadingChanger.js`, `TaskToAlertHeadingChanger.js`, `TaskToItemHeadingChanger.js` — all confirmed to do exactly what their names suggest: simple DOM text-color styling by keyword match, or brute-force `<span>` text search/replace to rename a default SharePoint button label. No hidden complexity.

### Key takeaway

**7 of the 23 non-jQuery JS files are not referenced by any of the 121 scanned CEWP/SEWP web parts**: `sputility.js`, `calendar-month-backlink.js`, `connect_to_Outlook-hold.js`, `default_All_Day_Event.js`, `Greeting.js`, `HideGear.js`, `OpenCalendarItemModal.js`. Three of these (`calendar-month-backlink.js`, `OpenCalendarItemModal.js`, `default_All_Day_Event.js`) are calendar-specific and were very likely wired up via **list/view JSLink settings on the `ITAU_Cal_*` calendars** rather than via a Content Editor Web Part — outside what `scan-webparts.ps1` looks for (it only scans for CEWP/SEWP, not JSLink column/view settings). **A separate JSLink/view-settings audit of the calendar lists is recommended** before concluding these are dead code — two of them (`OpenCalendarItemModal.js`, `calendar-month-backlink.js`) contain genuinely non-trivial logic that would need a real migration decision if still active.

Two files with **hardcoded SharePoint View GUIDs** (`linkCase.js`, `linkPIOCase.js`, `makehyperlink.js`) are JSLink field-renderers, not simple link-hiders — these need explicit re-implementation (SPFx Field Customizer or modern column formatting) since the GUIDs they reference won't exist in SPO.

One file (`connect_to_Outlook-hold.js`) appears to be **stale/broken** — hardcoded to DEV and referencing a list name that doesn't match the actual CMAT schema.

---

*Analysis generated: 2026-07-15 (final pass after WebPartId refresh)*  
*Source: legacy_webparts_scan_results.csv (121 total web parts, refreshed via scan-webparts.ps1); webpart_content_extract.json (121/121 extracted); webpart-code-groups.json (38 unique groups, ~33 after manual dedup correction); ALL-UNIQUE-WEBPART-CODE-FOR-REVIEW.md (manual review source); 14_prototyping/aspx_conversions/site-assets/JS/ (23 non-jQuery JS files, all read directly for Section 8)*
