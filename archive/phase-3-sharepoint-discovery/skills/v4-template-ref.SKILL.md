---
name: test-do-not-use-strict-format-v4-template-ref
description: |-
  Phase 3.0 capability-discovery test skill, variant 4 (external template reference). Tests
  whether a skill can reliably follow an output template stored in a SEPARATE sibling file
  (output-template.txt) rather than embedded inline in SKILL.md.

  Use when the user says:
    - "use the template-ref test format"
    - "answer using discovery template v4"
---
# Strict Format Discovery Test — Variant 4 (External Template Reference)

## When to use
Use this skill whenever the user asks a question and explicitly requests "the template-ref test
format" or "discovery template v4". This is a Phase 3.0 capability-discovery test skill only.

## Steps
1. Answer the user's question using only retrieved/grounded content.
2. Retrieve the file `output-template.txt`, located in this same skill's folder
   (`AgentAssets/Skills/test-do-not-use-strict-format-v4-template-ref/output-template.txt`).
3. Format your ENTIRE response using exactly the structure found in that file, replacing only the
   placeholder text in angle brackets with your actual values. Do not add commentary, headings,
   or citations before or after it.

## Output format
Defined externally in the sibling file `output-template.txt` in this skill's own folder — read
that file and follow it exactly. Do not paraphrase or reformat it.
