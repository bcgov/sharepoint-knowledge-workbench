# SPFx packaging: build steps and pre-flight checklist

## Contents

- [Build and package](#build-and-package)
- [Do not force-upgrade dependencies](#do-not-force-upgrade-dependencies)
- [Pre-flight checklist](#pre-flight-checklist)

## Build and package

This applies to SPFx web parts and Form Customizers alike. Prerequisites: Node.js v18 or v22 LTS active in the terminal (`nvm use 22`).

```powershell
pwsh -File scripts/package-spfx-solution.ps1 -SolutionPath path/to/spfx-solution-root
```

The script runs `npx heft test --clean --production`, then `npx heft package-solution --production`, then confirms a non-empty `.sppkg` exists under `sharepoint/solution/`, printing PASS or FAIL for each stage.
The equivalent direct commands are `npx heft test --clean --production && npx heft package-solution --production`, or `npm run build` when defined in `package.json`. If you run the commands directly, confirm exit code 0 and
that `sharepoint/solution/<solution-name>.sppkg` exists with a size above 0 KB and no build or linting errors.

## Do not force-upgrade dependencies

Do not run `npm audit fix --force`. SPFx projects use strictly pinned toolchain packages (`@rushstack/heft`, `@microsoft/spfx-web-build-rig`); forced upgrades break the Heft build toolchain.

## Pre-flight checklist

A production SPFx build is compute-intensive (typically 4 to 6 minutes), so audit the code and configuration before building to avoid costly rebuilds.

1. **Dynamic site path resolution (no hardcoded URLs).** Audit `*WebPart.ts` and `*Props.ts` for hardcoded site-relative URLs (for example `/sites/<some-site>`). Site paths must default dynamically to the current web
   (`this.context.pageContext.web.serverRelativeUrl`) or be fully configurable in the property pane.
2. **Unlocked property pane configuration.** Fields in `getPropertyPaneConfiguration()` (such as `sourceSiteUrl`, list dropdowns, view filters) must be editable, not permanently `disabled: true`. Implement
   `onPropertyPaneFieldChanged` handlers to reload dynamic dropdowns when the site path or list source changes.
3. **Self-healing auto-binding.** If a required list GUID property (`applicationsListId`, `libraryId`, and so on) is empty or invalid on mount, query the target site's lists and bind to the matching default list
   name (`Applications`, `Documents`, and so on).
4. **Semantic version bump.** Increment `solution.version` in `config/package-solution.json` (see `spfx-naming-and-versioning.md`).
5. **Web part UI selector title check.** Confirm `preconfiguredEntries[0].title.default` in the web part manifest matches the intended user-facing title.
6. **Relational lookup and PnPjs schema alignment.** When web parts read or write SharePoint Lookup columns (such as join tables like `My Favourite Apps -> ApplicationId`):
   - **Write**: SharePoint REST and PnPjs require writing `<LookupInternalName>Id` (for example `ApplicationIdId: 100`). Implement dual-mode write: `ApplicationIdId` first, fall back to `ApplicationId` for numeric schemas.
   - **Read**: select both ID and text fields: `items.select('Id', 'ApplicationId/ID', 'ApplicationId/Title', 'ApplicationIdId').expand('ApplicationId')`.
   - **Relational integrity**: enforce `RelationshipDeleteBehavior = Restrict` and `Indexed = $true` on lookup column definitions.
