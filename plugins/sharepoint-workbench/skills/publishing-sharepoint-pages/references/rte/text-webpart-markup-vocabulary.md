# Text web part markup vocabulary

## Contents

Evidence levels | Block structure | Alignment and indent | Character formatting | Lists | Tables | Inline images | Wrappers PnP adds

Evidence levels:
- **Confirmed-CK5** — seen in stored HTML of a CK5 page (contentVersion 5) in a real tenant capture
  (PnP Core SDK test recordings) or a public CK5 bug report with stored HTML.
- **Stored** — seen in real stored page HTML, but on a CK4 page or one whose editor version is not
  recorded. Very likely still valid; confirm with one round-trip test.
- **Transformer** — emitted by PnP Framework `HtmlTransformator` (wiki → modern, CK4-era design).
  Generally still renders and survives; confirm with a round-trip test before bulk use.
- **Capture** — feature exists in the toolbar but the stored markup is not publicly documented.
  Capture it from your tenant ([text-webpart-capture-and-verify](text-webpart-capture-and-verify.md)) and add it to [assets/rte-vocabulary.json](../assets/rte-vocabulary.json).

All content lives inside the text part's `<div data-sp-rte="">…</div>`. When using
`Add-PnPPageTextPart -Text`, pass only the inner HTML; PnP adds the wrappers.

## Block structure
| Intent | Markup | Evidence |
|---|---|---|
| Paragraph | `<p>…</p>` | Confirmed-CK5 |
| Paragraph, "Normal text with spacing" | `<p class="noSpacingAbove spacingBelow" data-text-type="withSpacing">…</p>` | Confirmed-CK5 |
| Paragraph without spacing / other spacing combos | likely other `spacing*`/`noSpacing*` classes + `data-text-type` | Capture |
| Headings | `<h2>`, `<h3>`, `<h4>` only (RTE does not use `h1`, `h5`, `h6`) | Stored (CK4 page) + Transformer |
| UI "Heading 1/2/3" ↔ stored tag | believed `h2/h3/h4`; confirm once | Capture |
| Quote (classic) | `<blockquote>…</blockquote>` | Stored (CK4 page) |
| New quote styles (MC888883) | unknown classes | Capture |
| Monospaced | `<pre>…</pre>` | Stored (CK4 page) |
| Horizontal rule | not supported; transformer replaces `<hr>` with `<span><br><br></span>` | Transformer |

## Alignment and indent
| Intent | Markup | Evidence |
|---|---|---|
| Align | `style="text-align:center"` (left/right/justify) on `p`/`h*`/`td` | Transformer (kept by CleanStyles) |
| Indent level n | `style="margin-left:{40*n}px"` on a block element | Transformer |
| Line spacing (custom) | unknown | Capture |

`text-align` and `margin-left` on blocks, and `width`/`text-align` on inline elements, are the
**only** style properties the transformer keeps. Treat any other `style` property as stripped
unless captured from the tenant.

## Character formatting
| Intent | Markup | Evidence |
|---|---|---|
| Bold / italic | `<strong>` / `<em>` | Stored / Transformer |
| Underline / strike | `<u>` / `<s>` (never `text-decoration` CSS) | Transformer |
| Super / subscript | `<sup>` / `<sub>` | Transformer |
| Link | `<a href="…">…</a>` (stored links often carry `data-interception="off"`) | Transformer / public sample |
| Formatting on non-span elements | wrap: `<span class="fontColorRed"><strong>x</strong></span>` | Stored (PnP Core test, editor version not recorded) |

### Font size classes (on `<span>`)
| Class | Classic wiki size it replaces | Evidence |
|---|---|---|
| `fontSizeSmall` | 8pt | Transformer |
| `fontSizeMedium` | 10pt | Transformer |
| `fontSizeMediumPlus` | 12pt | Transformer |
| *(no class)* | 18pt → default size | Transformer |
| `fontSizeXLargePlus` | — | Stored (edit round trip not shown) |
| `fontSizeXxLarge` | 24pt | Transformer |
| `fontSizeXxxLarge` | 36pt | Transformer |
| `fontSizeXxLargePlus` | 48pt | Transformer |
| `fontSizeSuper` | 72pt | Transformer |
| Custom typed size 8–250 | unknown (may be inline `font-size`) | Capture |

### Font color classes (on `<span>`)
Standard (Transformer): `fontColorRedDark`, `fontColorRed`, `fontColorYellow`,
`fontColorYellowLight`, `fontColorGreenLight`, `fontColorGreen`, `fontColorBlueLight`,
`fontColorBlue`, `fontColorBlueDark`, `fontColorPurple`.
`fontColorRed` is Stored.

Theme (Transformer): `fontColorThemeSecondary`, `fontColorThemePrimary`,
`fontColorThemeDarkAlt`, `fontColorThemeDark`, `fontColorThemeDarker`.
Default text color (Neutral Primary) = no class.

Custom hex color (MC888883): unknown, possibly inline `color` → **Capture**.

### Highlight classes (on `<span>`)
Transformer: `highlightColorMaroon`, `highlightColorRed`, `highlightColorYellow`,
`highlightColorGreen`, `highlightColorAqua`, `highlightColorBlue`, `highlightColorDarkBlue`,
`highlightColorPurple`.

## Lists
`<ul><li>…</li></ul>` — Stored (CK4 page); `<ol><li>…</li></ol>` — Transformer.
Bullet styles (disc/circle/square), numbering styles (1/A/a/I/i) and "start at N" — **Capture**
(CK5 typically uses `list-style-type` and the `start` attribute, but do not assume).

## Tables
CK5 stored form (observed after CK4→CK5 conversion, sp-dev-docs #9160):
```html
<figure class="table tableLeftAlign canvasRteResponsiveTable">
  <table class="ck-table-resized {styleClass}">
    <colgroup><col style="width:50%;"><col style="width:50%;"></colgroup>
    <tbody><tr><td>…</td><td>…</td></tr></tbody>
  </table>
</figure>
```
CK4 / transformer form (still accepted and upgraded on edit, but upgrade has had width bugs):
```html
<div class="canvasRteResponsiveTable">
  <div class="tableLeftAlign tableWrapper">
    <table class="{styleClass}" title="Table"><tbody>
      <tr><td style="width:400px;"><strong>Header</strong></td>…</tr>
      <tr><td style="width:400px;">cell</td>…</tr>
    </tbody></table>
  </div>
</div>
```
- Alignment classes: `tableLeftAlign`, `tableCenterAlign`, `tableRightAlign`.
- Style classes (Transformer): `simpleTableStyleNeutral`, `borderHeaderTableStyleNeutral`,
  `filledHeaderTableStyleNeutral`, `bandedRowTableStyleNeutral`, `filledHeaderTableStyleTheme`,
  `bandedRowTableStyleTheme`. Map to UI names (Plain / Subtle header / Header /
  Alternating rows / Column header × neutral/theme) with a capture; Column-header style class
  is **Capture**.
- Header row: transformer emits a normal first row with `<strong>` in `td` (no `th`).
- No `colspan`/`rowspan`, no nested tables.
- Prefer generating the CK5 `figure` form for new content once a capture confirms it in your tenant.

## Inline images (CK5)
Single block element, no CK4 widget wrappers (Confirmed-CK5):
```html
<div class="imagePlugin" style="background-color:transparent;position:relative;"
     data-alignment="Center" data-imageurl="/sites/x/SiteAssets/pic.png"
     data-uploading="0" data-width="600" data-height="400"
     data-imagenaturalwidth="600" data-imagenaturalheight="400"
     data-widthpercentage="100"
     data-siteid="…" data-webid="…" data-listid="…" data-uniqueid="…"
     data-alttext="Alt text" data-captiontext="" data-isoverlaytextenabled="false"
     data-linkurl=""></div>
```
Do not hand-build the GUID attributes — generate with PnP Core `page.GetInlineImage(...)`
(or `Add-PnPPageTextPart -ImageUrl`). Pixel widths: omit `data-widthpercentage`. A raw `<img>`
displays but is removed on edit.

## Captured from the tenant (evidence tag: Captured, 2026-10-21)
- Table: `<figure class="table tableCenterAlign canvasRteResponsiveTable" title="Table"><table class="simpleTableStyleNeutral customCells ck-table-resized"><colgroup><col style="width:100%;"></colgroup>…` (full width).
- Cell shading and bar: `<td class="lightBackground" style="background-color:rgb(250, 249, 248);border-left:6px solid rgb(1, 51, 102);">`; header cells are `<thead><tr><th class="lightBackground" style="background-color:#fbff00;" scope="col">`.
- Text: `<span style="color:#013366;">`, `<span style="background-color:#fef1d8;">`; `font-size` becomes `fontSizeXLargePlus`-style classes; `font-family` and `<hr>` are dropped.
- Spacing: `<p style="line-height:2;">`, `<p class="spacingBelow" style="margin-bottom:24px;" data-text-type="withSpacing">`; lists gain `class="customListStyle"` and `data-list-item-id`.
- These are also in `rte-vocabulary.json` under `tenant`.

## Wrappers PnP adds (do not include in -Text)
`<div data-sp-canvascontrol="" data-sp-canvasdataversion="1.0" data-sp-controldata="{…}">`
`<div data-sp-rte="">…</div></div>` — identical for CK4 and CK5 pages (pnpcore discussion #1599).
