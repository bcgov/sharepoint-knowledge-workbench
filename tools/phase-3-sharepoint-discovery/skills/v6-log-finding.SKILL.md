---
name: test-do-not-use-log-finding
description: |-
  Phase 3.0 capability-discovery test skill. Tests whether a native SharePoint skill invoked
  by a Copilot agent can perform a real WRITE action (creating a SharePoint list item), not
  just answer questions from grounded content — per the research priority "verify how custom
  SharePoint agents discover or invoke native skills" and "create review follow-up items"
  pattern documented in docs/research/field-note-sharepoint-agentassets-review-manual-topics-skill.md.

  Use when the user says:
    - "log a finding"
    - "log this to the discovery log"
    - "record this test finding"
---
# Log a Discovery Finding (Write-Action Test)

## When to use
Use this skill when the user asks to "log a finding", "log this to the discovery log", or
"record this test finding". This is a Phase 3.0 capability-discovery test skill only — it writes
to a test list, `TEST-DO-NOT-USE-Discovery-Log`, on the current site.

## Inputs
- A short title for the finding (from the user's request, or ask if not provided).
- Notes describing the finding (from the user's request, or ask if not provided).
- The source file/document this finding relates to, if any.

## Steps
1. Identify the title, notes, and source file from the user's request. If the title or notes are
   missing, ask the user to provide them rather than inventing content.
2. Confirm the list `TEST-DO-NOT-USE-Discovery-Log` exists on this site.
3. Create ONE new item in `TEST-DO-NOT-USE-Discovery-Log` with:
   - Title: the finding title
   - Notes: the finding notes
   - SourceFile: the source file name, or "NONE" if not applicable
4. Report back to the user whether the item was created successfully, and show the values used.
   If item creation fails or is not possible, say so plainly — do not claim success without
   confirming it.

## Output format
Report using this structure:

- **Action:** Logged finding to TEST-DO-NOT-USE-Discovery-Log
- **Title:** <title used>
- **Notes:** <notes used>
- **Source file:** <source file or NONE>
- **Status:** <Created | Failed — reason>
