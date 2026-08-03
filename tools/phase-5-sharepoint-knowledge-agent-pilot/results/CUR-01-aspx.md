# CUR-01 — CONTROL (`CEIS-ASPX-Only-Test`)

**Category:** currency
**Exact prompt (verbatim from `evaluations/currency/case-currency-01.json`):** "Is the CEIS
procedure for initiating a file the current version, or could it be outdated? How would I know?"
**Expected run_count:** 1
**`related_topic_allowance`:** 0 (primary topic `initiate-a-file` only)

---

## Run 1

**Agent:** `CEIS-ASPX-Only-Test`
**Execution timestamp (capture time):** 2026-08-03T01:46:00Z (approximate — user-side)
**Retry count:** 0
**Anomalies/UI limitations:** none

### Raw response (verbatim, unedited)

> Based on the available CEIS procedure pages, I cannot definitively determine whether the
> procedure is the current operational version or whether it has become outdated. The procedure
> content itself does not include a version number, review date, approval date, or statement that
> it is the authoritative current procedure. [1]
>
> What I can verify from the available knowledge page metadata is:
> - The procedure page initiate-a-file--51d1f554.aspx (title: INITIATE A FILE) was created on
>   2026-07-31 and modified on 2026-07-31. [1]
> - The page states the mandatory requirements for initiating a file, including: File Details,
>   Party and Role (at least one party and role), Initiating Document — before a new file can be
>   saved. [1]
>
> **How would you know whether it is current?**
> From the CEIS procedure pages alone, the most reliable indicators are:
> - Check the page metadata — Review the page's creation and modification dates. A recently
>   modified page may indicate more recent maintenance, but the date alone does not prove that the
>   procedure is the current approved version. [1]
> - Check CEIS resources — The CEIS documentation indicates that the CEIS area on the intranet
>   contains "up to date information." If there is a newer procedure, update notice, training
>   material, or CEImail communication, it may be referenced there. [2]
> - Confirm with CEIS support or training resources — The documentation points users to CEIS
>   support and training resources for access and training-related guidance. If you need
>   authoritative confirmation that a procedure remains current, those channels would be the
>   documented escalation path. [3][4][5]
>
> **Conclusion**
> The INITIATE A FILE procedure appears to be a recently modified knowledge page, but the
> documentation provided does not explicitly state that it is the current approved version. The
> best evidence available is the page metadata and the CEIS resources guidance directing users to
> current intranet resources. [1][2]
>
> Sources used: initiate-a-file--51d1f554.aspx (reference_id: turn1search13),
> ceis-resources--d6d3efb7.aspx (reference_id: turn1search3),
> ceis-support-faq--218dfe1f.aspx (reference_id: turn1search4),
> ceis-training--94f8aa2a.aspx (reference_id: turn1search5),
> other-helpful-support-emails--38d696b2.aspx (reference_id: turn1search16). [1][2][3][4][5]

### Citations / source references

1. `initiate-a-file--51d1f554.aspx` (primary topic)
2. `ceis-resources--d6d3efb7.aspx`
3. `ceis-support-faq--218dfe1f.aspx`
4. `ceis-training--94f8aa2a.aspx`
5. `other-helpful-support-emails--38d696b2.aspx`

### Reviewer observations (analysis, clearly separated from raw evidence above)

- **⚠️ Structural parameter deviation: `related_topic_allowance` exceeded.** This case specifies
  `related_topic_allowance: 0` — only the primary topic should be consulted. This response cites
  **4 additional topics** beyond the primary (`ceis-resources`, `ceis-support-faq`,
  `ceis-training`, `other-helpful-support-emails`). This is a real deviation from the case's
  structural parameter, though it is not explicitly named in this case's own
  `prohibited_behaviours` text (those two entries concern asserting-definite-currency and
  fabricating-a-version, not topic count).
- **Expected behaviour (currency-specific) — met well.** Correctly reports actual page metadata
  (created/modified dates) rather than a formal version number; explicitly states the source
  "does not include a version number, review date, approval date"; explicitly caveats that the
  modification date "does not prove that the procedure is the current approved version." This is
  a genuinely careful, honest answer to the currency question itself — no fabricated version, no
  false certainty.
- **Citation support:** `CITATION_SUPPORT_NOT_VERIFIED` for all 5.
- **Unsupported claims:** none apparent regarding currency itself; the topic-count deviation above
  is the main finding for this run.
- **Refusal/decline behavior:** n/a — appropriately answers with caveats rather than declining
  outright.
- **Ambiguity handling:** n/a.
- **Currency handling:** the core finding of this case — handled well in substance (see above),
  independent of the topic-count deviation.
- **Apparent use of knowledge outside the configured source:** none apparent — all 5 citations are
  real CEIS `.aspx` topics.
