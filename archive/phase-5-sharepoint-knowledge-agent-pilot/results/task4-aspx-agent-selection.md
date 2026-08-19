# Task 4 Results — `.aspx` Agent Selection

**Date:** 2026-08-02. **Method:** direct `.agent`-file access (path 1) exclusively — see
`docs/research/field-note-ready-made-copilot-agent-launch-by-name.md` for why the generic
ready-made Copilot's "launch by name" path (path 2) was ruled out as unreliable before this test.

## All 5 agents confirmed working via direct access

Every one of the 5 existing `.agent` files opens a working chat pane when accessed directly, and
every one produces a real, well-grounded answer to the `NORM-01` smoke-test prompt ("What are the
steps to initiate a new file in CEIS?") — specific procedural steps, correct citations to real
CEIS `.aspx` topic pages, no hallucination.

| Agent | Welcome prompt identity | `NORM-01` result | Citations |
|---|---|---|---|
| `CEIS-Pilot-Knowledge-Agent` | Generic ("Ask a question...") | Well-grounded, 4-step procedure | `initiate-a-file`, +3 |
| `CEIS-Pilot-Knowledge-Agent-Corrected` | Generic (identical to above) | Well-grounded, 5-step procedure with cross-topic synthesis (roles/documents/appearances) | `initiate-a-file`, `file-details`, +5 (7 total) |
| `CEIS-ASPX-Only-Test` | Distinct ("I can answer questions about CEIS procedures and processes from the available knowledge pages") | Well-grounded, 5-step procedure | `initiate-a-file`, `file-details`, `parties`, `documents-data-entry` (4 total) |
| `CEISPilotKnowledgePages-manuallycreated` | Generic (identical to first two) | Well-grounded, 4-step procedure + related-topics section | `file-details`, `initiate-a-file`, +3 (5 total) |
| `CEIS-Topic-Reviewer-with-Skills` | Distinct ("I can review and analyze CEIS procedures. Ask me to review a specific topic") | Well-grounded, 4-step procedure | `initiate-a-file`, `file-details`, +2 (4 total) |

Each agent's welcome-prompt identity differing (or matching) exactly along the lines predicted by
its instructions text (the two "-Corrected"/original/manually-created agents share the same
generic identity; `CEIS-ASPX-Only-Test` and `CEIS-Topic-Reviewer-with-Skills` each have their own
distinct identity) is itself confirming evidence that direct `.agent`-file access really does apply
each file's own distinct instructions — consistent with the path-1-vs-path-2 finding in the field
note above.

## Baseline chosen: `CEIS-ASPX-Only-Test`

**Reason:** beyond passing `NORM-01` cleanly, this is the only one of the 5 whose refusal behavior
was explicitly tested and confirmed correct. After tightening its instructions (see the field
note's "Follow-up confirmation" section for the exact text), it was asked a deliberately
out-of-scope question ("What is the maximum sentence length for a criminal assault charge in BC?")
and correctly refused — stating plainly that the information "is not documented in the available
CEIS `.aspx` procedure pages," citing only real CEIS content (`data-capture-standards`), not
general knowledge or unrelated site content. None of the other 4 agents' refusal behavior was
tested this round. Its stricter, explicit folder/extension-scoped instructions make `NEG-01`/
`NEG-02` (Task 3's negative-category cases) more discriminating than the other agents' looser
wording would.

**Confirmed instructions text (used verbatim for Task 7's `.aspx`-side test runs, and as the
template Task 6 mirrors for the `.md`-grounded comparison agent):**

> "You are the CEIS Procedures Agent. You must answer ONLY using content from `.aspx` files
> located in the SharePoint folder `/SitePages/CEISPilotKnowledgePages`. Do not use any other
> folder, site, image, or general knowledge as a source. If the requested information is not found
> in a `.aspx` file in that exact folder, respond only with: 'This procedure is not documented in
> the CEIS Manual.' Do not answer any question unrelated to CEIS procedures, even if you know the
> answer from general knowledge. Never cite or reference content outside
> `/SitePages/CEISPilotKnowledgePages`."
