# Acceptance Criteria: sharepoint-scaffold-spfx-webpart

- Skill slug: `sharepoint-scaffold-spfx-webpart`.
- Target plugin: `sharepoint-spfx-development`.
- Purpose: Guides scaffolding of any new, generic SPFx web part from scratch by confirming toolchain dependencies, interactively gathering the web part's requirements (name, purpose, data source, framework, configurability), running the official Yeoman generator, and customizing the generated files. Use when no more specific scaffold skill fits.

## Constraints honored

- Do not guess the web part's shape. Ask the clarifying questions, one at a time with defaults, before running the generator, and do not proceed with unstated assumptions about layout or data source.
- Do not scaffold on an unsupported Node version: require Node v18 or v22 (`scripts/check-spfx-toolchain.ps1` checks Node, npm, `yo` and `@microsoft/generator-sharepoint`).
- Escape any user-editable or list-sourced string before inserting it into `this.domElement.innerHTML` (XSS).
- For a master-detail dashboard, a React app or a form, use the more specific scaffold skills. Local work only; nothing is written to the tenant.

## Verification passes

- The build exits 0 and produces `sharepoint/solution/<solution-name>.sppkg`. The manifest title and description match the intended toolbox entry.
- Focused plugin tests for this skill pass.
