# Script Inventory — `tools/` vs. `plugins/` Disposition

**Status:** ANALYSIS ONLY. No file has been moved. Per explicit instruction: produce the
inventory, classification, and proposed disposition first; stop for review before any
`git mv` migration happens.

**Ownership rule applied** (as given): `tools/` = phase-specific experiments, evidence capture,
probes, evaluation harnesses, thin phase wrappers. `plugins/` = reusable operational
implementation — canonical scripts, skills, references, tests, installer-delivered capabilities.

**Existing plugin landscape checked before proposing destinations:** `plugins/
sharepoint-content-publication` already exists (per `CLAUDE.md`, currently a
`TRANSITIONAL_HOLDING_LOCATION`) — Python only (`sharepoint_cli.py`, `sharepoint_dry_run.py`,
`sharepoint_package.py`, `sharepoint_reconcile.py`), no PowerShell, no `skills/` subfolder yet.
No `sharepoint-agents` or `sharepoint-native-skills` plugin exists yet — proposing one is a gap
to flag, not something to create here (no empty plugins to satisfy a taxonomy).

## `tools/phase-3-sharepoint-discovery/`

| Script | Purpose | Classification | Tenant R/W | Callers | Tests | Config | Proposed disposition |
|---|---|---|---|---|---|---|---|
| `phase-3-0-tenant-discovery.ps1` | Read-only tenant capability inventory (Stage 3.0.1) | Phase-specific probe | Read-only | None found | None | `config.psd1` | **Retain in tools/** — one-time discovery probe, not reusable operational capability |
| `provision-agentassets.ps1` | Creates the `AgentAssets` library on first use | Reusable (library provisioning is a repeatable operation) | Write (`New-PnPList`) | Manual | None | `config.psd1` | **Plugin gap** — no `sharepoint-agents` or `sharepoint-native-skills` plugin exists yet to own this; flag as pending, do not move without a destination |
| `push-aspx-experiment.ps1` | One-time ASPX-vs-modern-page experiment upload | Phase-specific experiment | Write | Manual | None | `config.psd1` | **Retain in tools/** — named "experiment" in its own docstring, historical evidence |
| `run-phase3-tenant-pilot.ps1` | Orchestrates the Phase 3.0 pilot run | Phase-specific orchestration | Write | Manual | None | `config.psd1` | **Retain in tools/** — phase-specific evidence orchestration |

## `tools/phase-4-native-sharepoint-skills/deployment/scripts/`

| Script | Purpose | Classification | Tenant R/W | Tests | Proposed disposition |
|---|---|---|---|---|---|
| `create-test-agent.ps1` | Creates `CEIS-Pilot-Knowledge-Agent.agent` | Reusable (agent creation) | Write | None found | **Plugin gap → future `sharepoint-agents`** |
| `create-corrected-agent.ps1` | Creates `CEIS-Pilot-Knowledge-Agent-Corrected.agent` | Reusable (agent creation) | Write | None found | **Plugin gap → future `sharepoint-agents`** |
| `create-aspx-only-agent-test.ps1` | Creates `CEIS-ASPX-Only-Test.agent` | Reusable (agent creation) | Write | None found | **Plugin gap → future `sharepoint-agents`** |
| `create-updated-agent-sitepages.ps1` | Creates an agent variant scoped to Site Pages | Reusable (agent creation) | Write | None found | **Plugin gap → future `sharepoint-agents`** |
| `create-test-skill.ps1` | Creates `ceis-test-skill` under `AgentAssets/Skills/` | Reusable (native-skill deployment) | Write | None found | **Plugin gap → future `sharepoint-native-skills`** |
| `deploy-and-verify-skill.ps1` | Deploys + SHA-256-verifies a native skill | Reusable (native-skill deployment) | Write | None found | **Plugin gap → future `sharepoint-native-skills`** |
| `task-8-deploy-review-manual-topics.ps1` | Deploys the real `review-manual-topics` skill | Reusable, but named `task-8-*` (phase-specific wrapper around reusable logic) | Write | None found | **Split**: extract reusable deploy logic to future `sharepoint-native-skills`; keep a thin `task-8-*` wrapper in tools/ that supplies Phase 4's specific skill/params |
| `task-8a-reconcile-deployed-skill.ps1` | Reconciles deployed skill hash vs. repo | Reusable (drift detection) | Read-only | None found | **Plugin gap → future `sharepoint-native-skills`** |
| `rollback-skill.ps1` | Rolls back a deployed skill (has `-ConfirmExactTarget` gate per design spec Section 2) | Reusable (rollback) | Write (guarded) | `test_rollback_and_exit_gate.py` (3 pre-existing failures, confirmed unrelated to Phase 5 this session) | **Plugin gap → future `sharepoint-native-skills`** — already has the safety-gate pattern other plugin scripts should copy |
| `rollback-skill-deployment.ps1` | Similar/overlapping with `rollback-skill.ps1` — **possible duplicate capability, needs file-level diff before disposition** | Unclear — flagged | Write | Shares test file above? unconfirmed | **Needs deeper review before disposition — do not assume distinct from `rollback-skill.ps1`** |
| `task-12-rollback.ps1` | Phase 4 Task 12's rollback exercise orchestration | Phase-specific wrapper | Write | `test_rollback_and_exit_gate.py` | **Retain in tools/** as thin wrapper once reusable rollback logic above moves |
| `task-9-retrieve-topic-metadata.ps1` | Retrieves SharePoint list-item metadata for Task 9 evidence | Reusable (metadata query) | Read-only | `test_metadata_visibility.py` | **Plugin gap → future `sharepoint-agents`** (metadata visibility is an agent-grounding-adjacent capability) |
| `provision-agentassets.ps1` | Same purpose as the phase-3 copy — **likely duplicated logic across phase-3 and phase-4** | Reusable, duplicated | Write | `test_provisioning_discovery.py` | **Needs deconfliction with phase-3's copy before either moves — do not move independently** |
| `diagnose-sharepoint-library.ps1` | Diagnostic read of a library's structure | Reusable (diagnostic) | Read-only | None found | **Plugin gap → future `sharepoint-content-publication` or a shared diagnostics module** |
| `find-ceis-location.ps1` | Searches for where CEIS content actually lives on the tenant | Phase-specific one-time discovery | Read-only | None found | **Retain in tools/** — its own name signals a one-time discovery probe |
| `inventory-skills.ps1` | Lists deployed native skills | Reusable (inventory) | Read-only | None found | **Plugin gap → future `sharepoint-native-skills`** |
| `verify-agentassets-artifact.ps1` | Verifies one artifact's presence/hash in `AgentAssets` | Reusable (verification) | Read-only | `test_deployment_verifier.py` | **Plugin gap → future `sharepoint-native-skills`** |
| `verify-agentassets-ready.ps1` | Verifies `AgentAssets` library exists/ready before deployment | Reusable (precondition check) | Read-only | Likely `test_provisioning_discovery.py` | **Plugin gap → future `sharepoint-native-skills`** |
| `probe-metadata-visibility.py` | Task 9's metadata-visibility probe (Python) | Phase-specific evidence capture | Read-only | `test_metadata_visibility.py` | **Retain in tools/** — named "probe," Task-9-specific |
| `validate-phase4-exit-gate.py` | Validates Phase 4's exit-gate evidence is complete | Phase-specific evidence validation | Read-only, local files | `test_phase4_exit_gate.py` | **Retain in tools/** — exit-gate evidence is inherently phase-specific |
| `evaluations/validate_cases.py` + `tests/*.py` (9 files) | Evaluation-case harness/tests | Phase-specific evaluation harness (already explicitly reused as a pattern by Phase 5, not moved) | N/A | Self | **Retain in tools/** — matches the given rule ("evaluation harnesses" stay in tools/) |

## `tools/phase-5-sharepoint-knowledge-agent-pilot/`

| Script | Purpose | Classification | Tenant R/W | Tests | Proposed disposition |
|---|---|---|---|---|---|
| `upload-rendered-markdown.ps1` | Uploads rendered `.md` pages into an existing library's subfolder | Reusable (content publication) | Write | None found | **Plugin gap → future `sharepoint-content-publication`** (this plugin already exists, currently Python-only — would need a PowerShell upload capability added, or a Python equivalent using the existing `sharepoint_package.py`/`sharepoint_cli.py` pattern instead of introducing PowerShell into an otherwise-Python plugin — **needs a design decision, not assumed**) |
| `backup-existing-agents.ps1` | Downloads `.agent` files to local disk for reference | Reusable (agent backup/restore) | Read-only | None found | **Plugin gap → future `sharepoint-agents`** |
| `backup-skills-and-templates.ps1` | Downloads skill/template files to local disk | Reusable (native-skill backup) | Read-only | None found | **Plugin gap → future `sharepoint-native-skills`** |
| `evaluations/validate_cases.py` + `tests/test_evaluations_harness.py` | Phase 5's evaluation-case harness (deliberate near-copy of Phase 4's, per its own docstring) | Phase-specific evaluation harness | N/A | Self | **Retain in tools/** — matches the given rule explicitly |

## Files that should remain in `tools/` (per the rule, independent of plugin gaps)

Every file in the "Phase-specific" classification column above: `phase-3-0-tenant-discovery.ps1`,
`push-aspx-experiment.ps1`, `run-phase3-tenant-pilot.ps1`, `task-12-rollback.ps1` (as a thin
wrapper), `find-ceis-location.ps1`, `probe-metadata-visibility.py`, `validate-phase4-exit-gate.py`,
both phases' `evaluations/validate_cases.py` + test suites, and Phase 5's evaluation case JSON
files/results/README (not scripts, but explicitly evidence per the rule).

## Files that should move to `plugins/` — blocked on plugin gaps, not ready to move yet

Every row marked "**Plugin gap →**" above. None of these can be moved today because their target
plugin (`sharepoint-agents`, `sharepoint-native-skills`) does not exist, and creating an empty
plugin "merely to satisfy this taxonomy" was explicitly ruled out. `upload-rendered-markdown.ps1`
has a different problem: its target plugin (`sharepoint-content-publication`) already exists but
is Python-only, so adding a PowerShell script there needs its own decision about
language-consistency, not an assumed drop-in move.

## Duplicate or overlapping capabilities found (need deconfliction before any move)

1. **`provision-agentassets.ps1` exists in both `tools/phase-3-sharepoint-discovery/` and
   `tools/phase-4-native-sharepoint-skills/deployment/scripts/`** — same filename, likely
   overlapping or duplicated logic. Needs a file-level diff to determine if these are identical,
   diverged copies, or genuinely different implementations before either is proposed for a plugin
   move (moving one without reconciling the other would just relocate the duplication).
2. **`rollback-skill.ps1` vs. `rollback-skill-deployment.ps1`** — names suggest overlapping
   rollback capability. Not diffed in this pass; flagged as needing review, not assumed distinct.

## Plugin gaps requiring a future design decision (not authorized to create here)

- **`sharepoint-agents`** — would own agent creation, backup/restore, knowledge-source binding,
  agent-template handling, validation. Real candidate scripts exist (5+ in the tables above) —
  this is not a speculative plugin, there's already enough reusable capability to justify one, but
  creating it is a separate authorized decision, not a side effect of this inventory.
- **`sharepoint-native-skills`** — would own native-skill deployment, backup/restore, inventory,
  hash verification, rollback. Similarly, real candidate scripts already exist.
- **`workbench-setup`** — already specified in `docs/superpowers/specs/
  2026-08-02-multi-document-destination-configuration-design.md` Section 8; no scripts in this
  inventory map to it directly yet (root config generation doesn't exist as a script today).
- **`sharepoint-content-publication`'s language boundary** — currently pure Python; whether it
  should absorb PowerShell upload scripts as-is, or whether `upload-rendered-markdown.ps1`'s logic
  should be reimplemented in Python to match, is an open decision this inventory surfaces but does
  not resolve.

## Explicitly not resolved by this inventory (per instruction: stop for review)

No `git mv` has been performed. No plugin has been created. No `symlinks.json`/`plugin.json`/
`SKILL.md` has been touched. This document is the analysis artifact to review before any
migration sequence is authorized.
