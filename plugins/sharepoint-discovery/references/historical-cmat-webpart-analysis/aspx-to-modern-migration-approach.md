# Proposed Approach: SharePoint Page Migration (ASPX → Modern)

## 1. Inventory All ASPX Pages

Extract the full list of pages, metadata, and locations from the source SP2016 site before any conversion work begins.

- Run `scripts/page-migration/extract-site-navigation.ps1` to capture nav structure
- Run `scripts/page-migration/convert-wiki-page.ps1` (inventory mode) to enumerate all `.aspx` files
- Output: page list with URL, layout, last modified, author

---

## 2. Disposition Content Before Migration

Classify every page before migrating to avoid carrying low-value content into SPO.

| Disposition | Criteria |
|---|---|
| **Keep** | Active, referenced in navigation, or has known audience |
| **Merge** | Overlapping content with another page — consolidate first |
| **Archive** | No edits in 2+ years, not linked anywhere — export to static HTML |
| **Delete** | Confirmed stale, duplicated elsewhere, or explicitly decommissioned |

Reduces conversion volume and defect surface before any script work begins.

---

## 3. Analyze Page Structure

For all **Keep** pages:

- Group by **page layout** (WikiLayout, WebPartPage layouts 1–8, publishing layouts)
- Group by **web parts used** (CEWP, ListView, XsltListView, ContentQuery, custom)

---

## 4. Build Component Inventories

Produce two inventories from the analysis:

1. **Unique layouts** — count and example pages per layout
2. **Unique web parts** — count, source DLL (if known), and example pages per web part

These drive the classification step below.

---

## 5. Classify Web Parts by Migration Approach

For each unique web part, assign exactly one migration path:

| Class | Definition |
|---|---|
| **Directly convertible** | Script can convert with no manual intervention |
| **Replace with modern OOTB** | Map to a built-in SPO equivalent (e.g. XsltListView → List web part) |
| **Custom SPFx / Power Apps** | Only if the web part is business-critical |

> **Custom web part exceptions require explicit justification:**  
> - What business function does it serve?  
> - What is the build, support, and ongoing maintenance cost?  
> - Who approves it? (Not vendor discretion — must be a named business owner.)

---

## 6. Create Page Dependency Matrix

Map every **Keep** page to its layout and web parts.

Columns: `PageUrl | Layout | WebParts[] | ComplexityScore | RiskFlag`

Purpose: identify high-risk combinations (multiple custom web parts, deeply nested CTs) before scripted conversion begins.

---

## 7. Develop Isolated Test Cases

Test each component **independently** before testing page combinations:

- One test per unique layout
- One test per unique web part
- Validate: renders correctly, metadata preserved, no JS console errors

Catching issues at component level is far cheaper than diagnosing them in full-page context.

---

## 8. Test Representative Page Combinations

Select a coverage set of pages that exercises the most complex layout + web part combinations identified in the dependency matrix.

- Convert using scripts
- Validate with subject-matter users (not just technical review)
- Document pass/fail per combination

---

## 9. Separate Link Remediation from Page Conversion

Page conversion scripts do **not** fix broken links. These are distinct work streams.

Link remediation requires:

- A dedicated scan after conversion (tools: `scripts/page-migration/find-broken-links.ps1` or equivalent)
- A mapping of old SP2016 URLs → new SPO URLs
- A second pass to update page content, nav, and promoted links

Do not assume links will be correct after conversion alone.

---

## 10. Implement Robust Scripted Migration

Conversion scripts must include:

- **Per-page logging** — success/failure with page URL and error message
- **Error handling and retry** — failed pages re-queued, not silently skipped
- **Metadata validation** — Title, ContentType, Modified, Author preserved
- **Output validation** — converted page exists in SPO at expected URL

Scripts without these controls cannot be trusted at scale.

---

## 11. Conduct UAT on Representative Pages

Before full-scale execution, validate with business users:

- Functional equivalence (does the page do what it did before?)
- UX differences (modern rendering vs. classic — explicitly accepted, not assumed)
- Business acceptance sign-off per page group or layout type

---

## 12. Iterate and Refine

Use UAT findings to update:

- Conversion scripts
- Web part mapping rules
- Disposition classifications (some "Keep" pages may move to "Merge" after user review)

Revalidate the affected coverage set before proceeding to full scale.

---

## 13. Execute Full Migration at Scale

Run scripts across the full **Keep** dataset only after:

- All test combinations pass
- UAT sign-off received
- Link remediation plan confirmed
- Rollback plan documented (original ASPX files remain in SP2016 — read-only source)

Monitor logs in real time. Stop on first unexpected error class and diagnose before continuing.
