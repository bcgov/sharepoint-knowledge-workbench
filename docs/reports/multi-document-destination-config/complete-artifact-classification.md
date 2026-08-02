# Complete Artifact Classification — `tools/` vs. `plugins/`

**Status:** ANALYSIS ONLY. No file has been moved, no plugin created, no skill created. Supersedes
the narrower first-pass inventory in `script-inventory-and-plugin-migration-candidates.md` (kept
for its diff/hash evidence on the two duplicate-suspect pairs) with the full artifact-type sweep
requested: every `SKILL.md`, `.agent` artifact, PowerShell/Python script, schema, config example,
agent template, and reusable reference/asset under `tools/phase-3-sharepoint-discovery/`,
`tools/phase-4-native-sharepoint-skills/`, `tools/phase-5-sharepoint-knowledge-agent-pilot/`, and
`plugins/sharepoint-content-publication/`.

**Successor note (added 2026-08-02):** this report remains the evidence inventory — every
per-artifact classification below is still valid and is reused, not superseded, by
`docs/superpowers/specs/2026-08-02-sharepoint-agents-and-skills-plugin-design.md`. That design
document records the accepted proposed domain model (plugin name `sharepoint-agents-and-skills`,
rejecting this report's own tentative two-plugin framing and the vision doc's original
`sharepoint-knowledge` proposal) and supersedes **only** the unresolved plugin-naming/topology
question this report left open — not the artifact-level classifications themselves. All artifacts
here remain subject to migration review before any move happens.

**Disposition enum used (as specified):** `RETAIN_PHASE_EVIDENCE`, `RETAIN_PHASE_HARNESS`,
`RETAIN_THIN_PHASE_WRAPPER`, `MOVE_TO_EXISTING_PLUGIN`, `MOVE_TO_APPROVED_NEW_PLUGIN`,
`RESEARCH_FUTURE_PLUGIN`, `HISTORICAL_ONLY`, `RETIRE_WITH_APPROVAL`, `REQUIRES_HUMAN_DECISION`.

## 1. `SKILL.md` files

| Path | Purpose | Disposition |
|---|---|---|
| `tools/phase-4-native-sharepoint-skills/skills/review-manual-topics/SKILL.md` (+ its `README.md`) | The real, deployed native skill — its own README names it the repository source of truth, deployment target `AgentAssets/Skills/review-manual-topics/SKILL.md`. Confirmed reusable, confirmed installed. | **MOVE_TO_APPROVED_NEW_PLUGIN** — target is `sharepoint-knowledge` (or whichever name the human decision below settles on), `skills/review-manual-topics/`. This is the single clearest case in the entire inventory. |
| `tools/phase-3-sharepoint-discovery/skills/reference-real-skill-review-manual-topics.SKILL.md` | A reference *copy* pulled from the real deployed skill, used during Phase 3.0 discovery to probe format compliance. Not the canonical source (that's the Phase 4 file above). | **HISTORICAL_ONLY** — evidence of a probe, would become a stale duplicate if "promoted" alongside the real one. |
| `tools/phase-3-sharepoint-discovery/skills/{example-skill-strict-format,v2-fewshot,v3-json,v4-template-ref,v5-list-libraries,v6-log-finding,v7-scoped-manual-qa,v8-cross-topic}.SKILL.md` (8 files) | Deliberate throwaway skill-format-compliance experiments (v2 through v8 naming makes the iterative-probe intent explicit), per `docs/research/research-summary-phase3-sharepoint-write-capability-discovery.md`. | **RETAIN_PHASE_EVIDENCE** — these are the actual evidence artifacts the research findings are based on; moving or deleting them would sever that evidence trail. |
| `tools/phase-5-sharepoint-knowledge-agent-pilot/backups/skills/{review-manual-topics,ceis-test-skill}/SKILL.md` | Local backup copies (this session), downloaded read-only from the tenant before considering any cleanup. Not source — the Phase 4 file is. | **RETAIN_PHASE_EVIDENCE** (as a dated backup/snapshot) — do not treat as a second canonical source; if `review-manual-topics/SKILL.md` moves per the row above, this backup copy stays exactly what it is, a point-in-time tenant snapshot. |

## 2. `.agent` artifacts

| Path | Purpose | Disposition |
|---|---|---|
| Live tenant: `SitePages/CEISPilotKnowledgePages/{CEIS-Pilot-Knowledge-Agent,CEIS-Pilot-Knowledge-Agent-Corrected,CEIS-ASPX-Only-Test,CEIS-Topic-Reviewer-with-Skills,CEISPilotKnowledgePages-manuallycreated}.agent` | 5 real, deliberate learning-phase agent variants (confirmed working, per Task 4 of the Phase 5 plan). Not repo files — they live only on the tenant. | **REQUIRES_HUMAN_DECISION** — not a repo-artifact classification at all; whether/when any of these get deleted, kept, or promoted into an `sharepoint-knowledge`-style agent-template capability is a tenant-state decision already deferred to you, not a file-move decision. |
| `tools/phase-5-sharepoint-knowledge-agent-pilot/backups/agents/*.agent` (5 files) | Local read-only backups of the above, downloaded this session. | **RETAIN_PHASE_EVIDENCE** — the whole reason they exist is as a safety-net snapshot before any tenant cleanup decision; they are not reusable implementation themselves. |
| `tools/phase-3-sharepoint-discovery/agents/{pnp-uploaded-agent-format,ui-created-agent-format}.agent.json` | Captured reference examples of the `.agent` file format (one PnP-uploaded, one UI-created) — used to reverse-engineer the schema during Phase 3.0 discovery. | **RETAIN_PHASE_EVIDENCE** — these are the format-discovery evidence itself (cited in the research doc's Section 3), not something a plugin would import. |

## 3. PowerShell / Python scripts

### `tools/phase-3-sharepoint-discovery/`

| Path | Disposition |
|---|---|
| `phase-3-0-tenant-discovery.ps1` | `RETAIN_PHASE_EVIDENCE` — one-time discovery probe |
| `provision-agentassets.ps1` | `REQUIRES_HUMAN_DECISION` — reusable capability (library provisioning), but diverged from the Phase 4 copy of the same name (confirmed via SHA-256 + diff: different hashes, Phase 4's version added placeholder-value detection and a Phase-3-config fallback). Cannot move either without first deciding which behavior is canonical — do not move as a false-duplicate pair. |
| `push-aspx-experiment.ps1` | `RETAIN_PHASE_EVIDENCE` — named "experiment" in its own docstring |
| `run-phase3-tenant-pilot.ps1` | `RETAIN_PHASE_EVIDENCE` — phase orchestration |

### `tools/phase-4-native-sharepoint-skills/deployment/scripts/`

| Path | Disposition |
|---|---|
| `create-test-agent.ps1`, `create-corrected-agent.ps1`, `create-aspx-only-agent-test.ps1`, `create-updated-agent-sitepages.ps1` | `RESEARCH_FUTURE_PLUGIN` — real reusable agent-creation capability once parameterized (currently hard-codes CEIS-specific site URLs, IDs, folder names, instructions per your own review), but no approved plugin owner exists yet. Candidate: `sharepoint-agents`. |
| `create-test-skill.ps1`, `deploy-and-verify-skill.ps1` | `RESEARCH_FUTURE_PLUGIN` — native-skill deployment capability. Candidate: `sharepoint-native-skills`. |
| `task-8-deploy-review-manual-topics.ps1` | `RETAIN_THIN_PHASE_WRAPPER` — once the reusable deploy logic it wraps has an approved plugin home, this stays as the thin Phase 4 wrapper supplying `review-manual-topics`-specific parameters. |
| `task-8a-reconcile-deployed-skill.ps1` | `RESEARCH_FUTURE_PLUGIN` — reusable drift-detection capability. Candidate: `sharepoint-native-skills`. |
| `rollback-skill.ps1` | `RETAIN_THIN_PHASE_WRAPPER` — confirmed via diff to be a literal alias (`& rollback-skill-deployment.ps1 ...`) with no independent logic; not a duplicate, a deliberate thin wrapper over the row below. |
| `rollback-skill-deployment.ps1` | `RESEARCH_FUTURE_PLUGIN` — the real reusable rollback implementation (has the `-Execute`/`-ConfirmExactTarget` safety-gate pattern other scripts should copy). Candidate: `sharepoint-native-skills`. |
| `task-12-rollback.ps1` | `RETAIN_THIN_PHASE_WRAPPER` — Task 12's evidence orchestration around the rollback capability above. |
| `task-9-retrieve-topic-metadata.ps1` | `RESEARCH_FUTURE_PLUGIN` — reusable metadata-query capability. Candidate: `sharepoint-agents` (agent-grounding-adjacent) or `sharepoint-native-skills` — needs the human decision below. |
| `provision-agentassets.ps1` | `REQUIRES_HUMAN_DECISION` — see the Phase 3 duplicate-suspect row above; same file, same unresolved conflict. |
| `diagnose-sharepoint-library.ps1` | `RESEARCH_FUTURE_PLUGIN` — reusable diagnostic. Candidate: `sharepoint-content-publication` or a shared diagnostics module — not decided. |
| `find-ceis-location.ps1` | `RETAIN_PHASE_EVIDENCE` — named as a one-time discovery probe |
| `inventory-skills.ps1` | `RESEARCH_FUTURE_PLUGIN` — candidate: `sharepoint-native-skills` |
| `verify-agentassets-artifact.ps1`, `verify-agentassets-ready.ps1` | `RESEARCH_FUTURE_PLUGIN` — candidate: `sharepoint-native-skills` |
| `probe-metadata-visibility.py` | `RETAIN_PHASE_EVIDENCE` — named "probe," Task-9-specific |
| `validate-phase4-exit-gate.py` | `RETAIN_PHASE_EVIDENCE` — exit-gate evidence is inherently phase-specific |

### `tools/phase-4-native-sharepoint-skills/` (harness/tests)

| Path | Disposition |
|---|---|
| `evaluations/validate_cases.py`, `tests/*.py` (9 files) | `RETAIN_PHASE_HARNESS` — matches your own confirmation that evaluation harnesses stay in `tools/` |

### `tools/phase-5-sharepoint-knowledge-agent-pilot/`

| Path | Disposition |
|---|---|
| `upload-rendered-markdown.ps1` | `RESEARCH_FUTURE_PLUGIN` — reusable content-publication capability. Candidate: `sharepoint-content-publication` — **but that plugin's existing scripts are deliberately package-only/zero-tenant-I/O** (confirmed by reading its actual source this session: "Never performs any SharePoint tenant I/O" is stated in two of its four scripts' own docstrings). This script does live `Connect-PnPOnline` writes — adding it as-is would silently break that plugin's design contract. Not a drop-in move. |
| `backup-existing-agents.ps1`, `backup-skills-and-templates.ps1` | `RESEARCH_FUTURE_PLUGIN` — reusable backup/restore capability. Candidates: `sharepoint-agents` (agent backup) and `sharepoint-native-skills` (skill backup) respectively — currently two different domains bundled by phase, not by capability. |
| `evaluations/validate_cases.py`, `tests/test_evaluations_harness.py` | `RETAIN_PHASE_HARNESS` |

### `plugins/sharepoint-content-publication/scripts/`

| Path | Disposition |
|---|---|
| `sharepoint_cli.py`, `sharepoint_dry_run.py`, `sharepoint_package.py`, `sharepoint_reconcile.py` | Already correctly plugin-owned — **no disposition needed**, listed here only to confirm they were checked. Design note for the record: all four are explicitly package-only (build/validate/reconcile an `UploadPackage`, zero tenant I/O) — a human uploads manually and the reconciliation step diffs against CSV-exported evidence. This plugin currently has **no `skills/` subfolder and no installed skill** exposing this capability to an agent — it is implementation packaged as a plugin but not yet user-facing. |

## 4. Schemas

| Path | Disposition |
|---|---|
| `tools/phase-4-native-sharepoint-skills/schemas/evaluation-case-schema.json` | `RETAIN_PHASE_HARNESS` — this is the evaluation-case schema Phase 5 already explicitly reuses by relative reference (not copied) rather than moved; changing that now would break Phase 5's `evaluations/validate_cases.py`. |

## 5. Config examples

| Path | Disposition |
|---|---|
| `tools/phase-3-sharepoint-discovery/config.psd1.example`, `tools/phase-4-native-sharepoint-skills/config.psd1.example`, `tools/phase-5-sharepoint-knowledge-agent-pilot/config.psd1.example` | `REQUIRES_HUMAN_DECISION` — this is exactly the fragmentation `docs/superpowers/specs/2026-08-02-multi-document-destination-configuration-design.md` already addresses (root `Connection`/`Authentication`/`Defaults` config + per-document publication profile + explicit script parameters). That design is written but **explicitly not authorized to implement** — do not consolidate these three files until that authorization happens. |
| `tools/phase-4-native-sharepoint-skills/tenant-config.psd1` | Real filled-in tenant credentials file — **not `.example`**, should already be gitignored; flagging only to confirm it was checked, not proposing a move for a credentials file. |

## 6. Agent templates / reusable references and assets

| Path | Disposition |
|---|---|
| `tools/phase-3-sharepoint-discovery/skills/v4-output-template.txt`, `v5-assets-library-inventory-template.txt` | `RETAIN_PHASE_EVIDENCE` — inputs to the v4/v5 format-probe experiments above, same evidence trail |
| `tools/phase-5-sharepoint-knowledge-agent-pilot/backups/skills/ceis-procedure-review-template.md` | `RETAIN_PHASE_EVIDENCE` — backup copy; canonical source is the live `AgentAssets/ceis-procedure-review-template.md` on the tenant, which is Phase 4 deliverable content, out of scope for any move here (not a script/skill, real published content) |

## Domain-ownership matrix (candidate, not authorized)

| Candidate plugin | Real artifacts that would move there | Status |
|---|---|---|
| `sharepoint-content-publication` (exists) | `upload-rendered-markdown.ps1` (needs a package-only-vs-live-I/O design decision first) | Exists, but scope conflict must be resolved before this specific script moves |
| `sharepoint-agents` (proposed in `docs/vision/ai-assisted-structured-knowledge-workbench-broader-plan.md` as `sharepoint-knowledge`, NOT as this name — see that document's naming-reconciliation note) | `create-test-agent.ps1`, `create-corrected-agent.ps1`, `create-aspx-only-agent-test.ps1`, `create-updated-agent-sitepages.ps1`, `task-9-retrieve-topic-metadata.ps1` (maybe), `backup-existing-agents.ps1` | Not created — **naming itself is unresolved**, see below |
| `sharepoint-native-skills` (also folds into the same `sharepoint-knowledge` proposal's `native-skills/` skill group per the vision doc) | `review-manual-topics/SKILL.md`, `create-test-skill.ps1`, `deploy-and-verify-skill.ps1`, `task-8a-reconcile-deployed-skill.ps1`, `rollback-skill-deployment.ps1`, `inventory-skills.ps1`, `verify-agentassets-artifact.ps1`, `verify-agentassets-ready.ps1`, `backup-skills-and-templates.ps1` | Not created — same naming question |
| `workbench-setup` (specified in `docs/superpowers/specs/2026-08-02-multi-document-destination-configuration-design.md` Section 8) | Nothing yet — root config generation doesn't exist as a script today | Not created, design-only |

## The one unresolved naming question blocking any real move

`docs/vision/ai-assisted-structured-knowledge-workbench-broader-plan.md` already proposes **one**
plugin, `sharepoint-knowledge`, covering both the "agents" and "native-skills" capability groups
above as skill groups within it (`native-skills/`, `agents/`, `deployment/`, `governance/`,
`health/`) — not two separate plugins. This classification's own candidate table above still lists
them as two separate future plugins (`sharepoint-agents`, `sharepoint-native-skills`), which may be
the right call given how much real capability exists in each, or may be exactly the kind of
unauthorized re-splitting the vision doc's own "no empty taxonomy plugins" rule warns against.
**This is a real, unresolved decision — not something to resolve unilaterally in this document.**

## Verified NOT-duplicate findings (symlink/hash check requested)

- `provision-agentassets.ps1` (phase-3 vs. phase-4): different SHA-256 hashes, real diverged
  content (diff evidence in Section 3 above) — `DOMAIN_SPECIFIC_VARIANT`, not
  `EXACT_DUPLICATE_PROVEN_BY_HASH`, not a managed symlink (both regular files).
- `rollback-skill.ps1` vs. `rollback-skill-deployment.ps1`: NOT duplicates — the former is a
  literal one-line alias/wrapper calling the latter. `REGULAR_FILE` (wrapper) +
  `REGULAR_FILE` (real implementation), `NOT_DUPLICATE`.
- No `.psm1`/`.py` file under any of the three `tools/phase-N-*` folders resolved as a symlink
  (`ls -la` confirmed all are regular files, no `->` targets) — the duplication-vs-symlink question
  the governing rules raised does not apply to anything found in this sweep.

## Explicitly not resolved by this classification

No file moved. No plugin created. No skill created. No `symlinks.json`/`plugin.json`/`SKILL.md`
touched. The `sharepoint-agents` vs. `sharepoint-native-skills` vs. single-`sharepoint-knowledge`
naming question above is the specific decision blocking any first migration slice.
