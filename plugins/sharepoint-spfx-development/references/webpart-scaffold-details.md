# Generic web part scaffolding details

## Contents

- [Intent and toolchain](#intent-and-toolchain)
- [Clarifying questions](#clarifying-questions)
- [Run the generator](#run-the-generator)
- [Customize the generated files](#customize-the-generated-files)
- [Verify the build](#verify-the-build)
- [Next steps](#next-steps)

## Intent and toolchain

A generic, interactive workflow for a new SPFx web part: confirm the toolchain, ask what the web part needs to do, run the official Yeoman generator with the answers, then customize the boilerplate. It intentionally assumes
no specific layout, data source or content shape. Toolchain: Node.js LTS (v18 or v22), `yo` and `@microsoft/generator-sharepoint`, SPFx 1.20+ (Heft / Webpack); PowerShell 7 with `PnP.PowerShell` only later, for deployment.

`scripts/check-spfx-toolchain.ps1` checks Node (v18.x or v22.x), npm, `yo` and `@microsoft/generator-sharepoint`, printing PASS or FAIL per dependency and exiting non-zero if a required one is missing. If Node is missing
or on an incompatible major version, install or select it first (for example `nvm install 22 && nvm use 22`) and re-run the check. Do not scaffold on an unsupported Node version.

## Clarifying questions

Do not guess the web part's shape. Ask one question at a time, offering sensible defaults:

- What should the web part be called (solution name and web part name)?
- What is its purpose, in a sentence or two?
- Where does its content come from: a static or config-driven list, a SharePoint list via REST, an external API, or static markup?
- Must it be user-configurable after deployment (property pane fields), or is a fixed layout fine?
- Does the UI need state or interactivity complex enough to warrant React, or is plain DOM (`No JavaScript framework`) enough?
- Where should the new project live on disk?

Use the answers for the Yeoman prompts and the customization step; do not proceed with unstated assumptions about layout or data source.

## Run the generator

```powershell
md path/to/<solution-folder>
cd path/to/<solution-folder>
yo @microsoft/sharepoint
```

Prompts: Solution name (the folder name, or a kebab-case name); Target `SharePoint Online only (latest)`; Component type `WebPart`; Web part name (PascalCase); Web part description (one line); Framework
`No JavaScript framework` or `React`; Template `Minimal` unless a richer one was requested. This generates the solution shell (`package.json`, `config/`, `tsconfig.json`, `src/webparts/<webPartName>/`).

## Customize the generated files

Under `src/webparts/<webPartFolder>/`:

1. `<WebPartName>WebPart.ts`: implement `render()` for the described behavior, and `getPropertyPaneConfiguration()` if post-deployment configurability was requested.
2. `<WebPartName>WebPart.module.scss`: style with CSS module classes (no inline styles; keep class names module-scoped).
3. `<WebPartName>WebPart.manifest.json`: set `preconfiguredEntries[0].title`, `.description` and `officeFabricIconFontName` to match the purpose.
4. `loc/en-us.js` and `loc/mystrings.d.ts`: add user-facing strings used by the property pane or markup.

Escape any user-editable or list-sourced string before inserting it into `this.domElement.innerHTML` (XSS mitigation).

## Verify the build

```powershell
cd path/to/<solution-folder>
npm install
npm run build
```

Confirm the build exits 0 and produces `sharepoint/solution/<solution-name>.sppkg`. See `spfx-naming-and-versioning.md` for the solution name versus the toolbox title authors see.

## Next steps

Package with `sharepoint-package-spfx-solution` (if `npm run build` has not covered it), then `sharepoint-deploy-spfx-solution` or `sharepoint-publish-spfx-package` to upload and enable the package in a Site Collection or Tenant App Catalog.
