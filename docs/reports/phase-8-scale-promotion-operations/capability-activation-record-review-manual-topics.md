# Phase 8 Capability Activation Record — `review-manual-topics` (native SharePoint skill)

**Status:** `CONFIRMED` — this record satisfies `docs/superpowers/specs/phase-8-scale-promotion-operations-spec.md`
Section 5's prerequisite before any Stage 8.1.1/8.3 work begins.

**Authorization basis:** Richard authorized Phase 8 work on 2026-08-04, scoped only to a capability
whose own originating phase has independently reached its exit gate. See `start-here.md`'s "Phase 8
— authorized to begin, scoped to the Phase 4 capability only" section for the full authorization
record. **Scope of this record and all Phase 8 work derived from it: Subphases 8.1 (promotion) and
8.3 (ownership/lifecycle) only.** Subphases 8.2 (cross-capability monitoring) and 8.4
(records/retention/audit) are out of scope — their own entry gates are not met (8.2 requires ≥2
operational capabilities; 8.4 requires a Phase 3 retrospective trigger, and Phase 3's own exit gate
is not met). Phase 3, Phase 5, Phase 6, and Phase 7's deferred live-validation work are explicitly
**not** part of this activation — Phase 7 in particular remains paused at its own research
checkpoint, unaffected by this record.

## 1. Capability name and type

- **Capability:** `review-manual-topics`
- **Type:** native SharePoint Copilot skill (`AgentAssets/Skills/review-manual-topics/SKILL.md`),
  one of two runtimes of the same capability defined in the `sharepoint-agents-and-skills` plugin
  (the other runtime, `repository-claude`, is out of this record's scope — it is not a
  SharePoint-native deployable artifact and has no promotion/lifecycle question of the kind
  Subphase 8.1/8.3 addresses).

## 2. Originating phase and exit evidence

- **Originating phase:** Phase 4 (Native SharePoint Skills Pilot).
- **Exit evidence:** `docs/reports/phase-4-native-sharepoint-skills/phase-4-exit-gate-evidence.md`
  — every exit-gate row `COMPLETE` or `WAIVED`, every disposition "Accepted per `start-here.md`."
  Supporting per-task evidence: `EVID-PHASE4-TASK8-DEPLOYMENT.md`, `EVID-PHASE4-TASK8A-
  RECONCILIATION.md`, `TASK-9-METADATA-VISIBILITY-REPORT.md`, `EVID-PHASE4-TASK9-METADATA-PROBE-
  RESULTS.md`, `TASK-10-PERMISSION-EVALUATION-PLAN.md`, `PHASE-4-LICENSING-CONSTRAINT.md`,
  `TASK-11-SAFETY-EVALUATION-REPORT.md`, `EVID-PHASE4-TASK11-SAFETY-PROBE-RESULTS.md`,
  `TASK-12-ROLLBACK-EXERCISE-AND-EXIT-GATE.md`, `EVID-PHASE4-TASK12-ROLLBACK-COMPLETION.md`.
- **Exit gate satisfied:** "One native skill deployed and evaluated with evidence across all five
  evaluation categories; manual deployment steps documented as automation candidates; no
  oversharing/permission failures" (master initiative plan, Phase 4 exit gate) — met, with two
  explicitly recorded exceptions carried forward as known limitations (Section 6 below), not
  hidden: the 4-identity permission matrix was `WAIVED` (not executed), and negative/ambiguous
  evaluation categories were only partially executed at Phase 4 exit.

## 3. Accountable owner

- **Richard Fremmerlid** (pilot lead) — per `TASK-12-ROLLBACK-EXERCISE-AND-EXIT-GATE.md` Section
  B.2, unchanged since Phase 4 exit. `CONFIRMED`.

## 4. Current environment and users

- **Tenant:** `AG-CSB-INTRANET-DEV` (dev/pilot environment only — no production tenant, no
  production users).
- **Deployed location:** `AgentAssets/Skills/review-manual-topics/SKILL.md`.
- **Current deployed hash:** the skill has been deployed and redeployed twice in this repository's
  history — first at Phase 4 Task 8 (hash `9586379f777d2064004e747b2d73e49a3d16680efd0dc3e2c67d5d3c5e71ce2c`),
  then found stale and redeployed during Phase 6's live native-runtime execution (2026-08-04),
  byte-for-byte hash match confirmed at that point. **`PROVISIONAL`** — this record does not
  re-verify the currently live hash; before any Stage 8.1.1 promotion-path work treats a specific
  artifact version as the baseline to promote, re-run the reconciliation script
  (`tools/phase-4-native-sharepoint-skills/deployment/scripts/reconcile-deployed-skill.ps1`) against
  the real tenant and record the result, since staleness was found twice already in this
  capability's history.
- **Users:** the pilot lead only, driving live Copilot chat manually (`CEIS-Pilot-Knowledge-Agent`).
  No other users have used this deployment.

## 5. Scope proposed for promotion

- **In scope for Subphase 8.1 (Stage 8.1.1):** define a dev → test → production promotion path for
  this one skill artifact, using the existing deployment script
  (`task-8-deploy-review-manual-topics.ps1`) and reconciliation script as the mechanical basis, and
  promote it through that path for real (spec Section 6.1 requires at least one real artifact
  promoted before the stage is accepted).
- **In scope for Subphase 8.3:** formalize the ownership/support charter already informally recorded
  in Task 12 (Section 8 below), and exercise a real or staged incident/drill and a real or staged
  retirement per Stage 8.3.1/8.3.2.
- **Out of scope:** any additional skill, any additional runtime, any additional tenant, any
  cross-capability work, any records/retention work.

## 6. Known risks and limitations

Carried forward from real evidence, not invented:

1. **Related-topic-cap enforcement is instruction-governed only in this runtime, not
   code-enforced** — confirmed by live observation during Phase 6 (`AMB-01` run 1: 3 related topics
   consulted; run 2: 7 — both exceed the shared contract's cap of 2;
   `plugins/sharepoint-agents-and-skills/evaluations/common/native-sharepoint-results/RESULT-AMB-01.md`,
   `DRIFT-CHECK.md`). This is cited here as a known risk of the exact artifact being activated for
   promotion, not as importing Phase 6's own capability into this record's scope. **Not fixed** —
   a real, open remediation item that any Stage 8.1.1 promotion-path design must account for
   (e.g., as a documented known-limitation disclosure at each promotion stage, not silently
   dropped).
2. **4-identity permission matrix was `WAIVED`, not executed** (`PHASE-4-LICENSING-CONSTRAINT.md`)
   — Premium-licensing blocker; the pilot lead judged SharePoint's underlying security model
   sufficiently understood without a full matrix run. Any promotion beyond the current dev tenant
   should re-raise whether this waiver still holds for a test/production environment with different
   licensing.
3. **Negative and ambiguous evaluation categories were only partially executed at Phase 4 exit**
   (`TASK-12-ROLLBACK-EXERCISE-AND-EXIT-GATE.md` Part B: "Negative cases: Not formally tested";
   "Ambiguous cases: Partially tested"). Accepted as a Phase 4 exit-gate exception, not a Phase 8
   blocker, but a real gap a promotion path's own validation stage should not silently assume is
   closed.
4. **Architecturally questionable scope:** a skill named for reviewing manual topics also offers
   delete actions, gated only by SharePoint's own permission enforcement, not by the skill's own
   design (Task 12's own recorded recommendation for future enhancement, never actioned).

## 7. Operational dependencies

- SharePoint Online tenant `AG-CSB-INTRANET-DEV` and its PnP PowerShell access.
- `AgentAssets/Skills/` document library structure (skill discovery mechanism).
- The `CEIS-Pilot-Knowledge-Agent` Copilot agent, whose grounding/source configuration is a
  separate artifact from the skill itself (not covered by this record).
- The deployment/reconciliation/rollback PowerShell scripts under
  `tools/phase-4-native-sharepoint-skills/deployment/scripts/` — 4 real cmdlet-parameter bugs were
  found and fixed in these scripts during Phase 6's live execution
  (`.agent/map-debt.md`'s 2026-08-03 entries, commits `5e05893`, `0345b5f`); any promotion-path
  design should assume these scripts, not a hypothetical clean rewrite, are the actual mechanism.

## 8. Rollback or disable path

Already exercised and verified once (Phase 4 Task 12, Part A):

- **Manual removal:** delete the `AgentAssets/Skills/review-manual-topics` folder in SharePoint.
- **Verification:** confirm the folder is gone; confirm the skill is unavailable in Copilot chat.
- **Emergency disable:** identical to manual removal — delete the skill folder if a security issue
  is discovered.
- **Re-deployment:** re-run `task-8-deploy-review-manual-topics.ps1` against the verified hash.

`CONFIRMED` — this path has real execution evidence (`EVID-PHASE4-TASK12-ROLLBACK-COMPLETION.md`),
not just a documented plan.

## 9. Support owner

- **Richard Fremmerlid**, same as the accountable owner — no formal split between accountable
  owner and support owner exists yet for this single-pilot-lead capability. `PROVISIONAL`: if
  Stage 8.3.1's ownership/support charter later needs a distinct support role (e.g., for
  triage separate from accountability), that is a decision for whoever executes Stage 8.3.1, not
  invented here.

## 10. Records/legal trigger status

- **Not triggered.** No records/retention/audit requirement has been identified for this
  capability. This is consistent with Subphase 8.4 remaining out of scope (Section entry-gate
  note above) — Subphase 8.4 activates only when the Phase 3 retrospective surfaces a concrete
  need, and Phase 3 has not reached its own exit gate.

## 11. Cross-capability dependencies

- **None.** This is the only capability currently eligible for Phase 8 activation (Phase 3's
  library, Phase 5's agent, and Phase 6's multi-runtime model have not independently reached their
  own exit gates). Subphase 8.2's cross-capability monitoring/drift detection therefore has no
  second capability to span and remains out of scope until one exists.

## 12. What this record does not do

- Does not promote anything yet — Stage 8.1.1 (a real artifact promoted through a defined path) is
  separate follow-on work, informed by this record.
- Does not exercise Stage 8.3.1/8.3.2 (a real incident/drill; a real or staged retirement) — also
  separate follow-on work.
- Does not close, soften, or reinterpret any Phase 4, Phase 6, or Phase 7 finding cited above.
- Does not imply Phase 7's deferred live-validation work is complete or passed.
