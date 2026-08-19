---
name: test-do-not-use-strict-format-v3-json
description: |-
  Phase 3.0 capability-discovery test skill, variant 3 (JSON). Tests whether requesting a
  well-known structured format (strict JSON) is followed more reliably than a custom ASCII
  delimiter template.

  Use when the user says:
    - "use the json test format"
    - "answer using discovery template v3"
---
# Strict Format Discovery Test — Variant 3 (JSON)

## When to use
Use this skill whenever the user asks a question and explicitly requests "the json test format"
or "discovery template v3". This is a Phase 3.0 capability-discovery test skill only.

## Steps
1. Answer the user's question using only retrieved/grounded content.
2. Respond with ONLY a single valid JSON object matching the schema below. No Markdown, no code
   fences, no citations, no extra text before or after the JSON object.

## Output format
Respond with exactly one JSON object, and nothing else, matching this schema:

```json
{
  "question": "<restate the user's question verbatim>",
  "answer": "<your answer, one sentence only>",
  "confidence": "HIGH|MEDIUM|LOW",
  "source_file": "<exact filename grounded on, or null>"
}
```

Do not wrap the JSON in a code fence. Do not add any text before the opening `{` or after the
closing `}`.
