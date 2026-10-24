# Acceptance Criteria: sharepoint-scaffold-spfx-master-detail-webpart

- Skill slug: `sharepoint-scaffold-spfx-master-detail-webpart`.
- Target plugin: `sharepoint-spfx-development`.
- Purpose: Scaffolds a complete SPFx Master-Detail Web Part boilerplate (TypeScript, SCSS module, manifest) from a JSON list layout specification. Use when modernizing legacy SharePoint 2013/2016 multi-list briefing or dossier pages that rely on URL parameter query filtering (?SelectedID=...).

## Constraints honored

- Out-of-the-box List Web Parts cannot filter on a URL query string; this is the reason for a custom web part. Use it only for that kind of URL-driven master-detail page.
- The generator is local (Python 3.8+) and writes only to `--output-dir`. It needs Node.js LTS (v18 or v22) and SPFx 1.20+ for the surrounding project.
- `scripts/provision-sample-master-detail-schema.ps1`, the optional test-data script, is a live tenant write with no dry-run gate: use a non-production site and let the user run it.
- Run from this skill's root.

## Verification passes

- All three files exist in the output directory, and the manifest carries a unique GUID. Build and package to confirm the web part compiles.
- Focused plugin tests for this skill pass.
