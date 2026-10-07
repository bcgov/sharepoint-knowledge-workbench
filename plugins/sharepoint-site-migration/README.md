# sharepoint-site-migration

Plans and executes SharePoint site migration: validates a source-site export, derives the object
dependency graph and migration wave plan, scaffolds wave scripts, analyzes and modernizes classic
pages (plan, preview, single and library conversion, validation, reports), migrates list content
with two-pass lookup re-linking, and extracts and updates links in pages, documents and rich-text
columns. Planning and analysis are read-only; most writing scripts are dry-run by default, gated behind -Execute plus an operation-specific -ConfirmToken; the preserved consumer-specific repair script in the content-audit folder is a documented exception (it writes unless -DryRun is passed), so check each script's own parameters.

## Plugin layout

```text
plugins/sharepoint-site-migration/
├── assets/
├── references/
├── scripts/
├── skills/
└── tests/
```

## Skills by functional group

### Migrate and modernize SharePoint sites

- `sharepoint-analyze-classic-pages` -- Stages 1-2 of classic page modernization. Parses exported classic .aspx content, view exports and connected-consumer overrides into a neutral component inventory, then classifies each component by role, type and...
- `sharepoint-analyze-migration-dependencies` -- Deterministically shapes a caller-supplied dependency-matrix object list into a computed wave order (reusing wave_planning.plan_waves directly), gated by completeness checks (source coverage, orphan matrix entries,...
- `sharepoint-audit-list-migration` -- Audit list and library content fidelity between SP2016 On-Premises and SharePoint Online. Reconciles multi-value and single-value identity lookup columns against ground truth, detects Item ID vs Case ID suffix...
- `sharepoint-convert-legacy-aspx-to-html` -- Converts one eligible static legacy ASPX page to HTML for migration.
- `sharepoint-convert-page-library-to-modern` -- Orchestrates classic-to-modern page conversion across every page in a library, one subprocess per page, with a resumable manifest and post-run validation. Use to convert a whole library in one run. Dry-run by...
- `sharepoint-convert-page-to-modern` -- Converts a single classic SharePoint page to a modern Site Page with ConvertTo-PnPPage and stamps caller-supplied field-mapping and literal metadata onto the converted page. Use to convert one classic .aspx page...
- `sharepoint-create-page-preview` -- Merges a site's structural chrome (navigation, header, logo, ancestors) with an already-extracted page's content (modern-preview.html plus metadata.json) into a single self-contained offline preview HTML file. Use so...
- `sharepoint-extract-links` -- Extracts and classifies every hyperlink from SharePoint page or document content (absolute, server-relative, protocol-relative, mailto, anchor, malformed) into a LinkInventory with an honest outcome (OBSERVED, EMPTY,...
- `sharepoint-generate-modernization-report` -- Renders a human-readable Markdown disposition report from a PageConversionManifest (conforming to assets/manifest-schema.json), with a web-part classification table, a gaps section naming every unmigrated item, and a...
- `sharepoint-initialize-migration-project` -- Confirms the workbench's own repository-root config.psd1 (produced by sharepoint-workbench-setup's initialize-connection-config) already exists with a Connection block, then creates a per-migration working directory...
- `sharepoint-migrate-list-content` -- Migrates SharePoint list-item content in batches with retry, and resolves lookup-column values with a two-pass ID-mapping technique (record source-to-destination IDs during a content pass, resolve lookup fields...
- `sharepoint-normalize-migration-inventory` -- Validates and normalizes an already-produced source-site export directory (lists, fields, and critically lookup-column targets) into the raw object list that stage 3a needs. Use as stage 2 after exporting a source...
- `sharepoint-plan-migration-waves` -- Computes a deployment wave plan by topologically sorting a caller-supplied, dependency-annotated list of deployment objects, grouping them into ordered stages where every dependency is satisfied by a strictly earlier...
- `sharepoint-plan-page-modernization` -- Stages 3-4 of classic page modernization. Selects a modern page layout from declarative, data-driven rules, then maps classified components to modern sections and views, emitting an explicit gap notice for components...
- `sharepoint-scaffold-migration-wave-scripts` -- Reads dependency-matrix.json (from the dependency-graph analysis) and synthesizes one wave-script skeleton per computed wave, plus a single human wave guide, using real object names, types and dependsOn from the...
- `sharepoint-update-links-in-documents` -- Rewrites legacy URLs embedded INSIDE Office documents (docx, xlsx, pptx via stdlib zipfile, with no python-docx, openpyxl or python-pptx dependency) and PDFs (through an optional caller-injected handler) stored in a...
- `sharepoint-update-page-links` -- Rewrites legacy SharePoint URLs in page/HTML body content to their modern targets using a declarative, parameterized rewrite ruleset. Use after a migration has moved content (for example classic /Pages/ to...
- `sharepoint-update-rich-text-image-links` -- Inventory-verified remediation of an embedded img reference inside a rich-text list field. Classifies each item against a real document-library inventory (matched, missing, broken-placeholder-no-src, no-image) and...
- `sharepoint-validate-link-integrity` -- Verifies that links resolve after a migration or remediation pass, classifying each as RESOLVED, BROKEN, UNRESOLVABLE or SKIPPED with an honest overall outcome. Use last, to prove a migration or remediation actually...
- `sharepoint-validate-page-modernization` -- Read-only validation of converted modern pages against a run manifest, checking page existence, mapped-field population and literal field values. Use after a conversion run, to confirm every page landed with its...

## Previous identities

Skill and plugin names changed in the seven-domain migration (issue #6). Old names are not retained as aliases.

| Previous skill | Current skill | Previous plugin |
|---|---|---|
| `sharepoint-analyze-aspx-pages` | `sharepoint-analyze-classic-pages` | `sharepoint-page-modernization` |
| `sharepoint-analyze-sharepoint-dependency-graph` | `sharepoint-analyze-migration-dependencies` | `sharepoint-migration-planning` |
| `sharepoint-audit-list-content` | `sharepoint-audit-list-migration` | `sharepoint-content-migration` |
| `sharepoint-execute-page-bulk-migration` | `sharepoint-convert-page-library-to-modern` | `sharepoint-page-modernization-execution` |
| `sharepoint-convert-page-to-modern` | `sharepoint-convert-page-to-modern` | `sharepoint-page-modernization-execution` |
| `sharepoint-compose-page-preview` | `sharepoint-create-page-preview` | `sharepoint-page-modernization` |
| `sharepoint-extract-links` | `sharepoint-extract-links` | `sharepoint-link-remediation` |
| `sharepoint-generate-conversion-report` | `sharepoint-generate-modernization-report` | `sharepoint-page-modernization` |
| `sharepoint-setup-sharepoint-migration-project` | `sharepoint-initialize-migration-project` | `sharepoint-migration-planning` |
| `sharepoint-migrate-sharepoint-list-content` | `sharepoint-migrate-list-content` | `sharepoint-content-migration` |
| `sharepoint-discover-sharepoint-site-inventory` | `sharepoint-normalize-migration-inventory` | `sharepoint-migration-planning` |
| `sharepoint-plan-sharepoint-deployment-waves` | `sharepoint-plan-migration-waves` | `sharepoint-migration-planning` |
| `sharepoint-convert-aspx-pages` | `sharepoint-plan-page-modernization` | `sharepoint-page-modernization` |
| `sharepoint-generate-sharepoint-wave-scripts` | `sharepoint-scaffold-migration-wave-scripts` | `sharepoint-migration-planning` |
| `sharepoint-remediate-document-content-links` | `sharepoint-update-links-in-documents` | `sharepoint-link-remediation` |
| `sharepoint-remediate-links` | `sharepoint-update-page-links` | `sharepoint-link-remediation` |
| `sharepoint-remediate-field-image-references` | `sharepoint-update-rich-text-image-links` | `sharepoint-link-remediation` |
| `sharepoint-validate-link-integrity` | `sharepoint-validate-link-integrity` | `sharepoint-link-remediation` |
| `sharepoint-validate-page-migration` | `sharepoint-validate-page-modernization` | `sharepoint-page-modernization-execution` |

## Source namespaces

This package consolidates independently developed implementations. Each keeps its own flat module namespace under a
subfolder named for its original function so that same-named modules (for example `canonical_package`, `hashing`)
never collide. Skill folders live flat under `skills/`; skills reach their scripts and references through their own
file-level symlink spokes.

| Source plugin | Namespace | Scripts | Tests | References |
|---|---|---|---|---|
| `sharepoint-content-migration` | `content-migration` | yes | yes | yes |
| `sharepoint-link-remediation` | `link-remediation` | yes | yes | yes |
| `sharepoint-migration-planning` | `migration-planning` | yes | yes | yes |
| `sharepoint-page-modernization` | `page-modernization` | yes | yes | yes |
| `sharepoint-page-modernization-execution` | `page-modernization-execution` | yes |  | yes |

Original package READMEs and manifests are preserved as provenance under `references/source-packages/<source-plugin>/`.

## Running the tests

Each namespace is tested in its own process because bare-name imports (for example `import canonical_package`) are
namespace-local:

```bash
python3 plugins/sharepoint-site-migration/tests/run_namespaces.py
```

To run one namespace: `cd plugins/sharepoint-site-migration && python3 -m pytest tests/<namespace>`.

## Installing

See the repository [INSTALL.md](../../INSTALL.md). Example:

```text
/plugin install sharepoint-site-migration@sharepoint-knowledge-workbench
```
