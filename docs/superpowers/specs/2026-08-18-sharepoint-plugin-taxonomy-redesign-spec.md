# SharePoint Plugin & Skill Taxonomy Redesign — Target State Spec

**Status: APPROVED TARGET STATE (2026-08-18) — incorporates complete domain standardization (`content-*`, `sharepoint-*`, `workbench-*`), all confirmed capability gaps, and real-world enterprise SharePoint operations.**

## Why this exists

A 2026-08-18 session found that several plugin/skill names in this repo's SharePoint domain
actively lied about what they do: `sharepoint-provisioning` shipped zero tenant writes despite its
name, while a real PnP executor (`spo-provision-calendar.ps1`) sat stranded inside
`sharepoint-migration-planning`, a plugin whose entire naming contract is "produce information
only." An independent audit then caught stray executors elsewhere and missing essential operations
required for production SharePoint projects.

Every merge/split/prefix/gap-fill decision below follows three core principles:

1. **Structure vs. Content** — defining the *shape* of a site (lists, columns, content types,
   permissions, navigation, term sets, hub associations) is a categorically different operation than
   filling it with *data* (item rows, pages, files).
2. **Domain Prefix Standardization** — every plugin and every skill follows its exact domain namespace:
   - `content-*` for the 4 core local document intake/structuring/rendering pipeline plugins and skills.
   - `sharepoint-*` for all SharePoint tenant operations, discovery, provisioning, publication, and migration.
   - `workbench-*` for environment setup, configuration, and app registration.
3. **Install-only-what-you-need** — a plugin that only makes sense when migrating an *existing*
   legacy site must not be merged into a plugin a greenfield ("build a brand-new site") user would
   also need.

---

## Domain Taxonomy & Namespace Map

### 1. Content Processing Domain (`content-*`)
Pure local file operations (Word/PDF $\rightarrow$ Canonical $\rightarrow$ Markdown/ASPX). Zero SharePoint tenant I/O.
- **`content-extraction`** (renamed from `source-document-extraction`)
  - `content-extract-docx`: Run pandoc against source `.docx` and produce normalized document contract.
- **`content-structure-analysis`** (renamed from `document-structure-analysis`)
  - `content-analyze-structure`: Structural analysis, heading hierarchy, defect detection.
- **`content-assembly`** (renamed from `structured-content-assembly`)
  - `content-assemble-package`: Chunking, canonicalization, validation, and package promotion.
- **`content-rendering`** (renamed from `structured-content-rendering`)
  - `content-render-markdown`: Multipage Markdown renderer.
  - `content-render-aspx`: Modern SharePoint ASPX renderer.
  - `content-validate-rendered-output`: Validate rendered Markdown/ASPX packages.
  - `content-compare-rendered-output`: Compare rendered output against golden masters.
  - `content-create-markdown-template`: Template authoring for Markdown.
  - `content-create-aspx-template`: Template authoring for ASPX.
  - `content-validate-rendering-template`: Template conformance validation.

### 2. SharePoint Operations Domain (`sharepoint-*`)
All tenant interactions (reading, planning, executing, modernizing, publishing, migrating).

#### A. Discovery & Schema Inspection
- **`sharepoint-discovery`** (absorbs `sharepoint-schema`; zero-I/O analysis + live read-only inspection)
  - `sharepoint-collect-inventory`: Live site inventory collection.
  - `sharepoint-audit-schema`: Live schema auditing.
  - `sharepoint-diff-schema`: Schema comparison between sites or exports.
  - `sharepoint-extract-calculated-columns`: Formula extraction & dependency checks.
  - `sharepoint-extract-choice-fields`: Choice and MultiChoice options inventory.
  - `sharepoint-generate-schema-from-export`: Transform export into declarative schema definition.
  - `sharepoint-scaffold-schema-definition` **[NEW]**: Authors a target `SiteSchemaDefinition` from scratch.
  - `sharepoint-analyze-page-inventory`: Classic/modern page inventory classification.
  - `sharepoint-analyze-permissions`: Unique permissions & role assignment audits.
  - `sharepoint-analyze-site-navigation`: Structural quicklaunch/top-nav audits.
  - `sharepoint-analyze-webpart-code`: Web part script/markup grouping.
  - `sharepoint-analyze-custom-forms`: Infopath/custom form detection.
  - `sharepoint-audit-managed-metadata`: Term store & taxonomy binding discovery.
  - `sharepoint-audit-onprem-schema-drift`: SP2016 vs SPO drift detection.
  - `sharepoint-generate-discovery-reports`: Consolidate multi-skill audit results into reports.

#### B. Schema Planning & Reconciliation (Zero-I/O)
- **`sharepoint-schema-reconciliation`** (renamed from old `sharepoint-provisioning`; plans only, zero tenant writes)
  - `sharepoint-plan-list-reconciliation`: Plan list creation/deletion diffs.
  - `sharepoint-plan-field-reconciliation`: Plan site column diffs.
  - `sharepoint-plan-content-type-reconciliation`: Plan content type additions/attachments.
  - `sharepoint-plan-calendar-reconciliation`: Plan modern calendar list definitions.

#### C. Tenant Provisioning & Execution (Real PnP Writes)
- **`sharepoint-provisioning`** (renamed from `sharepoint-provisioning-execution`; executes approved plans)
  - `sharepoint-apply-provisioning-plan`: Monolithic dispatcher & executor suite for all tenant writes:
    - Lists & Columns: `spo-provision-list.ps1`, `spo-update-list.ps1`, `spo-provision-site-columns.ps1`, `spo-update-site-column.ps1`, `spo-remove-site-column.ps1`, `spo-add-list-column.ps1`, `spo-update-list-column.ps1`, `spo-remove-list-column.ps1`, `spo-provision-list-view.ps1` **[NEW]**
    - Content Types: `spo-provision-content-types.ps1`, `spo-update-content-type.ps1`, `spo-remove-content-type.ps1`, `spo-detach-content-type-from-list.ps1`
    - Sites & Governance: `spo-provision-site.ps1` **[NEW]**, `spo-provision-branding.ps1` **[NEW]**, `spo-manage-hub-site.ps1` **[NEW]**, `spo-configure-library-settings.ps1` **[NEW]**
    - Pages & Webparts: `spo-create-modern-page.ps1` **[NEW]**, `spo-configure-webparts.ps1` **[NEW]**
    - Security & Formatting: `spo-provision-permissions.ps1` **[NEW]**, `spo-configure-item-permissions.ps1` **[NEW]**, `spo-configure-column-formatting.ps1` **[NEW]**
    - Navigation, Taxonomy, & Indexing: `spo-provision-navigation.ps1` **[NEW]**, `spo-provision-term-set.ps1` **[NEW]**, `spo-provision-calendar.ps1` (moved), `spo-trigger-reindex.ps1` **[NEW]**
    - Data Seeding: `spo-add-list-item.ps1` **[NEW]**

#### D. Content Publication & Delivery
- **`sharepoint-content-publication`** (packages and uploads rendered content packages to SPO)
  - `sharepoint-plan-aspx-publication`: Plan ASPX modern page delivery (plan-only).
  - `sharepoint-publish-markdown`: Plan and deploy multipage Markdown + media.
  - `sharepoint-upload-content`: Generic publication plan execution via PnP uploader.
  - `sharepoint-reconcile-publication`: Post-upload reconciliation against expected state.
  - `sharepoint-rollback-publication`: Safe reversal/recycling of published assets.
  - `sharepoint-validate-publication`: Pre-flight and post-deployment presence checks.

#### E. Content & Attachment Migration
- **`sharepoint-content-migration`** (migrates legacy data, items, attachments, files)
  - `sharepoint-migrate-list-content`: Migrate list items with 2-pass lookup ID relinking.
  - `sharepoint-migrate-library-files` **[NEW]**: Migrate document library files, folders, and attachments.
  - Principal & Taxonomy term mapping utilities (`mapping_utils.py`) **[NEW]**.

#### F. Page Modernization (Classic $\rightarrow$ Modern)
- **`sharepoint-page-modernization`** (plan only, zero I/O)
  - `sharepoint-analyze-aspx-pages`: Parse classic web part pages & extract zones.
  - `sharepoint-map-aspx-to-modern-layout`: Map web parts to modern layouts/components.
  - `sharepoint-compose-page-preview`: Compose offline preview HTML.
  - `sharepoint-generate-conversion-report`: Summary matrix of page modernization readiness.
- **`sharepoint-page-modernization-execution`** [NEW PLUGIN] (executes modern conversions)
  - `sharepoint-convert-page-to-modern`: Single page conversion (`ConvertTo-PnPPage`).
  - `sharepoint-execute-bulk-page-conversion`: Subprocess-orchestrated bulk page migration.
  - `sharepoint-validate-page-conversion`: Post-conversion field and layout verification.
  - `sharepoint-copy-page-between-sites`: Cross-site modern page promotion.

#### G. Link Remediation
- **`sharepoint-link-remediation`** (rewrite and repair legacy URLs)
  - `sharepoint-extract-links`: Inventory URLs from HTML, ASPX, and Markdown.
  - `sharepoint-remediate-links`: Rewrite links via declarative ruleset.
  - `sharepoint-remediate-document-links`: Remediate links inside structured workbench packages.
  - `sharepoint-remediate-field-image-references`: Remediate image paths in list item HTML fields.
  - `sharepoint-validate-link-integrity`: Final link health & 404 verification.

#### H. Migration Wave Planning
- **`sharepoint-migration-planning`** (sequencing & deployment waves)
  - `sharepoint-analyze-dependency-graph`: Build DAG of lists, content types, and lookups.
  - `sharepoint-discover-site-inventory`: Validate input inventory completeness.
  - `sharepoint-plan-deployment-waves`: Partition schema & content into executable waves.
  - `sharepoint-generate-wave-scripts`: Emit deterministic PnP orchestrator scripts.
  - `sharepoint-setup-migration-project`: Initialize migration workspace structure.

#### I. Agents & Skills
- **`sharepoint-agents-and-skills`** (Copilot agent authoring & Native AgentAssets skill deployment)
  - `sharepoint-create-agent`, `sharepoint-update-agent`, `sharepoint-backup-agents`, `sharepoint-restore-agents`
  - `sharepoint-configure-agent-knowledge`, `sharepoint-create-agent-template`, `sharepoint-apply-agent-template`
  - `sharepoint-create-native-skill`, `sharepoint-deploy-native-skill`, `sharepoint-verify-native-skill`
  - `sharepoint-backup-native-skills`, `sharepoint-restore-native-skills`, `sharepoint-rollback-native-skill`
  - `sharepoint-inventory-agentassets`, `sharepoint-review-manual-topics`

#### J. SPFx Development
- **`sharepoint-spfx-authoring`** (SPFx scaffolding, packaging, and catalog deployment)
  - `sharepoint-scaffold-spfx-webpart`
  - `sharepoint-scaffold-spfx-master-detail`
  - `sharepoint-package-spfx-solution`
  - `sharepoint-deploy-spfx-solution`
  - `sharepoint-request-site-collection-app-catalog`

---

### 3. Workbench Environment Domain (`workbench-*`)
- **`workbench-setup`**
  - `workbench-validate-environment`
  - `workbench-resolve-paths`
  - `workbench-request-app-registration`

---

## Summary of Structural & Inventory Changes

1. **Total Plugins**: 16 plugins (4 `content-*`, 11 `sharepoint-*`, 1 `workbench-*`).
2. **Standardized Prefixes**: Every single skill adopts its parent domain prefix (`content-*`, `sharepoint-*`, or `workbench-*`).
3. **Confirmed Defects & Gaps Resolved**:
   - `sharepoint-schema` merged into `sharepoint-discovery`.
   - `sharepoint-provisioning` (old) renamed to `sharepoint-schema-reconciliation`, with hardened purity tests.
   - `sharepoint-provisioning-execution` renamed to `sharepoint-provisioning`, gaining all real-world gap-fill PnP scripts (site creation, branding, hub sites, modern pages, webparts, views, library settings, item permissions, taxonomy, reindexing).
   - `sharepoint-page-modernization-execution` cleanly separated from `sharepoint-content-publication`.
   - Stale `.claude-plugin/marketplace.json` entries and doc claims fully repaired.
   - All Hub-and-Spoke symlinks updated and verified via `symlink_manager.py`.
