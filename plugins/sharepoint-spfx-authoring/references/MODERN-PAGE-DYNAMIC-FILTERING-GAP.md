# Modern Page Dynamic Cross-Web-Part Filtering Gap

_lastUpdated: 2026-08-17 — added confirmed negative tests (FilterField1/FilterValue1 and DispForm.aspx) against real SharePoint Online test environment_

## Issue

Several SP2016 ASPX pages (e.g. `Appearing-Persons-Briefings.aspx`) use multiple web parts on one page with dynamic filtering: a top web part lists Persons, and selecting a person filters all other web parts on the page to that person's related data.

On SP2016, this is driven by a `SelectedID` URL query string parameter (e.g. `?SelectedID=1234`) that automatically filters the top Persons web part, which then cascades filtering to the other web parts on the page.

## Gap in SharePoint Online

In modern SPO pages, out-of-the-box web parts (List, Highlighted Content, etc.) do not support this same URL-parameter-driven, cross-web-part filtering behavior. Achieving equivalent behavior in SPO requires a custom SPFx web part (or web part set) to read the query string and coordinate filtering across the other web parts on the page — there is no no-code/out-of-the-box equivalent.

## Proven Solution: Consolidated Master-Detail SPFx Web Part

_Status: VALIDATED & PROVEN on Trial Tenancy (2026-08-17)_

### Why Native Modern List Web Parts Cannot Be Used
Live testing on the trial tenancy confirmed:
1. **SharePoint Online Modern List Web Parts do not support URL query string filtering** (`?SelectedID=...` or `?FilterField1=...`).
2. The modern List Web Part's "Dynamic filtering" only connects to other native List Web Parts on the canvas via mouse-click selection. It **does not accept custom SPFx dynamic data providers** as filter inputs.

### The Modern Replatforming Pattern: Master-Detail Dashboard
Instead of placing 5 separate list web parts on an ASPX page and trying to wire them together with cross-web-part connections:
- A single custom SPFx web part (`SelectedIdFilterWebPart` / `DossierBriefingWebPart`) reads `?SelectedID=<id>` from the URL.
- It executes parallel REST queries to retrieve:
  1. `Persons` (Identification & Status)
  2. `All_Appearances` (Upcoming where `EventDate >= Today` and Previous where `EventDate < Today`)
  3. `Dossier_Narratives` (Background Information)
- It renders all 5 sections in one unified, responsive dashboard matching the SP2016 layout.
- It embeds functional **`+ new appearance`**, **`+ new item`** (narrative), and **`Edit`** action buttons that link directly to SharePoint's native forms with `Source=<currentUrl>` return redirection.

### Benefits of the Master-Detail SPFx Solution
- **100% URL-Filtering Fidelity**: Works identically to SP2016's `?SelectedID=...` deep-linking.
- **Zero Canvas Configuration**: No fragile web part connection wiring in the page edit UI.
- **Superior Performance**: Fast, parallel asynchronous REST queries in a single client-side render pass.
- **Modern Responsive UI**: Clean card and table layouts matching Microsoft Fluent UI standards.
