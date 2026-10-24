# Text web part HTML: what the editor keeps (and the PnP HtmlTransformator)

Status: experiment in progress. Update the "Experiment log" as results come in.

## Problem

The publisher stores our HTML verbatim in the page's Text web part. View mode shows it as stored. When a person opens the part in edit mode, the rich text editor (CKEditor 5) reloads it and keeps only what its toolbar can produce. The next save writes the cleaned HTML back. Observed on the Operations Policy Manual DEV page: styled `<div>` wrappers, `background-color`, `border`, `padding`, `font-family` and `color` were all dropped; only `<p>`, `<strong>`, `<i>`, `<u>`, `<a>`, `<h2>` and `text-align` on `<p>` survived. No tenant setting turns this off (unverified beyond community and Microsoft guidance).

Consequence: BC design tokens expressed as inline CSS cannot live in an editable Text web part. Text parts cannot use CSS variables either.

## PnP.Framework `HtmlTransformator`

Source: `PnP.Framework.Modernization.Transform.HtmlTransformator` (loaded with `Import-Module PnP.PowerShell`; verified with PnP.PowerShell 3.2.0).

```powershell
$t = [PnP.Framework.Modernization.Transform.HtmlTransformator]::new($null)
$clean = $t.Transform($html, $false)
```

Verified behaviour (offline probes):

| Input | Output |
|---|---|
| inline `style` | removed, except `text-align` / `margin-left` on blocks and `width` |
| `<h1>`..`<h3>` | shifted to `<h2>`..`<h4>` (the page title owns h1) |
| `<h4>` and below | `<div>` (heading lost) |
| `<p>` | wrapped in `<span>` |
| `ms-rteForeColor-N` / `ms-rteBackColor-N` / `ms-rteFontSize-N` | `fontColor<Name>`, `highlightColor<Name>`, `fontSize<N>` (fixed palette; no arbitrary hex) |
| `<table class="ms-rteTable-default">` | wrapped in `canvasRteResponsiveTable`, class `borderHeaderTableStyleNeutral` |
| `<table class="ms-rteTable-4">` | class `filledHeaderTableStyleTheme` |
| `<blockquote>` | kept |
| styled `<div>` boxes | wrapper kept, styles dropped |

Limits: it targets classic wiki `ms-rte*` markup and predates CKEditor 5, so newer toolbar features (custom colours, line and paragraph spacing) are not produced. Exact BC hex colours cannot be expressed.

## BC element mapping (best effort)

Script: `plugins/sp-migration/scripts/publication/convert-package-to-rte.ps1` (tests: `tests/convert-package-to-rte.Tests.ps1`). Reads a package, writes a new package; never edits the input.

| Our markup | Editor-native result |
|---|---|
| Warning alert (`#fef1d8` / `#f8bb47`) | one-cell full-width figure table, cell `background-color:#fef1d8`, 6px `#f8bb47` left bar, bold title line (superseded the two-row theme table) |
| Callout (`#faf9f8`, `#013366` left bar) | one-cell full-width figure table, cell fill and 6px navy left bar |
| BC text colour | kept as `span` `color`; font-family dropped (theme font applies) |
| links, bold, italic, `text-align` | kept |

Colours are literal hex values, not BC tokens, so report "approximated with editor tables", not "BC design tokens applied". The box shapes are captured editor forms; the 6px bar and the alert border are approximations of the BC style.

Alternatives if the table approximation is not acceptable: a non-editor web part (Markdown or SPFx) for the boxes, or a plain text part with styled boxes as separate parts.

## Round-trip test (the only reliable check)

1. Publish the transformed package (user runs it).
2. Open the part in edit mode, change a word, save.
3. Re-export with `scripts/migration/export-modern-page.ps1` (DEV only; prompts for sign-in) and diff the stored HTML against what was published.
4. Anything missing from the stored HTML is outside the allow-list.

The best source of truth for the tenant's allow-list is a part built by hand with the toolbar (table, quote, highlight, font colour) and read back with `Get-PnPPageComponent`.

## Experiment log

- Baseline (styled divs, no transform): formatting stripped on edit (see Problem).
- Transformed package `package-rte.json` (theme table classes only): formatting survived edit, but the BC colours did not appear and boxes rendered about 550px wide.
- Capture page `RTE-Capture` (2026-10-21, DEV): published a matrix of markup, edited and saved it in the editor, then read it back with `Get-PnPPage`. Findings:
  - **Inline colour is kept.** `span` `color` and `background-color` survive. `th`/`td` `background-color`, `color` and `border-left:6px solid …` survive (stored as `rgb(...)`). The earlier "inline styles are stripped" belief was wrong for these properties.
  - **Lost or rewritten:** `font-family` is dropped; `font-size:24px` becomes the class `fontSizeXLargePlus`; `<hr>` is dropped; the `ms-rteTable-*` classes collapse to `simpleTableStyleNeutral` (only `filledHeaderTableStyleTheme` and `borderHeaderTableStyleTheme` survive); `table width`/`style` attributes are ignored.
  - **Full width** comes from the editor's own wrapper `<figure class="table …"><table class="… customCells ck-table-resized"><colgroup><col style="width:100%;">`, not from a table width attribute.
  - Kept as-is: `p` `line-height`, `p` `margin-bottom` (plus `spacingBelow`), `blockquote`, `ol`/`ul` (gain `customListStyle`), `a target="_blank"` (gains `data-interception="off" rel="noopener noreferrer"`), `u s sup sub code pre`.
  - The editor's toolbar offers a custom hex colour picker, highlight colours, table cell fill, and border weight/style/colour.
- Decision: `convert-package-to-rte.ps1` now emits the BC alert (`#fef1d8`, `#f8bb47` bar) and callout (`#faf9f8`, `#013366` bar) as that figure/table form with cell `background-color`, `border-left` and `color`, hidden from `HtmlTransformator` with placeholders. Publishing and the post-edit check of the Operations page are pending.
- Not yet captured: a full `border` on a cell, `border-radius`, text colour inside a cell after edit, and whether links keep `#255A90` (link styles are dropped; the theme link colour applies).
- Open: stray `??` after "training materials." in the stored Operations text (encoding on our side).

