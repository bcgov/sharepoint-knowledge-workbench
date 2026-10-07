# sharepoint-site-build-and-publish

Creates, configures and publishes SharePoint content: schema definitions (generate, scaffold,
compare) and declarative column, content-type, list/library and calendar reconciliation plans (zero
tenant I/O), real PnP.PowerShell tenant-write executors for site columns, list columns, content
types, views, items, libraries, sites, branding, navigation, permissions and taxonomy, and safe
content publication (Markdown files, modern pages, page copy plans, publication-state comparison and
removal). Every writing script is dry-run by default, gated behind -Execute plus an operation-
specific -ConfirmToken.

## Skills by functional group

### Create and configure SharePoint objects

- `sharepoint-add-list-column` -- Adds a column directly to an existing SharePoint list or library. Use when a column belongs to one list only. Dry-run by default; real writes require -Execute and confirmation token ADD-SPO-LIST-COLUMN.
- `sharepoint-add-list-item` -- Creates new list items in a SharePoint list with given field values. Use to seed or load items into an existing list. Dry-run by default; real writes require -Execute and confirmation token ADD-SPO-LIST-ITEM.
- `sharepoint-apply-provisioning-plan` -- The real PnP.PowerShell executors for sharepoint-site-build-and-publish's plan JSON, covering create, update and delete of lists, libraries, site columns and content types, content-type attach and detach, and the...
- `sharepoint-compare-schema-definitions` -- Compares schema DEFINITIONS (the declarative SiteSchemaDefinition shape) against each other, or a schema definition against an exported SchemaExport, answering what would change if a target definition were applied...
- `sharepoint-configure-column-formatting` -- Applies JSON custom column formatting and custom renderers to SharePoint fields. Use to change how a column displays. Dry-run by default; real writes require -Execute and confirmation token...
- `sharepoint-configure-library-settings` -- Configures advanced SharePoint document library version limits, content approval and draft visibility settings. Use to tune versioning and approval on a library. Dry-run by default; real writes require -Execute and...
- `sharepoint-create-content-type` -- Creates new SharePoint content types, binds field links and attaches content types to target lists. Use to define a reusable content type. Dry-run by default; real writes require -Execute and confirmation token...
- `sharepoint-create-document-library` -- Creates a new SharePoint document library (Template 101) using PnP.PowerShell. Use to add a document library to a site. Dry-run by default; real writes require -Execute and confirmation token PROVISION-SPO-LIST.
- `sharepoint-create-list` -- Creates a new SharePoint custom list (Template 100) using PnP.PowerShell. Use to add a custom list to a site. Dry-run by default; real writes require -Execute and confirmation token PROVISION-SPO-LIST.
- `sharepoint-create-list-view` -- Creates and configures custom views for SharePoint lists and document libraries. Use to add a filtered or sorted view. Dry-run by default; real writes require -Execute and confirmation token PROVISION-SPO-LIST-VIEW.
- `sharepoint-create-site-column` -- Creates new SharePoint site columns across standard or complex types (Text, Choice, Lookup, User, Calculated via Field XML). Use to define a reusable site column. Dry-run by default; real writes require -Execute and...
- `sharepoint-detach-content-type` -- Detaches and unlinks a content type from a specific SharePoint list or library. Use to stop a list using a content type without deleting it. Dry-run by default; real writes require -Execute and confirmation token...
- `sharepoint-generate-schema-definition-from-export` -- Transforms an already-loaded SharePoint schema export (site columns, content types, lists with fields) into a declarative, JSON-serializable schema definition. Use when you need a definition suitable for later...
- `sharepoint-plan-column-changes` -- Filters an exported field set down to deployable fields, detects live-type drift against a declared schema, and builds raw Field XML for column types a typed field-creation API cannot express (Calculated has no...
- `sharepoint-plan-content-type-changes` -- Plans create-if-missing SharePoint content-type provisioning from a caller-supplied declarative definition (add, hide, show and unlink field links, with hidden-flag drift against the schema surfaced rather than...
- `sharepoint-reconcile-calendar-list` -- Plans provisioning of a working modern SharePoint Online calendar list, structurally preventing a real platform bug (Start/End declared as site columns or content-type-linked fields silently breaks calendar view...
- `sharepoint-reconcile-site-schema` -- Reconciles a whole declarative SharePoint provisioning schema (site columns, content types, target lists) against caller-supplied current state, detects duplicate-titled lists before any delete, and gates any real...
- `sharepoint-remove-content-type` -- Deletes a SharePoint content type from the site collection. Use to remove an obsolete content type. Dry-run by default; real writes require -Execute and confirmation token REMOVE-SPO-CONTENT-TYPES.
- `sharepoint-remove-list` -- Deletes a SharePoint list or document library and re-checks that it is gone, failing loud if it still exists. Use to remove an obsolete list or library. Dry-run by default; real writes require -Execute and...
- `sharepoint-remove-list-column` -- Removes a list-scoped column from a SharePoint list or library. Use to drop a column from one list only. Dry-run by default; real writes require -Execute and confirmation token REMOVE-SPO-LIST-COLUMN.
- `sharepoint-remove-site-column` -- Deletes a SharePoint site column and reports each column as removed or failed. Use to remove an obsolete site column. Dry-run by default; real writes require -Execute and confirmation token REMOVE-SPO-SITE-COLUMNS.
- `sharepoint-scaffold-schema-definition` -- Scaffolds a declarative SiteSchemaDefinition JSON structure from scratch or from input parameters, without a live tenant connection. Use to author or bootstrap a new SharePoint site schema definition locally before...
- `sharepoint-update-content-type` -- Updates SharePoint content type name, description, group or hidden properties. Use to rename or reclassify a content type. Dry-run by default; real writes require -Execute and confirmation token UPDATE-SPO-CONTENT-TYPES.
- `sharepoint-update-list-column` -- Updates a list-scoped column's properties on a specific SharePoint list. Use to change one list's column. Dry-run by default; real writes require -Execute and confirmation token UPDATE-SPO-LIST-COLUMN.
- `sharepoint-update-list-settings` -- Updates SharePoint list or library title, description and versioning settings using Set-PnPList. Use to rename or reconfigure a list. Dry-run by default; real writes require -Execute and confirmation token...
- `sharepoint-update-site-column` -- Updates existing SharePoint site column properties (display name, description, required, choices) using Set-PnPField. Use to change a reusable site column. Dry-run by default; real writes require -Execute and...

### Publish and maintain SharePoint content

- `sharepoint-download-file` -- Downloads a remote document, file, or page from a SharePoint Online library or site to a local directory with existence and size verification. Zero tenant writes.
- `sharepoint-publish-html-page` -- Publishes an HTML page (.html) to a SharePoint Online document library or Site Pages library (SitePages/) with checkout/checkin discipline and post-upload presence verification. Dry-run by default; real writes require -Execute and confirmation token PUBLISH-SPO-HTML.
- `sharepoint-apply-page-publication-plan` -- Executes a PublishPlan (built by sharepoint-plan-page-publication or sharepoint-publish-markdown-files) either through an explicitly injected Python uploader or through a real PnP executor that creates and publishes...
- `sharepoint-compare-publication-state` -- Read-only comparison of an expected UploadPackage against the actual observed SharePoint library state (a CSV export), reporting missing, duplicate, mismatched or unexpected items. Use after an upload to check that...
- `sharepoint-copy-page-between-sites` -- Builds a safe, human-reviewed plan for copying or promoting an existing SharePoint Online Site Page, such as an .aspx page in Site Pages, from one SPO site to another. Use for TEST-to-PROD page promotion requests....
- `sharepoint-plan-page-publication` -- Builds a human-actionable publish plan (a PublishPlan) for rendered content as SharePoint modern pages. Use after rendering, before uploading. Performs no tenant writes and never attempts raw .aspx upload (blocked);...
- `sharepoint-publish-markdown-files` -- Builds a human-actionable publish plan mapping rendered Markdown and media files to an exact SharePoint library and folder, then a real PnP executor uploads it with Add-PnPFile and checkout/checkin discipline. Use to...
- `sharepoint-remove-publication` -- Builds a rollback plan reversing a prior publication's exact actions, scoped to one document, then a real PnP executor removes each target (Remove-PnPPage or Remove-PnPFile) with fail-loud removal verification. Use...
- `sharepoint-validate-publication` -- Offline pre-upload schema validation of an UploadPackage against the target library schema, plus a read-only post-deployment presence check (Get-PnPPage or Get-PnPFile) confirming that a PublishPlan's targets landed...

## Plugin structure

Shared scripts and references live at the plugin root in namespace folders; each skill links to them with file-level symlinks.

```text
sharepoint-site-build-and-publish/
├── .claude-plugin/plugin.json   # Plugin manifest
├── agents/                      # Plugin agent definitions
├── docs/                        # Plugin documentation
├── references/                  # References and acceptance criteria by namespace
│   ├── content-publication/
│   ├── provisioning/
│   ├── schema-reconciliation/
│   └── source-packages/
├── rules/                       # Plugin rules
├── scripts/                     # Canonical implementation by namespace
│   ├── calendar-executor/
│   ├── content-publication/
│   ├── provisioning/
│   └── schema-reconciliation/
├── skills/<skill-name>/         # SKILL.md plus symlinked scripts/ and references/
├── tests/                       # Namespace test suites (run via tests/run_namespaces.py)
├── plugin.json
├── plugin.yaml
└── pyproject.toml
```

## Previous identities

Skill and plugin names changed in the seven-domain migration (issue #6). Old names are not retained as aliases.

| Previous skill | Current skill | Previous plugin |
|---|---|---|
| `sharepoint-add-list-column` | `sharepoint-add-list-column` | `sharepoint-provisioning` |
| `sharepoint-add-list-item` | `sharepoint-add-list-item` | `sharepoint-provisioning` |
| `sharepoint-upload-content` | `sharepoint-apply-page-publication-plan` | `sharepoint-content-publication` |
| `sharepoint-apply-provisioning-plan` | `sharepoint-apply-provisioning-plan` | `sharepoint-provisioning` |
| `sharepoint-reconcile-sharepoint-publication` | `sharepoint-compare-publication-state` | `sharepoint-content-publication` |
| `sharepoint-diff-sharepoint-schema` | `sharepoint-compare-schema-definitions` | `sharepoint-discovery` |
| `sharepoint-configure-column-formatting` | `sharepoint-configure-column-formatting` | `sharepoint-provisioning` |
| `sharepoint-configure-library-settings` | `sharepoint-configure-library-settings` | `sharepoint-provisioning` |
| `sharepoint-copy-page-between-sites` | `sharepoint-copy-page-between-sites` | `sharepoint-page-modernization-execution` |
| `sharepoint-create-content-type` | `sharepoint-create-content-type` | `sharepoint-provisioning` |
| `sharepoint-create-document-library` | `sharepoint-create-document-library` | `sharepoint-provisioning` |
| `sharepoint-create-list` | `sharepoint-create-list` | `sharepoint-provisioning` |
| `sharepoint-create-list-view` | `sharepoint-create-list-view` | `sharepoint-provisioning` |
| `sharepoint-create-site-column` | `sharepoint-create-site-column` | `sharepoint-provisioning` |
| `sharepoint-detach-content-type` | `sharepoint-detach-content-type` | `sharepoint-provisioning` |
| `sharepoint-generate-sharepoint-schema-from-export` | `sharepoint-generate-schema-definition-from-export` | `sharepoint-discovery` |
| `sharepoint-provision-fields` | `sharepoint-plan-column-changes` | `sharepoint-schema-reconciliation` |
| `sharepoint-provision-content-types` | `sharepoint-plan-content-type-changes` | `sharepoint-schema-reconciliation` |
| `sharepoint-publish-aspx-to-sharepoint` | `sharepoint-plan-page-publication` | `sharepoint-content-publication` |
| `sharepoint-publish-markdown-to-sharepoint` | `sharepoint-publish-markdown-files` | `sharepoint-content-publication` |
| `sharepoint-provision-modern-calendar-list` | `sharepoint-reconcile-calendar-list` | `sharepoint-schema-reconciliation` |
| `sharepoint-provision-list` | `sharepoint-reconcile-site-schema` | `sharepoint-schema-reconciliation` |
| `sharepoint-remove-content-type` | `sharepoint-remove-content-type` | `sharepoint-provisioning` |
| `sharepoint-remove-list` | `sharepoint-remove-list` | `sharepoint-provisioning` |
| `sharepoint-remove-list-column` | `sharepoint-remove-list-column` | `sharepoint-provisioning` |
| `sharepoint-rollback-sharepoint-publication` | `sharepoint-remove-publication` | `sharepoint-content-publication` |
| `sharepoint-remove-site-column` | `sharepoint-remove-site-column` | `sharepoint-provisioning` |
| `sharepoint-scaffold-schema-definition` | `sharepoint-scaffold-schema-definition` | `sharepoint-discovery` |
| `sharepoint-update-content-type` | `sharepoint-update-content-type` | `sharepoint-provisioning` |
| `sharepoint-update-list-column` | `sharepoint-update-list-column` | `sharepoint-provisioning` |
| `sharepoint-update-list-settings` | `sharepoint-update-list-settings` | `sharepoint-provisioning` |
| `sharepoint-update-site-column` | `sharepoint-update-site-column` | `sharepoint-provisioning` |
| `sharepoint-validate-publication` | `sharepoint-validate-publication` | `sharepoint-content-publication` |

## Source namespaces

This package consolidates independently developed implementations. Each keeps its own flat module namespace under a
subfolder named for its original function so that same-named modules (for example `canonical_package`, `hashing`)
never collide. Skill folders live flat under `skills/`; skills reach their scripts and references through their own
file-level symlink spokes.

| Source plugin | Namespace | Scripts | Tests | References |
|---|---|---|---|---|
| `sharepoint-migration-planning` | `calendar-executor` | yes |  |  |
| `sharepoint-content-publication` | `content-publication` | yes | yes | yes |
| `sharepoint-provisioning` | `provisioning` | yes |  | yes |
| `sharepoint-schema-reconciliation` | `schema-reconciliation` | yes | yes | yes |

Original package READMEs and manifests are preserved as provenance under `references/source-packages/<source-plugin>/`.

## Running the tests

Each namespace is tested in its own process because bare-name imports (for example `import canonical_package`) are
namespace-local:

```bash
python3 plugins/sharepoint-site-build-and-publish/tests/run_namespaces.py
```

To run one namespace: `cd plugins/sharepoint-site-build-and-publish && python3 -m pytest tests/<namespace>`.

## Installing

See the repository [INSTALL.md](../../INSTALL.md). Example:

```text
/plugin install sharepoint-site-build-and-publish@sharepoint-knowledge-workbench
```
