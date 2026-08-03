# NORM-01 — CONTROL (`CEIS-ASPX-Only-Test`)

**Category:** normal
**Exact prompt (verbatim from `evaluations/normal/case-normal-01.json`):** "What are the steps to
initiate a new file in CEIS?"
**Expected run_count:** 2

---

## Run 1

**Agent:** `CEIS-ASPX-Only-Test`
**Execution timestamp (capture time):** 2026-08-03T00:16:49Z
**Retry count:** 0
**Anomalies/UI limitations:** none

### Raw response (verbatim, unedited)

> To initiate a new file in CEIS, the documented procedure is as follows:
>
> **Initiate a New File**
> Enter the required information in the File Details section.
> Enter at least one Party and Role.
> Enter the Initiating Document.
> Save the file once all mandatory information has been entered. CEIS validates that the required
> information is complete before allowing the file to be saved. [1]
>
> **Mandatory Information Required**
> According to the procedure, CEIS checks that the following details have been entered before a
> new file can be saved:
> - File Details
> - Party and Role (at least one party and role)
> - Initiating Document
>
> If the Initiate File sequence is abandoned before the required information is entered and
> saved, the file is not completed. [1]
>
> **Related Data Entry Requirements**
> When entering the initiating document:
> - The initiating document must be entered as part of file initiation.
> - CEIS automatically assigns a sequence number to documents.
> - The initiating document receives the first sequence number, and subsequent documents receive
>   sequential numbering. [2]
>
> **File Details Requirements**
> The General File Details tab must be completed before navigating to the other File Details
> tabs. The File Details screen contains multiple tabs, including specialized tabs for certain
> file classifications. [3]
>
> Sources:
> - initiate-a-file--51d1f554.aspx (Reference: turn1search13) [1]
> - documents-data-entry--e87c1624.aspx (Reference: turn1search10) [2]
> - file-details--3422225d.aspx (Reference: turn1search12) [3]

### Citations / source references

1. `initiate-a-file--51d1f554.aspx`
2. `documents-data-entry--e87c1624.aspx`
3. `file-details--3422225d.aspx`

### Reviewer observations (analysis, clearly separated from raw evidence above)

- **Expected answerability matched:** yes — this is a directly answerable procedural question and
  the agent answered it directly.
- **Citation support:** `CITATION_SUPPORT_NOT_VERIFIED` for all 3 — sources not opened/checked
  against the response text in this pass.
- **Unsupported claims:** none apparent from the response text alone (pending citation
  verification above).
- **Refusal/decline behavior:** n/a — not a refusal case.
- **Ambiguity handling:** n/a.
- **Currency handling:** n/a — not asked about currency.
- **Apparent use of knowledge outside the configured source:** none apparent — response is
  procedural detail consistent with a real CEIS system manual, not generic court-system knowledge.

---

## Run 2

**Agent:** `CEIS-ASPX-Only-Test`
**Execution timestamp (capture time):** 2026-08-03T00:24:00Z (approximate — user-side, not
independently timestamped)
**Retry count:** 0
**Anomalies/UI limitations:** none

### Raw response (verbatim, unedited)

> To initiate a new file in CEIS, the documented procedure is:
>
> Start the Initiate File process and enter the required file information on the General File
> Details tab. The General File Details tab must be completed before you can move to the other
> tabs. [1][2]
>
> Complete the File Details information. The File Details screen contains multiple tabs, and the
> required file information must be entered before the file can be saved. [2][1]
>
> Add at least one Party and Role. CEIS requires at least one party and associated role before a
> new file can be saved. When entering parties:
> - Individuals are entered using surname and given name fields.
> - Organizations are entered using a single organization-name field. [1][3]
>
> Enter the Initiating Document. To complete file initiation, the initiating document must be
> entered into CEIS. CEIS automatically assigns a sequence number to the document, with the
> initiating document receiving the first sequence number. [1][4]
>
> Save the file. Before CEIS will save a new file, it verifies that the following mandatory items
> have been entered:
> - File Details
> - Party and Role (at least one)
> - Initiating Document [1]
>
> Do not abandon the initiation process before these mandatory items are entered. The procedure
> page notes that specific mandatory data must be entered before a new file can be saved. [1]
>
> Source Pages
> - initiate-a-file--51d1f554.aspx (Reference: turn1search13) [1]
> - file-details--3422225d.aspx (Reference: turn1search12) [2]
> - parties--62236e0e.aspx (Reference: turn1search17) [3]
> - documents-data-entry--e87c1624.aspx (Reference: turn1search10) [4]

### Citations / source references

1. `initiate-a-file--51d1f554.aspx`
2. `file-details--3422225d.aspx`
3. `parties--62236e0e.aspx`
4. `documents-data-entry--e87c1624.aspx`

### Reviewer observations (analysis, clearly separated from raw evidence above)

- **Expected answerability matched:** yes.
- **Citation support:** `CITATION_SUPPORT_NOT_VERIFIED` for all 4.
- **Unsupported claims:** none apparent from the response text alone.
- **Refusal/decline behavior:** n/a.
- **Ambiguity handling:** n/a.
- **Currency handling:** n/a.
- **Apparent use of knowledge outside the configured source:** none apparent.
- **Consistency across runs 1 and 2:** substance consistent (same 4-step core procedure: File
  Details → Parties/Roles → Initiating Document → Save, same mandatory-items list) — Run 2 adds
  more procedural detail (party entry format, explicit source-page list of 4 vs. 3) but does not
  contradict Run 1. Matches the expected-behaviour requirement "remains consistent in substance
  across repeated runs."
