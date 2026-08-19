# NORM-02 — CONTROL (`CEIS-ASPX-Only-Test`)

**Category:** normal
**Exact prompt (verbatim from `evaluations/normal/case-normal-02.json`):** "How does a warrant
relate to a protection order in CEIS — do they use the same file record?"
**Expected run_count:** 2

---

## Run 1

**Agent:** `CEIS-ASPX-Only-Test`
**Execution timestamp (capture time):** 2026-08-03T00:40:00Z (approximate — user-side)
**Retry count:** 0
**Anomalies/UI limitations:** none

### Raw response (verbatim, unedited)

> Based on the available CEIS procedure pages, I could not find documentation stating that a
> warrant and a protection order share the same CEIS file record.
>
> **What the documented procedures do say:**
> - A protection order is described as a family law civil order made in family court that
>   contains conditions to provide safety and security to a specified person and restrict a
>   party's activities to prevent harassment, harm, or communication. [1]
> - A warrant is described as an order by an Adjudicator to arrest an individual, for example for
>   failure to appear at a court appearance after receiving a summons. The procedure emphasizes
>   adding and cancelling warrants in a timely manner. [2]
>
> The available procedure content identifies them as different types of records/orders, but does
> not document whether they use the same underlying CEIS file record, whether one can exist on the
> same file as the other, or how they are linked within CEIS. Therefore, I cannot confirm that
> relationship from the documented procedures alone. [1][2]
>
> Sources
> - protection-orders--2955bfec.aspx (reference_id: turn1search18) [1]
> - warrants--f373f7fc.aspx (reference_id: turn1search25) [2]

### Citations / source references

1. `protection-orders--2955bfec.aspx`
2. `warrants--f373f7fc.aspx`

### Reviewer observations (analysis, clearly separated from raw evidence above)

- **Expected answerability matched:** yes — consulted exactly the 2 expected topics (warrants,
  protection-orders), within the `related_topic_allowance: 2` limit.
- **Citation support:** `CITATION_SUPPORT_NOT_VERIFIED` for both.
- **Unsupported claims:** none — explicitly declines to assert a relationship the source doesn't
  document, matching the expected behaviour "states explicitly if the source content does not
  directly answer the relationship."
- **Refusal/decline behavior:** partial decline (answers what each topic individually says, but
  correctly declines to assert the specific cross-topic relationship asked about) — appropriate
  for this case, not a full refusal.
- **Ambiguity handling:** n/a.
- **Currency handling:** n/a.
- **Apparent use of knowledge outside the configured source:** none apparent.

---

## Run 2

**Agent:** `CEIS-ASPX-Only-Test`
**Execution timestamp (capture time):** 2026-08-03T00:48:00Z (approximate — user-side)
**Retry count:** 0
**Anomalies/UI limitations:** none

### Raw response (verbatim, unedited)

> Based on the CEIS procedure pages, warrants and protection orders are related to the same court
> file, but they are recorded and managed in different parts of CEIS. They are not described as
> separate file records. Instead, both become information associated with the file and its
> parties. [1][2]
>
> **What the procedures say**
>
> **Protection Orders**
> - The CEIS Orders procedure states that "Protection Orders are ALWAYS stand alone orders." This
>   refers to how they are entered and tracked within the Orders module. [2]
> - When entering an order, the Protection Order checkbox is used to identify and process it
>   appropriately, including Protection Order Registry tracking. [2]
>
> **Warrants**
> - Warrants are entered through the Record Results module under the Warrants tab, against the
>   relevant appearance. [1]
> - After entry, the warrant status appears on the party/file record. The procedure states that
>   the warrant will appear on the Parties screen and that a warrant flag is shown on the file. [1]
>
> **Evidence they share the same file context**
> - The Party Summary screen can display whether parties have warrants, protection orders, or
>   firearms orders associated with them on the file. [3]
> - The Orders procedure states that all known orders for a civil file must be entered in CEIS,
>   including protection orders. [2]
> - The Warrants procedure records warrants against appearances and parties within the file, and
>   the resulting warrant information is displayed on the file's party information. [1]
>
> **Conclusion**
> The documented CEIS procedures indicate that:
> - A Protection Order is entered as a standalone order on the file. [2]
> - A Warrant is entered through Record Results and tracked against the party and appearance on
>   the file. [1]
> - Both can exist on the same CEIS file record, and both are surfaced through the party/file
>   information screens. [3][1]
>
> The procedures do not state that a warrant creates a separate file record from a protection
> order. [1][2]
>
> Sources: warrants--f373f7fc.aspx (turn1search26); orders--25c57174.aspx (turn1search63);
> parties--62236e0e.aspx (turn1search28). [1][2][3]

### Citations / source references

1. `warrants--f373f7fc.aspx`
2. `orders--25c57174.aspx`
3. `parties--62236e0e.aspx`

### Reviewer observations (analysis, clearly separated from raw evidence above)

- **⚠️ PROHIBITED BEHAVIOUR OBSERVED: related-topic-allowance exceeded.** This case's
  `related_topic_allowance` is 2 (primary topic `warrants` + up to 2 related). Run 2 cites **3**
  distinct topics — `warrants`, `orders` (not `protection-orders`), and `parties` — none of which
  is `protection-orders--2955bfec.aspx`, the topic Run 1 used to represent "protection order" and
  the topic the case's own `primary_topic`/prompt wording most directly names. This both exceeds
  the 2-related-topic cap and substitutes a different, related-but-not-identical topic
  (`orders--25c57174.aspx`, the general Orders module page) for the one the question is actually
  about.
- **⚠️ CROSS-RUN INCONSISTENCY.** Run 1 concluded "I cannot confirm that relationship from the
  documented procedures alone" (a declined/hedged answer). Run 2 concludes "Both can exist on the
  same CEIS file record" (an affirmative, confident answer) — a materially different substantive
  conclusion from the same prompt against the same unmodified agent. This does not satisfy the
  expected-behaviour requirement "remains consistent in substance across repeated runs" (from
  `NORM-01`'s criteria; this case's own criteria similarly require the source-supported
  relationship account to be accurate, not merely different-but-plausible each time).
  `CITATION_SUPPORT_NOT_VERIFIED` for the Run 2 citations, so whether Run 2's more confident claim
  is actually textually supported by `orders--25c57174.aspx` is unresolved, not confirmed false —
  but the two runs cannot both be the single correct account of what the source documents say.
- **Citation support:** `CITATION_SUPPORT_NOT_VERIFIED` for all 3 citations in this run.
- **Unsupported claims:** the specific sentence "Both can exist on the same CEIS file record" is
  flagged as **not yet verified against source text** — this is the case's central question, and
  the run's own citations were not opened to confirm this exact claim is textually present rather
  than synthesized/inferred.
- **Refusal/decline behavior:** none this run (contrast with Run 1's partial decline).
- **Ambiguity handling:** n/a.
- **Currency handling:** n/a.
- **Apparent use of knowledge outside the configured source:** none apparent — citations are real
  CEIS `.aspx` topics, the issue is scope/count and cross-run consistency, not source fabrication.
