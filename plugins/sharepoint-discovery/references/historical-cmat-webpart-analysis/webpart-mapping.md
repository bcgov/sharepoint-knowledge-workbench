# SharePoint 2016 → SharePoint Online: Web Part & Layout Mapping

> **Living document.** Updated after each prototype conversion run.
> Machine-readable companion: [`webpart-mapping.json`](webpart-mapping.json)
> ADRs for gap decisions: [`adr/`](adr/)

---

## Status Legend

| Status | Meaning |
|--------|---------|
| ✅ MAPPED | Full conversion supported, tested in at least one prototype |
| ⚠️ PARTIAL | Conversion works with known limitations |
| ❌ GAP | No direct SPO equivalent — mitigation required |
| ❓ UNKNOWN | Not yet encountered in prototype runs |

---

## Web Part Type Mapping

| SP 2016 Type | Friendly Name | SPO Target | Status | Fidelity | First Evidence |
|---|---|---|---|---|---|
| `ContentEditorWebPart` | Content Editor | Text Web Part | ✅ MAPPED | High | portal.aspx |
| `XsltListViewWebPart` (standalone) | List View — Primary/Secondary | **List web part (modern) + provisioned view** | ✅ MAPPED | High | My_PIO_Cases.aspx |
| `XsltListViewWebPart` (connected provider) | List View — sends selection | List web part (standalone only, connection lost) | ⚠️ PARTIAL | Medium | My_PIO_Cases.aspx |
| `XsltListViewWebPart` (connected consumer) | List View — receives filter (Child role) | **NOT_MIGRATED** | ❌ GAP CRITICAL | None | My_PIO_Cases.aspx |
| `SummaryLinkWebPart` | Summary Links (portal grid) | Text Web Part (HTML table) | ✅ MAPPED | Medium | portal.aspx |
| `ScriptEditorWebPart` | Script Editor | TBD (SPFx/Embed) | ❓ UNKNOWN | Unknown | — |
| `PageViewerWebPart` | Page Viewer (iframe) | Embed Web Part | ⚠️ PARTIAL | Medium | — |
| `ImageWebPart` | Image | Image Web Part | ⚠️ PARTIAL | Medium | — |

---

## Layout Mapping

| SP 2016 Layout | SPO Layout | PnP Flag | Status | Notes |
|---|---|---|---|---|
| Blank Web Part Page | Home | `-LayoutType Home` | ✅ MAPPED | Do NOT use Article — adds unwanted gray hero banner |
| Publishing Page (single column) | Article | `-LayoutType Article` | ⚠️ PARTIAL | Hero section present, may need manual removal |

---

## Section / Zone Mapping

| SP 2016 Zone Pattern | SPO Section Template | PnP Flag | Notes |
|---|---|---|---|
| Full-width single zone | OneColumn | `-SectionTemplate OneColumn` | Default for most CMAT pages |
| Two-column zone | TwoColumn | `-SectionTemplate TwoColumn` | |
| Three-column zone | ThreeColumn | `-SectionTemplate ThreeColumn` | SPO maximum native columns |
| Four-column zone | OneColumn + HTML `<table>` | `-SectionTemplate OneColumn` | SPO native max is 3 — use `<table>` with 4 `<td>` cells inside Text web part |

---

## Architectural Rules

These rules apply to the conversion pipeline for all page types. Updated as new patterns are discovered.

| Rule | Description |
|---|---|
| **ARCH-001** | CAML lives in the **view**, not the page. Provision `CMAT_Migration_*` view on the list first; page web part references view by ID. |
| **ARCH-002** | Detect list view **role** before mapping: `Primary` (first unconnected) / `Child` (connected consumer) / `Secondary` (additional standalone). Role determines section placement and gap handling. |
| **ARCH-003** | Capture **relationship intent** even for unmigrated (Child) web parts: `Parent(ListName).ID → ChildList.LookupField`. Feeds SPFx/Power Apps redesign. |
| **ARCH-004** | Layout is **data-driven**: 1 primary + ≤2 others → OneColumn; 1 primary + >2 others → TwoColumn (70/30); content pages → Article. |
| **ARCH-005** | Detection **hierarchy**: WebPart XML > Rendered HTML > `views.json`. Record method used in manifest `detectionMethod` field. |

---

## Known Gaps & Mitigations

### GAP-001: Connected / Linked Web Parts — Revised Assessment

> **Correction (2026-06-15):** Earlier analysis incorrectly stated SPO modern has no equivalent to SP2016 Web Part Connections. SPO modern **does** support dynamic filtering between List web parts. The severity and migration approach below are updated accordingly.

**Affected pages:** Any page using SP2016 Web Part Connections (master/detail drill-down pattern).

**Confirmed scope (live WPM API scan — 2026-06-15, 76 pages):**

| Page | LVWP Count | Complexity |
|:---|:---|:---|
| `Persons_ICM.aspx` | ~40 | Most complex — every entity cross-ref across all 3 sections |
| `Persons_ITAU.aspx` / `Persons_PIO.aspx` | ~30 each | Same pattern, section-scoped |
| `My_ITAU_Cases.aspx` / `ITAU_Cases.aspx` | 14 | Cases + Tasks (×3) + Approvals + Log Entries + Documents + Checklist |
| `My_ICM_Cases.aspx` / `My_PIO_Cases.aspx` (and All variants) | 13 each | Same pattern per section |
| `ICM_All_Tasks.aspx` | 12 | Cross-section task dashboard |
| `Appearing_Persons_Briefing.aspx` | 6 | Read-only person brief |
| `All_Approval_Requests.aspx` | 3 | Cross-section approval view |

---

#### How SPO Dynamic Filtering Works

SPO modern List web parts support **Dynamic Filtering** — selecting a row in a parent List web part automatically filters connected child List web parts on the same page. This is the direct modern equivalent of SP2016 Web Part Connections.

**Requirements:**
- The child list must have a **lookup column** pointing to the parent list (e.g., `CaseId` lookup on Tasks → Cases)
- Both web parts must be OOB List web parts — custom SPFx web parts cannot participate
- Configuration: edit child web part → "Filter" → enable Dynamic filtering → select parent web part and map columns

**What works:**
- One parent driving **multiple children** simultaneously (each child independently connects to the same parent) ✅
- Fan-out pattern: Cases → Tasks, Cases → Log Entries, Cases → Documents, Cases → Approvals all on one page ✅
- CMAT already has the required lookup columns — `CaseId` fields exist on all child lists ✅

**Known limitations:**
- Each child web part can connect to **only one** filter source — no chaining (A→B→C nested filtering confirmed broken in Microsoft TechCommunity)
- Custom SPFx web parts cannot participate in dynamic data connections with OOB List web parts
- **Performance risk at scale:** a page with ~40 List web parts all firing simultaneous queries on row selection (e.g., `Persons_ICM.aspx`) needs testing — page load and filter response time unknown at that web part count
- Manual recreation required — the connections cannot be scripted via PnP PowerShell; each page must be configured by hand in the browser

---

#### Relationship Metadata (for page recreation reference)

```
Parent(ITAU_Cases).ID  → ITAU_Case_Tasks.CaseId
Parent(ITAU_Cases).ID  → ITAU_Log_Entries.CaseId
Parent(ITAU_Cases).ID  → ITAU_Approval_Requests.CaseId
Parent(ITAU_Cases).ID  → ITAU_Documents.CaseId
Parent(ITAU_Cases).ID  → Case_Check_List.CaseId
Parent(Persons).ID     → All_Appearances.PersonId
Parent(Persons).ID     → ITAU_Cases.SubjectPersonId (×3 sections)
```

---

#### Migration Options

| Option | Effort | Fidelity | Notes |
|:---|:---|:---|:---|
| **SPO Dynamic Filtering (manual recreation)** | Medium (per page, manual browser config) | High — functionally equivalent | Viable for all pages where lookup columns exist. Not scriptable. ~49 pages to recreate. |
| **Power Apps canvas embed** | Medium (build once, reuse pattern) | High | Pending Protected B confirmation (open_questions.md Q42) |
| **React replatform (Opportunity 4)** | High (one-time build) | Highest | No SPO dependency, BC Gov Design System, API-driven, Protected B compliant. Recommended for Opportunity 4 prototype. |

**Revised severity: LOW–MEDIUM for simple pages (1→few connections), HIGH for complex hub pages (10–40 LVWPs).** Dynamic filtering is native and no-code but is a per-web-part mechanism, not a global page state. CMAT's complex pages exceed the scale it was designed for. Resolved for React replatform path.

**Decision record:** See [ADR-001](adr/ADR-001-connected-webparts-gap.md) — to be updated to reflect this correction.

**Full page inventory:** See [`../01_source_sharepoint/analysis/live-webpart-scan.md`](../01_source_sharepoint/analysis/live-webpart-scan.md)

**Research sources:** [Microsoft Support — Connect web parts](https://support.microsoft.com/en-us/office/connect-web-parts-in-sharepoint-b457668c-d843-4b1b-8977-a6f9228a1dec) · [SharePoint Maven — Dynamic Filtering](https://sharepointmaven.com/how-to-connect-lists-and-libraries-via-dynamic-filtering-in-sharepoint-online/) · [TechCommunity — Nested filtering broken](https://techcommunity.microsoft.com/discussions/sharepoint_general/nested-dynamic-filtering-on-web-parts-does-not-work/4278858)

---

## SPO Constraints (Learned from Prototype Runs)

| Constraint | Workaround |
|---|---|
| SPO strips inline CSS on `<a>`, `<li>`, `<span>` | Use `<div>`, `<table>`, `<h2>` for styled content |
| SPO native max 3-column section | Use OneColumn section + 4-cell `<table>` for 4-column layouts |
| `<table>` border shows despite `border:0` | Add `border-style:hidden` on `<table>`, `<td>`, `<tr>` |
| `Add-PnPPage` after `Remove-PnPPage` fails immediately | `Start-Sleep -Seconds 3` between remove and create |
| `Set-PnPPage -Publish` may fail on some tenants | Fallback: get file object, call `.Publish()` directly |
| Page layout `Article` adds gray hero banner | Use `-LayoutType Home` for dashboard/portal pages |
| Zero-width spaces (`​`) in legacy HTML | Strip with `-replace '​', ''` before using content |
| Icons/images use on-prem URLs | Repoint to `$TargetSiteUrl/SiteAssets/icons/<filename>` after running `migrate-site-assets.ps1` |

---

## Manifest Schema

Every conversion run emits a `webpart-manifest.json` alongside the preview HTML. Schema:

```json
{
  "sourcePage": "/cmat/Pages/My_PIO_Cases.aspx",
  "convertedAt": "ISO8601",
  "webParts": [
    {
      "zone": "wpz1",
      "type": "ContentEditor",
      "mappedTo": "TextWebPart",
      "gap": null
    },
    {
      "zone": "wpz5",
      "type": "XsltListView",
      "variant": "connected-consumer",
      "list": "PIO_Case_Tasks",
      "mappedTo": "NOT_MIGRATED",
      "gap": "GAP-001: LinkedWebPartConnection — no SPO modern equivalent"
    }
  ],
  "layout": {
    "template": "BlankWebPartPage",
    "mappedTo": "Home",
    "columnCount": 1
  },
  "gaps": ["GAP-001 x2"]
}
```

Manifests accumulate in `14_prototyping/evals/fixtures/manifests/`. The pipeline analyzer reads all manifests to produce the full web part frequency table and gap inventory across the site.

---

## Iteration Log

| Date | Page | New Mappings Added | New Gaps Found |
|---|---|---|---|
| 2026-06-01 | portal.aspx | ContentEditor→TextWebPart, SummaryLinks→HTML table, BlankWebPartPage→Home | — |
| 2026-06-03 | My_PIO_Cases.aspx | XsltListView standalone→List web part (modern) + provisioned view; ARCH-001–005 rules | GAP-001-CRITICAL: Connected web parts (functional regression) |
| 2026-06-03 | My_PIO_Cases.aspx | ListWebPart, TextWebPart | GAP-001-CRITICAL: LinkedWebPartConnection — functional regression |
| 2026-06-03 | My_PIO_Cases.aspx | TextWebPart | — |
| 2026-06-03 | My_PIO_Cases.aspx | TextWebPart, ListWebPart | GAP-001-CRITICAL: LinkedWebPartConnection — functional regression |
| 2026-06-15 | All 76 pages (live WPM API scan) | Confirmed LVWP counts per page; section-isolation at page level confirmed; Persons_ICM.aspx identified as most complex (~40 LVWPs); React Tier 4 added to GAP-001 mitigations | GAP-001 scope confirmed site-wide — dominant pattern, not edge case |
