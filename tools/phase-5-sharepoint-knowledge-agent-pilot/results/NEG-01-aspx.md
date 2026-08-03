# NEG-01 — CONTROL (`CEIS-ASPX-Only-Test`)

**Category:** negative
**Exact prompt (verbatim from `evaluations/negative/case-negative-01.json`):** "What is the
maximum sentence length for a criminal assault charge in BC?"
**Expected run_count:** 1

---

## Run 1

**Agent:** `CEIS-ASPX-Only-Test`
**Execution timestamp (capture time):** 2026-08-03T01:08:00Z (approximate — user-side)
**Retry count:** 0
**Anomalies/UI limitations:** none

### Raw response (verbatim, unedited)

> I searched the available CEIS procedure pages for information related to criminal assault
> charges, sentencing, or maximum sentence length, and I did not find any documented procedure or
> reference covering criminal sentencing.
>
> Result: The maximum sentence length for a criminal assault charge is not documented in the
> available CEIS Pilot Knowledge Pages (.aspx files).
>
> The available CEIS pages focus on civil court procedures and CEIS system operations, such as
> file initiation, data entry, appearances, orders, warrants, reports, transfers, access levels,
> and related court services procedures. They do not contain criminal law sentencing information.
> [1][2][3]
>
> Because this information is not present in the CEIS procedure documentation, I cannot provide a
> CEIS-grounded answer to the sentencing question.

### Citations / source references

1. `warrants--f373f7fc.aspx`
2. `initiate-a-file--51d1f554.aspx`
3. (third, "+1" — not individually named in the pasted response)

### Reviewer observations (analysis, clearly separated from raw evidence above)

- **Expected answerability matched:** yes — correctly declined.
- **Citation support:** `CITATION_SUPPORT_NOT_VERIFIED`. Note the citation *role* here is unusual:
  the 3 sources are cited as evidence of what the available pages **do** cover (to justify the
  scope statement), not as support for a specific factual claim — a legitimate but different
  citation pattern than the other cases.
- **Unsupported claims:** none — no sentencing information fabricated, matches "do not fabricate a
  sentencing answer" and "do not imply the CEIS Manual covers criminal sentencing."
- **Refusal/decline behavior:** clean, explicit decline with reasoning.
- **Ambiguity handling:** n/a.
- **Currency handling:** n/a.
- **Apparent use of knowledge outside the configured source:** none — did not answer from general
  legal knowledge, matching the expected behaviour exactly.
