# Sources (researched 2026-10-21)

Microsoft
- Support: Add text, tables, and images to your page with the Text web part (updated 2026-10-13) —
  https://support.microsoft.com/en-us/sharepoint/web-parts-and-apps-in-sharepoint/add-text-tables-and-images-to-your-page-with-the-text-web-part
- Learn: New web part editing experience powered by CKEditor lib v5 —
  https://learn.microsoft.com/en-us/sharepoint/sites/new-text-web-part-editing-experience-powered-by-editor-lib-five
- Message Center MC799209 (font sizes 8–250, list styles) — https://mc.merill.net/message/MC799209
- Message Center MC888883 (custom colors, paragraph/line spacing, quote styles) — https://mc.merill.net/message/MC888883
- Message Center MC1004412 (Text web part UI update, Feb 2025) — https://mc.merill.net/message/MC1004412
- Graph SharePoint Pages API GA (CK5 recommended for text web parts) —
  https://devblogs.microsoft.com/microsoft365dev/microsoft-graph-api-for-sharepoint-pages-is-now-generally-available

PnP code (read directly)
- pnpframework `HtmlTransformator.cs` (dev, includes PR #1294 merged 2026-10-21) —
  https://github.com/pnp/pnpframework/blob/dev/src/lib/PnP.Framework/Modernization/Transform/HtmlTransformator.cs
- pnpframework `InlineImageTransformator.cs` and docs/using-the-framework/readme.md (same PR)
- pnpcore `Page.cs` (EditorType, RtePageSettings.contentVersion, CK5 default) and
  PnP.Core.Test mock recordings (stored text part HTML; CK5: PageTextWithCK5InlineImageWithOptionsTest)
- PnP Core docs, "reverse engineer" formatted text — https://pnp.github.io/pnpcore/using-the-sdk/pages-webparts.html

Community reports
- sp-dev-docs #9160: CK4→CK5 table conversion markup — https://github.com/SharePoint/sp-dev-docs/issues/9160
- pnpcore discussion #1219 (CK4 vs CK5) — https://github.com/pnp/pnpcore/discussions/1219
- pnpcore discussion #1599 (CK5 wrappers unchanged) — https://github.com/pnp/pnpcore/discussions/1599
- Tech Community thread "Migrating HTML to Modern Pages – looks great until page is edited"
