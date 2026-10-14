# Navigation Menu Pattern

A site-wide mega-menu driven by the site's own Quick Launch, so editors keep managing links as navigation nodes and the extension only renders them.

## Contents

- [Data source](#data-source)
- [Rendering rules](#rendering-rules)
- [Accessibility](#accessibility)
- [Styling](#styling)

## Data source

Read the Quick Launch tree from the same site (`pageContext.web.absoluteUrl`) with `SPHttpClient`:

- Preferred: `/_api/navigation/menustate?mapprovidername='SPNavigationProvider'` returns nested `Nodes` with `Children`, `Title` and `SimpleUrl`. Verify the exact response shape on the target tenant before depending on it.
- Fallback: `/_api/web/navigation/QuickLaunch` for top-level nodes, then `/_api/web/navigation/GetNodeById(<id>)/Children` per node for deeper levels.

Cache the result briefly (for example in `sessionStorage` keyed by site and a short expiry) so each page view does not re-fetch, and show the last good menu if a refresh fails.

## Rendering rules

- Skip the built-in `Recent` node.
- A node whose URL is the SharePoint linkless placeholder (`http://linkless.header/`) is a label: render a button that opens its children, not a link.
- Absolute same-site URLs and external URLs are valid links; only allow `http`, `https` and relative schemes. Open off-site links without changing the editors' intent (no forced new tab unless the node says so).
- Set text with `textContent`. Never concatenate titles or URLs into `innerHTML`.
- Render once per page; on `navigatedEvent` update the current-page state instead of re-appending.
- Provide a narrow-width layout (a button that opens a stacked, expandable list).

## Accessibility

Use `nav` with an `aria-label`, disclosure buttons with `aria-expanded` and `aria-controls`, a visible focus ring, and keyboard support: Tab through top-level items, Enter or Space to open, Arrow keys within a level, Escape to close and return focus to the trigger. Meet WCAG 2.1 AA contrast. Do not open menus on hover only.

## Styling

Match the organisation's design system tokens. Prefix all CSS class names to avoid collisions with SharePoint's styles, and avoid targeting SharePoint's internal class names, which change without notice.

### B.C. Government design alignment

For B.C. Government sites, take every value from the `bc-gov-design-system` skill (`assets/colors_and_type.css`, `references/REFERENCE.md`) rather than retyping it. For React-based UI also read `bc-gov-react`. Tokens used by the menu:

| Use | Token | Value |
|---|---|---|
| Bar background | `--color-brand-primary` | `#013366` |
| Hover | `--color-brand-primary-hover` | `#1E5189` |
| Pressed | `--color-brand-primary-pressed` | `#01264C` |
| Focus ring (never omit) | `--color-brand-focus` | `#2E5DD7` |
| Links in the dropdown | `--color-brand-link` | `#255A90` |
| Text | `--color-text-primary` | `#2D2D2D` |
| Borders and dividers | `--color-border` | `#D8D8D8` |
| Gold line under the bar | `--color-border-indigenous` | `#FBD389` |

- Font is `'BC Sans', 'Noto Sans', sans-serif`. SharePoint does not provide BC Sans, so the extension must load it itself: bundle the `.woff2` files from the design-system skill's `assets/fonts/` (licence in `assets/fonts/LICENSE`) or host them in a library the site can read, and declare `@font-face` with `font-display: swap`.
- Take the component structure (Header, Menu, MenuItem) from the B.C. Design System React components, which use React Aria for keyboard and screen-reader behaviour, but there is no ready-made mega-menu, so compose one from those primitives.
- Before choosing `@bcgov/design-system-react-components`, confirm that its React and React Aria versions work with the React version the SPFx project pins. If they do not, build the menu with plain TypeScript and DOM using the tokens above and the accessibility rules in this file. Record which route was taken and why.
- Include the design system's required accessibility behaviour regardless of route (WCAG 2.1 AA, visible focus, keyboard operation).
