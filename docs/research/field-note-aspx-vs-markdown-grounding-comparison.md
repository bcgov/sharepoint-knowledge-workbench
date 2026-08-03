# Field Note — `.aspx` vs. Rendered-Markdown Grounding: Live Comparison Findings

**Date:** 2026-08-02/03. **Status:** TENANT-TESTED EVIDENCE, small sample (7 cases, 1-2 runs each).
Source: Phase 5 CEIS grounding-only prototype, Tasks 4-8 —
`tools/phase-5-sharepoint-knowledge-agent-pilot/results/task8-consolidated-findings.md` is the
full evidence record; this note extracts the findings with the broadest relevance beyond Phase 5
itself.

## What was tested

Two live SharePoint Copilot agents, identical instructions except for source-format substitution,
grounded on the same CEIS Manual content in two representations: `CEIS-ASPX-Only-Test`
(pandoc-converted `.aspx` pages) and `CEIS-Markdown-Comparison-Agent` (rendered `.md` pages). 7
researcher-authored questions (normal/negative/ambiguous/currency categories), run against both,
1-2 times each, 20 total live runs.

## Findings with relevance beyond Phase 5

### 1. Agents will use file-system metadata as a currency proxy when no real one exists — a general trust-boundary risk, not a CEIS- or format-specific bug

Asked "was topic A or topic B reviewed more recently," **both** agents independently answered by
comparing the topics' SharePoint file-modification (upload) timestamps — an artifact of the
researcher's own batch-upload process, not authored content — and stated a confident conclusion
("reviewed more recently, by 18 seconds" / "by 6 seconds") with no caveat that this isn't a real
review date. Neither agent declined or flagged the absence of real currency metadata, even though
no topic page in the entire evidence set was ever observed to contain an actual authored
"Reviewed: [date]" line.

**Why this generalizes:** this is exactly the risk `docs/vision/ai-assisted-sharepoint-knowledge-workbench-government-vision.md`
and `docs/vision/key-unanswered-questions.md` already flag under currency/trust-boundary design —
concrete, reproducible evidence that a grounded agent will silently substitute a plausible-looking
but semantically wrong signal (upload time) for a real one (authored review date) when asked a
question the source doesn't actually answer. Any future Phase 3/5 currency-handling policy
(`docs/superpowers/specs/phase-5-sharepoint-knowledge-agent-pilot-spec.md` Section 7's
`CURRENT/STALE/OUT_OF_REVIEW/SUPERSEDED/CONFLICTING/UNKNOWN` states) needs an explicit test case
for exactly this failure mode, not just a general "does it handle stale content" check — this
shows the agent doesn't even recognize *absence* of real currency metadata as the `UNKNOWN` state
it should report.

### 2. Repeated runs of the same cross-topic-relationship question can produce mutually contradictory confident answers

Asked twice (same unmodified agent, fresh conversations) whether two related procedures "use the
same file record," both agents' first run appropriately declined/hedged, but the second run gave a
confident, specific answer — and the two agents' confident answers directly contradicted each
other (one said "same record," the other said "separate records"). Also, both agents' second runs
exceeded the evaluation case's configured related-topic count limit.

**Why this generalizes:** consistency-across-repeated-runs is a real, measurable failure mode for
any grounded agent asked to synthesize a relationship the source doesn't directly state — worth a
named evaluation category (not just "cross-topic synthesis," but specifically "repeated-run
consistency for synthesized relationships") in any future formal Phase 5 evaluation-case set,
beyond this prototype's informal `run_count: 2` mechanism.

### 3. Ambiguity handling showed the only representation-level (not shared) difference found

On the one ambiguity-category case tested, the Markdown-grounded agent cleanly met the
ambiguity-handling requirement on both runs (asking a clarifying question on one run, explicitly
enumerating distinct documented scenarios on the other); the `.aspx`-grounded agent only partially
met it on both runs (blended distinct scenarios into one generalized answer without asking or
cleanly enumerating). This is a single-case finding, not confirmed against a larger ambiguity-case
set, but it's the only place in this evidence where format (not shared model behavior) looked like
the explanatory variable.

### 4. Direct/negative-case grounding quality was comparable across formats

For directly-answerable procedural questions and out-of-scope/nonexistent-topic decline cases, both
representations performed comparably well — detailed, well-cited, correctly declining when
appropriate, with no material quality gap. This is consistent with (and adds tenant-tested evidence
for) `docs/research/concept-dual-target-rendering-agent-vs-human.md`'s premise that multiple
renderer targets can serve an agent-grounding use case without a forced format trade-off.

## Explicit limitation

Citation support was **not verified** in any of the 20 runs (no cited source was opened and
checked against the claim it supposedly supports) — see
`task8-consolidated-findings.md` Section 5. All findings above rest on response text and structure,
not confirmed source accuracy. Sample size (7 cases, 1-2 runs) is too small for any statistical
claim; findings 1 and 2 above are the strongest (reproduced across both agents independently),
finding 3 is the weakest (single case, unconfirmed against a larger sample).

## Relevance to open questions elsewhere in this repo

- `docs/vision/key-unanswered-questions.md` — currency/trust-boundary and AI-trust-boundary
  questions gain a concrete reproducible failure example (finding 1).
- `docs/superpowers/specs/phase-5-sharepoint-knowledge-agent-pilot-spec.md` Section 7 (currency
  behavior states) — needs an explicit "no real currency metadata exists → agent must report
  `UNKNOWN`, not infer from file timestamps" test case.
- `docs/research/concept-dual-target-rendering-agent-vs-human.md` — finding 4 is tenant-tested
  support for that document's premise; finding 3 is a data point (not yet conclusive) for a
  possible format-specific difference worth a dedicated follow-up test if the dual-target model is
  pursued further.
