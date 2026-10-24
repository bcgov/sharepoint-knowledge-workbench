# SharePoint Knowledge Workbench (`sharepoint-workbench`)

The unified, production-grade SharePoint Knowledge Workbench plugin. Provides 11 self-contained domain skills for SharePoint Online and hybrid SharePoint modernization, information architecture, development, publishing, and Copilot extensibility.

## The 11 Domain Skills

| # | Skill Name | Scope & Purpose |
|:---:|:---|:---|
| 1 | [`setting-up-sharepoint-workbench`](skills/setting-up-sharepoint-workbench/SKILL.md) | Setup, connection profiles (`config.psd1`), Entra ID app registration requests. |
| 2 | [`assessing-sharepoint-sites`](skills/assessing-sharepoint-sites/SKILL.md) | Read-only discovery: inventories, permissions, webparts, metadata, schema drift. |
| 3 | [`converting-sharepoint-documents`](skills/converting-sharepoint-documents/SKILL.md) | Gated document compiler: DOCX/PDF ➡️ AST analysis ➡️ Markdown/SPO page render. |
| 4 | [`developing-spfx-solutions`](skills/developing-spfx-solutions/SKILL.md) | SPFx developer toolchain: web parts, extensions, hosted workbench, sppkg deploy. |
| 5 | [`managing-sharepoint-lists-and-libraries`](skills/managing-sharepoint-lists-and-libraries/SKILL.md) | Storage containers: lists, document libraries, views, list columns, settings, files. |
| 6 | [`publishing-sharepoint-pages`](skills/publishing-sharepoint-pages/SKILL.md) | Web publishing: modern pages, HTML pages, markdown deployment, CKEditor 5 RTE formatting. |
| 7 | [`managing-sharepoint-schema`](skills/managing-sharepoint-schema/SKILL.md) | Enterprise IA: site columns, content types, JSON column formatters, PnP provisioning templates. |
| 8 | [`managing-sharepoint-navigation`](skills/managing-sharepoint-navigation/SKILL.md) | Declarative navigation provisioning: Excel workbook ↔ live SPO Top Nav / Quick Launch sync. |
| 9 | [`modernizing-sharepoint-pages`](skills/modernizing-sharepoint-pages/SKILL.md) | Interactive classic ASPX ➡️ modern canvas conversion wizard with `spo-webparts.json`. |
| 10 | [`migrating-sharepoint-sites`](skills/migrating-sharepoint-sites/SKILL.md) | Interactive sequencing wizard: dependency discovery, topological sort, wave execution ledger. |
| 11 | [`managing-sharepoint-copilot-agents-and-skills`](skills/managing-sharepoint-copilot-agents-and-skills/SKILL.md) | Declarative Copilot `.agent` packages, knowledge grounding, `AgentAssets`, native skills. |

## Key Invariants

- **Self-Contained Spokes:** Every skill contains its own `scripts/`, `references/modes/`, and `assets/`. There are **0 symlinks**.
- **Interactive Wizards with Human Gates:** Multi-turn operations (`converting-sharepoint-documents`, `modernizing-sharepoint-pages`, `migrating-sharepoint-sites`) retain human confirmation gates before execution.
- **Safety by Default:** All tenant writes require `-Execute` and an explicit `-ConfirmToken`.
