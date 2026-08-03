# Task 8 — Consolidated Findings

**Source evidence used exclusively:** `results/{NORM-01,NORM-02,NEG-01,NEG-02,AMB-01,CUR-01,CUR-02}-{aspx,md}.md`
and `results/task7-run-ledger.md`. No case was rerun, no agent was modified, no tenant content was
modified, and no citation was opened or validated to produce this document.

---

## 1. Prototype scope

This was a **grounding-only exploratory comparison** between two SharePoint Copilot agents grounded
on the same underlying CEIS Manual content in two different representations:

- **CONTROL:** `CEIS-ASPX-Only-Test` — grounded on the pandoc-converted `.aspx` topic pages.
- **COMPARISON:** `CEIS-Markdown-Comparison-Agent` (created in Task 6) — grounded on the rendered
  `.md` topic pages, with instructions identical to CONTROL except for the minimal source-format
  substitutions documented in `results/task6-instruction-diff.md`.

**This prototype does not certify:** production readiness; legal accuracy; comprehensive
permission safety; suitability for legal decision-making; citation correctness; coverage of all
CEIS procedures; or coverage of all possible user questions. It evaluates a bounded set of 7
researcher-created questions against 2 agents, nothing broader.

## 2. Test design

- 7 approved evaluation cases: 2 normal (`NORM-01`, `NORM-02`), 2 negative (`NEG-01`, `NEG-02`),
  1 ambiguous (`AMB-01`), 2 currency (`CUR-01`, `CUR-02`).
- Both agents tested against every case, using the identical, verbatim approved prompt text from
  each case's evaluation JSON.
- Both agents were live, unmodified, direct-`.agent`-file-access instances — no instructions or
  source bindings were changed during Task 7.
- 0 technical retries were required.
- **20 total recorded runs** (`task7-run-ledger.md`): `NORM-01`, `NORM-02`, and `AMB-01` each have
  `run_count: 2` per their evaluation JSON (2 runs × 2 agents = 4 runs each = 12 runs);
  `NEG-01`, `NEG-02`, `CUR-01`, `CUR-02` each have `run_count: 1` (1 run × 2 agents = 2 runs each =
  8 runs). 12 + 8 = 20 total runs.
- **14 final agent/case evidence records** — one file per (case × representation) pair
  (7 cases × 2 representations = 14 files), each file containing all of that pair's runs (1 or 2,
  per the case's `run_count`).
- **Documented provenance correction:** during `AMB-01` execution, a response intended as
  CONTROL's second run was, based on its own response header, identified as a genuine
  `CEIS-Markdown-Comparison-Agent` response instead. It was not discarded — per the retry rule
  (no retry solely to obtain a different result), it was filed as `AMB-01-md.md` Run 1, with an
  explicit provenance note preserved in that file. This correction remains visible in this report,
  not silently absorbed into the run count.

## 3. Per-case comparison

### NORM-01 — "What are the steps to initiate a new file in CEIS?"

- **Expected answerability:** directly answerable from one topic (`initiate-a-file`).
- **CONTROL:** both runs answered directly and consistently (same core 4-step procedure across
  runs), citing 2–4 real `.aspx` topics per run.
- **COMPARISON:** both runs answered directly and consistently (same 4-step structure), citing the
  `.md` counterparts of the same topics.
- **Answer completeness:** both representations gave complete, detailed procedural answers in
  both runs.
- **Refusal/decline:** none — not applicable to this case.
- **Ambiguity handling:** n/a.
- **Currency handling:** n/a.
- **Citation presence:** present in all 4 runs (2 CONTROL, 2 COMPARISON).
- **Citation source type:** real named topic pages (`.aspx` for CONTROL, `.md` for COMPARISON),
  matching the queried representation.
- **Unsupported/questionable statements:** none flagged.
- **Material difference between representations:** none of substance — both representations
  produced comparable, consistent, well-structured answers.
- **Evidence files:** `NORM-01-aspx.md`, `NORM-01-md.md`.

### NORM-02 — "How does a warrant relate to a protection order in CEIS — do they use the same file record?"

- **Expected answerability:** cross-topic synthesis, up to 2 related topics.
- **CONTROL:** Run 1 declined to confirm the relationship ("I cannot confirm that relationship
  from the documented procedures alone"), citing 2 topics (within allowance). Run 2 gave a
  confident, different conclusion ("Both can exist on the same CEIS file record"), citing 3 topics
  — exceeding the case's `related_topic_allowance: 2`.
- **COMPARISON:** Run 1 also declined ("does not explicitly state whether... same underlying
  database/file record"), citing 1 topic. Run 2 gave a confident, different conclusion ("separate
  record types... not the same CEIS record"), citing 4 topics — also exceeding the allowance, and
  contradicting CONTROL's own confident Run 2 conclusion.
- **Answer completeness:** all 4 runs are substantively complete; the issue is consistency and
  scope compliance, not completeness.
- **Refusal/decline:** partial decline in both agents' Run 1; no decline in either agent's Run 2.
- **Ambiguity handling:** n/a (this case is cross-topic synthesis, not the ambiguity category).
- **Currency handling:** n/a.
- **Citation presence:** present in all 4 runs.
- **Citation source type:** real named topics in all runs; Run 2 of both agents cited topics
  beyond the allowed count.
- **Unsupported/questionable statements:** both agents' Run 2 conclusions are flagged as
  `CITATION_SUPPORT_NOT_VERIFIED` and mutually contradictory — at most one can be the accurate
  account of the source content, and neither has been confirmed correct.
- **Material difference between representations:** both representations show the **same failure
  shape** (Run 1 hedge → Run 2 confident-but-allowance-exceeding-and-inconsistent) — this is a
  shared behavior pattern, not a representation-specific difference; the specific Run 2 answers
  differ in content between agents (same-record vs. separate-record framing).
- **Evidence files:** `NORM-02-aspx.md`, `NORM-02-md.md`.

### NEG-01 — "What is the maximum sentence length for a criminal assault charge in BC?"

- **Expected answerability:** entirely out of scope; should decline.
- **CONTROL:** clean, explicit decline, citing 3 topics as evidence of what the source *does*
  cover (a scope-justification citation pattern).
- **COMPARISON:** clean, explicit decline, citing 0 topics (nothing found to cite), and offered to
  search for a specific topic if provided.
- **Answer completeness:** n/a (decline case) — both declines were complete and clear.
- **Refusal/decline:** both agents declined cleanly and correctly.
- **Ambiguity handling:** n/a.
- **Currency handling:** n/a.
- **Citation presence:** present (3) for CONTROL, absent (0, appropriately) for COMPARISON.
- **Citation source type:** CONTROL cited real `.aspx` topics to explain scope; COMPARISON cited
  none.
- **Unsupported/questionable statements:** none in either.
- **Material difference between representations:** stylistic only (citation-for-scope vs.
  no-citation-plus-offer-to-search) — both decline correctly.
- **Evidence files:** `NEG-01-aspx.md`, `NEG-01-md.md`.

### NEG-02 — "What is the CEIS procedure for filing an appeal after a court decision?"

- **Expected answerability:** no direct topic exists; optional graceful redirect to a related real
  topic is acceptable.
- **CONTROL:** correctly reported no "filing an appeal" procedure exists, redirected to the real
  `transfers` topic, explicitly flagged it as not a direct match.
- **COMPARISON:** near-identical behavior — same redirect, same explicit limitation statement.
- **Answer completeness:** both complete for what they cover (the related transfer procedure),
  both explicit about what they do not cover.
- **Refusal/decline:** partial decline in both, redirecting rather than fabricating.
- **Ambiguity handling:** n/a.
- **Currency handling:** n/a.
- **Citation presence:** present in both (1 citation each, to the `transfers` topic in its
  respective format).
- **Citation source type:** real named topic in both.
- **Unsupported/questionable statements:** none in either.
- **Material difference between representations:** none of substance — this is the closest match
  between the two agents observed in the entire evidence set.
- **Evidence files:** `NEG-02-aspx.md`, `NEG-02-md.md`.

### AMB-01 — "How do I get access to a file?"

- **Expected answerability:** deliberately ambiguous; should ask a clarifying question or
  explicitly enumerate the distinct documented procedures.
- **CONTROL:** both runs synthesized one generalized answer (Access Level + Access Role), gesturing
  at an internal/external distinction but not cleanly asking a clarifying question or enumerating
  distinct named procedures — a **partial** satisfaction of the expected behaviour, consistent
  across both runs. One provenance-affected paste occurred here (see Section 2) and was not filed
  under CONTROL.
- **COMPARISON:** Run 1 asked a genuine clarifying question (4 distinct access scenarios offered).
  Run 2 explicitly enumerated 4 distinct documented access-level categories instead. Both are the
  case's two explicitly acceptable strategies — this case's requirement was **cleanly met** on
  both runs.
- **Answer completeness:** all runs substantively complete.
- **Refusal/decline:** n/a.
- **Ambiguity handling:** the case's central test — CONTROL partial both runs; COMPARISON clean
  both runs, via two different valid strategies.
- **Currency handling:** n/a.
- **Citation presence:** present in all runs (2–3 topics each).
- **Citation source type:** real named topics in all runs.
- **Unsupported/questionable statements:** none flagged; the specific clarifying/enumerated
  categories offered by COMPARISON did not exactly match the case's own framing
  (public/party/staff), but this was not treated as fabrication — it is real source-grounded
  content addressing a genuinely different (but real) ambiguity axis.
- **Material difference between representations:** the clearest representation-level difference in
  the evidence set — COMPARISON handled this case's core requirement better than CONTROL on both
  runs.
- **Evidence files:** `AMB-01-aspx.md`, `AMB-01-md.md`.

### CUR-01 — "Is the CEIS procedure for initiating a file the current version, or could it be outdated? How would I know?"

- **Expected answerability:** should report actual currency signals if present, state plainly if
  none exist, avoid asserting certainty.
- **CONTROL:** correctly reported no version/review/approval date exists in the source content;
  cited page creation/modification metadata with an explicit caveat that this "does not prove...
  the current approved version." Cited 5 topics — exceeding `related_topic_allowance: 0` (4
  beyond the primary).
- **COMPARISON:** cited only the primary topic (1, respecting the allowance), but concluded the
  page "suggests it is a current version rather than an outdated copy" based on a "last modified
  about an hour ago" timestamp, without CONTROL's explicit disclaimer that this doesn't prove
  approved-current status.
- **Answer completeness:** both complete.
- **Refusal/decline:** neither declined; both answered with caveats of differing strength.
- **Ambiguity handling:** n/a.
- **Currency handling:** the case's central test — CONTROL gave stronger caveats but broke the
  topic-count constraint; COMPARISON respected the topic-count constraint but gave weaker caveats
  and leaned closer to asserting currency from an edit timestamp.
- **Citation presence:** present in both (5 for CONTROL, 1 for COMPARISON).
- **Citation source type:** real named topics; CONTROL's additional 4 are support-page topics
  (`ceis-resources`, `ceis-support-faq`, `ceis-training`, `other-helpful-support-emails`), not
  duplicates of the primary.
- **Unsupported/questionable statements:** COMPARISON's inference from "recently modified" to
  "current version" is flagged as the weakest point in this case's evidence.
- **Material difference between representations:** a genuine trade-off — neither representation is
  unambiguously better; each violates a different part of the case's requirements.
- **Evidence files:** `CUR-01-aspx.md`, `CUR-01-md.md`.

### CUR-02 — "Was the warrants procedure or the protection-orders procedure reviewed more recently?"

- **Expected answerability:** should check for real review/version metadata in both topics; state
  plainly if neither carries it; must not infer recency from irrelevant signals.
- **CONTROL:** inferred "reviewed more recently" from an **18-second** file-modification-timestamp
  gap between the two `.aspx` files' tenant upload records, stated as a confident conclusion
  ("Therefore... was reviewed more recently, by 18 seconds") with no caveat.
- **COMPARISON:** inferred the identical conclusion type from a **6-second** file-modification-
  timestamp gap between the two `.md` files' tenant upload records, also stated confidently
  ("The warrants procedure was reviewed more recently... modified approximately 6 seconds
  later"), with no caveat.
- **Answer completeness:** both complete in form, both substantively incorrect in kind (see below).
- **Refusal/decline:** neither declined; both should have, per this case's expected behaviour.
- **Ambiguity handling:** n/a.
- **Currency handling:** **the clearest shared failure in the entire evidence set** — both agents
  committed the same prohibited-behaviour pattern ("infer recency from irrelevant signals"),
  substituting tenant upload-batch timing (an artifact of the researcher's own upload process, not
  documented content) for real review metadata, with no source page in the entire Task 7 evidence
  set ever having quoted an actual in-content "Reviewed: [date]" line.
- **Citation presence:** present in both (2 each, within the `related_topic_allowance: 2` cap in
  both cases).
- **Citation source type:** real named topics in both.
- **Unsupported/questionable statements:** the core conclusion in both runs ("reviewed more
  recently") is flagged as unsupported relative to what "reviewed" means in this case's framing.
- **Material difference between representations:** none — this is a shared, format-independent
  failure.
- **Evidence files:** `CUR-02-aspx.md`, `CUR-02-md.md`.

## 4. Cross-case findings

**OBSERVED_IN_EVIDENCE:**
- Both agents answered directly-answerable procedural questions (`NORM-01`) with comparable
  completeness, structure, and citation practice.
- Both agents declined out-of-scope and non-existent-topic questions cleanly (`NEG-01`, `NEG-02`),
  with near-identical quality on `NEG-02` specifically.
- Both agents exceeded the case-specified `related_topic_allowance` on their second run of
  `NORM-02` (3 and 4 topics vs. a cap of 2) and on `CUR-01` (CONTROL: 5 vs. cap of 0).
- Both agents produced mutually inconsistent conclusions across repeated runs of `NORM-02`
  specifically — this instability was not observed on `NORM-01`, `NEG-01`, `NEG-02`, or `AMB-01`.
- Both agents committed the identical prohibited-behaviour pattern on `CUR-02` (inferring recency
  from an upload-timestamp gap), using different underlying timestamp values consistent with each
  representation's own separate upload event.
- COMPARISON handled `AMB-01`'s ambiguity-recognition requirement more cleanly than CONTROL on
  both runs of that case specifically.
- COMPARISON gave a currency answer on `CUR-01` that was more assertive about "current" status
  than CONTROL's answer to the same question.

**INTERPRETATION (not directly measured, offered as reviewer synthesis only):**
- The `NORM-02` and `CUR-02` failure patterns appearing on both agents suggests these are
  properties of the underlying model's reasoning tendencies (over-synthesis on repeated runs of an
  under-specified relationship question; treating any available timestamp as a currency proxy when
  no real one exists) rather than an artifact specific to `.aspx` vs. `.md` grounding format. This
  is a plausible reading of the pattern, not a proven causal claim — the evidence set (7 cases, 1-2
  runs each) is too small to rule out coincidence.
- `AMB-01`'s result might suggest the Markdown representation's content structure makes distinct
  access scenarios easier for the model to identify as separate items than the `.aspx`
  representation does — but this is a single case observation, not confirmed against any other
  ambiguity-category case (only 1 exists in this evidence set), and could equally be run-to-run
  variance unrelated to format.
- No pattern in this evidence set suggests one representation is more prone to prohibited behaviour
  overall — the two clearest violations (`NORM-02`'s allowance-exceeding, `CUR-02`'s timestamp
  inference) both occurred on **both** agents.

## 5. Citation limitation

**`CITATION_SUPPORT_NOT_VERIFIED`** applies to every citation in every one of the 20 recorded runs
and all 14 evidence files. Specifically:
- No citation was opened or checked against the response text that cited it.
- The mere presence of a citation, or a citation's title appearing topically relevant, does not
  prove the cited source actually contains or supports the specific claim attributed to it.
- No conclusion in this document, or in any of the 14 evidence files, claims citation correctness.
- Citation verification remains explicitly deferred — none of the findings above (including the
  `NORM-02` and `CUR-02` failure findings) rest on confirmed citation-content accuracy; they rest
  on the response text's own internal claims, structure, and stated reasoning, which is a
  different and weaker form of evidence than verified citation support.

## 6. Representation conclusion

- **Did both representations produce usable responses for the selected cases?** Yes — both
  agents produced substantive, on-topic responses for all 7 cases, with no outright failures to
  respond.
- **Did one representation show a consistent advantage in this evidence?** No single
  representation was consistently better across all cases. COMPARISON showed a clear advantage on
  `AMB-01` (ambiguity handling) and better topic-count discipline on `CUR-01`. CONTROL showed
  stronger currency caveats on `CUR-01`. On `NORM-01`, `NEG-01`, `NEG-02`, `NORM-02`, and `CUR-02`,
  the two representations performed comparably (including comparably poorly on `NORM-02` and
  `CUR-02`).
- **Were differences large enough to justify a publication-format decision?** No. The evidence is
  mixed, the case count is small (7 cases, some with only 1 run), and the two clearest failure
  patterns found were shared by both representations rather than distinguishing between them. This
  evidence does not support choosing `.aspx` over `.md` or vice versa as a grounding format on
  quality grounds alone.
- **Which observed differences require further testing?** The `AMB-01` ambiguity-handling
  difference (1 case only — needs more ambiguous-category cases to confirm it's a real,
  repeatable pattern rather than case-specific); the `CUR-01` currency-caveat-strength difference
  (also 1 case); whether the shared `NORM-02`/`CUR-02` failure patterns are genuinely
  format-independent model behavior or coincidental given the small sample.

**Evidence is mixed. No winner is declared.**

## 7. Content gaps

| Case | Representation | Response evidence | Likely concern |
|---|---|---|---|
| `NORM-02` | both | Neither agent's source citations, on either run, could confirm a documented statement of whether warrants and protection orders share a file record — both hedged (Run 1) or guessed differently (Run 2) | `POSSIBLE_CONTENT_GAP` — the CEIS Manual may genuinely not document this specific cross-topic relationship, or the agents' retrieval may not be surfacing it if it exists. Cause not distinguished by this evidence; the manual itself was not checked. |
| `CUR-01` / `CUR-02` | both | No case response, across the entire Task 7 evidence set, ever quoted an in-content "Reviewed: [date]" or version-number line from any topic page | `POSSIBLE_CONTENT_GAP` — the CEIS Manual's topics may genuinely lack authored currency/version metadata. This is consistent across both representations and all currency-category cases, which weakly supports a real content gap rather than a retrieval failure (a retrieval failure would more plausibly show inconsistency between agents or runs). Not confirmed — the source itself was not directly checked as part of this task. |
| `AMB-01` | CONTROL | Both CONTROL runs did not surface the public/party/staff access distinction the case's own framing expects, even though `file-access`/`ceis-access-levels` were cited | Unknown cause — could be a retrieval/synthesis limitation (content exists but wasn't surfaced as distinct items) or an instruction-following limitation (content was seen but blended together anyway). Not distinguished by this evidence. |

## 8. Prototype limitations

- Researcher-created case set (7 cases), not authored or reviewed by a CEIS subject-matter expert.
- Small case count — several cases had only 1 run; even the 2-run cases provide limited statistical
  basis for any conclusion.
- Single source document (the CEIS Manual) — findings do not generalize to other manuals or
  content types.
- Single SharePoint sandbox (`AG-CSB-INTRANET-DEV`), not a production tenant.
- Single licensed test account/identity — no multi-identity permission or oversharing testing was
  performed (explicitly deferred per the Phase 5 design).
- No native-skill comparison (`GROUNDING_PLUS_NATIVE_SKILL`) was performed — explicitly deferred.
- No citation-support verification was performed — explicitly deferred, see Section 5.
- No production deployment governance or approval process was exercised.
- No legal-accuracy validation was performed on any CEIS procedural content.
- No statistical significance claim is made or supportable from this evidence — sample sizes are
  too small (1-2 runs per case) for any quantitative generalization.

## 9. Recommended next steps

- **NOW:** none — this prototype's findings do not require immediate action; they are exploratory
  evidence, not a production defect requiring a fix.
- **NEXT:** if this prototype's scope is extended, prioritize (a) more ambiguous-category cases to
  confirm whether `AMB-01`'s COMPARISON advantage is real and repeatable, and (b) a direct check of
  whether the CEIS Manual source content actually contains the warrant/protection-order
  relationship (`NORM-02`) and any review/version metadata (`CUR-01`/`CUR-02`), to distinguish real
  content gaps from retrieval/synthesis limitations.
- **LATER:** citation-support verification (opening and checking every cited source against its
  claim) across the existing 20 runs, before treating any of this document's findings as more than
  provisional.
- **DEFERRED:** multi-identity permission/oversharing testing; native-skill comparison; any
  production deployment or governance decision; any decision to standardize on `.aspx` or `.md` as
  the grounding format for future documents (Section 6 explicitly found no evidence basis for such
  a decision).

## 10. Final bounded conclusion

> This prototype evaluates grounded answer behavior for a selected set of researcher-created CEIS
> questions. It does not certify production readiness, complete permission safety, citation
> correctness, or suitability for legal decision-making.
