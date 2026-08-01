# Task 9 Metadata Visibility Protocol — Testing Framework

**Date:** 2026-08-01  
**Phase:** Phase 4 - Native SharePoint Skills Pilot  
**Task:** 9 - Execute Metadata Visibility Empirical Probe  
**Status:** EXECUTING

---

## Ground Truth (Verified via Tenant Query)

**Selected Topic:** DATA CAPTURE STANDARDS  
**Item ID:** 182  
**Library:** Site Pages (ID: 1a4a1eda-a2fe-4c43-8d48-4a841f07b253)

### Actual SharePoint Field Values

| Field | Value | Present | Type |
|-------|-------|---------|------|
| TopicID | NULL | ✗ NO | Not present |
| PublicationOrder | 0 | ✓ YES | Number |
| TopicContentSHA256 | c72e3ca522cff7a91ff7acbe4026ccc298c06f83beb58217e47ec92f96f5e1aa | ✓ YES | Text (SHA-256) |
| Status | NULL | ✗ NO | Not present |
| ReviewDate | NULL | ✗ NO | Not present |
| TransitionAction | NULL | ✗ NO | Not present |
| TransitionTarget | NULL | ✗ NO | Not present |

---

## Testing Strategy

For each of the 7 metadata fields, test whether the deployed review-manual-topics skill can access them as structured metadata.

### Test Design Principles

1. **Unambiguous prompts:** Each prompt identifies the topic unambiguously without exposing the expected field value
2. **One field per prompt:** Test field visibility in isolation
3. **No content hints:** Prompts don't suggest what the field might contain
4. **Read-only interaction:** No modifications to the topic
5. **Human review required:** Determine if returned values are structured metadata or inferred from content

---

## Test Prompts (to be executed via Copilot + review-manual-topics skill)

### Prompt 1: TopicID Field

```
Review the DATA CAPTURE STANDARDS topic. 
Check whether this topic has a TopicID field value assigned in its metadata.
If a TopicID exists, report the exact value.
If no TopicID is assigned, state that clearly.
Do not infer or generate a TopicID.
```

**Expected ground truth:** TopicID is NULL (not assigned)  
**Evidence to capture:** Agent's exact response text

---

### Prompt 2: PublicationOrder Field

```
Review the DATA CAPTURE STANDARDS topic.
What is the PublicationOrder metadata field value for this topic?
Return only the numeric value if present, or state if not assigned.
```

**Expected ground truth:** PublicationOrder = 0  
**Evidence to capture:** Agent's response

---

### Prompt 3: TopicContentSHA256 Field

```
Review the DATA CAPTURE STANDARDS topic.
Does this topic have a TopicContentSHA256 field in its metadata?
If yes, report the exact SHA-256 hash value.
If no, state that.
Do not calculate or derive a content hash.
```

**Expected ground truth:** TopicContentSHA256 = c72e3ca522cff7a91ff7acbe4026ccc298c06f83beb58217e47ec92f96f5e1aa  
**Evidence to capture:** Agent's response

---

### Prompt 4: Status Field

```
Review the DATA CAPTURE STANDARDS topic.
Check whether the Status metadata field is assigned.
Report the Status value if present, or state that no Status is assigned.
```

**Expected ground truth:** Status is NULL (not assigned)  
**Evidence to capture:** Agent's response

---

### Prompt 5: ReviewDate Field

```
Review the DATA CAPTURE STANDARDS topic.
What is the ReviewDate metadata field value?
Return the date if assigned, or state if not assigned.
Do not infer a date.
```

**Expected ground truth:** ReviewDate is NULL (not assigned)  
**Evidence to capture:** Agent's response

---

### Prompt 6: TransitionAction Field

```
Review the DATA CAPTURE STANDARDS topic.
Is there a TransitionAction metadata field assigned to this topic?
If yes, report the value.
If no, state that.
```

**Expected ground truth:** TransitionAction is NULL (not assigned)  
**Evidence to capture:** Agent's response

---

### Prompt 7: TransitionTarget Field

```
Review the DATA CAPTURE STANDARDS topic.
Check for a TransitionTarget metadata field.
Report its value if present, or state if not assigned.
```

**Expected ground truth:** TransitionTarget is NULL (not assigned)  
**Evidence to capture:** Agent's response

---

## Evidence Capture Template

For each prompt, record:

```
Prompt: [Number and field name]
Ground Truth: [Expected value from tenant query]
Agent Response: [Exact text returned by skill]
Citation: [Source cited by agent, if any]
Classification: [See below]
Notes: [Observer comments]
```

---

## Classification Framework

Assign exactly ONE classification per field based on agent response vs. ground truth:

| Classification | Meaning | When to use |
|---|---|---|
| AVAILABLE_AS_STRUCTURED_METADATA | Agent returned exact field value | Agent returned "PublicationOrder = 0" and ground truth is 0 |
| AVAILABLE_THROUGH_RENDERED_OR_FILE_CONTENT | Value is in page content, not metadata | Agent found value in page text, not from metadata field |
| VISIBLE_ONLY_IN_SHAREPOINT_UI | Value is in SharePoint UI but not accessible via agent | Agent cannot access, but value visible in UI |
| INFERRED_NOT_VERIFIED | Agent's answer seems plausible but unverified | Agent returned a value but couldn't cite source |
| NOT_OBSERVED | Agent did not return the value | Agent said "Not found" or didn't mention it |
| INACCESSIBLE_TO_TEST_IDENTITY | Access forbidden | Agent returned permission error |

---

## Next Steps

1. **Execute prompts:** Run each prompt via Copilot + review-manual-topics skill
2. **Capture responses:** Record exact responses in evidence template
3. **Classify findings:** Assign classification for each of 7 fields
4. **Analyze patterns:** Determine which fields are accessible as structured metadata
5. **Document limitations:** Note any platform constraints or skill limitations
6. **Generate report:** Populate task-9-metadata-visibility-report.md with findings

---

**Protocol prepared:** 2026-08-01  
**Ready for execution:** YES  
**Human reviewer required:** YES (to interpret agent responses and assign classifications)
