# Phase 3.0 Write-Exploration Findings — Agent/Skill/Template Capability Discovery

Log of hands-on, authorized capability discovery performed directly on the BC Gov dev site
(`AG-CSB-INTRANET-DEV`), moving beyond the read-only `phase-3-0-tenant-discovery.ps1` script into
staged, reversible write actions. Site owner (user) explicitly authorized this as an active
capability-discovery exercise. All artifacts below are labeled `TEST-DO-NOT-USE-*` and are
reversible/removable per the staged-write protocol
(`docs/vision/master-initiative-plan-workstreams-and-phases.md`, Subphase 3.0.2).

**App registration constraint in effect throughout:** `ag.csb.cmat.interactive` is intentionally
manage-only (no permission-management rights). Findings below reflect what this specific
delegated-permission profile can do, not a blanket "any SharePoint account" claim.

Evidence source for this doc: raw JSON/script output stays local
(`tools/phase-3-sharepoint-discovery/`, gitignored where tenant-specific); this file is the
sanitized, committable summary.

---

## Executive Summary (for external review — e.g. asking GPT-5.6 what else to test)

**Setup:** a document library and a `.agent` file were created on a real BC Gov dev SharePoint
site, both entirely via PnP PowerShell (no Copilot UI wizard). Real content was then added: a
small synthetic test file with a planted secret keyword, and later the **actual real CEIS manual
rendered output** (25 of 26 topic pages + 111 images from the `docx-to-content` plugin's Phase 1
pilot deliverable). Eight custom `SKILL.md` skill variants were authored and uploaded to
`AgentAssets/Skills/` to probe format-compliance and capability boundaries, then tested live
through the agent's chat pane in the browser.

### Confirmed working capabilities (tempered per external review — see "Scope corrections" below)
1. **Document libraries, lists, and custom fields** are fully scriptable via PnP PowerShell
   (`New-PnPList`, `Add-PnPField`) even under a manage-only (no permission-management) app
   registration.
2. **`.agent` files are plain JSON** (schema `0.2.0`) and can be hand-authored and uploaded via
   `Add-PnPFile` with no Copilot UI wizard involved — the resulting agent is fully functional in
   this tested tenant/session: renders correctly, its `OneDriveAndSharePoint` source binding
   works, and it grounds and cites real content correctly (proven with a planted keyword test,
   then with real manual content). **Classification: technically viable in the tested tenant;
   no supported deployment interface established** — see correction #3.
3. **`SKILL.md` native skills were automatically discovered by the tested same-site custom
   agent** through trigger wording, once dropped in `AgentAssets/Skills/<name>/SKILL.md` — with
   no explicit skill reference in that agent's own `.agent` JSON. See correction #2 for what this
   does and doesn't prove.
4. **Native Markdown rendering works well** — SharePoint's built-in Markdown viewer correctly
   renders headings and turns relative Markdown links into working in-viewer navigation between
   topic files, plus surfaces contextual Copilot suggestion chips automatically. This resolves a
   previously-flagged manual-only verification item from the read-only discovery script.
5. **Multi-document synthesis across real manual content is high quality**: asked to relate two
   real CEIS topics (warrants, protection orders), the agent correctly identified 3 relevant
   source files, synthesized an accurate, domain-specific answer (correct form names/codes),
   cited every claim, and explicitly avoided overclaiming a causal relationship the source
   material didn't support.
6. Built-in Copilot behaviors work without any custom skill: **quiz generation** from grounded
   content, and **Mermaid syntax generation** (though not rendering, see limitations).

### Confirmed limitations (tempered per external review — see "Scope corrections" below)
1. **In the tested custom `.agent` chat-pane invocation path, list and document write actions
   were unavailable.** Asked directly (via a skill designed to create a SharePoint list item) and
   asked generally ("summarize your capabilities"), the agent consistently and correctly
   self-reported that it cannot create/modify list items or documents — verified independently
   via PnP that no item was silently created. **This is a `CONFIRMED_TENANT_OBSERVATION` for this
   invocation path only** — it does not establish that all custom agents, all Copilot-in-SharePoint
   experiences, or native-skill invocation through other surfaces can never write. See correction
   #1 and Priority 2 in the follow-up backlog below.
2. **A skill's `## Output format` section is a stylistic bias, not an enforced contract**, in the
   tested invocation path. Tested 4 formatting strategies (custom ASCII delimiters, few-shot
   example, strict JSON, external template file reference): JSON-schema requests were honored
   most reliably; custom delimiter templates were consistently ignored in favor of the model's
   own native `Q:`/`A:`/bullet style; an externally-referenced template file was **not read
   literally** — the agent fabricated a plausible-looking field name instead of quoting the real
   file content (a real hallucination-of-structure risk, not just imperfect formatting). Not yet
   isolated from the confounding source-scope failure in the `assets/`-subfolder test — see
   Priority 4 below.
3. **No image/diagram rendering in the chat pane.** The agent can generate Mermaid syntax or
   ASCII-art layouts but explicitly cannot render an actual image/SVG — text-only output surface,
   for this invocation path.
4. **The tested agent's *knowledge retrieval* is strictly bounded by its attached `Sources`.**
   It could not enumerate/derive content outside what was explicitly added (e.g. couldn't list
   other site libraries when only one library was attached as a source). **This is a knowledge-
   retrieval-scope finding, not a proven general claim about SharePoint action/tool capability or
   about the current user's own SharePoint permissions** — those are three distinct things that
   this test did not separate. See correction #4.
5. There is no distinct "output template" artifact type — it's just a skill's own
  `## Output format` markdown section; no separate PnP cmdlets exist for authoring
  agents/skills/templates as first-class object types (only `Get-PnPCopilotAgent`, read-only,
  which — per Microsoft's docs — cannot inventory a site's complete agent experience anyway,
  since the ready-made/default site agent has no `.agent` file to enumerate).

### Scope corrections from external review (2026-07-29) — read before citing any finding above

An external review (requested from GPT-5.6) of this document's findings identified four places
where our stated conclusions were broader than the evidence actually supports. Corrected framing:

1. **Custom-agent write failure is a `CONFIRMED_TENANT_OBSERVATION`, not a universal platform
   boundary.** What was proven: *this* custom `.agent` chat pane, in *this* tenant/ring, with
   *this* user/app permission profile, with *this* source configuration, through *this*
   invocation path, did not perform list/document writes. What was **not** proven: that all
   custom SharePoint agents, all Copilot-in-SharePoint experiences, all native skills, across all
   tenants/rings/licensing configurations, can never write. Microsoft's current Copilot-in-
   SharePoint documentation describes capabilities for creating sites, pages, lists, libraries,
   reports, files, and workflows, and agents/native skills have different execution surfaces and
   permission models than what we tested. **Recommended wording going forward:** "In the tested
   custom `.agent` chat-pane invocation path, list and document write actions were unavailable.
   The agent declined accurately, and independent PnP verification confirmed no write occurred.
   Whether native Copilot-in-SharePoint skill invocation supports bounded writes through a
   different surface remains unverified."
2. **"Site-wide skill auto-discovery" is slightly overclaimed.** What was proven: a `SKILL.md` in
   `AgentAssets/Skills/` was discovered by the tested custom agent, on the same site, when
   prompted with a matching trigger phrase. What was **not** proven: discovery by every agent on
   the site, by the ready-made/default agent, by users with different permissions, from every
   SharePoint context, across sites, when the skill file has unique permissions, or when several
   skills compete for the same trigger. **Recommended wording:** "Native skills were
   automatically discovered by the tested same-site custom agent through trigger wording, without
   an explicit skill reference in that agent's `.agent` JSON." This remains a major result — just
   not a universal one.
3. **"Fully scriptable agent authoring" needs a supportability qualifier.** Hand-authored `.agent`
   JSON uploaded via `Add-PnPFile` was genuinely parsed and functioned — but the schema was
   reverse-engineered (not documented by Microsoft), PnP exposes retrieval (`Get-PnPCopilotAgent`)
   but no dedicated agent-creation cmdlet, generic file-upload success does not establish a
   supported deployment contract, and a future product update could change validation/schema
   expectations without notice. **Classification going forward:** technically viable in the
   tested tenant; supported deployment interface not established; suitable for future controlled
   adapter research; **not yet an operational deployment contract.**
4. **Agent-source scope must be separated from platform capability scope.** The library-
   enumeration test did not prove agents fundamentally cannot enumerate libraries — it proved the
   tested agent could not derive libraries outside its attached source scope from grounded
   content alone. Three distinct things must not be conflated: (a) knowledge retrieval scope
   (what the agent was configured to see), (b) SharePoint action/tool capability (what the
   platform can technically do), and (c) the current user's own SharePoint permissions (what the
   underlying account can access). Microsoft's agent documentation notes agents answer from
   configured sources the user can access, and that selecting a hub can expand source scope to
   associated sites — a dimension we have not yet tested (see Priority 8 below).

### Not yet tested / open questions — superseded by the prioritized backlog below

The bullet list originally here has been absorbed into and superseded by the structured,
prioritized backlog from the 2026-07-29 external review, below — kept only as a pointer.

### Prioritized follow-up test backlog (from 2026-07-29 external review)

This is the next round of tests to run, in priority order, before treating any current finding
as a stable basis for pilot/production design decisions. Framed as **falsification and lifecycle
testing**, not additional happy-path feature exploration — the goal is to find where current
conclusions break, not to accumulate more confirming examples.

**Priority 1 — permission-boundary matrix for agents and skills.** Highest risk-reduction value
of any remaining test. Use ≥3 identities: (A) site owner/editor/agent author, (B) intended
reader/viewer, (C) a user without access to one source/folder (if approved). For each identity,
test: can they discover the agent; open the `.agent` file; edit the agent; invoke each skill;
read `SKILL.md` directly; modify/replace `SKILL.md`; retrieve restricted source content through
the agent; do titles/citations/filenames/summaries/starters leak inaccessible information; does
discovery change after breaking `AgentAssets` inheritance; does execution run as the caller or as
the skill author. **Exit evidence:** an expected-vs-actual matrix. Any inaccessible
filename/title/citation/content surfacing for the restricted identity is a blocking finding.

**Priority 2 — ready-made/default Copilot vs. custom `.agent`.** Now the most important
capability-boundary test, since it directly resolves the discrepancy between the real
`review-manual-topics` skill's list-write description and our custom agent's write refusal.
Repeat identical requests (grounded keyword retrieval, list-item write, document modification,
skill invocation, strict JSON output, out-of-scope refusal, quiz generation, cross-topic
synthesis) across: (A) custom hand-authored `.agent`, (B) custom UI-created `.agent`, (C) the
ready-made/default site agent, (D) the native Copilot-in-SharePoint site/library pane if
distinguishable from (C). Record per surface: same skill discovered; write capability claimed;
write actually performed; same sources retrieved; consistent citation; `discourage_model_
knowledge` honored; unsupported actions handled honestly.

**Priority 3 — skill collision and routing.** Build a controlled collision set: (A) exact
trigger phrase, (B) overlapping trigger phrase, (C) broad generic description, (D) same name in
a different folder, (E) malformed frontmatter, (F) inaccessible to the caller. Test exact
invocation, paraphrase, ambiguous-match, broad-match, case/punctuation variation, follow-up
without repeating the trigger, renamed skill, removed-after-prior-use, and conflicting
agent-vs-skill / skill-vs-skill instructions. Capture requested wording, selected skill (if
observable), response behavior, citation/source scope, whether ambiguity was disclosed, and
which instructions prevailed. Goal: discover whether routing is predictable enough for a
governed pilot — not to reverse-engineer an undocumented algorithm.

**Priority 4 — skill asset retrieval, isolated properly.** Our `assets/`-subfolder test (§10/12)
was confounded by an unrelated source-scope failure and never actually isolated whether asset
files are read literally. Retest with a read-only skill with no unrelated source requirement,
three variants (`Skills/test-flat/template.txt`, `Skills/test-assets/assets/template.txt`,
`Skills/test-references/references/template.md`), each containing a unique high-entropy planted
token (e.g. `FLAT-ASSET-731`, `ASSETS-SUBFOLDER-842`, `REFERENCES-SUBFOLDER-953`). Ask the skill
to quote only the token and filename. Run negative controls: token absent from agent sources;
token only in the asset file; asset permission removed from viewer; asset renamed after skill
creation; duplicate token in two locations. Classify each as: literal retrieval confirmed /
inferred structure only / asset invisible / permission-trimmed / ambiguous. **Do not accept a
plausible field name as evidence — only a planted high-entropy token proves literal access**
(this is exactly the failure mode our v4 test already exposed once).

**Priority 5 — embedded media and link fidelity.** Open real topic pages exercising the actual
CEIS profile: image-heavy topic, nested relative image path, spaces/special characters in
filenames, table-heavy topic, deep heading hierarchy, cross-topic relative link, broken-image
negative control, missing-target negative control, image alt text, duplicate image name in
different folders. Check separately: browser viewer rendering, browser editor/split rendering,
agent retrieval of surrounding text, agent awareness of alt text, agent citation of the topic,
agent ability to describe image content if supported. Do not assume chat-pane image reproduction
just because the browser page displays it — text-only chat behavior (§11) and native browser
Markdown rendering (§13) are separate, already-distinguished results.

**Priority 6 — agent lifecycle through raw file operations.** Before considering any "agent
factory," test the full lifecycle, not just creation: upload valid `.agent` → confirm
visibility/use → modify instructions via `Set-PnPFileContent` (or approved equivalent) → confirm
when the new behavior becomes visible → change source binding → confirm old source content is no
longer retrievable → rename → move to another folder/library → replace with malformed JSON →
restore previous version → delete → restore from recycle bin (if authorized) → confirm links/
approval/default-state/usage-history behavior after each step. Capture observed propagation
delay (without assuming a service guarantee), file version, availability, staleness, rollback
result, whether deletion removes usability immediately, whether malformed content fails closed.
This determines whether generic file operations are safe enough to form a controlled deployment
adapter — directly informs correction #3 above.

**Priority 7 — `.agent` schema mutation suite.** Treat the reverse-engineered schema (§3) as a
contract *candidate*, not a contract, and mutate one field at a time: missing `schemaVersion`;
unsupported `schemaVersion`; missing `customCopilotConfig`/`gptDefinition`/`name`; empty
instructions; unknown top-level property; unknown capability; invalid GUID; wrong list ID;
URL/GUID mismatch; invalid source type; duplicate source entries; missing `unique_id`; non-zero
valid `unique_id`; invalid `discourage_model_knowledge` type; oversized instruction text;
malformed JSON. For each: record whether upload is accepted/rejected, file opens or not, Edit UI
parses or not, agent launches or not, source binding displays or not, grounded query succeeds or
not, error shown to user, whether failure is silent. This will show which fields are actually
load-bearing — the all-zero `unique_id` working once (§3) does not prove it's universally
optional.

**Priority 8 — source-scope variants.** Build separate agents for: one file; one folder; one
library; current site; another authorized site; hub site; mixed source items; 20 source items
(Microsoft's documented current limit); an attempted 21st item if safe/approved; one source
inaccessible to the test reader. Test source-selection fidelity, retrieval outside the intended
folder, hub associated-site expansion, inaccessible-source trimming, stale-source removal,
duplicate sources, and correct source attribution in citations. The hub test is particularly
important — it can broaden grounding beyond what the `.agent` designer assumed, and we have not
tested it at all (directly relevant to correction #4 above).

**Priority 9 — Restricted Content Discovery (RCD) behavior.** If a tenant administrator can
observe or run the approved test, compare the same site before/after RCD through authorized
processes: custom agent availability, ready-made agent availability, Copilot entry points, skill
invocation, org-wide search, site-context search, direct file access, existing permissions,
propagation behavior, removal/recovery behavior. RCD suppresses org-wide discovery and AI entry
points but does not change permissions or remove content from the search index — this needs
tenant-admin-level access we don't currently have (already flagged as `Forbidden` in the
read-only discovery script's output), so this priority may remain blocked pending admin
involvement.

**Priority 10 — Teams cross-surface parity (added 2026-07-30, from official Microsoft doc, see
§18).** Every finding in this document was tested through the SharePoint chat-pane surface only.
Microsoft's own documentation confirms the same custom `.agent` is independently discoverable
and usable from the Microsoft Teams app store (added to a chat/channel/meeting, or shared as a
message preview). Repeat the core test battery (grounded retrieval, write-action request, skill
invocation, format compliance, refusal logic, quiz generation) via the same agent accessed from
Teams instead of SharePoint, and record whether behavior/sources/citations are identical or
whether the Teams host surface changes anything (different app-permission prompts, different
citation/image rendering, different write-capability surface). **Exit evidence:** a side-by-side
transcript comparison, SharePoint chat pane vs. Teams, for each test in the battery.

**Note:** the external review's message was truncated after Priority 9 (ended mid-sentence,
"This—"). If a Priority 10 (from that same original review) or 11+ exists beyond what's
captured here, incorporate it when available — the Priority 10 above was added independently
from a separate Microsoft documentation source, not from the truncated review.

**Priority 11 — Autofill authority testing (added 2026-07-30, from a GPT-5.6 summary of the
YouTube video "I Tested the SharePoint Knowledge Agent: Here's What It Can Do," see §19).**
Add one low-risk, explicitly AI-maintained metadata column to the test library, run SharePoint's
native Autofill against several real CEIS topics, change one topic and observe whether Autofill
updates its value, and confirm Autofill never alters deterministic package fields (`TopicID`,
`ChunkID`, `PackageIdentity`, `TopicContentSHA256`, `PublicationOrder`). Test across Draft/
Published/Retired items and under two different permission identities; record whether the
generated value is a proposal a human must approve, an auto-applied value, or both. **Exit
evidence:** confirmation that SharePoint's AI metadata enrichment can safely coexist with the
structured field-authority matrix without any deterministic field ever being silently overwritten.

**Priority 12 — Agent-optimized rendering target (added 2026-07-30, from user design idea, not
yet phase-scoped).** Today's per-agent 20-source-item limit (§16) rewards fewer, denser items.
Rather than relying solely on folder-nesting to work around the ceiling, evaluate a genuinely
new Renderer output: a compact, agent-optimized artifact (flat terminology, explicit cross-
references instead of "see above," no reliance on visual formatting) distinct from the existing
human-oriented Markdown/ASPX renders. The agent-facing render would be the one actually indexed
as the agent's grounding source; its answers/chunks would explicitly point people to the richer
human-formatted Markdown or ASPX version and to non-indexed source links for full detail. This
is a Content + Template + Renderer extension (a second renderer target alongside human-Markdown
and ASPX) — a real idea worth prototyping in a later phase, not yet built or scoped to a
specific phase.

## 19. External research video — "I Tested the SharePoint Knowledge Agent: Here's What It Can Do"

**Source:** YouTube video [tVgZErn-dkE](https://www.youtube.com/watch?v=tVgZErn-dkE), summarized
by GPT-5.6 (2026-07-30) from the video's title, description, feature list, and chapter
timestamps — **a chapter-level summary, not a full transcript**; treat capability claims as
indicative, not independently verified against our own tenant.

**Capabilities demonstrated (per the summary), with chapter timestamps:**
1. **AI-generated library metadata** (~0:50) — AI examines document content and proposes
   metadata values to support filtering/organization/automation.
2. **Autofill** (~7:08) — keeps that AI-generated metadata updated automatically as content
   changes.
3. **Natural-language rules** (~9:01, reviewed ~14:05) — create simple automation rules by
   describing them in plain language.
4. **AI-assisted filtered views** (~16:07) — construct custom SharePoint views (e.g. Published/
   Draft/Retired/By-owner/Overdue-review) using natural language plus existing metadata.
5. **Content Q&A** (~17:26) — ask questions grounded in library content; this is the capability
   category our own tenant testing (§1-18) goes materially deeper on (manually authored `.agent`
   JSON, native `SKILL.md` discovery, planted-token retrieval, citations, source boundaries,
   format-compliance limits, write-action refusal, multi-topic synthesis).

**Setup requirements stated in the video:** a Microsoft 365 Copilot license, plus administrator
opt-in to the preview at time of recording — treat as a snapshot of that recording's product
state; current official Microsoft documentation (§16-18) remains the authority for our tenant.

**Why this matters for our architecture:** the video reinforces (does not change) the layered
model already established in this document —

```text
Repository workbench   → authoritative content, identities, validation, packages
SharePoint              → governed storage, operational metadata, views, review, discovery
SharePoint agents       → permission-aware Q&A and synthesis over approved sources
Native SharePoint skills → reusable, site-scoped procedures within the supported runtime
```

The one genuinely new idea is the **Autofill vs. structured-authority boundary**: AI-generated
descriptive metadata (subject, audience, category, summary) is a legitimate SharePoint-native
enrichment layer, but it must never be allowed to compete with or silently overwrite the
deterministic package fields (`TopicID`, `ChunkID`, `PackageIdentity`, `TopicContentSHA256`,
`PublicationOrder`) that this repository's structured pipeline is the sole source of truth for.
This is now captured as **Priority 11** in the backlog above.



### Technical mechanics — how each capability was actually exercised (for reproducing/extending tests)

**Environment:** macOS, PowerShell 7.7.0-preview.3 (`pwsh`, installed via
`brew install --cask powershell` → resolves to `powershell@preview`), `PnP.PowerShell` module
`3.3.0`. App registration `ag.csb.cmat.interactive` — intentionally manage-only (no
permission-management rights); confirmed this does NOT block list/library/field/file creation,
only permission/role-assignment reads and tenant-admin-tier calls.

**Auth pattern** (used for every script in this session):
```powershell
$config = Import-PowerShellDataFile -Path ./config.psd1   # ClientId, TenantId, SiteUrl
Connect-PnPOnline -Url $config.SiteUrl -ClientId $config.ClientId -Tenant $config.TenantId `
  -Interactive -ForceAuthentication -ErrorAction Stop
```

**1. Library/list/field creation (write-capable, confirmed):**
```powershell
New-PnPList -Title 'Name' -Template DocumentLibrary -EnableVersioning -EnableContentTypes
New-PnPList -Title 'Name' -Template GenericList
Add-PnPField -List 'Name' -DisplayName 'Notes' -InternalName 'Notes' -Type Note -AddToDefaultView
```
Note: `Add-PnPList` does not exist (a plausible-but-wrong guess); `New-PnPList` is correct.
SharePoint auto-generates the URL path by stripping hyphens from the title (title and
server-relative URL diverge — don't assume they match).

**2. File/folder upload (used for `.agent`, `SKILL.md`, and real content files):**
```powershell
Resolve-PnPFolder -SiteRelativePath 'AgentAssets/Skills/my-skill-name'   # creates folder if absent
Add-PnPFile -Path <local-file> -Folder 'AgentAssets/Skills/my-skill-name' -NewFileName 'SKILL.md'
```
For recursive folder upload (used for the 348-file CEIS manual output): `Get-ChildItem -Recurse
-File`, then loop calling `Resolve-PnPFolder` per subfolder + `Add-PnPFile` per file, preserving
relative paths manually (no built-in "upload whole folder" cmdlet in PnP.PowerShell for this).

**3. `.agent` file format** — plain JSON, `schemaVersion: "0.2.0"`, top-level
`customCopilotConfig` containing:
- `conversationStarters.conversationStarterList[]` (`{text}`) + `welcomeMessage.text`
- `gptDefinition.name`, `.description`, `.instructions`
- `gptDefinition.capabilities[]` — knowledge-source binding, e.g.
  `{"name":"OneDriveAndSharePoint","items_by_url":[{"url","name","site_id","web_id","list_id","unique_id","type":"Folder"}]}`
  — `site_id`/`web_id`/`list_id` are real tenant GUIDs (readable via `Get-PnPSite`/`Get-PnPWeb`/
  `Get-PnPList`); copying them from an existing library's GUIDs into a hand-authored file worked
  fine; `unique_id` was left as the observed placeholder `00000000-...-000000000000` with no ill
  effect.
- `gptDefinition.behavior_overrides.special_instructions.discourage_model_knowledge` (boolean) —
  real, functioning flag to bias the agent away from general model knowledge.
- `icon` — optional base64 PNG data URI, cosmetic only, omitted with no functional issue observed.
Full real examples saved at `tools/phase-3-sharepoint-discovery/agents/*.agent.json` (one
UI-wizard-created, one hand-authored — both proven functional).

**4. `SKILL.md` format** — Markdown with YAML frontmatter:
```yaml
---
name: skill-name
description: |-
  What it does. Use when the user says: "trigger phrase one" / "trigger phrase two"
---
```
Body sections observed/used: `# Title`, `## When to use`, `## Inputs`, `## Steps` (numbered,
prescriptive), `## Output format` (Markdown/prose describing the desired structure — NOT
reliably enforced, see limitations above). The real pre-existing skill
(`review-manual-topics`, reverse-engineered — saved at
`tools/phase-3-sharepoint-discovery/skills/reference-real-skill-review-manual-topics.SKILL.md`)
additionally describes SharePoint list-creation/item-creation steps in prose; whether those
list-write steps actually execute (vs. just get described back to the user, as our v6 write-test
found) is one of the open questions above.

**Folder convention:** only confirmed pattern is flat —
`AgentAssets/Skills/<skill-name>/SKILL.md` (matches the one pre-existing real skill found on the
tenant). We also tried co-locating a sibling template file flatly
(`AgentAssets/Skills/<name>/output-template.txt`, not reliably read — see limitations) and in an
`assets/` subfolder (`AgentAssets/Skills/<name>/assets/template.txt`, inconclusive — the test that
would have isolated this failed for a different reason first). No official convention/docs found
for template subfolders; this remains genuinely open.

**No PnP write cmdlets exist for:** agent creation (`Get-PnPCopilotAgent` is read-only; no
`New-PnPCopilotAgent`), skill authoring, or output-template authoring as first-class object
types — everything in §3/§4 above works only because `.agent`/`SKILL.md` are plain files
uploadable via the generic `Add-PnPFile` cmdlet, not because PnP has dedicated support for them.

**All 8 test skills, both test agents, and all local reference copies** (pretty-printed JSON,
`.SKILL.md` files) are saved under `tools/phase-3-sharepoint-discovery/{agents,skills,reports}/`
in this repo for direct inspection/reuse.

---

## 1. Document library creation — scriptable (confirmed)

- Cmdlet: `New-PnPList -Title <string> -Template DocumentLibrary -EnableVersioning -EnableContentTypes`
  (NOT `Add-PnPList` — that cmdlet doesn't exist).
- Created `TEST-DO-NOT-USE-Agent-Pilot` successfully via PnP PowerShell with the manage-only app
  registration.
  - List ID: `a2750381-6274-4f02-aed1-cfd9069b0f30`
  - Auto-generated URL: SharePoint strips hyphens from the title for the folder path
    (`TEST-DO-NOT-USE-Agent-Pilot` → `/TESTDONOTUSEAgentPilot`) — titles and server-relative URLs
    diverge; don't assume they match when scripting downstream references.
  - `BaseTemplate = 101` (standard Document Library), versioning + content types enabled as
    requested.
- **Conclusion:** library creation and permission management are separate rights. This account
  can create libraries even though it cannot manage permissions/role assignments (confirmed
  `Forbidden` on `RoleAssignments` in the read-only discovery script).

## 2. Copilot agent creation via SharePoint UI — confirmed, produces a `.agent` file in-place

- Using the **Copilot** button in the document library's command bar → "Create an agent" (or
  similar), the user created an agent named `TEST-DO-NOT-USE-Pilot-Agent`.
- Result: a file named `TEST-DO-NOT-USE-Pilot-Agent.agent` appeared **directly inside the
  triggering document library itself** (`TEST-DO-NOT-USE-Agent-Pilot`), NOT inside the site's
  `AgentAssets` library.
- **Key finding:** `.agent` files are not required to live in a library specifically named
  `AgentAssets`. Any document library can host an agent definition file. (`AgentAssets` may still
  be a *convention* SharePoint/Copilot defaults to in other flows — e.g. the pre-existing
  `review-manual-topics/SKILL.md` found by the read-only discovery script lived under
  `AgentAssets/Skills/...` — but agent creation from a library's own Copilot button drops the
  `.agent` file into that same library.)

## 3. `.agent` file format — reverse-engineered from a real, UI-created file

Downloaded and inspected the real `.agent` file. It is a **plain JSON file**, not a proprietary
binary format. Structure (fields observed, values redacted/genericized where tenant-specific):

```json
{
  "schemaVersion": "0.2.0",
  "customCopilotConfig": {
    "conversationStarters": {
      "conversationStarterList": [
        { "text": "Summarize recent items" },
        { "text": "Tell me more about..." },
        { "text": "How can you help me?" }
      ],
      "welcomeMessage": { "text": "Ask a question or get started with one of these prompts:" }
    },
    "gptDefinition": {
      "name": "TEST-DO-NOT-USE-Pilot-Agent",
      "description": "purpose description of TEST-DO-NOT-USE-Pilot-Agent",
      "instructions": "Provide accurate information about the content in the selected files and reply in a formal tone.",
      "capabilities": [
        {
          "name": "OneDriveAndSharePoint",
          "items_by_sharepoint_ids": [],
          "items_by_url": [
            {
              "url": "https://bcgov.sharepoint.com/sites/AG-CSB-INTRANET-DEV/TESTDONOTUSEAgentPilot",
              "name": "TEST-DO-NOT-USE-Agent-Pilot",
              "site_id": "<guid>",
              "web_id": "<guid>",
              "list_id": "<guid>",
              "unique_id": "00000000-0000-0000-0000-000000000000",
              "type": "Folder"
            }
          ]
        }
      ],
      "behavior_overrides": {
        "special_instructions": { "discourage_model_knowledge": true }
      }
    },
    "icon": "data:image/png;base64,<...>"
  }
}
```

Notable fields:
- `gptDefinition.capabilities[].name = "OneDriveAndSharePoint"` — the knowledge-source binding;
  points at a specific library/folder by `site_id`/`web_id`/`list_id` + URL, not just a URL string.
- `behavior_overrides.special_instructions.discourage_model_knowledge` — a real, present flag
  controlling whether the agent leans on general model knowledge vs. only grounded content. Useful
  for future CEIS-manual-grounded agent design (we'd want this `true` to force citation-grounded
  answers).
- `icon` is an embedded base64 PNG data URI — cosmetic, not required for function (omitted in our
  own test file below with no apparent issue at upload time, though UI *rendering* correctness
  wasn't independently confirmed at time of writing).
- No skill or template reference field observed in this particular file — a plain
  knowledge-grounded agent with no skill/action attached. Confirms skills/templates are likely a
  separate reference mechanism not yet exercised in this test.

## 4. Programmatic `.agent` file creation via PnP — confirmed upload succeeds

- Constructed a second, equivalent JSON file by hand (same schema, own `name`/`description`,
  pointed at the same library's `site_id`/`web_id`/`list_id`), and uploaded it with:
  ```powershell
  Add-PnPFile -Path <local-file> -Folder 'TESTDONOTUSEAgentPilot' `
    -NewFileName 'TEST-DO-NOT-USE-Copilot-CLI-Agent.agent'
  ```
- **Upload succeeded** — no rejection, no special content-type/registration step required at the
  file-write layer. `.agent` is just a file extension recognized by the SharePoint/Copilot UI, not
  a server-enforced schema-validated content type (at least not at basic upload time).
- **CONFIRMED FUNCTIONAL (shell only):** opening the hand-authored file in the browser launched a
  real, working agent chat panel — correct agent name, personalized greeting, and our custom
  `welcomeMessage`/`conversationStarterList` text rendered exactly as authored (not the UI
  wizard's defaults).
- **KNOWLEDGE GROUNDING — CONFIRMED WORKING (revised from earlier negative finding):** the
  earlier failed "What is this library for?" test was misleading — the library had 0 content
  items at that point (only `.agent` files), so there was nothing to ground on. The Edit Agent UI
  (Overview/Sources/Behavior tabs) confirmed the hand-authored JSON's `name`, `description`,
  `OneDriveAndSharePoint` source binding (`TEST-DO-NOT-USE-Agent-Pilot` folder correctly listed
  under Sources), welcome message, starter prompts, and instructions all parsed **perfectly** —
  identical fidelity to a UI-wizard-created agent.
  - **Definitive grounding test:** uploaded `test-content.md` (via `Add-PnPFile`) containing a
    unique planted string, `PINEAPPLE-DISCOVERY-42`, into the same library. Asked the
    hand-authored agent: *"What is the secret test keyword mentioned in the library's test
    document?"* It answered correctly — `PINEAPPLE-DISCOVERY-42` — **with a citation back to
    `test-content.md`**.
  - **Conclusion (confirmed, not hypothesis):** a `.agent` JSON file authored entirely outside the
    Copilot UI wizard (hand-written, uploaded via `Add-PnPFile`) is **fully functional**: it
    renders correctly, its knowledge-source binding is correctly registered, and it retrieves and
    cites real grounded content. No additional registration/indexing step, Graph API call, or
    special `unique_id` was required beyond copying the `site_id`/`web_id`/`list_id` values from
    an existing library. This is full, working, end-to-end scriptable agent authoring.
- **Implication for the broader initiative:** this opens a real, evidence-backed path to a future
  "agent factory" — generating one `.agent` JSON per manual/topic-set from our `docx-to-content`
  plugin's structured/rendered output and batch-uploading via PnP, rather than manually
  building each agent one-by-one through the Copilot UI wizard. NOT yet authorized or in scope
  beyond this discovery — would need its own reviewed spec (naming conventions, source-folder
  layout, instruction/behavior templating, `discourage_model_knowledge` policy, versioning/update
  strategy for regenerated agents) before any real implementation.

## 5. Skill (`SKILL.md`) and output-template authoring — not yet attempted this session

No PnP write cmdlet exists for creating/authoring:
- Copilot Agent `.agent` files (via a dedicated cmdlet — only raw file upload, per §4 above)
- Native `SKILL.md` skill definitions in `AgentAssets`
- Output templates in `AgentAssets`
- Wiring a template + skill into an agent's configuration

These remain exclusively Copilot-in-SharePoint browser UI / Copilot Studio actions as far as
discoverable PnP cmdlets go (`Get-Command -Module PnP.PowerShell -Name '*Copilot*','*Agent*','*Skill*'`
returns only `Get-PnPCopilotAgent`, `Get-PnPCopilotAdminLimitedMode`,
`Set-PnPCopilotAdminLimitedMode` — no creation cmdlets). Whether a skill or template can be
authored the same way agents were (as a plain file drop, by reverse-engineering the format from an
existing example) has NOT been tested yet — next step.

## 6. Output-template enforcement via `## Output format` — partial compliance only

- Confirmed `AgentAssets` has no separate "template" file type/folder — `Get-Command
  -Module PnP.PowerShell -Name '*Template*'` only returns unrelated PnP **site-provisioning**
  template cmdlets (`New-PnPSiteTemplate`, etc.), and `AgentAssets`'s root only contains
  `Forms`/`Skills`, no `Templates` folder. **An "output template" is just the `## Output format`
  section inside a skill's `SKILL.md`** — there is no distinct template artifact type.
- Authored a deliberately rigid test skill, `test-do-not-use-strict-format`
  (`skills/example-skill-strict-format.SKILL.md`), whose `## Output format` demands an exact,
  unusual ASCII-delimited template (`>>> DISCOVERY-TEMPLATE-START <<<` / `QUESTION::` /
  `ANSWER::` / `CONFIDENCE::` / `SOURCE-FILE::` / `>>> DISCOVERY-TEMPLATE-END <<<`), uploaded via
  `Add-PnPFile` to `AgentAssets/Skills/test-do-not-use-strict-format/SKILL.md` (no
  `Resolve-PnPFolder` issues — folder auto-created cleanly).
- Asked the same hand-authored agent: *"Use the strict test format to answer: what is the secret
  test keyword in the library's test document?"*
  - **Skill auto-discovery: CONFIRMED.** The agent found and used the skill automatically —
    no explicit "attach this skill" step in the agent's config was needed. Response was headed
    "Strict Test Format" (the skill's `name`), and correctly grounded/cited `test-content.md` for
    the keyword `PINEAPPLE-DISCOVERY-42`. This means skills in `AgentAssets/Skills/` are
    auto-discoverable site-wide by trigger phrase, not scoped only to an agent's own attached
    sources.
  - **Exact template compliance: FAILED.** The agent did NOT reproduce our literal
    `>>> DISCOVERY-TEMPLATE-START <<<` / `QUESTION::` / etc. structure. Instead it answered in its
    own native bullet-point/citation style (`Document: test-content.md`, `Secret Test Keyword:
    ...`, `Source: ...`).
- **Conclusion:** Copilot in SharePoint treats a skill's `## Output format` section as a **loose
  behavioral hint that influences tone/structure**, not a hard-enforced literal template. It
  clearly picked up the *intent* (structured, labeled answer with a cited source) but reformatted
  it into its own native SharePoint Copilot citation/bullet conventions rather than the exact
  delimiters we specified. Do not rely on `SKILL.md` output-format sections for byte-exact
  structured output (e.g. machine-parseable text) — they bias formatting, they don't guarantee it.
  This is directly relevant to any future plan to have a SharePoint agent produce
  strictly-structured output (e.g. JSON, a fixed report schema) from CEIS-manual content: expect
  to need downstream validation/post-processing rather than trusting exact compliance.

## 7. Format-compliance A/B test — four variants compared

Ran the same underlying question ("what is the secret test keyword...") through three format
variants, plus a fourth actionable ("list libraries") skill, all attached to the same
`TEST-DO-NOT-USE-Copilot-CLI-Agent`:

| Variant | Approach | Result |
|---|---|---|
| v1 baseline | Custom ASCII delimiters, abstract placeholders | Ignored template; own bullet/citation style |
| v2 few-shot | Same delimiters + a fully filled-in example answer | Still ignored literal delimiters, but shifted to a `Q:`/`A:`/`Evidence:`/`Sources used:` labeled style — closer to "structured" but not exact |
| v3 JSON | Strict JSON schema, no prose | **Closest match** — returned real, valid JSON with the right key names for `question`/`answer`/`source.file`, though it added extra fields we didn't ask for (`source.evidence`, `citations` array) and appended one sentence of prose *after* the JSON block instead of nothing |
| v4 external template ref (flat sibling file) | Skill points to a separate `output-template.txt` in the same folder | **Worse than v1** — did not retrieve/reproduce the literal file content at all; instead fabricated its own field, `Template: SecretKeywordLookup`, which appears nowhere in our template. Strong evidence it did not actually read the sibling file's exact bytes, just inferred "this skill implies a templated answer" |
| v5 actionable + `assets/` subfolder template | Skill asks the agent to enumerate all libraries in the site, template lives in `assets/` subfolder | **Sources-scope limitation surfaced** — the agent only listed `TEST-DO-NOT-USE-Agent-Pilot` (extracted from a *mention* of it inside `test-content.md`'s text), not a real enumeration of site lists/libraries. This agent's `Sources` binding is scoped to one library folder only, not the whole site — it has no way to see `Site contents`/other libraries unless one is explicitly added as a source. User had to clarify ("I'm talking about ... list of lists or document libraries in here") — follow-up pending as of this writing.

**Ranked conclusions:**
1. **JSON-schema output requests are honored far more reliably than custom ASCII-delimited
   templates** — likely because JSON is a well-known format the underlying model has strong
   priors for, whereas arbitrary delimiter syntax gets "smoothed over" into the model's own
   native answer style.
2. **A literal, byte-exact external template file is NOT reliably read/followed** — worse, the
   agent may fabricate plausible-looking fields instead of quoting the real file, which is a
   meaningfully risky failure mode (silent hallucination of structure) for anything expecting
   copy-exact output.
3. **A skill's `## Output format` (regardless of variant) is best treated as a strong stylistic
   bias, not an enforceable contract.** For anything requiring guaranteed-exact structure (e.g.
   machine-parseable downstream automation), plan on: (a) using JSON as the requested format
   (best compliance observed), AND (b) validating/repairing the agent's actual output
   programmatically rather than trusting it — never pipe raw SharePoint-agent output directly
   into a strict parser without a validation step.
4. **A skill's real *task* (enumerate libraries) is bounded by the *agent's* attached `Sources`,
   not by what the skill's own instructions describe.** A skill cannot exceed the knowledge
   scope of the agent invoking it — if you want site-wide enumeration, the *agent* (not just the
   skill) needs the whole site added as a source, not just one library.
5. **`assets/` subfolder placement for a skill's template file was not conclusively tested** —
   the v5 test failed for a different, more fundamental reason (source-scope), before we could
   isolate whether the subfolder path itself was retrievable. Revisit once source-scope is fixed.

## 8. Write-action skills — CONFIRMED NOT SUPPORTED (agent self-reports the limitation honestly)

Per the research README's near-term priority "verify how custom SharePoint agents discover or
invoke native skills," and the real `review-manual-topics` skill's own steps (which describe
*creating* Content Review list items), we tested whether a Copilot-in-SharePoint agent invoking a
skill can perform a genuine **write** action.

- Created a real test list, `TEST-DO-NOT-USE-Discovery-Log` (via `New-PnPList` +
  `Add-PnPField`, both scriptable and successful — list/field creation remains a confirmed
  capability), confirmed empty (0 items) before the test.
- Authored `test-do-not-use-log-finding` (`skills/v6-log-finding.SKILL.md`), a skill whose steps
  explicitly describe creating one new list item with Title/Notes/SourceFile values, modeled
  directly on the real skill's list-write pattern.
- Asked the agent: *"Log a finding: title 'Test write action', notes 'Testing whether a
  SharePoint agent skill can create a real list item', source file test-content.md"*
  - **Result: the agent explicitly declined**, stating verbatim: *"I can't create or modify
    SharePoint list items or perform write actions in your environment."* It then produced only
    a draft/preview of what the record *would* contain (Title/Notes/Source File as a bulleted
    draft), without claiming the write succeeded.
  - **Independently verified via PnP** (`Get-PnPListItem`) immediately after: the list still had
    **0 items** — confirms the agent's self-reported refusal was accurate, not a false negative
    hiding an actual side effect.
- **Conclusion:** a Copilot-in-SharePoint custom agent, even when invoking a skill whose written
  instructions describe a list-write action, **cannot actually perform that write** in this
  context (this UI/preview surface, this permission profile). This is a genuine, hard capability
  boundary, not a prompt-engineering problem — no amount of more explicit skill wording is likely
  to make the agent itself perform the write. This is a *trustworthy* failure mode: it reported
  its own limitation honestly rather than hallucinating success, which is reassuring for
  governance purposes but means:
  - The real `review-manual-topics` skill's Content Review list-creation behavior (documented in
    the field-note) may only work through a different invocation path than a custom `.agent`
    chat pane — e.g., directly through Copilot in SharePoint's native site-wide assistant (not a
    custom agent), a different licensing tier, or an update since that original field test. This
    discrepancy is worth a follow-up: retest the exact same write-action request against the
    site's default/ready-made Copilot experience (not a custom `.agent`), if accessible.
  - Any real write-automation need (e.g., logging review items from CEIS-manual content) should
    NOT be designed around "the SharePoint agent does the write" — it should route through PnP
    PowerShell/Graph/Power Automate (systems with genuine write access), with the SharePoint
    agent's role limited to drafting/preparing content for a human or automated process to then
    commit.

- **Corroborating evidence:** separately asked the agent to "summarize your capabilities in
  sharepoint please" (no skill invoked, plain question) — it self-reported the same boundary
  unprompted: *"I can only provide information that is explicitly supported by the available
  source content and cannot create SharePoint list items, modify documents, or perform other
  write operations in SharePoint."* This is a general, consistent self-model, not a one-off
  refusal tied to a specific skill's wording — strengthens confidence this is a real platform
  boundary for custom `.agent` chat panes, not a fluke of our particular skill's phrasing.

## 9. Quiz generation — confirmed as a native (no-skill-needed) capability

The research README (`docs/research/README.md`) lists "generate a draft quiz" as an example
native-skill capability. Tested it directly as a plain question (no custom skill invoked):
*"can you generate a quiz based on content in a document in here?"* — the agent produced a
correctly grounded, cited multiple-choice quiz (e.g. "What is the title of the document?" with
A/B/C/D options and a cited answer) straight from `test-content.md`, with no skill authored for
it. **Conclusion:** quiz generation is a built-in Copilot-in-SharePoint behavior available to any
agent with a grounded source — does not require a dedicated skill to unlock.

## 10. Scoped, production-style Q&A skill — combining lessons learned

Building on §7's format-compliance findings (literal ASCII/JSON templates get reformatted;
natural labeled-bullet output is followed far more consistently) and §8's scope-boundary finding
(agent only sees its attached Sources), authored a realistic pattern for a real deployment:
`test-do-not-use-scoped-manual-qa` (`skills/v7-scoped-manual-qa.SKILL.md`). Design choices,
deliberately informed by prior experiments rather than fighting them:
- **Scope restriction as an explicit refusal rule**, not just a Sources binding — instructs the
  skill to refuse (with a fixed phrase) rather than guess when the answer isn't in the named
  source, and to suggest a follow-up topic instead of a dead end.
- **Output format uses the same labeled-bullet style the model naturally produces**
  (`**Answer:**`, `**Found in:**`, `**Suggested follow-up:**`) rather than a rigid ASCII/JSON
  template — working with the model's tendency (§7) instead of against it, on the theory that
  *consistent* labels are more achievable than *literal* structure.
- **Built-in "suggested follow-up question" field** — pairs with the agent's native
  `conversationStarterList` (§3) to keep users inside the scoped topic rather than wandering into
  out-of-scope questions.

## 11. Mermaid/diagram rendering — confirmed NOT supported (text-only chat surface)

Asked the agent to "output content in a structured mermaid workflow and output the visual not
just the markdown code." It generated correct, well-formed Mermaid flowchart syntax grounded on
`test-content.md`, but explicitly and correctly stated it **cannot render an actual visual
diagram/image inside SharePoint** — only the Mermaid markup text, which "a Mermaid-compatible
viewer" would need to render separately. When pushed again ("can you show the visual of that?"),
it produced an ASCII-box-art fallback instead of a real image, again stating plainly: *"I can
generate Mermaid code and text-based visualizations, but I cannot directly render the Mermaid
graph as an interactive image or SVG in this chat."*
- **Conclusion:** the Copilot-in-SharePoint custom-agent chat pane is a **text-only output
  surface** — no image/SVG/diagram rendering capability, regardless of skill or prompt wording.
  This is directly relevant to the `docx-to-content` plugin's rendered Markdown output (which
  includes real images/diagrams for the CEIS manual) — a SharePoint agent grounded on that
  content can *describe* diagrams or *generate* Mermaid syntax on request, but cannot display the
  manual's actual images/diagrams as visuals within its own chat responses. Any image content
  the user needs to see must come from opening the source file directly, not from the agent
  chat pane.

## 12. Scoped Q&A skill test results — labels still overridden, but scope-refusal logic worked well

Tested the §10 `test-do-not-use-scoped-manual-qa` skill with both an in-scope and an
out-of-scope question:
- **In-scope** ("what is the secret test keyword?"): answered correctly
  (`PINEAPPLE-DISCOVERY-42`, cited), but used its own **`Q:` / `A:`** labels — not the skill's
  specified `**Answer:**` / `**Found in:**` / `**Suggested follow-up:**` labels. The
  "Found in"/"Suggested follow-up" fields were omitted entirely.
- **Out-of-scope** ("what's the weather like today?"): **correctly refused** rather than
  hallucinating — explained plainly that the only in-scope source, `test-content.md`, contains no
  weather information. It did not use our exact fixed refusal phrase, but the underlying
  *behavior* (no guessing, cites why it's out of scope) matched the intent precisely.
- **Revised conclusion (supersedes the more optimistic framing in §10):** even a skill designed
  to "work with the model's natural style" still doesn't get its **exact label wording** followed
  — the model appears to have a strong built-in preference for terse `Q:`/`A:`-style output
  regardless of what a skill's `## Output format` requests. However, **higher-level behavioral
  instructions (scope restriction / refuse-rather-than-guess) are followed reliably and
  correctly**, even without exact phrasing compliance. **Practical implication for any future
  production skill design:** don't rely on `SKILL.md` to dictate exact label text/formatting —
  design for the *behavior* you need (correct refusals, correct grounding, correct citations) and
  treat exact surface formatting as unreliable/cosmetic. If exact machine-parseable output is a
  hard requirement, don't use a SharePoint agent chat response as the parsing source at all;
  post-process/validate downstream instead (echoes §7's JSON finding).

## 13. Native Markdown rendering — CONFIRMED (resolves a previously flagged manual-only item)

The original read-only discovery script's `ManualStepsNeeded` explicitly flagged Stage 3.0.2.4
("native Markdown rendering: this script cannot observe rendered output... manually upload one
sample rendered CEIS topic... and record whether it renders usably") as requiring manual,
non-automatable verification. That verification is now done:

- Uploaded the **real CEIS manual rendered output** (`runs/ceis-manual-v2/render/rendered-output/`,
  348 files / ~83MB, including `pages/` and `media/` subfolders — the actual Phase 1 pilot
  deliverable, not synthetic test content) into the test library via a recursive
  `Get-ChildItem` + `Add-PnPFile` loop that preserves the source folder structure
  (`ceis-manual-full/index.md`, `ceis-manual-full/pages/*.md`, `ceis-manual-full/media/*`).
- Opening `index.md` directly in the browser renders it with SharePoint's native split-pane
  Markdown viewer: the `# Index` H1 heading renders correctly, and every relative Markdown link
  (e.g. `[LOCATE A FILE](pages/locate-a-file--82c06d21.md)`) renders as a real, clickable
  hyperlink in the preview pane — **confirmed working**, including navigating through to the
  linked topic pages themselves (user confirmed clicking through renders correctly, not just the
  index).
- The rendered-Markdown view also surfaces contextual Copilot suggestion chips automatically
  ("Summarize this document", "Create an FAQ from this document", "What can Copilot do?") without
  any skill/agent configuration — a built-in feature of SharePoint's native Markdown viewer, not
  something we configured.
- **Conclusion:** the `docx-to-content` plugin's actual multipage Markdown output (headings,
  relative cross-topic links, and — pending a dedicated image-heavy topic test — embedded media
  references) is directly, natively viewable and navigable in SharePoint with no conversion step,
  no custom web part, and no special SharePoint configuration required. This substantially
  de-risks the "publish rendered manual content directly to SharePoint" path referenced in the
  broader initiative's vision documents. Still to verify as a distinct follow-up: whether a topic
  page containing embedded images (`![...](../media/...)`) renders those images correctly in the
  same native preview pane, since `index.md` itself contains only links, not images.

## 14. Multi-document cross-topic synthesis — CONFIRMED, high quality (most impressive result yet)

Uploaded the real CEIS manual rendered output (`ceis-manual-full/`, 25 of 26 real topic pages +
111 media images; `ceis-sample/`, 5 hand-picked topics) and asked, using the §
`test-do-not-use-manual-cross-topic` skill: *"how do warrants relate to protection orders in the
CEIS manual?"*

- The agent correctly identified **3 relevant source files** and synthesized across all of them,
  structuring its answer as "Topic A: Warrants" / "Topic B: Protection Orders" / "Relationship
  Between the Topics" — organically matching the *intent* of the skill's structure even though
  (consistent with §12's finding) it did not use the skill's literal `**Answer:**` /
  `**Topics used:**` / `**Cross-topic relationship found:**` labels.
- Content accuracy was high and domain-specific: correctly named real CEIS warrant types
  (Warrant of Arrest/WOA, Warrant of Committal/WOC, Warrant for Arrest/WFA) and protection-order
  form types (POR, OTP, NRP, RESO/FMER), correctly referenced the Reports Module's Warrants
  Report and POR Reconciliation Report, and drew an accurate higher-level relationship (both are
  party-level status indicators, both are court-generated records, both have dedicated
  monitoring/reporting) — this is real domain content correctly extracted and connected across
  multiple real manual topics, not hallucinated.
- Each factual claim carried a numbered citation back to its specific source file.
- **Conclusion:** this is the strongest evidence yet that a SharePoint Copilot agent grounded on
  the `docx-to-content` plugin's real rendered output can perform genuinely useful,
  multi-topic-spanning question answering with accurate citations — the core value proposition
  of the broader AI-Assisted Structured Knowledge Workbench vision. Combined with §13's native
  Markdown rendering confirmation, this is meaningful, real evidence (not synthetic-content-only)
  that grounding a SharePoint agent on structured/rendered manual content is viable.

- Also notable: the response included a distinct "**Cross-Topic Conclusion**" section that
  carefully avoided overclaiming a causal relationship — explicitly stating *"The manual does not
  state that a warrant automatically creates or results from a protection order. Instead, it
  links them operationally..."* — correctly distinguishing correlation/operational linkage from
  causation, then citing the exact three source files (`parties--62236e0e.md`,
  `document-production--ad3390e0.md`, and a third) backing each claim. This is a meaningful
  epistemic-honesty signal: the agent did not force a connection where the source material only
  supports a weaker one, directly matching what §10's skill design asked for ("if the topics
  don't actually connect... say so honestly rather than forcing a connection").

## 15. ASPX / modern-page conversion experiment — testing SharePoint as a multi-format Renderer target

**Motivation:** this repo's own stated vision is `Content + Template + Renderer = Published
Output` — a single structured Markdown source rendered to multiple output formats. This probe
tests whether SharePoint itself can be one such Renderer target, using a real CEIS manual topic
(`initiate-a-file--51d1f554.md`, 4 headings, 2 images, 2 tables) converted via `pandoc -t html`.

**Raw `.aspx` file upload (boundary probe, unsupported path) — CONFIRMED BLOCKED.**
Wrapped the pandoc HTML fragment in a minimal classic `<%@ Page %>` ASPX shell and attempted
`Add-PnPFile -Folder "Site Pages" -NewFileName "TEST-DO-NOT-USE-raw-initiate-a-file.aspx"`.
**Result: `Access denied`** — the upload was rejected outright, before any rendering question
even arose. This is consistent with SharePoint Online's "no script"/restricted-file-type
enforcement on modern sites, which blocks raw executable-page-type uploads (`.aspx`, `.asmx`,
etc.) outside the sanctioned page-creation APIs — not a permissions gap on our test account
(the same account/app registration succeeded at every other write probe in this document), but
an explicit content-type restriction on that specific library/file-type combination.

**Modern client-side page (supported path) — CONFIRMED WORKING.**
`Add-PnPPage -Name "TEST-DO-NOT-USE-modern-initiate-a-file" -LayoutType Article -Publish:$false`
→ `Add-PnPPageTextPart -Page $page -Text $rewrittenHtml` (same pandoc HTML, with the 2 image
`src` attributes rewritten to absolute URLs after uploading the images to a
`SiteAssets/TEST-DO-NOT-USE-aspx-experiment/` test folder) → `Set-PnPPage -Publish`. Pushed
without error and rendered correctly: heading, bullet list, body paragraphs, and the first
embedded image (the CEIS "Caution" warning-dialog screenshot) all rendered inline exactly as
authored, confirmed by user screenshot (`aspx-experiment/modern-page-rendered-screenshot.png`).

**Classification: `CONFIRMED_TENANT_OBSERVATION`** — this tested tenant/site/permission profile
only, consistent with the "Scope corrections" section above; not a universal SharePoint claim
about every tenant/ring/licensing configuration.

**Implication for the multi-format vision:** SharePoint modern pages are a **viable Renderer
target** for this initiative's structured Markdown source, via the `Add-PnPPage` +
`Add-PnPPageTextPart` route specifically — **not** via raw `.aspx` authoring, which is a real,
confirmed platform boundary, not just an unsupported convention. Practical caveats for any future
production pipeline: (1) image assets need their own upload-and-rewrite step, not a drop-in file
copy — pandoc's relative `../media/...` paths must be resolved to absolute tenant URLs before
the HTML is handed to `Add-PnPPageTextPart`; (2) this was tested with a single Text web part
holding the whole page's HTML, which worked for headings/lists/paragraphs/tables, but a
production pipeline would need to decide whether multi-section pages (multiple web parts,
columns) are worth the added complexity or whether "one Text web part per topic" is sufficient.

**Corroborating research (found this session, from a sibling BC Gov project):**
`/Users/richardfremmerlid/projects/jag-csb-cmat-sharepoint-online/plugins/sharepoint-migration/`
has two directly relevant, more mature skills for classic-ASPX→modern-SPO conversion:
`sp-converting-aspx-pages` (an 8-stage inventory→classify→layout→map→manifest→validate→
preview→report pipeline for migrating real classic SP2016 pages) and `sp-converting-wiki-pages`.
Their shared research doc,
`sp-converting-wiki-pages/references/aspx-to-spo-migration-strategy.md`, independently confirms
the core finding here from a completely different angle (real production migration project, not
a from-scratch experiment): **"There is no direct conversion... this is not 'convert pages' — it
is 'reconstruct pages'"** — modern pages only support modern (client-side) web parts, no 1:1
classic-page-model mapping exists, and **"PnP PowerShell is the primary automation tool"** for
"provisioning modern pages, adding sections and columns, placing web parts programmatically,"
explicitly recommending the exact `Add-PnPPage`/`Add-PnPPageWebPart`/`Add-PnPPageTextPart`
pattern this probe used, while explicitly warning that classic page content must be *rebuilt*,
never *imported as-is* ("Rebuild layout, don't import — tools often fail to migrate pages cleanly").
This external validation raises confidence in today's small-scale result beyond what one probe on
one file could establish alone.

**Not yet tested (flagged for future backlog, per user's decision not to expand this experiment
further today):**
- Generating `.docx` and `.pptx` from the same source via pandoc — deliberately deferred; pandoc
  already supports both formats natively from Markdown input, so this would be a cheap follow-up
  test, reusing `push-aspx-experiment.ps1`'s image-upload/rewrite logic and swapping only the
  `pandoc -t html` invocation for `-t docx` (pptx would need a different Markdown dialect, e.g.
  reveal.js slide breaks, since pandoc's native pptx writer expects slide-delimited input).
- Multi-page/multi-section modern pages (this probe used one Text web part for one whole topic;
  a production pipeline might want per-heading sections or multiple web parts per page).
- Whether the second image (`image18.png`) and the tables in the source topic also rendered
  correctly — the shared screenshot only shows the top of the page (heading through the first
  image); scrolling further to confirm the rest of the page (second image, both data tables) was
  not captured this session.

## 16. Official Microsoft FAQ — corroborates and extends several findings above

**Source:** [Frequently asked questions about Copilot in SharePoint](https://support.microsoft.com/en-us/sharepoint/copilot-in-sharepoint/frequently-asked-questions-about-copilot-in-sharepoint) (Microsoft Support, accessed 2026-07-30). This is official platform documentation, not tenant-specific observation — treated here as corroborating/contextualizing evidence for our hands-on findings, not a replacement for them.

Key points directly relevant to this document's findings, with the specific finding each one
touches:

- **Every SharePoint site/document library has a ready-made agent; edit permissions let you
  create custom ones too.** Directly relevant to Priority 2 of the follow-up backlog (comparing
  ready-made vs. custom-agent behavior) — confirms the ready-made agent is a distinct, always-
  present surface we have not yet tested.
- **Agent-creation UX requires a Modern site; a Modern-site agent can select *any* SharePoint
  site as a knowledge source.** Consistent with our tenant being Modern throughout.
- **Up to 20 source items** (sites, libraries, folders, or files, in any mix) is the current
  documented agent source-item limit. Confirms Priority 8 of the follow-up backlog (source-scope
  variants, including the 20-item boundary) is testing a real, documented constraint, not a
  guess.
- **Agents only surface content the current user already has permission to see — even if it's in
  the agent's configured sources.** Directly supports correction #4 above (knowledge-retrieval
  scope vs. platform capability vs. user permissions are three distinct things) and is exactly
  the mechanism Priority 1's permission-boundary matrix is designed to empirically verify.
- **Supported source file types explicitly include `ASPX`, `HTM`, `HTML`** (alongside Office
  formats, PDF, TXT, RTF, ODT/ODP, and the new FLUID/LOOP formats). This means our §15 finding
  (raw `.aspx` upload to Site Pages returning `Access denied`) was a **write/upload-path**
  boundary specifically — the FAQ confirms `.aspx` files are readable/groundable *as agent
  knowledge sources* once they exist, which is a different question than whether an agent (or a
  script) can create/upload one directly. Worth testing as its own follow-up: does a
  successfully-created modern page (§15's working path) get picked up as a groundable `.aspx`
  source if added to an agent's Sources?
- **"Agents currently don't use data from Lists. Also, you can't add pages from the Site Pages
  library as source for an agent."** This is a very significant, previously-unknown-to-us
  constraint. It directly **explains** §8's write-action test result from a different angle: our
  `TEST-DO-NOT-USE-Discovery-Log` was a List, and even if writes had been supported, an agent
  could never read/ground on List data anyway — meaning our list-write test was probing a
  surface (Lists) that's out of scope for agent grounding entirely, regardless of the write
  question. It also means §15's modern page (`Site Pages` library) **cannot itself be added as
  an agent knowledge source** — a real, documented limitation on how far the ASPX/modern-page
  Renderer-target idea from §15 could ever be combined with agent grounding.
- **Role-permission matrix (site visitors / site members with edit / site owners+):** confirms
  which roles can interact with, create, share, edit, approve-as-default, and delete agents —
  directly usable as the *expected* half of Priority 1's permission-boundary matrix (we still
  need the *actual* half, tested per-identity).
- **Hub-site source expansion changed in September 2025:** ready-made agents always include
  associated hub sites; for *custom* agents, hub-site sources created **before** September 2025
  don't auto-include associated sites unless the hub source is removed and re-added — a concrete,
  dated mechanic directly relevant to Priority 8's hub-scope test, and a reminder to check the
  custom agent's creation date against this cutoff before drawing conclusions from any hub test.
- **Copilot-in-SharePoint's rich-text-editor "rewrite" feature is a separate surface** from
  agents — it only sees the text currently in the editor, not documents or Graph data, and saves
  no history. Not something we tested this session; noted here in case it's ever relevant to a
  future authoring-workflow question (see `docs/vision/editing-workflow-options-for-external-review.md`).
- **Responsible-AI/governance framing:** "AI-generated content may be incomplete, inaccurate, or
  out-of-date... should not be relied on without independent verification"; "not for high-risk
  uses (medical, legal, financial, professional advice)"; "customer data is not used to train
  Microsoft's foundation models." Relevant context for any future governance-controls design work
  (Phase 3's Subphase 3.4).

## 17. Official Microsoft "Get started with SharePoint agents" — further corroboration

**Source:** [Get started with SharePoint agents](https://support.microsoft.com/en-us/sharepoint/ai-copilot/get-started-with-sharepoint-agents) (Microsoft Support, accessed 2026-07-30). Same status as §16 — official platform documentation, corroborating/contextualizing our tenant-specific hands-on findings, not a substitute for them.

Points directly relevant to this document's findings and backlog:

- **Confirms the two-agent-type model precisely as tested:** "ready-made agent" (automatically
  scoped to the site, no `.agent` file, cannot be edited/shared/deleted) vs. "custom-built agent"
  (created with site-editing permissions, has an `.agent` file, fully editable/shareable). This
  matches our own reverse-engineered understanding (§3) and directly confirms why
  `Get-PnPCopilotAgent` alone can't inventory "the complete agent experience" (correction #3
  above) — the ready-made agent has nothing for that cmdlet to find.
- **"SharePoint admins can remove the ready-made agent through the restricted content discovery
  policy as needed."** Directly names the mechanism Priority 9 of the follow-up backlog (RCD)
  would need to test — confirms RCD is specifically an admin-level, ready-made-agent-targeting
  control, not a general site-permissions setting.
- **Custom agent editing is explicitly described as: branding/purpose, sources (sites/pages/
  files), and "customized prompts tailored to the purpose and scope."** Matches exactly what we
  hand-authored in the `.agent` JSON schema (§3) and what the Edit Agent UI showed (§4) — no new
  capability beyond what we already found, but useful as an independent confirmation that our
  reverse-engineered schema covers the full documented editing surface, not just a subset.
- **Licensing: M365 Copilot license, or pay-as-you-go SharePoint-agents billing, both work.**
  Consistent with our tenant's licensing (never directly probed, but agent creation/use worked
  throughout without incident).
- **Sharing mechanism confirmed:** ellipsis on the agent list → Share → Copy Link — matches our
  assumption in earlier sections that a shareable link exists per custom agent; we have not
  actually tested opening a shared link as a different identity (Priority 1's permission-boundary
  matrix would cover this).
- **No mention of write/list-modification capability anywhere in this overview page** — silence
  here doesn't confirm or deny anything new; it's consistent with (but doesn't independently
  corroborate beyond) our own tested finding that writes were unavailable in the custom-agent
  chat-pane path (§8, correction #1).

## 18. Official Microsoft — SharePoint agents are discoverable/usable in Microsoft Teams

**Source:** [Find and use an agent created in SharePoint from Teams app store](https://support.microsoft.com/en-us/office/copilot-in-sharepoint/find-and-use-an-agent-created-in-sharepoint-from-teams-app-store) (Microsoft Support, accessed 2026-07-30). Same status as §16/§17 — official platform documentation, corroborating/contextualizing our tenant-specific findings, not a substitute for them.

**Key confirmation: a SharePoint-created custom agent is not confined to the SharePoint chat
pane — it's a cross-surface artifact.** Agents created in SharePoint are discoverable in the
Teams app store's "Agents" category, personalized per user by recent activity, previewable
(name, icon, creator, source site, grounding sources, Teams app permissions), and can be added
directly to a chat, channel, or meeting (one at a time, repeatable for multiple destinations), or
shared as a message preview into a chat/channel.

**Why this matters for our findings:**
- Every capability/limitation finding in this document (§1-15) was tested through the
  **SharePoint chat-pane surface only**. This resource confirms the same underlying agent object
  is also invoked through **Microsoft Teams**, a materially different UI/host surface. None of
  our findings have been re-verified there — this is a new, concrete gap, not covered by any of
  the existing 9 backlog priorities as originally scoped (Priority 2 compares ready-made vs.
  custom agent *within* SharePoint-adjacent surfaces; it does not currently include Teams).
- **New backlog item (Priority 10 — Teams cross-surface parity):** repeat the core test battery
  (grounded retrieval, write-action request, skill invocation, format compliance, refusal
  logic, quiz generation) via the same custom agent accessed from Teams instead of SharePoint,
  and record whether behavior, sources, and citations are identical, or whether the Teams host
  surface changes anything (e.g. different app-permission prompts, different rendering of
  citations/images, different write-capability surface). This directly relevants to any future
  Phase 5 SharePoint-agent-grounding work, since a real pilot's actual usage may happen through
  Teams as much as through SharePoint directly.
- Confirms agents are genuinely a **Microsoft 365-wide capability** rather than a SharePoint-
  page-scoped feature, reinforcing why Phase 5 (SharePoint agent grounding) is correctly framed
  as its own phase in the master plan rather than folded into Phase 3 — the agent surface has a
  broader reach than the library it's grounded on.

## Reference files (committed alongside this doc)

- `agents/ui-created-agent-format.agent.json` — pretty-printed JSON downloaded from the real,
  UI-wizard-created `TEST-DO-NOT-USE-Pilot-Agent.agent`.
- `agents/pnp-uploaded-agent-format.agent.json` — the hand-authored JSON we wrote and uploaded via
  `Add-PnPFile`, proven fully functional (see §4 above). Use this as a starting template for any
  future scripted agent creation.
- `skills/reference-real-skill-review-manual-topics.SKILL.md` — the real, pre-existing skill
  downloaded from the tenant, used to reverse-engineer the `SKILL.md` format (§ above).
- `skills/example-skill-strict-format.SKILL.md` — our hand-authored test skill exploring
  output-template enforcement (see §6 above).
- `reports/phase-3-0-discovery-report.json` — raw output of the read-only discovery script's most
  recent run.

Both contain real tenant GUIDs (`site_id`/`web_id`/`list_id`) for this dev site — fine to keep
committed per the user's direction that this tool folder is helpful discovery information, not
sensitive; only `config.psd1` (live credentials) stays gitignored.

## Open Questions / Next Steps

1. **Does the hand-crafted `.agent` file actually work as a live agent?** Open it in the browser,
   confirm it launches/answers questions. If yes — full agent-authoring pipeline is scriptable.
2. **Can a `SKILL.md` be authored the same way** (plain file, correct Markdown/frontmatter format,
   dropped into `AgentAssets/Skills/<name>/SKILL.md`)? We already have one real example
   (`review-manual-topics/SKILL.md`, documented in
   `docs/research/sharepoint-platforms-capabilities/field-note-agentassets-skill-creation.md`) to
   reverse-engineer from, same approach as §3–4 above.
3. **Can an output template be authored/uploaded the same way**, and what file format/extension
   does Copilot in SharePoint use for templates?
4. **Can an agent's `.agent` JSON reference a skill and/or template directly** (e.g. an additional
   `capabilities` entry, or a distinct top-level field) — inspect a UI-created agent that has a
   skill/template attached, once one exists, to find that field.
5. Once these are answered: decide whether a small scriptable "agent factory" (structured CEIS
   content → generated `.agent` + skill + template files → batch PnP upload) is worth building as
   a documented, optional future capability — NOT yet authorized/in scope beyond this discovery.

## Cleanup Reminder (staged-write protocol)

All `TEST-DO-NOT-USE-*` artifacts created during this exploration (library, both `.agent` files,
and any skill/template files added later) should be removed once discovery concludes, keeping only
this findings document and the sanitized report as evidence — per the master plan's
remove-after-discovery requirement. Not yet cleaned up as of this writing (exploration still
in progress).
