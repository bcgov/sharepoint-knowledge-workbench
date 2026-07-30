---
name: test-do-not-use-strict-format-v2-fewshot
description: |-
  Phase 3.0 capability-discovery test skill, variant 2 (few-shot). Tests whether giving the
  model a fully filled-in EXAMPLE output (not just abstract placeholders) improves exact
  output-template compliance versus variant 1.

  Use when the user says:
    - "use the fewshot test format"
    - "answer using discovery template v2"
---
# Strict Format Discovery Test — Variant 2 (Few-Shot)

## When to use
Use this skill whenever the user asks a question and explicitly requests "the fewshot test
format" or "discovery template v2". This is a Phase 3.0 capability-discovery test skill only.

## Steps
1. Answer the user's question using only retrieved/grounded content.
2. Copy the EXACT structure of the example below, character for character, only replacing the
   VALUE text — do not change any label, punctuation, spacing, or line order. Do not add any
   commentary, heading, or citation formatting before or after it.

## Output format
This is a real, complete, filled-in EXAMPLE of a correct response to a DIFFERENT question. Match
this exact structure for your own answer, substituting only the values:

```
>>> DISCOVERY-TEMPLATE-START <<<
QUESTION:: What color is the sky?
ANSWER:: The sky is blue during a clear day.
CONFIDENCE:: HIGH
SOURCE-FILE:: NONE
>>> DISCOVERY-TEMPLATE-END <<<
```

Your response must look exactly like that example above, but with your own question/answer
values substituted in place of "What color is the sky?" etc. Do not use bullet points, headings,
bold text, or citations/footnote markers anywhere in your response.
