# NEG-02 — COMPARISON (`CEIS-Markdown-Comparison-Agent`)

**Category:** negative
**Exact prompt (verbatim from `evaluations/negative/case-negative-02.json`):** "What is the CEIS
procedure for filing an appeal after a court decision?"
**Expected run_count:** 1

---

## Run 1

**Agent:** `CEIS-Markdown-Comparison-Agent`
**Execution timestamp (capture time):** 2026-08-03T01:20:00Z (approximate — user-side)
**Retry count:** 0
**Anomalies/UI limitations:** none

### Raw response (verbatim, unedited)

> Based on the CEIS procedure documented in transfers--439a0b5a.md, the process for a file
> transfer related to an appeal is as follows:
>
> **Transfer for an Appeal**
> When a file is transferred from Provincial Court to Supreme Court for an appeal:
> - The Provincial Court file remains open for data entry in CEIS because subsequent hearings may
>   still occur in Provincial Court. [1]
> - Data from the Provincial Court file must not be transferred directly into a new Supreme Court
>   file. [1]
> - An appeal is initiated by filing a Notice of Appeal. [1]
> - The Supreme Court must first create a new file and assign a Supreme Court file number based on
>   the Notice of Appeal. [1]
> - The Provincial Court then electronically transfers the file. [1]
> - The Supreme Court accepts the transfer into the existing Supreme Court file number that was
>   already created from the Notice of Appeal. [1]
>
> **Limitation of the Documentation**
> The procedure page describes how CEIS handles the transfer of a file for an appeal, but it does
> not document the procedural steps for filing an appeal itself (such as forms, deadlines, service
> requirements, or court filing requirements). It only explains the CEIS file-transfer process
> once an appeal has been initiated. [1]
>
> Source: transfers--439a0b5a.md (section "Transfer for an Appeal") [1]

### Citations / source references

1. `transfers--439a0b5a.md`

### Reviewer observations (analysis, clearly separated from raw evidence above)

- **Expected answerability matched:** yes — same well-executed optional-behaviour pattern as
  CONTROL: correctly redirects to the real related `transfers` topic, clearly flags it as not a
  direct match for the appeal-filing procedure itself.
- **Citation support:** `CITATION_SUPPORT_NOT_VERIFIED`.
- **Unsupported claims:** none apparent.
- **Refusal/decline behavior:** partial, matching CONTROL's pattern.
- **Ambiguity handling:** n/a.
- **Currency handling:** n/a.
- **Apparent use of knowledge outside the configured source:** none apparent.
- **Comparison note vs. CONTROL (`NEG-02-aspx.md`):** near-identical content and structure —
  same 6-point transfer procedure, same explicit limitation statement, single citation to the
  `.md` counterpart of the same topic. This is the closest match between the two agents observed
  so far in Task 7.
