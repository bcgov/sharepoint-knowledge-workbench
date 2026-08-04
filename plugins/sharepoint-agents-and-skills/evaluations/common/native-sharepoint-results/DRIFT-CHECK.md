# Cross-Runtime Drift Check — Final Pass (2026-08-04)

Runs `drift_detection.detect_drift()` (Task 8) against real structural results from both runtimes,
for every case with a real, executed result this session.

## Method

For each case, built a `CaseResult` (resolved/related_count) from the actual observed
behavior — `repository-claude` via real `resolve_topic()` execution, `native-sharepoint` via the
related-topic counts explicitly stated in the live agent's raw responses (see
`RESULT-*.md`) — and ran it through the same `detect_drift()` function used throughout this
session's `repository-claude` testing, applying it cross-runtime for the first time.

## Results

| Case | Runtime | related_count | allowance | Drift |
|---|---|---|---|---|
| AMB-01 run 1 | native-sharepoint | 3 | 2 | **`related_topic_cap_exceeded`** |
| AMB-01 run 2 | native-sharepoint | 7 | 2 | **`related_topic_cap_exceeded`** |
| PERM-01 | native-sharepoint | 0 | 2 | none |
| PERM-02 | native-sharepoint | 0 | 2 | none |
| NORM-01 | repository-claude | 0 | 2 | none |
| NEG-01 | repository-claude | n/a (correctly not found) | n/a | none |
| SAFE-01 | repository-claude | 0 | 2 | none |
| SAFE-02 | repository-claude | 0 | 2 | none |
| BOUND-01 | repository-claude | n/a (correctly hard-rejected per contract) | 2 | none |

## Finding: real cap violation on the native runtime, not a false positive

`AMB-01`'s live responses explicitly named related pages consulted "as evidence": run 1 named 3
("INITIATE A FILE, FILE DETAILS, and DOCUMENTS/DATA ENTRY"), run 2 explicitly listed 7 under
"Related pages reviewed" (`FILE ACCESS`, `INITIATE A FILE`, `FILE DETAILS`, `DOCUMENTS/DATA
ENTRY`, `DOCUMENT PRODUCTION`, `APPEARANCES`, `PARTIES`). Both exceed the case's own
`related_topic_allowance: 2` and `SKILL.md`'s stated "up to 2 (max 2)" boundary.

This is exactly the risk Task 3 (`task-3-shared-capability-specification.md`) and Task 4
(`task-4-adversarial-intent-preservation-review.md`, Finding 1) flagged as a **theoretical**
asymmetry earlier this session: the related-topic cap is code-enforced on `repository-claude`
(`TooManyRelatedTopicsError`, proven again here — `BOUND-01` correctly hard-rejects) but only
*behavioral* (instruction-adherence) on `native-sharepoint`. This live run is empirical proof that
theoretical asymmetry is a real, live gap, not a hypothetical one — the native agent did not
reliably honor the stated cap when a topic had many surrounding pages to draw from.

**This is a genuine cross-runtime drift finding that belongs in the final disposition, not a
tooling bug.** `detect_drift()` performed exactly as designed (Task 8's own "add deliberate drift
and prove detection" requirement is now additionally validated against a *real*, not just
synthetically-introduced, drift instance).

## Not re-litigated here

`BOUND-01`'s hard-reject-per-contract behavior on `repository-claude` (resolved this session's
earlier remediation round from the approved `SKILL.md` contract) is unchanged and still correct —
included above for completeness, not as a new finding.
