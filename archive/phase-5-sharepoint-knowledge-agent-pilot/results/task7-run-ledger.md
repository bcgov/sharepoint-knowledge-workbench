# Task 7 Run Ledger

Tracks execution state per case/agent/run. Updated as each response is captured. Order: cases run
in file order (NORM-01, NORM-02, NEG-01, NEG-02, AMB-01, CUR-01, CUR-02); for each case, CONTROL
run(s) first, then COMPARISON run(s), same order both agents. `run_count` per case is taken from
its evaluation JSON — NORM-01/NORM-02/AMB-01 require 2 runs each, the rest require 1.

**CONTROL** = `CEIS-ASPX-Only-Test` (direct `.agent`-file access). **COMPARISON** =
`CEIS-Markdown-Comparison-Agent` (direct `.agent`-file access). Neither agent's instructions or
source binding may be modified during this run — none were.

| Case | run_count | CONTROL runs | COMPARISON runs | Status |
|---|---|---|---|---|
| NORM-01 | 2 | 2/2 | 2/2 | both executed, evidence captured; citation checks pending |
| NORM-02 | 2 | 2/2 | 2/2 | both executed — **anomaly on both agents**: each agent's Run 2 exceeded the 2-related-topic allowance (CONTROL: 3, COMPARISON: 4) and reached a conclusion inconsistent with its own Run 1; the two agents' Run 2 conclusions also disagree with each other (see NORM-02-aspx.md / NORM-02-md.md) |
| NEG-01 | 1 | 1/1 | 1/1 | both executed, both clean declines, evidence captured |
| NEG-02 | 1 | 1/1 | 1/1 | both executed — near-identical good results on both agents (see NEG-02-aspx.md / NEG-02-md.md) |
| AMB-01 | 2 | 2/2 | 2/2 | CONTROL both runs: partial ambiguity-handling only (no question, no clean enumeration). COMPARISON both runs: fully met, via 2 different valid strategies (clarify vs. enumerate). Notable format-level difference favoring COMPARISON on this case. |
| CUR-01 | 1 | 1/1 | 1/1 | both executed — CONTROL: good currency caveats but exceeded topic allowance (5 vs. 1 max); COMPARISON: respected topic allowance but weaker currency caveat, leans toward inferring "current" from edit timestamp |
| CUR-02 | 1 | 1/1 | 1/1 | both executed — **identical prohibited-behaviour violation on both agents**: each inferred "reviewed more recently" from an upload-timestamp gap (18s ASPX / 6s MD), a shared format-independent failure, the clearest cross-agent finding in Task 7 |

**Legend:** pending → executed → citation checked → complete. Technical retries (UI/agent failure
only, never quality-based) logged inline per case when they occur, with the original failure
preserved.

## Summary (all 7 cases, both agents, complete)

- **Total runs:** 20 (CONTROL: 10, COMPARISON: 10 — NORM-01×2, NORM-02×2, NEG-01×1, NEG-02×1,
  AMB-01×2, CUR-01×1, CUR-02×1, per agent).
- **Citation verification:** every citation across all 20 runs recorded as
  `CITATION_SUPPORT_NOT_VERIFIED` — no cited source was opened/checked against the response text
  during this pass. This is a recorded limitation, not a silent gap.
- **Agent configuration:** neither `CEIS-ASPX-Only-Test` nor `CEIS-Markdown-Comparison-Agent` was
  modified at any point during Task 7 — no script or tenant-write action was run by the controller
  during this task; all 20 responses came from live, unmodified agent queries.
- **Retries:** 0 technical retries. One evidence-provenance issue occurred (AMB-01: a response
  originally intended as CONTROL Run 2 was correctly identified as COMPARISON Run 1 based on its
  own response header, and filed accordingly rather than discarded or treated as a quality-based
  retry) — documented in `AMB-01-md.md`'s provenance note, not hidden.
- **Cross-case findings (full detail in each case's own file):**
  - `NORM-02`: both agents' second run exceeded the related-topic-allowance and reached a
    conclusion inconsistent with their own first run; the two agents' confident answers also
    contradicted each other.
  - `AMB-01`: COMPARISON met the ambiguity-handling requirement cleanly on both runs (via two
    different valid strategies); CONTROL only partially met it on both runs.
  - `CUR-01`: CONTROL exceeded the related-topic-allowance (0 allowed, 4 used) but gave careful
    currency caveats; COMPARISON respected the allowance but was more assertive about "current"
    than the source supports.
  - `CUR-02`: **both agents** committed the identical prohibited-behaviour violation — inferring
    "reviewed more recently" from an irrelevant file-upload-timestamp gap, not documented review
    metadata. The clearest shared, format-independent finding in the run.

## Log

(entries appended as each run completes — see per-case files for full raw evidence and reviewer
observations; this ledger tracks status only)
