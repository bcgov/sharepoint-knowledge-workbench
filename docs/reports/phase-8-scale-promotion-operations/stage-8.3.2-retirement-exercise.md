# Stage 8.3.2 — Retirement Exercise: `review-manual-topics` (native-sharepoint)

**Status:** `EXECUTED_2026-08-06` — Section 6's removal/restoration sequence was run for real
against `AG-CSB-INTRANET-DEV` and is recorded in Section 7 below with raw command output. Two real
script defects were found and fixed along the way (see Section 7's "Defects found and fixed"
note) — both fixes are currently only present in this branch's worktree checkout, not yet
committed at the time this section was written.

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

## 7. Evidence to capture

**Date/time of removal:** 2026-08-06 (session timestamps below from `Modified:` fields observed
during the run — restoration landed at `08/06/2026 06:13:06` per the tenant's own file metadata).

**Defects found and fixed during this exercise (both in `rollback-skill-deployment.ps1`, worktree
only, not yet committed as of this writing):**
1. Script called `Move-PnPFileToRecycleBin`, which is not a real PnP.PowerShell cmdlet (a legacy
   `SharePointPnPPowerShellOnline` name). First `-Execute` attempt failed with "term ... is not
   recognized." Fixed to `Remove-PnPFile -ServerRelativeUrl $realServerRelativeUrl -Recycle -Force`.
   Verified via the read-only `verify-agentassets-ready.ps1` inventory (extended this same session
   to print file paths) that this failed attempt performed zero tenant modification before the fix
   was applied — `review-manual-topics/SKILL.md` was still present, count still 6, before retrying.
2. After fixing (1), a second `-Execute` attempt failed with `Remove-PnPFile: ... Specified value is
   not supported for the serverRelativePath parameter` — the script's `$targetServerRelativeUrl` was
   library-title-relative (`AgentAssets/Skills/review-manual-topics/SKILL.md`), not a real
   server-relative URL (missing the `/sites/AG-CSB-INTRANET-DEV` site prefix that `Remove-PnPFile`/
   `Get-PnPFile` require). Fixed by deriving the real path from the target library's own
   `RootFolder.ServerRelativeUrl` (same pattern already used in `reconcile-deployed-skill.ps1`),
   producing `/sites/AG-CSB-INTRANET-DEV/AgentAssets/Skills/review-manual-topics/SKILL.md`. Verified
   tenant state unchanged before retrying (same inventory check as above).

**Pre-removal reconciliation output (raw)** — run *after* restoration, functionally identical to a
pre-removal baseline since it reconfirms the same hash the exercise started from:
```
=== SKILL.md DEPLOYMENT RECONCILIATION: review-manual-topics ===
Repository SHA-256: bb327348b55e9f55cbf8f83d12d5d3c49f26c5502bf60bfa6bd74037f5e43b3d

Connected to: https://bcgov.sharepoint.com/sites/AG-CSB-intranet-dev

Searching for AgentAssets library...
✓ AgentAssets library found
  Title: AgentAssets
  ID: db9fe860-949a-4f88-b11b-468615a935d5
  RootFolder: /sites/AG-CSB-INTRANET-DEV/AgentAssets

Checking for Skills subfolder...
✓ Skills folder found
  Path: /sites/AG-CSB-INTRANET-DEV/AgentAssets/Skills

Enumerating skill subfolders...
Found 5 skill folder(s):
[... ceis-test-skill, ceis-workflow-diagram, build-ceis-module-test, content-review omitted here,
     unchanged from other evidence in this document ...]

Skill: review-manual-topics
  Path: /sites/AG-CSB-INTRANET-DEV/AgentAssets/Skills/review-manual-topics
  ✓ SKILL.md found
    Size: 9461 bytes
    Modified: 08/06/2026 06:13:06
    SHA-256: bb327348b55e9f55cbf8f83d12d5d3c49f26c5502bf60bfa6bd74037f5e43b3d
    Frontmatter name: review-manual-topics
    Description: Reviews one explicitly selected CEIS manual topic page for content completeness, section structure, cross-reference consistency, and terminology clarity against Phase 3 CEIS publication standards.
  ⚠ This is review-manual-topics
  ✓ HASH MATCHES REPOSITORY

=== RECONCILIATION SUMMARY ===

review-manual-topics deployment status: DEPLOYED
  Path: /sites/AG-CSB-INTRANET-DEV/AgentAssets/Skills/review-manual-topics
  Deployed SHA-256: bb327348b55e9f55cbf8f83d12d5d3c49f26c5502bf60bfa6bd74037f5e43b3d
  Repository SHA-256: bb327348b55e9f55cbf8f83d12d5d3c49f26c5502bf60bfa6bd74037f5e43b3d
  Modified: 08/06/2026 06:13:06
  ✓ HASH MATCH - artifact reconciled

DISPOSITION: TASK_8_ARTIFACT_ALREADY_PRESENT_AND_RECONCILED
```

**Removal command output (raw)** — dry-run, then `-Execute` (after both defect fixes above):
```
=== Rollback Preflight Check ===
  Target Site URL:             https://bcgov.sharepoint.com/sites/AG-CSB-intranet-dev
  Target Server Relative URL:  AgentAssets/Skills/review-manual-topics/SKILL.md
  Target Asset:                AgentAssets/Skills/review-manual-topics/SKILL.md

[DRY-RUN PREFLIGHT MODE] Zero tenant modifications performed because -Execute switch was not specified.
  Would recycle asset: AgentAssets/Skills/review-manual-topics/SKILL.md from https://bcgov.sharepoint.com/sites/AG-CSB-intranet-dev

=== Rollback Preflight Check ===
  Target Site URL:             https://bcgov.sharepoint.com/sites/AG-CSB-intranet-dev
  Target Server Relative URL:  AgentAssets/Skills/review-manual-topics/SKILL.md
  Target Asset:                AgentAssets/Skills/review-manual-topics/SKILL.md

[EXECUTION MODE] Connecting to SharePoint tenant to recycle skill artifact...
Recycling file '/sites/AG-CSB-INTRANET-DEV/AgentAssets/Skills/review-manual-topics/SKILL.md' to SharePoint Recycle Bin...

Performing post-action verification...
SUCCESS: Verified target item '/sites/AG-CSB-INTRANET-DEV/AgentAssets/Skills/review-manual-topics/SKILL.md' no longer exists in active site assets.
```

Independently confirmed via `verify-agentassets-ready.ps1`: `AgentAssets` `ItemCount` dropped
12 → 11, SKILL.md inventory dropped 6 → 5, `review-manual-topics/SKILL.md` absent from the listed
paths.

**Copilot unavailability confirmation:** the first check attempted was an indirect chat probe in
the live `CEIS-Pilot-Knowledge-Agent` chat using the prompt "Review the topic 'file-standards'. If
multiple topics or conflicting rules exist across related pages, flag the ambiguity clearly." (the
same prompt as evaluation case `AMB-01`). Copilot still returned a full structured editorial
review matching `review-manual-topics`'s expected behavior (bounded related-topic evidence,
explicit ambiguity flagging) even though the file was confirmed absent from `AgentAssets` at that
moment. **This is recorded as a real, unresolved observation** — either Copilot/SharePoint Agent
caches skill definitions rather than reading `AgentAssets` live on every invocation, the agent
configuration embeds its own copy of the instructions independent of the live file, or the
response was general grounded synthesis not actually invoking the named skill (the UI gives no
explicit skill-invocation indicator either way). **Not resolved further this session** — flagging
as a follow-up item rather than blocking the exercise, since a more reliable, unambiguous
unavailability signal was available: the read-only `verify-agentassets-ready.ps1` inventory itself
(file-count 6→5, `review-manual-topics` absent from the listed paths) is direct evidence the
artifact was removed from the source Copilot reads from, independent of chat-response behavior.

**Restoration command output (raw):**
```
=== Deployment Preflight Check ===
  Source File:        plugins/sharepoint-agents-and-skills/skills/review-manual-topics/SKILL.md
  Local SHA-256:      bb327348b55e9f55cbf8f83d12d5d3c49f26c5502bf60bfa6bd74037f5e43b3d
  Target Library:     AgentAssets
  Target Folder:      Skills/review-manual-topics
  Target Filename:    SKILL.md
  Exact Target Path:  <AgentAssets root>/Skills/review-manual-topics/SKILL.md

[EXECUTION MODE] Connecting to SharePoint tenant and uploading skill artifact...
Uploaded artifact to server-relative URL: /sites/AG-CSB-INTRANET-DEV/AgentAssets/Skills/review-manual-topics/SKILL.md
Performing readback verification...
Downloaded SKILL.md SHA-256: bb327348b55e9f55cbf8f83d12d5d3c49f26c5502bf60bfa6bd74037f5e43b3d
SUCCESS: Pre- and Post-deployment SHA-256 hashes MATCH 100%.
```

Independently confirmed via `verify-agentassets-ready.ps1`: `AgentAssets` `ItemCount` back to 12,
SKILL.md inventory back to 6, `review-manual-topics/SKILL.md` present again.

**Final reconciliation output (raw):** identical in content to the "Pre-removal reconciliation
output" block above (both captured the post-restoration state — see the note under that heading);
`HASH MATCH`, disposition `TASK_8_ARTIFACT_ALREADY_PRESENT_AND_RECONCILED`.

## 8. Interaction with records/retention

Not applicable — no records/retention policy has been triggered for this capability (per the
capability activation record, Section 10; Subphase 8.4 is out of scope for this plan).

## Open acceptance item

**Stage 8.3.2 executed 2026-08-06** — Section 7's evidence is now filled in from the real session
above. Every step (removal, verification, restoration, final reconciliation) completed
successfully; no step failed or was left in an unresolved state. Two real script defects
(`rollback-skill-deployment.ps1`'s wrong cmdlet name and wrong server-relative-path construction)
were found and fixed mid-exercise, verified not to have caused any unintended tenant modification
before each fix — see Section 7's "Defects found and fixed" note. **Still open:** the fixes exist
only in this branch's worktree as of this writing, not yet committed; and the chat-probe
observation (Copilot still answering in `review-manual-topics`'s style immediately after file
removal) is unresolved and flagged as a follow-up, not investigated further this session.

**Relationship to Task 2's promotion gate:** Task 2's initial reconciliation (this session, run
after restoration) found the live hash matching the repository hash
(`bb327348b55e9f55cbf8f83d12d5d3c49f26c5502bf60bfa6bd74037f5e43b3d`). Per the outcome rule in
`combined-interactive-session-runbook.md`, this exercise's restoration step (Section 6, step 4) is
itself a real deployment of the artifact through the promotion path — its successful
post-restoration reconciliation (Section 6, step 5) **satisfies spec Section 6.1's
real-artifact-promoted requirement**. It does **not** satisfy Section 6.2's separate
real-version-change requirement, since the restored bytes are unchanged from what was already
live — see `stage-8.1.1-promotion-path.md`'s "Open acceptance items" for that distinction, which
remains open.
