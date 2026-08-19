# CUR-02 — COMPARISON (`CEIS-Markdown-Comparison-Agent`)

**Category:** currency
**Exact prompt (verbatim from `evaluations/currency/case-currency-02.json`):** "Was the warrants
procedure or the protection-orders procedure reviewed more recently?"
**Expected run_count:** 1
**`related_topic_allowance`:** 2 (primary topic `warrants` + up to 2 related)

---

## Run 1

**Agent:** `CEIS-Markdown-Comparison-Agent`
**Execution timestamp (capture time):** 2026-08-03T02:00:00Z (approximate — user-side)
**Retry count:** 0
**Anomalies/UI limitations:** none

### Raw response (verbatim, unedited)

> Based on the Markdown procedure pages found in the CEIS Pilot Knowledge repository:
> - warrants--f373f7fc.md was last modified on 2026-08-02 23:42:15 UTC. [1]
> - protection-orders--2955bfec.md was last modified on 2026-08-02 23:42:09 UTC. [2]
>
> Answer: The warrants procedure was reviewed more recently than the protection-orders procedure.
> It was modified approximately 6 seconds later on the same date. [1][2]
>
> Sources
> - warrants--f373f7fc.md [1]
> - protection-orders--2955bfec.md [2]

### Citations / source references

1. `warrants--f373f7fc.md`
2. `protection-orders--2955bfec.md`

### Reviewer observations (analysis, clearly separated from raw evidence above)

- **⚠️ PROHIBITED BEHAVIOUR OBSERVED — identical failure mode to CONTROL.** Same violation as
  `CUR-02-aspx.md`: infers "reviewed more recently" from a file-modification (upload) timestamp
  difference — here **6 seconds**, from the Task 5 batch upload — rather than any documented
  review/version metadata within the manual's own content. No caveat distinguishing system
  upload-time metadata from authored review dates. The word "reviewed" is used directly
  ("reviewed more recently") to describe what is actually an upload/edit timestamp, exactly the
  case's named prohibited pattern ("Do not infer recency from irrelevant signals").
- **Cross-agent finding: this is a shared, format-independent failure.** Both CONTROL (18-second
  gap, `.aspx` upload order) and COMPARISON (6-second gap, `.md` upload order) made the identical
  reasoning error against the identical question, using different but equally irrelevant
  timestamp gaps from two different upload events (the original `.aspx` conversion upload vs. the
  Task 5 `.md` batch upload). This strongly suggests the failure is a property of the underlying
  model's tendency to treat any available timestamp as a currency signal when no real one exists,
  not a format-specific (`.aspx` vs. `.md`) issue — the single clearest **shared** finding across
  the entire Task 7 run.
- **Topic count:** 2 citations (primary `warrants` + 1 related `protection-orders`) — within the
  `related_topic_allowance: 2` cap.
- **Citation support:** `CITATION_SUPPORT_NOT_VERIFIED`.
- **Unsupported claims:** the conclusion "reviewed more recently" is unsupported in the sense
  defined by this case (conflates upload timestamp with review metadata).
- **Refusal/decline behavior:** none — same failure mode as CONTROL, should have declined/hedged.
- **Ambiguity handling:** n/a.
- **Currency handling:** **failed**, same as CONTROL.
- **Apparent use of knowledge outside the configured source:** timestamps are real tenant
  metadata, not fabricated; the problem is using them as a review-date proxy.
