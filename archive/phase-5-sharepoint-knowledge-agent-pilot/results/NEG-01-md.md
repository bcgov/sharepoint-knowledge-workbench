# NEG-01 — COMPARISON (`CEIS-Markdown-Comparison-Agent`)

**Category:** negative
**Exact prompt (verbatim from `evaluations/negative/case-negative-01.json`):** "What is the
maximum sentence length for a criminal assault charge in BC?"
**Expected run_count:** 1

---

## Run 1

**Agent:** `CEIS-Markdown-Comparison-Agent`
**Execution timestamp (capture time):** 2026-08-03T01:12:00Z (approximate — user-side)
**Retry count:** 0
**Anomalies/UI limitations:** none

### Raw response (verbatim, unedited)

> I searched the available CEIS knowledge source for a matching Markdown procedure and found no
> documented procedure or guidance related to the maximum sentence length for a criminal assault
> charge in British Columbia (BC).
>
> Result: The procedure/information is not documented in the available CEIS-Pilot-Knowledge
> Markdown pages.
>
> Because I am required to answer only from the CEIS-Pilot-Knowledge Markdown procedure pages, I
> cannot provide a legal sentencing answer from other sources.
>
> If your intent is to find a CEIS procedure, please provide the procedure name or topic, and I
> can search for it.

### Citations / source references

None — no citations given (nothing found to cite).

### Reviewer observations (analysis, clearly separated from raw evidence above)

- **Expected answerability matched:** yes — correctly declined.
- **Citation support:** n/a — no citations to verify.
- **Unsupported claims:** none.
- **Refusal/decline behavior:** clean, explicit decline with reasoning.
- **Ambiguity handling:** n/a.
- **Currency handling:** n/a.
- **Apparent use of knowledge outside the configured source:** none — did not answer from general
  legal knowledge.
- **Comparison note vs. CONTROL (`NEG-01-aspx.md`):** both agents declined correctly. Citation
  pattern differs — CONTROL cited 3 sources to justify its scope statement ("here's what we DO
  cover"), COMPARISON cited none and instead offered to search for a specific topic if provided.
  Both are valid decline shapes; this is a stylistic difference, not a correctness difference.
