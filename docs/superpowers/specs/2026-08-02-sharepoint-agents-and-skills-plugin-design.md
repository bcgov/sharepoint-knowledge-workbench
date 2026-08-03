# `sharepoint-agents-and-skills` Plugin — Migration Design

```text
Status:            DESIGN_COMPLETE
Implementation:     NOT_AUTHORIZED
Plugin creation:    NOT_STARTED
File migration:     NOT_STARTED
Phase 5 impact:      SEPARATE PLANNING STREAM — DOES NOT RESET OR REPLACE PHASE 5 PROGRESS
```

Does not authorize file movement, plugin creation, skill creation, or tenant modification.
Produced per explicit instruction: "Proceed only with a migration design, not file movement
yet... Stop before moving files or creating the plugin." Builds on `docs/reports/
multi-document-destination-config/complete-artifact-classification.md` (the full artifact sweep,
still the evidence inventory of record) and supersedes only that document's tentative two-plugin
(`sharepoint-agents` / `sharepoint-native-skills`) framing with the decided single-plugin name
below.

## Decision (already made, recorded here for traceability)

One future plugin: **`sharepoint-agents-and-skills`**. Not two plugins. Not `sharepoint-knowledge`
(rejected as too vague — could mean content publication, search, grounding, authoring, or
knowledge management generally). Rationale: agents and native skills both use `AgentAssets`, share
connection/inventory/backup/restore/deployment/verification/rollback infrastructure, agent
configuration may reference native skills, and the repository does not yet justify two
independently versioned plugin lifecycles. Skills remain separate user intents *inside* one
plugin.

This decision **updates** `docs/vision/ai-assisted-structured-knowledge-workbench-broader-plan.md`'s
naming-reconciliation note (added 2026-08-02, near the top), which had flagged the `sharepoint-knowledge`
proposal as unresolved and explicitly warned against inventing an alternative name ad hoc. This is
not an ad hoc invention — it is a considered rejection of both the vision doc's original proposal
and the classification's tentative two-plugin split, recorded as its own decision. **The vision
doc's naming-reconciliation note itself needs a follow-up amendment** — see "Required specification
amendments" below.

## 1. Final artifact disposition matrix

Every artifact from `complete-artifact-classification.md`, mapped to its final destination.

### → `sharepoint-agents-and-skills` (reusable capability, once parameterized)

| Artifact | Extracted capability | Target skill (if any) |
|---|---|---|
| `tools/phase-4-native-sharepoint-skills/skills/review-manual-topics/{SKILL.md,README.md}` | **`RESOLVED` (2026-08-03) — see "Ownership decision required" below.** `PLUGIN_MAY_CONTAIN_REUSABLE_PLATFORM_CAPABILITIES_AND_CONFIGURED_SOLUTION_SKILLS` is the recorded decision. `review-manual-topics` is a `CONFIGURED_SOLUTION_SKILL` / `CEIS_SPECIFIC` owned by this plugin, labeled as such — not described as generic. It moves/is implemented as-is, no generalization pass required. | `skills/review-manual-topics/` |
| `inventory-skills.ps1` | Native-skill inventory query | `skills/deploy-sharepoint-native-skill/` (shared script) or its own `scripts/native-skills/` capability, exposed via `deploy-sharepoint-native-skill`'s supporting logic |
| `deploy-and-verify-skill.ps1` | Native-skill deployment + SHA-256 readback verification | `skills/deploy-sharepoint-native-skill/` |
| `task-8a-reconcile-deployed-skill.ps1` | **Corrected — do not move as-is (was listed as a direct move).** Verified by reading the file: it hard-codes a repository SHA-256 (`9586379f...`) as a default parameter, Phase 4 task language ("TASK 8A" banners), `review-manual-topics`-specific special-casing (`$isReviewManualTopics`), a Phase-3-config-fallback block, and direct frontmatter regex parsing. Extract a generic reconciliation capability instead — see the script parameter matrix's new entry. | `skills/verify-sharepoint-native-skill/` (backed by the extracted generic script, not this file) |
| `rollback-skill-deployment.ps1` | The real rollback implementation (has the `-Execute`/`-ConfirmExactTarget` safety gate) | `skills/rollback-sharepoint-native-skill/` |
| `verify-agentassets-artifact.ps1` | Verifies one artifact's presence/hash in `AgentAssets` | `skills/verify-sharepoint-native-skill/` |
| `verify-agentassets-ready.ps1` | Verifies `AgentAssets` library exists/ready before deployment | `scripts/agentassets/` (shared precondition check, used by multiple skills) |
| `provision-agentassets.ps1` (**both** the phase-3 and phase-4 copies — see "Requires human decision" below before this can actually move) | `AgentAssets` library provisioning | `scripts/agentassets/` |
| `backup-existing-agents.ps1` | Agent backup (once parameterized — see script parameter matrix) | `skills/backup-sharepoint-agents/` **or** `skills/backup-sharepoint-agent-assets/` — naming corrected below, not finalized |
| `backup-skills-and-templates.ps1` | Native-skill/template backup (once parameterized) | **Corrected — naming was wrong (was bundled under `backup-sharepoint-agents`, which does not describe backing up native skills/templates).** Either one renamed shared skill `backup-sharepoint-agent-assets/`, or two distinct skills `backup-sharepoint-agents/` + `backup-sharepoint-native-skills/` — see "Backup skill naming" below, not decided here. |
| `create-test-agent.ps1`, `create-corrected-agent.ps1`, `create-aspx-only-agent-test.ps1`, `create-updated-agent-sitepages.ps1` | **Not moved as-is.** A NEW parameterized `create-sharepoint-agent` script is designed from the pattern these four scripts demonstrate (see script parameter matrix) — the four originals stay in `tools/phase-4-*` as research/evidence of the pattern, per "treat custom agent experiments carefully" below | `skills/create-sharepoint-agent/`; `configure-agent-knowledge` is **provisional**, not a confirmed skill — see below |
| `task-9-retrieve-topic-metadata.ps1` | Agent-grounding-adjacent metadata query | Folds into `configure-agent-knowledge` support logic, or stays research-only — **requires human decision**, not resolved by this design (its capability is closer to a grounding-source diagnostic than agent lifecycle management proper) |

### Ownership decision — does this plugin permit solution-specific skills? `RESOLVED` (2026-08-03)

**Recorded decision:** `PLUGIN_MAY_CONTAIN_REUSABLE_PLATFORM_CAPABILITIES_AND_CONFIGURED_SOLUTION_SKILLS`.

`sharepoint-agents-and-skills` holds both generic platform tooling (agent creation, native-skill
deployment/verification/rollback) and CEIS-specific configured skills, side by side, clearly
labeled by kind. `review-manual-topics` is a `CONFIGURED_SOLUTION_SKILL` / `CEIS_SPECIFIC` skill
owned by this plugin — not generic, not described as such, moved/implemented as-is with no
generalization pass required. Generic platform scripts remain organizationally separate from
configured-solution-skill resources within the plugin (e.g. `scripts/` for shared platform
capabilities vs. a skill's own resources under its `skills/<skill>/` folder), but both live in this
one plugin.

### Backup skill naming — not finalized

`backup-sharepoint-agents` does not describe backing up native skills/templates. Choose one,
not decided here:

- One skill, renamed: `backup-sharepoint-agent-assets`
- Two skills, split by user intent: `backup-sharepoint-agents` + `backup-sharepoint-native-skills`

Either way, both stay inside the single `sharepoint-agents-and-skills` plugin — this is a skill-
naming/grouping decision, not a plugin-boundary decision.

### → `sharepoint-content-publication` (existing plugin, scope-expansion candidate — NOT approved by this design)

| Artifact | Note |
|---|---|
| `upload-rendered-markdown.ps1` | Per instruction: "Do not silently drop the script into that plugin. First amend its responsibilities, safety model, parameters, and tests." This design does **not** perform that amendment — it only records the target and the precondition. See "Required specification amendments" below. |

### → `workbench-setup` (future plugin, design-only per the separate multi-document-destination-configuration design)

| Artifact | Note |
|---|---|
| None yet | No script in this sweep implements root-config generation today; `workbench-setup`'s scope is specified in `docs/superpowers/specs/2026-08-02-multi-document-destination-configuration-design.md` Section 8, unchanged by this document. |

### `RETAIN_PHASE_EVIDENCE`

`tools/phase-3-sharepoint-discovery/{phase-3-0-tenant-discovery.ps1, push-aspx-experiment.ps1, run-phase3-tenant-pilot.ps1, find-ceis-location.ps1}`, its `skills/{example-skill-strict-format,reference-real-skill-review-manual-topics,v2-fewshot,v3-json,v4-template-ref,v5-list-libraries,v6-log-finding,v7-scoped-manual-qa,v8-cross-topic}.SKILL.md` and `{v4-output-template.txt,v5-assets-library-inventory-template.txt}`, its `agents/{pnp-uploaded-agent-format,ui-created-agent-format}.agent.json`; `tools/phase-4-native-sharepoint-skills/deployment/scripts/{probe-metadata-visibility.py, validate-phase4-exit-gate.py}`; all Phase 4/5 evaluation JSON, results, fixtures; `tools/phase-5-sharepoint-knowledge-agent-pilot/backups/**` (agent/skill backup snapshots — stay evidence even after the scripts that produced them move, per instruction: "Keep in Phase 5 tools: ... prototype evidence").

### `RETAIN_THIN_PHASE_WRAPPER`

`rollback-skill.ps1` only — confirmed via diff to be a literal one-line alias calling
`rollback-skill-deployment.ps1`, with no independent logic. `task-9-*` pending the human decision
above (not yet classified either way).

### `HISTORICAL_PHASE_IMPLEMENTATION_REQUIRING_REPLACEMENT`

**Corrected (was incorrectly listed as `RETAIN_THIN_PHASE_WRAPPER` above) — verified by reading
both files directly:**

- **`task-12-rollback.ps1`** — NOT a wrapper. It independently calls `Connect-PnPOnline`, searches
  `AgentAssets` for the target item, and calls `Remove-PnPListItem -Force` directly — no
  `-Execute` gate, no `-ConfirmExactTarget`, no recycle-bin behavior (unlike the real
  `rollback-skill-deployment.ps1`, which has all three). This is a separate, less-safe
  implementation, not a call into the guarded rollback capability. During migration, preserve the
  historical file path (Phase 4 evidence may require it) but replace its executable behavior with
  a genuine thin call to `rollback-skill-deployment.ps1`.

### `PHASE_SPECIFIC_DUPLICATED_IMPLEMENTATION_TO_REPLACE_WITH_THIN_WRAPPER`

- **`task-8-deploy-review-manual-topics.ps1`** — NOT currently a wrapper (corrected from the row
  above). Verified: it independently authenticates (including its own Phase-3-fallback logic,
  duplicated from `provision-agentassets.ps1`'s pattern), creates the target folder, uploads via
  `Add-PnPFile`, and reports success — it never calls `deploy-and-verify-skill.ps1`. Its
  "verification" is the **pre-upload source hash plus the `Add-PnPFile` return value**
  (`$hashMatch = $true` is hard-set after upload, not computed from a readback) — it does not
  download the deployed file and compare its hash post-upload, unlike the real
  `deploy-and-verify-skill.ps1`. The eventual thin wrapper must call that real deploy-and-readback
  script with Phase-4-specific arguments (skill name, source path) instead of duplicating the
  upload logic.

### `RETAIN_PHASE_HARNESS`

`tools/phase-4-native-sharepoint-skills/{evaluations/validate_cases.py, schemas/evaluation-case-schema.json, tests/*.py}`; `tools/phase-5-sharepoint-knowledge-agent-pilot/{evaluations/validate_cases.py, tests/test_evaluations_harness.py, evaluations/*.json, results/*.md}`.

### `HISTORICAL_ONLY`

`tools/phase-3-sharepoint-discovery/skills/reference-real-skill-review-manual-topics.SKILL.md` (a point-in-time copy of the real skill, not the source).

### `REQUIRES_HUMAN_DECISION`

1. **`provision-agentassets.ps1` (phase-3 vs. phase-4 divergence)** — confirmed different SHA-256, real diverged logic (phase-4's version adds placeholder-value detection + phase-3-config fallback). Which behavior becomes the plugin's canonical version, and whether the other's extra logic (the fallback) is a real requirement or phase-4-specific scaffolding, is not decided here.
2. **`task-9-retrieve-topic-metadata.ps1`'s domain** — agent-grounding-adjacent vs. a distinct diagnostic capability, not resolved.
3. **`upload-rendered-markdown.ps1`'s home** — blocked on the `sharepoint-content-publication` scope-amendment decision (design work only, not approval, per this document's own scope).
4. **`review-manual-topics`'s ownership** — whether `sharepoint-agents-and-skills` permits
   solution-specific configured skills (this one is explicitly CEIS-specific) or only generic
   platform capabilities. See "Ownership decision required" in Section 1 above. Blocks this
   skill's migration entirely until recorded.

## 2. Proposed plugin tree

**Corrected — Wave 0 no longer scaffolds empty taxonomy folders (see Section 7).** The tree below
shows the plugin's eventual full shape once all waves complete; it is not what Wave 0 creates.
Each `scripts/` subfolder below is created only in the wave that adds its first real script —
never as an empty placeholder ahead of implementation.

```text
plugins/sharepoint-agents-and-skills/
├── .claude-plugin/
│   └── plugin.json
├── plugin.yaml
├── README.md
├── scripts/
│   ├── connection/
│   ├── agentassets/
│   ├── agents/
│   ├── native-skills/
│   ├── backup/
│   ├── validation/
│   └── rollback/
├── references/
│   ├── agent-artifact-format.md
│   ├── native-skill-deployment.md
│   └── safety-boundaries.md
├── assets/
│   └── examples/
├── skills/
│   ├── review-manual-topics/
│   ├── create-sharepoint-agent/
│   ├── configure-agent-knowledge/
│   ├── backup-sharepoint-agents/
│   ├── deploy-sharepoint-native-skill/
│   ├── verify-sharepoint-native-skill/
│   └── rollback-sharepoint-native-skill/
└── tests/
```

## 3. Proposed skill list (only real implemented backing capability, no empty placeholders)

| Skill | Backed by (real artifact/pattern) | Ready to implement now, or blocked? |
|---|---|---|
| `review-manual-topics` | `tools/phase-4-native-sharepoint-skills/skills/review-manual-topics/SKILL.md` | **Blocked (corrected — was "Ready")** on the ownership decision in Section 1 — this skill is confirmed CEIS-specific, not generic; cannot move "as-is" until the plugin's solution-specific-skill policy is recorded |
| `deploy-sharepoint-native-skill` | `deploy-and-verify-skill.ps1`, `inventory-skills.ps1`, `verify-agentassets-ready.ps1` | Ready once parameterized (Section 4) |
| `verify-sharepoint-native-skill` | `verify-agentassets-artifact.ps1`, plus a **new generic reconciliation script extracted from** `task-8a-reconcile-deployed-skill.ps1` (corrected — that file itself does not move, per Section 1) | Ready once the extraction (Section 4's new parameter set) and `verify-agentassets-artifact.ps1`'s parameterization are both done |
| `rollback-sharepoint-native-skill` | `rollback-skill-deployment.ps1` (already has the safety-gate pattern) | Ready — least parameterization needed, already has `-ConfigFile`/`-ManifestFile`/`-Execute`/`-ConfirmExactTarget` |
| `create-sharepoint-agent` | Pattern demonstrated by the 4 `create-*-agent.ps1` research scripts, but **no single one of them is reusable as-is** — needs the new parameterized script designed in Section 4 before this skill has real backing | **Blocked** on new-script design, not just extraction |
| `configure-agent-knowledge` | Same 4 scripts' source-binding logic (the `capabilities`/`items_by_url` block) | **`PROVISIONAL_SKILL_PENDING_DISTINCT_USER_INTENT` (corrected — was "Blocked" implying eventual certainty).** Current evidence only shows source-binding logic embedded inside agent-creation experiments — it does not yet prove a separate update/reconfigure-after-creation user journey exists. Do not create this skill until that journey is independently demonstrated; agent creation may fully cover this need on its own. |
| `backup-sharepoint-agents` (or `backup-sharepoint-agent-assets` / split into two — see "Backup skill naming" in Section 1, not finalized) | `backup-existing-agents.ps1` + `backup-skills-and-templates.ps1` | Ready once parameterized **and** the naming/grouping decision above is made |

## 4. Script parameter matrix

For the **new** `create-sharepoint-agent` script (does not exist yet — designed here, not
extracted verbatim from any one of the 4 research scripts, since none of them is parameterized):

| Parameter | Source in root config / profile / explicit | Notes |
|---|---|---|
| `-SiteUrl` | Root config `Connection.SiteUrl` | |
| `-ClientId` | Root config `Connection.ClientId` | |
| `-TenantId` | Root config `Connection.TenantId` | |
| `-AgentName` | Explicit, mandatory | |
| `-AgentDescription` | Explicit, mandatory | |
| `-AgentInstructions` | Explicit, mandatory (or `-AgentInstructionsPath` to a file — avoids shell-escaping the long instruction text the 4 research scripts embed inline) | |
| `-KnowledgeSourcePaths` | Explicit, array — replaces the research scripts' hard-coded `items_by_url` blocks | |
| `-AgentTemplatePath` | Explicit, optional | For cloning an existing agent's structure (e.g. the confirmed-working `CEIS-ASPX-Only-Test` pattern from Phase 5 Task 4/6) |
| `-OutputPath` | Explicit, optional | Local `.agent` file staging path before upload |
| `-Overwrite` | Explicit switch, default `$false` | Fail closed if the target `.agent` file already exists and this isn't set |

For **existing** scripts being promoted with minimal change (already reasonably parameterized —
confirmed by reading each): `deploy-and-verify-skill.ps1`, `rollback-skill-deployment.ps1`,
`verify-agentassets-artifact.ps1` already take `-ConfigFile`/`-ManifestFile`-style parameters, not
hard-coded values — their promotion work is `git mv` + updating their `-ConfigFile` default to the
plugin's own config-resolution convention (once `workbench-setup`/root-config exists), not a
rewrite. `backup-existing-agents.ps1`/`backup-skills-and-templates.ps1` currently hard-code the 5
agent filenames / 3 skill/template paths as internal arrays — promotion requires converting those
to a `-Targets` array parameter with the current hard-coded lists becoming the *default* value
(backward compatible for the existing Phase 5 callers), per the same fail-closed-not-silent-default
principle as the destination-configuration design.

**New — generic reconciliation script (replaces moving `task-8a-reconcile-deployed-skill.ps1` as-is):**

| Parameter | Notes |
|---|---|
| `-ConfigPath` | Root config, not hard-coded `tools/phase-4-.../config.psd1` |
| `-SiteUrl`, `-ClientId`, `-TenantId` | Root config `Connection.*` — replaces the file's embedded Phase-3-fallback authentication block |
| `-SkillName` | Explicit, mandatory — replaces the hard-coded `$isReviewManualTopics` special-case |
| `-RepositorySkillPath` | Explicit — the script computes the hash itself rather than taking a hard-coded `-RepositorySHA` default (the current file's `9586379f...` default is the exact hard-coding this corrects) |
| `-ExpectedSHA256` | Optional override if the caller already computed it; otherwise derived from `-RepositorySkillPath` |
| `-AgentAssetsLibrary`, `-SkillsFolder` | Explicit, replace the hard-coded `AgentAssets`/`Skills` literals |
| `-JsonOutputPath` | Optional structured output, same pattern as `rollback-skill-deployment.ps1`'s existing `-JsonOutputPath` |

## 5. Phase-wrapper strategy

**Corrected — `task-8-deploy-review-manual-topics.ps1` and `task-12-rollback.ps1` are NOT
currently thin wrappers** (verified by reading both files; see Section 1's
`PHASE_SPECIFIC_DUPLICATED_IMPLEMENTATION_TO_REPLACE_WITH_THIN_WRAPPER` and
`HISTORICAL_PHASE_IMPLEMENTATION_REQUIRING_REPLACEMENT` entries). The migration must **replace**
their executable bodies with genuine thin calls into the promoted reusable scripts
(`deploy-and-verify-skill.ps1` and `rollback-skill-deployment.ps1` respectively), supplying only
Phase 4's specific skill name/parameters — this is new work, not a `git mv`. `task-9-*` stays
pending the human decision on its domain. Only `rollback-skill.ps1` is already the correct shape
(a literal one-line call) and needs no rewrite, only its target's eventual new location updated
once `rollback-skill-deployment.ps1` moves.

## 6. Evidence-preservation strategy

Nothing in `RETAIN_PHASE_EVIDENCE`/`RETAIN_PHASE_HARNESS`/`HISTORICAL_ONLY` above moves. The 4
`create-*-agent.ps1` research scripts stay in `tools/phase-4-*` permanently (not a staging area to
later empty out) — per instruction, they are "Phase 4 research," and the new `create-sharepoint-agent`
script is a fresh design informed by their pattern, not a promotion of any one of them. Likewise,
`task-8-deploy-review-manual-topics.ps1` and `task-12-rollback.ps1`'s **historical file paths** are
preserved if Phase 4 evidence requires reproducing them exactly — only their executable bodies
change, per Section 5. This avoids the failure mode the earlier map-debt entry (Wave 8,
`sharepoint_*.py`) already documented: never assume a "temporary" holding area's contents are
fully accounted for by a migration plan's own inventory without a fresh full-directory diff at
execution time.

## 7. Migration waves (design only — none authorized to execute)

**Corrected per external review:** Wave 0 no longer scaffolds empty taxonomy folders; Wave 1 is
gated on the `review-manual-topics` ownership decision rather than treated as a zero-design-work
first step; Wave 2 now explicitly replaces (not merely relocates) `task-8-*`/`task-12-*`'s
executable bodies.

1. **Wave 0 — plugin scaffold, no empty folders.** Create `plugins/sharepoint-agents-and-skills/`
   with only manifests (`plugin.json`, `plugin.yaml`), `README.md`, and whatever `tests/` Wave 1
   actually needs — **no** empty `scripts/{connection,agentassets,agents,native-skills,backup,
   validation,rollback}/` subfolders ahead of real implementation, per this repo's own
   "no empty taxonomy plugins/folders" principle. Each `scripts/` subfolder is created in the wave
   that adds its first real script.
2. **Wave 1 — resolve `review-manual-topics` ownership, then migrate only if approved.** First
   record `PLUGIN_MAY_CONTAIN_REUSABLE_PLATFORM_CAPABILITIES_AND_CONFIGURED_SOLUTION_SKILLS` or
   `PLUGIN_CONTAINS_ONLY_GENERIC_PLATFORM_CAPABILITIES` (Section 1). Only if the former is chosen:
   `git mv` the real skill, update `symlinks.json`/installer references, verify standalone
   install. If the latter is chosen, this skill needs a different plan entirely (not covered by
   this design) — do not proceed with Wave 1 as originally scoped.
3. **Wave 2 — native-skill lifecycle scripts, genuine thin wrappers.** Promote
   `deploy-and-verify-skill.ps1`, `rollback-skill-deployment.ps1`, `verify-agentassets-artifact.ps1`,
   `verify-agentassets-ready.ps1`, `inventory-skills.ps1` as-is (`git mv` + parameter update).
   Extract the new generic reconciliation script (Section 4) from `task-8a-reconcile-deployed-skill.ps1`
   rather than moving that file. Wire up `deploy-sharepoint-native-skill`/
   `verify-sharepoint-native-skill`/`rollback-sharepoint-native-skill` skills. **Rewrite** (not
   relocate) `task-8-deploy-review-manual-topics.ps1` and `task-12-rollback.ps1` so their bodies
   become genuine thin calls into the promoted scripts, per Section 5 — do not move their current
   implementations unchanged.
4. **Wave 3 — backup skill(s), corrected naming.** First resolve the naming/grouping decision
   (Section 1: one `backup-sharepoint-agent-assets` skill, or two split by user intent). Then
   parameterize and promote `backup-existing-agents.ps1` + `backup-skills-and-templates.ps1`
   accordingly.
5. **Wave 4 — new agent-creation capability.** Design and build the new parameterized
   `create-sharepoint-agent` script (Section 4), informed by but not copied from the 4 research
   scripts, which remain in place. Do **not** build `configure-agent-knowledge` in this wave —
   it stays `PROVISIONAL_SKILL_PENDING_DISTINCT_USER_INTENT` until a separate update/reconfigure
   journey is demonstrated (Section 3).
6. **Deferred, separate approval required:** `provision-agentassets.ps1`'s canonical-version
   decision (blocks nothing above — `verify-agentassets-ready.ps1` doesn't depend on it); the
   `sharepoint-content-publication` scope amendment for `upload-rendered-markdown.ps1`;
   `workbench-setup` plugin creation.

## 8. Required specification amendments

1. **`docs/vision/ai-assisted-structured-knowledge-workbench-broader-plan.md`**'s naming-
   reconciliation note (added 2026-08-02) currently says "any renaming decision belongs here, not
   as an ad hoc choice during an unrelated task" about the `sharepoint-knowledge` proposal. This
   document's decision (`sharepoint-agents-and-skills`, rejecting `sharepoint-knowledge` as too
   vague) should be recorded as a follow-up amendment to that note — not left for a future session
   to rediscover the conflict between the vision doc's original proposal and this document's
   decision.
2. **`.agent/map-debt.md`'s 2026-08-02 entry** (Status: `OPEN`) should be updated to reference this
   design document once it exists, so a future session finds the resolution path directly rather
   than re-deriving it.
3. **`docs/reports/multi-document-destination-config/complete-artifact-classification.md`** should
   get a superseded-by pointer to this document for its domain-ownership matrix section
   specifically (its artifact-level classification data remains valid and is reused here, not
   superseded).
