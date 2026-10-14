# Application Customizer Workflow

## Contents

- [Scaffold](#scaffold)
- [Placeholders](#placeholders)
- [Debugging](#debugging)
- [Package, deploy, activate](#package-deploy-activate)
- [Rollback](#rollback)

## Scaffold

Run `scripts/check-spfx-toolchain.ps1` (Node v18 or v22, npm, `yo`, `@microsoft/generator-sharepoint`). Then:

```powershell
yo @microsoft/sharepoint
```

Answers: SharePoint Online only; Extension; **Application Customizer**; a PascalCase name; a one-line description; framework **No framework** for plain DOM or **React** when the UI is component-heavy. Generator 1.23 produces a Heft-based project, older generators (for example the 1.20 `back-to-top` extension) use gulp; build with the scripts in the generated `package.json`, and use the matching Node version.

Keep the manifest `id` stable: it is the component id used for registration and for `serve.json`.

## Placeholders

`PlaceholderName.Top` and `PlaceholderName.Bottom`. Always call `tryCreateContent` and handle `undefined` (the placeholder is missing on some pages). Subscribe to `placeholderProvider.changedEvent` and dispose handlers and DOM in `onDispose`. For in-app navigation, `navigatedEvent` from `sp-application-base` fires without a page reload, so re-render rather than appending again.

## Debugging

Set `config/serve.json` `serveConfigurations.default.pageUrl` to a page of the non-production site and `customActions.<manifest-id>.location` to `ClientSideExtension.ApplicationCustomizer`, then `npm run serve` (or `gulp serve`) and accept the prompt to load debug scripts. A manual URL is:

```text
<page-url>?loadSPFX=true&debugManifestsFile=https://localhost:4321/temp/manifests.js&customActions={"<id>":{"location":"ClientSideExtension.ApplicationCustomizer","properties":{}}}
```

Trust the local dev certificate once with `npm run trust-dev-cert` (or `gulp trust-dev-cert`).

## Package, deploy, activate

1. Build and package with `sharepoint-package-spfx-solution` (`includeClientSideAssets: true`).
2. Deploy to the site or tenant App Catalog and add the app to the site with `sharepoint-deploy-spfx-solution`.
3. If `skipFeatureDeployment` is true, or the extension is not tenant-wide, register it:
   `scripts/register-application-customizer.ps1` (dry-run first). `-Scope Web` for one site, `-Scope Site` for a site collection.
4. Re-query is automatic in the script; also hard-refresh the browser. Allow a few minutes for propagation.

## Rollback

`scripts/register-application-customizer.ps1 -Remove` (with `-Execute -ConfirmToken ...`) removes every matching action and is safe when none exist. It does not delete the package, the app or any content.
