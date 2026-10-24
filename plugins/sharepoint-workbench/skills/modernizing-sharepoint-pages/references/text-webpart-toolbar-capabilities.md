# Text web part toolbar capabilities (SharePoint Online, as of Oct 2026)

What an author can produce with the toolbar and the **Text and table formatting** pane.
If an effect is not in this list, the Text web part cannot keep it after an edit.
Markup for each item is in [text-webpart-markup-vocabulary](text-webpart-markup-vocabulary.md).

Sources: Microsoft Support "Add text, tables, and images to your page with the Text web
part" (updated 2026-10-13); Message Center MC799209 (May–Jul 2024), MC888883 (Sep 2024),
MC1004412 (Feb 2025); Microsoft Learn "New web part editing experience powered by CKEditor
lib v5".

## Text styles (Styles dropdown)
- Heading 1, Heading 2, Heading 3 (UI names). Page anchors are added automatically to
  Heading 1–3, so headings double as in-page bookmarks (`page.aspx#Heading text`).
- A further heading level (stored `h4`) appears in older content and in transformer output.
- Normal text **with** spacing between paragraphs / **without** spacing (MC888883).
- Quote styles — "new quote style options" (MC888883). Older content uses `blockquote`.
- Monospaced / pre-formatted text (`pre` appears in stored captures).

## Character formatting
- Bold, italic, underline, strikethrough, superscript, subscript.
- Font size: presets plus custom 8–250 typed value (MC799209).
- Font color: theme colors, standard colors, and custom colors (custom added MC888883).
- Highlight color.
- Clear formatting.

## Paragraph formatting
- Alignment: left, center, right, justify.
- Increase / decrease indent.
- Spacing before/after paragraphs and headings (MC888883).
- Custom line spacing (MC888883). Note: the Support article still says line height is fixed
  at 140% — treat that sentence as stale; the feature exists but its stored markup must be
  captured.

## Lists
- Bulleted: disc, circle, square.
- Numbered: 1, A, a, I, i ("numbered, alphabetical, alphabetical small, roman, roman small").
- Start new list / Start list at N (MC799209).

## Links
- Hyperlink via toolbar, pane, or Ctrl+K; can search and pick a site page; pasting a URL
  auto-links it.

## Tables
- Insert table; insert row above/below, column left/right; delete row/column/table; Tab adds rows.
- Five style shapes, each in a **simple** (neutral) and a **themed** variant:
  Plain · Subtle header (bottom border) · Header (solid header, reverse font) ·
  Alternating rows (solid header + banded rows) · Column header (solid header, first column
  and alternate rows shaded).
- Table alignment: left, center, right.
- Column widths are resizable in CK5 (proportional to editor width).

## Images
- Paste inline images; align left/center/right; resize via corner handles; alt text; link.
- Left/right alignment works best above 50% of column width.

## Not available in the Text web part
Font family / custom fonts (brand fonts come from the site theme or the
"custom fonts and colors" features, not per-run markup), borders/boxes around paragraphs,
background color on blocks, multi-column layout, embedded iframes/video/script, custom CSS
classes. Use page sections (with section background), Quick Links, Callout/Hero, Image,
Embed, Markdown, or an SPFx web part for these.
