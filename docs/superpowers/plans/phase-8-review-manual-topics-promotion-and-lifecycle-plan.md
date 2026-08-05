# Phase 8 Implementation Plan — Promotion & Lifecycle for `review-manual-topics` (native runtime)

**Status:** approved-scope implementation plan, not a new authorization gate. Authorization already
recorded in `start-here.md`'s "Phase 8 — authorized" section and
`docs/reports/phase-8-scale-promotion-operations/capability-activation-record-review-manual-topics.md`
(commit `411bc36`). This plan turns that authorization into concrete, executable tasks for
Subphases 8.1 and 8.3 only.

**Scope:** the Phase 4-piloted `review-manual-topics` **native-sharepoint** runtime, in the
`AG-CSB-INTRANET-DEV` tenant. **Out of scope:** the `repository-claude` runtime (no SharePoint
promotion/lifecycle question applies to it), Subphases 8.2/8.4, and any Phase 3/5/6/7 capability.

## Task status (updated after this round — no false completion of Subphase 8.1 or 8.3)

| Task | Agent-executable part | Status | Human-dependent part | Status |
|---|---|---|---|---|
| 1 — promotion path | full document | `DONE` — `docs/reports/phase-8-scale-promotion-operations/stage-8.1.1-promotion-path.md` | — | — |
| 2 — real promotion exercise | commands/templates prepared | `DONE` (prep only) | live reconciliation + promote-if-differing + verify | `PENDING_RICHARD` |
| 3 — version-compatibility policy | policy written (in Task 1's file, §10) | `DONE` (drafted) | real version/promotion check to cite | `PENDING_TASK_2` |
| 4 — ownership/support charter | full document | `DONE` — `stage-8.3.1-ownership-support-charter.md` | — | — |
| 5 — incident drill | tabletop performed | `DONE` — `stage-8.3.1-incident-drill.md` | (none — drill is tabletop by design) | n/a |
| 6 — retirement exercise | procedure + evidence template + commands | `DONE` — `stage-8.3.2-retirement-exercise.md` | live remove/confirm/restore + raw evidence | `PENDING_RICHARD` |
| 7 — onboarding guide | guide + unfamiliar-operator checklist | `DONE` — `stage-8.3.3-onboarding-guide.md` | actual unfamiliar-person attempt | `PENDING_ATTEMPT` |

**Subphase 8.1 exit criteria (spec Section 12, "Promotion and release"): not yet met.** A named
owner exists and the path is defined, but no real artifact has yet been promoted through it and no
real version bump has been checked against the compatibility policy — both wait on Task 2's live
session.

**Subphase 8.3 exit criteria (spec Section 12, "Ownership and lifecycle"): partially met.**
Ownership/support charter is written and a drill was run through the documented process (this
satisfies Stage 8.3.1's own verification clause, which accepts "a real incident **or** drill").
Retirement (8.3.2) is prepared but not exercised — `PENDING_RICHARD`. Onboarding (8.3.3) has a
guide but no completed attempt — `PENDING_ATTEMPT`. **Subphase 8.3 as a whole is not yet fully
closed** because 8.3.2 and 8.3.3 remain open, even though 8.3.1 alone is arguably satisfied.

A combined runbook for Richard's one interactive tenant session (covering both Task 2's real
promotion check and Task 6's real retirement exercise) is at
`docs/reports/phase-8-scale-promotion-operations/combined-interactive-session-runbook.md`.

## Reconnaissance (performed before this plan, facts not assumed)

- **Single tenant, no separate test/production environment exists.** `tools/phase-4-native-
  sharepoint-skills/tenant-config.psd1` names one site: `AG-CSB-INTRANET-DEV`. There is no
  provisioned test or production SharePoint site for this capability. **This changes what "dev/test/
  production promotion path" (spec Section 6.1) must mean today** — see Task 1.
- **All tenant-write scripts require interactive human auth.** `deploy-and-verify-skill.ps1`,
  `reconcile-deployed-skill.ps1`, `rollback-skill.ps1` (and every other Phase 4/6 script) call
  `Connect-PnPOnline ... -Interactive`. This agent's execution environment has PnP.PowerShell 3.3.0
  installed but no browser/Entra session — **it cannot itself perform any live tenant action.**
  Every real tenant step below must be run by Richard interactively, exactly as in every prior
  phase; this plan's role is to specify the exact command and capture the resulting evidence.
- **The deployed skill has been redeployed at least twice already** (Phase 4 Task 8, then Phase 6's
  live session after finding it stale). The activation record already flags this as `PROVISIONAL` —
  re-verify the current live hash before treating any specific version as the promotion baseline.
- **No version field exists in `SKILL.md`'s own front matter** (only `name`/`description`). Version
  identity today comes entirely from `deployment-manifest.example.json` and the tenant-config's
  recorded hash — Task 3's compatibility policy must work with this real mechanism, not an
  imagined semver field.
- **A real retirement/rollback has already been exercised once**, with full evidence
  (`docs/reports/phase-4-native-sharepoint-skills/EVID-PHASE4-TASK12-ROLLBACK-COMPLETION.md`).
  Task 6 treats this as strong precedent, not as automatically satisfying Stage 8.3.2 for a
  Phase-8-promoted version — a fresh, minimal exercise against whatever this plan actually promotes
  is still required by the spec ("exercised against one real... retirement").

## Task 1 — Stage 8.1.1 promotion-path document

**No tenant action.** Define, in writing, what "promotion path" means given the single-tenant
reality above:

- **Artifact identity:** the `review-manual-topics` `SKILL.md` file content, identified by its
  SHA-256 hash (the mechanism already in use — `deployment-manifest.example.json` +
  `tenant-config.psd1`'s recorded hash).
- **Environment boundaries (today):** one real boundary exists — *repository* (source of truth,
  version-controlled) vs. *deployed* (the live `AgentAssets/Skills/review-manual-topics/` object in
  `AG-CSB-INTRANET-DEV`). Document explicitly that no test/production tier exists yet; promotion
  today means repository → the one live dev tenant, with reconciliation as the only
  "environment-boundary" check available.
- **Approval point:** Richard (accountable owner, per the activation record) reviews any `SKILL.md`
  diff before it is deployed — same gate already implicit in every prior phase, made explicit here.
- **Validation before promotion:** hash comparison between the repository artifact and the
  manifest-declared expected hash (`deploy-and-verify-skill.ps1`'s existing pre-upload check).
- **Deployment step:** `deploy-and-verify-skill.ps1 -Execute` (Richard runs interactively).
- **Post-promotion verification:** `reconcile-deployed-skill.ps1` (Richard runs interactively) —
  confirms deployed hash matches the just-promoted repository hash.
- **Rollback:** `rollback-skill.ps1` / `task-12-rollback.ps1` (already evidenced in Phase 4 Task 12).
- **Evidence capture:** a new file under `docs/reports/phase-8-scale-promotion-operations/`
  recording date/time, before/after hash, command output, and Richard's approval note.
- **Emergency disablement:** identical to rollback (delete the skill folder) — already documented
  in the activation record Section 8.

**Deliverable:** `docs/reports/phase-8-scale-promotion-operations/stage-8.1.1-promotion-path.md`.
**Acceptance:** document exists, cites only real mechanisms already in this repo (no invented
tooling), and defines the approval/validation/rollback points above without gaps.

## Task 2 — Stage 8.1.1 real promotion exercise (requires Richard, live tenant)

**Real tenant action, cannot be executed by this agent.**

1. Richard confirms the currently *live* deployed hash by running
   `pwsh tools/phase-4-native-sharepoint-skills/deployment/scripts/task-8-deploy-review-manual-topics.ps1`
   in dry-run (no `-Execute`) or the underlying `reconcile-deployed-skill.ps1` interactively, and
   reports the result back.
2. If the live hash matches the current repository `SKILL.md` hash, promotion is a no-op this
   round — record that finding as the "real artifact promoted through the path" evidence (a
   verified-current-and-unchanged promotion still counts as exercising the path, per spec Section
   6.1's requirement, since the path's validation/verification steps still ran for real).
3. If the live hash differs (stale, as it has been twice before), Richard re-runs
   `task-8-deploy-review-manual-topics.ps1 -Execute`, then `reconcile-deployed-skill.ps1` to confirm.
4. Either way, Richard reports the exact command output back to this session so it can be recorded
   verbatim in the Task 1 evidence file (per this repo's own "raw output, not summarized prose"
   dispute-resolution convention).

**Prerequisite / blocker:** Richard's own interactive PnP session against `AG-CSB-INTRANET-DEV`.
**Deliverable:** the evidence file from Task 1, filled in with real command output.
**Acceptance:** a real promotion-path run happened (verify-or-redeploy), with raw evidence, not a
described intention.

## Task 3 — Stage 8.1.2 version-compatibility policy (single-capability scope)

**No tenant action.** Document compatibility rules for this one capability's real contracts:

- **Schema compatibility:** `SKILL.md`'s YAML front matter (`name`, `description`) plus its markdown
  body's documented input/output contract (single-topic-only, read-only synthesis, prohibited
  scopes already listed in the file itself).
- **Deployment-manifest compatibility:** `deployment-manifest.example.json`'s hash field must always
  match the actually-deployed `SKILL.md` — this is the whole reconciliation mechanism; state it as
  the compatibility rule, not a new one.
- **Migration/deprecation:** any future `SKILL.md` content change is a new version by hash
  definition (no semver exists); deprecating the whole capability follows Task 6's retirement
  procedure.
- Explicitly state: cross-capability compatibility (e.g., with the `repository-claude` runtime, or
  any Phase 3/5/6 artifact) is `DEFERRED_UNTIL_EVIDENCE` per the spec — not addressed here.

**Deliverable:** appended to the same `stage-8.1.1-promotion-path.md` file as a "Version
Compatibility Policy" section (one document, since both stages concern the same one artifact —
avoids an unnecessary second file for a single-capability policy).
**Acceptance:** at least one real version check (Task 2's exercise) is referenced as having been
checked against this policy.

## Task 4 — Stage 8.3.1 ownership/support charter

**No tenant action.** Formalize what Phase 4 Task 12 Section B.2 already informally recorded, as
its own named Phase 8 artifact (not a duplicate — a promotion to a first-class charter):

- Accountable owner: Richard Fremmerlid.
- Support owner: Richard Fremmerlid (same person; `PROVISIONAL` per the activation record — no
  split exists yet).
- Incident triage path: manual — Richard observes an issue, decides disable-vs-fix, executes
  rollback if needed (Task 1's rollback step).
- Review cadence: carry forward Task 12's stated cadence (monthly log review if logs exist; annual
  platform-change review) — flag as `PROVISIONAL` since no monthly review has actually happened yet
  (the skill has existed since 2026-08-01; state whether one is now overdue as a real finding, not
  silently reset the clock).
- Escalation: none defined beyond Richard himself (single-person pilot) — state this plainly rather
  than inventing an escalation chain that doesn't exist.
- Service boundary: dev-tenant pilot only, no SLA, no production users.
- Dependency ownership: the deployment/reconciliation/rollback scripts are owned by this repository
  (`sharepoint-agents-and-skills` plugin); no external team dependency exists.
- Handoff/succession: not yet defined — `DEFERRED_UNTIL_EVIDENCE`, no second person has ever
  operated this capability.

**Deliverable:** `docs/reports/phase-8-scale-promotion-operations/stage-8.3.1-ownership-support-charter.md`.
**Acceptance:** every field above is stated from real evidence or explicitly marked
`PROVISIONAL`/`DEFERRED_UNTIL_EVIDENCE` — no invented process.

## Task 5 — Stage 8.3.1 incident/drill exercise

**Simulated drill, no live tenant action required** (spec Section 8.1 permits "a real incident or
controlled drill" — no tenant access exists for a live drill in this session, so this task is
explicitly a tabletop exercise, not disguised as a live test):

1. Pick a concrete, plausible incident scenario grounded in a real known limitation from the
   activation record (Section 6) — recommended: "the native runtime is observed live-consulting
   more than the 2-topic cap again" (exactly the Phase 6 `AMB-01` finding recurring).
2. Walk the charter's incident-triage path (Task 4) against that scenario step by step: who notices,
   what they check, what decision they make (disable vs. accept-and-monitor vs. escalate — noting
   there is no one to escalate to), what evidence they'd capture.
3. Record where the drill exposes a real gap in the charter (e.g., "no monitoring exists to notice
   this without a human manually re-reading a transcript" — state this plainly if true, don't
   soften it).

**Deliverable:** `docs/reports/phase-8-scale-promotion-operations/stage-8.3.1-incident-drill.md`.
**Acceptance:** a specific scenario was actually walked through (not described in the abstract), and
any real gap found is stated as a gap, not smoothed over.

## Task 6 — Stage 8.3.2 retirement exercise

**Requires Richard for the live half; the staging/decision half does not.**

1. Reuse Phase 4 Task 12's rollback evidence
   (`EVID-PHASE4-TASK12-ROLLBACK-COMPLETION.md`) as **precedent evidence**, cited explicitly — do
   not re-describe it as fresh Phase 8 evidence.
2. Define a fresh, minimal staged retirement scoped to *this* plan's own promotion exercise (Task
   2): after Task 2's real promotion (or verified-current no-op) is recorded, Richard removes the
   skill folder once more, confirms via Copilot that it's unavailable, then re-deploys it (so the
   pilot capability is not left permanently retired by a documentation exercise). This is the same
   mechanical action as Task 1's rollback step, exercised here specifically as the Stage 8.3.2
   deliverable rather than an emergency-disable deliverable.
3. Record: retirement trigger used ("Phase 8 exercise, not a real incident"), notification (none
   needed — single-user pilot), dependency check (none — no other artifact depends on this skill),
   rollback window (immediate re-deploy, same session), removal of access/credentials (not
   applicable — no separate credential exists for this skill), evidence preservation (this record
   itself).

**Prerequisite / blocker:** Richard's own interactive PnP session (same blocker as Task 2 — can be
combined into the same live session).
**Deliverable:** `docs/reports/phase-8-scale-promotion-operations/stage-8.3.2-retirement-exercise.md`.
**Acceptance:** a real removal-and-restoration happened this Phase 8 round (not just cited from
Phase 4), with raw command evidence.

## Task 7 — Stage 8.3.3 onboarding/adoption guide

**No tenant action.** Write an onboarding guide a person unfamiliar with this capability could
follow: what the skill is, where it lives (repo path + deployed path), how to verify it's current
(Task 2's reconciliation command), how to promote a change (Task 1's path), how to roll it back
(existing rollback script), who owns it (Task 4's charter). Explicitly note this guide has **not**
been attempted by an actual unfamiliar person yet — spec Section 8.3 requires the attempt, not just
the document; record that as an open item rather than claiming the stage is closed.

**Deliverable:** `docs/reports/phase-8-scale-promotion-operations/stage-8.3.3-onboarding-guide.md`.
**Acceptance:** guide exists and is accurate against the real repository paths/commands; the
"not yet attempted by an unfamiliar person" gap is stated explicitly, not silently closed.

## Sequencing and blockers

```text
Task 1 (no blocker) → Task 2 (blocked on Richard, live tenant)
Task 3 (no blocker, depends on Task 2's result for its "one real check" citation)
Task 4 (no blocker) → Task 5 (no blocker, depends on Task 4)
Task 6 (blocked on Richard, live tenant — can share Task 2's live session)
Task 7 (no blocker)
```

**Real blocker for this session:** Tasks 2 and 6 require Richard's own interactive PnP/Entra
session against `AG-CSB-INTRANET-DEV` — this agent has no credentials and cannot perform them.
Tasks 1, 3, 4, 5, 7 have no such blocker and can proceed now.

## Explicit exclusions (restated)

- Subphase 8.2 (cross-capability monitoring) and Subphase 8.4 (records/retention/audit) — out of
  scope, entry gates not met.
- Phase 3's library, Phase 5's agent, Phase 6's multi-runtime model, Phase 7's Cowork/Studio
  evaluation — no activation, no implication that any of their own exit/re-entry conditions changed.
- The `repository-claude` runtime of this same capability — no SharePoint promotion/lifecycle
  question applies to it; not addressed by this plan.
