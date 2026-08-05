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

Per current repository evidence, no additional pilot user is documented beyond Richard (accountable
owner and the only currently documented operator of this deployment). No other party requires
notification on that evidence. This is a repository-evidence statement, not a tenant-wide guarantee
— it has not been independently verified against live tenant usage logs.

## 3. Dependency check

No repository dependency was found in the verified search performed for this document:
- `CEIS-Pilot-Knowledge-Agent`'s grounding configuration references the `CEISPilotKnowledgePages`
  library directly, not the skill; removing the skill does not remove the agent's grounding.
- No other skill or plugin references `review-manual-topics`'s native deployment, per a repository
  grep for the skill name.

**This is a repository-only search and does not rule out an undocumented tenant-side dependency.**
Before running Section 6's removal step, Richard should independently confirm (e.g., by checking
the live `CEIS-Pilot-Knowledge-Agent` configuration and any other tenant artifacts he is aware of)
that nothing tenant-side depends on this skill that this repository search could not see — do not
treat this section's repository-search result alone as sufficient clearance to remove.

## 4. Rollback window

Immediate — restoration (Section 6, step 3 below) is intended to happen in the same interactive
session as removal, per this plan's Task 6.

## 5. Removal of access/credentials

Not applicable — no separate credential exists for this skill beyond the tenant account's own
PnP/Entra session used for every other deployment action.

## 6. Exact commands (Richard runs interactively; not executable by this agent)

**Prerequisite:** a real, filled-in `plugins/sharepoint-agents-and-skills/config.psd1`, copied from
the canonical `plugins/sharepoint-agents-and-skills/config.psd1.example` template (created this
round — see `stage-8.1.1-promotion-path.md` Section 6) and filled in with the real `SiteUrl` (and
`ClientId`/`TenantId` if using app-only auth). The reconciliation script's optional
`-FallbackConfigFile tools/phase-3-sharepoint-discovery/config.psd1` fallback is not required if
the primary config file above is present.

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
session — this document prepares the exercise; it does not perform it. If removal or restoration
fails at any step in Section 6, stop and resolve/recover before proceeding to the next step; do not
record the exercise as complete past a failed step.

**Relationship to Task 2's promotion gate:** if Task 2's initial reconciliation (before this
exercise) found the live hash already matching the repository hash, this exercise's restoration
step (Section 6, step 4) is itself a real deployment of the artifact through the promotion path —
its successful post-restoration reconciliation (Section 6, step 5) satisfies spec Section 6.1's
real-artifact-promoted requirement in that case. It does **not** satisfy Section 6.2's separate
real-version-change requirement, since the restored bytes are unchanged from what was already
live — see `stage-8.1.1-promotion-path.md`'s "Open acceptance items" for that distinction.
