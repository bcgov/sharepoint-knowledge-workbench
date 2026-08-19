# NORM-01 — COMPARISON (`CEIS-Markdown-Comparison-Agent`)

**Category:** normal
**Exact prompt (verbatim from `evaluations/normal/case-normal-01.json`):** "What are the steps to
initiate a new file in CEIS?"
**Expected run_count:** 2

---

## Run 1

**Agent:** `CEIS-Markdown-Comparison-Agent`
**Execution timestamp (capture time):** 2026-08-03T00:29:00Z (approximate — user-side)
**Retry count:** 0
**Anomalies/UI limitations:** none

### Raw response (verbatim, unedited)

> According to the procedure page initiate-a-file--51d1f554.md, initiating a new file in CEIS
> requires entering a minimum set of mandatory information before the file can be saved. [1]
>
> **Steps to Initiate a New File**
>
> **1. Enter File Identification Details**
> The first step is to record the file identification details. All fields in the File
> Identification screen are mandatory. [1]
>
> Required fields include:
> - Court File Number: The file number corresponding to the physical file jacket. This uniquely
>   identifies the file. [1]
> - Level: Select the court level:
>   - Supreme (S)
>   - Provincial (P) [1]
> - Class: Select the appropriate file type/class. [1]
> - Location: The default location is entered automatically, but another location can be selected
>   if required. [1]
>
> Important Notes:
> - The Date Opened should not be after the filing date of the initiating document. Normally they
>   should be the same day. [1]
> - For new Provincial or Supreme Court civil files, numeric values only may be used in the File
>   Number field. CEIS does not accept alpha characters for new files. [1]
>
> **2. Save the File Identification Details**
> After entering the file identification information, click Save. The file will then be
> maintained through the regular Maintain File screens used for existing files. [1]
>
> **3. Add Parties and Roles**
> At least one party and one role must be entered before the file can be saved successfully. CEIS
> validates that a Party and Role exist. [1]
>
> The parties--62236e0e.md procedure states that when initiating a file, you add party information
> using Add Parties from the File Details screen, and the mandatory tabs are:
> - Party Details
> - Party Roles [2]
>
> **4. Enter the Initiating Document**
> To complete file initiation, you must enter the initiating document. CEIS requires an initiating
> document before a new file can be saved. [1][3]
>
> The documents-data-entry--e87c1624.md procedure notes:
> - Use Add Document.
> - The first document added is automatically treated as the initiating document.
> - Complete all mandatory document fields and save. [3]
>
> **Minimum Requirements Before Saving**
> CEIS checks that the following have been entered:
> - File Details
> - At least one Party and Role
> - An Initiating Document [1]
>
> If you abandon the initiation process before entering these minimum details, CEIS will warn you
> that the file may be deleted and must be re-entered from the beginning. [1]
>
> Source: initiate-a-file--51d1f554.md [1]

### Citations / source references

1. `initiate-a-file--51d1f554.md`
2. `parties--62236e0e.md`
3. `documents-data-entry--e87c1624.md`

### Reviewer observations (analysis, clearly separated from raw evidence above)

- **Expected answerability matched:** yes.
- **Citation support:** `CITATION_SUPPORT_NOT_VERIFIED` for all 3.
- **Unsupported claims:** none apparent from the response text alone.
- **Refusal/decline behavior:** n/a.
- **Ambiguity handling:** n/a.
- **Currency handling:** n/a.
- **Apparent use of knowledge outside the configured source:** none apparent.
- **Comparison note vs. CONTROL Run 1/2 (`NORM-01-aspx.md`):** substantively very similar content
  and structure (same 4-step core: File Identification → Save → Parties/Roles → Initiating
  Document), citing the `.md` counterparts of the same 3 source topics
  (`initiate-a-file`, `parties`, `documents-data-entry`). This is an observation only, not a
  scored comparison — the evaluation schema defines no numeric score for this.

---

## Run 2

**Agent:** `CEIS-Markdown-Comparison-Agent`
**Execution timestamp (capture time):** 2026-08-03T00:33:00Z (approximate — user-side)
**Retry count:** 0
**Anomalies/UI limitations:** none

### Raw response (verbatim, unedited)

> According to initiate-a-file--51d1f554.md, the procedure to initiate a new file in CEIS is as
> follows: [1]
>
> **Initiate a New File in CEIS**
>
> **Prerequisites**
> Before a new file can be saved, CEIS requires the following minimum information: [1]
> - File Details
> - At least one Party and Role
> - An Initiating Document
>
> If you exit the initiation process before entering these items, CEIS will display a warning
> message. Choosing Yes deletes the incomplete file; choosing No keeps the screen open so you can
> continue. [1]
>
> **Step 1: Enter File Identification Details**
> Complete all mandatory fields on the File Identification screen. [1]
>
> Required information includes:
> - Court File Number — the file number corresponding to the physical file jacket. This uniquely
>   identifies the file across the province. [1]
> - Level — Select the court level: Supreme (S) / Provincial (P) [1]
> - Class — Select the appropriate file type/class for the matter. [1]
> - Location — The default location is populated automatically, but you can select a different
>   location if required. [1]
>
> Important Notes:
> - All fields on the File Identification screen are mandatory. [1]
> - The Date Opened should never be later than the filing date of the initiating document.
>   Normally, they should be the same date. [1]
> - For new Provincial or Supreme civil files, use numeric values only in the File Number field.
>   CEIS does not accept alphabetic characters for new file numbers. [1]
>
> **Step 2: Save the File Identification Information**
> After entering the File Identification details, click Save. Once saved, you will use the
> Maintain File screens to complete the remainder of the file initiation process. [1]
>
> **Step 3: Add Parties and Roles**
> The next step is to enter at least one party and assign the appropriate role(s) to that party.
> Party roles must correspond to the initiating document and file class. [2][1]
>
> **Step 4: Enter the Initiating Document**
> To complete file initiation, enter the initiating document. CEIS automatically assigns it
> sequence number 1. The initiating document is mandatory for file creation. [3][1]
>
> Source: initiate-a-file--51d1f554.md (primary procedure), with supporting details from
> parties--62236e0e.md and documents-data-entry--e87c1624.md. [1][2][3]

### Citations / source references

1. `initiate-a-file--51d1f554.md`
2. `parties--62236e0e.md`
3. `documents-data-entry--e87c1624.md`

### Reviewer observations (analysis, clearly separated from raw evidence above)

- **Expected answerability matched:** yes.
- **Citation support:** `CITATION_SUPPORT_NOT_VERIFIED` for all 3.
- **Unsupported claims:** none apparent from the response text alone.
- **Refusal/decline behavior:** n/a.
- **Ambiguity handling:** n/a.
- **Currency handling:** n/a.
- **Apparent use of knowledge outside the configured source:** none apparent.
- **Consistency across runs 1 and 2:** substance consistent — same 4-step structure, same 3 cited
  topics, same mandatory-items list (File Details / Party and Role / Initiating Document) in both
  runs. Matches the expected-behaviour requirement "remains consistent in substance across
  repeated runs."
