---
name: test-do-not-use-list-libraries
description: |-
  Phase 3.0 capability-discovery test skill. Lists all document libraries in the current
  SharePoint site and formats the result using a strict external template stored in this
  skill's assets/ subfolder, to test (a) whether a skill can perform a real enumeration action
  (not just answer from grounded file content) and (b) whether a template file placed in an
  assets/ subfolder is retrievable, versus a flat sibling file (see v4 variant for comparison).

  Use when the user says:
    - "list all document libraries"
    - "use the library inventory test format"
    - "discovery template v5"
---
# List Document Libraries — Strict Template Test (assets/ subfolder)

## When to use
Use this skill when the user asks to list document libraries/lists on the current SharePoint
site using "the library inventory test format" or "discovery template v5". This is a Phase 3.0
capability-discovery test skill only.

## Inputs
- The current SharePoint site context (no user-supplied inputs required).

## Steps
1. Enumerate the document libraries in the current site (title, item count, and whether
   versioning is enabled, if that information is available to you).
2. Retrieve the file `assets/library-inventory-template.txt` in this skill's own folder
   (`AgentAssets/Skills/test-do-not-use-list-libraries/assets/library-inventory-template.txt`).
3. Format your ENTIRE response using exactly the structure found in that template file,
   replacing only the placeholder values. Do not add commentary, headings, or citations before
   or after it. If you cannot access the template file, say so explicitly rather than inventing
   a format.

## Output format
Defined externally in `assets/library-inventory-template.txt` in this skill's own folder — read
that file and follow it exactly. Do not paraphrase or reformat it.
