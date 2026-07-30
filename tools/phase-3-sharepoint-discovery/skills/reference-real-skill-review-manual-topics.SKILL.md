---
name: review-manual-topics
description: |-
  Reviews selected manual topics, checks required metadata, summarizes gaps, and records unresolved review items in a Content Review list.

  Use when the user says:
    - "review selected manual topics"
    - "check manual topic metadata"
    - "add missing manual info to Content Review"
    - "find missing metadata in these manual topics"
    - "create review items for incomplete manual content"
---
# Review Manual Topics

## When to use
Use this skill when the user wants selected manual topics, pages, files, or list items reviewed for required metadata completeness, with unresolved gaps summarized and added to a SharePoint **Content Review** list.

Do not use this skill for general document summaries unless the user asks to check metadata or create review follow-up items.

## Inputs
- Selected manual topics, files, pages, or list items from the current SharePoint context.
- Required metadata fields. Prefer required fields from the source list/library schema. If the user provides a fixed required-field list, use that instead.
- Target review list name: default to **Content Review** unless the user names another list.
- Optional reviewer, due date, priority, topic owner, or notes supplied by the user.

## Steps
1. Identify the selected topics.
   - Use the current SharePoint selection or folder/library context where available.
   - If no selected items can be determined, ask the user to select topics or provide item names/links.

2. Determine required metadata.
   - Retrieve the source list or library schema for the selected items.
   - Treat fields marked as required as required metadata.
   - Exclude system-only fields that users cannot reasonably maintain, such as ID, GUID, version, modified timestamp, created timestamp, path, and internal content infrastructure fields.
   - If the user supplied a required-field list, use it instead of the schema-derived list.

3. Inspect each selected topic.
   - Retrieve item properties and, when needed, file contents to understand whether metadata values are present.
   - For each required field, classify it as Present, Missing, Empty, Ambiguous, or Not Applicable.
   - Do not invent metadata values. If a value is unclear, mark it Ambiguous.

4. Summarize missing information.
   - Group gaps by topic.
   - Include the field name, current value if any, why it needs review, and a short recommended action.
   - Separate resolved/no-gap topics from unresolved topics.

5. Ensure the review list exists.
   - Look for a SharePoint list named **Content Review** in the current site unless the user named another list.
   - If it does not exist, create it with practical columns:
     - Title: single line of text
     - Topic: hyperlink or text
     - Source Item ID: number or text
     - Source Library/List: single line of text
     - Missing Metadata: multiple lines of text
     - Recommended Action: multiple lines of text
     - Review Status: choice values New, In Progress, Resolved, Won't Fix
     - Priority: choice values Low, Medium, High
     - Owner: person or group, optional
     - Due Date: date/time, optional

6. Add unresolved items to Content Review.
   - Create one review item per topic with unresolved required metadata gaps.
   - Use a clear title, such as `Review metadata: <topic title>`.
   - Set Review Status to `New` unless the user specifies another status.
   - Set Priority to `Medium` unless the user specifies another priority.
   - Include links or identifiers back to the source topic whenever available.
   - Avoid duplicate entries when a matching unresolved review item already exists for the same source item and missing metadata.

7. Report results.
   - State how many topics were checked.
   - State how many had missing or ambiguous required metadata.
   - State how many Content Review items were created or skipped as duplicates.
   - If any tool fails or returns empty, say so plainly and don't invent content.

## Output format
Provide a concise summary:

- **Checked:** <number> topics
- **Complete:** <number> topics
- **Needs review:** <number> topics
- **Content Review items added:** <number>
- **Skipped duplicates:** <number>

Then include a compact table:

| Topic | Missing or ambiguous metadata | Recommended action | Review item |
|---|---|---|---|
| <topic title> | <fields> | <action> | <created/skipped/link if available> |

If no unresolved gaps are found, say that no Content Review items were needed.