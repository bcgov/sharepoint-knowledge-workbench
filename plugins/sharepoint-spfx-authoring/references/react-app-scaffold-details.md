# Enterprise React web part scaffolding details

## Contents

- [Architecture](#architecture)
- [Toolchain](#toolchain)
- [Specification and generator](#specification-and-generator)
- [Tailwind build setup](#tailwind-build-setup)

## Architecture

For complex, interactive SharePoint Online components (document catalogues, personal favourites portals, multi-list dashboards, cross-site data aggregators), this skill scaffolds an Enterprise React SPFx web part with:

- **PnPjs v4 (`@pnp/sp` 4.18+):** a centralized singleton with cross-site-collection query support (`getWeb(url)`).
- **Tailwind CSS 3:** clean CLI preprocessing alongside Heft / Webpack without ejecting the build.
- **Fluent UI 8/9 and theme adaptation:** automatic adaptation to SharePoint section background colors.
- **Self-healing GUID recovery:** a resilient fallback to list titles when web parts are promoted across DEV, TEST and PROD.

Reference guides: `SPFX-TAILWIND-INTEGRATION-GUIDE.md` (Tailwind CLI setup), `SPFX-PNPJS-V4-CROSS-SITE-ARCHITECTURE.md` (hub-and-spoke data patterns), `SPFX-SELF-HEALING-MIGRATION-GUIDE.md` (list GUID recovery).

## Toolchain

Node.js LTS (v18 or v22); SPFx 1.20+ (Heft / Webpack); Python 3.8+ for the generator.

## Specification and generator

`app_spec.json`:

```json
{
  "webPartName": "DocumentCatalogue",
  "title": "Corporate Document Catalogue",
  "description": "Interactive document browser with personal favouriting and metadata filtering."
}
```

```bash
python scripts/scaffold_spfx_react_app.py --spec path/to/app_spec.json --output-dir path/to/spfx-project/src/webparts/documentCatalogue
```

It writes `DocumentCatalogueWebPart.manifest.json`, `DocumentCatalogueWebPart.ts`, `components/DocumentCatalogue.tsx`, `components/pnpjsConfig.ts`, and `style/tailwind.css` plus `style/tailwind.output.css`.

## Tailwind build setup

Ensure `package.json` contains the pre-build Tailwind compilation command:

```json
{
  "scripts": {
    "build:tailwind": "tailwindcss -i ./src/webparts/documentCatalogue/style/tailwind.css -o ./src/webparts/documentCatalogue/style/tailwind.output.css --minify",
    "build": "npm run build:tailwind && heft test --clean --production && heft package-solution --production"
  }
}
```

Then verify with `npm run build`.
