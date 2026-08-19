# AMB-01 — CONTROL (`CEIS-ASPX-Only-Test`)

**Category:** ambiguous
**Exact prompt (verbatim from `evaluations/ambiguous/case-ambiguous-01.json`):** "How do I get
access to a file?"
**Expected run_count:** 2

---

## Run 1

**Agent:** `CEIS-ASPX-Only-Test`
**Execution timestamp (capture time):** 2026-08-03T01:26:00Z (approximate — user-side)
**Retry count:** 0
**Anomalies/UI limitations:** none

### Raw response (verbatim, unedited)

> According to the CEIS procedures documentation, access to a file is controlled by the file's
> Access Level and your assigned CEIS access role.
>
> **How file access works**
> - A file is assigned an Access Level when it is initiated.
> - The Access Level determines who can access that file.
> - Access is differentiated between internal users (court staff) and external users (members of
>   the public). [1]
>
> **If you cannot access a file**
> Your ability to view or update a file depends on the access roles assigned to you in CEIS.
> Users are assigned access roles for specific levels and classes of files, and those roles
> determine:
> - Which files they can access.
> - Which data-entry functions they can perform. [2]
>
> **Requesting access**
> The CEIS training and access documentation states that access is obtained through the CEIS
> access process and that users should contact the Access Group regarding CEIS access
> requirements. [3]
>
> Source pages
> - FILE ACCESS (reference: turn1search11) [1]
> - CEIS ACCESS LEVELS (reference: turn1search2) [2]
> - CEIS TRAINING (reference: turn1search5) [3]
>
> If you are trying to access a specific file and are receiving an access error, the procedure
> pages do not document the exact escalation steps, but they do indicate that access is determined
> by your assigned CEIS access level and role. [2][1]

### Citations / source references

1. `file-access--e19256ff.aspx`
2. `ceis-access-levels--42edb397.aspx`
3. `ceis-training--94f8aa2a.aspx`

### Reviewer observations (analysis, clearly separated from raw evidence above)

- **⚠️ Expected behaviour only partially met.** The case expects the agent to "recognize the
  question is ambiguous (public inquiry access vs. party access vs. staff internal access are
  documented as different procedures)" and "either ask a clarifying question or explicitly
  enumerate the distinct documented procedures rather than silently picking one." This response
  does neither cleanly: it does not ask a clarifying question, and it does not explicitly enumerate
  the distinct procedures as separate, named scenarios. It does gesture at a distinction
  ("differentiated between internal users (court staff) and external users (members of the
  public)") but blends this into one generalized answer about "Access Level" and "access roles"
  rather than treating public/party/staff access as clearly separate documented procedures the
  reader must choose among. This is a **partial**, not clean, satisfaction of the expected
  behaviour — closer to the prohibited "silently assume... and answer only that one without
  flagging the ambiguity" than the case intends, though it does not fully collapse to a single
  unflagged scenario either.
- **Topic count:** 3 sources consulted (primary `file-access` + 2 related: `ceis-access-levels`,
  `ceis-training`) — within the `related_topic_allowance: 2` cap (1 primary + 2 related = 3 max).
- **Citation support:** `CITATION_SUPPORT_NOT_VERIFIED` for all 3.
- **Unsupported claims:** none apparent — no fabricated procedure.
- **Refusal/decline behavior:** n/a — this is a synthesis/ambiguity case, not a decline case.
- **Ambiguity handling:** flagged above as the key finding — partial, not clean.
- **Currency handling:** n/a.
- **Apparent use of knowledge outside the configured source:** none apparent.

---

## Run 2

**Agent:** `CEIS-ASPX-Only-Test`
**Execution timestamp (capture time):** 2026-08-03T01:35:00Z (approximate — user-side)
**Retry count:** 0 (see anomaly note below — not counted as a retry since no failed *execution*
occurred, only a mislabeled paste caught before filing)
**Anomalies/UI limitations:** a first paste for this run was headed "CEIS-Markdown-Comparison-Agent"
instead of the expected `CEIS-ASPX-Only-Test` — flagged immediately, not filed, and the user
re-confirmed by re-querying and re-pasting the response below, correctly headed
`CEIS-ASPX-Only-Test`. The mislabeled response was never saved as evidence for either agent.

### Raw response (verbatim, unedited)

> According to the CEIS procedures, access to a file is controlled by the file's Access Level and
> your assigned CEIS access role.
>
> **File Access**
> - An Access Level code is entered when a file is initiated.
> - This access level determines who can access the file.
> - Access is differentiated between internal users (court staff) and external users (members of
>   the public). [1]
>
> **User Access Roles**
> - Users are assigned access roles in CEIS for specific levels and classes of files.
> - These roles determine:
>   - Which files a user can access.
>   - Whether the user can perform various data-entry functions.
> - Once a user has been granted access to a particular registry location, they receive the
>   permissions associated with their assigned role for that location. [2]
>
> **If You Need Access**
> The documented procedure does not provide steps for requesting access to a specific file.
> However, the training and access documentation states that CEIS access is managed through the
> Access Group, and users must complete the required training to obtain CEIS access. [3]
>
> Sources
> - file-access--e19256ff.aspx (Reference: turn1search11) [1]
> - ceis-access-levels--42edb397.aspx (Reference: turn1search2) [2]
> - ceis-training--94f8aa2a.aspx (Reference: turn1search5) [3]

### Citations / source references

1. `file-access--e19256ff.aspx`
2. `ceis-access-levels--42edb397.aspx`
3. `ceis-training--94f8aa2a.aspx`

### Reviewer observations (analysis, clearly separated from raw evidence above)

- **⚠️ Expected behaviour only partially met — same pattern as Run 1.** Again does not ask a
  clarifying question, and again does not explicitly enumerate public/party/staff access as
  distinct named procedures — synthesizes one generalized "Access Level + Access Role" answer with
  a passing internal/external mention. Consistent with Run 1's finding: partial, not clean,
  satisfaction of the ambiguity-handling requirement.
- **Topic count:** same 3 sources as Run 1 (`file-access`, `ceis-access-levels`, `ceis-training`) —
  within the 3-max cap.
- **Citation support:** `CITATION_SUPPORT_NOT_VERIFIED` for all 3.
- **Unsupported claims:** none apparent.
- **Ambiguity handling:** partial, matching Run 1 — this is a **consistent** finding across both
  runs (unlike NORM-02's cross-run inconsistency), which is itself notable: the agent
  consistently fails to cleanly enumerate or ask about the ambiguity, rather than doing so
  sometimes and not others.
- **Currency handling:** n/a.
- **Apparent use of knowledge outside the configured source:** none apparent.
