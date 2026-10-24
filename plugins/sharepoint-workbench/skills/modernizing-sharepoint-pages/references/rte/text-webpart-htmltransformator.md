# PnP Framework `HtmlTransformator`

`PnP.Framework.Modernization.Transform.HtmlTransformator` — "transforms the received Html in
html that can be displayed and maintained in the modern client side text part". Built for
classic wiki / publishing HTML (`ms-rte*` classes). Source:
https://github.com/pnp/pnpframework/blob/dev/src/lib/PnP.Framework/Modernization/Transform/HtmlTransformator.cs
(facts below read from the `dev` branch on 2026-10-21).

## Calling it from PowerShell
PnP.PowerShell loads PnP.Framework, so the class is reachable after import (verified: PnP.PowerShell 3.2.0, 2026-10-21):
```powershell
Import-Module PnP.PowerShell
$t = [PnP.Framework.Modernization.Transform.HtmlTransformator]::new($null)
$clean = $t.Transform($html, $false)   # $true = add "***Image placeholder…***" paragraphs
```

## Pipeline (in order)
1. Removes zero-width spaces.
2. Headings: `h1→h2`, `h2→h3`, `h3→h4`; `h4/h5/h6` → `<div>` (plain text). Keeps `text-align`.
3. Blockquotes used for indentation (`margin:0px 0px 0px 40px`) → blocks with
   `margin-left:{40*level}px`; strike/underline on them → `<s>`/`<u>` wrappers.
4. On `span, sup, sub, strong, em, p`:
   - `ms-rteStyle-*` → combinations of italic (`em`), underline, and colors
     (Emphasis/Accent1 → fontColor index 8, Accent2 → 9).
   - `ms-rteThemeForeColor-x-N` → `fontColorTheme*` (see vocabulary; N=0 → default).
   - `ms-rteThemeBackColor-*` → dropped.
   - `ms-rteForeColor-N` (1–10) → `fontColor{RedDark,Red,Yellow,YellowLight,GreenLight,Green,BlueLight,Blue,BlueDark,Purple}`.
   - `ms-rteBackColor-N` (1–10) → `highlightColor{Maroon,Red,Yellow,Yellow,Green,Green,Aqua,Blue,DarkBlue,Purple}`.
   - `ms-rteFontSize-N` (1–8) → `fontSize{Small,Medium,MediumPlus,(default),XxLarge,XxxLarge,XxLargePlus,Super}`.
   - `ms-rteFontFace-*` → dropped (no font families in modern).
   - CSS `text-decoration: line-through|underline` → `<s>` / `<u>`.
   - A `span` left with no class and no child elements is unwrapped to text.
   - Non-span elements that carry a class are wrapped: `<span class="…"><strong>…</strong></span>`.
5. Images/iframes: if `usePlaceHolder` is true, a `<p>***Image placeholder for source …***</p>`
   is inserted before each (the element itself is not converted by this class).
6. Tables → CK4 responsive wrapper (`div.canvasRteResponsiveTable > div.tableLeftAlign.tableWrapper >
   table.{style}[title=Table]`), `th` header → first row of `td><strong>`, colspan/rowspan expanded
   into empty cells, cell widths = 800px split evenly, nested tables dropped.
   `ms-rteTable-N` → `simpleTableStyleNeutral` (0,3), `bandedRowTableStyleNeutral` (1),
   `filledHeaderTableStyleNeutral` (2), `bandedRowTableStyleTheme` (6),
   `filledHeaderTableStyleTheme` (4,5,7–10), else `borderHeaderTableStyleNeutral`.
7. `CleanStyles`: on block elements keep only `margin-left`, `text-align`; on inline elements keep
   only `width`, `text-align`. Every other style property is deleted.
8. `CleanHtmlNodes`: `<hr>` → `<span><br><br></span>`. Nothing else is removed.

## What this means for hand-written HTML
- Inline `color:#…`, `background`, `font-size`, `font-family`, `line-height`, `padding`,
  `border`… are **deleted**, not translated. Map them to classes yourself first.
- It does **not** remove unsupported tags (`div`, `font`, `section`, custom classes on `div`…).
  Run `scripts/sp_text_webpart_html.py check` on the output.
- Output tables are CK4-shaped; CK5 converts them on first edit (historically with width bugs,
  sp-dev-docs #9160). For new content prefer the CK5 `figure` form once captured.
- Headings shift down one level (`h1` becomes `h2`). If your source already uses `h2` for
  "Heading 1", map headings yourself instead of transforming.

## Inline images in the full modernization pipeline (new)
On 2026-10-20/21 (pnp/pnpframework#1294, merged to `dev`) the page-transformation pipeline gained
an internal `InlineImageTransformator`: images are preserved through `HtmlTransformator` and
converted to native CK5 `div.imagePlugin` inline images (CK5 target pages only; CK4 targets
throw). It is `internal`, only runs inside page transformation, and may not be in the
released PnP.PowerShell yet. Outside that pipeline, generate image markup with PnP Core
`GetInlineImage` / `Add-PnPPageTextPart -ImageUrl`. PnP's own guidance for this change: validate
by opening the page in the CK5 editor and saving again, not by checking initial rendering.

## Probe results (PnP.PowerShell 3.2.0, `Transform($html, $false)`, run 2026-10-21)
| Input | Output |
|---|---|
| `<th>H</th>` | `<td style="width: 800px"><strong>H</strong></td>` (never `th`) |
| `ms-rteTable-4` / `ms-rteTable-default` | `filledHeaderTableStyleTheme` / `borderHeaderTableStyleNeutral` |
| `<p style="color:red">x</p>` | `<span><p>x</p></span>` (style dropped, `p` wrapped in `span`) |
| `<div data-sp-bc-tokens style="...">` | div kept, style dropped, inner `p` wrapped in `span` |
| `ul`, `ol`, `a`, `br`, `blockquote` | unchanged |
| `h2` | `h3` |
| `hr` | `<span><br><br></span>` |

The linter flags a `div` wrapper with `data-sp-bc-tokens`: a `div` is allowed only as a table or
image wrapper. Our BC alert and callout are therefore approximated with editor tables.