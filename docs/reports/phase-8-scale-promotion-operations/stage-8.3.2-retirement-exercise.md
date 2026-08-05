# Stage 8.3.2 — Retirement Exercise: `review-manual-topics` (native-sharepoint)

**Status:** `PROCEDURE_READY_NOT_EXECUTED`. This document is a procedure and evidence template
only. **No removal, restoration, or other tenant action has occurred.** Do not read any section
below as a completed exercise — every field marked "(to be filled in by Richard)" is genuinely
empty until the live session in Section 6 happens.

## 1. Retirement trigger

**Trigger for this exercise:** a planned Phase 8 Stage 8.3.2 exercise, not a real incident.
Distinguished explicitly from Phase 4 Task 12's rollback
(`docs/reports/phase-4-native-sharepoint-skills/EVID-PHASE4-TASK12-ROLLBACK-COMPLETION.md`), which
is cited here as **precedent evidence that the mechanism works**, not as satisfying this stage's
own requirement for a retirement exercised under this plan.

## 2. Notification

Not applicable — single-user pilot (Richard is both the accountable owner and the only user of
this deployment). No other party requires notification.

## 3. Dependency check

No other artifact in this repository or tenant depends on this skill's presence:
- `CEIS-Pilot-Knowledge-Agent`'s grounding configuration references the `CEISPilotKnowledgePages`
  library directly, not the skill; removing the skill does not remove the agent's grounding.
- No other skill or plugin references `review-manual-topics`'s native deployment.
(To be re-confirmed at execution time if the tenant state has changed since this document was
written.)

## 4. Rollback window

Immediate — restoration (Section 6, step 3 below) is intended to happen in the same interactive
session as removal, per this plan's Task 6.

## 5. Removal of access/credentials

Not applicable — no separate credential exists for this skill beyond the tenant account's own
PnP/Entra session used for every other deployment action.

## 6. Exact commands (Richard runs interactively; not executable by this agent)

**Prerequisite:** a real, filled-in `plugins/sharepoint-agents-and-skills/config.psd1` (and, if
the reconciliation script's fallback path is used, `tools/phase-3-sharepoint-discovery/
config.psd1`) must exist locally — both are git-ignored; only their `.example` templates are
tracked in this repository.

```powershell
# Step 1 — confirm current state before touching anything
pwsh plugins/sharepoint-agents-and-skills/scripts/reconcile-deployed-skill.ps1 `
  -ConfigFile plugins/sharepoint-agents-and-skills/config.psd1

# Step 2 — remove (dry-run first, per the script's own default; then -Execute)
pwsh plugins/sharepoint-agents-and-skills/scripts/rollback-skill-deployment.ps1 `
  -ConfigFile plugins/sharepoint-agents-and-skills/config.psd1 `
  -ManifestFile plugins/sharepoint-agents-and-skills/deployment-manifest.example.json
# review dry-run output, then:
pwsh plugins/sharepoint-agents-and-skills/scripts/rollback-skill-deployment.ps1 `
  -ConfigFile plugins/sharepoint-agents-and-skills/config.psd1 `
  -ManifestFile plugins/sharepoint-agents-and-skills/deployment-manifest.example.json `
  -Execute -ConfirmExactTarget "CONFIRM-REMOVE"

# Step 3 — confirm unavailability: in the live Copilot chat for CEIS-Pilot-Knowledge-Agent,
# attempt to invoke review-manual-topics and confirm it is no longer offered/available.

# Step 4 — restore (re-deploy) so the pilot capability is not left retired by this exercise
pwsh plugins/sharepoint-agents-and-skills/scripts/deploy-and-verify-skill.ps1 `
  -ConfigFile plugins/sharepoint-agents-and-skills/config.psd1 `
  -ManifestFile plugins/sharepoint-agents-and-skills/deployment-manifest.example.json `
  -Execute

# Step 5 — final reconciliation, confirming restoration matches the repository artifact
pwsh plugins/sharepoint-agents-and-skills/scripts/reconcile-deployed-skill.ps1 `
  -ConfigFile plugins/sharepoint-agents-and-skills/config.psd1
```

## 7. Evidence to capture (template — empty until Richard runs the above)

| Field | Value |
|---|---|
| Date/time of removal | (to be filled in by Richard) |
| Pre-removal reconciliation output (raw) | (to be filled in by Richard) |
| Removal command output (raw) | (to be filled in by Richard) |
| Copilot unavailability confirmation | (to be filled in by Richard) |
| Restoration command output (raw) | (to be filled in by Richard) |
| Final reconciliation output (raw) | (to be filled in by Richard) |

## 8. Interaction with records/retention

Not applicable — no records/retention policy has been triggered for this capability (per the
capability activation record, Section 10; Subphase 8.4 is out of scope for this plan).

## Open acceptance item

**Stage 8.3.2 remains open** until Section 7's evidence table is actually filled in from a real
session — this document prepares the exercise; it does not perform it.
