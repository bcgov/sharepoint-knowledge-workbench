# Task 6 — Instruction Diff (control vs. comparison)

Proves the only intended differences between the `.aspx` control agent and the `.md` comparison
agent are representation/knowledge-source references — everything else (purpose, search sequence,
citation requirement, unsupported-answer behavior, tone instruction) is identical.

## Control — `CEIS-ASPX-Only-Test` (`AUTHORITATIVE_LIVE_BASELINE`, unmodified)

> You are the CEIS Procedures Agent. Search and answer ONLY using the **CEISPilotKnowledgePages
> .aspx procedure pages**. Search strategy: (1) Search the **CEISPilotKnowledgePages folder** for
> **.aspx pages** matching the user's question, (2) Extract detailed step-by-step procedures from
> the **.aspx pages** found, (3) Always cite the specific **.aspx page** name, (4) If the answer is
> not found in the **.aspx pages**, state clearly that the procedure is not documented. Do NOT
> search images or other sources. Reply in a formal, professional tone.

## Comparison — `CEIS-Markdown-Comparison-Agent` (new)

> You are the CEIS Procedures Agent. Search and answer ONLY using the **CEIS-Pilot-Knowledge
> Markdown procedure pages**. Search strategy: (1) Search the **CEISPilotKnowledge/pages folder**
> for **.md pages** matching the user's question, (2) Extract detailed step-by-step procedures from
> the **.md pages** found, (3) Always cite the specific **.md page** name, (4) If the answer is not
> found in the **.md pages**, state clearly that the procedure is not documented. Do NOT search
> images or other sources. Reply in a formal, professional tone.

## Exact substitutions made (4 source-related phrases only)

| Control | Comparison |
|---|---|
| `CEISPilotKnowledgePages .aspx procedure pages` | `CEIS-Pilot-Knowledge Markdown procedure pages` |
| `CEISPilotKnowledgePages folder` | `CEISPilotKnowledge/pages folder` |
| `.aspx pages` (×3 occurrences: search-match, extract-from, not-found) | `.md pages` (×3) |
| `.aspx page` (citation instance, singular) | `.md page` |

## Confirmed unchanged (word-for-word identical in both)

- Opening identity: "You are the CEIS Procedures Agent."
- Search-strategy numbering and structure (4 numbered steps, same order)
- Citation requirement: "Always cite the specific [...] page name"
- Unsupported-answer behavior: "state clearly that the procedure is not documented"
- Non-source-related restriction: "Do NOT search images or other sources."
- Tone instruction: "Reply in a formal, professional tone."
- No `discourage_model_knowledge` setting present in either agent's JSON (neither the control nor
  the new comparison agent's `.agent` file sets this field — confirmed absent in both, not silently
  added or removed by this change).
- Conversation starters: both agents use the same generic 3-item starter list
  (`"Summarize recent items"`, `"Tell me more about..."`, `"How can you help me?"`) — the control's
  actual starters were not customized beyond the default, so the comparison agent matches by using
  the same default, not by copying a customization.
