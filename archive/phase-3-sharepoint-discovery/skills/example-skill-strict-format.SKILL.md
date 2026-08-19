---
name: test-do-not-use-strict-format
description: |-
  Phase 3.0 capability-discovery test skill. Answers any question using a rigid, unusual
  output template, to test whether a SharePoint Copilot agent will exactly follow a
  skill-defined output format rather than its own default answer style.

  Use when the user says:
    - "use the strict test format"
    - "answer using the discovery test template"
---
# Strict Format Discovery Test

## When to use
Use this skill whenever the user asks a question and explicitly requests "the strict test
format" or "the discovery test template". This is a Phase 3.0 capability-discovery test skill
only — never use it for real content.

## Steps
1. Answer the user's question using only the retrieved/grounded content available.
2. Format the entire response using EXACTLY the template in "Output format" below — do not
   add, omit, or reorder any of the labeled lines.

## Output format
Your ENTIRE response must be formatted exactly as follows, with no extra commentary before or
after it:

```
>>> DISCOVERY-TEMPLATE-START <<<
QUESTION:: <restate the user's question verbatim>
ANSWER:: <your answer, one sentence only>
CONFIDENCE:: <one of: HIGH | MEDIUM | LOW>
SOURCE-FILE:: <the exact filename you grounded this answer on, or NONE>
>>> DISCOVERY-TEMPLATE-END <<<
```

Do not use bullet points, headings, or any other Markdown formatting inside the template.
