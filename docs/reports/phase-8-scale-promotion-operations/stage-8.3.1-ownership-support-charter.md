# Stage 8.3.1 — Ownership and Support Charter: `review-manual-topics` (native-sharepoint)

**Status:** `CHARTER_DOCUMENTED`. **Not yet accepted per spec Section 8.1** — that stage requires
"a named owner and a real incident (or drill) run through the documented process." The drill is a
separate document (`stage-8.3.1-incident-drill.md`); this charter alone does not close the stage.

**Scope:** the `review-manual-topics` **native-sharepoint** runtime only, in tenant
`AG-CSB-INTRANET-DEV`. This formalizes, as a first-class Phase 8 artifact, what Phase 4 Task 12
recorded informally (`docs/reports/phase-4-native-sharepoint-skills/TASK-12-ROLLBACK-EXERCISE-
AND-EXIT-GATE.md`, Section B.2) — it is a promotion of that record, not a duplicate contradicting it.

## Accountable owner

**Richard Fremmerlid** — unchanged since Phase 4 exit (`TASK-12-ROLLBACK-EXERCISE-AND-EXIT-
GATE.md`, Section B.2: "Owner: Richard Fremmerlid (pilot lead)").

## Technical maintainer

**Richard Fremmerlid** — same person. The deployment/reconciliation/rollback scripts
(`plugins/sharepoint-agents-and-skills/scripts/deploy-and-verify-skill.ps1`,
`reconcile-deployed-skill.ps1`, `rollback-skill-deployment.ps1`) and the `SKILL.md` content itself
are both maintained by the same person who owns the capability. `PROVISIONAL`: no distinct
maintainer role has ever been exercised separately from the accountable-owner role.

## Content owner

**Richard Fremmerlid**, in his role as CEIS manual pilot lead — the `SKILL.md` content's editorial
standards reference "Phase 3 CEIS publication standards" (per the skill's own description field),
which Richard also owns as pilot lead. No separate content-authority person exists.

## Deployment authority

**Richard Fremmerlid** — the only person with the interactive PnP/Entra credentials this
capability's deployment scripts require (`Connect-PnPOnline ... -Interactive`). This agent
(and any future automated session) has no deployment authority — it can prepare commands and
evidence templates but cannot execute a tenant write.

## Incident triage path

1. Richard (or, in principle, any observer with Copilot access to `CEIS-Pilot-Knowledge-Agent`)
   notices anomalous skill behavior.
2. Richard checks the live transcript/response against the skill's documented contract
   (single-topic-only, read-only, the prohibited-scope list in `SKILL.md`) and against known,
   already-recorded limitations (see "Known limitations" below).
3. Richard decides: accept-and-monitor (if the behavior matches an already-accepted known
   limitation), fix-and-redeploy (via the Stage 8.1.1 promotion path), or disable (via the
   rollback/emergency-disable step in that same document).
4. Richard records the decision and evidence.

**Real gap, stated plainly:** there is no monitoring mechanism that surfaces an anomaly to
Richard automatically — step 1 depends entirely on a human manually watching a live Copilot
session or reviewing a transcript afterward. This is the same gap the incident drill
(`stage-8.3.1-incident-drill.md`) walks through concretely.

## Review cadence

Carried forward from Task 12's stated intent: monthly review of execution logs (if available) to
detect anomalies; annual review against latest SharePoint/Copilot platform changes. **Real
finding, stated rather than reset:** the skill has been deployed since 2026-08-01; **no monthly
review has been recorded as having actually happened** in this repository's evidence trail
between then and now (only ad hoc reconciliation during Phase 6's live session on 2026-08-04,
which found the deployment stale — that is exactly the kind of drift a monthly review is meant to
catch, and it was caught only incidentally, not by the stated cadence). `PROVISIONAL`: whether to
formalize an actual monthly review process (and who runs it, since only one person exists) is an
open item for whoever executes Stage 8.3.1 beyond this charter, not decided here.

## Escalation

**None defined.** This is a single-person pilot; there is no second person to escalate to. Stated
plainly rather than inventing an escalation chain that does not exist.

## Service boundary

Dev-tenant pilot only (`AG-CSB-INTRANET-DEV`). No production tenant, no production users, no
service-level agreement of any kind. Any statement of uptime, response time, or support hours
would be invented — none exists and none is claimed here.

## Dependency ownership

- The three deployment/reconciliation/rollback PowerShell scripts: owned by this repository's
  `sharepoint-agents-and-skills` plugin.
- The `SKILL.md` content itself: owned by this repository's `plugins/sharepoint-agents-and-
  skills/skills/review-manual-topics/` directory.
- The `AgentAssets` document library and `CEIS-Pilot-Knowledge-Agent` Copilot agent: tenant-side
  artifacts, not owned by this repository, but administered by Richard within the dev tenant.
- No external team or third-party dependency exists for this capability.

## Handoff and succession

**`DEFERRED_UNTIL_EVIDENCE`.** No second person has ever operated, deployed, or reconciled this
capability. A handoff procedure written today would be speculative, not evidence-derived — Stage
8.3.3's onboarding guide (`stage-8.3.3-onboarding-guide.md`) is the closest available artifact,
and it explicitly still needs a real unfamiliar-operator attempt before any handoff claim could be
made.

## Known limitations (carried forward, not re-litigated here)

Cited from the capability activation record (`docs/reports/phase-8-scale-promotion-operations/
capability-activation-record-review-manual-topics.md`, Section 6) as the concrete inputs an
incident-triage decision would actually need to check against:

1. Related-topic-cap enforcement is instruction-governed only in this runtime (live-observed
   drift: `AMB-01` consulted 3 then 7 related topics against a cap of 2).
2. 4-identity permission matrix was waived, not executed.
3. Negative/ambiguous evaluation categories were only partially executed at Phase 4 exit.
4. The skill's delete capability is gated only by SharePoint's own permission enforcement, not by
   the skill's own design scope.
