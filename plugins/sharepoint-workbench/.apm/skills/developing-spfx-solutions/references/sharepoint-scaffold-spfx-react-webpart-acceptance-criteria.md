# Acceptance Criteria: sharepoint-scaffold-spfx-react-webpart

- Skill slug: `sharepoint-scaffold-spfx-react-webpart`.
- Target plugin: `sharepoint-spfx-development`.
- Purpose: Scaffolds an enterprise-grade React 17/18 SPFx Web Part with Fluent UI 8/9, PnPjs v4 cross-site context, Tailwind CSS, self-healing migration GUID recovery and robust state management. Use for complex, interactive components such as document catalogues, favourites portals, multi-list dashboards or cross-site aggregators.

## Constraints honored

- The generator is local (Python 3.8+) and writes only to `--output-dir`. The surrounding project needs Node.js LTS (v18 or v22) and SPFx 1.20+ (Heft / Webpack).
- Tailwind must be compiled before the SPFx build; add the `build:tailwind` step to `package.json` so `npm run build` runs it first.
- For lists promoted across DEV, TEST and PROD, rely on the self-healing GUID recovery (fall back to list titles); do not hardcode list GUIDs.
- Run from this skill's root.

## Verification passes

- The output holds the web part `.ts` and manifest, `components/` (the React component and `pnpjsConfig.ts`) and `style/` (Tailwind input and output). `npm run build` succeeds.
- Focused plugin tests for this skill pass.
