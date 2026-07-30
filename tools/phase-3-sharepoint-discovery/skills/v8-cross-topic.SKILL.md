---
name: test-do-not-use-manual-cross-topic
description: |-
  Phase 3.0 capability-discovery test skill. Tests multi-document synthesis grounding across
  several real CEIS manual topics (not a single synthetic test file), to see whether a
  SharePoint Copilot agent can correctly combine and cite information spanning multiple
  source files in one answer.

  Use when the user says:
    - "cross-reference the manual topics"
    - "use the cross-topic test format"
---
# Manual Cross-Topic Synthesis Test

## When to use
Use this skill when the user asks a question that likely requires combining information from
more than one CEIS manual topic file (e.g. warrants, protection orders, file access) and
explicitly says "use the cross-topic test format". This is a Phase 3.0 capability-discovery
test skill only.

## Steps
1. Identify which of the uploaded CEIS manual topic files are relevant to the question.
2. Answer using information combined from ALL relevant files — do not limit yourself to just
   one file if the question spans multiple topics.
3. Explicitly name every source file used in your answer.
4. If the topics don't actually connect (no real overlap), say so honestly rather than forcing
   a connection.

## Output format
- **Answer:** <synthesized answer combining the relevant topics>
- **Topics used:** <comma-separated list of every source file referenced>
- **Cross-topic relationship found:** <Yes/No/Partial — briefly explain>
