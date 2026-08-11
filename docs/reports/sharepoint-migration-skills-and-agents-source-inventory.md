# SharePoint Migration skills/ and agents/ Source Inventory

**Correction to task brief:** the source `plugins/sharepoint-migration/skills/` directory contains
**35** skill folders (not 33 as initially briefed), 148 files total. All 35 are read/inventoried
below. 10 agent files (9 agents + 1 shared reference doc) in `agents/`, also all read in full.

**Headline finding:** roughly half of the 35 skills already have a workbench counterpart —
overwhelmingly the **local-analysis half only**. Every skill whose real work is a live-tenant
*collector* (`Connect-PnPOnline`/CSOM/REST against a real site) was either (a) already flagged in
the existing `.ps1`-only inventory (`docs/reports/sharepoint-migration-ps1-source-inventory.md`,
since its collector script lives under `scripts/`, reached via symlink from the skill folder) or
(b) explicitly deferred/rejected by the Phase 9 provenance record for being out of scope for a
declared read-only-analysis plugin. **No skill folder introduces net-new source material the
`.ps1` audit and `.agent/map-debt.md`'s 2026-08-11 entries didn't already surface** — this pass
mainly confirms and cross-references, and corrects one count discrepancy (33 vs 35) and clarifies
which skill each already-ported Python module maps to by name.

## Skills Inventory

| Skill folder | Live-tenant or local-only | What it does | Overlaps existing .ps1 audit? | Destination plugin | Destination skill (existing/new) | Classification |
|---|---|---|---|---|---|---|
| `sp-analysing-aspx-pages` | Mixed (collector + local analysis) | Bulk ASPX extraction (VPN) then `analyse_aspx_content.py` layout/component analysis | Yes — `page-migration/*` rows | `sharepoint-page-modernization` | `analyze-aspx-pages` (existing) | ALREADY_EXISTS_IN_WORKBENCH |
| `sp-auditing-schema` | Local-only (6 live scripts, disk diffs) | Schema comparison, site parity, duplicate-field audit, missing-field detection | Partially (`schema-audit/compare-prod-vs-test-schema.ps1` As-Is row) | `sharepoint-schema` | `audit-schema` (existing) | ALREADY_EXISTS_IN_WORKBENCH |
| `sp-content-migration` | Live-tenant | Config-driven list-content migration (`migrate-list.ps1`, `get-source-item-counts.ps1`) | Yes — `content-migration/*` rewrite rows | `sharepoint-content-migration` | `migrate-sharepoint-list-content` (existing, executor missing) | ALREADY_COVERED_BY_PS1_AUDIT |
| `sp-converting-aspx-pages` | Local-only (richest skill, 32 real files, no symlinks) | 8-stage classify/map/select-layout/emit-manifest pipeline, zero tenant I/O | Yes — `page-migration/*` rows | `sharepoint-page-modernization` | `convert-aspx-pages` (existing) | ALREADY_EXISTS_IN_WORKBENCH |
| `sp-converting-wiki-pages` | Live-tenant (VPN + CSOM/IWA) | `convert-wiki-page.ps1` — live collector, not an analyser of an export | Yes — `page-migration/convert-wiki-page.ps1` (this row's own SKILL.md) | none — no owning plugin | new (would need an unowned live-collector plugin) | NOT_RECOMMENDED (explicitly rejected in Phase 9 Wave 4, not merely deferred — scope mismatch with the read-only-analysis plugin contract) |
| `sp-copying-spo-pages` | Local-only planner (`spo_page_copy_plan.py`) | Builds a same-tenant page-copy plan for `Copy-PnPPage` | No | `sharepoint-content-publication` | `copy-spo-page-between-sites` (existing — built independently this session, not ported from this source skill; name similarity is coincidental, verified by content) | ALREADY_EXISTS_IN_WORKBENCH |
| `sp-discovering-content-types` | N/A | `PLANNED_WITH_NO_IMPLEMENTATION` — no backing script | No | — | — | NOT_RECOMMENDED (nothing to onboard) |
| `sp-discovering-forms` | Mixed | `download-custom-forms.ps1` (collector) + `generate-deep-forms-analysis.py` (analysis, ported) | Partially (analysis script ported; collector not in `.ps1` audit's explicit table but named in "New Skills Needed") | `sharepoint-discovery` | `analyze-custom-forms` (existing, analysis half only) | ALREADY_EXISTS_IN_WORKBENCH (analysis) / gap confirmed for collector |
| `sp-discovering-lists` | N/A | `PLANNED_WITH_NO_IMPLEMENTATION` | No | — | — | NOT_RECOMMENDED |
| `sp-discovering-navigation` | Mixed | `extract-site-navigation.ps1` (collector) + `generate-deep-nav-analysis.py` (analysis, ported) | Yes — `page-migration/extract-site-navigation.ps1` row | `sharepoint-discovery` | `analyze-site-navigation` (existing, analysis half only) | ALREADY_EXISTS_IN_WORKBENCH (analysis) |
| `sp-discovering-pages` | Live-tenant | `extract-all-aspx-pages.ps1`, `analyze-aspx-webparts.ps1`, `convert-wiki-page.ps1` (duplicate reference to `sp-converting-wiki-pages`'s own script) | Yes — `page-migration/extract-all-aspx-pages.ps1` row | `sharepoint-discovery` | `collect-sharepoint-inventory` (new, named in ps1 audit) / `analyze-page-inventory` (existing, analysis half) | ALREADY_COVERED_BY_PS1_AUDIT |
| `sp-discovering-permissions` | Mixed | `generate-deep-permissions-analysis.py` (analysis, ported, dual input-shape); collection leg not separately scripted here (uses site-structure/nav exports) | Not explicitly tabled in ps1 audit — **correction candidate**, see below | `sharepoint-discovery` | `analyze-permissions` (existing, analysis half only) | ALREADY_EXISTS_IN_WORKBENCH (analysis) |
| `sp-discovering-site-structure` | Live-tenant (2 collectors, highest literal density: 147/178 hits) | `export-sharepoint-inventory.ps1` / `-custom.ps1`, `diagnose-page.ps1` | Yes — `inventory/*` rewrite rows | `sharepoint-discovery` | `collect-sharepoint-inventory` (new, named in ps1 audit) | ALREADY_COVERED_BY_PS1_AUDIT |
| `sp-discovering-web-parts` | Mixed (richest discovery skill) | Live web-part scan/extraction + `analyze-webpart-code.py`/deep-analysis (ported) | Yes — `page-migration/scan-webparts.ps1` etc. rewrite rows | `sharepoint-discovery` | `analyze-webpart-code` (existing, analysis half only) | ALREADY_EXISTS_IN_WORKBENCH (analysis) / ALREADY_COVERED_BY_PS1_AUDIT (collectors) |
| `sp-discovering-workflows` | N/A | `PLANNED_WITH_NO_IMPLEMENTATION` | No | — | — | NOT_RECOMMENDED |
| `sp-extracting-choices` | Live-tenant (thin, 1 script) | `extract-choices.ps1` — SP2016 REST `$expand=Choices` extraction | Yes — `utilities/extract-choices*.ps1` rewrite rows | `sharepoint-discovery` | `extract-choice-fields` (existing, local-parsing reimplementation only) | ALREADY_COVERED_BY_PS1_AUDIT |
| `sp-extracting-links` | Local-only (analysis, ported) | `generate-deep-link-analysis.py` — 7-surface link inventory | No (this script not in the 147-file `scripts/` tree table; it's under `page-migration/`, already ported) | `sharepoint-link-remediation` | `extract-links` (existing) | ALREADY_EXISTS_IN_WORKBENCH |
| `sp-generating-migration-reports` | N/A | `PLANNED_WITH_NO_IMPLEMENTATION` | No | — | — | NOT_RECOMMENDED |
| `sp-mapping-content-types` | N/A | `PLANNED_WITH_NO_IMPLEMENTATION` | No | — | — | NOT_RECOMMENDED |
| `sp-mapping-lists` | N/A | `PLANNED_WITH_NO_IMPLEMENTATION` | No | — | — | NOT_RECOMMENDED |
| `sp-mapping-taxonomy` | N/A | `PLANNED_WITH_NO_IMPLEMENTATION` | No | — | — | NOT_RECOMMENDED |
| `sp-migrating-content` | Live-tenant (very large: wave0a–9 schema+content deployment) | Full CMAT tenant provisioning/migration wave sequence | Yes — `waves/*`, `calendars/*`, `lib/*` tables (largest overlap in the whole audit) | `sharepoint-provisioning` + `sharepoint-content-migration` | multiple existing stub skills, executors missing | ALREADY_COVERED_BY_PS1_AUDIT |
| `sp-provisioning-modern-calendars` | Live-tenant | `modern-calendar-lib.ps1` — Template-100 calendar provisioning | Yes — `calendars/modern-calendar-lib.ps1` As-Is-adjacent row | `sharepoint-provisioning` | `provision-modern-calendar-list` (existing, executor missing per ps1 audit) | ALREADY_COVERED_BY_PS1_AUDIT |
| `sp-remediating-document-content-links` | N/A | `PLANNED_WITH_NO_IMPLEMENTATION` (reference doc only, no script) | No | — | — | NOT_RECOMMENDED |
| `sp-remediating-links` | Live-tenant | `Repair-EmbeddedLinks.ps1` — regex URL rewrite in `CanvasContent1` | Yes — Onboard-As-Is row | `sharepoint-link-remediation` | `remediate-links` (existing, Python text-transform only — real tenant-write executor missing) | ALREADY_COVERED_BY_PS1_AUDIT |
| `sp-remediating-page-layouts` | N/A | `PLANNED_WITH_NO_IMPLEMENTATION` | No | — | — | NOT_RECOMMENDED |
| `sp-remediating-web-parts` | N/A | `PLANNED_WITH_NO_IMPLEMENTATION` | No | — | — | NOT_RECOMMENDED |
| `sp-running-sharegate-jobs` | Mixed | 2 ShareGate-dependent upload scripts + `combine-preview.ps1` (zero ShareGate/tenant I/O, already ported) | Yes — Duplicate/Low-Value rows for the ShareGate scripts | `sharepoint-page-modernization` | `compose-page-preview` (existing, for the local-only piece) | NOT_RECOMMENDED (ShareGate-dependent parts — requires a commercial licensed tool, explicitly flagged, not silently recommended) / ALREADY_EXISTS_IN_WORKBENCH (`combine-preview.ps1` piece only) |
| `sp-synthesizing-deployment-matrix` | N/A | Claimed `active` in SKILL.md but zero backing scripts/symlinks — reclassified `PLANNED_WITH_NO_IMPLEMENTATION` on direct read | No | — | — | NOT_RECOMMENDED |
| `sp-synthesizing-discovery` | Local-only (thin, 129 lines) | Meta-review rollup — mostly **hardcoded/fabricated** metrics, not real analysis | No | — | — | NOT_RECOMMENDED (fabricates output; correctly rejected on evidence, not just deferred) |
| `sp-uploading-content` | Live-tenant | `upload-modern-page.ps1`/`-rest.ps1`, `migrate-site-assets.ps1` | Yes — Duplicate/Low-Value row for the two upload scripts (superseded in the workbench's own judgement) | `sharepoint-content-publication` | `upload-content` (existing; real `spo-upload-plan.ps1` executor added 2026-08-11 for page creation only, asset upload still missing) | ALREADY_EXISTS_IN_WORKBENCH |
| `sp-validating-app-registration` | Live-tenant | `test-spo-auth.ps1` device-code auth validation | Yes — Already-Exists row | `workbench-setup` | `validate-app-registration` (existing) | ALREADY_EXISTS_IN_WORKBENCH |
| `sp-validating-content` | N/A | `PLANNED_WITH_NO_IMPLEMENTATION` | No | — | — | NOT_RECOMMENDED |
| `sp-validating-link-integrity` | Live-tenant (thin, 1 script) | `Test-LinkConversion.ps1` — post-conversion link resolution check | No explicit row (thin skill, technique reimplemented not ported) | `sharepoint-link-remediation` | `validate-link-integrity` (existing) | ALREADY_EXISTS_IN_WORKBENCH |
| `sp-validating-permissions` | N/A | `PLANNED_WITH_NO_IMPLEMENTATION` | No | — | — | NOT_RECOMMENDED |

## Agents Inventory

| Agent file | Orchestrates | Destination plugin | Existing destination agent equivalent? |
|---|---|---|---|
| `sp-discovery-agent.md` | 14-step full discovery sequence (pages → web parts scan/extract/cluster/catalog → report suite → nav → forms → aspx layout → permissions → links → forms report → nav report → master meta-review) against a **live** SP2016/SPO site, with a mandatory interactive interview (site URL, output dir, auth method, config strategy) and a 2-stage "run script, then deep-read output" protocol per step | `sharepoint-discovery` | **No.** Not extracted in Phase 9 Wave 2 (3 project literals, explicitly out of scope for that wave). `sharepoint-discovery` currently has no orchestrating agent at all — only individual analysis skills. |
| `sp-schema-agent.md` | Routes schema questions to `sp-auditing-schema` (read-only, always first) vs. planned `sp-mapping-*` skills, flags unscripted mapping | `sharepoint-schema` (routing) / `sharepoint-agents-and-skills` (destination location) | Yes — `agents/sharepoint-schema-agent.md` exists (Phase 9 Wave 2, Record 5), re-targeted to real destination skills |
| `sp-validation-agent.md` | Routes post-migration validation/reporting; source version had nothing real to route to (all 3 skills planned) | `sharepoint-agents-and-skills` | Yes — `agents/sharepoint-validation-agent.md` exists (Wave 2, Record 6); destination version materially improved since real validators exist here |
| `sp-modernization-agent.md` | Chooses full ASPX pipeline vs. lighter wiki-page path; flags planned remediation skills | `sharepoint-agents-and-skills` | Yes — `agents/sharepoint-modernization-agent.md` exists (Wave 2, Record 4), with an explicit scope note that this workbench renders new pages, it doesn't rebuild existing classic ones |
| `sp-link-agent.md` | Sequences extract → remediate → validate for links | `sharepoint-agents-and-skills` | Yes — `agents/sharepoint-link-agent.md` exists (Wave 2, Record 3) |
| `sp-deployment-planner.md` | Synthesizes discovery + schema into a deployment plan; decides when to update `wave-dependency-matrix.json` or run completeness tests | none | **No.** Deliberately not extracted in Wave 2 (14 literals) — no destination equivalent exists; would require a wave-planning capability the destination doesn't have (closest: `sharepoint-migration-planning`'s dependency-graph analysis, but that's a different mechanism). |
| `sp-migration-agent.md` | Picks execution-domain skill for a migration task (schema deploy / list-item migration / document migration / single-asset upload), gates on app-registration validation | none | **No.** Not extracted (3 literals) — no single destination agent currently spans schema-provisioning + content-migration + upload decision-making; each of those lives in a separate plugin with no cross-plugin router. |
| `sp-migration-orchestrator.md` | End-to-end 7-domain sequencing (discovery → schema audit → schema deploy → content migration wave-by-wave → modernization → link remediation → validation), with a detailed wave-by-wave content-migration runbook, failure-handling table, and hard constraints (never write on-prem, VPN gates, quarantine orphan rows) | none | **No.** Not extracted (36 literals) — this is the single most CMAT-specific agent (hardcoded list names, wave orders, ORDS references); no destination equivalent, and porting it would require a full cross-plugin orchestrator that doesn't exist anywhere in the workbench today. |
| `sp-wave-orchestrator.md` | One-command-at-a-time wave deployment advisor for the CMAT schema (wave0a→9), VPN/dry-run/TDD gating, full command reference, dependency map | none | **No.** Not extracted (161 literals — by far the most literal-dense agent in the source). Entirely CMAT-specific (site URLs, list names, calculated-column formulas per named list); not a generic capability, would need a full rewrite to a config-driven wave-runner to be reusable at all. |
| `references/guiding-principles.md` | Shared decision philosophy ("like-for-like is a principle not a rule", "quantity ≠ effort", "manual recreation beats complex automation") referenced by `sp-migration-orchestrator.md` | n/a (reference doc, not an agent) | No direct equivalent; conceptually generic and portable, but was not read as a stand-alone extraction candidate in Phase 9 and is not referenced from this inventory's other findings. |

## Corrections to the existing `.ps1`-only inventory

1. **Skill-folder count discrepancy.** The dispatching prompt for this audit stated 33 skill
   folders; direct `find` enumeration shows **35**. Both `.ps1`-only inventory and this document
   should be read against the actual 35-folder structure.
2. **`sp-discovering-permissions`'s live-collection leg has no explicit row in the `.ps1` audit.**
   The `.ps1` audit tables `page-migration/generate-deep-permissions-analysis.py`'s ported analysis
   implicitly (it's the backing script for `analyze-permissions`), but the *export/collection*
   side of permissions discovery (enumerating unique role assignments/principals from a live site)
   has no named source `.ps1` and no "New Skill Needed" bullet the way navigation/forms/pages do.
   This is a real gap in the `.ps1` audit's "New Plugins/Skills Needed" section, not just an
   omission in this document.
3. **`sp-discovering-pages`'s `convert-wiki-page.ps1` reference and `sp-converting-wiki-pages`'s
   own copy are the same underlying script**, confirmed directly from both `SKILL.md` files. The
   `.ps1` audit already treats `page-migration/convert-wiki-page.ps1` as a single file (rewrite
   table, target `extract-legacy-page-content`), so this is not a double-count risk in that
   document — but a reader relying on skill folders alone could double-count it as two capabilities.
4. **No new capability surfaced by this pass that the `.ps1` audit or `.agent/map-debt.md`'s
   2026-08-11 entries didn't already identify.** Every live-tenant collector named in a skill's
   `SKILL.md` resolves to a `scripts/` file already tabled in the `.ps1` audit (Onboard As-Is /
   With Rewrite / Duplicate) or already named in its "New Plugins/Skills Needed" section.

## Priority findings

- **`sp-discovery-agent.md` materially changes what `sharepoint-discovery`'s intended *end-state*
  scope should look like, but it does not change or duplicate the two pieces already in flight
  this session** (`collect-sharepoint-page-inventory.ps1`, and a `collect-sharepoint-inventory`
  skill another agent is currently building). The source agent's 14-step sequence spans *all 5*
  discovery domains (pages, web parts, navigation, forms, permissions) plus a synthesis step this
  workbench correctly rejected as fabricated (`sp-synthesizing-discovery`). Only step [1] (page
  collection) overlaps what's being built right now; steps [2]–[5],[7]–[13] correspond to the
  still-missing collectors for web-parts/nav/forms/permissions already tracked in
  `.agent/map-debt.md`'s 2026-08-11 entry and the `.ps1` audit's "New Plugins/Skills Needed" list.
  No orchestrating agent for `sharepoint-discovery` exists yet in the destination — that is a real,
  confirmed gap this source agent would fill once the underlying collectors exist, but building the
  agent now (before the collectors) would just be routing to skills that don't work yet.
- Of the 4 orchestrator/planner agents at the top of the source's coordination hierarchy
  (`sp-deployment-planner`, `sp-migration-agent`, `sp-migration-orchestrator`, `sp-wave-orchestrator`),
  **none exist in the destination and none were even attempted in Phase 9** — they are the most
  CMAT-literal-dense files in the whole audit (14/3/36/161 literals respectively) and would need
  substantial rewrites, not simple genericization passes.
- `sp-running-sharegate-jobs` correctly straddles two classifications in one skill folder: two of
  its three scripts require a commercial ShareGate license (`NOT_RECOMMENDED`, explicitly flagged
  per this audit's instructions, not silently proposed) while the third (`combine-preview.ps1`) has
  zero ShareGate/tenant dependency and is already ported as `compose-page-preview`.
- 14 of the 35 skills are confirmed `PLANNED_WITH_NO_IMPLEMENTATION` in the source itself (no
  backing script) — these are honest gaps in the *source* repo, not missed extraction opportunities.
- The single largest remaining onboarding surface by file count is `sp-migrating-content`'s
  wave0a–9 sequence — already fully covered by the `.ps1` audit's `waves/`, `calendars/`, and
  `lib/` tables, and already tracked as the `sharepoint-provisioning`/`sharepoint-content-migration`
  "executor missing" gap in `.agent/map-debt.md`. This pass adds no new information there beyond
  confirming the skill-level framing matches the file-level framing.
