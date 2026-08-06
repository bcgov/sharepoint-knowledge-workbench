# Stage 8.1.1 / 8.1.2 — Promotion Path and Version-Compatibility Policy: `review-manual-topics` (native-sharepoint)

**Status:** `PROMOTION_PATH_DOCUMENTED`. **Not yet accepted per spec Section 6.1** — that stage
requires "at least one real artifact... promoted through the resulting path," which has not
happened yet (see "Open acceptance items" below). This document defines the path; it does not
itself constitute the required real promotion event.

**Scope:** the `review-manual-topics` **native-sharepoint** runtime only, in tenant
`AG-CSB-INTRANET-DEV`. Not the `repository-claude` runtime (no SharePoint promotion applies to it).

## 1. Artifact identity

- **Repository source of truth:**
  `plugins/sharepoint-agents-and-skills/skills/review-manual-topics/SKILL.md`.
- **Identity mechanism:** SHA-256 of the file's exact bytes — there is no separate version number
  field in the file itself (verified: its YAML front matter has only `name` and `description`).
  Version identity is carried entirely by the hash recorded in
  `plugins/sharepoint-agents-and-skills/deployment-manifest.example.json` and in
  `tools/phase-4-native-sharepoint-skills/tenant-config.psd1`'s
  `AgentAssets.DeployedSkills.ReviewManualTopics.RepositorySHA256` field.

## 2. Environment boundaries (real, not aspirational)

**Verified fact:** `tools/phase-4-native-sharepoint-skills/tenant-config.psd1` names exactly one
site — `https://bcgov.sharepoint.com/sites/AG-CSB-INTRANET-DEV`. **No separate test or production
SharePoint environment for this capability exists in this repository's tracked configuration.**

The only real environment boundary today is:

```text
repository (version-controlled SKILL.md)
   ↓  promotion
deployed (AgentAssets/Skills/review-manual-topics/ in AG-CSB-INTRANET-DEV)
```

A future test/production tier is not designed here — inventing one without an actual second
environment would not be a real promotion path. If a test or production SharePoint site is
provisioned later, this document must be revised against that real environment, not extended
speculatively now.

## 3. Approval point

Richard Fremmerlid (accountable owner, per the capability activation record) reviews any
`SKILL.md` content diff before it is deployed. This is the same gate already implicit in every
prior phase (Phase 4, Phase 6), made explicit here as a named promotion-path step rather than an
unstated assumption.

## 4. Validation before promotion

`deploy-and-verify-skill.ps1`'s existing preflight behavior (no tenant writes without `-Execute`):
validates the deployment manifest and configuration file, computes the local repository file's
SHA-256, and compares it against the manifest-declared expected hash before any upload is
attempted.

## 5. Deployment step

```powershell
pwsh plugins/sharepoint-agents-and-skills/scripts/deploy-and-verify-skill.ps1 `
  -ConfigFile plugins/sharepoint-agents-and-skills/config.psd1 `
  -ManifestFile plugins/sharepoint-agents-and-skills/deployment-manifest.example.json `
  -Execute
```

Run interactively by Richard (the script calls `Connect-PnPOnline ... -Interactive`; this agent's
environment has no Entra/browser session and cannot execute this step). Uploads the skill file,
downloads it back, and verifies a byte-for-byte SHA-256 match as part of the same script run.

## 6. Post-promotion verification

```powershell
pwsh plugins/sharepoint-agents-and-skills/scripts/reconcile-deployed-skill.ps1 `
  -ConfigFile plugins/sharepoint-agents-and-skills/config.psd1 `
  -FallbackConfigFile tools/phase-3-sharepoint-discovery/config.psd1
```

Read-only (per the script's own header: "No upload, overwrite, delete, or tenant modification").
Compares the live deployed `SKILL.md`'s hash against the repository artifact's hash and reports
match/mismatch.

**Real prerequisite gap found and fixed this round:** no `plugins/sharepoint-agents-and-skills/
config.psd1.example` template existed anywhere in this repository, even though all three scripts
(`deploy-and-verify-skill.ps1`, `reconcile-deployed-skill.ps1`, `rollback-skill-deployment.ps1`)
default to `plugins/sharepoint-agents-and-skills/config.psd1` and instruct "Copy config.psd1.example
to config.psd1" on a missing file. **Canonical template, created this round:**
`plugins/sharepoint-agents-and-skills/config.psd1.example`, containing only the fields the scripts
actually read (`SiteUrl` required; `ClientId`/`TenantId` optional — verified against each script's
`$config.` usage; there is no `TargetLibrary`/other field these three scripts consume from this
config, unlike the older `tools/phase-4-native-sharepoint-skills/config.psd1.example` template,
which serves different, wrapper-level scripts). `plugins/sharepoint-agents-and-skills/config.psd1`
(the real, filled-in file) has also been added to `.gitignore` this round — it was not previously
excluded. Richard must copy the new `.example` to `config.psd1` and fill in `SiteUrl` (and
`ClientId`/`TenantId` if using app-only auth) before either command above can run.
`reconcile-deployed-skill.ps1`'s `-FallbackConfigFile tools/phase-3-sharepoint-discovery/
config.psd1` is an optional fallback path only — its own `.example` template already exists at
`tools/phase-3-sharepoint-discovery/config.psd1.example`; using it is not required if the primary
config file above is present.

## 7. Rollback

```powershell
pwsh plugins/sharepoint-agents-and-skills/scripts/rollback-skill-deployment.ps1 `
  -ConfigFile plugins/sharepoint-agents-and-skills/config.psd1 `
  -ManifestFile plugins/sharepoint-agents-and-skills/deployment-manifest.example.json `
  -Execute -ConfirmExactTarget "CONFIRM-REMOVE"
```

Dry-run by default (no `-Execute`); recycles rather than permanently deletes; verifies removal.
Already exercised once for real in Phase 4 Task 12
(`docs/reports/phase-4-native-sharepoint-skills/EVID-PHASE4-TASK12-ROLLBACK-COMPLETION.md`), via
the historical wrapper `tools/phase-4-native-sharepoint-skills/deployment/scripts/task-12-
rollback.ps1`, which delegates to this same canonical script.

## 8. Evidence capture

Each real promotion-path run must be recorded as its own file under
`docs/reports/phase-8-scale-promotion-operations/`, containing: date/time, the exact command run,
its raw output (not a paraphrase — per this repository's own "reviewer/implementer state
disputes" convention in `start-here.md`), before/after hash values, and Richard's explicit
approval note for the underlying `SKILL.md` change (if any).

### 2026-08-06 — live reconciliation, retirement exercise, restoration

Run against `AG-CSB-INTRANET-DEV`, interactively by Richard. Full raw command output for the
removal/restoration sequence (Steps 4–7 of `combined-interactive-session-runbook.md`) is recorded
in `stage-8.3.2-retirement-exercise.md` Section 7 — not duplicated here. Summary relevant to this
document's own gate:

- **Baseline/final reconciliation (`reconcile-deployed-skill.ps1`):** repository SHA-256
  `bb327348b55e9f55cbf8f83d12d5d3c49f26c5502bf60bfa6bd74037f5e43b3d` matched the deployed artifact's
  hash both before and after the retirement exercise. Disposition:
  `TASK_8_ARTIFACT_ALREADY_PRESENT_AND_RECONCILED`.
- **This is the "hashes already match" branch** described below — the baseline match alone is not
  a real promotion event. **Section 6.1 is satisfied instead by the retirement exercise's
  restoration step**: `deploy-and-verify-skill.ps1 -Execute` redeployed the artifact for real after
  removal, with its own pre/post SHA-256 readback match (`bb327348...` both sides), independently
  confirmed via `verify-agentassets-ready.ps1`'s inventory (file present again, count back to 6).
  Full raw output in `stage-8.3.2-retirement-exercise.md` Section 7.
- **Section 6.2 remains open** — the restored bytes are identical to what was already live; no
  approved `SKILL.md` content change was deployed this session.
- **Two real script defects found and fixed** in `rollback-skill-deployment.ps1` during this
  session (wrong recycle cmdlet name; wrong server-relative-path construction) — see
  `stage-8.3.2-retirement-exercise.md` Section 7 for full detail. Fixes are in this branch's
  worktree only as of this writing, not yet committed.
- Richard's explicit approval: this was a planned Stage 8.3.2 exercise, not a `SKILL.md` content
  change — no separate content-change approval applies.

## 9. Emergency disablement

Identical to Section 7's rollback — deleting/recycling the deployed skill folder is both the
rollback mechanism and the emergency-disable mechanism; there is no separate "disable in place"
capability for a `SKILL.md`-based native skill.

## 10. Version-compatibility policy (Stage 8.1.2, single-capability scope)

- **Schema compatibility:** the contract is `SKILL.md`'s YAML front matter (`name`,
  `description`) plus its documented body — single-topic-only input, read-only editorial
  synthesis, the explicitly listed prohibited scopes already written into the file itself. Any
  future change that alters this contract (e.g., adds a new capability, removes the single-topic
  restriction) is a breaking change requiring the full approval/validation/deployment sequence
  above, not a silent redeploy.
- **Deployment-manifest compatibility:** `deployment-manifest.example.json`'s declared hash must
  always equal the actually-deployed `SKILL.md`'s hash — this is the entire reconciliation
  mechanism (Section 6); stated here as the compatibility rule rather than as a separate new one.
- **Migration/deprecation:** there is no semantic version number for this artifact — every content
  change is a new version by hash definition. Deprecating the capability entirely follows Stage
  8.3.2's retirement procedure, not this section.
- **Cross-capability compatibility:** `DEFERRED_UNTIL_EVIDENCE` per the Phase 8 specification — no
  second operational capability exists yet to be compatible with (see the capability activation
  record, Section 11).

## Open acceptance items — explicitly not closed by this document

- **Stage 8.1.1 — Section 6.1 satisfied 2026-08-06.** Spec Section 6.1 requires "at least one real
  artifact... actually promoted through it." The live reconciliation found hashes already matching
  (the "hashes already match" branch below), so the baseline match alone was not itself a
  promotion — but the retirement exercise's restoration step (`stage-8.3.2-retirement-exercise.md`
  Section 6/7) redeployed the repository artifact through this same path after a real removal, with
  a successful post-restoration reconciliation. **That satisfies Section 6.1.** See Section 8's
  2026-08-06 evidence entry above for the full record.
  - **If hashes differ (not what happened this round):** redeploying and verifying (Section 5/6)
    would itself be the real promotion — Section 6.1 satisfied directly by that redeploy.
  - **If hashes already match (what actually happened):** the baseline match alone is valid
    reconciliation evidence only, not itself a real promotion — satisfied instead via the
    retirement exercise's restoration, as recorded above.
- **Stage 8.1.2 is not yet accepted, and is not satisfied merely by Section 6.1 being satisfied.**
  Spec Section 6.2 requires "at least one real version **bump**... exercised against it" — a
  distinct criterion from Section 6.1's "an artifact was promoted." Neither an unchanged-hash
  redeploy nor the retirement exercise's byte-identical restoration is a version *change*; both
  redeploy the same bytes that were already live. **This criterion stays open until an actual
  approved `SKILL.md` content change is deployed through this path** — do not manufacture a
  meaningless content change merely to close it.
