# Architecture Note: Standardizing Tenancy Rollouts via Canonical Workbench Skills

> **Research note, not a current command catalog.** This document records rollout
> findings and proposed standards from an earlier repository state. Plugin names and
> ownership below may have changed. For current installable package names and skill
> identities, use the [seven-domain catalog](../../architecture/seven-domain-plugin-skill-catalog.md)
> and each plugin's current `SKILL.md`; do not copy old command paths from this note.

## 1. Context & Problem
During the trial tenancy deployment of custom SPFx web parts (e.g. a "favorite apps" web part), ad-hoc PowerShell scripts were temporarily generated under `temp/trialtenancy/*/scripts/` for list provisioning, data seeding, and view configuration.

While functional, generating throwaway scripts creates:
- Code duplication across test runs and projects.
- Drift from the 16 standard domain plugins (`plugins/*`).
- Missed opportunities to stress-test and improve the repository's built-in declarative skills.

## 2. Core Architectural Principle
**Every SharePoint operation should flow through the repository's canonical skills (`plugins/*`) using declarative manifests or standardized CLI parameters, rather than one-off custom scripts.**

## 3. Standardized Mapping Matrix

| Capability Needed | Legacy Ad-hoc Approach | Canonical Plugin Skill Pattern |
| :--- | :--- | :--- |
| **List & Schema Provisioning** | Custom `01-provision-prereq-lists.ps1` | `sharepoint-site-build-and-publish` / `sharepoint-apply-provisioning-plan`<br>Pass a declarative schema definition specifying lists, fields, and types. |
| **List Views & Sorting** | Custom `01c-configure-applications-view.ps1` | `sharepoint-create-list-view`<br>Run `spo-provision-list-view.ps1 -PlanPath <view-plan.json> -Execute -ConfirmToken PROVISION-SPO-LIST-VIEW`. |
| **Sample Data & Content Seeding** | Custom `02-seed-sample-data.ps1` | `sharepoint-site-migration` for migration; `sharepoint-site-build-and-publish` for adding items. Confirm the current skill interface before use. |
| **SPFx Solution Packaging & Deploy** | Custom `04-publish-sppkg.ps1` | `sharepoint-publish-spfx-package`<br>Run `publish-spfx-package.ps1 -PackagePath <path> -Scope Site/Tenant -ConfigPath <config.psd1>`. |

## 4. Universal Parameter & Execution Standards for Canonical Skills

To ensure any canonical skill script can be executed across different environments without writing throwaway wrapper scripts, every script in `plugins/*` must conform to the following standards:

### 4.1. Universal Parameter Interface
1. **Dual Configuration Resolution**:
   - **Default Mode**: Automatically resolve connection parameters from active `config.psd1` (via robust multi-tier probing).
   - **Explicit Mode**: Accept optional command-line overrides (`-SiteUrl`, `-TenantAdminUrl`, `-ClientId`, `-TenantId`, `-ConfigPath`) so skills can run against any target site without modifying `config.psd1`.
2. **Lifecycle & Prerequisite Automation Switches**:
   - **`-Install` / `-Activate`**: When deploying assets/packages to a site scope, auto-install them into the site so they immediately appear in SharePoint toolboxes.
   - **`-Ensure<Prerequisite>`** (e.g. `-EnsureSiteAppCatalog`): Auto-provision underlying containers/catalogs if they do not yet exist.
   - **`-SkipFeatureDeployment`**: Enable tenant-wide instant deployment for tenant-scoped packages.
3. **Safe Mutation Discipline**:
   - Gated behind `-Execute` and specific confirmation tokens (e.g. `-ConfirmToken PROVISION-SPO-LIST`) with default dry-run mode for all destructive or provisioning operations.

---

## 5. SKILL.md Authoritative Documentation Requirements

Every `SKILL.md` under `plugins/*/skills/*/` and `.agents/skills/*/` must provide explicit, copy-pasteable PowerShell calling examples covering at least 4 scenarios:

1. **Standard Automated Flow** (Recommended config-driven run):
   ```powershell
   pwsh -File plugins/<plugin>/scripts/<script>.ps1 -Scope Site -Install
   ```
2. **First-Time / Self-Healing Setup** (Ensuring prerequisites):
   ```powershell
   pwsh -File plugins/<plugin>/scripts/<script>.ps1 -Scope Site -EnsureSiteAppCatalog -Install
   ```
3. **Enterprise / Tenant Scope** (Tenant admin execution):
   ```powershell
   pwsh -File plugins/<plugin>/scripts/<script>.ps1 -Scope Tenant -SkipFeatureDeployment
   ```
4. **Explicit Connection Overrides** (Zero `config.psd1` dependency):
   ```powershell
   pwsh -File plugins/<plugin>/scripts/<script>.ps1 `
     -SiteUrl "https://tenant.sharepoint.com/sites/target" `
     -ClientId "<id>" -TenantId "<id>" -Install
   ```

---

## 6. SPFx Naming & Identity Architecture Standard

All SPFx authoring and deployment tooling must document and handle the 4 distinct naming layers:

| Layer | Configuration File | Purpose & UI Location | Example |
| :--- | :--- | :--- | :--- |
| **Package File** | `config/package-solution.json` (`paths.zippedPackage`) | Physical `.sppkg` file name generated in `sharepoint/solution/`. | `my-fav-apps-dev.sppkg` |
| **Solution Name** | `config/package-solution.json` (`solution.name`) | Display title in **App Catalog** and **Site Contents > Add an App**. | `my-favorite-apps-dev` |
| **Solution Version** | `config/package-solution.json` (`solution.version`) | Semantic version string (`1.0.7.0`) triggering SharePoint upgrade prompts. | `1.0.7.0` |
| **Web Part Selector Title** | `*WebPart.manifest.json` (`preconfiguredEntries[0].title.default`) | 🌟 **The actual name displayed to authors in the SharePoint page `+` toolbox selector.** | `My Applications` |
| **Toolbox Category** | `*WebPart.manifest.json` (`preconfiguredEntries[0].group.default`) | Category heading in the toolbox. | `Advanced` |

---

## 7. Discovered PnP.PowerShell Cmdlet Inaccuracies in Plugin Scripts (Audit Findings)

During real tenant validation, the following cmdlet discrepancies were identified and flagged for remediation across the repository skills:

1. **`Publish-PnPPage` vs `Set-PnPPage -Publish`**:
   - **Discrepancy**: PnP.PowerShell has no standalone `Publish-PnPPage` cmdlet. Publishing a modern page requires `Set-PnPPage -Identity "<page>" -Publish` (or `Save-PnPPage -Publish`).
   - **Affected plugin files**:
     - `plugins/sharepoint-site-build-and-publish/scripts/content-publication/spo-publish-modern-page.ps1` (Line 131)
     - `plugins/sharepoint-site-build-and-publish/scripts/content-publication/sharepoint_upload.py`
     - Associated `SKILL.md` docstrings.

2. **`Set-PnPView -Query` Parameter**:
   - **Discrepancy**: `Add-PnPView` accepts `-Query`, but `Set-PnPView` does not support `-Query` directly. Modifying CAML queries on existing views requires setting `$view.ViewQuery` and executing `Invoke-PnPQuery`.
   - **Affected plugin files**:
     - `plugins/sharepoint-site-build-and-publish/scripts/provisioning/spo-provision-list-view.ps1`

3. **`config.psd1` Relative Path Resolution**:
   - **Discrepancy**: Scripts assuming `$PSScriptRoot/../../../../config.psd1` fail when executed from repo root if using `Resolve-Path` directly without probing `$PWD` and fallback candidates.
   - **Affected plugin files**: Ensure all skills use multi-tier path probing consistently.

---

## 8. Planned Next Steps / Backlog Items
1. **Audit & Patch Skill Scripts**: Fix `Publish-PnPPage` and `Set-PnPView` across `plugins/sharepoint-site-build-and-publish` and `plugins/sharepoint-site-build-and-publish`.
2. **Apply Universal Parameter Pattern to All 16 Plugins**: Update all plugin provisioning and migration scripts to support explicit parameter overrides (`-SiteUrl`, `-ClientId`, etc.) alongside `config.psd1`.
3. **Scaffold Generic Manifest Generators**: This is a proposal from the research period, not a claim about current capability. Check the setup and site-build-and-publish plugin inventories before planning work.
4. **Unified Rollout Orchestrator**: Create a generic declarative wave orchestrator (`sharepoint-plan-sharepoint-deployment-waves`) that executes pre-flight connectivity -> schema provisioning -> asset upload -> package publication -> view creation in sequence.

---

## 9. Canonical Script Alignment Checklist & Progress Tracker

Every `.ps1` script across the 16 plugins will be aligned using the 3-step standard:
1. **Read full script**: Inspect current parameter declarations, config loading logic, and PnP cmdlet calls.
2. **Analyze alignment**: Add explicit parameter overrides (`-SiteUrl`, `-ClientId`, `-TenantId`, `-ConfigPath`), prerequisite/lifecycle switches (`-Install`, `-Ensure...`), multi-tier path probing, and verify correct PnP cmdlet syntax.
3. **Update script & skill**: Update script, sync `.agents/skills` mirror, verify tests, and check off the item.

### 9.1. `plugins/sharepoint-spfx-development`
- [x] `publish-spfx-package.ps1` — Supports `-Scope Site/Tenant`, `-Install`, `-EnsureSiteAppCatalog`, `-SkipFeatureDeployment`, explicit overrides, and multi-tier config resolution.
- [x] `package-spfx-solution.ps1` — Supports auto-install of missing `node_modules`, hermetic `npm run build` invocation, and `.sppkg` non-zero validation.
- [x] `deploy-spfx-package.ps1` — Aligned parameters with `publish-spfx-package.ps1` (supports `-Scope`, `-Install`, `-EnsureSiteAppCatalog`, dual-mode config).
- [ ] `check-spfx-toolchain.ps1` — Verify Node.js v18/v22 and SPFx toolchain checks.

### 9.2. `plugins/sharepoint-site-build-and-publish`
- [x] `spo-provision-list-view.ps1` — Fixed `Set-PnPView` / `Add-PnPView` handling, updated CSOM `$view.ViewQuery` + `Invoke-PnPQuery`, and added proper `finally { Disconnect-PnPOnline }`.
- [ ] `apply-provisioning-plan.ps1` — Add explicit connection parameter overrides and multi-tier config resolution.
- [ ] `spo-provision-list.ps1` — Add explicit connection parameter overrides and confirmation gating.
- [ ] `spo-provision-fields.ps1` — Add explicit connection parameter overrides.
- [ ] `spo-provision-content-types.ps1` — Add explicit connection parameter overrides.
- [ ] `spo-remove-list.ps1` — Add explicit connection parameter overrides and fail-loud post-deletion check.
- [ ] `spo-remove-list-column.ps1` — Add explicit connection parameter overrides.
- [ ] `spo-remove-site-column.ps1` — Add explicit connection parameter overrides.
- [ ] `spo-remove-content-type.ps1` — Add explicit connection parameter overrides.
- [ ] `spo-update-list-settings.ps1` — Add explicit connection parameter overrides.
- [ ] `spo-update-list-column.ps1` — Add explicit connection parameter overrides.
- [ ] `spo-update-site-column.ps1` — Add explicit connection parameter overrides.
- [ ] `spo-update-content-type.ps1` — Add explicit connection parameter overrides.
- [ ] `spo-configure-library-settings.ps1` — Add explicit connection parameter overrides.
- [ ] `spo-configure-column-formatting.ps1` — Add explicit connection parameter overrides.
- [ ] `spo-detach-content-type.ps1` — Add explicit connection parameter overrides.

### 9.3. `plugins/sharepoint-site-build-and-publish`
- [x] `spo-publish-modern-page.ps1` — Replaced invalid `Publish-PnPPage` with `Set-PnPPage -Identity "<page>" -Publish` and added `finally { Disconnect-PnPOnline }`.
- [ ] `spo-upload-file.ps1` — Add explicit connection overrides and verify checkout/checkin discipline.
- [ ] `spo-validate-publication-deployment.ps1` — Add explicit connection parameter overrides.
- [ ] `spo-rollback-publication.ps1` — Add explicit connection parameter overrides.
- [ ] `Get-WorkbenchConnectionConfig.ps1` — Ensure multi-tier path probing (`$PWD`, parent directories).

### 9.4. `plugins/sharepoint-site-migration`
- [ ] `spo-migrate-list-items.ps1` — Add `Microsoft.SharePoint.Client.FieldUrlValue` formatting support and explicit connection overrides.
- [ ] `spo-migrate-library-files.ps1` — Add explicit connection overrides and binary verification.
- [ ] `Get-WorkbenchConnectionConfig.ps1` — Multi-tier path probing alignment.

### 9.5. `plugins/sharepoint-site-assessment`
- [ ] `collect-sharepoint-inventory.ps1` — Add explicit connection overrides.
- [ ] `collect-sharepoint-schema-export.ps1` — Add explicit connection overrides.
- [ ] `collect-sharepoint-page-inventory.ps1` — Add explicit connection overrides.
- [ ] `collect-sharepoint-custom-forms.ps1` — Add explicit connection overrides.
- [ ] `collect-sharepoint-permissions.ps1` — Add explicit connection overrides.
- [ ] `collect-sharepoint-site-navigation.ps1` — Add explicit connection overrides.
- [ ] `collect-sharepoint-webpart-content.ps1` — Add explicit connection overrides.
- [ ] `audit-sharepoint-managed-metadata.ps1` — Add explicit connection overrides.
- [ ] `audit-onprem-sharepoint-managed-metadata.ps1` — Add legacy authentication parameter overrides.
- [ ] `audit-onprem-sharepoint-schema-drift.ps1` — Add parameter overrides.
- [ ] `collect-onprem-sharepoint-inventory.ps1` — Add legacy authentication parameter overrides.
- [ ] `collect-onprem-sharepoint-aspx-pages.ps1` — Add legacy authentication parameter overrides.
- [ ] `generate-sharepoint-discovery-report-set.ps1` — Add path resolution robustness.

### 9.6. `plugins/sharepoint-site-migration`
- [ ] `spo-convert-page-to-modern.ps1` — Verify `ConvertTo-PnPPage` parameter alignment and explicit overrides.
- [ ] `spo-execute-page-bulk-migration.ps1` — Add explicit connection overrides and progress manifest resume support.
- [ ] `spo-validate-page-migration.ps1` — Add explicit connection overrides and fail-loud reporting.
- [ ] `spo-copy-page-between-sites.ps1` — Add explicit source and destination connection parameter overrides.

### 9.7. `plugins/sharepoint-copilot-agents-and-skills`
- [ ] `deploy-and-verify-skill.ps1` — Add explicit connection parameter overrides and SHA-256 readback check.
- [ ] `reconcile-deployed-skill.ps1` — Add explicit connection parameter overrides.
- [ ] `rollback-skill-deployment.ps1` — Add explicit connection parameter overrides and recycle bin discipline.
- [ ] `backup-sharepoint-native-skills.ps1` — Add explicit connection parameter overrides.
- [ ] `restore-sharepoint-native-skills.ps1` — Add explicit connection parameter overrides.
- [ ] `provision-agentassets.ps1` — Add explicit connection parameter overrides.
- [ ] `verify-agentassets-ready.ps1` — Add explicit connection parameter overrides.
- [ ] `verify-agentassets-artifact.ps1` — Add explicit connection parameter overrides.
- [ ] `diagnose-sharepoint-library.ps1` — Add explicit connection parameter overrides.
- [ ] `inventory-skills.ps1` — Add explicit connection parameter overrides.
- [ ] `configure-sharepoint-agent-knowledge.ps1` — Add explicit connection parameter overrides.
- [ ] `get-agent-resource-identifiers.ps1` — Add explicit connection parameter overrides.
- [ ] `backup-sharepoint-agents.ps1` — Add explicit connection parameter overrides.
- [ ] `restore-sharepoint-agents.ps1` — Add explicit connection parameter overrides.
- [ ] `create-sharepoint-agent.ps1` — Local package authoring verification.
- [ ] `create-sharepoint-agent-template.ps1` — Local template authoring verification.
- [ ] `apply-sharepoint-agent-template.ps1` — Local transform verification.
- [ ] `update-sharepoint-agent.ps1` — Local package update verification.
- [ ] `create-sharepoint-native-skill.ps1` — Local skill authoring verification.

### 9.8. `plugins/sharepoint-workbench-setup`
- [ ] `test-spo-connection.ps1` — Verify connection reporting across delegated vs app-only modes.
- [ ] `init-workbench-config.ps1` — Profile template generator alignment.
- [ ] `resolve-workbench-paths.ps1` — Path resolution alignment.
- [ ] `request-app-registration.ps1` — Guidance and script alignment.
- [ ] `initialize-document-workflow.ps1` — Workflow scaffolding alignment.

---

## 10. SKILL.md Calling Pattern & Parameter Awareness Alignment

Following the update of underlying `.ps1` scripts, every `SKILL.md` file in each skill folder (both under `plugins/<plugin>/skills/<skill>/SKILL.md` and their `.agents/skills/<skill>/SKILL.md` mirrors) must be updated to document the new parameter interface and calling examples:

### 10.1. Required Sections in Every `SKILL.md`
1. **Parameter Reference Table**:
   - Complete table listing all parameters (`-SiteUrl`, `-TenantAdminUrl`, `-ClientId`, `-TenantId`, `-ConfigPath`, `-Install`, `-Ensure...`, `-Execute`, `-ConfirmToken`, `-OutputPath`).
2. **Four Standardized Calling Examples**:
   - Example 1: Standard automated execution (default `config.psd1` resolution).
   - Example 2: Self-healing prerequisite execution (e.g. `-EnsureSiteAppCatalog -Install`).
   - Example 3: Enterprise / Tenant-wide execution (e.g. `-Scope Tenant -SkipFeatureDeployment`).
   - Example 4: Direct parameter overrides (zero `config.psd1` dependency for ad-hoc / multi-tenant execution).
3. **Dry-Run vs. Execution Safety Gates**:
   - Clear documentation of dry-run output vs. the exact `-ConfirmToken <TOKEN>` required for mutation.

### 10.2. SKILL.md Update Checklist
- [x] `plugins/sharepoint-spfx-development/skills/sharepoint-publish-spfx-package/SKILL.md` — Updated with 4 calling examples, naming matrix, and site activation instructions.
- [x] `plugins/sharepoint-spfx-development/skills/sharepoint-package-spfx-solution/SKILL.md` — Updated with dependency rules, versioning discipline, and naming matrix.
- [x] `plugins/sharepoint-spfx-development/skills/sharepoint-scaffold-spfx-webpart/SKILL.md` — Updated with naming matrix and toolbox title distinction.
- [ ] `plugins/sharepoint-spfx-development/skills/sharepoint-deploy-spfx-solution/SKILL.md`
- [ ] `plugins/sharepoint-site-build-and-publish/skills/sharepoint-create-list-view/SKILL.md`
- [ ] `plugins/sharepoint-site-build-and-publish/skills/sharepoint-create-list/SKILL.md`
- [ ] `plugins/sharepoint-site-build-and-publish/skills/sharepoint-create-document-library/SKILL.md`
- [ ] `plugins/sharepoint-site-build-and-publish/skills/sharepoint-create-site-column/SKILL.md`
- [ ] `plugins/sharepoint-site-build-and-publish/skills/sharepoint-create-content-type/SKILL.md`
- [ ] `plugins/sharepoint-site-build-and-publish/skills/sharepoint-apply-provisioning-plan/SKILL.md`
- [ ] `plugins/sharepoint-site-build-and-publish/skills/sharepoint-plan-page-publication/SKILL.md`
- [ ] `plugins/sharepoint-site-build-and-publish/skills/sharepoint-publish-markdown-files/SKILL.md`
- [ ] `plugins/sharepoint-site-build-and-publish/skills/sharepoint-apply-page-publication-plan/SKILL.md`
- [ ] `plugins/sharepoint-site-build-and-publish/skills/sharepoint-validate-publication/SKILL.md`
- [ ] `plugins/sharepoint-site-build-and-publish/skills/sharepoint-remove-publication/SKILL.md`
- [ ] `plugins/sharepoint-site-migration/skills/sharepoint-migrate-list-content/SKILL.md`
- [ ] `plugins/sharepoint-site-build-and-publish/skills/sharepoint-add-list-item/SKILL.md`
- [ ] `plugins/sharepoint-site-assessment/skills/*/SKILL.md` (all 13 discovery skills)
- [ ] `plugins/sharepoint-page-modernization-execution/skills/*/SKILL.md` (all 4 modernization execution skills)
- [ ] `plugins/sharepoint-copilot-agents-and-skills/skills/*/SKILL.md` (all 19 agent/skill management skills)
- [ ] `plugins/sharepoint-workbench-setup/skills/*/SKILL.md` (all 5 workbench setup skills)
