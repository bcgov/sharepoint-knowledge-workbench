# BC Design System for migrated SharePoint pages

How `sp-migration` applies the B.C. Government Design System, and which installed skills own which part. Read before changing page styling in a skill or script.

## Contents

- [Installed design-system skills](#installed-design-system-skills)
- [Token source of truth](#token-source-of-truth)
- [Which approach per page type](#which-approach-per-page-type)
- [Modern-page token styling (dynamic pages)](#modern-page-token-styling-dynamic-pages)
- [Honest limits](#honest-limits)
- [Verification](#verification)
- [Sources](#sources)

## Installed design-system skills

| Skill (`.agents/skills/`) | Owns | Use here |
|---|---|---|
| `standard-design-system` | Tokens (that skill's REFERENCE.md), canonical CSS (its colors_and_type.css), BC Sans fonts, logo, WCAG acceptance criteria | Read-only token and asset source for every page |
| `design-system-react` | `@bcgov/design-system-react-components` guidance | Only for SPFx React web parts; not for static HTML or text web parts |
| `sharepoint-publish-html-page` | Dry-run-first publication of standalone `.html` pages | Upload step for static pages |
| `sharepoint-convert-legacy-aspx-to-html` | Legacy ASPX to HTML conversion | Reference for the static route |
| `sharepoint-scaffold-spfx-*`, `sharepoint-package-spfx-solution`, `sharepoint-deploy-spfx-solution` | SPFx web parts | Only if a page needs real components (header/footer/menu) |

Plugin skills that consume them: `sp-static-aspx-file-migration` (full chrome, shared CSS/fonts, validator) and `sp-dynamic-aspx-page-migration` (token-styled inline HTML only).

Rule: never patch `.agents/` copies. Upstream owns tokens; this plugin only references them.

## Token source of truth

- Tokens are semantic key-value aliases named `System.Usage.Property.Modifier.Component.Variant` (for example `surface.color.primary.button.default` = `#013366`). They cover colour, typography, elevation, sizing and spacing.
- The component library is Figma + React. Other front ends re-implement components from tokens.
- Use the values in the `standard-design-system` skill's colors_and_type.css; do not retype values from memory.

Tokens applied to dynamic pages (from that file):

| Purpose | Token | Value |
|---|---|---|
| Font stack | `--font-primary` | `'BC Sans','Noto Sans',sans-serif` (fall back if BC Sans is not loaded) |
| Body text | `--color-text-primary` | `#2D2D2D` |
| Secondary text | `--color-text-secondary` | `#474543` |
| Link | `--color-text-link` | `#255A90` |
| Brand / heading accent | `--color-brand-primary` | `#013366` |
| Focus ring | `--color-brand-focus` | `#2E5DD7` |
| Border | `--color-border` | `#D8D8D8` |
| Surface | `--color-surface-default` | `#FAF9F8` |
| Body size / line height | `--text-body` / `--lh-body` | 16px / 27px |
| Headings h1-h6 | `--text-h1`..`--text-h6` | 36, 32, 28, 24, 20, 18px; line height 1.1; weight 700 |

## Which approach per page type

| Page type | Route | Design-system handling |
|---|---|---|
| Static `.aspx` renamed `.html` (Option 2 default) | `sp-static-aspx-file-migration` | Full: that skill's bc-design-system-page-chrome.md and shared-design-system-assets.md references, `validate_design_system_page.py` |
| Dynamic page to modern SitePage | `sp-dynamic-aspx-page-migration` | Token-styled inline HTML inside the text web part (below) |

## Modern-page token styling (dynamic pages)

A modern text web part sanitises HTML: no `<link>`, no `<style>` blocks that persist, no custom fonts. So:

1. Apply token values as inline `style` attributes on the migrated body HTML (font stack, `#2D2D2D` text, `#255A90` links, heading sizes/weights, 16/27 body).
2. Run this after legacy font stripping and layout-style removal, so legacy `font-family`/`font-size` do not fight the tokens.
3. Keep the transform idempotent: a second run must not change the output.
4. Do not touch alt text, link targets, tables' structure or image placement.

## Honest limits

- This is token styling, not full design-system compliance. Do not report a page as "design-system compliant"; report "BC design tokens applied".
- BC Sans renders only where it is installed or loaded; otherwise `Noto Sans`/`sans-serif` shows.
- Header, footer, Indigenous acknowledgment and components are not available in a text web part. Options if the user wants them: an SPO site theme (tenant/site admin decision), or an SPFx application customizer/web part (separate project, `sharepoint-*-spfx-*` skills). Neither is done implicitly.

## Verification

- Plan/package HTML contains the token font stack and colours; headings use token sizes.
- Re-running normalization yields identical HTML (idempotency test).
- Accessibility: link colour `#255A90` on white and text `#2D2D2D` meet WCAG 2.1 AA contrast; keep native heading order and alt text.
- Human review of the rendered DEV page before any inventory update.

## Sources

- B.C. Design System: [design tokens](https://www2.example.com/gov/content/digital/design-system/foundations/design-tokens), [components](https://www2.example.com/gov/content/digital/design-system/components)
- `standard-design-system` skill: REFERENCE.md and colors_and_type.css
