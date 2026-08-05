# Combined Interactive-Session Runbook — Richard, `AG-CSB-INTRANET-DEV`

**Purpose:** one session covering the real, human-dependent portions of Tasks 2 and 6 of
`docs/superpowers/plans/phase-8-review-manual-topics-promotion-and-lifecycle-plan.md`. Everything
below requires your own interactive PnP/Entra login (`Connect-PnPOnline ... -Interactive`) — this
agent cannot execute any of it.

**Prerequisite:** a real, filled-in `plugins/sharepoint-agents-and-skills/config.psd1` must exist
locally (git-ignored; create from the committed `.example` template if you don't already have one).

Run each step from the repository root. After each step, paste the **raw** console output back
(not a summary) so it can be recorded verbatim in the evidence files.

## 1. Live hash reconciliation (baseline)

```powershell
pwsh plugins/sharepoint-agents-and-skills/scripts/reconcile-deployed-skill.ps1 `
  -ConfigFile plugins/sharepoint-agents-and-skills/config.psd1
```

Read-only. Tells us whether the live deployed hash already matches the repository's current
`SKILL.md` hash.

## 2. Real promotion — only if hashes differ AND there is an approved artifact change

- **If Step 1 shows a match:** skip straight to Step 3's re-confirmation is unnecessary — record
  the match as valid reconciliation evidence for Stage 8.1.1, but the spec's "real artifact
  promoted" requirement stays open until an actual approved `SKILL.md` change exists. **Do not
  create a meaningless change to force a promotion event.**
- **If Step 1 shows a mismatch** (as happened twice before — Phase 4 → Phase 6): the live artifact
  is stale relative to the repository. Redeploying it to match the repository **is** a real
  promotion event and satisfies Stage 8.1.1/8.1.2's real-artifact requirement.

```powershell
pwsh plugins/sharepoint-agents-and-skills/scripts/deploy-and-verify-skill.ps1 `
  -ConfigFile plugins/sharepoint-agents-and-skills/config.psd1 `
  -ManifestFile plugins/sharepoint-agents-and-skills/deployment-manifest.example.json `
  -Execute
```

## 3. Post-promotion verification

```powershell
pwsh plugins/sharepoint-agents-and-skills/scripts/reconcile-deployed-skill.ps1 `
  -ConfigFile plugins/sharepoint-agents-and-skills/config.psd1
```

Confirms the just-deployed (or already-matching) artifact's hash now matches the repository.

## 4. Retirement — removal

```powershell
# dry-run first
pwsh plugins/sharepoint-agents-and-skills/scripts/rollback-skill-deployment.ps1 `
  -ConfigFile plugins/sharepoint-agents-and-skills/config.psd1 `
  -ManifestFile plugins/sharepoint-agents-and-skills/deployment-manifest.example.json

# then, after reviewing dry-run output:
pwsh plugins/sharepoint-agents-and-skills/scripts/rollback-skill-deployment.ps1 `
  -ConfigFile plugins/sharepoint-agents-and-skills/config.psd1 `
  -ManifestFile plugins/sharepoint-agents-and-skills/deployment-manifest.example.json `
  -Execute -ConfirmExactTarget "CONFIRM-REMOVE"
```

## 5. Confirm unavailability

In the live Copilot chat for `CEIS-Pilot-Knowledge-Agent`, attempt to invoke
`review-manual-topics` and confirm it is no longer offered/available. Note the exact prompt you
used and what Copilot returned.

## 6. Restoration

```powershell
pwsh plugins/sharepoint-agents-and-skills/scripts/deploy-and-verify-skill.ps1 `
  -ConfigFile plugins/sharepoint-agents-and-skills/config.psd1 `
  -ManifestFile plugins/sharepoint-agents-and-skills/deployment-manifest.example.json `
  -Execute
```

## 7. Final reconciliation

```powershell
pwsh plugins/sharepoint-agents-and-skills/scripts/reconcile-deployed-skill.ps1 `
  -ConfigFile plugins/sharepoint-agents-and-skills/config.psd1
```

Confirms the restored deployment matches the repository artifact again.

## 8. Raw evidence capture

Paste the raw output of Steps 1–3 into
`docs/reports/phase-8-scale-promotion-operations/stage-8.1.1-promotion-path.md`'s evidence-capture
section (Section 8) as a new dated sub-entry, and the raw output of Steps 4–7 into
`docs/reports/phase-8-scale-promotion-operations/stage-8.3.2-retirement-exercise.md`'s Section 7
evidence table. This agent will file both once you provide the raw output — do not paraphrase it
yourself in the interim, per this repository's own "raw output, not summarized prose" convention.
