# EVID-PHASE4-TASK9-001 — Metadata Visibility Probe Results

**Date:** 2026-08-01  
**Phase:** Phase 4  
**Task:** 9 - Metadata Visibility Empirical Probe  
**Topic Tested:** DATA CAPTURE STANDARDS (ID: 182)  
**Testing Method:** Copilot in SharePoint + review-manual-topics skill  
**Status:** AWAITING EXECUTION

---

## Testing Instructions

### How to Execute the Metadata Visibility Probes

1. **Navigate to the deployed skill:**
   - Open Copilot in SharePoint on AG-CSB-INTRANET-DEV
   - The review-manual-topics skill should be discoverable

2. **For each prompt below:**
   - Copy the exact prompt text
   - Paste into Copilot chat
   - Wait for response
   - Record the response in the Evidence Capture section
   - Note whether the skill was invoked (check skill name in response)

3. **Record findings:**
   - Exact agent response text
   - Whether the skill was used (INVOCATION_CONFIRMED, INFERRED, AMBIGUOUS, NOT_OBSERVED)
   - What the agent cited as source
   - Your classification based on the Classification Framework

---

## Evidence Capture — Prompt Results

### Prompt 1: TopicID Field

**Prompt Text:**
```
Review the DATA CAPTURE STANDARDS topic. 
Check whether this topic has a TopicID field value assigned in its metadata.
If a TopicID exists, report the exact value.
If no TopicID is assigned, state that clearly.
Do not infer or generate a TopicID.
```

**Ground Truth:** TopicID = NULL (not assigned)

**Evidence Capture:**
- Agent Response: [AWAITING EXECUTION]
- Skill Invoked: [AWAITING EXECUTION]
- Citation: [AWAITING EXECUTION]
- Classification: [AWAITING CLASSIFICATION]
- Notes: [AWAITING EXECUTION]

---

### Prompt 2: PublicationOrder Field

**Prompt Text:**
```
Review the DATA CAPTURE STANDARDS topic.
What is the PublicationOrder metadata field value for this topic?
Return only the numeric value if present, or state if not assigned.
```

**Ground Truth:** PublicationOrder = 0

**Evidence Capture:**
- Agent Response: [AWAITING EXECUTION]
- Skill Invoked: [AWAITING EXECUTION]
- Citation: [AWAITING EXECUTION]
- Classification: [AWAITING CLASSIFICATION]
- Notes: [AWAITING EXECUTION]

---

### Prompt 3: TopicContentSHA256 Field

**Prompt Text:**
```
Review the DATA CAPTURE STANDARDS topic.
Does this topic have a TopicContentSHA256 field in its metadata?
If yes, report the exact SHA-256 hash value.
If no, state that.
Do not calculate or derive a content hash.
```

**Ground Truth:** TopicContentSHA256 = c72e3ca522cff7a91ff7acbe4026ccc298c06f83beb58217e47ec92f96f5e1aa

**Evidence Capture:**
- Agent Response: [AWAITING EXECUTION]
- Skill Invoked: [AWAITING EXECUTION]
- Citation: [AWAITING EXECUTION]
- Classification: [AWAITING CLASSIFICATION]
- Notes: [AWAITING EXECUTION]

---

### Prompt 4: Status Field

**Prompt Text:**
```
Review the DATA CAPTURE STANDARDS topic.
Check whether the Status metadata field is assigned.
Report the Status value if present, or state that no Status is assigned.
```

**Ground Truth:** Status = NULL (not assigned)

**Evidence Capture:**
- Agent Response: [AWAITING EXECUTION]
- Skill Invoked: [AWAITING EXECUTION]
- Citation: [AWAITING EXECUTION]
- Classification: [AWAITING CLASSIFICATION]
- Notes: [AWAITING EXECUTION]

---

### Prompt 5: ReviewDate Field

**Prompt Text:**
```
Review the DATA CAPTURE STANDARDS topic.
What is the ReviewDate metadata field value?
Return the date if assigned, or state if not assigned.
Do not infer a date.
```

**Ground Truth:** ReviewDate = NULL (not assigned)

**Evidence Capture:**
- Agent Response: [AWAITING EXECUTION]
- Skill Invoked: [AWAITING EXECUTION]
- Citation: [AWAITING EXECUTION]
- Classification: [AWAITING CLASSIFICATION]
- Notes: [AWAITING EXECUTION]

---

### Prompt 6: TransitionAction Field

**Prompt Text:**
```
Review the DATA CAPTURE STANDARDS topic.
Is there a TransitionAction metadata field assigned to this topic?
If yes, report the value.
If no, state that.
```

**Ground Truth:** TransitionAction = NULL (not assigned)

**Evidence Capture:**
- Agent Response: [AWAITING EXECUTION]
- Skill Invoked: [AWAITING EXECUTION]
- Citation: [AWAITING EXECUTION]
- Classification: [AWAITING CLASSIFICATION]
- Notes: [AWAITING EXECUTION]

---

### Prompt 7: TransitionTarget Field

**Prompt Text:**
```
Review the DATA CAPTURE STANDARDS topic.
Check for a TransitionTarget metadata field.
Report its value if present, or state if not assigned.
```

**Ground Truth:** TransitionTarget = NULL (not assigned)

**Evidence Capture:**
- Agent Response: [AWAITING EXECUTION]
- Skill Invoked: [AWAITING EXECUTION]
- Citation: [AWAITING EXECUTION]
- Classification: [AWAITING CLASSIFICATION]
- Notes: [AWAITING EXECUTION]

---

## Classification Reference

Use the Classification Framework from task-9-metadata-visibility-protocol.md:
- **AVAILABLE_AS_STRUCTURED_METADATA** — Agent returned exact field value from metadata
- **AVAILABLE_THROUGH_RENDERED_OR_FILE_CONTENT** — Value found in page content, not metadata
- **VISIBLE_ONLY_IN_SHAREPOINT_UI** — In UI but not accessible via agent
- **INFERRED_NOT_VERIFIED** — Agent's answer seems plausible but unverified
- **NOT_OBSERVED** — Agent did not return the value
- **INACCESSIBLE_TO_TEST_IDENTITY** — Permission error

---

## Summary (To be completed after execution)

**Findings Summary:** [AWAITING EXECUTION]
**Fields accessible as structured metadata:** [AWAITING CLASSIFICATION]
**Fields accessible only through content:** [AWAITING CLASSIFICATION]
**Fields inaccessible:** [AWAITING CLASSIFICATION]
**Limitations identified:** [AWAITING EXECUTION]

---

**Evidence ID:** EVID-PHASE4-TASK9-001  
**Status:** TEMPLATE PREPARED, AWAITING EXECUTION  
**Reviewer:** [To be assigned]
