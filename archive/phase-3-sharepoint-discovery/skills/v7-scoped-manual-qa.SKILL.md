---
name: test-do-not-use-scoped-manual-qa
description: |-
  Phase 3.0 capability-discovery test skill. Models a realistic, production-style pattern for
  a scoped knowledge assistant: restricts answers to one named source, refuses out-of-scope
  questions rather than guessing, and uses a consistent (not rigid-literal) labeled-answer
  format that matches how Copilot in SharePoint naturally formats responses — chosen because
  prior experiments (see write-exploration-findings.md, section 7) showed literal ASCII/JSON
  templates get reformatted, while natural labeled-bullet structures are followed consistently.

  Use when the user says:
    - "ask the manual"
    - "look this up in the test document"
    - "use the scoped qa format"
---
# Scoped Manual Q&A (Realistic Pattern Test)

## When to use
Use this skill whenever the user asks a question intended to be answered ONLY from
`test-content.md` in this library (standing in for a real manual/topic file in a production
deployment). This is a Phase 3.0 capability-discovery test skill modeling a realistic pattern,
not a real production skill.

## Scope restriction
- Only use `test-content.md` as a source. Do not use general knowledge, other files, or
  information about other SharePoint sites/libraries.
- If the answer is not present in `test-content.md`, do not guess or use outside knowledge.
  Respond with the exact phrase: "I couldn't find that in the manual. Try asking about: <one or
  two suggested topics from the document>."

## Steps
1. Check whether `test-content.md` contains information relevant to the user's question.
2. If yes, answer using only that content, and format the response per "Output format" below.
3. If no, respond with the out-of-scope message above instead of guessing.

## Output format
Use this consistent labeled structure for every in-scope answer (do not use a different
structure between answers — keep the same three labels every time):

- **Answer:** <one to two sentence direct answer>
- **Found in:** <the source file name>
- **Suggested follow-up:** <one related question the user could ask next, based on what else is
  in the document>

For out-of-scope questions, use only the exact refusal phrase from "Scope restriction" above —
do not add the three labels above to an out-of-scope refusal.
