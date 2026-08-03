# NEG-02 — CONTROL (`CEIS-ASPX-Only-Test`)

**Category:** negative
**Exact prompt (verbatim from `evaluations/negative/case-negative-02.json`):** "What is the CEIS
procedure for filing an appeal after a court decision?"
**Expected run_count:** 1

---

## Run 1

**Agent:** `CEIS-ASPX-Only-Test`
**Execution timestamp (capture time):** 2026-08-03T01:16:00Z (approximate — user-side)
**Retry count:** 0
**Anomalies/UI limitations:** none

### Raw response (verbatim, unedited)

> Based on the CEIS knowledge pages, there is no documented procedure titled "filing an appeal
> after a court decision." However, there is a documented CEIS process for a transfer for an
> appeal from Provincial Court to Supreme Court. [1]
>
> **CEIS Procedure: Transfer for an Appeal**
> When a file is transferred from Provincial Court to Supreme Court for an appeal:
> - The Provincial Court file remains open for data entry in CEIS, because subsequent hearings may
>   still be ongoing. [1]
> - Information from the Provincial Court file should not be transferred directly into a new
>   Supreme Court file. [1]
> - The appeal is initiated by filing a Notice of Appeal. [1]
> - The Supreme Court must first initiate a new file based on that Notice of Appeal. [1]
> - The Provincial Court then electronically transfers the file. [1]
> - The Supreme Court accepts the transfer into the existing Supreme Court file number that was
>   assigned when the Notice of Appeal was filed. [1]
>
> **Limitation**
> The available CEIS procedure pages do not provide additional step-by-step instructions for
> preparing, submitting, or processing a Notice of Appeal itself. The documentation only describes
> the CEIS transfer handling once an appeal file is being established between courts. [1]
>
> Source: transfers--439a0b5a.aspx (TRANSFERS) [1]

### Citations / source references

1. `transfers--439a0b5a.aspx`

### Reviewer observations (analysis, clearly separated from raw evidence above)

- **Expected answerability matched:** yes, and this is a well-executed instance of the case's
  *optional* allowed behaviour: "optionally suggests the closest related real topic if one exists,
  clearly labeled as not a direct match." It explicitly states no "filing an appeal" procedure
  exists, names the real related topic (`transfers`), and explicitly flags the limitation ("do not
  provide additional step-by-step instructions for preparing, submitting, or processing a Notice
  of Appeal itself").
- **Citation support:** `CITATION_SUPPORT_NOT_VERIFIED`.
- **Unsupported claims:** none apparent — no invented appeal-filing procedure; the described
  "transfer for an appeal" content is presented as a distinct, real, related procedure, not
  substituted as if it directly answers the appeal-filing question.
- **Refusal/decline behavior:** partial — declines the specific "filing an appeal" question while
  correctly redirecting to real related content, matching the case's stated optional-good
  behaviour rather than a full flat refusal.
- **Ambiguity handling:** n/a.
- **Currency handling:** n/a.
- **Apparent use of knowledge outside the configured source:** none apparent.
