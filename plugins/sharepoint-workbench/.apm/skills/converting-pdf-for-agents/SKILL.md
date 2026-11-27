---
name: converting-pdf-for-agents
plugin: sharepoint-workbench
description: Converts a text-layer PDF, or a folder of PDFs, into either agent-optimized Markdown (front matter, stable headings, one topic per page, linked index, tables and images kept, chunks.jsonl) or a static HTML5 site styled to the B.C. Design System (navigation, styled tables, figures, BC Sans typography, WCAG 2.1 AA), with dry-run-first PnP PowerShell publication to SharePoint Online (SitePages + SiteAssets) using workbench .psd1 connection configs. Asks which output format is wanted unless the user already said (e.g. "convert to html"). Topics come from PDF bookmarks or heading sizes, or are proposed by the agent and confirmed by the user. Use when the user wants to convert, split, restructure or prepare a PDF for agents, knowledge bases or reading as static HTML or Markdown, or publish a converted PDF HTML site to SharePoint Online. Not for scanned PDFs needing OCR.
---

# Converting PDF for Agents

Turns a text-layer PDF into topic pages plus an index, in **agent-optimized Markdown** (`--format agent-md`) or **B.C. Design System static HTML5** (`--format html`), with dry-run-first **PnP PowerShell** publication to SharePoint Online (`SitePages` + `SiteAssets`) using `.psd1` connection configs.

## Contents

- [Constraints](#constraints) • [Quick start](#quick-start) • [Workflow](#workflow) • [Scripts](#scripts) • [Verification](#verification) • [References](#references)

## Constraints

- Text-layer PDFs only; pages without text are reported, never guessed (no default OCR).
- Know the output format first: ask `(a) agent-md` vs `(b) html` unless already specified.
- Page text is copied unchanged; AI only proposes topic boundaries/titles for weak PDFs, and `build` waits for confirmation unless `structure` is `strong` on a fast-path request.
- Write job artifacts only under the caller's working folder (`temp/<job>/` or `working/<job>/`), never inside the skill folder.
- Tenant writes are dry-run by default: `scripts/Publish-PdfHtmlSite.ps1` performs zero tenant I/O without `-Execute -ConfirmToken PUBLISH-PDF-HTML-SITE`.

## Quick start

```bash
python scripts/convert_pdf.py check
python scripts/convert_pdf.py plan  <in>/Doc.pdf --work <job>/work
python scripts/convert_pdf.py build <in>/Doc.pdf --topics <job>/work/topics.xlsx --out <job>/out --title "Doc" --format html   # or: agent-md
python scripts/convert_pdf.py publish <job>/out/<doc> --site-root <job>/sp --folder Manuals/CEIS --pdf-path Manuals/ceis-manual.pdf --no-design-system
```

```powershell
# Dry-run SharePoint publication (resolves SiteUrl/ClientId/TenantId from .psd1):
pwsh -File scripts/Publish-PdfHtmlSite.ps1 -SiteRoot <job>/sp -ConfigPath <path-to-config.psd1>
# Live upload + major check-in + online.json capture (human-confirmed):
pwsh -File scripts/Publish-PdfHtmlSite.ps1 -SiteRoot <job>/sp -ConfigPath <path-to-config.psd1> -Overwrite -Execute -ConfirmToken PUBLISH-PDF-HTML-SITE
# Verify live files & published levels:
python scripts/convert_pdf.py verify <job>/sp --online <job>/sp/online.json
```

## Workflow

1. **Choose format & inputs**: confirm `agent-md` or `html`, source PDF(s), and destination (local folder or SharePoint site via `.psd1` config / `-SiteUrl`).
2. **Check & Plan**: run `convert_pdf.py check`, then `plan`. For `strong` structure (`outline`/`font`), topics are auto-extracted; for `weak` structure, propose topics from `pages-digest.md` per [conversion-rules.md](references/conversion-rules.md).
3. **Confirm & Build**: confirm `topics.xlsx` (or fast-path when `strong`), then run `build --format <chosen>`. Every build runs `scripts/check_links.py` and writes `validation.json`.
4. **Publish HTML to SharePoint (optional)**: run `convert_pdf.py publish` to split `SitePages/<folder>/*.html` and `SiteAssets/<folder>/*` into a local mirror + `publish-plan.json`, run `Publish-PdfHtmlSite.ps1` dry-run first, execute with `-Execute -ConfirmToken PUBLISH-PDF-HTML-SITE`, and verify with `convert_pdf.py verify <sp> --online <sp>/online.json`.

## Scripts

| Script | Purpose |
|---|---|
| `scripts/convert_pdf.py` | `check`, `plan`, `build`, `publish`, `verify` CLI |
| `scripts/render_outputs.py` | Deterministic `agent-md` (`chunks.jsonl`) and B.C. Design System `html` writers |
| `scripts/check_links.py` | Mandatory link, `#anchor`, `<pdf>#page=N`, and heading-level validator |
| `scripts/Publish-PdfHtmlSite.ps1` | PnP.PowerShell publisher for `publish-plan.json` using `.psd1` config (`-ConfigPath` / `-SiteUrl`) |
| `scripts/Get-WorkbenchConnectionConfig.ps1` | Shared `.psd1` connection config resolver |
| `scripts/build_html_fallback.py` | Standalone HTML-only fallback (`pdfplumber` + `pdftoppm`) |
| `scripts/selftest.py` | End-to-end deterministic self-test (`98` checks) |

## Verification

- Run `python scripts/selftest.py` (all checks must PASS).
- Run `python scripts/check_links.py <output_folder>` on any built or moved output.
- After SharePoint upload, run `convert_pdf.py verify <sp> --online <sp>/online.json` (`status: PASS`) and ask the user to open `<SiteUrl>/SitePages/<folder>/index.html`.

## References

- [conversion-rules.md](references/conversion-rules.md): `topics.xlsx` schema, weak-PDF topic rules, image extraction, limits.
- [output-formats-and-design.md](references/output-formats-and-design.md): `agent-md` / `html` layouts, B.C. Design System v5.1.0 tokens, WCAG 2.1 AA, link check rules.
- [sharepoint-publishing.md](references/sharepoint-publishing.md): `SitePages` / `SiteAssets` split, shared `--design-system` CSS, `Publish-PdfHtmlSite.ps1`, fallback mode.
