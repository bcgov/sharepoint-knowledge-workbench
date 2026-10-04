# Field Note — Creating a Native SharePoint Skill in the `AgentAssets` Library

**Purpose:** Record the observed creation pattern, storage requirement, generated `SKILL.md`, and practical implications of creating a native Copilot in SharePoint skill.  
**Status:** Empirical implementation note based on a successful SharePoint test. Validate behaviour in each target tenant because preview implementation details may differ from published documentation or change over time.

## 1. Key Finding

In the tested SharePoint environment, the required document library name was:

```text
AgentAssets
```

The library name used **no space**.

After the `AgentAssets` document library existed, Copilot in SharePoint created a native skill definition as Markdown.

This observed result is important because Microsoft documentation and interface descriptions may refer generically to an **Agent Assets** library. For deployment and automation, do not infer the physical library name from the display label. Verify the actual library title, URL, and internal identity in the target site.

Recommended verification fields:

```text
Display title
Internal/library name
Server-relative URL
Library ID
Content types
Permissions
Versioning
Retention and sensitivity settings
```

## 2. Observed Creation Pattern

The successful test followed this general pattern:

```text
Create SharePoint document library named AgentAssets
→ open Copilot in SharePoint
→ describe the reusable workflow in natural language
→ review the generated skill
→ save the skill
→ inspect the generated Markdown definition
```

The generated skill was named:

```text
review-manual-topics
```

Its purpose was to:

- review selected manual topics;
- determine required metadata;
- identify missing, empty, ambiguous, or inapplicable metadata;
- summarize gaps;
- create unresolved follow-up items in a SharePoint `Content Review` list;
- avoid duplicate review items;
- report concise results.

## 3. Generated Native SharePoint Skill

The following is the generated definition, cleaned only to remove HTML line-break artifacts introduced when copying it from the interface.

```markdown
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
```

## 4. What This Proves

The test provides practical evidence that a native SharePoint skill can be represented as a structured Markdown file containing:

- YAML front matter;
- a stable skill name;
- a natural-language description;
- example trigger phrases;
- use and non-use guidance;
- inputs;
- ordered workflow steps;
- native SharePoint list and library operations;
- error-handling instructions;
- an expected output format.

The generated definition resembles repository-based skills structurally, but its execution environment is different.

```text
Repository skill
→ may invoke custom scripts, tools, tests, Git, and approved APIs

Native SharePoint skill
→ interpreted by Copilot in SharePoint and limited to supported native actions
```

## 5. Why This Skill Is a Useful Workbench Output

This skill is a strong example of the proposed compilation model:

```text
Content-management requirement
→ workbench designs a bounded workflow
→ workbench generates a native-compatible skill specification
→ human reviews it
→ skill is saved in AgentAssets
→ Copilot in SharePoint runs it within the user's permissions
→ results are evaluated and governed
```

The workbench could generate the following package before deployment:

```text
sharepoint-native-skills/
  review-manual-topics/
    SKILL.md
    governance-metadata.json
    permission-assumptions.md
    evaluation-cases.md
    deployment-manifest.json
    source-specification.md
```

The generated `SKILL.md` is the SharePoint runtime artifact. The additional files remain workbench evidence and governance artifacts unless a separate SharePoint storage model is approved.

## 6. SharePoint Storage Model

Based on the observed result, the target site should contain:

```text
SharePoint site
└── AgentAssets
    └── Skills
        └── review-manual-topics
            └── SKILL.md
```

Before treating this as a reusable deployment convention, verify the actual folder and file location created in the target site.

Record:

- site URL;
- `AgentAssets` library ID;
- server-relative path;
- generated skill folder;
- generated file name;
- file version;
- permissions;
- author and modifier;
- retention or sensitivity settings;
- audit events.

## 7. Accessibility to Copilot in SharePoint and SharePoint Agents

The observed skill is native to Copilot in SharePoint on the site where it is stored.

The expected operating model is:

```text
User opens Copilot in SharePoint
→ user request matches the skill description or trigger phrases
→ Copilot loads the native skill
→ skill runs supported SharePoint actions
→ actions remain constrained by the user's permissions
```

A native skill and a SharePoint agent are separate artifacts.

```text
Native SharePoint skill
= repeatable workflow

SharePoint agent
= purpose-specific conversational experience grounded in selected sources
```

Do not assume that creating the skill automatically attaches it to every custom SharePoint agent. Validate in the target site:

- whether the site-level Copilot experience automatically discovers the skill;
- whether a custom SharePoint agent can invoke the skill;
- whether skill availability changes with agent scope;
- whether the user must explicitly name the skill;
- whether the skill works from a site, page, and document-library context;
- whether sharing an agent also makes the skill usable by the recipient;
- whether AgentAssets permissions affect discovery or execution.

This test confirmed skill creation and generated content. It did not, by itself, prove every agent-to-skill invocation scenario.

## 8. Licensing and Permission Questions to Record

Before broader use, record the actual tenant result for:

- Microsoft 365 Copilot licensing of skill authors;
- Microsoft 365 Copilot licensing or other entitlement of skill users;
- Copilot in SharePoint availability for the site;
- tenant or selected-site inclusion settings;
- Restricted Content Discovery settings;
- permission required to create `AgentAssets`;
- permission required to author the skill;
- permission required to run the skill;
- permission required to create the `Content Review` list;
- permission required to add review items;
- whether Pay-As-You-Go SharePoint-agent access changes native-skill availability.

Do not assume licensing for SharePoint agents and licensing for the Copilot in SharePoint preview are identical.

## 9. Important Governance Risks in the Generated Skill

The generated workflow contains several actions that deserve explicit review.

### 9.1 Automatic List Creation

The skill says to create the `Content Review` list if it does not exist.

Questions:

- Should a review skill be allowed to create site structure?
- Should list creation require separate confirmation?
- Should the list be provisioned in advance from an approved schema?
- Who owns the resulting list?
- What retention and sensitivity settings should apply?

Recommended production pattern:

```text
Design and provision Content Review separately
→ native skill checks for the approved list
→ if unavailable, stop and report the missing dependency
```

This is safer than allowing each execution to invent or recreate governance structure.

### 9.2 Schema-Derived Required Fields

The skill derives required metadata from the source library schema unless the user supplies a list.

Questions:

- Are all technically required columns valid business requirements?
- Are conditional requirements represented?
- Are content-type-specific requirements handled?
- Are hidden, calculated, inherited, or workflow-controlled fields excluded correctly?

A future version should use an approved metadata profile rather than relying only on the SharePoint `Required` flag.

### 9.3 Duplicate Detection

The skill says to avoid duplicate unresolved review items.

A production design should define a deterministic duplicate key, such as:

```text
Source site ID
+ Source list/library ID
+ Source item ID
+ Normalized missing-field set
+ Unresolved status
```

Without a defined key, duplicate detection may be inconsistent.

### 9.4 Default Priority

The skill defaults unresolved items to `Medium` priority.

That default is convenient but is not grounded in a documented risk model. A safer pattern may be:

```text
Priority = Unassessed
```

or a deterministic rule based on approved metadata criticality.

### 9.5 `Won't Fix` Status

The generated choice is `Won't Fix`.

For regulated use, consider whether a more formal value is preferable:

```text
Accepted exception
Not applicable
Deferred
Superseded
Resolved
```

An exception status should capture approver, reason, and decision date.

### 9.6 Content Inspection

The skill allows retrieval of file content when needed.

Confirm:

- which file types are supported;
- whether content inspection respects sensitivity and permissions;
- whether the output might expose protected content;
- whether only metadata should be reported for some classifications.

## 10. Recommended Hardened Version

Before deploying beyond a test site, consider these changes:

1. Require the `Content Review` list to be pre-provisioned from an approved schema.
2. Stop if the approved list is missing rather than creating it automatically.
3. Use a controlled metadata profile by content type.
4. Record source site, list ID, item ID, stable topic ID, and content type.
5. Use a deterministic duplicate key.
6. Use `Unassessed` priority unless a rule or user sets priority.
7. Replace informal exception states with an approved disposition vocabulary.
8. Require explicit confirmation before creating review items for a large selection.
9. Limit reported content to the minimum required for review.
10. Record skill version in every generated review item.
11. Add evaluation cases for missing selection, inaccessible items, mixed content types, conditional metadata, duplicate items, and partial failures.
12. Record a clear completion state when only part of the selected set was processed.

## 11. Proposed Evaluation Cases

### Normal Cases

- one complete manual topic;
- one topic with one missing required field;
- multiple topics with different missing fields;
- user-supplied required-field list;
- existing approved `Content Review` list.

### Boundary Cases

- no selection;
- mixed files and list items;
- different content types with different metadata profiles;
- empty versus whitespace-only text fields;
- ambiguous person or taxonomy values;
- field marked required but controlled by workflow;
- inaccessible selected item;
- deleted item during execution.

### Duplicate Cases

- identical unresolved review item exists;
- previous item is resolved;
- same topic has a different missing-field set;
- same item ID appears in a different library or site.

### Permission Cases

- user can read source but cannot create review items;
- user can add review items but cannot create the list;
- user cannot read one selected topic;
- AgentAssets skill is visible but a required target action is unauthorized.

### Safety Cases

- protected content should not be quoted in the review summary;
- sensitive metadata should not be copied into a broadly visible list;
- skill must not invent owner, due date, classification, or missing values;
- partial failure must be disclosed.

## 12. Evidence to Capture From Future Tests

For each test, capture:

```text
Tenant and site
Date tested
Copilot in SharePoint availability
User licence/entitlement
User permissions
AgentAssets library identity and path
Skill file path and version
Input selection
Expected result
Actual result
Lists or items created
Duplicate behaviour
Permission behaviour
Audit evidence
Reviewer disposition
Known limitation
```

## 13. Architecture Conclusion

The successful creation of `review-manual-topics` demonstrates the practical deployment target envisioned by the workbench:

```text
GitHub Copilot / VS Code studio
→ design and validate workflow
→ generate target-native SKILL.md
→ deploy or recreate in AgentAssets
→ run through Copilot in SharePoint
→ evaluate and govern the result
```

The important field correction is:

```text
Observed library name: AgentAssets
No space
```

Treat the observed internal name as tenant-tested evidence. Continue distinguishing it from human-readable references such as “Agent Assets.”

The generated skill is a strong proof of concept, but production hardening should address list provisioning, metadata authority, duplicate identity, exception vocabulary, permissions, sensitivity, partial failure, and evaluation.

## 14. Dated Follow-Up — Phase 3.0 Controlled Tenant Discovery Addendum (2026-07-30)

During Phase 3.0 controlled tenant discovery, further empirical tests were conducted on native SharePoint skills and custom `.agent` files in the tested development tenant:

- `CONFIRMED_TENANT_OBSERVATION`: Generic PnP file upload of `SKILL.md` beneath `AgentAssets/Skills/<skill-name>/SKILL.md` succeeded and was discovered by the same-site custom agent through matching trigger wording.
- `CONFIRMED_TENANT_OBSERVATION`: The tested custom agent `.agent` JSON did not require an explicit skill reference to discover the same-site native skill.
- `TENANT_OBSERVED_LIMITATION`: Exact formatting instructions (e.g. `## Output format` delimiters) in `SKILL.md` were unreliable when executed by the tested custom agent.
- `TENANT_OBSERVED_LIMITATION`: JSON output requests were followed more closely than arbitrary delimiter templates, but exact schema compliance was not guaranteed.
- `NOT_SUPPORTED_IN_TESTED_CONFIGURATION`: List-write and item-creation instructions executed through the tested custom-agent chat pane declined write operations, and independent PnP verification confirmed no list item was created.
- `INCONCLUSIVE`: Sibling template file reading beneath supporting-resource folders was not proven to be read literally.
- `INCONCLUSIVE`: Behavior of ready-made/default SharePoint agents, owner/editor/viewer permission boundaries, skill collision across overlapping triggers, and enterprise supportability of manual file uploads remain unverified and open for further testing.

