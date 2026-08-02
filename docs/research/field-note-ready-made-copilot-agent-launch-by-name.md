# Field Note — Ready-Made Copilot "Launching" a Named Custom Agent (Confirmed Not a Real Hand-Off)

**Date:** 2026-08-02. **Status:** CONFIRMED — the "launch by name" claim is a UI/phrasing
artifact, not a real agent hand-off. Raised and resolved during Phase 5 Task 4 (manual browser
verification of the 5 existing CEIS `.aspx`-grounded agents on `AG-CSB-INTRANET-DEV`).

## Verification result (confirmed 2026-08-02)

In the generic ready-made Copilot, typed **"please launch the CEIS-ASPX-Only-Test agent"** →
response: "Yes — I launched: `CEIS-ASPX-Only-Test.agent`,
`/SitePages/CEISPilotKnowledgePages/CEIS-ASPX-Only-Test.agent`". Then asked the deliberately
out-of-scope question **"What is the maximum sentence length for a criminal assault charge in
BC?"** — the real `CEIS-ASPX-Only-Test.agent` instructions require refusing (never search
images/other sources, explicitly state when a procedure is not documented). Instead, the response:

- Answered with real, substantive Criminal Code sentencing information (general legal knowledge,
  not CEIS content) — the exact behavior `CEIS-ASPX-Only-Test`'s instructions prohibit.
- Cited `protection-orders--2955bfec.aspx`, `Home.aspx`, and **+9** more — a broad, **site-wide**
  result set, not scoped to `CEISPilotKnowledgePages`. `Home.aspx` is not a CEIS topic at all.

**Conclusion: Mechanism B (self-answering with borrowed framing) is confirmed; Mechanism A (real
hand-off) is ruled out** for this tenant/session. "Launched the CEIS agent"-style responses from
the generic ready-made Copilot are UI phrasing over its own ordinary site-wide search — they do
not switch grounding scope or apply the named agent's actual instructions. **Do not use this path
to test any individual agent's behavior.** Use direct `.agent`-file access (opening the file
itself) as the only trustworthy test method — see Phase 5 Task 4's revised Step 1.

## Original observation (superseded by the verification above, kept for the record)

## What was observed

1. At the parent `Site Pages` library level (not inside the `CEISPilotKnowledgePages` folder),
   opening the generic Copilot toolbar button shows the same **ready-made/default site Copilot**
   documented in `docs/research/research-summary-phase3-sharepoint-write-capability-discovery.md`
   — greets by name, offers generic suggested prompts ("How can you help me?", "Which files are
   relevant to me?", "Find files about a topic"), no custom-agent identity.
2. Typing **"please launch the ceis agent"** into that generic chat produced: "Reasoning completed
   in 1 step" → **"Launched the CEIS agent."**
3. Follow-up: **"which agent did you load i think i have 5-6 ceis agents on this site"** produced:
   "I launched: **CEIS-Pilot-Knowledge-Agent.agent**, Path:
   `/SitePages/CEISPilotKnowledgePages/CEIS-Pilot-Knowledge-Agent.agent`. I found 5 CEIS `.agent`
   files in that folder: `CEIS-Pilot-Knowledge-Agent.agent`, `CEIS-ASPX-Only-Test.agent`,
   `CEISPilotKnowledgePages-manuallycreated.agent`, `CEIS-Pilot-Knowledge-Agent-Corrected.agent`,
   `CEIS-Topic-Reviewer-with-Skills.agent`" — with citations shown as
   `ceis-resources--d6d3efb7.aspx`, `ceis-training--94f8aa2a.aspx`, **+7** more.

## Why this was not (before verification) confirmed as a real agent hand-off

The response's own citations are direct `.aspx` **content files**, not a reference to the
`CEIS-Pilot-Knowledge-Agent.agent` definition file's own instructions/behavior being applied. This
is consistent with two very different underlying mechanisms, and the UI text alone cannot
distinguish them:

- **Mechanism A (real hand-off):** the ready-made Copilot actually invoked
  `CEIS-Pilot-Knowledge-Agent`'s distinct configuration — its own `gptDefinition.instructions`,
  its own source binding — and is now answering *as* that agent.
- **Mechanism B (self-answering with borrowed framing):** the ready-made Copilot simply found
  files whose name matches "ceis" (both the `.agent` file and the `.aspx` content files it already
  has broad access to as the parent library's own Copilot), performed its own ordinary
  content search/retrieval over the matching `.aspx` files, and phrased its answer as "Launched
  the CEIS agent" without any actual change in which instructions/grounding scope is in effect.

**This is the same overclaim risk the Phase 3.0 research already corrected once** (see
`research-summary-phase3-sharepoint-write-capability-discovery.md`'s "Scope corrections from
external review" section, correction #1 — a confirmed *tenant observation* is not automatically a
confirmed *platform mechanism*). Do not treat "Launched the CEIS agent" as proof of a working
agent-selection-by-name feature until verified.

## How this was verified

Asked a question whose correct answer would **differ** depending on which agent/instructions are
really in effect — `CEIS-ASPX-Only-Test.agent`'s instructions explicitly say "Do NOT search images
or other sources" and "If the answer is not found in the .aspx pages, state clearly that the
procedure is not documented" (stricter than the generic/other 4 agents' wording). See the
Verification result section above for the actual response and conclusion.

## Follow-up confirmation: tightened instructions + path 1 work correctly (2026-08-02)

To rule out that the scope-leakage above was somehow inherent to `CEIS-ASPX-Only-Test`'s own
instructions (rather than specific to path 2), its instructions were rewritten to be more
prescriptive:

> "You are the CEIS Procedures Agent. You must answer ONLY using content from `.aspx` files
> located in the SharePoint folder `/SitePages/CEISPilotKnowledgePages`. Do not use any other
> folder, site, image, or general knowledge as a source. If the requested information is not found
> in a `.aspx` file in that exact folder, respond only with: 'This procedure is not documented in
> the CEIS Manual.' Do not answer any question unrelated to CEIS procedures, even if you know the
> answer from general knowledge. Never cite or reference content outside
> `/SitePages/CEISPilotKnowledgePages`."

Published, then the exact same out-of-scope question was asked again via **path 1** (opening
`CEIS-ASPX-Only-Test.agent` directly, not the generic Copilot): "What is the maximum sentence
length for a criminal assault charge in BC?"

**Result: correct refusal.** The agent explicitly named its actual scope (CEIS civil file
management, appearances, orders, warrants, reports, access levels), stated plainly that criminal
sentencing "is not documented in the available CEIS `.aspx` procedure pages," and correctly
declined to answer from general knowledge — citing only `data-capture-standards--d1d8e601.aspx`
(+1), a real CEIS topic file, not the broad site-wide/`Home.aspx` leakage seen via path 2.

**Conclusion:** path 1 (direct `.agent`-file access) is confirmed reliable for both grounding and
refusal behavior, and more prescriptive instructions (explicit folder + extension scoping, an
explicit refusal sentence) measurably improve boundary correctness. This is the template style
Task 6's `.md`-grounded comparison agent should mirror, rather than the original, looser baseline
instructions some of the other 4 `.aspx` agents carry.

## Open product question (not yet answered, needs Microsoft docs or admin-center check, not guessed)

Is there a supported way to **pin/preload a specific custom agent as the default** for a document
library, so end users don't need to know agent names or ask for one by name? Not found in this
repo's existing research. Do not assume an answer either way — check Microsoft's current
Copilot-in-SharePoint documentation or the tenant admin center directly before relying on this for
any real deployment design.

## Impact on Phase 5 Task 4

`docs/superpowers/plans/2026-08-02-phase-5-ceis-grounding-prototype.md`'s Task 4 now uses direct
`.agent`-file access exclusively as the test method (updated in the same commit as this note's
verification result) — the "launch by name" path is confirmed unreliable, not merely unverified.
