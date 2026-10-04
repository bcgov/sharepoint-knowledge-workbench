# Field Note — `AgentAssets` Tenant Inventory (2026-08-05)

**Purpose:** Record a live-tenant inventory of everything currently deployed under
`AgentAssets` on `TargetSite-Dev`, attribute each item to a known repository source
(or flag it as unattributed), and capture the capability patterns visible in the skills that
have **no** repository source of truth. This is empirical tenant evidence, not a governance
decision.

**Status:** Point-in-time observation. Re-verify before relying on this list — tenant content
can change between sessions and no repository-owned automation currently re-runs this check.

**Method:** No existing skill performs this end-to-end (inventory + download + capability
analysis + write-up). This note was produced manually using two existing, narrower
`sharepoint-agents-and-skills` capabilities:

- `inventory-and-validate-agentassets` (`verify-agentassets-ready.ps1`) — confirmed
  `AgentAssets`/`Skills/` exist and listed every `SKILL.md`/`.md` file found.
- `backup-sharepoint-native-skills` (`backup-sharepoint-native-skills.ps1`) — downloaded each
  file's exact content to a local, gitignored folder (`temp/agentassets-analysis/downloaded-
  skills/`) for reading.

See "Gap identified" below — this two-step manual process is exactly the kind of repeatable
capability a dedicated skill should own.

## 1. Inventory

| Item | Path | Size (bytes) | Repository attribution |
|---|---|---|---|
| `sample-test-skill` | `AgentAssets/Skills/sample-test-skill/SKILL.md` | 821 | **Known** — created by `tools/phase-4-native-sharepoint-skills/deployment/scripts/create-test-skill.ps1` (Phase 4.7.5 test skill). |
| `review-manual-topics` | `AgentAssets/Skills/review-manual-topics/SKILL.md` | 9,461 | **Known** — repository skill at the time of this 2026-08-05 observation (see `field-note-agentassets-skill-creation.md`). It has since moved into `sharepoint-document-conversion`; consult the current seven-domain catalog before using old paths. |
| `sample-procedure-review-template.md` | `AgentAssets/sample-procedure-review-template.md` | 383 | **Known** — a tracked Phase 4 deliverable template (see `tools/phase-5-sharepoint-knowledge-agent-pilot/backup-skills-and-templates.ps1`'s own docstring, which explicitly lists it as "real Phase 4 deliverables, explicitly NOT in scope for any deletion"). |
| `build-sample-module-test` | `AgentAssets/Skills/build-sample-module-test/SKILL.md` | 3,949 | **Unattributed.** No match anywhere in this repository's tracked source, docs, or tools for this skill name or its content. Not created by any script in this repo. |
| `sample-workflow-diagram` | `AgentAssets/Skills/sample-workflow-diagram/SKILL.md` | 3,779 | **Unattributed.** Same as above — no repository source. |
| `content-review` | `AgentAssets/Skills/content-review/SKILL.md` | 11,748 | **Unattributed.** Same as above. (Repo docs use the generic phrase "content review"/"prepare-content-review" as a *proposed capability name* in design docs — that is not the source of this deployed skill's actual content.) |

Confirmed via `git grep` across all tracked files (excluding the gitignored download folder)
for each unattributed skill's exact name — zero matches outside the three known items above.

## 2. Capability patterns observed in the unattributed skills

These three skills were not authored by this repository's tooling, yet they are live,
functioning native SharePoint skills on the pilot tenant. Read for their own capability value
(independent of the attribution question):

### `content-review` (11.7 KB — the largest skill found)

- Drives an **interactive, one-question-at-a-time** SME review checklist (8 fixed questions:
  accuracy, completeness, currency, link/reference currency, clarity, requested changes,
  recommended action, final status), rather than presenting a form or full checklist at once.
- Reads the **target item's own list/library schema** to find real internal field names
  (`Review Status`, `Reviewed By`, `Reviewed Date`, `Review Notes`, `Next Review Date`,
  `Content Owner`) rather than assuming they exist or guessing internal names — explicitly
  told to stop and ask if a required column is missing.
- Applies **AI-assisted content edits** grounded only in original content + reviewer feedback,
  with an explicit "Needs SME confirmation" bucket for anything unverifiable.
- Writes a **visible, styled HTML status box** (color-coded per status) directly into the page
  content, full-width, below the header — a UI/UX pattern not seen in any repository-authored
  skill.
- Writes **both** content and metadata in the same save flow, and reports both outcomes
  separately if one fails.
- This is the richest read+write interactive workflow found across every skill (repo-authored
  or not) reviewed in this plugin so far.

### `build-sample-module-test` (3.9 KB)

- Generates a Markdown **quiz/assessment** (default 10 questions, mixed format) from SampleManual
  module content, with a required answer key + rationale + **source citation per question**.
- Explicit anti-hallucination guardrails: refuses to invent facts/policy/steps not present in
  retrieved source content; marks ambiguous questions "Needs human review" instead of guessing.
- A capability category (content-derived assessment generation) not present in any
  repository-authored skill reviewed to date.

### `sample-workflow-diagram` (3.8 KB)

- Converts SampleManual procedure text/pages into a **Mermaid flowchart** embedded in a new `.md` file,
  written to a fixed destination (`TargetPilotKnowledgeMarkdown/diagrams/`), with a defined
  filename convention (kebab-case + `-workflow-diagram.md` suffix, collision-avoidance
  suffixing).
- Includes an explicit "Assumptions or gaps" section when a step is unclear, rather than
  inventing missing steps.
- This is the only skill found so far that **creates a new file** as its primary output rather
  than reviewing/updating an existing one.

## 2.1 Attribution mechanism resolved (2026-08-05, live user confirmation)

Follow-up testing the same day resolved the "authored by whom, how" question left open below:
the user confirmed all 3 unattributed skills were created by **asking the site's ready-made
Copilot assistant directly, in chat, to author each skill** — not by hand-writing and uploading
a `SKILL.md` file, and not through this repository's `create-sharepoint-native-skill`/
`deploy-sharepoint-native-skill` tooling. This is a materially different origin than "unknown
human, unknown method" — it is a **known creation mechanism** (natural-language skill
authoring via the ready-made assistant), just not a repository-tracked one. See
`sharepoint-agent-and-skill-capability-reference.md` §2.6 for the full capability writeup this
unlocks. The exact author identity and timestamp remain unverified from repository evidence
alone; the tenant's own file version history is still the next place to check for that detail.

The same live session also confirmed `content-review` performs genuine, persisted writes when
actually used through that ready-made assistant: while reviewing one topic's content, the skill
updated the content and its styling, and separately saved the metadata fields — both changes
were user-verified to persist, not just previewed. This directly confirms the write-capable
design described below is not just theoretical from reading the skill's own instructions; it
executes as written, at least via this invocation surface.

## 3. Gap identified

No skill under `plugins/sharepoint-copilot-agents-and-skills/skills/` currently performs the discovery
+ download + capability-analysis + write-up sequence this note required manually:

- `inventory-and-validate-agentassets` only confirms existence/readiness and lists filenames —
  it does not fetch or interpret content.
- `verify-sharepoint-native-skill` only does SHA-256 drift comparison against **one named,
  already-known** repository source — it has no way to characterize a skill this repository
  did not author (there is nothing to hash-compare against).
- `backup-sharepoint-agents`/`backup-sharepoint-native-skills` require the caller to already
  know the exact target list — neither discovers new/unattributed items on its own.
- `review-manual-topics` reviews SampleManual **manual content topics**, not skill/agent definitions.

Three unattributed, functioning, write-capable native skills existing on a shared pilot tenant
with no repository record, no test coverage, and no governance review is itself a real finding
— not just a documentation gap. Whoever authored `content-review`, `build-sample-module-test`,
and `sample-workflow-diagram` (and when) is currently unknown from this repository's evidence
alone; the tenant's own file version history would be the next place to check.

## 4. Evidence

```text
Site: https://contoso.sharepoint.com/sites/TargetSite-Dev
Date tested: 2026-08-05
AgentAssets library: exists, ItemCount 12
Skills/ subfolder: exists, accessible
SKILL.md files found: 6 (5 under Skills/, 1 loose template at AgentAssets root)
Tool used: verify-agentassets-ready.ps1 (inventory) + backup-sharepoint-native-skills.ps1 (download)
Local evidence (gitignored, not committed): temp/agentassets-analysis/
```
