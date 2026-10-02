# Master-Detail web part scaffolding details

## Contents

- [Why](#why)
- [Workspace setup](#workspace-setup)
- [The layout specification](#the-layout-specification)
- [Run the generator](#run-the-generator)
- [Generated files](#generated-files)
- [Sample data schema script](#sample-data-schema-script)

## Why

Modern SharePoint Online out-of-the-box List Web Parts do not support URL query-string filtering (`?SelectedID=...`). When modernizing classic ASPX pages that depend on URL-driven cross-web-part filtering (for example a
multi-list briefing or dossier page), this skill generates one consolidated Master-Detail SPFx web part (TypeScript, SCSS module, manifest) in place of a multi-web-part classic layout.

Toolchain: Python 3.8+, Node.js LTS (v18 or v22), SPFx 1.20+ (Heft / Webpack).

## Workspace setup

Starting from scratch, either:

- **Option A (instant template):** copy the pre-configured project boilerplate from `assets/templates/spfx-project-reference/` to your target directory. The bundled copy has no `.gitignore` (git refuses a symlinked
  `.gitignore` in the source repository); add one for your project, or use the plugin source's copy at `plugins/sharepoint-spfx-authoring/assets/templates/spfx-project-reference/.gitignore`; or
- **Option B (Yeoman):** run `yo @microsoft/sharepoint` choosing component type `WebPart` and template `Minimal` (Node v22 or v18 LTS required).

## The layout specification

A JSON file (for example `dossier_spec.json`) describing the primary record, lookup relationships and child lists:

```json
{
  "webPartName": "PersonBriefing",
  "title": "Master-Detail Dossier Dashboard",
  "primaryList": "Persons",
  "lookupList": "Authors",
  "childLists": [
    { "title": "Upcoming Appearances", "listName": "All_Appearances", "filterField": "RelatedAuthorId" },
    { "title": "Background Information", "listName": "Dossier_Narratives", "filterField": "RelatedAuthorId" }
  ],
  "imageLibrary": "Images"
}
```

## Run the generator

```bash
python scripts/scaffold_spfx_master_detail.py --spec path/to/dossier_spec.json --output-dir path/to/spfx-project/src/webparts/personBriefing
```

## Generated files

1. `PersonBriefingWebPart.ts`: parallel REST querying, URL parameter parsing (`?SelectedID=...`), dynamic HTML rendering and action link routing.
2. `PersonBriefingWebPart.module.scss`: Fluent UI responsive grid, card layout, portrait photo box, data tables and action buttons.
3. `PersonBriefingWebPart.manifest.json`: the SPFx component definition with a unique GUID.

Then package with the `sharepoint-package-spfx-solution` skill.

## Sample data schema script

`scripts/provision-sample-dossier-schema.ps1` idempotently creates sample lists, lookups, Picture columns, sample records and a modern test page (default name `master-detail-dossier-poc`, header type None), for
validating Master-Detail web parts. It is a live tenant write with no dry-run gate; use a non-production site. Parameters: `-SiteUrl`, `-ClientId`, `-TenantId`, `-TenantAdminUrl`, `-ConfigPath`, `-PageName`.
