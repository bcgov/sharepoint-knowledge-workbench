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
and three smaller wording issues, all corrected below.

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
`docs/diagrams/06-editing-workflow-hybrid-option.mmd`.

## Feedback requested

- Are there other realistic candidate models missing from this revised set?
- Of A–G, does any look clearly infeasible or clearly preferable on its face (setting aside that a
  final decision should wait for Phase 3.0 evidence)?
- Is the restated canonical-authority principle (one authoritative state per topic, authority
  split by concern, location left open) the right replacement for the earlier "canonical must live
  in Git" framing?
- Are the Phase 3.0 decision criteria complete enough to actually discriminate between C, D, E, and
  F once real tenant evidence exists?
