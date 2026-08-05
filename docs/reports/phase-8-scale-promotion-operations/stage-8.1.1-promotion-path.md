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

**Real prerequisite gap found during verification:** neither
`plugins/sharepoint-agents-and-skills/config.psd1` nor `tools/phase-3-sharepoint-discovery/
config.psd1` exists in this repository — only their `.example` templates are tracked
(`config.psd1` is git-ignored per `.gitignore`'s explicit comment: "only the real, filled-in file
is ignored"). Richard must have (or create, from the committed `.example` template) a real,
filled-in `config.psd1` locally before either command above can run. This is not a blocker this
document invents — it is the same gitignored-local-config pattern already established for every
other tenant-scripting tool in this repository (`CLAUDE.md`'s "Tenant-scripting destination
configuration" section).

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

- **Stage 8.1.1 is not yet accepted.** Spec Section 6.1 requires "at least one real artifact...
  actually promoted through it." This document defines the path only. The real exercise (reconcile
  the live tenant artifact against the repository artifact; if hashes differ, redeploy and verify;
  if they match, record the successful reconciliation but leave the real-promotion requirement
  open) is a separate task, blocked on Richard's interactive PnP session — see the implementation
  plan's Task 2.
- **Stage 8.1.2 is not yet accepted.** Its policy is defined above, but spec Section 6.2 requires
  "at least one real version bump exercised against it." No real version check has occurred yet —
  pending the same Task 2 exercise. **A meaningless content change must not be created merely to
  manufacture a promotion/version event** — if Task 2's reconciliation finds the live hash already
  matches the repository hash, this policy's real-check requirement stays explicitly open until an
  actual approved `SKILL.md` change is deployed through this path.
