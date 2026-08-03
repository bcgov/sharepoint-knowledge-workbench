# NORM-02 — COMPARISON (`CEIS-Markdown-Comparison-Agent`)

**Category:** normal
**Exact prompt (verbatim from `evaluations/normal/case-normal-02.json`):** "How does a warrant
relate to a protection order in CEIS — do they use the same file record?"
**Expected run_count:** 2

---

## Run 1

**Agent:** `CEIS-Markdown-Comparison-Agent`
**Execution timestamp (capture time):** 2026-08-03T00:55:00Z (approximate — user-side)
**Retry count:** 0
**Anomalies/UI limitations:** none

### Raw response (verbatim, unedited)

> Based on the CEIS procedure pages I found, warrants and protection orders are tracked
> separately, but both are associated to the same file and party record.
>
> The relevant documentation states:
> - In the Party Details screen, there is a "Party Warrant Information" area, and "If a WARRANTS
>   is entered into CEIS, information will be captured here." [1]
> - In the Party Summary screen, CEIS displays information about a party, including "any AKAs,
>   warrants, or protection/firearms orders against them." [1]
> - The example in the Party Summary section specifically notes that there were "no WARRANTS,
>   PROTECTION ORDERS or Firearm Orders" for the parties. [1]
>
> From the documented procedures, CEIS presents warrants and protection orders as distinct types
> of information tied to a party on a file, rather than describing them as a single shared
> record. However, the documentation I found does not explicitly state whether a warrant and a
> protection order use the exact same underlying database/file record or whether they are stored
> as separate records linked to the same file.
>
> Sources
> - parties--62236e0e.md [1]
>
> If you need the technical relationship (for example, whether entering a warrant creates a
> separate Warrants record versus an Order record), I can search the CEIS markdown pages
> specifically for "Warrants" and "Protection Orders" procedures.

### Citations / source references

1. `parties--62236e0e.md`

### Reviewer observations (analysis, clearly separated from raw evidence above)

- **Expected answerability matched:** partial — answers using only 1 topic (`parties`), never
  directly consulting the `warrants` or `protection-orders` topics the question is actually about.
  Stays well within the `related_topic_allowance: 2` cap (uses 1), unlike the CONTROL agent's
  Run 2 (see `NORM-02-aspx.md`), but this is a different kind of gap — under-consultation of the
  two topics the question directly names, rather than over-consultation.
- **Citation support:** `CITATION_SUPPORT_NOT_VERIFIED` for the 1 citation.
- **Unsupported claims:** none apparent — the response is explicitly hedged ("does not explicitly
  state whether... same underlying database/file record"), matching the expected behaviour
  "states explicitly if the source content does not directly answer the relationship."
- **Refusal/decline behavior:** partial decline on the core technical question, consistent with
  CONTROL Run 1's pattern.
- **Ambiguity handling:** n/a.
- **Currency handling:** n/a.
- **Apparent use of knowledge outside the configured source:** none apparent.
- **Anomaly — proactive follow-up offer.** The response ends by offering to search further
  ("If you need the technical relationship... I can search..."). This is a UI/behavioral
  observation, not a prohibited-behaviour violation per this case's defined criteria, but is noted
  since it's a response-shape difference from the CONTROL agent's runs (neither CONTROL run made
  this kind of offer).

---

## Run 2

**Agent:** `CEIS-Markdown-Comparison-Agent`
**Execution timestamp (capture time):** 2026-08-03T01:02:00Z (approximate — user-side)
**Retry count:** 0
**Anomalies/UI limitations:** none

### Raw response (verbatim, unedited)

> Based on the CEIS Markdown procedures, warrants and protection orders are tracked as separate
> records/functions within the same court file, not as the same record type.
>
> **What the procedures document**
> - Warrants are entered and managed through the Warrants tab in the Record Results module and
>   are associated with a party and appearance. Once issued, warrant information is also
>   displayed in the party details area and a warrant flag appears on the file. [1]
> - Protection Orders are entered as Orders (specifically POR/ROR order types), with their own
>   order details, protected/restrained parties, terms, and POR processing requirements. They are
>   maintained through the Orders/POR Details functionality. [2][3]
>
> **Relationship on the file**
> The procedures indicate that the Party Summary can show both:
> - Warrants
> - Protection Orders
> - Firearms Orders
>
> for a party on the file. This suggests they are distinct pieces of information attached to the
> same court file and party records, rather than a single shared record. [4]
>
> **Is the same file record used?**
> The documentation does not explicitly state that a warrant and a protection order share the
> same underlying CEIS record. What it does state is:
> - A warrant is created and maintained in the Warrants area. [1]
> - A protection order is created and maintained in the Orders/POR Details area. [2][3]
>
> Therefore, from the documented procedures, they are separate record types within the same court
> file, not the same CEIS record.
>
> Sources: warrants--f373f7fc.md, protection-orders--2955bfec.md, orders--25c57174.md,
> parties--62236e0e.md [1][2][3][4]

### Citations / source references

1. `warrants--f373f7fc.md`
2. `protection-orders--2955bfec.md`
3. `orders--25c57174.md`
4. `parties--62236e0e.md`

### Reviewer observations (analysis, clearly separated from raw evidence above)

- **⚠️ PROHIBITED BEHAVIOUR OBSERVED: related-topic-allowance exceeded, more severely than
  CONTROL.** This case's `related_topic_allowance` is 2. Run 2 cites **4** distinct topics
  (`warrants`, `protection-orders`, `orders`, `parties`) — even more than CONTROL Run 2's 3. Same
  violation pattern as the CONTROL agent, worse in degree.
- **⚠️ CROSS-RUN INCONSISTENCY, same shape as CONTROL.** Run 1 concluded the documentation "does
  not explicitly state whether... same underlying database/file record" (hedged/no answer). Run 2
  concludes definitively "they are separate record types within the same court file, not the same
  CEIS record" — a confident, specific answer to the exact question Run 1 declined to answer. This
  mirrors the CONTROL agent's Run1-hedge → Run2-confident-but-different-conclusion pattern almost
  exactly, though the two agents' Run 2 conclusions **also disagree with each other**: CONTROL
  Run 2 concluded "both can exist on the same CEIS file record" (same-record framing); this run
  concludes "separate record types... not the same CEIS record" (different-record framing). Four
  runs across two agents produced three distinct positions (hedge / same-record / different-record)
  on the identical question.
- **Citation support:** `CITATION_SUPPORT_NOT_VERIFIED` for all 4.
- **Unsupported claims:** the specific conclusion "not the same CEIS record" is flagged as **not
  yet verified against source text** — same caveat as CONTROL Run 2's opposite claim.
- **Refusal/decline behavior:** none this run (contrast with Run 1's partial decline).
- **Ambiguity handling:** n/a.
- **Currency handling:** n/a.
- **Apparent use of knowledge outside the configured source:** none apparent — all 4 citations are
  real CEIS `.md` topics.
