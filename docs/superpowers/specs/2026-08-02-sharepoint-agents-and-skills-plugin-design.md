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
| `tools/phase-4-native-sharepoint-skills/skills/review-manual-topics/{SKILL.md,README.md}` | The real, deployed native skill — moves as-is via `git mv`, no parameterization needed (it's already a `SKILL.md`, not a script) | `skills/review-manual-topics/` |
| `inventory-skills.ps1` | Native-skill inventory query | `skills/deploy-sharepoint-native-skill/` (shared script) or its own `scripts/native-skills/` capability, exposed via `deploy-sharepoint-native-skill`'s supporting logic |
| `deploy-and-verify-skill.ps1` | Native-skill deployment + SHA-256 readback verification | `skills/deploy-sharepoint-native-skill/` |
| `task-8a-reconcile-deployed-skill.ps1` | Deployed-skill drift detection (hash vs. repo) | `skills/verify-sharepoint-native-skill/` |
| `rollback-skill-deployment.ps1` | The real rollback implementation (has the `-Execute`/`-ConfirmExactTarget` safety gate) | `skills/rollback-sharepoint-native-skill/` |
| `verify-agentassets-artifact.ps1` | Verifies one artifact's presence/hash in `AgentAssets` | `skills/verify-sharepoint-native-skill/` |
| `verify-agentassets-ready.ps1` | Verifies `AgentAssets` library exists/ready before deployment | `scripts/agentassets/` (shared precondition check, used by multiple skills) |
| `provision-agentassets.ps1` (**both** the phase-3 and phase-4 copies — see "Requires human decision" below before this can actually move) | `AgentAssets` library provisioning | `scripts/agentassets/` |
| `backup-existing-agents.ps1` | Agent backup (once parameterized — see script parameter matrix) | `skills/backup-sharepoint-agents/` |
| `backup-skills-and-templates.ps1` | Native-skill/template backup (once parameterized) | `skills/backup-sharepoint-agents/` (shared backup skill, agent + skill artifacts both handled by one user-facing skill per the plugin tree below) |
| `create-test-agent.ps1`, `create-corrected-agent.ps1`, `create-aspx-only-agent-test.ps1`, `create-updated-agent-sitepages.ps1` | **Not moved as-is.** A NEW parameterized `create-sharepoint-agent` script is designed from the pattern these four scripts demonstrate (see script parameter matrix) — the four originals stay in `tools/phase-4-*` as research/evidence of the pattern, per "treat custom agent experiments carefully" below | `skills/create-sharepoint-agent/`, `skills/configure-agent-knowledge/` |
| `task-9-retrieve-topic-metadata.ps1` | Agent-grounding-adjacent metadata query | Folds into `configure-agent-knowledge` support logic, or stays research-only — **requires human decision**, not resolved by this design (its capability is closer to a grounding-source diagnostic than agent lifecycle management proper) |

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

`rollback-skill.ps1` (confirmed via diff: a literal one-line alias calling `rollback-skill-deployment.ps1`), `task-8-deploy-review-manual-topics.ps1`, `task-9-*` (pending the human decision above), `task-12-rollback.ps1`.

### `RETAIN_PHASE_HARNESS`

`tools/phase-4-native-sharepoint-skills/{evaluations/validate_cases.py, schemas/evaluation-case-schema.json, tests/*.py}`; `tools/phase-5-sharepoint-knowledge-agent-pilot/{evaluations/validate_cases.py, tests/test_evaluations_harness.py, evaluations/*.json, results/*.md}`.

### `HISTORICAL_ONLY`

`tools/phase-3-sharepoint-discovery/skills/reference-real-skill-review-manual-topics.SKILL.md` (a point-in-time copy of the real skill, not the source).

### `REQUIRES_HUMAN_DECISION`

1. **`provision-agentassets.ps1` (phase-3 vs. phase-4 divergence)** — confirmed different SHA-256, real diverged logic (phase-4's version adds placeholder-value detection + phase-3-config fallback). Which behavior becomes the plugin's canonical version, and whether the other's extra logic (the fallback) is a real requirement or phase-4-specific scaffolding, is not decided here.
2. **`task-9-retrieve-topic-metadata.ps1`'s domain** — agent-grounding-adjacent vs. a distinct diagnostic capability, not resolved.
3. **`upload-rendered-markdown.ps1`'s home** — blocked on the `sharepoint-content-publication` scope-amendment decision (design work only, not approval, per this document's own scope).

## 2. Proposed plugin tree

Adopting the structure already specified, unchanged:

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
| `review-manual-topics` | `tools/phase-4-native-sharepoint-skills/skills/review-manual-topics/SKILL.md` — moves as-is | **Ready** — first migration wave, per instruction |
| `deploy-sharepoint-native-skill` | `deploy-and-verify-skill.ps1`, `inventory-skills.ps1`, `verify-agentassets-ready.ps1` | Ready once parameterized (Section 4) |
| `verify-sharepoint-native-skill` | `task-8a-reconcile-deployed-skill.ps1`, `verify-agentassets-artifact.ps1` | Ready once parameterized |
| `rollback-sharepoint-native-skill` | `rollback-skill-deployment.ps1` (already has the safety-gate pattern) | Ready — least parameterization needed, already has `-ConfigFile`/`-ManifestFile`/`-Execute`/`-ConfirmExactTarget` |
| `create-sharepoint-agent` | Pattern demonstrated by the 4 `create-*-agent.ps1` research scripts, but **no single one of them is reusable as-is** — needs the new parameterized script designed in Section 4 before this skill has real backing | **Blocked** on new-script design, not just extraction |
| `configure-agent-knowledge` | Same 4 scripts' source-binding logic (the `capabilities`/`items_by_url` block) | **Blocked**, same reason |
| `backup-sharepoint-agents` | `backup-existing-agents.ps1` + `backup-skills-and-templates.ps1` (merged into one user-facing skill per the plugin tree, since both are "backup" intent even though they back up different artifact types) | Ready once parameterized |

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

## 5. Phase-wrapper strategy

Per instruction: preserve `task-8-deploy-review-manual-topics.ps1`, `task-9-*`, `task-12-rollback.ps1`
as thin wrappers supplying Phase 4's specific skill name/parameters once the underlying reusable
scripts move into the plugin — each wrapper's own logic becomes "call the plugin's real script
with these Phase-4-specific arguments," not duplicated implementation. `rollback-skill.ps1` is
already exactly this shape (a literal one-line call) and needs no rewrite, only its target's
eventual new location updated once `rollback-skill-deployment.ps1` moves.

## 6. Evidence-preservation strategy

Nothing in `RETAIN_PHASE_EVIDENCE`/`RETAIN_PHASE_HARNESS`/`HISTORICAL_ONLY` above moves. The 4
`create-*-agent.ps1` research scripts stay in `tools/phase-4-*` permanently (not a staging area to
later empty out) — per instruction, they are "Phase 4 research," and the new `create-sharepoint-agent`
script is a fresh design informed by their pattern, not a promotion of any one of them. This
avoids the failure mode the earlier map-debt entry (Wave 8, `sharepoint_*.py`) already documented:
never assume a "temporary" holding area's contents are fully accounted for by a migration plan's
own inventory without a fresh full-directory diff at execution time.

## 7. Migration waves (design only — none authorized to execute)

1. **Wave 0 — plugin scaffold.** Create `plugins/sharepoint-agents-and-skills/` structure (manifests,
   empty `scripts/`/`references/`/`assets/`/`tests/` subfolders per the tree above) — no skills yet.
2. **Wave 1 — `review-manual-topics` migration.** `git mv` the real skill, update
   `symlinks.json`/installer references, verify standalone install. The one artifact needing zero
   new design work.
3. **Wave 2 — native-skill lifecycle scripts.** Promote `deploy-and-verify-skill.ps1`,
   `rollback-skill-deployment.ps1`, `verify-agentassets-artifact.ps1`, `verify-agentassets-ready.ps1`,
   `inventory-skills.ps1`, `task-8a-reconcile-deployed-skill.ps1` into `scripts/native-skills/` +
   `scripts/agentassets/`, wire up `deploy-sharepoint-native-skill`/`verify-sharepoint-native-skill`/
   `rollback-sharepoint-native-skill` skills, leave `task-8-*`/`task-12-*` as updated thin wrappers.
4. **Wave 3 — backup skill.** Parameterize and promote `backup-existing-agents.ps1` +
   `backup-skills-and-templates.ps1` into `backup-sharepoint-agents`.
5. **Wave 4 — new agent-creation capability.** Design and build the new parameterized
   `create-sharepoint-agent` script (Section 4) plus `configure-agent-knowledge`, informed by but
   not copied from the 4 research scripts, which remain in place.
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
