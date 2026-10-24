# BC Design System page chrome for static HTML pages

Every converted page must carry the same chrome, not just the token CSS. Source:
`standard-design-system` skill, its REFERENCE document ("Header (with subheader)",
"Breadcrumb", "Full footer", "Data table") and its non-negotiable rules.

## Required page structure

1. `<!DOCTYPE html>`, `lang="en"`, UTF-8, viewport, and a real `<title>`.
2. `<link rel="stylesheet">` to the site-level `colors_and_type.css`
   (`{SITE_PATH}/SiteAssets/standard-design-system/colors_and_type.css`).
3. `<header class="site-header">`: BC logo (`.../icons/bc-logo.png`, alt
   "Government of British Columbia"), divider, organization name, then a
   `.subheader` bar naming the section (for example "Operations Services").
4. `<main class="page">`: breadcrumb `nav[aria-label="Breadcrumb"]`, optional eyebrow,
   `<h1>`, then the preserved source content.
5. Full footer: Indigenous acknowledgment band, logo and links block (Disclaimer,
   Privacy, Accessibility), and the copyright line with the current year.

## Rules

- Build every style from tokens (`var(--space-*)`, `--color-*`, `--text-*`,
  `--layout-*`); no new hex values outside the skill's own snippets.
- Add `a { color: var(--color-brand-link) }` and the `:focus-visible` ring
  (`2px solid var(--color-brand-focus)`, offset 2px) so links are styled and keyboard
  accessible.
- Reference logo and CSS by site-level absolute paths; never hotlink external hosts.
- Breadcrumb: link only destinations that exist on the target site (the home page is
  safe); show unknown levels as plain text rather than guessing URLs.
- Content tables keep their original structure. Style them with token borders and
  padding; use `th scope="row"` or `scope="col"` to match the source layout.
- Footer links use the public example.com disclaimer, privacy and accessible-government
  pages. Sentence case, no emoji, no exclamation marks.
- Preserve source text, table, row, cell, link and list counts; record them in the
  conversion evidence. Chrome additions are the only permitted extra content.

## Reuse

Copy the `<style>` block, header, breadcrumb and footer from the most recent
published page in the same environment and change only `{SITE_PATH}`, organization
name, subheader text, breadcrumb labels, title and `<h1>`. The first published example
is `Operations/Administration Documents/awards/criteria_processes.html` on DEV.
