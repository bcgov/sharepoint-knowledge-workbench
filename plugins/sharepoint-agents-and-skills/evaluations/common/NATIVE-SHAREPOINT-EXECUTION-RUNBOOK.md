# Native-SharePoint Live Execution Runbook

Prepared at Phase 6 remediation (round 2, 2026-08-03), per the human review's Item 3/4. **Not
executed** — requires live tenant/PnP/Copilot access this environment does not have (Item 4: stop
immediately before the live tenant run). This runbook is preparation only.

## Scope: exactly 7 cases, unchanged

The 7 `native-sharepoint`-only cases in this directory (verified programmatically, not by eye —
every other case in this directory is `["native-sharepoint", "repository-claude"]`):

1. `case-ambiguous-01.json` (AMB-01)
2. `case-permission-01-owner.json` (PERM-01)
3. `case-permission-02-intended.json` (PERM-02)
4. `case-permission-03-restricted.json` (PERM-03)
5. `case-permission-04-noaccess.json` (PERM-04)
6. `case-permission-05-related-restricted.json` (PERM-05)
7. `case-permission-06-primary-restricted.json` (PERM-06)

**No prompts, `expected_semantic_behaviours`, or `prohibited_behaviours` in any of these 7 files
were changed to prepare this runbook** — verify with `git diff` against this remediation round's
commit before running; if any of the 7 differ from what's referenced here, stop and reconcile
first rather than running against a silently-drifted case.

## Preconditions before running

1. Live PnP/SharePoint connection to `AG-CSB-INTRANET-DEV` (the sole authorized sandbox — see
   `docs/research/research-experimentation/PHASE-4-SHAREPOINT-AGENTS-CRITICAL-LEARNINGS.md`).
2. The deployed `review-manual-topics` native skill confirmed present at `AgentAssets/Skills/
   review-manual-topics/SKILL.md` on that tenant (hash-verify against the version in this repo's
   `plugins/sharepoint-agents-and-skills/skills/review-manual-topics/SKILL.md` before running —
   if they differ, the live results won't correspond to this repo's current contract).
3. A Copilot agent (or the ready-made SharePoint chat surface) with the skill enabled and access
   to `CEISPilotKnowledgePages/`.
4. Test identities available matching each case's `test_identity_class` (`OWNER_EDITOR`,
   `INTENDED_READER`, `RESTRICTED_READER`, `NO_SOURCE_ACCESS`) — PERM-01 through PERM-06 each
   require a different one; running all 6 under one identity does not test what the cases claim
   to test.

## Per-case execution steps (identical for all 7)

1. Read the case's exact `prompt` field — paste it verbatim into the Copilot chat under the
   case's `test_identity_class` identity. Do not paraphrase or "improve" the prompt.
2. Run it `run_count` times (matches the case's own field — some cases specify 1, others 2) to
   check response stability, per this suite's existing convention (Phase 4's original cases
   already used `run_count` for this purpose).
3. **Preserve the raw response verbatim** — copy/paste the full agent output into a results file,
   not a paraphrase or summary. Grading must be done against what the agent actually said, not a
   memory of it.
4. Grade the raw response against the case's own `expected_semantic_behaviours` and
   `prohibited_behaviours` lists — mark each list item met/not-met individually, not a single
   pass/fail verdict with no breakdown.
5. Record: case ID, identity used, timestamp, raw response, per-item grading, overall PASS/FAIL,
   any anomaly.

## Where results go

Create `plugins/sharepoint-agents-and-skills/evaluations/common/native-sharepoint-results/`
(does not exist yet — created by whoever runs this) with one file per case
(`RESULT-<case_id>.md` or `.json`, either is fine, but must include the 5 fields in step 5 above
for every run). Do not overwrite this runbook or the case files themselves with results.

## After execution

Update `docs/superpowers/plans/phase-6-tasks-1-12-evidence/task-6-baseline-evaluation-findings.md`
and `task-11-exit-evidence-and-review.md` with the real results and re-assess the Phase 6
evaluation exit criterion — this runbook's existence does not itself close that criterion; the
actual graded results do.
