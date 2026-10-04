# SPFx naming and versioning

## Contents

- [The naming layers](#the-naming-layers)
- [Version bump rule](#version-bump-rule)
- [Manifest locations](#manifest-locations)

## The naming layers

Verify all of these are aligned before building and packaging.

| Layer | Where | Purpose and impact |
|---|---|---|
| Package file | `config/package-solution.json` (`paths.zippedPackage`) | The physical `.sppkg` file name in `sharepoint/solution/`. |
| Solution name | `config/package-solution.json` (`solution.name`) | The display title in the App Catalog and in Site Contents > Add an App. |
| Solution version | `config/package-solution.json` (`solution.version`) | Increment (for example `1.0.6.0` to `1.0.7.0`) whenever code or manifests change so SharePoint prompts for the upgrade. |
| Web part title | the web part manifest (`preconfiguredEntries[0].title.default`) | The name authors actually see in the page `+` toolbox selector. |
| Web part description | the web part manifest (`preconfiguredEntries[0].description.default`) | The subtitle or tooltip under the title in the toolbox. |
| Toolbox category | the web part manifest (`preconfiguredEntries[0].group.default`) | The group header in the toolbox (for example `Advanced`). |

To change what authors see in the toolbox, edit `preconfiguredEntries[0].title.default` and rebuild with `sharepoint-package-spfx-solution`.

## Version bump rule

Always increment `solution.version` before packaging an update (for example `1.0.8.0` to `1.0.9.0`), so SharePoint recognizes and prompts for the updated package at deployment.

## Manifest locations

- Web part: `src/webparts/<name>/<Name>WebPart.manifest.json`.
- Form Customizer: `src/extensions/<name>/<Name>.manifest.json`.
