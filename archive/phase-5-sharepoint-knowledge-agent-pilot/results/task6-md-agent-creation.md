# Task 6 Results — `.md`-Grounded Comparison Agent

**Agent name:** `CEIS-Markdown-Comparison-Agent`
**Tenant path:** `/sites/AG-CSB-INTRANET-DEV/SitePages/CEISPilotKnowledgePages/CEIS-Markdown-Comparison-Agent.agent`
**Source binding:** `https://bcgov.sharepoint.com/sites/AG-CSB-intranet-dev/CEISPilotKnowledge/pages`
(verified via independent `Get-PnPFile` read-back, not just the creation script's own success
message)

## Baseline discrepancy found and resolved before this agent was created

See `results/task6-baseline-verification.md`. The instructions previously documented as
"confirmed, tightened" did not match the actual live `CEIS-ASPX-Only-Test.agent` text. The live
text (`AUTHORITATIVE_LIVE_BASELINE`) was re-verified against the Task 4 smoke-test and refusal
questions — both passed cleanly, no leakage — and accepted as the real control baseline. This
agent's instructions are that exact text with only the 4 source-related phrase substitutions
documented in `results/task6-instruction-diff.md` — no independent instruction rewriting.

## Exact instructions text used

> "You are the CEIS Procedures Agent. Search and answer ONLY using the CEIS-Pilot-Knowledge
> Markdown procedure pages. Search strategy: (1) Search the CEISPilotKnowledge/pages folder for
> .md pages matching the user's question, (2) Extract detailed step-by-step procedures from the
> .md pages found, (3) Always cite the specific .md page name, (4) If the answer is not found in
> the .md pages, state clearly that the procedure is not documented. Do NOT search images or other
> sources. Reply in a formal, professional tone."

## Smoke-test result (`NORM-01`'s prompt, via direct `.agent`-file access)

**Prompt:** "What are the steps to initiate a new file in CEIS?"

**Result:** well-grounded, detailed 4-step procedure (File Identification → Save → Parties/Roles →
Initiating Document), correctly citing **3 real `.md` sources**:
`initiate-a-file--51d1f554.md`, `parties--62236e0e.md`, `documents-data-entry--e87c1624.md`. No
`.aspx` citations, no fabrication, no out-of-scope content. Directly comparable in depth/quality to
the `.aspx` control agent's answer to the same question (Task 4/baseline-verification results).

**Disposition:** PASS. This agent is confirmed working and ready for Task 7's full 7-case run.
