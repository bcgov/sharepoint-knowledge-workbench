# Task 6 — Baseline Re-Verification (gate before creating the Markdown comparison agent)

**Purpose:** resolve a discrepancy found at Task 6 Step 1 — the instructions text documented in
the plan/design docs as "confirmed, tightened" does not match what's actually live on
`CEIS-ASPX-Only-Test.agent`. Per explicit instruction, the live tenant artifact is authoritative;
the documentation is corrected to match reality, not the other way around. The live agent has
**not** been modified — this is read-only retrieval only.

## Two distinct labels (do not conflate)

- **`DOCUMENTED_TIGHTENED_TEXT`** — previously recorded in
  `docs/superpowers/plans/2026-08-02-phase-5-ceis-grounding-prototype.md` (Task 4/6) and
  `docs/research/field-note-ready-made-copilot-agent-launch-by-name.md` as the confirmed-working
  instructions. **Not confirmed as the current live tenant value** — the available evidence proves
  only that the current live text differs from this recorded text, not why (browser edit not
  persisted, mis-recorded at the time, or the agent was later recreated — cause not established).
- **`AUTHORITATIVE_LIVE_BASELINE`** — the exact text retrieved from `CEIS-ASPX-Only-Test.agent`
  immediately before Task 6, below.

## Retrieval evidence

```text
RETRIEVAL_TIME: 2026-08-02T16:56:55.2017980-07:00
AGENT_FILENAME:  CEIS-ASPX-Only-Test.agent
TENANT_PATH:     /sites/AG-CSB-INTRANET-DEV/SitePages/CEISPilotKnowledgePages/CEIS-ASPX-Only-Test.agent
SHA256:          AB5A1B519CCB2E3F34E845B3E7CF25BBED194E4AE8F0A379E8B1CCEB959B50B4
```

## `AUTHORITATIVE_LIVE_BASELINE` — exact text

> "You are the CEIS Procedures Agent. Search and answer ONLY using the CEISPilotKnowledgePages
> .aspx procedure pages. Search strategy: (1) Search the CEISPilotKnowledgePages folder for
> .aspx pages matching the user's question, (2) Extract detailed step-by-step procedures from the
> .aspx pages found, (3) Always cite the specific .aspx page name, (4) If the answer is not found
> in the .aspx pages, state clearly that the procedure is not documented. Do NOT search images or
> other sources. Reply in a formal, professional tone."

## `DOCUMENTED_TIGHTENED_TEXT` (superseded — kept for the record, not used going forward)

> "You are the CEIS Procedures Agent. You must answer ONLY using content from `.aspx` files
> located in the SharePoint folder `/SitePages/CEISPilotKnowledgePages`. Do not use any other
> folder, site, image, or general knowledge as a source. If the requested information is not
> found in a `.aspx` file in that exact folder, respond only with: 'This procedure is not
> documented in the CEIS Manual.' Do not answer any question unrelated to CEIS procedures, even
> if you know the answer from general knowledge. Never cite or reference content outside
> `/SitePages/CEISPilotKnowledgePages`."

## Re-verification against the actual live agent — RESULTS

Both questions run directly against the live `CEIS-ASPX-Only-Test` agent (path 1) on 2026-08-02,
same session as the retrieval above.

**1. Smoke-test question: "What are the steps to initiate a new file in CEIS?"**

Well-grounded, detailed procedural answer (File Identification fields, party/role requirement,
initiating document, save/abandon behavior), citing 2 real sources:
`initiate-a-file--51d1f554.aspx`, `documents-data-entry--e87c1624.aspx`. No fabrication, no
out-of-scope content.

**2. Refusal question: "What is the maximum sentence length for a criminal assault charge in
BC?"**

Correctly declined: "I could not find any information in the available CEIS procedure pages that
documents the maximum sentence length for a criminal assault charge in British Columbia... The
maximum sentence length for a criminal assault charge in BC is not documented in the available
CEIS .aspx procedure pages." Cited only real CEIS content (`data-capture-standards--d1d8e601.aspx`)
to explain the scope boundary — no general legal knowledge, no site-wide/unrelated citations (the
earlier path-2 failure mode from `field-note-ready-made-copilot-agent-launch-by-name.md` does not
reproduce here).

A third question was judged unnecessary — question 2 already demonstrates clean refusal behavior
with no leakage, matching the pattern needed to trust this as a real control baseline.

**Disposition: PASS.** `AUTHORITATIVE_LIVE_BASELINE` (the exact text captured above) is retained as
the Task 6 baseline, unmodified. The live `CEIS-ASPX-Only-Test` agent itself was not touched by
this re-verification — read-only questions only.

**Status: RE-VERIFIED, BASELINE ACCEPTED.**
