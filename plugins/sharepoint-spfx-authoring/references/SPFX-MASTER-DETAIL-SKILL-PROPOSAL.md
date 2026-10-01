# SPFx Master-Detail Skill Proposal & Implementation Plan

## Overview
Based on the successful POC in `trial-tenancy-testing/books-authors-spfx-poc/`, modern SharePoint Online lacks out-of-the-box support for URL query parameter filtering (`?SelectedID=...`) across native List Web Parts.

This document outlines the design and scaffolding for a reusable **SPFx Master-Detail Modernization Skill** located in the `sharepoint-spfx-authoring` plugin (`plugins/sharepoint-spfx-authoring`).

---

## 1. Value Proposition
When modernizing legacy SharePoint 2013/2016/2019 applications to SharePoint Online:
- Legacy pages often feature **multi-list briefing/dossier layouts** driven by URL parameters (e.g. `Appearing_Persons_Briefing.aspx?SelectedID=123`).
- Rebuilding these with native SPO List Web Parts fails because modern List Web Parts only support manual click connections and ignore query parameters.
- A reusable **SPFx Master-Detail Skill** automates the scaffolding, REST wiring, styling, and packaging of consolidated dossier web parts in minutes.

---

## 2. Skill Architecture

### Skill Name: `scaffold-spfx-master-detail`
### Target Location: `plugins/sharepoint-spfx-authoring/skills/sharepoint-scaffold-spfx-master-detail/`

### Key Components Included in the Plugin:
1. **`SKILL.md`**:
   - Comprehensive workflow instructions on when to use SPFx Master-Detail over native list web parts.
   - Checklist for identifying URL-filtered legacy pages during discovery.
   - Node.js LTS environment requirements (Node v18 / v22) and SPFx generator commands (`heft test` / `heft package-solution`).
2. **`assets/templates/`**:
   - Generic Master-Detail TypeScript scaffold (`MasterDetailWebPart.ts.template`).
   - Fluent UI modern SCSS card/table styling (`MasterDetailWebPart.module.scss.template`).
3. **`scripts/`**:
   - `scaffold_spfx_master_detail.py`: Takes a JSON specification of the primary list, lookup fields, child lists, and photo library, and emits a complete, ready-to-build SPFx web part.
4. **`references/`**:
   - `MODERN-PAGE-DYNAMIC-FILTERING-GAP.md` (the authoritative rationale).
   - `FULL-SETUP-GUIDE.md` (the 8-step build, package, and deployment runbook).
