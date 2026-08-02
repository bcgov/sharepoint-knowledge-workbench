# Field Note — Ready-Made Copilot "Launching" a Named Custom Agent (Unverified Claim)

**Date:** 2026-08-02. **Status:** OBSERVATION, NOT YET VERIFIED. Raised during Phase 5 Task 4
(manual browser verification of the 5 existing CEIS `.aspx`-grounded agents on
`AG-CSB-INTRANET-DEV`).

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

## Why this is not yet confirmed as a real agent hand-off

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

## How to actually verify (not yet done)

Ask a question whose correct answer would **differ** depending on which agent/instructions are
really in effect — e.g. `CEIS-ASPX-Only-Test.agent`'s instructions explicitly say "Do NOT search
images or other sources" and "If the answer is not found in the .aspx pages, state clearly that
the procedure is not documented" (stricter than the generic/other 4 agents' wording). If asking
the parent ready-made Copilot to "launch CEIS-ASPX-Only-Test" and then asking an out-of-scope
question produces that agent's distinctive refusal wording, that's real evidence of a hand-off. If
it answers however the generic Copilot normally would, Mechanism B is more likely.

## Open product question (not yet answered, needs Microsoft docs or admin-center check, not guessed)

Is there a supported way to **pin/preload a specific custom agent as the default** for a document
library, so end users don't need to know agent names or ask for one by name? Not found in this
repo's existing research. Do not assume an answer either way — check Microsoft's current
Copilot-in-SharePoint documentation or the tenant admin center directly before relying on this for
any real deployment design.

## Impact on Phase 5 Task 4

`docs/superpowers/plans/2026-08-02-phase-5-ceis-grounding-prototype.md`'s Task 4 originally assumed
testing each of the 5 agents by opening its `.agent` file directly. This "launch by name" path is
an additional, lower-friction route worth trying, but its results should **not** be trusted as
agent-specific until the verification method above is actually run — see the plan update in the
same commit as this note.
