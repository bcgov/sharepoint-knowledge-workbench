# Dynamic page migration: conversion rules

Rules that govern how the plan and package are built: scope fields, page conventions, accordions, link policy, layout, relative paths and design tokens. Design-system detail: [Modern design system for modern pages](../bc-design-system-modern-pages.md).

## Contents

- [Plan and package](#plan-and-package)
- [Page conventions and accordions](#page-conventions-and-accordions)
- [Operations header band](#operations-header-band-title-banner)
- [Administration header band](#administration-header-band-title-banner)
- [Link policy](#link-policy)
- [Layout analysis](#layout-analysis)
- [Relative path building](#relative-path-building)
- [Design system](#design-system)

## Plan and package

- Source and destination are separate choices; ask for both, never infer either. Source = the SP2016 environment (usually PROD `source-tenant.example.com`, matching the inventory `Url`); destination = the SPO environment (`dev`, `test` or `prod`). `-ConfigPath` supplies both: its top-level connection is the destination and its `Source.SiteUrl` must match the source page host. The user picks the config from the root `config-spo-*.psd1` files; never assume or auto-build one. Never swap the source host to make a script pass.
- Require exactly one authoritative inventory record (`SiteName` + source `ServerRelativeUrl`). Never guess from a title or a nearby page.
- Source config must have `Source.ReadOnly = $true`; image extraction is read-only HTTP GET to SP2016 only.
- Missing, failed, partial or unavailable extraction is blocked, not a blank page. Unsupported components and cross-site dependencies need an explicit disposition.
- Plan: raw `exportwp.aspx` XML is authoritative for `ZoneID`/`PartOrder`. Missing `ZoneID` fails; missing `PartOrder` defaults to 0 (open `DEBT-20261005-SPMIG-15`), so verify placement first. Use `sharepoint-analyze-classic-pages` and `sharepoint-plan-page-modernization` for general analysis/layout.
- Scope fields required: `SiteName`, `ServerRelativeUrl`, `TargetPageServerRelativeUrl`, `Layout`, `TargetEnvironment`, `Wave`. Target: `Main` is `/SitePages/<leaf>.aspx`; other sites `/SitePages/<SiteName>/<leaf>.aspx`.
- Package: five inputs (scope, plan, image manifest, asset dir, output); scope/plan environment and wave must match; plan `WouldPublish=false`; reuse a complete exact wave-ID package set before rebuilding. Result is `Mode=DryRun`, `WouldPublish=false`; it never uploads.
- Duplicate target: require the user to choose `Reject`, `Approve` or `Skip`; never overwrite by implication. The package builder plans `CreateOnly`/`CreatePage` by default; only scope `ExistingPageDecision = "Approve"` plans `OverwriteExisting`/`OverwritePage`, and any other value stops the build.
- No raw ASPX upload. Dry-run is the default mode; a write needs the executor's `-Execute` flag, its confirmation token (`PUBLISH-SPO-PAGE`, supplied only by the user) and authorization.

## Page conventions and accordions

From the hand-built pages (see the Accordion entry's `pageConventions` and `designSystemReferences` in the mapping file):

- Follow `standard-design-system` accordion guidance (used sparingly, important content not hidden; sections collapsed by default, owner decision 2026-10-16). Add quick links at the top with one link per accordion section. No in-repo floating back-to-top extension is available; do not promise one. If a page requires a back-to-top control, ask the user to confirm a supported replacement before planning publication. Do not add per-section "Back to top" links inside collapsible sections.
- Content is copied from SP2016: clear formatting, then fix spacing. Review the plan's `ContentCleanup` findings (legacy `<font>`, Office/`ms-rte` classes, empty spans, stacked blank paragraphs, `&nbsp;` runs) and have the user check spacing against the SP2016 page.
- No extra white space: the breadcrumb starts directly with `Home >` (no leading `<p>&nbsp;</p>`), and no Text web part starts or ends with an empty paragraph or `<br>`; `convert-package-to-rte.ps1` trims them. Applies to new pages only; do not republish existing pages for this.
- A Bootstrap accordion (`panel-group`) is converted automatically (see `docs\analysis\accordion.md`): `new-page-migration-dry-run.ps1` emits an "On this page" quick-links section, then one native SPO collapsible section per panel (`plan.SectionSettings`: `Collapsible`, `IsExpanded` = false, `DisplayName` = panel title; no H2 or "Back to top" inside the panel) and sets `PageLayout` Home so the leading banner is not under the stock Article title area. `new-spo-page-publication-dry-run.ps1` copies `SectionSettings` into `Target`; `publish-spo-page.ps1` calls `Add-PnPPageSection -Collapsible -IsExpanded -DisplayName`.
- Accordion panel bodies are ordinary Text web parts inside the collapsible sections, so the same editor formatting rules apply: run `convert-package-to-rte.ps1` (via `sp-text-webpart-html`) on the package so panel text keeps its formatting when edited. The CSV flag `rte_formatting_flag` = `accordion-panels` marks these web parts.
- A hand-built H2 + "Back to top" accordion was rejected on the first DEV publish (not functional, not BC-aligned). Native sections cannot take BC styling (PnP sets only collapsible, title, expanded and a ZoneEmphasis background), so the BC AccordionGroup look is SPFx work (map-debt PAGE-10, App Catalog access).
- A banner `ImageWidth` is published with a proportional `-ImageHeight` read from the uploaded file, so SPO does not stretch it. The user checks whether quick links jump to collapsible sections.

## Operations header band (title banner)

**Every Operations page** uses the redesigned header first built on DEV `Operations/BCSS-Training-Section.aspx`, instead of republishing the SP2016 title banner image (for example "Central Programs / Provincial Programs / Radio Program"). Always pass `-AccordionOutput Spfx -HeaderText ... -HeaderSubtext ... -HeaderLogoUrl ...`, and drop the banner with `-LeadingImageWebPartIds <banner web part id>` (an image-only Content Editor web part; otherwise it stays as a leftover Text web part).

- Source of truth: `docs\analysis\modern-page-playbook.md` (web team). Playbook order: exception mapping, then page-specific playbook, then Main. `BC-Operations-Service-Division.aspx` and `BCSSS.aspx` map to Operations; Operations pages in the `Operations` library use the same Operations playbook. Every converted page (all playbooks): Comments Off and "You may also be interested in" Off.
- Shape: its own first section (`TwoColumnRight`, one-third left / two-thirds right; the playbook calls it One-third-left), strong emphasis (`SectionSettings` Emphasis 3), background `#002d72` (navy), accent `#ffffff`. Left: Image web part with the existing logo `/sites/<SiteName>/PublishingImages/header-footer/bcss-logo-1.png`; never copy it to `SiteAssets` or `SitePages`. Never set a fixed `ImageWidth` or height in the plan; the publisher reads the file's own pixel size (258x150 for `bcss-logo-1.png`) from the target site and sends it, because PnP stores a 150x150 box when no size is sent, which squashes a non-square logo (seen on DEV Shaping-the-Future, 2026-10-23, canvas `imgWidth`/`imgHeight` 150x150 against 258x150 on the hand-built BCSSS). Right: a Text web part with the titles. Body sections follow it.
- Titles (maximum 3, one paragraph each; separate them with Enter, never Shift+Enter or `<br>`): Title 1 and Title 2 are 28px in `#ffffff` (white); Title 3 is 24px in `#f2a900` (gold). Segoe UI (default font). Use editor classes (28px = `fontSizeXxLarge`, 24px = `fontSizeXLargePlus`, gold = `fontColorBrand2` or literal `#f2a900`), not `<h2>`/`<h3>`: the RTE converter turns them into same-size bold headings.
- Open item (planner not yet aligned): `new-page-migration-dry-run.ps1` still emits one `<p>` with `<br>` between rows and the sizes `fontSizeXxLargePlus` / `fontSizeXLarge`. Change it to one `<p>` per title with the playbook sizes, and add a test.
- Owner override (2026-10-22): the division's main page `BC-Operations-Service-Division` uses the original SP2016 banner image `/PublishingImages/Header%20Image/BCSS%20Email_Page%20Header.png` instead of the logo + titles band, in its own one-column first section, at its source width of 1235px (`ImageWidth`), with no band emphasis. Other Operations pages keep the band above.
- Planner switches on `new-page-migration-dry-run.ps1`: `-AccordionOutput Spfx -HeaderText "<line 1>" [-HeaderSubtext "<line 2>","<line 3>"] -HeaderLogoUrl <logo>`. The band is only emitted with `-HeaderText` AND `-AccordionOutput Spfx` (`$hasHeader`); the page-title breadcrumb then moves to the first body section.
- Heading text: one title per line of the source banner image (for example "Central Programs", "Provincial Programs", "Radio Program"), maximum 3. Ask the user when the image text is unclear.
- Editor-native markup was verified on DEV Radio Program, matching the hand-built Training page, with the earlier sizes (line 1 `fontSizeXxLargePlus`, middle rows `fontSizeXLarge`, last row `fontSizeXLarge` + `fontColorBrand2`); the playbook sizes above supersede them once the planner is updated.
- Accordion panels without a `panel-body` wrapper use the `panel-collapse` content (covered by `modern-page-structure.Tests.ps1`).
- Pages without an accordion use the Native output; the band is not available there until the planner drops the Spfx condition (open item).
- The SPFx accordion requires the deployed web part (SPFx hard stop in the skill).

## Administration header band (title banner)

Administration pages use the Administration playbook (web team) instead of republishing the SP2016 title banner. It is simpler than the Operations band: one title, no logo, no accordion dependency.

- Source of truth: `docs\analysis\modern-page-playbook.md`, "Administration Playbook". Playbook order: exception mapping, then page-specific playbook, then Main. `Administration-Administration-Division.aspx` is the listed exception mapped to Administration; apply the same playbook to the other pages in the `Administration` library, as for Operations, and confirm with the owner if a Administration page looks wrong. Every converted page (all playbooks): Comments Off and "You may also be interested in" Off.
- Layout: not a section. The band is the **page title area**: an Article page whose first zone holds the Banner web part, full width, with the theme colour white text on `#65799e` (muted blue). Body sections follow in later zones. (A first draft of this section described a coloured full-width section with an H2 title; the hand-built DEV page shows the title area is used, so that was wrong.)
- Banner web part: Layout Plain (`NoImage`), Alignment Left, Show Published Date On, Show Author Off, `isFullWidth` true, title as an H1 (`fontSizeBannerTitle`).
- Title: **Title 1 only**, the page title; never a Title 2 or Title 3 (the Operations band allows three; Administration allows one). The title is the SP2016 banner or page title wording; ask the user when the banner image text is unclear.
- Differences from Operations: no logo or Image web part, no `TwoColumnRight` section, no gold Title 3, no section emphasis. Do not use `-HeaderText`, `-HeaderSubtext` or `-HeaderLogoUrl` for Administration (the planner refuses the combination).
- Breadcrumb: `Home > Administration > <page title>` as in "Breadcrumb and title" in `SKILL.md` (pass `-BreadcrumbSection "Administration"`). The band shows the title, so the breadcrumb does not repeat it as a heading.
- Drop the SP2016 banner image the same way as Operations (`-LeadingImageWebPartIds <banner web part id>`), only when it is an image-only Content Editor web part.
- How it is built (verified on DEV against the hand-built `Administration/Accessibility-Resources`, 2026-10-23; test `tests\administration-title-banner.Tests.ps1`; map-debt `DEBT-20261023-SPMIG-44`):
  - Planner: `new-page-migration-dry-run.ps1 ... -PageHeaderStyle Administration -PageTitle "<title>" -BreadcrumbSection "Administration"`. It recorders `plan.PageHeader` (Plain, Left, publish date on, author off, `ZoneThemeIndex` 3) and keeps `PageLayout` Article (a Home layout has no title area; accordion pages normally force Home, but not with this switch). `new-spo-page-publication-dry-run.ps1` copies `PageHeader` into `Target`.
  - Publisher: `publish-spo-page.ps1` creates the Article page, publishes it with `Set-PnPPage -HeaderType PageTitleWebPart -HeaderLayoutType NoImage -ShowPublishDate`, then PnP has no parameter for the title zone colour, so it rewrites the saved page: `ConvertTo-SpoCanvasWithTitleBanner` moves the title into a Banner web part in zone 1, shifts the body zones down one, removes the old Title Region from `LayoutWebpartsContent` and adds the zone theme control (`lightIndex`/`darkIndex` 3, keyed by the banner zone id). It uses `Set-PnPListItem -UpdateType SystemUpdate`, so the page stays published with no extra version. The canvas shapes are in `assets\title-banner-canvas.json` (copied from the hand-built page), not in the script; the publisher finds it relative to its own path, so run the publisher from `plugins\sp-migration`.
  - `ZoneThemeIndex` 3 is the value stored on the hand-built page and confirmed by the owner to render white text on `#65799e`. It is an index into the site theme's colour list (`inventory\site-branding-theme.json`, `secondaryColors.light`: entry 2 is white on `#65799e`), so it can shift if the theme's colour list is reordered; re-check after any theme change.
- Not covered yet: pages that need both this banner and the SPFx accordion are built (plan only; not yet tested on DEV); the visual result of the converted page (blue band, white title, Edit mode opens) is adjudicatord by the owner on DEV, not by a script.

## Link policy

Same as the document and static-page skills; see `docs\plans\library-migration-process.md` "Link policy".

- Do not leave `source-tenant.example.com` links pointing at the old server. Rewrite every link and image to its **planned** SPO location, even if that target is not migrated yet, using `inventory\library-path-map.csv` (longest `source_prefix` wins; derived from `inventory\inventory-library.xlsx`).
- Subsites collapse into libraries and their old libraries become folders (`operations-subsite/library` becomes `Operations/library/`); `Pages` become `SitePages/` and `.aspx`/`.htm` links become `.aspx` on Site Pages for modern pages (`.html` only for static pages).
- Write links relative to the page for any target in the same site (for example `../Branch%20Info%20Documents/...` from a `Main` Site Page, so the same package works on DEV, TEST and PROD); never write the `/sites/<site>/` prefix into a plan.
- A mapping row with `status: assumed` is shown to the user. A link with no mapping is never guessed: list it and ask. External `http(s)`/`mailto` links stay.
- Before listing a link as unmapped or asking the user about a file (PDF, doc, image, video), look it up in the library ledgers `inventory\ledgers\<Library>\ledger.csv` (and `next-upload-plan.json` there): search by file name and source path. A `VERIFIED` row means the file is on the target; `upload`/skipped rows mean not migrated yet; no row means not in the inventory. Report what the ledger says for each such link. `file://` and other network-share links never exist in SPO. If the file is not in the ledgers, search the extracts and inventories; if it is an on-prem URL that looks dead, ask the user to check the source page. If it is not found anywhere, remove the link, keep the text and append `(missing link)` in brackets, and list it in the report.
- Show the user the rewrite report (old link, new link, basis) before the package is built. `sp-static-aspx-file-migration/scripts/rewrite_page_links.py` and `sp-document-library-upload` hold the existing implementation to learn from.

## Layout analysis

Part of page analysis, before the plan is built; never assumed. From the source page, list the web part zones and any content tables, and propose the SPO section layout (`OneColumn`, `TwoColumnLeft`, `TwoColumnRight`, `ThreeColumn`, or several sections in order, for example one column header, two column body, one column footer). Modern text web parts cannot render images inside table cells, so a table of photo-plus-text cells becomes columns, with each photo as its own image web part beside its text. Show the user the proposed sections and the placement of every component (section, column, order), and get confirmation before the package is built. The package carries `Target.Sections` (ordered templates), `Target.PageTitle`, and per-component `Section` and `Column`; `publish-spo-page.ps1` honours them. The page title is a separate choice: ask what it should be and whether the source banner image stays in the body, because the SharePoint title area is itself a header.

## Relative path building

A path is resolved against a base, so always state the base and show the result. Case matters for folder names and the site prefix is part of the URL. Worked example, DEV page `Headquarters-Division`: asset upload path `SiteAssets/SitePages/Headquarters-Division/<file>` is web-relative to the site root (`/sites/AG-Portal-WORKSPACE-DEV/`), so the server-relative path is `/sites/AG-Portal-WORKSPACE-DEV/SiteAssets/SitePages/Headquarters-Division/<file>`. A page at `/sites/AG-Portal-WORKSPACE-DEV/SitePages/Headquarters-Division.aspx` resolves a bare `SiteAssets/...` against `/SitePages/`, which is wrong; use `../SiteAssets/...` or the server-relative form. Before publishing, list each image or link as source, base, resolved URL and ask the user to confirm; after publishing, have the user open one image in a new tab and compare the URL. Do not assume a path is correct because the file uploaded. Add new worked examples here as they are learned.

## Design system

Automated by `Set-SpPageBcDesignTokenStyles` in `new-page-migration-dry-run.ps1` (`line-height` is not applied because publication normalization strips it). BC design **tokens** are applied as inline styles in the modern text web part (BC Sans/Noto Sans stack, `#2D2D2D` text, `#255A90` links; no inline heading sizes, so SPO theme heading styles apply). A leading banner image (`-LeadingImageWebPartIds`) keeps its SP2016 width as `ImageWidth`. Tokens come from `standard-design-system` (read-only). A text web part cannot load external CSS, fonts, header/footer or components, so report "BC design tokens applied", never "design-system compliant". Static `.html` pages use `sp-static-aspx-file-migration` instead. Header/footer need a site theme or SPFx; do not do either implicitly.
