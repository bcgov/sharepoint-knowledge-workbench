# Phase 6 Plan Scaffold — Multi-Runtime Capability Model

> **Planning status:**
> **Task 0: `AUTHORIZED_AND_IN_PROGRESS`.**
> **Tasks 1–12: `NOT_AUTHORIZED_UNTIL_TASK_0_EXIT_GATE`.**
> Tenant-dependent details, exact repository paths, commands, identities, field types, licensing,
> and platform behavior in Tasks 1–12 must be replaced with observed evidence before execution of
> those tasks.

## Planning discipline

- Run `superpowers:brainstorming` before finalizing design decisions.
- Run repository reconnaissance against current files and contracts.
- Use `superpowers:writing-plans` only after the specification is reviewed.
- Use a dedicated phase branch/worktree.
- Keep planning separate from implementation.
- Use `CONFIRMED`, `RECOMMENDED`, `PROVISIONAL`, `DEFERRED_UNTIL_EVIDENCE`, `BLOCKED`, and `RESEARCH` explicitly.
- Preserve package-only/manual paths until an approved identity and write path exist.
- Store durable evidence in tracked locations, not ignored `.superpowers/` scratch directories.
- Start with the cheapest capable agent and escalate only for architecture, ambiguity, security, failed tests, or contradictory evidence.

## Entry gate

Stop unless two real runtimes implement the same capability and have evaluation evidence. Phase 4
produced one real native SharePoint runtime for `review-manual-topics`. Phase 6 Task 0 is
explicitly authorized to create the missing repository/Claude runtime from the same proven
capability intent and to establish the `sharepoint-agents-and-skills` plugin foundation. Tasks
1–12 begin only after Task 0 proves both runtimes exist and have evaluation evidence.

**Revision note (2026-08-03):** the entry gate is currently `SECOND_RUNTIME_REQUIRED` — see
`docs/superpowers/specs/phase-6-multi-runtime-capability-model-spec.md` Section 1 for the verified
evidence review. This is not a speculative runtime invented only to satisfy a gate — it is a
previously requested, evidenced capability derived from the deployed Phase 4 skill. Tasks 1–12
below remain gated and unstarted until Task 0 closes.

## Task 0 — SharePoint Agent, Skill, Template, and Reusable Artifact Foundation

**Revision history:** replaces the earlier "Task 0a" draft (2026-08-03), itself a correction of
an incomplete first pass that scoped only the capabilities already convenient to migrate. This is
the complete Task 0 — zero `REQUIRES_HUMAN_DECISION` items, zero `TBD` deliverables, zero
provisional dispositions remain. Incorporates findings from this session's own audit of
`tools/phase-3-*`/`phase-4-*`/`phase-5-*` and `docs/research/` (`diagnose-sharepoint-library.ps1`,
the two diverged `provision-agentassets.ps1` copies — resolved, Phase-4 copy canonical —
`get-agent-resource-identifiers`, and the distinct write-capable `review-manual-topics-metadata`
skill — resolved, `RETAIN_AS_PHASE_EVIDENCE`, excluded from Task 0), cross-checked against an
independent GPT-5.6 review.

**Status note:** some subtasks were already started under the prior "Task 0a" numbering before
the STOP instruction — `review-manual-topics`'s native-runtime `git mv`, and generalized moves of
`deploy-and-verify-skill.ps1`, `inventory-skills.ps1`, `verify-agentassets-ready.ps1`,
`verify-agentassets-artifact.ps1`, `task-8a-reconcile-deployed-skill.ps1` →
`reconcile-deployed-skill.ps1`, and the two backup scripts. Marked **done**/**partially done**
inline below; nothing further has been implemented since the STOP.

Task 0 completes before Task 1 (shared-capability derivation) begins.

### Task 0.1 — Create `sharepoint-agents-and-skills`

- Create the real plugin — **partially done** (`scripts/`, `skills/review-manual-topics/` exist;
  `.claude-plugin/plugin.json`, `plugin.yaml`, `README.md` not yet written).
- Record that it may contain generic platform capabilities and clearly labelled configured
  solution skills: `PLUGIN_MAY_CONTAIN_REUSABLE_PLATFORM_CAPABILITIES_AND_CONFIGURED_SOLUTION_
  SKILLS` (already resolved in `docs/superpowers/specs/2026-08-02-sharepoint-agents-and-skills-
  plugin-design.md`).
- Create only folders backed by actual implementation.
- Add manifests, README, tests, and installer metadata.

### Task 0.2 — Migrate `review-manual-topics`

- `git mv` the existing skill from Phase 4 tools — **done**
  (`tools/phase-4-native-sharepoint-skills/skills/review-manual-topics/` →
  `plugins/sharepoint-agents-and-skills/skills/review-manual-topics/`).
- Preserve Phase 4 evidence and historical references — **done**.
- Keep one canonical editable `SKILL.md` — **done**.
- Label it `CONFIGURED_SOLUTION_SKILL` and `CEIS_SPECIFIC` — **done** (recorded in the design
  doc's ownership decision).

### Task 0.3 — Add repository runtime

- Implement `review_manual_topics.py` — **paused, not yet built.**
- Preserve one-primary-topic plus maximum-two-related-topics boundary.
- Preserve review-only and prohibited-action rules.
- Reuse adapted Phase 4 evaluations.
- Perform no tenant writes.

### Task 0.4 — Native-skill authoring and packaging

Implement:

- `create-sharepoint-native-skill` — new build; use `create-test-skill.ps1` only as experimental
  source evidence (a disposable test fixture, not reviewed for reusability — do not extract from
  it uncritically).
- `deploy-sharepoint-native-skill` — from `deploy-and-verify-skill.ps1`, `inventory-skills.ps1`
  (moved/generalized, **not yet packaged as a skill**).
- `verify-sharepoint-native-skill` — from `verify-agentassets-artifact.ps1`,
  `task-8a-reconcile-deployed-skill.ps1` (extracted/generalized to `reconcile-deployed-skill.ps1`
  — extraction **done**, packaging pending).
- `rollback-sharepoint-native-skill` — from `rollback-skill-deployment.ps1` (moved, **not yet
  packaged**; already had the `-Execute`/`-ConfirmExactTarget` safety-gate pattern).
- `inventory-and-validate-agentassets` — from `verify-agentassets-ready.ps1` (moved/generalized,
  **not yet packaged**), plus two findings from this session's deeper audit: (1)
  `diagnose-sharepoint-library.ps1` — a read-only library/content inspector, absent from the
  original design doc's extraction table entirely; folds in here as a diagnostic sub-capability;
  (2) `provision-agentassets.ps1`, which existed as **two diverged copies**
  (`tools/phase-3-*` vs. `tools/phase-4-*`, confirmed different SHA-256). **Resolved (2026-08-03):
  Phase-4's version is the canonical source** — it adds placeholder-value detection (retained) on
  top of Phase-3's base behavior. The Phase-3-config fallback is **not retained**: the canonical
  script requires an explicit `-ConfigPath` (or this repo's approved configuration-resolution
  method) rather than silently falling back to a different phase's config file. Both original
  scripts (`tools/phase-3-sharepoint-discovery/provision-agentassets.ps1`,
  `tools/phase-4-native-sharepoint-skills/deployment/scripts/provision-agentassets.ps1`) are
  preserved as historical evidence, disposition `RETAIN_AS_PHASE_EVIDENCE`.

Separate creation from deployment: `create-sharepoint-native-skill` produces a validated
native-skill source package; it does not deploy unless `deploy-sharepoint-native-skill` is
separately invoked.

### Task 0.5 — Native-skill backup and restoration

Implement:

- `backup-sharepoint-native-skills` — from Phase 5's `backup-skills-and-templates.ps1`
  (generalized to `backup-sharepoint-native-skills.ps1`, **not yet packaged as a skill**).
- `restore-sharepoint-native-skills` — **no existing implementation; new build required.**

Include templates and related `AgentAssets` artifacts where applicable.

### Task 0.6 — Agent creation and maintenance

Implement:

- `create-sharepoint-agent`
- `update-sharepoint-agent` — previously missing entirely; updating an existing agent and
  changing grounding sources must not require recreating the agent.
- `configure-sharepoint-agent-knowledge` — previously left `REQUIRES_HUMAN_DECISION` /
  `PROVISIONAL_SKILL_PENDING_DISTINCT_USER_INTENT` in the design doc; now `IMPLEMENT_NOW`.
  `task-9-retrieve-topic-metadata.ps1`'s grounding-adjacent capability folds in here rather than
  staying research-only.
- `backup-sharepoint-agents` — from Phase 5's `backup-existing-agents.ps1` (generalized, **not
  yet packaged as a skill**).
- `restore-sharepoint-agents` — **no existing implementation; new build required**, including a
  `get-agent-resource-identifiers` sub-capability found in this session's deeper audit (extract
  `site_id`/`web_id`/`list_id`/`unique_id` from a working reference agent —
  `phase-4-agent-format-learning-journal.md` and `PHASE-4-SHAREPOINT-AGENTS-CRITICAL-LEARNINGS.md`
  document this as the actual repeatedly-used manual method for fixing two separate site-isolation
  bugs; never scripted as its own reusable capability until now).

Extract and parameterize real reusable behavior from Phase 3–5 experiments. Do not promote
experimental scripts unchanged — retain the 5 `create-*-agent.ps1` scripts as Phase evidence.

**Excluded capability — the write-capable metadata skill (resolved 2026-08-03).** A second,
UI/Copilot-generated skill also named `review-manual-topics` exists, found in this session's
deeper audit of `field-note-sharepoint-agentassets-review-manual-topics-skill.md` and
`PHASE-4-SHAREPOINT-AGENTS-CRITICAL-LEARNINGS.md` Part 4. It is a genuinely different capability
from ours: metadata-completeness review, **write-capable**, creates `Content Review` list items
(ours is editorial, read-only) — not a variant of `review-manual-topics`, a distinct capability
that happens to share its name. **Disposition: `RETAIN_AS_PHASE_EVIDENCE`.** Not migrated,
packaged, implemented, or deployed as part of Task 0. Preserved as-is at
`tools/phase-3-sharepoint-discovery/skills/reference-real-skill-review-manual-topics.SKILL.md`.
If ever revived in a future task, its name is `review-manual-topics-metadata` (disambiguated from
the read-only editorial skill this plugin actually implements). Excluded from the Task 0
capability table and from the 15-skill exit count below.

### Task 0.7 — Agent templates

Implement:

- `create-sharepoint-agent-template` — produces a reusable template describing: agent purpose,
  description, instruction structure, answer boundaries, refusal behavior, citation expectations,
  knowledge-source placeholders, conversation starters, native-skill references, output style,
  governance metadata, template version.
- `apply-sharepoint-agent-template` — applies an existing template to a named agent configuration.

Template creation is distinct from agent creation. Agent creation may consume an existing
template through `-AgentTemplatePath`.

### Task 0.8 — Formatting and output templates

Add only templates supported by Phase 3–5 evidence: agent instruction template; refusal and
answer-boundary template; answer-format template; native-skill instruction template; native-skill
structured-output template; review findings template; backup manifest templates; evidence/result
template.

Use `assets/templates/generic/` and `assets/templates/solutions/standard-manual/`. Do not create speculative
empty templates. Templates separate required semantic sections, optional sections,
runtime-specific presentation, placeholders, and validation rules.

### Task 0.9 — Template validation

Validate: required fields; schema versions; unresolved placeholders; missing resources; embedded
secrets; hard-coded tenant values in generic templates; answer/refusal boundaries; output
sections. Include negative-control tests.

### Task 0.10 — Parameterization and configuration

Apply: root `config.psd1` for connection/authentication only (`SiteUrl`, `ClientId`, `TenantId`,
authentication mode, conditional certificate details); explicit parameters for operations; no
hidden agent, skill, template, path, overwrite, or evidence settings; dry-run and write gates
where applicable. (Does not reopen the deferred multi-document destination-configuration design —
`config.psd1` stays the same single-file, per-plugin pattern Phase 4/5 already used.)

### Task 0.11 — Thin Phase wrappers

Replace duplicated Phase 4/5 tenant operations with genuine wrappers calling canonical plugin
scripts.

Review at minimum:

- Task 8 deployment (`task-8-deploy-review-manual-topics.ps1`) — **done.**
- Task 8A reconciliation (`task-8a-reconcile-deployed-skill.ps1`) — canonical extraction **done**
  (`reconcile-deployed-skill.ps1`); the original `tools/` path's thin-wrapper conversion is
  **still pending**.
- Task 12 rollback (`task-12-rollback.ps1`) — **done** (previously an unguarded permanent-delete
  script; replaced with a call to the guarded canonical `rollback-skill-deployment.ps1`).
- `rollback-skill.ps1` — **done.**
- Backup wrappers (`backup-existing-agents.ps1`, `backup-skills-and-templates.ps1`) — **done.**

### Task 0.12 — Preserve Phase evidence

Keep evaluations, fixtures, reports, captured responses, research experiments, and genuine thin
wrappers under `tools/`.

No canonical reusable implementation or installable `SKILL.md` may remain stranded under `tools/`.

### Task 0.13 — Packaging and symlinks

- Plugin-root canonical resources.
- Managed file-level links through `symlink_manager.py`.
- Installer-produced hard copies.
- No manual links or duplicate editable source.
- Installed skills must work without `tools/` or repository-root paths.

### Task 0.14 — Verification and review

Run: plugin tests; adapted Phase 4 evaluations; repository-runtime evaluations; template tests;
agent/native-skill lifecycle tests; backup/restore tests; symlink validation; isolated
installation; installed-resource verification; tools-placement scan; relevant regression suites.

Produce the migration ledger and focused review bundle. This subsumes the prior standalone
"verify gate and select capability" task — its runtimes/owners/operational-status/versions/
artifacts/evaluations record becomes part of this verification's output.

### Required Task 0 exit gate

Task 0 closes only when:

- all 30 installed skill names are implemented and packaged — 15 under `sharepoint-agents-and-
  skills` (`review-manual-topics` counts as one skill name with two runtime implementations —
  native SharePoint and repository/Claude — not two skill names; the excluded write-capable
  metadata skill, disposition `RETAIN_AS_PHASE_EVIDENCE`, is not part of this count) plus 5 under
  `sharepoint-content-publication` (Task 0.15) plus 7 under `structured-content-rendering`
  (Task 0.16) plus 3 under `workbench-setup` (Task 0.17 — `initialize-publication-profile` is
  absorbed into `initialize-document-workflow`, not a fourth standalone skill);
- `review-manual-topics` has both native and repository runtime evidence;
- applicable reusable code is no longer stranded under `tools/`;
- Phase wrappers contain no duplicated reusable tenant logic;
- manifests, symlinks, installer behavior, tests, and documentation pass;
- a focused external-review bundle is accepted.

### Complete Task 0 capability table

| # | Skill | Existing source | Implementation method | Deliverable | Tests | Final destination |
|---|---|---|---|---|---|---|
| 0.2 | `review-manual-topics` (native) | `tools/phase-4-native-sharepoint-skills/skills/review-manual-topics/` | `git mv`, no rewrite — **done** | `SKILL.md`, README | Phase 4 evaluation suite (existing) | `plugins/sharepoint-agents-and-skills/skills/review-manual-topics/` |
| 0.3 | `review-manual-topics` (repository/Claude) | none | new build — deterministic topic resolver + skill instructions | `scripts/review_manual_topics.py`, `SKILL.md` section | adapted Phase 4 evals + new unit tests | same skill folder, repository-runtime section |
| 0.4 | `create-sharepoint-native-skill` | `create-test-skill.ps1` (experimental evidence only) | extract & parameterize | `scripts/create-sharepoint-native-skill.ps1`, `SKILL.md` | new unit/dry-run tests | `plugins/sharepoint-agents-and-skills/skills/create-sharepoint-native-skill/` |
| 0.4 | `deploy-sharepoint-native-skill` | `deploy-and-verify-skill.ps1`, `inventory-skills.ps1` | package existing (moved/generalized) — scripts **done**, packaging pending | `SKILL.md`, symlinked scripts | existing script behavior + new packaging tests | `plugins/sharepoint-agents-and-skills/skills/deploy-sharepoint-native-skill/` |
| 0.4 | `verify-sharepoint-native-skill` | `verify-agentassets-artifact.ps1`, `task-8a-reconcile-deployed-skill.ps1` → `reconcile-deployed-skill.ps1` | extract & parameterize — extraction **done**, packaging pending | `SKILL.md`, symlinked scripts | existing + new packaging tests | `plugins/sharepoint-agents-and-skills/skills/verify-sharepoint-native-skill/` |
| 0.4 | `rollback-sharepoint-native-skill` | `rollback-skill-deployment.ps1` | package existing (moved) | `SKILL.md`, symlinked script | existing safety-gate tests + new packaging tests | `plugins/sharepoint-agents-and-skills/skills/rollback-sharepoint-native-skill/` |
| 0.4 | `inventory-and-validate-agentassets` | `verify-agentassets-ready.ps1`, `diagnose-sharepoint-library.ps1`, `provision-agentassets.ps1` (Phase-4 copy canonical, resolved) | package existing + extract canonical `provision-agentassets` (placeholder-detection retained, Phase-3-config fallback removed, explicit `-ConfigPath` required) | `SKILL.md`, symlinked scripts | existing + new packaging tests | `plugins/sharepoint-agents-and-skills/skills/inventory-and-validate-agentassets/` |
| 0.5 | `backup-sharepoint-native-skills` | `backup-skills-and-templates.ps1` | package existing (generalized) | `SKILL.md`, symlinked script | existing + new packaging tests | `plugins/sharepoint-agents-and-skills/skills/backup-sharepoint-native-skills/` |
| 0.5 | `restore-sharepoint-native-skills` | none | new build (mirrors backup, safety-gated) | `scripts/restore-sharepoint-native-skills.ps1`, `SKILL.md` | new unit + dry-run tests | `plugins/sharepoint-agents-and-skills/skills/restore-sharepoint-native-skills/` |
| 0.6 | `create-sharepoint-agent` | 5 experimental `create-*-agent.ps1` scripts | extract & parameterize (design doc Section 4 matrix); originals `RETAIN_AS_PHASE_EVIDENCE` | `scripts/create-sharepoint-agent.ps1`, `SKILL.md` | new unit/dry-run tests | `plugins/sharepoint-agents-and-skills/skills/create-sharepoint-agent/` |
| 0.6 | `update-sharepoint-agent` | none | new build | `scripts/update-sharepoint-agent.ps1`, `SKILL.md` | new unit/dry-run tests | `plugins/sharepoint-agents-and-skills/skills/update-sharepoint-agent/` |
| 0.6 | `configure-sharepoint-agent-knowledge` | `items_by_url`/`capabilities` blocks embedded in agent experiments; `task-9-retrieve-topic-metadata.ps1` | extract & parameterize | `scripts/configure-sharepoint-agent-knowledge.ps1`, `SKILL.md` | new unit/dry-run tests | `plugins/sharepoint-agents-and-skills/skills/configure-sharepoint-agent-knowledge/` |
| 0.6 | `backup-sharepoint-agents` | `backup-existing-agents.ps1` | package existing (generalized) | `SKILL.md`, symlinked script | existing + new packaging tests | `plugins/sharepoint-agents-and-skills/skills/backup-sharepoint-agents/` |
| 0.6 | `restore-sharepoint-agents` | none (+ `get-agent-resource-identifiers` sub-capability, previously manual-only) | new build | `scripts/restore-sharepoint-agents.ps1`, `scripts/get-agent-resource-identifiers.ps1`, `SKILL.md` | new unit + dry-run tests | `plugins/sharepoint-agents-and-skills/skills/restore-sharepoint-agents/` |
| 0.7 | `create-sharepoint-agent-template` | none (only the `-AgentTemplatePath` idea) | new build | `scripts/create-sharepoint-agent-template.ps1`, `SKILL.md` | new unit tests | `plugins/sharepoint-agents-and-skills/skills/create-sharepoint-agent-template/` |
| 0.7 | `apply-sharepoint-agent-template` | none | new build | `scripts/apply-sharepoint-agent-template.ps1`, `SKILL.md` | new unit tests | `plugins/sharepoint-agents-and-skills/skills/apply-sharepoint-agent-template/` |

This table is 15 rows for 14 skill names plus `review-manual-topics`'s two runtime rows (0.2 native
+ 0.3 repository/Claude) = **15 installed skill names under `sharepoint-agents-and-skills`**. The
write-capable metadata skill (`review-manual-topics-metadata`, disposition `RETAIN_AS_PHASE_
EVIDENCE` — see the Task 0.6 note above) is excluded from this table and from the count; it is not
implemented, packaged, migrated, or deployed as part of Task 0. Zero `REQUIRES_HUMAN_DECISION`
items, zero `TBD` deliverables, and zero provisional dispositions remain in this table. Combined
with Task 0.15's 5 `sharepoint-content-publication` skills, Task 0.16's 7 `structured-content-
rendering` skills, and Task 0.17's 3 `workbench-setup` skills, Task 0's complete total is **30
installed skill names**.

**Out of scope for Task 0:** shared-capability-spec derivation, adapters, drift detection,
SharePoint tenant writes, deployment of any skill to a live tenant.

### Task 0.16 — Structured-content rendering

**Reassigned into Phase 6 Task 0 (2026-08-03), reversing the prior assignment to Phase 5.5B.**
Earlier revisions of this plan pointed to Phase 5.5B, Subphase 5.5B.2 for this capability; per
explicit direction this session, it is pulled into Phase 6 Task 0 instead. Phase 5.5B's copy of
this content has been removed from the master roadmap to avoid a duplicate/contradictory record —
this is now the single source.

**Owner:** `plugins/structured-content-rendering/`. Converts a structured-content package into
output artifacts. Not `sharepoint-agents-and-skills` (agent/native-skill lifecycle) and not
`sharepoint-content-publication` (consumes rendered artifacts, does not render them).

Implement and package:

- `render-multipage-markdown` — **substantially exists** (`skills/render-structured-content/`,
  `scripts/renderers/multipage_markdown.py`); packaging/naming needs verification against this
  skill name only, not a new build.
- `render-sharepoint-aspx` — new renderer. Implement per the `Renderer` protocol contract
  (`supported_manifest_versions`, `render(package, output_dir) -> RenderResult`), reusing the
  confirmed `Add-PnPPage`/`Add-PnPPageTextPart`-compatible HTML generation approach from Phase 3.0
  §15 (raw `.aspx` upload is `Access denied` — output must be structured for the page-creation
  API, not a raw file). Real, evidenced need: Phase 3.0's ASPX/modern-page conversion experiment
  (`docs/research/research-experimentation/tenant-discovery/field-note-sharepoint-write-capability-discovery.md` §15) and
  Phase 5's ASPX-vs-Markdown grounding comparison
  (`docs/research/knowledge-discovery-retrieval/field-note-aspx-vs-markdown-grounding.md`).
- `create-markdown-rendering-template` — new build, backed by real Phase 1–2 CEIS rendering
  evidence (`runs/ceis-manual-v2/`).
- `create-aspx-rendering-template` — new build, backed by Phase 3.0 §15's confirmed modern-page
  structure.
- `validate-rendering-template` — new build: schema/placeholder/required-section/asset/profile-
  compatibility validation, with negative-control tests.
- `validate-rendered-output` — `renderers/validate_rendered.py` exists for Markdown; extend for
  ASPX.
- `compare-rendered-output` — golden-master comparison pattern exists (Phase 2 Subphase 2.5.4);
  package as its own standalone skill.

**Template-family distinction (do not combine):** these are *rendering* templates — Markdown
document/page structure, ASPX page structure, navigation, headings/sections, metadata placement,
media placement, links, human-facing layout — under
`plugins/content-rendering/assets/templates/{generic,solutions/standard-manual}/{markdown,aspx}/`.
Distinct from Task 0.7/0.8's *agent/native-skill* templates (agent instructions, native-skill
instructions, agent answer formatting, review-result formatting). Do not merge the two template
systems.

**Tests/acceptance:** TDD per repo standard; `render-sharepoint-aspx` and `render-multipage-
markdown` pass fidelity/golden-master validation; registers with the existing renderer registry
without modifying it; `validate-rendering-template` correctly rejects each planted defect class.

### Task 0.17 — `workbench-setup` foundational skills

**Added 2026-08-03.** Previously identified for a proposed `workbench-setup` plugin in
`docs/superpowers/specs/2026-08-02-multi-document-destination-configuration-design.md` Section 8
(design-complete, `workbench-setup` not yet created) but absent from Phase 6 Task 0 until now.

**Owner:** `plugins/workbench-setup/` (new plugin — an authorized exception to the Global Gating
Rule limiting new plugins, per that design's own Section 8 scoping). **Authoring constraint
(corrected 2026-08-03):** an earlier version of this section wrongly classified this plugin's
skills as Category 1 (marketplace-style, authored in the sibling `agent-plugins-skills` monorepo).
That was a mistake — it conflated using the `marketplace-manager` skill (installed *from*
`agent-plugins-skills` into this repo) as a *procedure* for `marketplace.json` updates with
authoring the plugin's actual code *in* that repo. `workbench-setup` is a workbench-specific
plugin, same as `sharepoint-agents-and-skills` and `sharepoint-content-publication` (this repo's
own `plugins/` convention, per CLAUDE.md's "Plugin-Local Resource Sharing") — written directly in
this repo. The `marketplace-manager` skill is consulted only for the applicable
`marketplace.json` registration step, not as an indicator of code ownership.

Implement and package:

- `setup-sharepoint-connection` — creates the root, git-ignored `config.psd1` from the plugin's
  canonical `assets/config.psd1.example`. Generating the file is the default action and never
  connects to anything; a separate, explicit `-TestConnection` flag performs read-only validation
  only after opt-in. Mandatory: `SiteUrl`, `TenantId`, `ClientId`, `AuthenticationMode`.
- `initialize-document-workflow` — the broader interactive intake wizard (source-document
  identity, processing stages, requested output formats — only implemented renderer profiles
  offered as executable choices, publication locations, agent-grounding representations,
  governance/evidence settings, outstanding decisions). Produces
  `document-workflows/<DocumentId>.workflow.psd1` and
  `publication-profiles/<DocumentId>.publication.psd1`. Execution boundary: ask → propose
  defaults → validate → display resolved configuration → write profile files → stop. Must not
  extract documents, render content, connect to/modify SharePoint, or create agents/skills in
  this version.
- `validate-workbench-environment` — backed by the design's `validate_workflow_configuration.py`.
  Validates written configuration/profile files before they're consumed by other plugins.

**Correction on the source list — `initialize-publication-profile`:** the design doc names this as
a narrower, earlier-conceived skill but explicitly states it is **superseded/absorbed** into
`initialize-document-workflow`'s broader wizard flow, "not duplicated as a separate skill." It is
**not** a fourth standalone skill alongside the three above — its question set is inside
`initialize-document-workflow`. Recorded here so this isn't silently dropped without explanation.

**Tests/acceptance:** written profile/config files validate cleanly; `initialize-document-
workflow` performs zero tenant I/O, zero document extraction, and zero rendering in this version;
`setup-sharepoint-connection` performs zero connection unless `-TestConnection` is explicitly
passed.

### Task 0.15 — Complete `sharepoint-content-publication`

**Owner:** `plugins/sharepoint-content-publication/`. Consumes rendered artifacts (from
`structured-content-rendering`, per the boundary above) and uploads files/media, creates/updates
SharePoint pages, validates observed tenant state, reconciles expected-vs-actual publication, and
performs exact-target rollback. Does not own content rendering or rendering templates.
`sharepoint-agents-and-skills` owns agents, agent templates, `AgentAssets`, and native skills only
— does not own content rendering or publication either.

Implement and package:

- `publish-markdown-to-sharepoint`
- `publish-aspx-to-sharepoint`
- `reconcile-sharepoint-publication`
- `validate-sharepoint-publication`
- `rollback-sharepoint-publication`

**Existing source evidence to inventory and promote** (do not move Phase evidence, results,
fixtures, or research reports — use thin Phase wrappers where historical reproduction requires old
paths): `plugins/sharepoint-content-publication/scripts/{sharepoint_cli.py, sharepoint_dry_run.py,
sharepoint_package.py, sharepoint_reconcile.py}` (existing package-only/zero-tenant-I/O Python
implementation — real upload/page-creation/reconciliation/rollback logic still needs to be added on
top of this), `tools/phase-3-*/`, `tools/phase-4-*/`, `tools/phase-5-sharepoint-knowledge-agent-
pilot/upload-rendered-markdown.ps1`, existing page creation/update scripts (the `Add-PnPPage`/
`Add-PnPPageTextPart` pattern confirmed working in Phase 3.0 §15 — raw `.aspx` upload is `Access
denied`), and any existing publication reconciliation/rollback scripts.

**Parameterization** — root config (`SiteUrl`, `ClientId`, `TenantId`, authentication context) plus
explicit operation parameters, only as applicable per script: `ConfigPath`,
`PublicationProfilePath`, `DocumentId`, `SourcePath`, `LibraryName`, `TargetFolder`, `PageName`,
`MediaFolder`, `Overwrite`, `DryRun`, `Execute`, `ConfirmExactTarget`, `EvidencePath`.

**Safety** — exact resolved target displayed before writes; dry-run where practical; explicit
`Execute` gate; exact confirmation string for rollback/destructive actions; post-write
verification; package-scoped reconciliation (no effect on another `DocumentId`); no hard-coded
CEIS, tenant, library, folder, page, or agent values in generic scripts.

**Plugin completion** — `sharepoint-content-publication` receives: `plugin.json`, `plugin.yaml`,
`README`, canonical plugin-root scripts, the five `SKILL.md` files, tests, managed symlinks,
installer hard-copy verification, isolated installation proof. Retains its
`TRANSITIONAL_HOLDING_LOCATION` status until these gates pass; classified as an implemented plugin
afterward.

| Skill | Source artifacts | Implementation method | Destination | Parameters | Tests | Acceptance criteria |
|---|---|---|---|---|---|---|
| `publish-markdown-to-sharepoint` | `sharepoint_package.py` (package-building basis), `upload-rendered-markdown.ps1` | extend package-only basis with real upload call | `plugins/sharepoint-content-publication/skills/publish-markdown-to-sharepoint/` | `ConfigPath`, `SourcePath`, `LibraryName`, `TargetFolder`, `MediaFolder`, `Overwrite`, `DryRun`, `Execute`, `EvidencePath` | new unit tests (dry-run) + tenant-write tests | exact resolved target displayed pre-write; dry-run default; uploads to exact target only |
| `publish-aspx-to-sharepoint` | Phase 3.0 §15's confirmed `Add-PnPPage`/`Add-PnPPageTextPart` pattern; existing page creation/update scripts | new build using the confirmed page-creation API (not raw file upload) | `plugins/sharepoint-content-publication/skills/publish-aspx-to-sharepoint/` | `ConfigPath`, `SourcePath`, `PageName`, `TargetFolder`, `Overwrite`, `DryRun`, `Execute`, `EvidencePath` | new unit tests (dry-run) + tenant-write tests | pages created/updated via the confirmed API; dry-run default |
| `reconcile-sharepoint-publication` | `sharepoint_reconcile.py` — exists, zero tenant I/O | package existing module as an installable skill | `plugins/sharepoint-content-publication/skills/reconcile-sharepoint-publication/` | `ConfigPath`, `PublicationProfilePath`, `DocumentId`, `EvidencePath` | existing unit tests + new packaging tests | reconciles expected vs. actual publication, package-scoped to one `DocumentId` |
| `validate-sharepoint-publication` | `sharepoint_dry_run.py` (`validate_upload_package`) — partial basis | extend to post-deployment validation | `plugins/sharepoint-content-publication/skills/validate-sharepoint-publication/` | `ConfigPath`, `DocumentId`, `EvidencePath` | existing + new unit tests | validates files, pages, metadata, links, media, and publication identity against observed tenant state |
| `rollback-sharepoint-publication` | none — new build; mirrors the safety-gate pattern already proven in `sharepoint-agents-and-skills`'s `rollback-skill-deployment.ps1` | new build with exact-target confirmation | `plugins/sharepoint-content-publication/skills/rollback-sharepoint-publication/` | `ConfigPath`, `DocumentId`, `ConfirmExactTarget`, `DryRun`, `Execute`, `EvidencePath` | new unit tests (dry-run) + tenant-write tests | dry-run default; requires exact confirmation string; post-write verification; no effect on another `DocumentId` |

**Task 0 exit-gate addition:** Task 0 cannot close until, in addition to the existing exit-gate
items — all five publication skills are implemented and packaged; reusable publication code is no
longer stranded under `tools/`; Phase wrappers contain no duplicate reusable publication logic;
Markdown upload is independently reusable; ASPX publication is independently reusable;
reconciliation, validation, and rollback tests pass; installed skills work without `tools/` or
repository-root paths.

## CMAT overlap check (2026-08-03) — no migration performed

Before further Task 0 implementation, the 30-skill capability set was cross-checked against the
CMAT repository's (`jag-csb-cmat-sharepoint-online`) `sharepoint-migration` plugin to avoid
recreating already-proven capability. Full comparison table, per-skill dispositions, and the
Phase 9 destination-plugin-matching rule live in
`docs/superpowers/specs/phase-9-reusable-sharepoint-plugin-extraction-spec.md` §8c — not
duplicated here. Summary: no Phase 6 skill's scope was widened or narrowed based on CMAT; where
CMAT has a richer implementation (ASPX conversion, content upload, link-integrity validation,
app-registration validation, full-schema migration), Phase 6 stays scoped to its own narrower
requirement now, with the richer capability recorded as a Phase 9 extraction candidate targeting
an *existing* destination plugin — no new plugin justified. `rollback-sharepoint-publication` has
no CMAT counterpart; confirmed genuinely new work. No CMAT file was read into, copied into, or
referenced as executable source for any Phase 6 script.

## Preserve Tasks 1–12

Tasks 1–12 remain the actual multi-runtime capability-model work. They must not begin until
Task 0 closes.

## Task 1 — Superpowers brainstorming on original intent

Recover the originating user intent, governance rules, and success criteria. Identify implementation coincidences and unresolved differences.

## Task 2 — Inventory both implementations

Map inputs, outputs, steps, permissions, error behavior, human gates, evidence, and limitations without yet deriving a shared contract.

## Task 3 — Draft the shared capability specification

Classify each proposed element as essential, target-specific, accidental, deferred, or rejected. Trace essential elements to original intent.

## Task 4 — Conduct adversarial intent-preservation review

Challenge the draft for lowest-common-denominator loss, shared accidental limitations, erased safety controls, and false equivalence.

## Task 5 — Build the common evaluation set

Write meaning-based cases both runtimes can execute. Include normal, negative, ambiguous, permission/safety, and human-approval cases where applicable.

## Task 6 — Run baseline evaluations

Execute the common set on both existing runtimes and disposition differences.

## Task 7 — Implement target adapters only where needed

Adapters expose the shared intent while declaring unsupported and target-specific behavior. Avoid unnecessary abstraction.

## Task 8 — Implement drift detection

Compare runtime results against common semantic expectations. Add deliberate drift and prove detection.

## Task 9 — Apply reuse-versus-specific decision rules

Make one real decision about what is shared, generated, adapted, or kept independent.

## Task 10 — Versioning and compatibility

Define shared-spec and adapter compatibility, migration, and deprecation behavior based on real versions.

## Task 11 — Exit evidence and review

Produce derivation trace, evaluations, drift proof, intent review, and decision record. Obtain explicit approval before merge.

## Task 12 — Runtime placement for content-lifecycle actions (Subphase 6.3)

**(Added from external review, 2026-08-02, GPT 5.6 — see
`docs/vision/resolved-question-ongoing-editing-and-agent-assisted-rendering-phase-placement.md`.)**
For each action in Phase 3 Stage 3.1.4's ongoing structured-content maintenance workflow, decide
whether an agent may only recommend it, a native skill may invoke approved deterministic tooling,
or a deterministic pipeline/workstation process must perform it. Write the preview-vs-authoritative
rule (agent-generated output is a non-authoritative preview unless it passes the deterministic
pipeline's own contracts/validation) and the per-runtime evidence/rollback matrix. Do not broaden
Phase 5.5B's deterministic-renderer-expansion scope to cover this. Output feeds a future Phase 6.5
entry gate; does not itself authorize that phase.

## Cost allocation

- Low-cost: inventories, trace tables, evidence packaging.
- Mid-tier: adapters, evaluation harness, drift detector.
- Strong reasoning: original-intent recovery, contract derivation, adversarial review, final decision.
