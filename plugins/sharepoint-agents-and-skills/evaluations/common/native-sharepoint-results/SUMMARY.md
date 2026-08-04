# Native-SharePoint Live Execution Summary

Executed 2026-08-04 against the real `AG-CSB-INTRANET-DEV` tenant, live agent
`CEIS-Pilot-Knowledge-Agent`, per `NATIVE-SHAREPOINT-EXECUTION-RUNBOOK.md` — prompts and
expectations unchanged throughout.

## Precondition: skill deployment reconciled first

Before any case ran, `reconcile-deployed-skill.ps1` found the deployed `review-manual-topics`
skill was **stale** (`DISPOSITION: DEPLOYED_ARTIFACT_DRIFT_DETECTED`) relative to this repo's
current `SKILL.md`. Redeployed via `deploy-and-verify-skill.ps1 -Execute`; byte-for-byte
readback confirmed match; re-ran reconciliation and confirmed
`DISPOSITION: TASK_8_ARTIFACT_ALREADY_PRESENT_AND_RECONCILED` before proceeding. (This also
surfaced and fixed 4 real cmdlet-parameter bugs across both scripts — see `.agent/map-debt.md`'s
2026-08-03 entries and commits `5e05893`, `0345b5f`.)

## Results

| Case | Identity | Status | Disposition |
|---|---|---|---|
| AMB-01 | INTENDED_READER | Executed (2/2 runs) | **PASS** |
| PERM-01 | OWNER_EDITOR | Executed (1/1 run) | **PASS** |
| PERM-02 | INTENDED_READER | Executed (1/1 run) | **PASS** |
| PERM-03 | RESTRICTED_READER | **SKIPPED_BY_HUMAN_DECISION** | Not run |
| PERM-04 | NO_SOURCE_ACCESS | **SKIPPED_BY_HUMAN_DECISION** | Not run |
| PERM-05 | INTENDED_READER | **SKIPPED_BY_HUMAN_DECISION** | Not run |
| PERM-06 | RESTRICTED_READER | **SKIPPED_BY_HUMAN_DECISION** | Not run |

**3 of 7 executed, all PASS. 4 of 7 explicitly skipped by the human partner's own decision**
(stated reason: already knows how SharePoint permission behavior works; nothing new to learn from
running them) — not a technical failure, not an agent/tooling limitation, and not a retry
situation. Recorded honestly as skipped, not folded into a false 7/7 executed claim.

## No prompts, identities, or expectations were changed during this run

Every prompt sent was copied verbatim from its case file. No case file, `SKILL.md`, or agent
configuration was modified between or during runs.

## Detailed per-case results

See `RESULT-AMB-01.md`, `RESULT-PERM-01.md`, `RESULT-PERM-02.md` in this directory for full raw
responses and grading.
