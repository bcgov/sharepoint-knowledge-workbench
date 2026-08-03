# Complete Plugin/Skill Catalog — Expected Ecosystem After Phase 9

**Status:** Planning artifact. Records the expected plugin/skill ecosystem after Phase 6 (in
progress) and Phase 9 (not started, evidence-gated). Does not authorize implementation of any
Phase 9 item. No CMAT code has been migrated, copied, or extracted.

**Source inputs:**
- `docs/superpowers/plans/phase-6-multi-runtime-capability-model-plan-scaffold.md` (Task 0, 30 skills)
- `docs/superpowers/specs/phase-9-reusable-sharepoint-plugin-extraction-spec.md` §8c–§8e (34-skill CMAT audit)
- `temp/phase-6-planned-skills.md` (used as input, superseded by this tracked artifact)
- Machine-readable companion: `docs/architecture/complete-plugin-skill-catalog-after-phase-9.json`

**Skill totals — separate, mutually exclusive counts (computed directly from this catalog and
spec §8d, not invented). No grand total is published across categories that overlap** (e.g.
`review-manual-topics` is one skill name that appears once in "currently implemented" for its
native runtime and is not re-added when Phase 6's 30-name total is stated — see the note below
each block):

**Workbench (existing + Phase 6):**

| Category | Count | Detail |
|---|---|---|
| Unique installed skill names currently implemented | **5** | `extract-docx`, `analyze-document-structure`, `assemble-structured-content`, `render-multipage-markdown` (renamed from `render-structured-content` at Phase 6 Task 0.16; 4 core-pipeline skills) + `review-manual-topics` (native SharePoint runtime only; its repository/Claude runtime is not yet built). See `start-here.md`'s Phase 6 Task 0 progress section for the current, kept-up-to-date count of the 30-name Task 0 list (27/30 complete as of Task 0.16's close — all 7 `structured-content-rendering` skills plus the 20 `sharepoint-agents-and-skills`/`sharepoint-content-publication` skills; only `workbench-setup`'s 3 remain). |
| Unique additional Phase 6 skill names approved (Task 0, not yet built or partially built) | **29** | Phase 6 Task 0's full skill-name list is **30** names total; `review-manual-topics` is one of those 30 and is already counted above as implemented (native runtime) — so 29 is the count of Phase 6 names with no implementation yet, plus `review-manual-topics`'s own outstanding repository-runtime work is tracked under its existing single entry, not as a 30th separate "additional" name. |

**CMAT (Phase 9 source, spec §8d — 34 skills directly audited, mutually exclusive, sums to 34):**

| Category | Count |
|---|---|
| Phase 9 source skills audited | **34** |
| Phase 9 extraction candidates (has a `PHASE_9_EXTRACT_AS_NEW_PLUGIN` / `PHASE_9_EXTRACT_TO_EXISTING_PLUGIN` / `PHASE_9_MERGE_WITH_EXISTING_SKILL` disposition) | **19** |
| `KEEP_CMAT_SPECIFIC` (implemented, not extraction-eligible) | **1** (`sp-provisioning-modern-calendars`) |
| `REQUIRES_HUMAN_DECISION` (implemented, scope vs. another skill unresolved) | **1** (`sp-content-migration`, vs. `sp-migrating-content`) |
| `UNVERIFIED_ACTIVE_CLAIM` (claimed active, zero backing found) | **2** (`sp-synthesizing-deployment-matrix`, `sp-generating-migration-reports`) |
| `PLANNED_WITH_NO_IMPLEMENTATION` (claimed planned, zero backing found — confirms the claim) | **11** |
| **Sum check: 19 + 1 + 1 + 2 + 11** | **= 34** ✓ |

`ORDS_SPECIFIC_OUT_OF_SCOPE` (`ords-integration-migration` plugin) is excluded entirely from the
34 above — its own skill count was not itemized in this audit, per instruction to keep it out of
scope by default.

**No single number combines the workbench counts and the CMAT counts** — they describe different
things (skills that exist or are approved to be built, vs. skills that exist in a separate
repository and have not been extracted). Presenting `5 + 29 + 34` as one "grand total" would imply
a single unified skill count that does not exist; none is published here.

---

## Existing Content Pipeline (Phase 1–2, complete, unchanged by Phase 6/9)

### `source-document-extraction`
- **Status:** existing
- **Purpose:** extract and normalize a source `.docx` into a normalized-source-document contract.
- **Responsibilities:** pandoc invocation, EMF image conversion, heading parsing, defect detection.
- **Non-responsibilities:** topic-boundary analysis, canonical assembly, rendering, publication.
- **Skills:** `extract-docx` — implemented.
- **Dependencies/contracts:** produces `normalized-source-document` contract, consumed by `document-structure-analysis`.
- **Installation:** `pip install -e plugins/source-document-extraction`, standalone.

### `document-structure-analysis`
- **Status:** existing
- **Purpose:** analyze normalized content into heading hierarchy, topic boundaries, a proposed conversion plan.
- **Responsibilities:** topic-boundary reasoning, chunking-strategy recommendation.
- **Non-responsibilities:** DOCX parsing, canonical package assembly, rendering, publication.
- **Skills:** `analyze-document-structure` — implemented.
- **Dependencies/contracts:** consumes `normalized-source-document`, produces conversion-plan contract.
- **Installation:** standalone.

### `structured-content-assembly`
- **Status:** existing
- **Purpose:** cleanup, chunking, canonical package build and validation.
- **Responsibilities:** stable identities, source lineage, hashes, manifests, publication mappings.
- **Non-responsibilities:** extraction, topic-boundary decisions, rendering, publication.
- **Skills:** `assemble-structured-content` — implemented.
- **Installation:** standalone.

### `structured-content-rendering`
- **Status:** Phase 6 Task 0.16 complete — all 7 skill names implemented, packaged, tested (96/96, including a real isolated wheel install and a real CEIS-manual ASPX golden-master proof).
- **Purpose:** render a canonical package to output formats.
- **Responsibilities:** multipage-Markdown rendering, ASPX (SharePoint modern-page) rendering, render validation (both formats), rendering-template creation/validation (both formats), rendered-output comparison.
- **Non-responsibilities:** SharePoint tenant I/O (owned by `sharepoint-content-publication`); legacy-page *analysis/conversion* (Phase 9 candidate `sharepoint-page-modernization`, distinct domain per master-roadmap boundary).
- **Skills:**
  - `render-multipage-markdown` — implemented (renamed from `render-structured-content` at Task 0.16).
  - `render-sharepoint-aspx` — implemented; golden-master fidelity proof against the real CEIS manual complete (`runs/ceis-manual-v2/render-aspx/`).
  - `create-markdown-rendering-template` — implemented.
  - `create-aspx-rendering-template` — implemented.
  - `validate-rendering-template` — implemented.
  - `validate-rendered-output` — implemented (both Markdown and ASPX).
  - `compare-rendered-output` — implemented.
- **Phase 9 overlap:** `sp-converting-aspx-pages` (CMAT, richest implementation in the audit) — Phase 6 stays minimal-interface, full page-analysis/conversion sophistication is a Phase 9 candidate targeting *this* plugin (`PHASE_9_EXTRACT_TO_EXISTING_PLUGIN`), per spec §8c.
- **Installation:** standalone.

---

## Phase 6 Operational Plugins (Task 0, `AUTHORIZED_AND_IN_PROGRESS`)

### `sharepoint-content-publication`
- **Status:** Phase 6 planned (existing `TRANSITIONAL_HOLDING_LOCATION`, completed under Task 0.15)
- **Purpose:** consume rendered artifacts and deploy/reconcile/validate/rollback in SharePoint.
- **Responsibilities:** upload, page create/update, reconciliation, validation, rollback.
- **Non-responsibilities:** rendering, rendering templates, agent/native-skill lifecycle.
- **Skills:**
  - `publish-markdown-to-sharepoint` — Phase 6 Task 0.15, not yet built.
  - `publish-aspx-to-sharepoint` — Phase 6 Task 0.15, not yet built.
  - `reconcile-sharepoint-publication` — Phase 6 Task 0.15, existing Python basis (`sharepoint_reconcile.py`), packaging pending.
  - `validate-sharepoint-publication` — Phase 6 Task 0.15, existing partial Python basis, extension pending.
  - `rollback-sharepoint-publication` — Phase 6 Task 0.15, not yet built (no CMAT counterpart either).
- **Phase 9 overlap:** `sp-uploading-content` (CMAT, active, dual PnP+REST mechanism) → `PHASE_9_EXTRACT_TO_EXISTING_PLUGIN` here; `sp-migrating-content`'s single-item upload primitive (extracted from the 10-wave engine) is a further candidate once genericized.
- **Installation:** existing Python package structure; skills/manifests not yet complete.

### `sharepoint-agents-and-skills`
- **Status:** Phase 6 planned (new plugin, Task 0.1–0.14, partially scaffolded)
- **Purpose:** own agents, agent templates, `AgentAssets`, and native-skill lifecycle.
- **Responsibilities:** agent create/update/knowledge-configuration/backup/restore/template; native-skill create/deploy/verify/rollback/backup/restore; `AgentAssets` inventory/validation.
- **Non-responsibilities:** content rendering, publication, workbench setup/config-file generation.
- **Skills (15, Task 0.1–0.14) — one skill name each; `review-manual-topics` has two runtimes,
  not two skill names:**
  - `review-manual-topics`
    - runtimes:
      - `native-sharepoint` — **implemented** (moved from Phase 4, real deployed skill).
      - `repository-claude` — Task 0.3, not yet built.
  - `create-sharepoint-native-skill` — Task 0.4, not yet built.
  - `deploy-sharepoint-native-skill` — Task 0.4, scripts moved, packaging pending.
  - `verify-sharepoint-native-skill` — Task 0.4, scripts extracted, packaging pending.
  - `rollback-sharepoint-native-skill` — Task 0.4, script moved, packaging pending.
  - `inventory-and-validate-agentassets` — Task 0.4, script moved, `provision-agentassets` canonical-version decision resolved (Phase-4 copy), packaging pending.
  - `backup-sharepoint-native-skills` — Task 0.5, script generalized, packaging pending.
  - `restore-sharepoint-native-skills` — Task 0.5, not yet built.
  - `create-sharepoint-agent` — Task 0.6, not yet built.
  - `update-sharepoint-agent` — Task 0.6, not yet built (previously missing entirely).
  - `configure-sharepoint-agent-knowledge` — Task 0.6, not yet built.
  - `backup-sharepoint-agents` — Task 0.6, script generalized, packaging pending.
  - `restore-sharepoint-agents` — Task 0.6, not yet built (includes `get-agent-resource-identifiers`).
  - `create-sharepoint-agent-template` — Task 0.7, not yet built.
  - `apply-sharepoint-agent-template` — Task 0.7, not yet built.
- **Excluded from Task 0:** `review-manual-topics-metadata` (write-capable, UI-generated, distinct capability) — `RETAIN_AS_PHASE_EVIDENCE`, not implemented, not counted in the 15.
- **Phase 9 overlap:** `sp-validating-app-registration` (CMAT, active) → `PHASE_9_MERGE_WITH_EXISTING_SKILL` target is actually `workbench-setup`, not this plugin (per spec §8c/§8e) — noted here to prevent future misassignment.
- **Installation:** scaffold only; no `plugin.json`/`plugin.yaml`/`README.md` yet.

### `workbench-setup`
- **Status:** Phase 6 planned (new plugin, Task 0.17, not yet created)
- **Purpose:** foundational connection/config/workflow setup for the whole workbench.
- **Responsibilities:** `config.psd1` generation, document-workflow/publication-profile intake wizard, config/profile validation.
- **Non-responsibilities:** document extraction, rendering, tenant writes beyond opt-in connection testing, agent/skill creation.
- **Skills (3, Task 0.17):**
  - `setup-sharepoint-connection` — not yet built.
  - `initialize-document-workflow` — not yet built (absorbs `initialize-publication-profile`, not a 4th skill).
  - `validate-workbench-environment` — not yet built.
- **Authoring constraint (corrected 2026-08-03):** authored directly in this repo at `plugins/workbench-setup/`, same as `sharepoint-agents-and-skills`/`sharepoint-content-publication` — an earlier version of this line wrongly claimed Category 1 (marketplace-style, sibling `agent-plugins-skills` monorepo); that conflated using the `marketplace-manager` skill (installed from `agent-plugins-skills`) as the *procedure* for `marketplace.json` updates with authoring the plugin's code there. See `start-here.md`'s Task 0.17 correction record.
- **Phase 9 overlap:** `sp-validating-app-registration` (CMAT, active) is the richer connection/auth-validation implementation — `PHASE_9_MERGE_WITH_EXISTING_SKILL` target once `setup-sharepoint-connection`'s optional `-TestConnection` path is built.
- **Installation:** not yet created.

---

## Phase 9 Candidate Engineering Plugins (evidence-gated, none approved, none implemented)

**Presented as candidates only — none of the following exist in this workbench, none are
authorized, and none have had a single file extracted from CMAT.**

**Source path root for every `cmat_source` named below:**
`/Users/richardfremmerlid/Projects/jag-csb-cmat-sharepoint-online/plugins/sharepoint-migration/skills/<cmat_source>/`
— the exact per-skill path is `<root>/<cmat_source>/`. The JSON companion
(`complete-plugin-skill-catalog-after-phase-9.json`) records each one explicitly as
`cmat_source_path`.

### `sharepoint-discovery` (candidate — provisionally justified, spec §8e)
- **Purpose (candidate):** inventory an existing SharePoint site's structure, content, permissions.
- **Skills mapped (10):** `discover-site-structure` (from `sp-discovering-site-structure`, CMAT active), `discover-lists` (`sp-discovering-lists`, CMAT planned/no implementation), `discover-content-types` (`sp-discovering-content-types`, CMAT planned/no implementation), `discover-pages` (`sp-discovering-pages`, CMAT active), `discover-web-parts` (`sp-discovering-web-parts`, CMAT active, richest — 19 symlinks), `discover-navigation` (`sp-discovering-navigation`, CMAT active), `discover-forms` (`sp-discovering-forms`, CMAT active), `discover-permissions` (`sp-discovering-permissions`, CMAT active, thin), `discover-workflows` (`sp-discovering-workflows`, CMAT planned/no implementation), `synthesize-discovery-report` (`sp-synthesizing-discovery`, CMAT active, thin).
- **Overlap:** none with Phase 6 (Phase 6's `inventory-and-validate-agentassets` is `AgentAssets`-only, a different domain object).

### `sharepoint-schema` (candidate — provisionally justified on 1 skill)
- **Purpose (candidate):** audit/map SharePoint schema (content types, lists, taxonomy, choices).
- **Skills mapped (5):** `audit-schema` (`sp-auditing-schema`, CMAT active, real), `extract-choice-fields` (`sp-extracting-choices`, CMAT active, thin), `map-content-types` (`sp-mapping-content-types`, CMAT planned/no implementation), `map-lists` (`sp-mapping-lists`, CMAT planned/no implementation), `map-taxonomy` (`sp-mapping-taxonomy`, CMAT planned/no implementation).
- **Overlap:** none with Phase 6.

### `sharepoint-provisioning` (candidate — **not currently justified**, spec §8e)
- **Purpose (candidate):** dependency-aware schema/list/library provisioning + rollback.
- **Skills mapped (2):** `synthesize-deployment-matrix` (`sp-synthesizing-deployment-matrix`, CMAT claims active, **no implementation evidence found** — `REQUIRES_HUMAN_DECISION`), `provision-modern-calendars` (`sp-provisioning-modern-calendars`, CMAT-specific, `KEEP_CMAT_SPECIFIC`, calendar/court-scheduling concept).
- **Overlap:** none with Phase 6. No confirmed generic implemented skill exists here — re-evaluate after the unverified skill is directly re-checked.

### `sharepoint-page-modernization` (candidate — justified, strongest single pilot candidate)
- **Purpose (candidate):** analyze and convert *existing* classic SharePoint pages to modern SPO — distinct from `structured-content-rendering`, which originates new content from structured workbench data, never analyzes/converts a pre-existing page.
- **Skills mapped (5):** `analyze-aspx-pages` (`sp-analysing-aspx-pages`, CMAT active), `convert-aspx-pages` (`sp-converting-aspx-pages`, CMAT active, **richest implementation in the entire audit** — 12 scripts + 5 symlinks), `convert-wiki-pages` (`sp-converting-wiki-pages`, CMAT active), `remediate-page-layouts` (`sp-remediating-page-layouts`, CMAT planned/no implementation), `remediate-web-parts` (`sp-remediating-web-parts`, CMAT planned/no implementation).
- **Overlap:** `render-sharepoint-aspx` (Phase 6, minimal-interface origination only) and rendering-template creation (Phase 6, narrow validation scope) — both explicitly kept minimal in Phase 6 pending this candidate's full extraction, per spec §8c.

### `sharepoint-link-remediation` (candidate — provisionally justified)
- **Purpose (candidate):** extract, rewrite, and validate links broken by migration.
- **Skills mapped (4):** `extract-links` (`sp-extracting-links`, CMAT active), `remediate-links` (`sp-remediating-links`, CMAT active), `remediate-document-content-links` (`sp-remediating-document-content-links`, CMAT planned/no implementation), `validate-link-integrity` (`sp-validating-link-integrity`, CMAT active, thin).
- **Overlap:** `reconcile-sharepoint-publication`/`validate-sharepoint-publication` (Phase 6) named as candidate-technique targets in spec §8c, once genericized.

### `sharepoint-content-migration` (candidate — provisionally justified, contingent on genericity review)
- **Purpose (candidate):** bulk/wave-based content migration with schema provisioning.
- **Skills mapped (4):** `migrate-content` (`sp-content-migration`, CMAT real but scope-overlap with next row unresolved — `REQUIRES_HUMAN_DECISION`), `run-migration-waves` (`sp-migrating-content`, CMAT active, **44 symlinks, richest skill in the repo by link count** — mechanism-only extraction; wave *content* stays `KEEP_CMAT_SPECIFIC`), `run-sharegate-jobs` (`sp-running-sharegate-jobs`, CMAT active), `upload-content` — **reassigned out of this candidate** to `sharepoint-content-publication` (existing plugin preferred, per spec §8c/§8e).
- **Overlap:** `publish-markdown-to-sharepoint` (Phase 6) explicitly compared in spec §8c — scale mismatch intentional, Phase 6 stays single-document-scoped.

### `sharepoint-validation-and-reconciliation` (candidate — **not currently justified**, spec §8e)
- **Purpose (candidate):** post-migration parity/drift validation and evidence.
- **Skills mapped (4):** `validate-content` (`sp-validating-content`, CMAT planned/no implementation), `validate-permissions` (`sp-validating-permissions`, CMAT planned/no implementation), `validate-app-registration` (`sp-validating-app-registration`, CMAT active, real — **reassigned** to `workbench-setup`, existing plugin preferred), `generate-migration-reports` (`sp-generating-migration-reports`, CMAT claims active, **no implementation evidence found** — `REQUIRES_HUMAN_DECISION`).
- **Overlap:** `reconcile-/validate-sharepoint-publication` (Phase 6) explicitly compared in spec §8c. After `sp-validating-app-registration`'s reassignment, no confirmed implemented core remains in this candidate — re-evaluate only if the other 3 skills are ever built or verified.

---

## Explicitly Excluded

### `ords-integration-migration` (CMAT plugin — out of scope by default)
Court-scheduling ETL (ORDS queries, JUSTIN/CEIS matching, courthouse routing, monitored-person
logic, appearance cleanup, CMAT calendars, CMAT retention rules) — `ORDS_SPECIFIC_OUT_OF_SCOPE` /
`KEEP_CMAT_SPECIFIC` for its entire scope. Only a generic SharePoint helper found inside it would
ever be extraction-eligible; none was identified in this audit.

---

**No CMAT or ORDS source file has been copied, moved, or referenced as executable source anywhere
in this catalog or in Phase 6 Task 0's actual implementation.** The CMAT repository
(`jag-csb-cmat-sharepoint-online`) remains intact and unmodified.
