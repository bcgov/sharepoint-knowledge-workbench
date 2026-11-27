# Publishing HTML to a SharePoint Site & Fallback Mode

## Contents

- [Publishing HTML to a SharePoint site](#publishing-html-to-a-sharepoint-site)
- [Fallback without the scripts](#fallback-without-the-scripts)

## Publishing HTML to a SharePoint site

SharePoint serves only `.html` pages from **Site Pages**; `style.css`, `images/`, reports and the topics file must live in **Site Assets**. Use the **same folder path in both libraries** for consistency, e.g. `SitePages/Manuals/CEIS` and `SiteAssets/Manuals/CEIS` (with `images/` under it). All links are page-relative (e.g. `../../../SiteAssets/Manuals/CEIS/images/...`), so they work on any host.

Styling: with a shared design system the pages link `colors_and_type.css` and `manuals.css` from it (verified working on the CEIS manual when the page is opened at its own address, `.../SitePages/Manuals/<NAME>/index.html`); without one, the stylesheet is embedded in every page (`<style>`). Note: the library file viewer (`AllPages.aspx?id=...`) does not load linked files; open pages at their own address. `--link-css` links a per-manual `style.css` instead.

1. **Ask the user** (once, all together; `publish` refuses to run without the answers):
   - "Which folder should I use in Site Pages and Site Assets? (e.g. `Manuals/CEIS`)" → `--folder`.
   - "Is the source PDF already on the SharePoint site? If so, its link or path." → `--pdf-path` (a full URL or a site-relative path such as `Manuals/ceis-manual.pdf`; it is linked, not uploaded again) or `--no-site-pdf` (the PDF copy is published to the assets folder).
   - "Is there a shared design system or CSS on the site to reuse (fonts, colours, logo)? If so, its folder." → `--design-system SiteAssets/bc-gov-design-system` or `--no-design-system`. With a shared folder, pages link its `colors_and_type.css` (BC Sans `@font-face` + tokens; `--ds-tokens`) and header logo `icons/bc-logo.png` (`--ds-logo`), and the manual styling is published **once** as `<design-system>/manuals.css`, shared by every manual. Without a shared folder the styles are embedded in each page.
2. **Publish layout**: `python scripts/convert_pdf.py publish <build> --site-root <job>/sp --folder <folder> --pdf-path <path>`. Writes a local mirror (`<sp>/SitePages/<folder>/*.html`, `<sp>/SiteAssets/<folder>/...`), rewrites every `href`/`src`, extracts the shared sidebar menu into `<sp>/SiteAssets/<folder>/toc.js` (single-source menu across all pages; pass `--inline-toc` to keep static per-page `<nav>` instead), optionally injects `--site-home "Label|SitePages/..."` and `--parent "Label|SitePages/..."` links into `.subheader` and `.crumbs`, runs `check_links.py`, and writes `publish-plan.json` (`reference_only` lists the PDF copy kept only for the check, never uploaded). Status must be `PASS`.
3. **Dry-run with `Publish-PdfHtmlSite.ps1`**:
   ```powershell
   pwsh -File scripts/Publish-PdfHtmlSite.ps1 -SiteRoot <job>/sp -ConfigPath <path-to-config.psd1>
   ```
   `Get-WorkbenchConnectionConfig.ps1` resolves `SiteUrl`, `ClientId`, `TenantId`, `TenantAdminUrl`, and `AuthenticationMode` from the `.psd1` (for example `config-spo-dev.psd1`). Pass `-SiteUrl` to override `Connection.SiteUrl`.
4. **Execute live upload & major check-in (human-confirmed)**:
   ```powershell
   pwsh -File scripts/Publish-PdfHtmlSite.ps1 -SiteRoot <job>/sp -ConfigPath <path-to-config.psd1> -Execute -ConfirmToken PUBLISH-PDF-HTML-SITE
   ```
   Add `-Overwrite` when updating an existing published manual (checks out existing files before `Add-PnPFile` and checks them in with `Set-PnPFileCheckedIn -CheckinType MajorCheckIn` so `SitePages` items are `published` and visible to all users). Reuses a single `Connect-PnPOnline` session and writes `<job>/sp/online.json`.
5. **Verify the published files (mandatory)**:
   ```bash
   python scripts/convert_pdf.py verify <job>/sp --online <job>/sp/online.json
   ```
   Confirms every planned file is online at the same byte size and checked in (`published`), and that the linked PDF exists. Ask the user to open `<SiteUrl>/SitePages/<folder>/index.html` in the browser to confirm styling, images, and links.

## Fallback without the scripts

Only HTML output is covered. `scripts/build_html_fallback.py` (with `assets/` and `check_links.py` beside it) does steps 2–8 for a text-layer PDF and writes the same B.C. Design System site:

```bash
python scripts/build_html_fallback.py <in.pdf> <out_folder> "<title>" [first_content_page] \
  [--org "Branch"] [--doc-date "September 2026"] [--intro "Cover paragraph"] \
  [--img-alt "Image from PDF page {page}"] [--footer-cut 750]
```

Runs `check_links.py`, writes `validation.json`, and exits 2 on `FAIL`. Uses `pdfplumber`, `pypdf`, and `pdftoppm`. Rules:
1. Inspect `char['fontname']` and `size` on a few pages first (default heuristics: bold 16 pt = chapter, bold 14 pt = section, 12 pt = body). Skip front matter via `first_content_page`.
2. Drop running footers with `top > 750` (adjust `--footer-cut` to page height).
3. Merge consecutive heading-only topics and keep recurring headings like "Overview" as `<h2>` inside the topic page.
4. Rasterize embedded images >= 40 pt via `pdftoppm` (avoid `pdfimages` soft masks); exclude lines inside `page.find_tables()` boxes from body text.
5. Copy the source PDF beside the pages so `#page=N` links work; note that fallback omits `manifest.json`, `topics.xlsx`, Markdown, and `chunks.jsonl`.
