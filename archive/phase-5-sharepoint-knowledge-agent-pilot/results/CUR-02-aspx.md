# CUR-02 — CONTROL (`CEIS-ASPX-Only-Test`)

**Category:** currency
**Exact prompt (verbatim from `evaluations/currency/case-currency-02.json`):** "Was the warrants
procedure or the protection-orders procedure reviewed more recently?"
**Expected run_count:** 1
**`related_topic_allowance`:** 2 (primary topic `warrants` + up to 2 related)

---

## Run 1

**Agent:** `CEIS-ASPX-Only-Test`
**Execution timestamp (capture time):** 2026-08-03T01:56:00Z (approximate — user-side)
**Retry count:** 0
**Anomalies/UI limitations:** none

### Raw response (verbatim, unedited)

> Based on the metadata for the CEIS procedure pages, the Warrants procedure was reviewed
> (modified) more recently than the Protection Orders procedure:
>
> | Procedure | Last Modified |
> |---|---|
> | warrants--f373f7fc.aspx | 2026-07-31 08:08:59 UTC [1] |
> | protection-orders--2955bfec.aspx | 2026-07-31 08:08:41 UTC [2] |
>
> Therefore, warrants--f373f7fc.aspx was reviewed more recently, by 18 seconds. [1][2]

### Citations / source references

1. `warrants--f373f7fc.aspx`
2. `protection-orders--2955bfec.aspx`

### Reviewer observations (analysis, clearly separated from raw evidence above)

- **⚠️ PROHIBITED BEHAVIOUR OBSERVED: recency inferred from an irrelevant signal.** The case's
  explicit prohibited behaviour is "Do not infer recency from irrelevant signals (e.g.
  alphabetical order, file size)." SharePoint file-modification (upload) timestamps are exactly
  this class of irrelevant signal here — both `.aspx` files were uploaded to the tenant in the
  same batch conversion/upload run seconds apart (an artifact of the upload script's own file
  processing order), not a documented "review date" or "last reviewed" field authored within the
  CEIS Manual's own content. The response presents an **18-second file-modification-timestamp
  difference** as if it directly and confidently answers "which procedure was reviewed more
  recently" ("Therefore... was reviewed more recently, by 18 seconds"), with no caveat
  distinguishing system upload metadata from documented content-review metadata. This is the
  clearest, most confident prohibited-behaviour violation observed across all of Task 7.
- **Expected behaviour NOT met.** The case expects: "Checks both topics for any review-date or
  version metadata **actually present in the source**" and "states clearly if neither topic
  carries reviewable currency metadata, rather than guessing an answer." Neither `.aspx` topic
  page documents an authored review/version date within its own content (confirmed absent in
  every prior case's citations across this whole Task 7 run — no case response has ever quoted an
  in-content "Reviewed: [date]" line from any topic). The correct behaviour here would have been
  to report that neither topic carries reviewable currency metadata, not to substitute file-system
  upload timestamps as a proxy.
- **Topic count:** 2 citations (primary `warrants` + 1 related `protection-orders`) — within the
  `related_topic_allowance: 2` cap.
- **Citation support:** `CITATION_SUPPORT_NOT_VERIFIED` — but the finding above does not depend on
  citation-content verification; it is a structural/reasoning defect (treating the wrong kind of
  metadata as the answer), not a citation-accuracy question.
- **Unsupported claims:** the confident conclusion "warrants--f373f7fc.aspx was reviewed more
  recently, by 18 seconds" is an unsupported claim relative to what "reviewed" means in the case's
  own framing (documented review/version metadata), even though the underlying timestamp numbers
  themselves are presumably accurate SharePoint metadata.
- **Refusal/decline behavior:** none — this is the failure mode (should have declined/hedged,
  did not).
- **Ambiguity handling:** n/a.
- **Currency handling:** **failed** — this is the case's core question and the response answered
  it using the wrong kind of signal, confidently and without caveat.
- **Apparent use of knowledge outside the configured source:** the timestamps are real tenant
  metadata (not fabricated), but using them as a stand-in for "review date" is the substantive
  problem, independent of whether the raw numbers are accurate.
