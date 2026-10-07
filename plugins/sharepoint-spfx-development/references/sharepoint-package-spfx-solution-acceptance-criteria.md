# Acceptance Criteria: sharepoint-package-spfx-solution

- Skill slug: `sharepoint-package-spfx-solution`.
- Target plugin: `sharepoint-spfx-development`.
- Purpose: Automates production SPFx solution builds using Heft and Webpack and verifies .sppkg package integrity, for both web parts and Form Customizers. Use when an SPFx solution is ready to be built into a deployable package.

## Constraints honored

- Do not run `npm audit fix --force`: SPFx pins its toolchain (`@rushstack/heft`, `@microsoft/spfx-web-build-rig`) and forced upgrades break the build.
- Run the pre-flight checklist before building; a production build takes about 4 to 6 minutes, so avoid rebuild cycles.
- Always bump `solution.version` in `config/package-solution.json` before packaging an update, or SharePoint will not prompt for the upgrade.
- Requires Node.js v18 or v22 LTS active in the session (`nvm use 22`). The script builds locally and writes nothing to the tenant.

## Verification passes

- Both stages report PASS and the `.sppkg` is above 0 KB with no build or linting errors. If you ran the commands directly instead of the script, confirm exit code 0.
- Focused plugin tests for this skill pass.
