# Content-Author Editing Workflow Options — Open Question for External Review

**Status:** Draft open question, not yet decided or approved as part of any authorized phase.
Companion to `docs/vision/key-unanswered-questions.md` and the Phase 3 (Governed SharePoint
Knowledge Pilot) section of `docs/vision/master-initiative-plan-workstreams-and-phases.md`.

**Revision note:** this document was revised twice after external review (feedback incorporated
2026-07-29). The original draft conflated four distinct concerns — **editing format** (Markdown
vs. modern-page rich text), **authoring location** (Git vs. SharePoint), **authority** (which
artifact is authoritative), and **integration mechanism** (how content moves between them). It
also implied native SharePoint skills could perform Git operations or arbitrary reverse
conversion, which they cannot. The first revision made those axes explicit and corrected the
mischaracterized models. A second round of review found a remaining self-contradiction in Model C
and three smaller wording issues, all corrected below. A third round of review raised a deeper
usability flaw: the models were still designed from the system's perspective rather than the
editor's, risking exposure of Git/publication machinery to non-technical authors — see
"Third round of review" below for the resulting non-negotiable design rule. A fourth round proposed
a concrete near-term bridge using a human technical publisher role and PnP PowerShell scripts —
see "Concrete near-term bridge" below. A fifth round consolidated that bridge into three named,
supervised repository skills — see "Refinement: three named repository skills" below.

## Issue Summary

Canonical content today is git-only Markdown, edited via VS Code/GitHub/Copilot CLI. That's fine
for this technical pilot, but it was never designed as the real end-user authoring experience for
the actual intended content owners — non-technical business/government staff (e.g., court registry
staff) who are the example content owners named in the broader vision docs.

A future phase (Phase 3, gated behind a not-yet-started tenant-capability-discovery phase) plans to
publish hardened canonical content into a governed SharePoint knowledge library —
package-only by default, no autonomous write. That phase's own planning already flags an
unresolved question: whether manual editing of published SharePoint content is prohibited,
tolerated, or reconciled, and whether such edits ("drift") should flow back into canonical content.

The plan's existing "reconciliation" work (Phase 3, Subphase 3.3) only **detects** drift between
the canonical publication map and actual SharePoint library items — it does not define any
mechanism to **pull edited content back** into canonical Markdown. If SharePoint becomes an editing
surface without such a mechanism, canonical content in this repo goes stale the moment someone
edits there, and every downstream skill (re-rendering to other formats, future
evaluation/grounding work) only ever operates on canonical content — so SharePoint edits would
otherwise be a dead end with no way back into the system that produced them.

**The core question this document raises:** where do content authors actually edit chunks
day-to-day, and how does edited content re-enter canonical git if the edit location isn't git?

## Context

This repo (`manual-conversion-poc`) implements Phase 1 of an initiative moving Word/PDF manuals
from a document-centric model to a content-centric model: canonical Markdown content + generated
elements (TOC, navigation) + a presentation template = a published output for a given destination.

## Candidate models (revised, none decided, none built)

The models below make four independent design axes explicit: editing format, authoring location,
authority, and integration mechanism. Some models intentionally select different combinations of
those axes — e.g. A and C deliberately differ on editing format (rendered page vs. Markdown) — so
they should not be treated as one indivisible platform choice, but each model's row states exactly
which combination it picks.

| # | Model | How it works | Key tension / open problem |
|---|---|---|---|
| A | **SharePoint modern-page editing + external conversion intake** | Authors edit rendered SharePoint pages (not raw Markdown). A separately hosted, authorized adapter extracts approved page content, converts it into a canonical change proposal, validates it, and submits it to Git for review. | Modern-page storage and web-part structures may not map cleanly or losslessly to canonical Markdown — layout, generated elements, embedded components, unsupported web parts, and locally introduced presentation can make reverse conversion ambiguous. This is the hardest reverse-conversion case of the set. |
| B | **Git-only authoring; SharePoint projection only** | Authors use VS Code/GitHub/Copilot CLI directly on canonical Markdown; SharePoint only ever receives rendered, read-only published output. | Architecturally simplest (no reverse sync needed at all) but likely real friction/adoption risk for non-technical business content owners who don't use git day-to-day. |
| C | **SharePoint-hosted Markdown authoring + validated Git promotion** | Authors edit Markdown topic files in SharePoint. SharePoint holds the business-facing *working copy*, not an independently authoritative canonical copy. An authorized intake pipeline retrieves an approved candidate version, validates it, and creates a Git branch/pull request; the change becomes canonical only after the repository review-and-merge gate succeeds. | Does **not** require rich-text-page-to-Markdown reverse conversion (its biggest advantage over A), but requires an authorized SharePoint-to-Git integration, conflict handling, stable topic identity across the boundary, and clear approval/metadata ownership. |
| D | **Purpose-built web editor over Git** | A simple, purpose-built web UI lets authors edit Markdown without touching git/VS Code/GitHub directly. Edits must not commit silently to the protected canonical branch — the safe form is: author edits → app creates a change proposal/branch → validation runs → human review/approval → merge → republish. | New product surface that must additionally solve identity/attribution, authorization, concurrent editing, conflict resolution, branch/PR lifecycle, preview, validation feedback, metadata editing, accessibility, and long-term support/ownership — not just "less friction than raw git." |
| E | **SharePoint change-proposal workflow feeding Git** | Authors do not edit the authoritative published item directly. They submit proposed replacement text or a draft Markdown topic in SharePoint. An authorized adapter turns that proposal into a Git branch/PR: `SharePoint proposal → authorized adapter → Git branch/PR → validation and review → canonical merge → republish`. | This is a one-way **change-intake** workflow, not full bidirectional sync — it deliberately avoids maintaining two independently editable working copies that require general bidirectional reconciliation. Fits government approval chains well (author proposes → reviewer evaluates → pipeline validates → approver accepts → pipeline republishes), at the cost of being a proposal/review loop rather than direct editing. |
| F | **Central publishing-team model** | Business owners submit changes through a familiar, controlled mechanism (e.g., a request form, ticket, or the change-proposal flow in E); trained content specialists are the ones who actually maintain canonical Markdown in Git. | Not the most technically elegant option, but realistic — many organizations separate subject-matter ownership from publishing-system operation, avoiding the requirement that every registry content owner become a git user, a Markdown expert, or a direct publisher. Costs: publishing-team capacity, queue delays, possible transcription errors, weaker immediate ownership, risk of a bottleneck. Still a legitimate baseline to evaluate the other options against. |
| G | **Hybrid by content risk or author group** | Different content/author combinations use different models above — e.g., technical authors use Git (B) directly; ordinary business authors use SharePoint Markdown (C) or change proposals (E); high-risk policy content routes through the central publishing team (F); modern pages remain generated projections throughout; agents/skills assist authors and reviewers in any of the above but never own the synchronization boundary themselves. | Avoids forcing one model to fit every author/content combination, at the cost of more operational complexity (more than one supported authoring path to design, document, and support). |

**Correction to the original draft's Model A:** it previously said "a new sync skill pulls edited
content back into canonical git." A native SharePoint skill cannot perform Git operations or run
arbitrary reverse-conversion code — any SharePoint-to-Git transfer requires a separately hosted,
authorized integration (an adapter, a synchronization service, or an intake pipeline), not a
"skill" in the native-SharePoint-skill sense.

**Correction to the original draft's Model C:** it previously proposed "a Python-backed skill
invoked from SharePoint" running the render pipeline directly. A native SharePoint skill is not an
arbitrary Python execution environment. Model C above is now redefined as SharePoint hosting the
*authoring working copy* of canonical Markdown (a genuinely distinct architectural choice from A),
with Git remaining the sole point at which a version actually becomes canonical — a second-round
review found the first correction's wording ("SharePoint hosts the canonical Markdown" while also
requiring Git review "before it becomes canonical") self-contradictory, since both cannot be true
at once. This is now resolved in favor of Git-side promotion (see below), not SharePoint-side
canonicality. The alternative correction considered (a SharePoint-triggered but externally hosted
rendering service) is a publication mechanism, not an authoring model, and doesn't answer the core
question of where edits re-enter canonical content, so it isn't carried forward as a separate
lettered model here.

## Role of SharePoint agents and native skills

SharePoint agents and native SharePoint skills may improve the authoring and review experience by
helping users locate relevant approved content, apply an authoring checklist, check required
sections or metadata, prepare a proposed revision, summarize changes, identify related topics, or
create/update review items where supported.

**They do not independently solve synchronization with canonical Git.** Native SharePoint skills
cannot run repository scripts, execute Git operations, perform arbitrary custom conversion, or
connect directly to Git. Any SharePoint-to-Git transfer therefore requires a separately authorized
integration mechanism (as in Models A, C, and E above) — agents/skills assist the workflow, they
do not provide the SharePoint-to-Git integration boundary itself.

## The canonical-authority principle, restated

The original framing risked assuming "canonical is authoritative" necessarily means the only
editable canonical copy must physically reside in Git. That assumption is dropped. Restated:

> **There must be one authoritative canonical content state for each topic. Generated pages,
> assembled publications, navigation, TOCs, Office/PDF outputs, and agent-facing representations
> are projections. The approved operating model must define where canonical content is edited, how
> a version becomes authoritative, and how authoritative versions enter the validated release
> process.**

Authority is then defined separately, by concern, rather than by "one copy in one place":

- **Content authority** — approved topic prose.
- **Business authority** — owner, effective date, approval, review date and disposition.
- **Engineering authority** — schemas, validators, renderers, templates, stable-ID rules.
- **Publication authority** — publication maps and approved release manifests.
- **Platform projection** — generated SharePoint pages, published library items, assembled
  outputs, and other destination-specific representations. (Distinct from a SharePoint-hosted
  *authoring* working copy under Model C, which is an input to canonical content, not a projection
  of it — the two must not be conflated.)

This preserves the architectural discipline of "canonical is authoritative" while leaving it to
Phase 3.0 evidence to determine whether approved Markdown is actually authored in Git, in
SharePoint, or through a controlled front end.

## Decision criteria for Phase 3.0 (evidence to gather, not questions to guess at now)

- Can representative business authors complete routine edits without technical assistance?
- Is the edited source Markdown, modern-page content, or another structured format?
- Can stable topic IDs survive editing, rename, move, and synchronization?
- Can generated regions (nav, TOC, indexes) be protected from manual editing?
- Can an edit be validated before becoming canonical?
- Can reviewers see both topic-level and assembled-publication impact of a change?
- What happens when Git and SharePoint are both changed before either is reconciled?
- Is synchronization one-way intake, one-way publication, or genuinely bidirectional?
- Can the system prevent silent overwrite and synchronization loops?
- Which platform owns each metadata field?
- How are author identity, approval, and Git attribution preserved across the boundary?
- Can the workflow restore a prior approved version?
- Can a complete release be reproduced from recorded source and tool versions?
- Can SharePoint agents reliably retrieve and cite the selected content representation?
- What licensing, tenant, permission, and hosting dependencies exist for any adapter/service?
- Who operates and supports the integration when it fails?
- **At what exact event does a proposed version become authoritative, and can the system prove
  that only one version holds that state?** (The discriminator Model C's contradiction obscured —
  arguably the most important governance question across all models.)
- Can authors edit machine-controlled front matter, stable IDs, or provenance fields, and if not,
  how are those regions protected?
- How are links and media resolved consistently between the SharePoint authoring context, the Git
  validation context, and each rendered destination?
- What happens to an approved SharePoint proposal if Git validation rejects it?
- Can the system distinguish business approval of *meaning* from technical acceptance into the
  canonical package?
- How are topic rename, split, merge, and retirement handled? These are not ordinary text edits
  and may alter publication maps, references, stable identity, and downstream outputs.

## Explicit non-decision, and what should be tested first

**No model is selected here.** This remains deliberately deferred to Phase 3 (gated behind
Phase 3.0's tenant-capability discovery), consistent with this repo's standing discipline of not
building/deciding phases ahead of the evidence they're meant to produce.

What changes with this revision is *what Phase 3.0 should test*. The first experiment should
compare:

1. SharePoint editing of actual canonical Markdown (Model C);
2. SharePoint-based change proposals feeding Git (Model E);
3. Git authoring through a simplified/assisted interface (Model D, or plain Model B);
4. the central-publisher baseline (Model F).

**Modern-page reverse conversion (Model A) should be deprioritized** in that first experiment
unless there is a strong business requirement that authors must edit modern pages directly — it is
the option most likely to mix canonical meaning with destination-specific presentation and produce
an unreliable round trip, per the tension noted in its row above.

**A likely eventual hybrid worth naming explicitly (not a selection, a candidate to test):** C for
day-to-day drafting experience, combined with E's proposal/promotion semantics for how a version
actually becomes canonical — i.e., SharePoint may provide direct Markdown editing while every
submitted edit is still treated as a change proposal until repository validation and approval
promote it to canonical state. This resolves Model C's original self-contradiction (SharePoint
editing without SharePoint holding independent authority) and may be the strongest candidate
architecture in the set, but it remains something for Phase 3.0's experiment to test, not a
decision made here.

An illustrative (not authoritative) diagram of this candidate hybrid — SharePoint business
authoring, the authorized SharePoint-to-Git boundary, Git validation and canonical promotion, the
governed publication pipeline, and the published SharePoint knowledge environment — is at
`docs/diagrams/06-phase3-editing-workflow-hybrid-candidate.mmd`.

## Third round of review: the editor must not see the machinery

A third external review pass raised a more fundamental usability flaw in the C+E hybrid above: it
was still designed from the *system's* perspective, not the editor's. As drafted, a business
author could still be exposed to Git-flavored concepts — branches, pull requests, adapters,
validation pipelines, synchronization, canonical promotion, publication manifests — even if only
as status detail. For a non-technical registry content owner, none of that should be visible. The
routine editing experience should be:

1. Open the topic in SharePoint.
2. Edit it.
3. Select **Submit for approval**.
4. If rejected, revise it.
5. If approved, the system handles everything else automatically.

(SharePoint document approval can be orchestrated through Power Automate, which can retrieve the
approved file and trigger downstream actions after the approval decision —
[Power Automate SharePoint approval guidance](https://learn.microsoft.com/en-us/sharepoint/dev/business-apps/power-automate/guidance/require-doc-approval),
[SharePoint library triggers](https://learn.microsoft.com/en-us/power-automate/trigger-sharepoint-library).)

This reframes the evaluation question for every model above. It is no longer:

> Can non-technical authors successfully participate in a Git change-proposal workflow?

It becomes:

> Can the architecture completely hide Git and publication engineering behind the ordinary
> SharePoint edit-and-approve experience?

If it cannot, the model is probably unsuitable for ordinary business authors, regardless of how
architecturally rigorous it is.

**Proposed non-negotiable design rule**, to apply to whichever model is eventually selected:

> The routine authoring experience must require no knowledge of Git, branches, pull requests,
> synchronization, adapters, renderers, publication maps, or canonical promotion. A business author
> edits content in SharePoint, submits it through the familiar approval process, and receives
> either requested changes or confirmation of publication. All engineering and synchronization
> activity occurs behind that workflow.

**One remaining complication:** "approved" (by a human reviewer) and "published" (passes automated
validation) are not necessarily the same event. The hidden pipeline could still reject an
approved document — invalid Markdown structure, broken links/media, damaged stable identifiers,
prohibited edits to machine-controlled fields, publication-level conflicts — but that must surface
in business language, not as a failed CI job or rejected pull request, e.g. *"Publication checks
found issues. Please correct the highlighted items and resubmit."* The author-visible states
should probably be:

**Draft → In review → Changes requested → Approved → Publishing → Published**, with an exceptional
**Publication issue — author action required** state for the case above. An illustrative diagram of
the editor-facing half of this flow (through the Approved state, where the publisher notification
in `docs/diagrams/07-phase3-publisher-triggered-render-workflow.mmd` picks up) is at
`docs/diagrams/08-phase3-editor-submission-and-approval-workflow.mmd`.

**Revised framing of the preferred candidate:** not "authors feed Git," but *SharePoint is the
complete authoring, review, approval, and status experience; Power Automate and the repository
toolchain operate invisibly behind it as implementation infrastructure.* Git may remain the
engineering/canonical-release mechanism, but it must be an implementation detail invisible to
editors. The underlying usability test: if registry staff must understand the architecture diagram
in this document to update a topic, the architecture has failed — regardless of which lettered
model it resembles.

## Concrete near-term bridge: a human technical publisher, no GitHub-SharePoint integration required

The design rule above answers what editors must never see, but leaves open what actually moves an
approved SharePoint chunk into a validated, published release *before* any GitHub↔SharePoint
integration exists. A fourth review pass proposed a concrete, human-in-the-loop bridge for exactly
this gap, using a **technical publisher role** rather than automated synchronization:

1. **Chunk approval triggers a notification.** The SharePoint/Power Automate approval process
   notifies a designated technical publisher, identifying the approved chunk, its exact approved
   SharePoint version, the affected publication and publication ID, the approval/effective date,
   the SharePoint source location, urgency (standalone vs. grouped release), and a link to the
   publication status record. This is the publisher's work queue.
2. **Publisher opens the repository** in VS Code with GitHub Copilot, or the GitHub Copilot
   app/workspace — using this repo's existing `render-content` skill and scripts rather than
   recreating that capability elsewhere.
3. **A `Get-ApprovedContentPackage.ps1` intake script (PnP PowerShell)** connects to the governed
   SharePoint authoring library, locates the affected publication, retrieves the exact approved
   version of every required chunk plus metadata, refuses drafts/pending versions, stages the
   files into a controlled local/repository area, and writes an intake manifest recording every
   retrieved SharePoint version. This is read-only against the authoring source.
4. **GitHub Copilot runs the existing repository render/validation skills** — ingest the
   approved-chunk package, assemble the publication, apply the publication map and approved
   template, generate TOC/navigation, render required formats, validate, and produce a preview and
   release report. The scripts stay deterministic; Copilot invokes the workflow, it does not
   invent publication content.
5. **Publisher reviews one release package**: approved chunks included, SharePoint versions used,
   generated outputs, validation results, a content/change summary, publication preview, and
   target SharePoint destination — then corrects/reruns or accepts.
6. **A separate `Publish-KnowledgeRelease.ps1` script (PnP PowerShell, via `Add-PnPFile`)** uploads
   the generated outputs, sets required metadata, and checks in/approves/publishes per the
   destination library's governance. It refuses an unvalidated or incomplete package and creates
   the deployment record. An optional `Complete-PublicationRequest.ps1` updates the SharePoint
   publication-status record and triggers completion notifications.

Keeping these as four separate, single-purpose scripts (intake / render — the existing skill /
publish / status-completion) mirrors this repo's existing preference for clearly bounded,
independently testable units rather than one script that downloads, transforms, validates, and
publishes without clear boundaries.

This yields two distinct, intentionally different experiences:

- **Business editor:** edit → submit → approval → receive publication notification. No Git,
  scripts, or repository exposure at all — consistent with the design rule above.
- **Technical publisher:** receive notification → retrieve approved package → ask Copilot to
  render → review → publish. Uses Git/the repository directly, but is a designated technical role,
  not the content author.

**Proposed recommendation (Phase 3 pilot baseline, not yet decided):** following approval of one or
more chunks, Power Automate notifies a designated technical publisher; the publisher uses a
repository workspace with GitHub Copilot and PnP PowerShell to retrieve the exact approved
SharePoint versions, execute the repository's rendering/validation skills, review the release
package, and publish the validated outputs back to SharePoint. This is feasible today without any
GitHub↔SharePoint integration, and later automation could replace pieces of it (e.g., an eventual
adapter absorbing the intake/publish scripts) without changing the editor-facing experience.

An illustrative diagram of this flow is at
`docs/diagrams/07-phase3-publisher-triggered-render-workflow.mmd`.

## Refinement: three named repository skills, supervised not autonomous

A fifth review pass consolidated the bridge above into three concrete, named repository skills,
and stressed that this is **supervised** Copilot use, not an unattended agentic workflow:

1. **Get latest approved chunks** — a controlled PnP PowerShell intake script connects to the
   SharePoint authoring library, retrieves only the latest *approved* versions required by the
   publication map (refusing draft/pending versions), writes them into the repository working
   area, and creates an intake manifest recording the SharePoint source versions.
2. **Render approved content** — applies the publication map, selected template, and output
   profile; generates navigation/TOC; produces required outputs; runs deterministic validation;
   creates a reviewable release package and evidence. This stays repository-side because
   PowerShell, custom code, file-system access, deterministic transformation, testing, and
   reproducible release packages belong to GitHub Copilot repository skills rather than SharePoint
   skills, consistent with this document's "Role of SharePoint agents and native skills" section
   above.
3. **Publish rendered content** — requires explicit publisher confirmation; runs a separate
   controlled PnP PowerShell publication script; publishes only a successfully validated release
   package; uploads rendered outputs to the designated SharePoint destination; applies publication
   metadata; records the deployment result and release identity; never modifies the approved
   source chunks.

**User experience:** the designated publisher receives a notification (e.g. *"Approved content
changes are ready for the Court Registry Manual. Open the knowledge-workbench repository and run
the approved publication workflow."*), then in VS Code asks Copilot to *"Process the approved Court
Registry Manual changes."* A coordinating repository workflow invokes the three skills in
sequence:

> Get latest approved chunks → Render approved content → Stop for release review → Publish
> rendered content after confirmation

**Important boundary — this is supervised, not unattended:** the publisher initiates the process;
the PnP scripts are predefined and controlled; rendering and validation are deterministic; Copilot
does not rewrite approved content; the process stops before publication for human review; the
publisher explicitly authorizes the SharePoint write. This matches the document's layered division
of responsibility: SharePoint handles authoring, review, approval, metadata, and governance;
repository skills handle PowerShell, rendering, validation, packaging, and release evidence;
production publication requires an approved identity and explicit human authorization.

The concise operating model: **Notification → open VS Code → get-approved-chunks skill → render
skill → review → publish skill.**

## Feedback requested

- Are there other realistic candidate models missing from this revised set?
- Of A–G, does any look clearly infeasible or clearly preferable on its face (setting aside that a
  final decision should wait for Phase 3.0 evidence)?
- Is the restated canonical-authority principle (one authoritative state per topic, authority
  split by concern, location left open) the right replacement for the earlier "canonical must live
  in Git" framing?
- Are the Phase 3.0 decision criteria complete enough to actually discriminate between C, D, E, and
  F once real tenant evidence exists?
