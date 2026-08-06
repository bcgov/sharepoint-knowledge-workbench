# Combined Interactive-Session Runbook — Richard, `AG-CSB-INTRANET-DEV`

**Purpose:** one session covering the real, human-dependent portions of Tasks 2 and 6 of
`docs/superpowers/plans/phase-8-review-manual-topics-promotion-and-lifecycle-plan.md`. Everything
below requires your own interactive PnP/Entra login (`Connect-PnPOnline ... -Interactive`) — this
agent cannot execute any of it.

**Prerequisite:** a real, filled-in `plugins/sharepoint-agents-and-skills/config.psd1`, copied from
the canonical `plugins/sharepoint-agents-and-skills/config.psd1.example` template (created this
round) and filled in with the real `SiteUrl` (and `ClientId`/`TenantId` if using app-only auth).
The file is git-ignored, so it will not already exist in a fresh checkout.

**Outcome summary (read before running):**
- **Step 1 shows a mismatch → Step 2 redeploys → satisfies the real-promotion gate (spec Section
  6.1).** The compatibility gate (Section 6.2, "one real version change") still stays open, because
  redeploying the already-authored `SKILL.md` is not itself a version *change*.
- **Step 1 shows a match → Step 2 is skipped → the real-promotion gate stays open after Step 3.**
  It is satisfied later, by Step 6's restoration (a real deployment through the same path) once
  Step 7 confirms it. The compatibility gate (6.2) still stays open regardless, for the same reason.
- **The real-version-change compatibility gate (6.2) is only closed by an actual approved `SKILL.md`
  content change deployed through this path** — not by anything in this session unless you also
  bring such a change. Do not create one solely to close this gate.
- **If any step in Section 4 or 6 (removal/restoration) fails or errors, stop immediately.** Do not
  proceed to the next step. Resolve/recover the tenant state first (e.g., confirm whether the skill
  is actually removed or actually restored before assuming either), then report back before this
  agent records any evidence.

Run each step from the repository root. After each step, paste the **raw** console output back
(not a summary) so it can be recorded verbatim in the evidence files.

## 1. Live hash reconciliation (baseline)

```powershell
pwsh plugins/sharepoint-agents-and-skills/scripts/reconcile-deployed-skill.ps1 `
  -ConfigFile plugins/sharepoint-agents-and-skills/config.psd1
```

Read-only. Tells us whether the live deployed hash already matches the repository's current
`SKILL.md` hash.

## 2. Real promotion — only if hashes differ

- **If Step 1 shows a match:** skip this step. Record the match as valid reconciliation evidence
  for Stage 8.1.1 — but the real-promotion requirement (Section 6.1) stays open; it will be
  satisfied later by Step 6's restoration, not by this match alone. **Do not create a meaningless
  change to force a promotion event now.**
- **If Step 1 shows a mismatch** (as happened twice before — Phase 4 → Phase 6): the live artifact
  is stale relative to the repository. Redeploying it to match the repository **is** a real
  promotion event and satisfies Section 6.1's real-artifact requirement (but not Section 6.2's
  separate real-version-change requirement — see the outcome summary above).

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

**If this step errors or the dry-run output looks wrong, stop — do not proceed to `-Execute`.**

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
used and what Copilot returned. **If the skill is still available, stop — do not proceed to
Step 6; investigate why removal did not take effect first.**

## 6. Restoration

**If Step 4 or 5 failed, resolve that first — do not attempt restoration on top of an unclear
removal state.**

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

Confirms the restored deployment matches the repository artifact again. **If Step 1 showed a
match (Section 2 skipped), this step's success is what satisfies the real-promotion gate (Section
6.1) — record that explicitly, not as an incidental restoration check. If this step shows a
mismatch, stop and re-run Step 6, or escalate — do not report the exercise as complete.**

## 8. Raw evidence capture

Paste the raw output of Steps 1–3 into
`docs/reports/phase-8-scale-promotion-operations/stage-8.1.1-promotion-path.md`'s evidence-capture
section (Section 8) as a new dated sub-entry, and the raw output of Steps 4–7 into
`docs/reports/phase-8-scale-promotion-operations/stage-8.3.2-retirement-exercise.md`'s Section 7
evidence table. This agent will file both once you provide the raw output — do not paraphrase it
yourself in the interim, per this repository's own "raw output, not summarized prose" convention.
