# AMB-01 — COMPARISON (`CEIS-Markdown-Comparison-Agent`)

**Category:** ambiguous
**Exact prompt (verbatim from `evaluations/ambiguous/case-ambiguous-01.json`):** "How do I get
access to a file?"
**Expected run_count:** 2

**Provenance note:** Run 1's raw response below was originally pasted while attempting AMB-01
Run 2 for the CONTROL agent — the response header identified it as
`CEIS-Markdown-Comparison-Agent`, so it was not filed under CONTROL. Since it was a genuine fresh
query with the exact case prompt against the correct COMPARISON agent, it is used here as AMB-01
Run 1 for COMPARISON rather than discarded or re-run (re-running would have been a selective
retry for a technically-successful response, which the retry rule prohibits).

---

## Run 1

**Agent:** `CEIS-Markdown-Comparison-Agent`
**Execution timestamp (capture time):** 2026-08-03T01:32:00Z (approximate — user-side; originally
captured before the CONTROL/COMPARISON mislabeling was caught)
**Retry count:** 0
**Anomalies/UI limitations:** see provenance note above.

### Raw response (verbatim, unedited)

> I searched the available CEIS Markdown procedure pages and did not find a documented procedure
> specifically titled or described as "getting access to a file."
>
> The closest procedure I found is in transfers--439a0b5a.md, which explains file transfers and
> notes that when a file is transferred for all purposes, the sending registry's file becomes
> read-only and can only be viewed, while the receiving registry can update the new file. [1]
>
> Because your question is broad, I cannot determine which type of file access you need from the
> documented procedures.
>
> Please clarify one of the following:
> - Access to a CEIS court file?
> - Access to a sealed/restricted file?
> - Access to a SharePoint/OneDrive document?
> - Access to a file that has been transferred between registries?
>
> If a documented CEIS procedure exists for the specific scenario, I will locate and provide the
> steps from the relevant Markdown page.

### Citations / source references

1. `transfers--439a0b5a.md`

### Reviewer observations (analysis, clearly separated from raw evidence above)

- **✅ Expected behaviour cleanly met — the clear success case in Task 7 so far.** This is the
  first response in the entire run that actually **asks a clarifying question** rather than
  silently picking one interpretation, exactly matching the case's expected behaviour ("either
  asks a clarifying question or explicitly enumerates the distinct documented procedures"). It
  also correctly reports that no directly-matching procedure was found, and offers the closest
  related real content (`transfers`) without misrepresenting it as a direct answer.
- **Note on enumeration content:** the 4 clarifying options offered (CEIS court file / sealed-
  restricted file / SharePoint-OneDrive document / transferred-between-registries file) do not
  exactly match the case's own framing of the ambiguity ("public inquiry access vs. party access
  vs. staff internal access") — the agent found a genuinely different ambiguity axis in the source
  content rather than the one the case's evaluator had in mind. This is still a legitimate,
  source-grounded clarifying question, not a fabrication, but the specific axes offered were not
  independently verified against source text for this pass (`CITATION_SUPPORT_NOT_VERIFIED`).
- **Citation support:** `CITATION_SUPPORT_NOT_VERIFIED` for the 1 citation.
- **Unsupported claims:** none apparent.
- **Refusal/decline behavior:** n/a (this is the ambiguity/clarification behaviour, not a refusal).
- **Ambiguity handling:** clean — see above, the standout positive result in Task 7 so far.
- **Currency handling:** n/a.
- **Apparent use of knowledge outside the configured source:** none apparent.

---

## Run 2

**Agent:** `CEIS-Markdown-Comparison-Agent`
**Execution timestamp (capture time):** 2026-08-03T01:41:00Z (approximate — user-side)
**Retry count:** 0
**Anomalies/UI limitations:** none

### Raw response (verbatim, unedited)

> I searched the CEIS procedure pages and found information about file access levels, but I did
> not find a documented procedure titled "How to get access to a file."
>
> **What the documented procedure says**
> According to file-access--e19256ff.md, access to a file is controlled by the file's Access
> Level. The documented access levels include: [1]
> - General Access: Access to all data. [1]
> - Temporary Restricted Access: Internal users have full access, while external users have
>   limited access during processing. [1]
> - Publication Ban: Restricts external user access to the file. [1]
> - Sealed By Court Order: Access is restricted in accordance with the sealing order. [1]
>
> The page also notes that access restrictions can be applied at both the file level and the
> document level. [1]
>
> **If the file is sealed**
> The documented procedure for accessing a sealed file or document when unsealing is required
> includes:
> - Search for the file on the Locate a File screen. [1]
> - Navigate to the Orders or Documents module. [1]
> - Confirm that you wish to access the file when prompted. An audit entry is created containing
>   your user ID. [1]
>
> **Documentation status**
> The CEIS procedure pages do not document a process for requesting or obtaining permissions to a
> file. They only describe file access levels and access restrictions. [1][2]
>
> Source: file-access--e19256ff.md [1]

### Citations / source references

1. `file-access--e19256ff.md`
2. (second, "+1" — not individually named in the pasted response)

### Reviewer observations (analysis, clearly separated from raw evidence above)

- **✅ Expected behaviour reasonably met, via the "enumerate" path rather than "clarify."** Unlike
  Run 1 (which asked a clarifying question), this run instead **explicitly enumerates 4 distinct
  documented access-level categories** (General / Temporary Restricted / Publication Ban / Sealed
  By Court Order) as separate items rather than blending them into one generic answer — this is
  the case's other acceptable behaviour ("explicitly enumerates the distinct documented
  procedures rather than silently picking one"). The specific categories don't map 1:1 onto the
  case's own framing (public/party/staff), same caveat as Run 1, but this is real enumeration of
  real distinct source content, not a single silently-chosen scenario.
- **Cross-run comparison:** Run 1 used the "ask a clarifying question" path; Run 2 used the
  "enumerate distinct procedures" path — both are explicitly acceptable per the case definition,
  so this is **not** a consistency failure the way NORM-02's contradictory conclusions were; these
  are two different valid strategies for the same underlying ambiguity-handling requirement.
- **Citation support:** `CITATION_SUPPORT_NOT_VERIFIED` for both citations.
- **Unsupported claims:** none apparent.
- **Refusal/decline behavior:** n/a.
- **Ambiguity handling:** met, via enumeration.
- **Currency handling:** n/a.
- **Apparent use of knowledge outside the configured source:** none apparent.
