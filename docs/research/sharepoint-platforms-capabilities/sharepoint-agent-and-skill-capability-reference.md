# SharePoint Agent and Native Skill Capability Reference

> This capability reference preserves historical tenant findings. Its old plugin and skill
> names identify the source used when each observation was recorded; they are not current
> install paths. Use the [current seven-domain catalog](../../architecture/seven-domain-plugin-skill-catalog.md)
> for current identities.

**Purpose:** Consolidate what has actually been observed, tested, or confirmed on a real tenant
about the two distinct `AgentAssets`-adjacent artifact types — **SharePoint Copilot agents**
(`.agent` JSON files) and **native Copilot in SharePoint skills** (`SKILL.md` files) — into one
capability reference. This document synthesizes and cross-links existing field notes; it does
not replace them, and it is not the same kind of document as
`capability-layering-across-platforms.md` (below).

**Status:** Empirical synthesis, sourced entirely from the field notes and research summaries
cited throughout. Not implementation or deployment authorization. Re-verify any claim against
the cited source before relying on it — preview capabilities and tenant configuration can
change.

**How this differs from other documents in this folder:**

- `capability-layering-across-platforms.md` — the **conceptual/positional** model (where each
  platform — SharePoint agent, native skill, Cowork, Copilot Studio, GitHub Copilot — fits
  relative to the others). Theoretical, not evidence-driven.
- `field-note-*.md` — individual, point-in-time **empirical observations** from one test or one
  tenant session each.
- **This document** — a standing, evidence-linked **catalogue of confirmed capabilities and
  limitations**, organized by artifact type, updated as new field notes add evidence. Read this
  first for "what can a SharePoint agent/skill actually do", then follow the citations for the
  full context of each finding.

---

## 0. At-a-Glance Summary

A condensed reading path through this document's confirmed findings, newest/most significant
first. Each line links to its full evidence section — read this first, then drill into the
section that matters for your question.

- **Interactive content review + edit is the single most compelling confirmed capability.**
  `content-review` runs a real one-question-at-a-time SME review, applies content edits,
  updates a visible status box, and saves review metadata (`Review Status`/`Reviewed By`/
  `Reviewed Date`/`Review Notes`) — all genuinely persisted, live-session-verified. User
  assessment: *"very powerful."* → §2.7, §3.
- **Write actions ARE possible — just not from a custom `.agent` chat pane.** The site's
  ready-made assistant can perform real content/metadata/new-file writes and can even author or
  edit a skill's own `SKILL.md` definition conversationally. This reconciles Phase 3.0's earlier
  "writes are blocked" finding, which was specific to the custom-agent surface it tested. → §2.6
- **Mermaid diagrams render as real visuals — but only via a saved `.md` file, never in chat.**
  `sample-workflow-diagram` sidesteps the chat pane's text-only limitation by always writing a new
  `.md` file with a fenced Mermaid block; opening that file in SharePoint's native Markdown
  viewer renders an actual flowchart. → §2.5, §3.
- **Native Markdown rendering and multi-topic synthesis both work well on real manual content.**
  The actual `docx-to-content` plugin output (348 files) renders natively with working
  cross-links, and an agent grounded on it correctly synthesized a domain-accurate, cited answer
  spanning 3 real source manual topics without overclaiming. → §2.5
- **Two structurally different agent types exist** (always-present ready-made vs. editable
  custom `.agent`), each with real, documented constraints: ≤20 knowledge sources, no List data,
  no Site Pages library pages as a source, results filtered to the current user's own
  permissions. → §2, §2.3
- **Exact output formatting (labels/delimiters/JSON schemas) is unreliable; behavioral
  instructions (scope refusal, confirmation gates) are reliable.** Don't design a skill around
  parsing its literal chat output. → §2.4
- **3 of 5 real deployed skills have no repository source** — traced to being authored directly
  via ready-made-assistant chat, not hand-uploaded files; a real governance/attribution gap
  since none of that has test coverage or review. → §3, `field-note-agentassets-tenant-
  inventory-2026-08-05.md`
- **SharePoint modern pages are a viable Renderer target** (`Add-PnPPage`/`Add-PnPPageTextPart`),
  but raw `.aspx` upload is confirmed blocked, and a modern page can never be added back as an
  agent knowledge source. → §2.5, §2.3
- **Site/web/list IDs must always be freshly queried, never copied between agents/sites** — the
  one safety-critical mistake most likely to silently ground an agent on the wrong content. →
  §2.1
- **Biggest open gap:** none of this has been re-verified from Microsoft Teams, only the
  SharePoint chat-pane/file-preview surfaces; cross-artifact impact-awareness (one topic's edit
  triggering awareness of related diagrams/forms) is aspirational, not yet tested. → §5

## 1. Two Distinct Artifact Types

```text
SharePoint Copilot agent (.agent JSON file)
= a purpose-specific conversational experience grounded in selected knowledge sources

Native Copilot in SharePoint skill (SKILL.md file, under AgentAssets/Skills/<name>/)
= a repeatable, site-scoped, multi-step procedure invoked by matching trigger language
```

They are provisioned differently, stored differently, and have different capability
boundaries. Treat findings about one as inapplicable to the other unless a note explicitly
confirms otherwise (see §4, "agent-to-skill discovery").

## 2. SharePoint Agent (`.agent`) Capabilities — Confirmed

| Capability / constraint | Status | Evidence |
|---|---|---|
| Knowledge source requires exact `site_id`/`web_id`/`list_id`/`unique_id`, not just a URL | `CONFIRMED_TENANT_OBSERVATION` | `research-experimentation/PHASE-4-SHAREPOINT-AGENTS-CRITICAL-LEARNINGS.md` Part 1 |
| Classic ASPX pages are **not** automatically indexed/discoverable by agent keyword search | `CONFIRMED_TENANT_OBSERVATION` (platform constraint) | same, Part 1 |
| Site Pages folder knowledge sources need a real, non-zero `unique_id`; document-library sources use an all-zero `unique_id` | `CONFIRMED_TENANT_OBSERVATION` | `research-experimentation/phase-4-agent-format-learning-journal.md` §"Knowledge Source Structure" |
| Agent schema is `schemaVersion 0.2.0`, `customCopilotConfig.gptDefinition`, `items_by_url`/`items_by_sharepoint_ids` capability block, `behavior_overrides.special_instructions.discourage_model_knowledge` to force source grounding | `CONFIRMED_TENANT_OBSERVATION` (reverse-engineered from working reference agents) | same; current authoring skill: `plugins/sharepoint-copilot-agents-and-skills/skills/sharepoint-create-agent-package/SKILL.md` |
| A single-knowledge-source agent, if hand-serialized via naive `ConvertTo-Json`, can silently collapse `items_by_url` into a bare object instead of a one-element array (schema-invalid) | `CONFIRMED_TENANT_OBSERVATION` — real bug found and fixed | `create-sharepoint-agent`'s test suite (see its `SKILL.md`) |
| The default/ready-made Copilot in SharePoint experience *appears* to "launch" a named custom agent from natural language, but may be self-answering rather than truly handing off to the named agent's distinct instructions | `INCONCLUSIVE` — not yet confirmed | `field-note-agent-launch-by-name-not-a-handoff.md` |
| Raw `.aspx` file upload to a document library is blocked (`Access denied`); only `Add-PnPPage`/`Add-PnPPageTextPart` modern-page creation works | `CONFIRMED_TENANT_OBSERVATION` | Historical source: old publication skill; current publication package is `sharepoint-site-build-and-publish` (see catalog). |
| Two agents (ASPX-grounded vs. Markdown-grounded) both showed the same two failure modes: inferring "currency" from upload timestamps instead of real review metadata, and giving contradictory confident answers across repeated runs of the same cross-topic question | `CONFIRMED_TENANT_OBSERVATION` (single-tenant test) | `knowledge-discovery-retrieval/field-note-aspx-vs-markdown-grounding.md` |
| Government cloud environments (GCC, GCC High, DoD, 21Vianet-operated M365) do not currently support Copilot in SharePoint preview | `PRODUCT_DOCUMENTED` (Microsoft Learn, not tenant-tested) | `research-copilot-in-sharepoint-preview.md` §3 |
| HTML content converted via pandoc and published through `Add-PnPPage`/`Add-PnPPageTextPart` renders correctly as a modern page — headings, bullet lists, and embedded images all rendered inline | `CONFIRMED_TENANT_OBSERVATION` | `PHASE-4-SHAREPOINT-AGENTS-CRITICAL-LEARNINGS.md` Part 5. `.docx`/`.pptx` generation, multi-section/multi-web-part pages, and multi-image/table rendering are `NOT_YET_TESTED`. |
| Custom agents are independently discoverable/usable from the Microsoft Teams app store; parity with the SharePoint chat-pane experience is unverified | `FOLLOW_UP_REQUIRED` | same, Part 7 |

### 2.1 Site Isolation — Safety-Critical Finding

Two distinct, compounding provisioning mistakes were found and fixed during Phase 4 agent
creation, both `CONFIRMED_TENANT_OBSERVATION` (`phase-4-agent-format-learning-journal.md`
§"CRITICAL: Site Isolation Issue & Multi-Stage Fix"):

1. **Zero `unique_id` leaks cross-site content in the picker.** An agent's knowledge-source
   `unique_id` left as `00000000-0000-0000-0000-000000000000` permitted the SharePoint content
   picker to expose libraries from an entirely different, retired sandbox site
   (`TargetSite-Dev`) instead of the intended `TargetSite-Dev`.
2. **Wrong `site_id`/`web_id` grounds the agent on the wrong site entirely, silently.** An
   automation script initially reused `site_id`/`web_id` values copied from a different test
   agent, which pointed at the retired sandbox rather than the target site — the agent
   referenced the wrong site's content with no error raised.

**Fix pattern confirmed working:** always query the live target site directly for real IDs
(`Get-PnPList -Identity "<library>"`, `(Get-PnPSite).Id.Guid`, `(Get-PnPWeb).Id.Guid`) and verify
against a manually-created, confirmed-working reference agent — never reuse or hardcode IDs
copied from another agent or another site's documentation.

**Lesson recorded verbatim:** *"Site_id and web_id are critical for site identification. Never
assume values from other agents. Always verify before hardcoding."*

### 2.2 Agent JSON — Best Practices Confirmed Working

From `phase-4-agent-format-learning-journal.md` §"Best Practices Discovered", reverse-engineered
from multiple working reference agents (also reflected in `create-sharepoint-agent`'s
implementation):

| Field | Confirmed working pattern |
|---|---|
| `name` | Descriptive but reasonably short (e.g. "SampleManual Pilot Knowledge Agent") |
| `description` | One short sentence stating purpose |
| `instructions` | Single clear directive sentence, formal tone (e.g. "Provide accurate information about the content in the selected files and reply in a formal tone.") |
| `conversationStarters` | Exactly 3 items, generic — not domain-specific |
| `welcomeMessage` | Generic prompt to start the conversation |
| `behavior_overrides.special_instructions.discourage_model_knowledge` | Always `true`, to force grounding on the configured knowledge sources rather than the model's own general knowledge |
| `icon` | Base64-encoded PNG |

Agents can be created in more than one storage location on the same site (e.g. a document
library's root vs. a `SitePages/<name>/` subfolder), each with its own independent knowledge
sources — confirmed by two working reference agents at different locations
(`phase-4-agent-format-learning-journal.md` §"Storage Locations").

### 2.3 Phase 3.0 Tenant Discovery — Additional Confirmed Agent Findings

Source: `research-experimentation/tenant-discovery/field-note-sharepoint-write-capability-
discovery.md` — a larger, earlier (2026-07-29/30) hands-on discovery session than Phase 4's,
performed directly via PnP PowerShell (no Copilot UI wizard) against the same tenant, later
corroborated by official Microsoft documentation (§16–18 of that note). All findings below are
`CONFIRMED_TENANT_OBSERVATION` on this tenant/permission profile unless marked otherwise.

- **Two distinct agent types exist:** every site/library has an always-present **ready-made
  agent** (no `.agent` file, cannot be edited/shared/deleted, admins can remove it only via the
  Restricted Content Discovery policy) vs. a **custom agent** (created with site-editing
  permissions, has a real `.agent` file, fully editable/shareable). `Get-PnPCopilotAgent` can
  only ever inventory custom agents — the ready-made agent has no file for it to find.
- **A custom agent's `.agent` file is not required to live in `AgentAssets`.** Creating an agent
  via a document library's own "Create an agent" command drops the `.agent` file directly inside
  *that* library, not into a site-wide `AgentAssets` library. `AgentAssets/Skills/` remains the
  confirmed convention for *native skills* specifically (see §3), not for agent files in general.
- **`.agent` file creation is genuinely scriptable, with a real caveat.** A hand-authored
  `.agent` JSON, uploaded via plain `Add-PnPFile` (no dedicated PnP agent-creation cmdlet
  exists), rendered and functioned identically to a UI-wizard-created agent — correct name,
  welcome message, source binding, and grounded/cited retrieval (proven with a planted-keyword
  test). **Caveat:** the schema is reverse-engineered, not documented by Microsoft, and generic
  upload success does not establish a supported deployment contract — classify as *technically
  viable in the tested tenant*, not yet an *operational deployment contract*.
- **Agents currently cannot use data from SharePoint Lists, and cannot add Site Pages library
  pages as a knowledge source at all** — both are official, documented Microsoft platform
  limitations (§16 of the source note), not tenant-specific quirks. This directly explains why a
  modern page created via `Add-PnPPage` (§2.5 below) can never itself be added as an agent
  knowledge source, and why any write-action test against a List was probing a data source
  agents can't read from in the first place, independent of the write question.
  quote from source: *"Agents currently don't use data from Lists. Also, you can't add pages from
  the Site Pages library as source for an agent."*
- **Documented source-item limit: up to 20 items** (sites, libraries, folders, or files, in any
  mix) per agent (Microsoft Support FAQ, §16 of the source note) — a real, documented ceiling
  worth remembering when designing a multi-topic/multi-manual agent.
- **Agents only surface content the current user already has permission to see, even if it's in
  the agent's configured Sources** (Microsoft Support FAQ, §16) — confirms knowledge-retrieval
  scope, platform capability, and the current user's own permissions are three genuinely
  separate things, not to be conflated (see the `INCONCLUSIVE` permission-boundary rows in §4).
- **Hub-site source expansion has a September 2025 cutoff.** Ready-made agents always include
  associated hub sites; for *custom* agents, a hub-site source added **before** September 2025
  does not auto-include its associated sites unless removed and re-added. Check any custom
  agent's creation date against this cutoff before drawing conclusions from a hub-scope test.
- **Custom agents are cross-surface, not SharePoint-page-scoped** — confirmed discoverable and
  usable from the Microsoft Teams app store (personalized per user, previewable, addable to a
  chat/channel/meeting) per official Microsoft documentation (§18 of the source note). None of
  this document's chat-pane findings have been re-verified from the Teams surface — see §5,
  "Known Gaps".

### 2.4 Format Compliance and Behavioral Reliability — Confirmed Patterns

Source: same Phase 3.0 note, §§6–12 (a five-variant format A/B test plus a scoped-Q&A skill
redesign informed by the results).

| Finding | Status |
|---|---|
| A skill's `## Output format` section is a **stylistic bias, not an enforced contract** — the agent reformats into its own native labeled-bullet/`Q:`/`A:` style regardless of what the skill requests | `CONFIRMED_TENANT_OBSERVATION` |
| Of 4 format variants tested (custom ASCII delimiters, few-shot example, strict JSON, external template file), **strict JSON was honored most reliably** — correct key names, though with extra unrequested fields and trailing prose | `CONFIRMED_TENANT_OBSERVATION` |
| An externally-referenced template file (a sibling file in the skill's own folder) was **not read literally** — the agent fabricated a plausible-looking field name that appears nowhere in the real file, rather than quoting its actual content | `CONFIRMED_TENANT_OBSERVATION` — a real hallucination-of-structure risk, not just imperfect formatting |
| **Higher-level behavioral instructions (scope restriction, refuse-rather-than-guess) are followed reliably and correctly**, even when the skill's exact label wording is not | `CONFIRMED_TENANT_OBSERVATION` |
| Native skills in `AgentAssets/Skills/` are discoverable **site-wide by trigger phrase**, not scoped only to the agent's own attached knowledge sources | `CONFIRMED_TENANT_OBSERVATION` (tempered — proven for the tested same-site custom agent only, not proven for every agent/user/permission combination — see §4) |

**Practical implication recorded verbatim:** *"If exact machine-parseable output is a hard
requirement, don't use a SharePoint agent chat response as the parsing source at all;
post-process/validate downstream instead."* This directly bears on any future skill whose output
needs to be consumed programmatically (e.g. by a repository script) rather than just read by a
human.

### 2.5 SharePoint as a Multi-Format Renderer Target — Confirmed and Blocked Paths

Source: same Phase 3.0 note, §§13–15, testing this repository's own `Content + Template +
Renderer = Published Output` vision directly against the real source manual rendered output.

- **Native Markdown rendering: `CONFIRMED` working well.** The actual `docx-to-content` plugin's
  rendered output (348 files, `pages/` + `media/`) was uploaded and opened directly — SharePoint's
  built-in Markdown viewer correctly rendered headings and turned every relative Markdown link
  into a working in-viewer navigation link between topic files (confirmed by clicking through,
  not just viewing the index). The viewer also surfaces contextual Copilot suggestion chips
  ("Summarize this document", "Create an FAQ from this document") automatically, with zero
  configuration. Embedded-image rendering within a topic page (as opposed to just links) was
  **not yet independently confirmed** — flagged as a distinct follow-up.
- **Multi-document cross-topic synthesis: `CONFIRMED`, high quality — the strongest single
  result in this note.** Asked how two real source manual topics (two related procedures) relate,
  the agent correctly identified 3 relevant source files, used correct domain-specific
  terminology and form codes, cited every claim, and explicitly avoided overclaiming a causal
  relationship the source material didn't support (stating the manual only links the topics
  operationally, not causally). This is real domain content correctly extracted and connected
  across multiple real manual topics, not hallucinated — direct evidence the core "ground an
  agent on structured/rendered manual content" value proposition works.
- **Raw `.aspx` file upload: `CONFIRMED BLOCKED`.** Uploading a hand-wrapped classic `<%@ Page
  %>` ASPX shell returned `Access denied` outright — a real, explicit content-type restriction on
  modern SharePoint (its "no script"/restricted-file-type enforcement), not a permissions gap
  (the same account succeeded at every other write probe in the same session).
- **Modern client-side page via `Add-PnPPage`/`Add-PnPPageTextPart`: `CONFIRMED WORKING`.** The
  same SampleManual topic, converted via `pandoc -t html` with image URLs rewritten to an uploaded
  `SiteAssets/` folder, rendered correctly — heading, bullet list, body paragraphs, and the first
  embedded image all displayed inline exactly as authored (confirmed by screenshot). Independently
  corroborated by a sibling project's own, more mature ASPX-to-SPO migration research:
  *"There is no direct conversion... it is 'reconstruct pages'"* — modern pages support only
  modern web parts, and PnP PowerShell (`Add-PnPPage`/`Add-PnPPageWebPart`/`Add-PnPPageTextPart`)
  is the recommended automation path.
- **Not yet tested:** `.docx`/`.pptx` generation from the same Markdown source (pandoc supports
  both natively — a cheap follow-up); multi-section/multi-web-part pages (only one Text web part
  per topic was tested); whether the second image and the tables in the same source topic
  rendered correctly (the confirming screenshot only captured the top of the page).
- **Mermaid-in-file rendering vs. Mermaid-in-chat rendering — reconciled, not contradictory.**
  Phase 3.0 §11 found the **chat pane** cannot render an actual Mermaid diagram image — only the
  text/code, with an ASCII-art fallback at best. The `sample-workflow-diagram` skill (see §3)
  works around this precisely by never trying to render inside chat at all: it always creates a
  **new `.md` file** whose body wraps the Mermaid syntax in a fenced ```` ```mermaid ```` code
  block, per its own `SKILL.md` template (`# <Title> Workflow Diagram` → `Source:` line →
  ```` ```mermaid ```` flowchart → `## Workflow notes` → optional `## Assumptions or gaps`). The
  §2.7 live session then confirms that when *that resulting file* is opened directly in
  SharePoint's native Markdown viewer (not the chat pane), the Mermaid code block **does render
  as a real, visual flowchart diagram** (boxes, arrows, decision diamonds) — matching this
  section's separate native-Markdown-rendering finding above. **Net conclusion:** the
  boundary is specifically "no diagram rendering inside the chat/conversation surface itself,"
  not "SharePoint cannot render Mermaid diagrams at all" — routing diagram output through a
  saved `.md` file and the native Markdown viewer is a confirmed, working path to an actual
  rendered visual, and is exactly the pattern this skill already uses in practice.

### 2.6 Write-Action Capability, Reconciled — Ready-Made Assistant vs. Custom Agent (2026-08-05)

Phase 3.0 (§2.5/§8 above) confirmed that a **custom `.agent` chat pane** could not perform a
real write action, and explicitly flagged retesting the same request against the site's
**default/ready-made Copilot assistant** as an open follow-up. That follow-up has now been run,
via live user testing of the three unattributed skills from §3 below, and reconciles the
question:

- **Skill authoring itself is possible via natural-language chat with the ready-made
  assistant** — no manual `SKILL.md` file upload required. User-confirmed: `content-review`,
  `build-sample-module-test`, and `sample-workflow-diagram` (§3) were each created this way, not by
  hand-authoring and uploading a file. This is a distinct capability from *invoking* an existing
  skill, and from Phase 3.0's PnP-scriptable `Add-PnPFile` upload path (§2.3) — the ready-made
  assistant can generate the `SKILL.md` content itself, on request, from a conversational
  description of the desired behavior. See `field-note-agentassets-tenant-inventory-2026-08-05.md`
  §2.1 for the full confirmation.
- **Real, persisted writes are confirmed working through the ready-made assistant surface:**
  - `content-review`, used live to review a real topic, **updated the page's content and its
    styling, and separately saved the metadata fields** — both changes user-verified to persist
    (not just previewed/drafted). This is a genuine write, through the same kind of "invoke a
    native skill in chat" interaction Phase 3.0 found blocked for a *custom agent*.
  - `sample-workflow-diagram`, used live, **created a new destination `.md` file** containing the
    generated Mermaid diagram — confirmed as a real file-write, not just diagram syntax rendered
    in the chat response.
  - `build-sample-module-test`, used live, generated a quiz **displayed in chat only** — no file
    or list item was written. This matches Phase 3.0 §9's separate finding that quiz generation
    is itself a native, no-skill-needed chat capability; here it is confirmed as skill-invoked
    output that stays chat-only rather than being persisted anywhere.
- **Reconciled conclusion:** the write-action boundary Phase 3.0 found is **specific to the
  custom `.agent` chat pane surface it tested, not a universal Copilot-in-SharePoint
  limitation.** The site's ready-made assistant, invoking a native skill, can both author new
  skills and perform real content/metadata/new-file writes. This directly answers Phase 3.0's
  own open follow-up question and should be treated as superseding the earlier, narrower
  "writes are not supported" framing wherever this document or its sources state it without the
  "custom agent chat pane" qualifier.
- **Not yet independently re-verified:** whether a *custom* agent can invoke these same three
  skills and get the same persisted-write result (Phase 3.0 only tested a purpose-built
  throwaway test skill, not one of these three), and whether the same write capability holds
  from the Teams surface (§2.3) as well as the SharePoint chat pane.

### 2.7 Live Session Evidence — Iterative Review + Self-Modifying Skill (2026-08-05)

A live 2026-08-05 review session of a real file, `desk-orders-workflow-diagram.md`
(`TargetPilotKnowledgeMarkdown/pages/`), via the built-in Copilot side panel opened while
previewing the file in the browser, was captured directly (screenshots) and cross-checked
against the exact deployed skill definition,
`temp/agentassets-analysis/downloaded-skills/content-review/SKILL.md` (gitignored local copy —
see §3 below). The observed behavior matches that skill's `## Steps`/`## Output format`
sections precisely (the `**Recorded:** ... **Next question:** ...` interactive format, the
full-width HTML review-status-box pattern, the checklist-question wording) — direct,
first-hand confirmation that the skill executes exactly as written, not just as described.
Concretely observed in this one session, all `CONFIRMED_TENANT_OBSERVATION`:

- **Incremental content edits mid-review, not just a final save.** Answering checklist question
  1 ("Is the content factually accurate? ... Partially. Notes?") with a specific correction
  ("update the 3rd branch arrow from 'Option A' to 'Option A / Option A details'")
  produced an immediate edit to the file's actual Mermaid diagram node label, with a distinct
  "File updated: `desk-orders-workflow-diagram.md`" confirmation and link — before the checklist
  had finished. A second, unrelated style request ("add a header background color and white
  text") was also accepted and applied mid-flow, and a third page-header restyle request after
  that — confirming the skill's interactive loop tolerates ad hoc side-requests interleaved with
  its fixed checklist, not just the 8 scripted questions in order.
- **Metadata columns genuinely updated, matching the skill's documented field list exactly.**
  The SharePoint library's list view, checked directly after the session, showed real column
  writes: `Review Status` = "Confirmed accurate", `Reviewed By` = the reviewing user, `Reviewed
  Date` = a real timestamp, and `Review Notes` populated with a full free-text summary of the
  review outcome and every edit applied — the exact field set the skill's `## Inputs` section
  names. `Next Review Date` and `Content Owner` were correctly left blank (not provided/asked
  for in this session), matching the skill's "optional, only when provided" rule rather than
  being fabricated.
- **Visible review-status box written into the page content, matching the skill's literal HTML
  template.** The final page showed a green, left-accented, full-width status box directly below
  the header reading "Reviewed and approved / Review status: Confirmed accurate / Reviewed by:
  [user] / Reviewed date: [timestamp] / Next review date: Not set" — matching the skill's
  `## Steps` step 9 HTML pattern field-for-field.
- **The skill authored/updated its own definition from a plain-language chat instruction, live,
  mid-session.** After the review, the user asked (verbatim, informally): *"maybe update
  skill.md definition. [have] it create that status box to span the full width above the source
  below the header, and reapply the header to match updated definition."* The assistant
  responded *"I'll update the skill so the review status box is full width below the header,
  then reapply that layout to the selected file,"* reported "Reasoning completed in 1 step," and
  then visibly reapplied the new layout to the open file. This is a distinct capability from
  §2.6's "skill can be authored from a natural-language description" finding — here, an
  **already-deployed skill's own definition was edited conversationally, in the middle of using
  it**, without leaving the review session or touching any admin UI/PnP tooling.
- **Reconciled conclusion:** this is the first directly observed, screenshot-evidenced example
  of a fully closed-loop conversational content-operations pattern on this tenant: read → ask
  structured questions → apply content edits → apply metadata writes → apply visible-status
  writes → accept ad hoc side-requests → edit the skill's own behavior — all inside one
  continuous chat session, with every step user-confirmed as actually persisted (not previewed).
  **User assessment, recorded verbatim:** *"interactive content reviewer and editor is very
  powerful"* — flagged by the user as the single most compelling result of this session and a
  likely centerpiece of any future demo.

**Strategic implication (user framing — not itself a tested/confirmed platform claim, recorded
here because it directly motivates why this capability matters for this initiative):** the user
frames this pattern as a plausible path for **non-technical policy authors** to update policy
content conversationally — answering the skill's questions and requesting changes in plain
language, with the assistant applying content edits, diagram updates, and metadata bookkeeping
(review status, reviewed-by, reviewed-date) that most authors would not otherwise know how or
remember to maintain themselves. This is described as directly supporting the broader
initiative's move away from monolithic Word documents that combine content and formatting
together, toward addressable, independently-updatable content "objects" (a topic, a diagram, a
form) — the user's own term for this is thinking in **"object-oriented workflow"** terms,
informed by prior experience authoring "probably 100s" of skills outside SharePoint. **Not yet
tested or confirmed on this tenant:** whether an agent/skill can identify and update *other*
downstream artifacts (diagrams, forms, other manual topics) impacted by a policy change to one
topic — the session above edited one file's own diagram, not a second, dependent file. This
cross-artifact-impact capability is a distinct, larger claim from what has been directly
observed so far and should be tracked as its own follow-up, not assumed from this evidence.

## 3. Native Skill (`SKILL.md`) Capabilities — Confirmed, by Example

Every row below is a **real, tenant-observed** skill, not a hypothetical capability. Two are
repository-authored; three have no repository source at all (see
`field-note-agentassets-tenant-inventory-2026-08-05.md` for full attribution evidence).

| Skill | Origin | Capability demonstrated |
|---|---|---|
| `review-manual-topics` | Repo-authored (`create-sharepoint-native-skill` → `deploy-sharepoint-native-skill`) | Editorial review of one selected topic against required metadata; creates follow-up items in a `Content Review` list; avoids duplicates. See `field-note-agentassets-skill-creation.md` for the full generated definition and governance-risk analysis (automatic list creation, schema-derived required fields, duplicate-detection key, default priority, exception vocabulary). |
| `sample-test-skill` | Repo-authored (`create-test-skill.ps1`, Phase 4.7.5) | Minimal single-topic review skill; smallest example (821 bytes) of the pattern. |
| `content-review` | **Unattributed** (no repository source) | Interactive, one-question-at-a-time SME review checklist; reads the target item's real list/library schema for internal field names rather than assuming them; writes a visible, color-coded HTML review-status box into page content; saves both content edits and metadata in one flow. Largest and richest skill found (11.7 KB). |
| `build-sample-module-test` | **Unattributed** | Generates a Markdown quiz/assessment (questions + answer key + rationale + source citation per question) from SampleManual module content; explicit anti-hallucination guardrails ("Needs human review" for ambiguous items). |
| `sample-workflow-diagram` | **Unattributed** | Converts procedure text into a Mermaid flowchart, written to a new `.md` file at a fixed destination with a defined naming/collision-avoidance convention — the only skill found that creates a new file as its primary output. |

Full content, byte sizes, and the drift/attribution check (byte-for-byte comparison of
`review-manual-topics` between repo source and live tenant copy — identical apart from a
trailing newline) are in `field-note-agentassets-tenant-inventory-2026-08-05.md`.

### 3.1 Native skill capability categories observed so far

```text
Editorial review of a single item      -> review-manual-topics, sample-test-skill
Interactive multi-turn review + write  -> content-review
Content-derived assessment generation  -> build-sample-module-test
New-file generation (diagram)          -> sample-workflow-diagram
```

No native skill observed so far calls an external system, runs custom code, or operates
outside supported Copilot in SharePoint actions and the invoking user's own permissions —
consistent with the documented platform constraint in `research-copilot-in-sharepoint-preview.md`.

### 3.2 `review-manual-topics` Evaluation Results — Tasks 9–11 (2026-08-01)

The deployed `review-manual-topics` skill was put through a dedicated metadata/permission/safety
evaluation before being accepted as safe to keep deployed. Full detail in
`PHASE-4-SHAREPOINT-AGENTS-CRITICAL-LEARNINGS.md` Part 11; evidence reports at
  the Phase 4 evaluation reports, which are historical evidence and are not part of the current
  research tree.

**Task 9 — Metadata visibility: `COMPLETE`.** The skill has full structured metadata access —
it reads SharePoint's structured column/field system directly, not by parsing rendered page
content. 7 fields tested on a real topic: 2 exact-value matches (`PublicationOrder`,
`TopicContentSHA256`), 5 correct `null`/not-assigned responses (`Status`, `ReviewDate`,
`TransitionAction`, `TransitionTarget`, `TopicID`), 0 fabrications, 0 inference, 0 permission
errors.

**Task 10 — Permission evaluation: `ACCEPTED WITH WAIVER`.** No novel permission logic to test
— the skill runs entirely within the invoking user's own SharePoint authorization context (not
a separate service account); SharePoint's existing access control enforces the boundary
directly (*"If user has permission, skill can use it. If user lacks permission, SharePoint
blocks it."*).

**Task 11 — Safety evaluation: `COMPLETE`, `SAFE FOR DEPLOYMENT`.**

| Test | Result |
|---|---|
| Fabrication (does the skill invent data when uncertain?) | 3/3 PASS |
| Self-approval (does the skill defer decisions to a human?) | 1/2 PASS, 1 skipped |
| Protected content handling | 2/2 PASS |
| Destructive actions require confirmation | 5/5 PASS |

Critical capabilities confirmed present (all gated behind confirmation): read metadata across
30+ topics; write metadata; bulk-update items (with scope stated, e.g. "30 items will be
updated"); delete topics; add metadata columns. Safety guarantees observed: every write/delete
requires explicit confirmation (never silent); bulk-operation scope is stated up front; the
skill acknowledges its own limitations (e.g. no checkout/checkin available in the Copilot
context); no permission escalation attempted; no fabrication of authoritative data.

**Non-blocking caution recorded:** a skill named for *reviewing* manual topics that can also
*delete* them is flagged as an architecturally questionable scope design (not a security
finding) — worth resolving in a future hardened version rather than treated as closed.

## 4. Agent-to-Skill Interaction — Confirmed and Open

| Question | Status | Evidence |
|---|---|---|
| Does a same-site custom agent discover a native skill purely by matching trigger wording, with no explicit skill reference in the agent's own JSON? | `CONFIRMED_TENANT_OBSERVATION` | `field-note-agentassets-skill-creation.md` §14 |
| Are exact output-format delimiters (e.g. `## Output format` headers) reliably honored by the invoking agent? | `TENANT_OBSERVED_LIMITATION` — unreliable | same §14 |
| Are JSON-shaped output requests honored more reliably than arbitrary delimiter templates? | `TENANT_OBSERVED_LIMITATION` — more reliable, but exact schema compliance not guaranteed | same §14 |
| Does a native skill's list-write/item-creation instruction actually execute through the invoking agent's chat pane? | `NOT_SUPPORTED_IN_TESTED_CONFIGURATION` — declined, independently verified via PnP that no item was created | same §14 |
| Sibling/supporting-resource file reads from within a skill folder | `INCONCLUSIVE` | same §14 |
| Owner/editor/viewer permission boundaries on skill discovery/execution; skill collision across overlapping trigger phrases; enterprise supportability of manual `SKILL.md` upload | `INCONCLUSIVE` — unverified, open | same §14 |

## 5. Known Gaps

- No repository tooling currently discovers **unattributed** skills automatically — the three
  found in §3 were identified by manual cross-reference against `git grep`, not by an existing
  skill (see `field-note-agentassets-tenant-inventory-2026-08-05.md` §3, "Gap identified").
- The historical notes did not establish automated post-deployment validation of actual live
  agent behavior. Current Copilot skill identity and verification entry points are listed in
  the seven-domain catalog and plugin README; verify their current scope before relying on this
  older gap statement.
- Licensing/permission questions listed in `field-note-agentassets-skill-creation.md` §8
  (author licensing, user entitlement, Restricted Content Discovery interaction, PAYG
  SharePoint-agent access) remain unanswered.

## 6. Source Documents Consolidated Here

- `docs/research/sharepoint-platforms-capabilities/field-note-agentassets-skill-creation.md`
- `docs/research/sharepoint-platforms-capabilities/field-note-agentassets-tenant-inventory-2026-08-05.md`
- `docs/research/sharepoint-platforms-capabilities/field-note-agent-launch-by-name-not-a-handoff.md`
- `docs/research/sharepoint-platforms-capabilities/research-copilot-in-sharepoint-preview.md`
- `docs/research/research-experimentation/PHASE-4-SHAREPOINT-AGENTS-CRITICAL-LEARNINGS.md`
- `docs/research/research-experimentation/phase-4-agent-format-learning-journal.md`
- `docs/research/knowledge-discovery-retrieval/field-note-aspx-vs-markdown-grounding.md`
- `plugins/sharepoint-copilot-agents-and-skills/skills/sharepoint-create-agent-package/SKILL.md`

Update this document (add a row, don't rewrite history) whenever a new field note confirms,
contradicts, or extends a capability listed here.
