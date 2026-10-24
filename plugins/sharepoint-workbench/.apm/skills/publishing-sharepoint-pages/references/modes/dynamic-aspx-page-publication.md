# Mode: Dynamic ASPX Page Publication & Migration

Feature-parity implementation for migrating and publishing a SharePoint classic dynamic ASPX page to a modern SharePoint Online page canvas.

## Overview

Coordinates the transformation and publication of a classic SharePoint ASPX page (containing web parts like Content Editor, Script Editor, List View, Accordion, etc.) into a modern SharePoint Online client-side page (`SitePages/*.aspx`).

## Constraints

- **No Raw ASPX Upload**: Never upload raw classic `.aspx` files to `SitePages`. Pages must be translated into modern canvas sections, columns, and modern client-side web parts.
- **Source Read-Only**: Source environment configuration must be read-only (`Source.ReadOnly = $true`).
- **Interactive Dry-Run First**: Publication is dry-run by default. Tenant writes require `-Execute` and explicit confirmation token `PUBLISH-SPO-PAGE`.
- **RTE Sanitization**: All rich text content in Content Editor web parts must be linted and sanitized against the modern CKEditor 5 allowlist (`assets/rte-vocabulary.json`) using `scripts/sp_text_webpart_html.py` and converted with `scripts/convert-package-to-rte.ps1`.
- **SPA Link Routing**: Modern SharePoint pages run as a Single Page Application (SPA). Relative links (`../../<Library>/...`) must be resolved to server-relative paths (`/sites/<SiteName>/...`), and external or document URLs (`.pdf`, `.docx`, `.xlsx`) must include `target="_blank"`.

## Workflow

1. **Intake & Scope**:
   Identify source page URL, source config, target SPO config, and destination site URL.
2. **Extract Web Parts & Images**:
   ```powershell
   pwsh -File scripts/batch-extract-webpart-content.ps1 -ConfigPath <source-config.psd1> -PageUrl <source-page-url> -OutputDir temp/extract
   pwsh -File scripts/extract-page-images.ps1 -ConfigPath <source-config.psd1> -PageUrl <source-page-url> -OutputDir temp/images
   ```
3. **Map Web Parts & Layout**:
   Map source web parts to modern equivalents (`Text`, `Banner`, `QuickLinks`, `HighlightedContent`, etc.) according to `assets/title-banner-canvas.json` and section layout rules.
4. **Sanitize Text to RTE Editor Markup**:
   ```powershell
   pwsh -File scripts/convert-package-to-rte.ps1 -PackagePath temp/extract/package.json -OutputPath temp/extract/package-rte.json
   ```
5. **Dry-Run Page Publication**:
   ```powershell
   pwsh -File scripts/new-page-migration-dry-run.ps1 -ConfigPath <target-config.psd1> -PackagePath temp/extract/package-rte.json
   ```
6. **Publish Modern Page (Human Gate)**:
   ```powershell
   pwsh -File scripts/publish-spo-page.ps1 -ConfigPath <target-config.psd1> -PackagePath temp/extract/package-rte.json -Execute -ConfirmToken PUBLISH-SPO-PAGE
   ```
7. **Verification**:
   Compare live extract versus modern published page (web parts, images, links, tables) and generate an evidence verification table.
