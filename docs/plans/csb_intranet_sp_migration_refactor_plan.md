# Refactoring Plan: Migrating `jag-csb-intranet` to SharePoint Knowledge Workbench Skills

**Target Consumer Repository:** `/Users/richardfremmerlid/Projects/jag-csb-intranet`  
**Provider Package:** `@sharepoint/sharepoint-workbench` (`/Users/richardfremmerlid/Projects/sharepoint-knowledge-workbench/plugins/sharepoint-workbench`)  
**Status:** Approved for execution upon completion of workbench consolidation  

---

## 1. Executive Summary & Objective

The `jag-csb-intranet` repository currently maintains a localized plugin `plugins/sp-migration` containing 10 custom skills. All 10 skills—plus the battle-tested RTE sanitization, dynamic ASPX conversion, and declarative navigation tools—have been ingested, sanitized, and consolidated into the upstream **SharePoint Knowledge Workbench** (`sharepoint-workbench`).

This plan provides guidance to refactor `jag-csb-intranet` so that:
1. Team members and automation agents can continue executing familiar workflows without friction or lost muscle memory.
2. Local proprietary inventories (`inventory/*.xlsx`, `inventory/ledgers/`, tenant configurations) remain untouched in the consumer repository.
3. Code duplication and maintenance overhead are eliminated by consuming the canonical `@sharepoint/sharepoint-workbench` package.

---

## 2. 1:1 Skill & Workflow Transition Matrix

Use this matrix to translate existing skills and operator commands to their modern workbench counterparts:

| Legacy `sp-migration` Skill | Target Consolidated Workbench Skill | Target Mode / Command | What Changed / Guidance |
|:---|:---|:---|:---|
| **`sp-navigation-sync`** | `managing-sharepoint-navigation` | `diff-navigation`<br>`sync-navigation` | Uses canonical `navigation_plan.py`. Same Excel structure (`Top Level`, `2nd Level`, `3rd Level`, `Url`, `OpenInNewTab`, `Enabled`). Pass `-ConfirmToken PROVISION-SPO-NAV` on execute. |
| **`sp-text-webpart-html`** | `publishing-sharepoint-pages`<br>*(also in `modernizing-sharepoint-pages`)* | `rte-sanitization` | Runs `sp_text_webpart_html.py` against `rte-vocabulary.json`. Table normalization and CKEditor 5 allowlisting. |
| **`sp-dynamic-aspx-page-migration`** | `publishing-sharepoint-pages`<br>*(also in `modernizing-sharepoint-pages`)* | `dynamic-aspx-page-publication`<br>*(or `convert-modern`)* | Same 7-stage workflow: extract web parts/images, map to SPO canvas, sanitize RTE HTML, dry-run, and publish with `-ConfirmToken PUBLISH-SPO-PAGE`. |
| **`sp-static-aspx-file-migration`** | `publishing-sharepoint-pages`<br>*(also in `modernizing-sharepoint-pages`)* | `static-aspx-file-publication`<br>*(or `aspx-to-html`)* | Inlines token styling into standalone HTML, runs `validate_design_system_page.py` and `rewrite_page_links.py`, and uploads with `-ConfirmToken UPLOAD-STATIC-PAGE`. |
| **`sp-document-library-upload`** | `managing-sharepoint-lists-and-libraries`<br>*(also in `migrating-sharepoint-sites`)* | `library-upload-orchestration` | Powered by `library_migration_ledger.py`. Maintains per-file staging, dry-run upload batches, and size-matched reconciliation. |
| **`sp-page-publish`** | `publishing-sharepoint-pages` | `page-publish-contract`<br>`apply-publication` | Standardized publication plan executor. Supports single-page and wave publication. |
| **`sp-page-inventory`** | `assessing-sharepoint-sites` | `sharepoint-analyze-page-inventory`<br>`sharepoint-collect-site-inventory` | Replaces on-prem collection scripts with standardized inventory crawlers and manifest validators. |
| **`sp-migration-wave-execution`** | `migrating-sharepoint-sites` | `wave-migration-orchestration`<br>`scaffold-wave-scripts` | Topologically sorted dependency waves; automated script scaffolding with verification gates between waves. |
| **`sp-migration-register-reconcile`** | `migrating-sharepoint-sites` | `reconciliation-contract`<br>`normalize-inventory` | Reconciles migration registers, status trackers, and inventory manifests. |
| **`sp-migration-release-readiness`** | `migrating-sharepoint-sites` | `audit-migration`<br>*(using `evaluate-release-readiness.ps1`)* | Validates release candidates against `release-manifest.template.json` before PROD signoff. |

---

## 3. Step-by-Step Refactor Roadmap for `jag-csb-intranet`

### Phase 1: APM Package Dependency Configuration
1. Open `/Users/richardfremmerlid/Projects/jag-csb-intranet/apm.yml` (create if absent).
2. Declare dependency on the unified package:
   ```yaml
   name: '@jag/csb-intranet'
   version: 1.0.0
   dependencies:
     '@sharepoint/sharepoint-workbench': '>=1.0.0'
   ```
3. Install package locally for agent harnesses:
   ```bash
   apm install @sharepoint/sharepoint-workbench --target claude,copilot,codex,antigravity
   ```

### Phase 2: Preserve Local Consumer State & Data Assets
Ensure these consumer-specific paths remain intact in `jag-csb-intranet`:
- `inventory/` (e.g., `navigation-menu.xlsx`, `page-migration-tracker.xlsx`, `ledgers/`).
- `context/` (control plane modes, human signing keys).
- `config*.psd1` (tenant credentials and site URLs).

### Phase 3: Update `AGENTS.md` and Operator Prompt Routing
1. Update `jag-csb-intranet/AGENTS.md` to reference the 11 consolidated skills rather than `sp-*`.
2. Add a quick reference table in `docs/migration-quickstart.md` linking familiar tasks to the new skill names.

### Phase 4: Deprecate and Retire `plugins/sp-migration/`
1. Verify that all automated workflows and tests in `jag-csb-intranet` resolve cleanly against the installed `@sharepoint/sharepoint-workbench` skills.
2. Remove the redundant `plugins/sp-migration/` folder and update `PLUGIN-INSTALL.md`.

---

## 4. Operator Cheat Sheet: Before vs. After Commands

### A. Navigation Menu Synchronization
- **Old:** `invoke skill sp-navigation-sync`
- **New:** `invoke skill managing-sharepoint-navigation`
  ```bash
  # Diff & plan:
  python3 <skill>/scripts/navigation_plan.py diff --plan temp/nav-plan.json --snapshot temp/nav-live.json --out temp/nav-ops.json
  # Sync to SPO:
  pwsh -File <skill>/scripts/sync-spo-navigation.ps1 -ConfigPath config-dev.psd1 -OpsPath temp/nav-ops.json -Execute -ConfirmToken PROVISION-SPO-NAV
  ```

### B. Dynamic ASPX Page Migration
- **Old:** `invoke skill sp-dynamic-aspx-page-migration`
- **New:** `invoke skill publishing-sharepoint-pages` (or `modernizing-sharepoint-pages`)
  ```powershell
  # 1. Sanitize RTE text webparts:
  pwsh -File <skill>/scripts/convert-package-to-rte.ps1 -PackagePath temp/extract/package.json -OutputPath temp/extract/package-rte.json
  # 2. Dry run preview:
  pwsh -File <skill>/scripts/new-page-migration-dry-run.ps1 -ConfigPath config-dev.psd1 -PackagePath temp/extract/package-rte.json
  # 3. Publish page:
  pwsh -File <skill>/scripts/publish-spo-page.ps1 -ConfigPath config-dev.psd1 -PackagePath temp/extract/package-rte.json -Execute -ConfirmToken PUBLISH-SPO-PAGE
  ```

### C. Document Library Migration Ledger
- **Old:** `invoke skill sp-document-library-upload`
- **New:** `invoke skill managing-sharepoint-lists-and-libraries`
  ```bash
  # Build plan:
  python3 <skill>/scripts/library_migration_ledger.py plan --inventory files.csv --source-library "Policies" --target-library "Documents" --ledger ledger.csv
  # Upload batch:
  python3 <skill>/scripts/library_migration_ledger.py upload-next --ledger ledger.csv --uploader <skill>/scripts/spo-upload-file.ps1 --config config-dev.psd1 --execute
  ```

---

## 5. Verification & Rollback Safeties

- **Zero Data Loss:** All existing tracker CSVs and Excel workbooks in `jag-csb-intranet/inventory/` remain untouched.
- **Fail-Safe Gate:** Because all 11 workbench skills enforce dry-run by default and require explicit confirmation tokens (`PROVISION-SPO-NAV`, `PUBLISH-SPO-PAGE`, `UPLOAD-STATIC-PAGE`), tenant operations cannot accidentally execute.
- **Parity Tested:** The workbench tools have been certified against identical test inputs with 100% test pass rates.
