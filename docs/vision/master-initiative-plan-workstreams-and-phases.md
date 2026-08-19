# Master Initiative Implementation Plan — AI-Assisted Structured Knowledge Workbench

**Status:** Whole-spectrum plan. Every phase (1–9, plus 3.0 and 5.5) is decomposed into subphases, and every
subphase into implementation stages with entry/exit criteria and evidence requirements. This is the
superordinate planning artifact; the Phase 2 contract-hardening plan
(`docs/superpowers/plans/2026-07-28-phase2-canonical-publication-contract-hardening.md`) is the detailed
execution plan for one phase (2) inside it.

**Revision history:** Supersedes an earlier, workstream-only version of this document. This revision
incorporates external adversarial review (GPT 5.6 + Opus, `temp/plan-reviews/full-plan-review/round3/`)
that found several full-vision capabilities named in traceability but never assigned an actual phase/stage
home, an unjustified hard dependency (Phase 5 on Phase 4), vague stage completion criteria, a missing
SharePoint publication-reconciliation/rollback concern, a missing source-of-truth lifecycle decision, an
under-specified Phase 6 shared-capability derivation, and two labeling issues (Workstream G mislabeled
REJECTED instead of RESEARCH; Phase 1's status inconsistent with Phase 2 Task 0's precondition wording).
All are fixed below.

**Detail-level discipline (unchanged):** Near phases (1, 2, 3.0, 3) carry concrete, implementation-ready
stages. Far phases (4–9) carry real subphase/stage *structure* with honest evidence gates — not fabricated
implementation detail, because their real requirements depend on tenant facts and pilot outcomes that do
not exist yet. Structure is planned; speculative internals are not invented.

**Disposition legend:** NOW = authorized to build · NEXT = next to plan in detail · LATER = deferred
pending prerequisite · RESEARCH = spike/discovery only, gated on a missing fact or use case, not a decision
against scope · REJECTED-for-now = revisit on trigger (reserved for items with a stated architectural
objection, not merely missing evidence — see the Workstream G fix below for why this legend distinction
matters).

---

## How To Read This Plan

Each phase below follows the same shape:

- **Goal** — the one outcome the phase exists to produce.
- **Entry gate** — what must be true before the phase may start.
- **Subphases** — the phase broken into independently reviewable units.
- **Implementation stages** — inside each subphase, the ordered work with its own test/evidence cycle.
  Every stage below states **deliverable / verification / evidence**, even for far phases — this is
  structural planning, not speculative technical design (see Stage 5.1.1 for the pattern this follows).
- **Exit gate** — the evidence (not narrative) that closes the phase.

A stage is the smallest unit that carries its own test cycle and is worth a fresh reviewer's gate.

---

## Per-Phase Git & Session Workflow (applies to every phase below)

Every phase in this plan follows the same integration and session-hygiene pattern, so context doesn't
bloat across a multi-month, multi-phase initiative and so each phase leaves a clean, resumable state behind
it. This section is referenced, not repeated, at each phase's exit gate below.

1. **Branch/worktree per phase.** Before a phase's first task starts, create an isolated workspace —
   a git worktree (`superpowers:using-git-worktrees`) or, at minimum, a dedicated feature branch named
   after the phase (e.g. `phase-2-contract-hardening`, `phase-3-sharepoint-pilot`). Never work a new
   phase directly on `main`. This applies even to Phase 2, which is already scoped to run inside one
   plugin — isolation still protects `main` from an in-progress phase's intermediate, possibly-broken
   states.
2. **Commit per task, not per phase.** Each task (or stage, for far phases once they reach implementation
   detail) gets its own commit(s) on the phase branch, per this plan's and the Phase 2 plan's existing
   task-level commit instructions — nothing new here, just confirming it happens on the phase branch, not
   `main`.
3. **Phase exit gate = merge gate.** A phase's exit gate (defined per-phase above) is also the merge gate:
   do not merge the phase branch into `main` until its exit gate's evidence exists and has been reviewed.
   Merge via a reviewed PR when working with GitHub remotes, or a direct fast-forward/no-ff merge with the
   user's explicit go-ahead when working locally — either way, this is a "confirm before merging" action
   per this repo's standing git-safety conventions, not an autonomous one.
4. **Update `start-here.md` as the last step before ending a phase's session, and immediately after
   merging.** `start-here.md` is this repo's authoritative, kept-current resume document (see `CLAUDE.md`).
   At the close of every phase: record what was actually done (not narrative — evidence, exact test/suite
   counts, exit-gate proof), what's still open, and the exact next action for whoever resumes. This is what
   makes starting a clean session for the next phase safe.
5. **Start the next phase in a fresh session.** Once a phase is merged to `main` and `start-here.md` is
   updated, the next phase should start in a **new session**, not a continuation of the current one — this
   repo's own multi-round review process across this session is itself a case study in context bloat
   (dozens of tool calls, multiple large bundles, several full-file reads) that a fresh session for the
   next phase avoids inheriting. The fresh session reads `start-here.md` first, per `CLAUDE.md`'s own
   resume convention, and does not need this session's full history to proceed correctly.
6. **Worktree cleanup after merge.** Once a phase branch is merged and `start-here.md` reflects it, remove
   the worktree/branch (`git worktree remove`, delete the merged branch) rather than leaving stale
   worktrees to accumulate — this repo has hit that exact problem before (`.claude/worktrees/` had a stale
   entry from a prior phase's worktree still present as of this session's own reconnaissance).

---

## Phase 1 — Structured Knowledge Conversion & Canonical Content POC

**Disposition:** DONE — formally closed. Human spot-check completed and recorded in
`runs/sample-manual-v2/evidence-report.md` (all applicable checklist rows PASS/accepted, footnote row N/A,
metadata row dispositioned); `fix-grid-table-rendering-defect` (PR #2) merged to `main`. **Detail level:**
Implemented.

**Goal:** Prove the content/format separation exists and is genuinely extensible, using the Source Manual as
the evidence vehicle.

**Entry gate:** (historical) approved Phase 1 design spec.

### Subphase 1.1 — Analyze / Convert / Render pipeline
- Stage 1.1.1 — `analyze-document`: structural scan → conversion plan. **DONE**
- Stage 1.1.2 — `convert-document`: cleanup pipeline + chunk + metadata sidecars. **DONE**
- Stage 1.1.3 — `render-content`: `multipage_markdown` renderer proving the contract is pluggable. **DONE**

### Subphase 1.2 — Validation & defect remediation
- Stage 1.2.1 — canonical + rendered validators. **DONE**
- Stage 1.2.2 — image239 regex defect: root-caused, regression-tested, media count 319/319, suite 449/1. **DONE**

### Subphase 1.3 — Formal closure (complete)
- Stage 1.3.1 — human spot-check: title/front-matter, image-heavy section, deep-hierarchy heading,
  begin/middle/end. **Deliverable:** four filled rows in `evidence-report.md`. **Verification:** a human
  actually opened `runs/sample-manual-v2/render/rendered-output/` and recorded what they saw. **Evidence:**
  the filled checklist rows themselves. **DONE.**
- Stage 1.3.2 — disposition the "plugin/marketplace metadata not verified" acceptance row. **DONE** — no
  `marketplace.json` exists for this plugin; `plugin.json`'s capabilities/description already accurately
  describe the built pipeline.
- Stage 1.3.3 — finalize `evidence-report.md`, mark Final Acceptance Checklist complete. **DONE.**

**Exit gate:** All four spot-check rows recorded; metadata row dispositioned; evidence report finalized.
**Met.** This gate was identical to Phase 2's Task 0 precondition — Phase 1 is now actually closed, not
just "engineering-complete," clearing Phase 2's golden-master baseline capture to proceed.

---

## Phase 2 — Canonical / Publication Contract Hardening

**Disposition:** NOW — spec approved; 18-task execution plan (including Task 0) reviewed across four
rounds of external technical review and technically ready. **External review does not itself authorize
implementation (round-5 correction, GPT 5.6)** — execution remains pending the user's explicit approval
and Phase 1's formal closure (Phase 1's own exit gate above). **Detail level:** Implementation-ready.

**On deliverable/verification/evidence for this phase's stages (round-5 clarification, GPT 5.6):** unlike
every other phase in this document, Phase 2's stages below are deliberately summarized without repeating
deliverable/verification/evidence inline — that detail already exists, per-task, in the subordinate plan
(`docs/superpowers/plans/2026-07-28-phase2-canonical-publication-contract-hardening.md`), which is
implementation-ready and would make this section redundant if duplicated. Every other phase's stages below
state deliverable/verification/evidence directly, since no subordinate plan exists for them yet.

**Goal:** Make the canonical→publication boundary explicit, independently testable, provably free of
DOCX-runtime dependencies, and *provably validated* (validators demonstrated on purpose to catch specific
corruption at the specific layer meant to catch it).

**Entry gate:** Phase 1 formally closed (Subphase 1.3 complete).

### Subphase 2.0 — Immutable baseline (must run first)
- Stage 2.0.1 — capture Phase-1-accepted `index.md`/`pages/`/`media/` as `golden-master-baseline/` before
  any code change; write `MANIFEST.sha256`; commit immutable.

### Subphase 2.1 — Identity & contract corrections
- Stage 2.1.1 — fix `package_identity` double-prefix.
- Stage 2.1.2 — rename `source_manifest_hash` → `source_content_sha256`; rename the stale-check code.
- Stage 2.1.3 — split schema-version constants per contract; repoint renderer version-gate at the manifest
  constant (not the conversion-plan alias — a real re-coupling bug found and fixed in round-3 review).
- Stage 2.1.4 — give `PublicationMapEntry.chunk_id` real chunk-ID semantics; remove `parent_topic_id`.

### Subphase 2.2 — Validator credibility
- Stage 2.2.1 — cross-artifact lineage checks (chunk sidecar `plan_id`/`source_sha256` vs manifest).
- Stage 2.2.2 — malformed / unexpected publication-map handling; strategy-conditional requirement; the
  publication-map validation check itself validates `entry.chunk_id` (what the renderer actually consumes),
  not `entry.topic_id` — a load-bearing divergence found and fixed in round-3 review.
- Stage 2.2.3 — close the content-comparison-skip loophole via manifest provenance
  (`manifest.generator.plugin`). **Known, accepted limitation (round-4 finding, Opus):** this provenance
  signal is self-asserted in the manifest, not independently verified — a package can claim
  `generator.plugin: "hand-authored-fixture"` and receive the same content-check exemption a genuine
  fixture gets. This is acceptable inside Phase 2's threat model (the producer is trusted; no untrusted
  second producer exists yet), but it is a narrowed bypass, not a closed one. When a second, less-trusted
  producer exists (see extraction triggers, Stage 2.5.3), this must become a verified provenance signal
  (e.g. a signed/hashed producer identity), not a self-declared string — tracked here so a future reader
  doesn't trust this mechanism further than it currently earns.

### Subphase 2.3 — Runtime independence
- Stage 2.3.1 — split `package.py`: extract read-only `canonical_package.py`; harden `load()` to re-derive
  lineage + publication-map integrity. **Sequencing note (round-4 finding, Opus):** this stage ships new
  enforcement logic in `load()` (publication-map re-validation, lineage cross-checks) with no dedicated
  test exercising it until Subphase 2.4's Layer-2 mutation suite runs several stages later. This gap is
  explicit, not accidental: the Layer-2 mutation tests are written after the module split so they can
  target the *final* `load()` shape rather than an intermediate one, but it means Stage 2.3.1's own
  "tests pass" claim covers only pre-existing behavior, not the new enforcement — the new enforcement is
  unverified until Stage 2.4.2 runs. Do not treat Stage 2.3.1 as self-verifying on its own.
- Stage 2.3.2 — transitive import-boundary test with negative-control self-tests.

### Subphase 2.4 — Adversarial mutation suites (headline deliverable)
- Stage 2.4.1 — Layer-1 (`validate_canonical_package`) mutations. **Meta-proof durability (round-4 finding,
  Opus):** for the two checks closest to the image239 lesson — content-comparison and media-reference —
  the "prove this test depends on its check" step must land as a **permanent** test (monkeypatch the check
  to a no-op inside the test itself and assert the mutation then goes undetected), not only a one-time
  throwaway script recorded in a commit message. The other three checks (manifest consistency, orphans,
  plan/source fingerprint) may use the throwaway-script form the Phase 2 plan already specifies.
- Stage 2.4.2 — Layer-2 (`CanonicalPackage.load()`) mutations incl. publication-map/lineage post-promotion
  attacks — this is where Stage 2.3.1's new enforcement logic actually gets its first real test coverage.
- Stage 2.4.3 — Layer-3 (`validate_rendered_output`) mutations incl. index-completeness with adversarial
  link cases.

### Subphase 2.5 — Independence proof & closure
- Stage 2.5.1 — independent hand-authored canonical fixture, validated by the real validator.
- Stage 2.5.2 — runtime-independence behavioral test (DOCX/intake/temp physically absent).
- Stage 2.5.3 — document extraction triggers, including the Stage 2.2.3 provenance-verification trigger
  above.
- Stage 2.5.4 — golden-master comparison against the Subphase 2.0 baseline (byte-identical content,
  semantic metadata).
- Stage 2.5.5 — full-suite run; Task 16's golden-master test must PASS, not SKIP, before completion is
  declared.

**Exit gate:** Mutation coverage matrix complete with every case reaching its intended detector (including
the two now-permanent meta-proof tests); two identity bugs fixed with regression tests; `chunk_id`
resolution proven against the field the renderer actually consumes; publication-map requirement enforced
all three ways; module split + transitive import test green, with Stage 2.3.1's new `load()` enforcement
confirmed covered by Stage 2.4.2 (not merely assumed); golden-master both surfaces pass; intentionally-
changed tests accounted for; exact suite counts reported.

---

## Phase 3.0 — SharePoint Tenant-Capability Discovery

**Disposition:** NEXT. **Detail level:** Research-spike-ready.

**Goal:** Replace assumption with observed tenant facts. Sole deliverable: `tenant-capability-report.md`.

**Entry gate:** Phase 2 exit gate met (a hardened canonical/publication contract exists to map against).

### Subphase 3.0.1 — Access & inventory
- Stage 3.0.1.1 — confirm tenant access, licence ring, and who is asking on whose authority. **Deliverable:**
  a one-page access record. **Verification:** a named person confirms tenant admin/licensing facts
  directly, not inferred. **Evidence:** the access record, dated and attributed.
- Stage 3.0.1.2 — inventory available surfaces (SharePoint Online site types, content types, column
  types). **Deliverable:** surface inventory. **Verification:** each surface confirmed present in the
  actual tenant, not from generic SharePoint documentation. **Evidence:** inventory with screenshots or
  admin-center exports.

### Subphase 3.0.2 — Capability probes (evidence, not assumption)

**Discovery is read-only by default; any write is staged and authorized (round-5 finding, GPT 5.6) —
discovering what a governance capability permits must not itself create an unauthorized governance
exception.** Every probe below that could involve writing anything follows this staged order, not a direct
production write attempt:
1. Confirm existence and inspect schema/permissions **read-only** first.
2. Identify the resource's owner and the permission actually required to write to it.
3. Use a designated non-production/test site or location, never a production knowledge library.
4. Obtain explicit authorization for a specific, reversible test write before attempting one.
5. Write a clearly labeled synthetic artifact (e.g. name-prefixed `TEST-DO-NOT-USE-...`).
6. Remove the synthetic artifact after the probe and preserve only the evidence (screenshots/transcripts),
   not the artifact itself.

- Stage 3.0.2.1 — AgentAssets: does it exist, where, who can write? **Deliverable:** probe result.
  **Verification:** read-only existence/schema check first (steps 1-2 above); a reversible authorized test
  write (steps 3-6) only if read-only inspection can't answer "who can write" definitively. **Evidence:**
  probe transcript/screenshot, with any test write's removal confirmed in the same record.
- Stage 3.0.2.2 — native `SKILL.md` authoring: available on this ring? what schema does it accept?
  **Deliverable:** schema sample or "not available" finding. **Verification:** an authoring attempt in a
  designated non-production test surface only (never a production knowledge location), following the
  staged order above. **Evidence:** the accepted/rejected sample and error text if rejected, plus
  confirmation the test artifact was removed.
- Stage 3.0.2.3 — agent creation: possible, by whom, what approval path, what write identity?
  **Deliverable:** approval-path record. **Verification:** confirmed with tenant admin, not inferred from
  general M365 licensing tiers — this stage is a read-only administrative confirmation, no test agent
  creation needed to answer it. **Evidence:** the approval-path record, named owner attached.
- Stage 3.0.2.4 — native Markdown rendering: enabled? **Deliverable:** yes/no finding. **Verification:**
  a rendering attempt against a designated non-production test item, following the staged order above.
  **Evidence:** screenshot of rendered (or failed) output, test item removed afterward.
- Stage 3.0.2.5 — metadata field types/constraints available for a pilot library. **Deliverable:** field
  type inventory. **Verification:** created against an explicitly designated, authorized non-production
  test library in the tenant (not an ad hoc write against whatever is convenient). **Evidence:** the field
  inventory with observed type constraints, test library's authorization recorded.

### Subphase 3.0.3 — Report & gating decision
- Stage 3.0.3.1 — write `tenant-capability-report.md` with observed evidence per probe. **Deliverable:**
  the report itself. **Verification:** every probe from Subphase 3.0.2 has a corresponding section citing
  its actual evidence, not a summary written from memory. **Evidence:** the report, cross-checked against
  each probe's own evidence artifact.
- Stage 3.0.3.2 — map each Phase 3–5 dependency to a "confirmed available / confirmed blocked / needs
  escalation" status. **Deliverable:** the dependency-status map. **Verification:** every Phase 3/4/5 entry
  gate item traced to a specific probe result. **Evidence:** the map. **Decision owner:** the initiative's
  technical lead, with tenant admin sign-off on any "confirmed blocked" finding.

**Exit gate:** `tenant-capability-report.md` answers all five probe questions with observed evidence;
Phase 3 scope confirmed feasible or explicitly re-gated.

---

## Phase 3 — Governed SharePoint Knowledge Pilot

**Disposition:** NEXT, gated behind 3.0. **Detail level:** Bounded pilot scope, provisional architecture.

**Goal:** Publish hardened canonical content into a governed SharePoint knowledge library — package-only by
default, no autonomous write — proving the metadata/source-of-truth model on one real library.

**Entry gate:** Phase 3.0 report confirms library metadata fields and (at minimum) package-only deployment
is feasible.

### Subphase 3.1 — Metadata schema mapping & source-of-truth lifecycle

**Design consideration carried forward from Phase 3.0 (§16 of `research-summary-phase3-sharepoint-write-capability-discovery.md`,
citing Microsoft's official Copilot-in-SharePoint FAQ):** agent knowledge sources are capped at
20 source items, but **a folder counts as one item regardless of how many files it contains** —
Microsoft's own guidance is to "nest the data at a higher level and source the agent to that
level" once a flat file count would exceed 20. The pilot project alone has ~26 topic pages before
counting media, so **the pilot library's folder structure must be planned with this in mind from
the start** — e.g. grouped by manual section/chapter — rather than left flat and restructured
later once an agent needs to be scoped to it. This is a structural decision for Stage 3.1.1's
schema-mapping work, not a detail to defer to Phase 5 (SharePoint agent grounding), since the
library's physical folder layout is set here, in Phase 3, and is expensive to change afterward.

**Design consideration added 2026-08-02 (Phase 5 Task 5 defect, real duplication caught before it
landed):** `docs/superpowers/specs/2026-08-02-multi-document-destination-configuration-design.md`
specifies a three-layer destination-configuration model (root connection config + per-document
publication profile + explicit script parameters) so a second real manual/policy/procedure doesn't
duplicate or collide with the first. Recommended entry gate: trigger together with Phase 5.5A's
own entry gate (a concrete second content type identified with a real document/need). **Design
only — not authorized to implement.** Read that spec before adding or modifying any
tenant-scripting tool's destination logic.

- Stage 3.1.1 — map canonical/publication contract → minimal library schema: owner, status, review date,
  topic ID, publication ID, validation state. **Deliverable:** schema-mapping document. **Verification:**
  every canonical/publication field has an explicit mapped library column or a stated reason it's omitted.
  **Evidence:** the mapping document.
- Stage 3.1.2 — reconcile schema against Phase 3.0's observed field-type constraints; adjust, don't guess.
  **Deliverable:** reconciled schema. **Verification:** every field type checked against Stage 3.0.2.5's
  actual observed constraints, not assumed compatible. **Evidence:** the reconciled schema with the 3.0.2.5
  reference cited per field.
- Stage 3.1.3 — define canonical-vs-published source-of-truth rule (canonical is authoritative; published
  is a rendered projection). **Deliverable:** one-paragraph rule statement. **Verification:** the rule is
  unambiguous about which artifact wins in a disagreement. **Evidence:** the rule statement, folded into
  Stage 3.1.4's document below.
- Stage 3.1.4 — **source-of-truth lifecycle rules (round-4 finding, GPT 5.6 — "canonical is authoritative"
  is an architectural slogan without these decisions).** Before any publication happens, decide and
  document, explicitly:
  - Is manual editing of published SharePoint content prohibited, tolerated, or reconciled?
  - What happens when someone edits published content directly — is that drift?
  - Must drift flow back into canonical content, or is it discarded on next republish?
  - How does republishing behave when manual edits exist (overwrite silently, warn, block)?
  - Which repository/package/version is authoritative when canonical and published disagree?
  - How are superseded versions marked in the library?
  **Deliverable:** `source-of-truth-lifecycle.md`. **Verification:** each question above has an explicit
  answer, not a default-by-omission. **Evidence:** the document itself, reviewed before Subphase 3.2 pilots
  anything.
  **Related open question (not yet decided, informs but does not resolve this stage):**
  `docs/vision/editing-workflow-options-for-external-review.md` explores where content authors would
  actually edit content (Git vs. SharePoint vs. a hybrid), candidate editing/synchronization models
  A–G, a proposed non-negotiable rule that routine authoring must hide Git/publication machinery from
  business authors, and a concrete supervised human-technical-publisher bridge (three named repository
  skills: get-approved-chunks / render / publish) usable before any GitHub↔SharePoint integration
  exists. Stage 3.1.4's answers should be informed by that document's eventual Phase 3.0 findings, not
  assume any of its candidate models in advance.
  **Scope clarification (external review finding, 2026-08-02, GPT 5.6 — Phase 5 brainstorming
  placement question):** Stage 3.1.4 owns the full **ongoing structured-content maintenance
  workflow**, not just "where editing happens." That includes: which representation is
  authoritative; how changes are proposed, reviewed, approved, versioned, and audited; how an
  edited topic re-enters the structured content package; and how IDs, lineage, hashes, manifests,
  cross-references, and publication maps are recalculated after an edit. This stage does **not**
  decide which runtime (deterministic pipeline vs. native skill vs. conversational agent) performs
  any of the above steps — that is Phase 6's responsibility (see its Subphase 6.3 below). See
  `docs/vision/resolved-question-ongoing-editing-and-agent-assisted-rendering-phase-placement.md` for
  the full architecture note and resolution this scope clarification is drawn from.

### Subphase 3.2 — Package-only deployment mode

**Forward-looking evidence pointer (not in scope for this subphase):** this subphase targets a
document library (files + metadata), which Phase 3.0 already confirmed viable (native Markdown
rendering, `docs/research/research-experimentation/tenant-discovery/field-note-sharepoint-write-capability-discovery.md` §13). A separate
Phase 3.0 probe (§15, same file) also confirmed that SharePoint **native pages** are a viable
*alternative* Renderer target via `Add-PnPPage`/`Add-PnPPageTextPart` (raw `.aspx` file upload is
blocked — `Access denied` — but the page-creation API works and renders correctly), relevant to
the broader vision's "multi-format rendering... non-SharePoint targets" language
(`ai-assisted-structured-knowledge-workbench-broader-plan.md`). This is evidence for a future
phase to draw on if/when page-based (not just library-file) publishing is ever scoped — it does
not change this subphase's document-library-based approach.

- Stage 3.2.1 — produce an upload-ready package (artifacts + metadata sidecar) that writes nothing
  autonomously. **Deliverable:** the upload-ready package. **Verification:** package contents traced back
  to Stage 3.1.1's schema mapping, field by field. **Evidence:** the package plus its schema-mapping trace.
- Stage 3.2.2 — dry-run validation: package matches target library schema; no field type violations.
  **Deliverable:** dry-run validation report. **Verification:** every field checked against the actual
  reconciled schema (Stage 3.1.2), not a generic schema. **Evidence:** the validation report.
- Stage 3.2.3 — manual, human-performed upload of the pilot library; record what the human had to do.
  **Deliverable:** upload log. **Verification:** a named human actually performed the upload and recorded
  every manual step (this is deliberate evidence for later automation scoping, not busywork). **Evidence:**
  the upload log.

### Subphase 3.3 — Publication Reconciliation and Recovery

**(New subphase, round-4 finding, GPT 5.6 — publication packaging/validation/upload alone does not cover
what happens when published state and canonical state drift, which is a first-class concern for any
system moving content into a second store, not an implicit metadata afterthought.)**

- Stage 3.3.1 — reconcile expected publications (from the publication map) against actual SharePoint
  library items — detect missing, duplicate, stale, and unexpected items. **Deliverable:** reconciliation
  report. **Verification:** every publication-map entry checked against an actual library item.
  **Evidence:** the reconciliation report.
- Stage 3.3.2 — preserve canonical package identity, publication identity, and validation lineage on every
  published item, so any item can be traced back to the exact canonical package/version that produced it.
  **Deliverable:** lineage-field mapping on the library schema. **Verification:** one real published item
  traced back to its exact source package. **Evidence:** the trace record.
- Stage 3.3.3 — define safe republish behavior (what happens when the same topic is published again —
  overwrite in place, version, or block on conflict). **Deliverable:** republish-behavior policy.
  **Verification:** exercised against one real republish in the non-production pilot. **Evidence:** the
  exercised republish's before/after record.
- Stage 3.3.4 — define rollback/unpublish behavior for a bad publication. **Deliverable:** rollback
  procedure. **Verification:** exercised against a deliberately "bad" non-production pilot item.
  **Evidence:** before/after inventory, execution log, and reviewer acceptance.
- Stage 3.3.5 — handle renamed or retired topic IDs without orphaning previously published items.
  **Deliverable:** rename/retirement handling policy. **Verification:** exercised against one deliberately
  renamed topic ID in the pilot. **Evidence:** the exercised test's before/after record.
- Stage 3.3.6 — require dry-run reconciliation reporting before any future authorized-write mode is
  approved (Subphase 3.4 below). **Deliverable:** the dry-run reporting mechanism itself. **Verification:**
  run at least once against the pilot library with zero autonomous writes performed. **Evidence:** the
  dry-run report.

### Subphase 3.4 — Governance controls
- Stage 3.4.1 — versioning + topic/publication review workflow (draft → reviewed → published).
  **Deliverable:** review-workflow definition. **Verification:** one real item walked through all three
  states. **Evidence:** the walked-through item's history.
- Stage 3.4.2 — permission review and oversharing/discoverability check (Protected B discoverability risk
  explicitly tested). **Deliverable:** oversharing-test report. **Verification:** tested under at least two
  distinct permission identities against the pilot library. **Evidence:** the test report.
- Stage 3.4.3 — authorized-write identity: *design only*, gated behind an approved write credential; do
  not build the write path until an owner and identity are approved, and until Subphase 3.3's reconciliation
  dry-run reporting exists to gate it. **Deliverable:** write-identity design document (no implementation).
  **Verification:** an accountable owner and identity are named, not left TBD. **Evidence:** the design
  document with named owner/identity.

### Subphase 3.5 — Pilot evaluation
- Stage 3.5.1 — content readiness checks against the live library. **Deliverable:** readiness-check report.
  **Verification:** every pilot item checked against the Stage 3.1.1 schema for completeness.
  **Evidence:** the report.
- Stage 3.5.2 — pilot retrospective: what the model got right, what governance gaps surfaced.
  **Deliverable:** `phase-3-retrospective.md`. **Verification:** every stage above's evidence is cited, not
  summarized from memory. **Evidence:** the retrospective document, which becomes the entry-gate evidence
  for Phase 4/5's "real (not assumed) requirements."

**Exit gate:** One real governed library populated via package-only deployment; metadata schema proven
against actual tenant constraints; source-of-truth lifecycle rules documented and followed; reconciliation/
rollback behavior demonstrated in dry-run; oversharing controls tested; retrospective documents real (not
assumed) requirements for Phases 4–5. Records/retention/audit remain LATER (Phase 8, Subphase 8.4) unless
this pilot surfaces a concrete need to pull that work forward.

---

## Phase 4 — Native SharePoint Skills Pilot

**Disposition:** RESEARCH, gated behind 3.0/3. **Detail level:** Requirements + subphase structure only;
internals await 3.0 findings.

**Goal:** Pilot one native SharePoint skill (`SKILL.md`-authored) end-to-end, manually deployed before any
automation.

**Entry gate:** Phase 3.0 confirms native skill authoring + AgentAssets are available and writable by an
identified owner; Phase 3 library exists as grounding substrate.

### Subphase 4.1 — Candidate selection & feasibility
- Stage 4.1.1 — pick one candidate skill (review-manual-topics is the leading candidate) against 3.0's real
  permission findings. **Deliverable:** candidate selection memo. **Verification:** selection checked
  against actual (not assumed) 3.0 permission findings. **Evidence:** the memo, citing the specific 3.0
  probe results it relies on.
- Stage 4.1.2 — confirm the skill's inputs exist in the Phase 3 library. **Deliverable:** input-availability
  check. **Verification:** each required input traced to a real item in the Phase 3 pilot library.
  **Evidence:** the check record.

### Subphase 4.2 — Authoring & manual deployment
- Stage 4.2.1 — author `SKILL.md`; validate against the schema 3.0 observed the tenant accepts.
  **Deliverable:** the authored `SKILL.md`. **Verification:** validated against Stage 3.0.2.2's observed
  schema, not a generic template. **Evidence:** the validation result.
- Stage 4.2.2 — manual deployment (no automation yet); record every manual step for later automation
  scoping. **Deliverable:** deployment log. **Verification:** a named human performed every step.
  **Evidence:** the deployment log.

### Subphase 4.3 — Evaluation harness
- Stage 4.3.1 — normal-case evaluation set. **Deliverable:** normal-case test set + results.
  **Verification:** every case checked for correct skill behavior. **Evidence:** the results.
- Stage 4.3.2 — negative / ambiguous / permission / safety evaluation sets. **Deliverable:** the four
  evaluation sets + results. **Verification:** each category has at least one real test case exercised
  against the deployed skill. **Evidence:** the results per category.
- Stage 4.3.3 — evidence capture: what passed, what the skill refused, what leaked. **Deliverable:**
  consolidated evidence report. **Verification:** every category from 4.3.1/4.3.2 accounted for.
  **Evidence:** the consolidated report — this is Phase 4's exit-gate evidence.

### Subphase 4.4 — Lifecycle
- Stage 4.4.1 — versioning, promotion, retirement policy for the piloted skill. **Deliverable:** lifecycle
  policy document. **Verification:** names a decision owner and a review cadence, not left open-ended.
  **Evidence:** the policy document.

**Exit gate:** One native skill deployed and evaluated with evidence across all five evaluation categories;
manual deployment steps documented as automation candidates; no oversharing/permission failures.

---

## Phase 5 — SharePoint Knowledge Agent Pilot

**Disposition:** RESEARCH, gated behind Phase 3 (not unconditionally behind Phase 4 — see entry gate,
round-4 finding, GPT 5.6). **Detail level:** Requirements + structure only.

**Goal:** Pilot one grounded knowledge agent over the Phase 3 library, with strict source scoping and
honest handling of stale/superseded content.

**Entry gate (corrected — round-4 finding, GPT 5.6):** an earlier version of this plan hard-coded "Phase 4
must complete before Phase 5," reasoning "an agent needs something to be grounded in." That over-states the
real dependency: the actual grounding source is Phase 3's governed library, not a native SharePoint skill.
The corrected gate is:
- Phase 3's governed knowledge library exists and is populated.
- Phase 3.0 confirms agent-creation permissions and an approval path for a write/agent-creation identity.
- Phase 4 is a **prerequisite only if** the specific agent scenario selected actually invokes or depends
  on a native skill (e.g., an agent that calls `review-manual-topics` as a tool). For a scenario that only
  needs to read/ground on the Phase 3 library directly, Phase 4 and Phase 5 may run as **parallel sibling
  pilots** after Phase 3, not sequentially. Decide which case applies per selected scenario at the start of
  Subphase 5.1, do not assume the stronger dependency by default.

**Reconciliation with the Global Gating Rules' "no new agents" rule (round-5 finding, GPT 5.6):** the
Global Gating Rules below say "no new agents until ≥2 plugins with ≥2 distinct user journeys exist," which
is a different, stricter gate than the one stated above — and as written, the two could contradict each
other (Phase 5's own gate could be met while the global rule still forbids proceeding). Resolved: the
global rule is about **general-purpose routing/orchestration agents** (e.g. a `knowledge-workbench-agent`
that decides which plugin/journey to invoke) — that class stays gated behind ≥2 plugins/journeys, unchanged.
A **bounded Phase 5 knowledge-agent pilot** (one specific, scoped agent grounded in one library, with its
own governance/evaluation gate above) is a different class and may proceed once Phase 5's own entry gate
above is met, independent of the plugin-count gate. See the Global Gating Rules section for the exact
restated rule.

### Subphase 5.1 — Grounding & scoping
- Stage 5.1.1 — define approved grounding sources; confirm source scoping honors library permissions.
  **Deliverable:** `approved-grounding-sources.md`. **Verification:** each source has an owner, permission
  scope, and review status. **Evidence:** governance approval plus permission-test results.
  **Decision owner:** the Phase 3 library's accountable owner.
- Stage 5.1.2 — agent instructions + explicit answer boundaries (what it must refuse). **Deliverable:**
  instruction/boundary document. **Verification:** boundary cases enumerated and each one tested against
  the deployed agent. **Evidence:** the boundary-test transcript. **Decision owner:** the agent's assigned
  owner (Stage 5.4.1).

### Subphase 5.2 — Content-currency behavior
- Stage 5.2.1 — current/stale/superseded handling using owner + review-date metadata from Phase 3.
  **Deliverable:** currency-handling policy. **Verification:** tested against at least one deliberately
  stale item in the pilot library. **Evidence:** the test transcript showing correct stale-content handling.
  **Decision owner:** the agent's assigned owner.
- Stage 5.2.2 — behavior when grounding content is out of review. **Deliverable:** out-of-review response
  policy (e.g., refuse, caveat, or escalate). **Verification:** tested against an item whose review date
  has lapsed. **Evidence:** the test transcript. **Decision owner:** the agent's assigned owner.

### Subphase 5.3 — Evaluation
- Stage 5.3.1 — answerable evaluation set (grounded, correct, cited). **Deliverable:** answerable-case
  evaluation set + results. **Verification:** each case checked for correct grounding and citation, not
  just a non-empty answer. **Evidence:** the evaluation run's recorded results. **Decision owner:** the
  agent's assigned owner.
- Stage 5.3.2 — unanswerable evaluation set (agent declines rather than fabricates). **Deliverable:**
  unanswerable-case evaluation set + results. **Verification:** each case confirms a decline, not a
  fabricated answer. **Evidence:** the evaluation run's recorded results. **Decision owner:** same.
- Stage 5.3.3 — permission/oversharing probes across identities. **Deliverable:** permission-probe set +
  results. **Verification:** probes run under at least two distinct permission identities, confirming no
  oversharing. **Evidence:** the probe transcripts. **Decision owner:** same, with the Phase 3 library
  owner co-signing.

### Subphase 5.4 — Deployment & lifecycle governance
- Stage 5.4.1 — deployment approval path; ownership; review cadence. **Deliverable:** deployment-approval
  record. **Verification:** named accountable owner signs off before deployment. **Evidence:** the signed
  approval record.

**Exit gate:** One grounded agent passing answerable + unanswerable + permission evaluation sets;
stale-content handling demonstrated; deployment governed by an accountable owner.

---

## Phase 5.5A — Content Model Expansion

**(Split from a single Phase 5.5, round-5 finding, GPT 5.6: an either/or exit gate across two
independently-triggered tracks created an accounting problem — completing only the renderer track could
mark the umbrella phase closed while the content-model track remained untouched, silently losing its
future home. Split into two independently tracked phases with their own status and exit gate.)**

**Disposition:** NOT TRIGGERED (RESEARCH once triggered). **Detail level:** Structure only.

**Goal:** Prove or disprove that the canonical content model generalizes beyond one content type
("manual"), using a real second case rather than speculative design.

**Entry gate:** A concrete second content type (policy, procedure, or training material) is identified with
a real document/need behind it — not invented to exercise this phase.

### Subphase 5.5A.1 — Content Model Expansion
- Stage 5.5A.1.1 — select a second real content type. **Deliverable:** selection memo. **Verification:**
  a real document of that type exists and has a real owner/need. **Evidence:** the memo naming the
  document and owner.
- Stage 5.5A.1.2 — analyze its structural and governance differences from "manual." **Deliverable:**
  gap-analysis document. **Verification:** every structural/governance difference from the manual profile
  is enumerated, not assumed absent. **Evidence:** the gap-analysis document.
- Stage 5.5A.1.3 — determine which canonical fields are shared vs. profile-specific. **Deliverable:**
  field-classification table. **Verification:** every canonical field classified shared/profile-specific
  with a stated reason. **Evidence:** the table.
- Stage 5.5A.1.4 — create authoring guidance and templates for the new type. **Deliverable:** authoring
  guide + template. **Verification:** a person unfamiliar with the type can follow the guide to author a
  valid example. **Evidence:** the guide/template plus a dry-run authoring attempt.
- Stage 5.5A.1.5 — convert one real example end-to-end. **Deliverable:** a real converted canonical
  package. **Verification:** passes the same canonical/render validators Phase 2 hardened, with no
  exceptions carved out for the new type. **Evidence:** validation reports.
- Stage 5.5A.1.6 — prove existing consumers (Phase 2's hardened contract, the renderer, any Phase 3-5
  pilots already live) do not break. **Deliverable:** regression-test run against existing consumers.
  **Verification:** full suite passes with the new type's fixture added, no existing test loosened.
  **Evidence:** the test run's exact pass/fail counts.
- Stage 5.5A.1.7 — decide, with evidence, whether the canonical model genuinely generalizes or needs a
  content-type-specific extension. **Deliverable:** decision record. **Verification:** the decision cites
  the evidence from Stages 5.5A.1.1-1.6, not a general impression. **Evidence:** the decision record.
  **Decision owner:** the initiative's technical lead.

**Exit gate:** One real second content type converted end-to-end, passing existing validators, with no
broken consumers, and an evidenced generalization decision recorded. Not evaluable until its entry gate is
met.

---

## Phase 5.5B — Renderer Expansion

**Disposition:** NOT TRIGGERED (RESEARCH once triggered) — independent of Phase 5.5A's status; completing
one does not close the other. **Detail level:** Structure only.

**Goal:** Prove or disprove that the publication contract generalizes beyond one renderer
("multipage-markdown"), using a real required output format rather than speculative design.

**Entry gate:** A concrete required output format (Word, PDF, HTML, PowerPoint, SharePoint `.aspx`) is
identified with a real need behind it — not invented to exercise this phase. **SharePoint `.aspx`'s entry
gate is met:** Phase 3.0's ASPX/modern-page conversion experiment
(`docs/research/research-experimentation/tenant-discovery/field-note-sharepoint-write-capability-discovery.md` §15) and Phase 5's
ASPX-vs-Markdown grounding comparison (`docs/research/knowledge-discovery-retrieval/field-note-aspx-vs-markdown-grounding.md`)
are both real, evidenced needs for a deterministic ASPX renderer, not invented ones.

**Scope guardrail (external review finding, 2026-08-02, GPT 5.6):** this phase stays limited to
**deterministic** renderer expansion — `structured content package → deterministic renderer →
validated output format`. Do not broaden it into an agent editing-and-publication workflow, or into
agent-performed rendering of edited content. That concern belongs to Phase 6 Subphase 6.3 (runtime
placement) and the future placeholder Phase 6.5 (Ongoing Structured Content Maintenance and
Assisted Republishing) — see
`docs/vision/resolved-question-ongoing-editing-and-agent-assisted-rendering-phase-placement.md`.

### Subphase 5.5B.1 — Renderer Expansion
- Stage 5.5B.1.1 — identify a real required output format (not speculative). **Deliverable:** format
  requirement memo. **Verification:** a real, named need exists for this format. **Evidence:** the memo.
- Stage 5.5B.1.2 — compare direct canonical-to-format rendering against transforming from the existing
  Markdown output. **Deliverable:** comparison memo. **Verification:** both approaches actually prototyped
  at a small scale before choosing. **Evidence:** the comparison memo with both prototypes' results.
- Stage 5.5B.1.3 — define the output profile/contract for the new renderer. **Deliverable:** renderer
  contract document. **Verification:** conforms to the `Renderer` protocol Phase 2 hardened
  (`supported_manifest_versions`, `render(package, output_dir) -> RenderResult`). **Evidence:** the
  contract document.
- Stage 5.5B.1.4 — implement one additional renderer. **Deliverable:** the renderer implementation.
  **Verification:** TDD per this repo's standing rule; registers with the existing renderer registry
  without modifying it. **Evidence:** the test suite for the new renderer.
- Stage 5.5B.1.5 — run fidelity and golden-master validation against it, same discipline as Phase 2's
  Subphase 2.5.4. **Deliverable:** golden-master comparison for the new renderer's output.
  **Verification:** byte-identical (or format-appropriate equivalent) comparison against an accepted
  baseline. **Evidence:** the comparison test results.
- Stage 5.5B.1.6 — decide whether renderer extraction into a separate module/plugin is warranted (per the
  extraction triggers, Stage 2.5.3). **Deliverable:** extraction decision record. **Verification:** checked
  against the actual extraction triggers, not a general preference. **Evidence:** the decision record.
  **Decision owner:** the initiative's technical lead.

**Exit gate:** One additional renderer implemented and passing fidelity/golden-master validation. Not
evaluable until its entry gate is met.

**Rendering-skill packaging reassigned (2026-08-03):** the 7 rendering/rendering-template skills
(`render-multipage-markdown`, `render-sharepoint-aspx`, `create-markdown-rendering-template`,
`create-aspx-rendering-template`, `validate-rendering-template`, `validate-rendered-output`,
`compare-rendered-output`) were briefly recorded here as Subphase 5.5B.2, then reassigned into
**Phase 6 Task 0.16** per explicit direction, to keep all of Task 0's capability additions in one
place. See `docs/superpowers/plans/phase-6-multi-runtime-capability-model-plan-scaffold.md`
Task 0.16 for the full task table — not duplicated here.

---

## Phase 6 — Multi-Runtime Capability Model

**Disposition (as of 2026-08-03): split.** **Task 0: `AUTHORIZED_AND_IN_PROGRESS`** — builds the
missing repository/Claude second runtime for `review-manual-topics` plus the full `sharepoint-
agents-and-skills`, `sharepoint-content-publication` (completion), `structured-content-rendering`
(skill packaging), and `workbench-setup` (foundational) capability sets — see
`docs/superpowers/plans/phase-6-multi-runtime-capability-model-plan-scaffold.md` Task 0 for the
full 31-skill task table. **Tasks 1–12 (below): `NOT_AUTHORIZED_UNTIL_TASK_0_EXIT_GATE`**,
`LATER`, gated behind ≥2 real runtimes existing. **Detail level (Tasks 1–12 only):** Decision
framework only.

**Goal:** Define a shared capability specification once two real runtimes (e.g. GitHub/Claude skill +
native SharePoint skill) exist to specify against — preventing behavioral drift across runtimes.

**Entry gate (Tasks 1–12 only):** At least two runtimes implement the same capability in
production. **Status (verified 2026-08-03): `SECOND_RUNTIME_REQUIRED` — gate not met.** One
SharePoint-side runtime exists (the deployed, tenant-exercised `review-manual-topics` native
skill, Phase 4); the repository/Claude-side runtime is being built now under Task 0.3. See
`docs/superpowers/specs/phase-6-multi-runtime-capability-model-spec.md` Section 1 for the full
evidence review.

### Subphase 6.1 — Capability specification format
- Stage 6.1.1 — extract the shared contract from the two existing runtime implementations (do not design
  speculatively). **Deliverable:** shared-contract document. **Verification:** every element traced to
  something both real implementations actually do. **Evidence:** the document with per-element traces.
- Stage 6.1.2 — common evaluation-case set both runtimes must pass. **Deliverable:** evaluation-case set.
  **Verification:** run against both real runtimes with recorded results. **Evidence:** both runtimes'
  results.
- Stage 6.1.3 — **adversarial intent-preservation check (round-4 finding, GPT 5.6).** Do not derive the
  "shared specification" merely by intersecting what the two implementations happen to do — both may share
  the same accidental limitation. Explicitly: compare both runtime implementations against the *original*
  user capability and governance intent (not against each other only); separate essential behavior from
  implementation coincidence; record intentional target-specific differences rather than erasing them;
  validate that shared evaluation cases test *meaning*, not merely matching output strings. **Deliverable:**
  intent-preservation review document. **Verification:** each shared-spec element checked against the
  originating capability/governance intent, not just cross-runtime agreement. **Evidence:** the review
  document. **Decision owner:** the initiative's technical lead.

### Subphase 6.2 — Adapters & drift detection
- Stage 6.2.1 — target-specific adapters over the shared spec. **Deliverable:** adapter implementations.
  **Verification:** each adapter passes the Stage 6.1.2 common evaluation set for its target.
  **Evidence:** per-adapter test results.
- Stage 6.2.2 — behavioral-drift detection comparing runtimes against the common cases. **Deliverable:**
  drift-detection mechanism. **Verification:** deliberately introduce a drift in one runtime and confirm
  detection. **Evidence:** the detection test result.
- Stage 6.2.3 — reuse-vs-target-specific-behavior decision rules. **Deliverable:** decision-rule document.
  **Verification:** at least one real reuse-vs-specific decision made using the rules, not hypothetically.
  **Evidence:** the applied decision record.

### Subphase 6.3 — Runtime placement for content-lifecycle actions

**(Added from external review, 2026-08-02, GPT 5.6 — Phase 5 brainstorming placement question. See
`docs/vision/resolved-question-ongoing-editing-and-agent-assisted-rendering-phase-placement.md`.)**

Phase 3 Stage 3.1.4 decides *what* the ongoing structured-content maintenance workflow must do
(review, approval, versioning, lineage/hash/manifest recalculation). This subphase decides *which
runtime* performs each step, once ≥2 real runtimes exist to decide against (this subphase inherits
Phase 6's overall entry gate — not separately triggered).

- Stage 6.3.1 — for each content-lifecycle action (propose edit, validate edit, recalculate
  lineage/hashes/manifests, render to a format, publish/reconcile), decide: may an agent only
  recommend the action; may a native skill invoke approved deterministic tooling; must a
  deterministic pipeline/workstation process perform the authoritative update. **Deliverable:**
  runtime-placement decision table, one row per action. **Verification:** every action in Phase
  3.1.4's maintenance workflow has an explicit runtime assignment, not a default assumption.
  **Evidence:** the decision table.
- Stage 6.3.2 — define when an agent-generated representation (e.g. an ad hoc rendering of edited
  content) is a non-authoritative preview versus an official publication. **Deliverable:**
  preview-vs-authoritative rule. **Verification:** the rule states the exact contract/validation an
  agent-generated output must pass before it can be treated as authoritative (same contracts as
  the deterministic pipeline, not a lighter bar). **Evidence:** the rule document.
  **Non-negotiable, stated here to prevent drift:** conversational/agent rendering is never
  authoritative for official publication on its own. The operating model is: agent assists or
  requests → deterministic tooling updates/renders → validation executes → human/governed workflow
  approves → publication reconciles.
- Stage 6.3.3 — how evidence, permissions, and rollback differ by runtime (deterministic pipeline
  vs. native skill vs. agent). **Deliverable:** per-runtime evidence/rollback matrix.
  **Verification:** each runtime's rollback/audit story is concretely described, not assumed
  equivalent to the others. **Evidence:** the matrix.

**Exit gate (for this subphase only):** every Phase 3.1.4 maintenance-workflow action has a
recorded runtime-placement decision, and the preview-vs-authoritative rule is defined. Feeds a
future Phase 6.5 entry gate (see below) — does not itself authorize that phase.

**Exit gate:** Shared spec + common evaluation cases demonstrably prevent drift across ≥2 runtimes, proven
against original intent (Stage 6.1.3), not just cross-runtime agreement. Not evaluable until the entry gate
is met.

---

## Phase 6.5 — Ongoing Structured Content Authoring and Republishing

**(Added from external review, 2026-08-02, GPT 5.6 — Phase 5 brainstorming placement question;
elaborated in a follow-up review the same day. See
`docs/vision/resolved-question-ongoing-editing-and-agent-assisted-rendering-phase-placement.md` for the
full architecture note this phase is drawn from. Named "Ongoing Structured Content Authoring and
Republishing" per the follow-up review's clearer naming — supersedes the initial working title
"Ongoing Structured Content Maintenance and Assisted Republishing.")**

**Disposition:** NOT TRIGGERED, NOT AUTHORIZED (RESEARCH once triggered). **Detail level:**
Structure only — this phase is a placeholder so the concern has a named future home; it does not
authorize any implementation. Per the follow-up review: this should become a later dedicated
phase, *after* the current Phase 5 prototype clarifies how people actually interact with the
published content — not pulled forward ahead of that evidence.

**Goal:** Implement the ongoing structured-content authoring/republishing loop, once Phase 3
Stage 3.1.4 (what the workflow must do) and Phase 6 Subphase 6.3 (which runtime does each step)
have both answered their respective design questions.

**Diagram:** `docs/diagrams/09-phase6-5-ongoing-authoring-and-republishing-loop.mmd` renders the
loop and runtime division below.

**The loop this phase closes** (three flows total, correcting the original two-flow framing in
the architecture note above — ingestion and publication already exist; this is the third,
currently missing, flow):

```text
Published structured content
  → edit or change proposal (SharePoint surface: direct edit, change proposal, review comment,
    agent-assisted drafting)
  → GitHub Copilot/Claude-assisted review and update (workstation content-engineering environment
    applies the approved change to structured source content)
  → validated structured content package (deterministic tooling: identity, lineage, hashes,
    cross-references, publication mappings recalculated)
  → re-render (deterministic renderer(s), all affected output representations)
  → republish and reconcile in SharePoint
  → SharePoint agents/native skills consume the updated published content
  → discover another improvement (loop repeats)
```

**Runtime division** (feeds Phase 6 Subphase 6.3's per-action runtime-placement decisions, not a
substitute for them):
- **SharePoint agent / native skill** — helps find content, proposes edits, reviews changes,
  gathers intent. Does not itself become the authoritative update path.
- **GitHub Copilot/Claude workbench** — applies the approved change to structured source content
  (the content-engineering environment, not SharePoint).
- **Deterministic tooling** — validates the change, updates hashes/lineage, renders, and
  republishes. This is the validation and rendering authority; official outputs must pass through
  it even when an agent assisted upstream.
- **SharePoint** — hosts the governed human-facing and agent-facing outputs.
- **SharePoint agents** — the user-facing knowledge interface consuming the republished result.

**Entry gate (all required, not yet met):**
- one real post-conversion content correction exists (not hypothetical);
- an identified business editor for that correction;
- an approved authoritative-source model (from Phase 3.1.4);
- one demonstrated second-format or republishing need;
- a runtime-placement decision covering the correction's lifecycle actions (from Phase 6.3);
- a permissions and approval model for the correction.

**Likely scope once triggered** (not authorized, not detailed at stage level yet): editing or
change-proposal models; SharePoint-to-Git change intake; agent-assisted authoring; human approval;
structured package updates; lineage and hash regeneration; impact analysis across related topics
(a change to one topic may affect cross-references in others); selective or complete re-rendering;
SharePoint republication and reconciliation; rollback and audit history.

**Explicit non-goal:** this phase does not fold into, or get folded into, Phase 5.5B. Phase 5.5B
stays limited to deterministic renderer expansion (structured content package → deterministic
renderer → validated output format, e.g. ASPX/PDF/Word/agent-grounding representation) — it must
not be broadened into an agent editing-and-publication workflow.

**Exit gate:** Not evaluable until the entry gate is met and the phase is explicitly authorized.

---

## Phase 7 — Cowork & Copilot Studio Evaluation

**Disposition:** RESEARCH (owner-and-use-case gate). **Detail level:** Decision framework, candidate pilots
only.

**Status (2026-08-03, desk-research round):** entry gate met (concrete use case + owner, see
`docs/superpowers/specs/2026-08-03-phase-7-cowork-copilot-studio-desk-research-design.md`). Both
Subphase 7.1 deliverables (gap-analysis memo, candidate list) are complete — see
`docs/reports/phase-7-cowork-copilot-studio-evaluation/desk-research-evidence-memo.md`. Cowork and
Copilot Studio both `REMAIN_RESEARCH`. **This exit gate — Stage 7.2.2's build/no-build decision —
remains `DEFERRED`, not yet satisfied**; the desk-research round does not by itself close Phase 7.
Re-entry triggers: a Copilot Studio Dedicated Environment becomes available, or Copilot Cowork
becomes enabled in the tenancy.

**Goal:** Decide, per target, whether to build — only for a target that has a concrete use case and an
accountable owner.

**Entry gate:** A concrete use case with a named accountable owner emerges. Until then, do not scaffold
packaging plugins or manifests.

### Subphase 7.1 — Capability-gap analysis
- Stage 7.1.1 — identify what Cowork/Copilot Studio would do that existing plugins/skills/agents cannot.
  **Deliverable:** gap-analysis memo. **Verification:** each named gap checked against what Phases 1-6
  actually already provide, not assumed absent. **Evidence:** the memo.
- Stage 7.1.2 — candidate use cases with named owners. **Deliverable:** candidate list. **Evidence:** the
  list, empty if no owner has yet come forward — an empty list is a valid, honest result here.

### Subphase 7.2 — Build/no-build gate
- Stage 7.2.1 — connector/external-system, workflow/orchestration, licensing/capacity/environment
  requirements per candidate. **Deliverable:** requirements memo per candidate. **Verification:** checked
  against actual licensing/capacity facts, not assumed. **Evidence:** the memo.
- Stage 7.2.2 — explicit build/no-build decision per target; build only the one with a concrete use case +
  owner. **Deliverable:** decision record per target. **Verification:** cites the specific use case and
  owner, or explicitly states neither exists yet. **Evidence:** the decision record. **Decision owner:**
  the initiative's technical lead + the named use-case owner, jointly.

**Exit gate:** A documented build/no-build decision per target, each traceable to a concrete use case and
owner, or an explicit "no owner/use case yet — remain RESEARCH."

---

## Phase 8 — Scale, Promotion & Operations

**Disposition:** LATER, activates **incrementally per capability** (round-5 fix, GPT 5.6 — a single
monolithic "Phases 3-5 all complete" gate could block operationalizing a successful Phase 3 pilot merely
because Phase 4 or 5 stalled on an unrelated tenant/owner blocker). **Detail level:** Operational
capability categories + entry criteria only.

**Goal:** Turn proven pilots into operable, monitored, lifecycle-managed capabilities — designed from real
operational experience, not in advance of it.

**Entry gate (corrected — round-5 finding, GPT 5.6):** Phase 8 activates **per capability**, not as one
block:
- The Phase 3 library may enter promotion/lifecycle management (Subphases 8.1/8.3, scoped to the library)
  as soon as Phase 3's own exit gate is met — it does not wait for Phase 4 or 5.
- A Phase 4 skill may enter skill lifecycle management as soon as Phase 4's own exit gate is met.
- A Phase 5 agent may enter agent operations as soon as Phase 5's own exit gate is met.
- **Cross-capability** concerns — Subphase 8.2's monitoring/drift detection *across* multiple capabilities,
  and any shared release-compatibility policy spanning more than one capability — require at least two
  operational capabilities to exist first (i.e. at least two of Phase 3/4/5 have individually reached this
  gate).
- Records/retention/audit (Subphase 8.4) may be pulled forward as soon as the Phase 3 retrospective
  (Stage 3.5.2) surfaces a concrete need — it does not wait for the rest of Phase 8 either.

### Subphase 8.1 — Promotion & release management
- Stage 8.1.1 — dev/test/production promotion path. **Deliverable:** promotion-path document, scoped to
  whichever capability triggered it first. **Verification:** at least one real artifact (skill, agent, or
  library schema change) actually promoted through it. **Evidence:** the promotion record.
- Stage 8.1.2 — release management + version compatibility across contracts, skills, agents.
  **Deliverable:** version-compatibility policy — single-capability scope until the cross-capability
  entry gate above is met, then extended. **Verification:** at least one real version bump exercised
  against it. **Evidence:** the compatibility-check result for that bump.

### Subphase 8.2 — Monitoring & assurance

**(Cross-capability — requires ≥2 operational capabilities per the entry gate above.)**

- Stage 8.2.1 — monitoring + behavioral-drift detection in production. **Deliverable:** monitoring
  mechanism spanning the ≥2 live capabilities. **Verification:** a deliberately introduced drift in one
  capability is detected. **Evidence:** the detection test result.
- Stage 8.2.2 — release evidence/auditability at scale. **Deliverable:** cross-capability release-evidence
  process. **Verification:** at least one real release across ≥2 capabilities produces the required
  evidence. **Evidence:** that release's evidence record.

### Subphase 8.3 — Ownership & lifecycle
- Stage 8.3.1 — ownership/support model, review cycles, incident handling. **Deliverable:**
  ownership/support charter. **Verification:** a named owner and a real incident (or drill) run through
  the documented process. **Evidence:** the charter plus the incident/drill record.
- Stage 8.3.2 — deprecation/retirement. **Deliverable:** deprecation/retirement procedure. **Verification:**
  exercised against one real (or deliberately staged) retirement. **Evidence:** the exercised procedure's
  record.
- Stage 8.3.3 — onboarding/adoption patterns for reuse. **Deliverable:** onboarding guide. **Verification:**
  a person unfamiliar with the capability follows it to onboard. **Evidence:** the onboarding attempt's
  record.

### Subphase 8.4 — Records, Retention & Audit

**(New subphase, round-4 finding, GPT 5.6 — Workstream C named records/retention/audit as LATER but no
phase or subphase ever picked the work up; this gives it an explicit home without inventing the actual
rules before the Phase 3 pilot surfaces real requirements.)**

- Stage 8.4.1 — determine records classification requirements from the SharePoint pilot's actual content
  (Phase 3 retrospective, Stage 3.5.2). **Deliverable:** classification memo. **Verification:** every
  classification cites a specific Phase 3 pilot item, not a generic records category. **Evidence:** the
  memo.
- Stage 8.4.2 — define retention treatment for canonical and published artifacts. **Deliverable:** retention
  policy. **Verification:** approved by records/legal review (Stage 8.4.5) before any enforcement.
  **Evidence:** the approved policy.
- Stage 8.4.3 — define audit evidence requirements (what must be provable, to whom, for how long).
  **Deliverable:** audit-requirements document. **Verification:** approved by records/legal review.
  **Evidence:** the approved document.
- Stage 8.4.4 — define supersession and destruction handling. **Deliverable:** supersession/destruction
  policy. **Verification:** approved by records/legal review. **Evidence:** the approved policy.
- Stage 8.4.5 — obtain the appropriate policy/legal/records review before implementing any of the above —
  this subphase does not invent records-management rules unilaterally. **Deliverable:** the review
  sign-off itself. **Verification:** a named records/legal reviewer actually reviewed Stages 8.4.1-8.4.4,
  not a self-certification. **Evidence:** the signed review record. **Decision owner:** the named
  records/legal reviewer.

**Exit gate:** Each operational capability category (promotion, monitoring, ownership, records) has an
owner, a defined process exercised at least once, and — for records/retention/audit specifically — the
required policy/legal review completed before any rule is enforced in production.

---


### Phase 9 — Reusable SharePoint Plugin Extraction

**Disposition:** LATER — selective ecosystem expansion, not a migration of the legacy source repository. **Detail level:** Requirements, evidence gates, and subphase structure only; exact extraction internals remain provisional until a pinned source baseline and one pilot capability are selected. Phase 9 has not started.

**Goal:** Selectively extract proven generic SharePoint capabilities from the legacy source repository, refactor them into independently reusable first-party plugins in the SharePoint Knowledge Workbench, and prove that the extracted plugins operate without legacy system, proprietary backend, tenant, environment, or cross-repository runtime dependencies while leaving the source repository and its plugins intact and independently operable.

**Source assessment baseline (observed 2026-08-01, not pinned):** `legacy-source-repository/plugins/sharepoint-migration/skills/` contains 119 directories and 272 files (144 real files + 128 symlinks) across 33 skills spanning discovery, schema, classic-page modernization, link analysis, content migration, provisioning/validation, and reporting. These figures describe the supplied baseline inventory at observation time — not a permanent total, since the source repository continues to evolve independently — and Stage 9.0/9.1 must pin an exact commit before any extraction begins. Full detail: `docs/superpowers/specs/phase-9-reusable-sharepoint-plugin-extraction-spec.md` §3a. **Phase 9 is selective extraction using this baseline as a classification input, not a repository migration** — the 272-file tree is not copied wholesale into the destination repository.

**Long-term workbench scope intent:** Phase 9's eventual outcome is intended to expand this repository beyond knowledge conversion/publication into a broader SharePoint engineering workbench — also covering site migration, page conversion/analysis, and web-part analysis. This is a stated future direction that informs why Phase 4.5's plugin conventions must be general enough for both families; it is not an authorization to begin that expansion.

**Entry gate:**
- The current SharePoint Knowledge Workbench phases have established stable destination conventions for first-party plugins, tests, evidence, lifecycle, and shared rules. **Phase 4.5 is the source of these conventions** (plugin manifests, domain-native skill ownership, implementation-status metadata, independent semantic versions, contract versions, compatibility matrix, three-tier test/fixture ownership, documentation categories, marketplace registration, dependency rules, lifecycle and removal gates) — Phase 9 must reuse them rather than inventing a second plugin system.
- Phase 3 has established expected-state, actual-state, reconciliation, permission, and evidence patterns that extracted SharePoint plugins must follow where applicable.
- A fixed legacy repository commit or immutable review bundle is selected as the extraction baseline (distinct from the observed-but-unpinned baseline above).
- At least one source capability demonstrates plausible reuse outside the legacy project.
- One pilot capability family is explicitly selected and approved after comparing at least `sharepoint-discovery`, `sharepoint-schema`, and `sharepoint-page-modernization` — **no candidate is pre-selected**. The observed source inventory shows `sp-converting-aspx-pages` (core of page modernization) has a materially richer implementation (27 files: full analyze→classify→map→preview→reconstruct→provision→validate→report pipeline, tests, fixtures, schema, architecture diagram) than most discovery skills (3-10 files, several likely planned-only), which may make page modernization a stronger pilot than originally assumed. Selection requires the full three-axis classification (implementation status, destination disposition, backlog priority) from Phase 9 spec §3b, not a read/write-risk heuristic alone.
- The original legacy repository remains the operational source implementation and regression reference. Phase 9 does not rename it, remove its plugins, or make it depend on the workbench.

**Explicit non-goals:**
- No legacy repository rename, migration, dismantling, or cleanup.
- No automatic movement of every source plugin, skill, script, agent, backlog item, or rule.
- No extraction of legacy backend integrations or domain-specific routing logic.
- No cross-repository symlinks or runtime imports.
- No immediate rebinding of LegacySource to consume workbench plugins.
- No general-purpose orchestration agent merely because source sub-agents exist.
- No write-capable extraction as the first pilot unless separately justified and approved.

#### Subphase 9.1 — Source baseline and inventory
- Stage 9.1.1 — pin the source baseline. **Deliverable:** source-baseline record naming the legacy repository commit or immutable bundle, repository role, and evidence location. **Verification:** hash/commit can be independently resolved and the source repository is unchanged. **Evidence:** baseline record plus manifest hashes.
- Stage 9.1.2 — inventory source capabilities. **Deliverable:** inventory of plugins, skills, agents, scripts, tests, references, assets, rules, configuration, symlinks, and known consumers. **Verification:** each item classified active, planned, obsolete, historical, project-specific, or candidate-reusable. **Evidence:** inventory report and completeness check.
- Stage 9.1.3 — identify source behaviour and test oracles. **Deliverable:** source-behaviour matrix linking each candidate to existing tests, fixtures, acceptance criteria, and proven outcomes. **Verification:** no candidate advances based only on a name or README claim. **Evidence:** matrix with source references.

#### Subphase 9.2 — Capability classification and prioritization
- Stage 9.2.1 — classify every candidate capability. **Deliverable:** disposition matrix using `EXTRACT_NOW`, `EXTRACT_LATER`, `MERGE_WITH_EXISTING_CAPABILITY`, `KEEP_PROJECT_SPECIFIC`, `RESEARCH`, `RETIRE`, or `REJECT`. **Verification:** every disposition has a reason, owner, dependency assessment, and safe default. **Evidence:** reviewed disposition matrix.
- Stage 9.2.2 — assess individual skills located under project-specific plugins. **Deliverable:** skill-level review, including skills currently housed under the ORDS plugin. **Verification:** classification is based on the skill's actual responsibility, not its current directory. Generic SharePoint skills may qualify; ORDS execution patterns and court-system business logic do not. **Evidence:** skill-level decision record.
- Stage 9.2.3 — select one pilot plugin family. **Deliverable:** selection memo comparing at least `sharepoint-discovery`, `sharepoint-schema`, and `sharepoint-page-modernization`. **Verification:** selection considers reuse value, read/write risk, coupling, test maturity, overlap, ownership, and extraction effort. **Evidence:** approved memo. **Recommended initial candidate:** `sharepoint-discovery`.

#### Subphase 9.3 — Coupling and dependency analysis
- Stage 9.3.1 — map all dependencies for the selected pilot. **Deliverable:** coupling matrix covering legacy literals, list/field names, tenant URLs and IDs, app registrations, environment names, ORDS dependencies, business rules, shared PowerShell modules, cross-plugin references, symlinks, fixtures, and permissions. **Verification:** each dependency is marked remove, parameterize, replace, retain-as-provenance, or block. **Evidence:** reviewed coupling matrix.
- Stage 9.3.2 — define the generic capability contract. **Deliverable:** target-neutral input, output, error, permission, dry-run, evidence, and lifecycle contract. **Verification:** no contract field requires legacy systems or a specific tenant. **Evidence:** contract document and adversarial review.
- Stage 9.3.3 — define source-to-destination provenance. **Deliverable:** provenance manifest connecting extracted files and behaviours to the pinned source baseline. **Verification:** a future maintainer can identify what was adapted, rewritten, omitted, or intentionally diverged. **Evidence:** provenance manifest.

#### Subphase 9.4 — Shared instruction and rule reconciliation
- Stage 9.4.1 — classify source instructions. **Deliverable:** rule inventory using `GENERIC_ENGINEERING`, `GENERIC_SHAREPOINT`, `PLUGIN_SPECIFIC`, `LegacySource_SPECIFIC`, `ENVIRONMENT_FACT`, `DUPLICATE`, or `CONFLICTING`. **Verification:** source `CLAUDE.md`, Copilot instructions, and applicable rule files are accounted for without wholesale copying. **Evidence:** rule-classification report.
- Stage 9.4.2 — reconcile generic rules into the destination. **Deliverable:** proposed destination rule changes. **Verification:** destination rules remain authoritative; duplicates are consolidated; conflicts are explicitly decided; LegacySource and environment facts remain in the source repository. **Evidence:** rule-diff review and decision record.
- Stage 9.4.3 — establish plugin-local guidance. **Deliverable:** only the selected plugin's genuinely specific technical rules placed in that plugin's documentation. **Verification:** no source-project operational state leaks into root workbench guidance. **Evidence:** documentation review.

#### Subphase 9.5 — Pilot plugin extraction
- Stage 9.5.1 — create the selected first-party plugin using destination conventions. **Deliverable:** plugin manifest, skills, scripts/modules, references, schemas, fixtures, and tests. **Verification:** follows the workbench's current plugin structure and marketplace metadata rules; exact paths are finalized through the Phase 9 implementation plan, not assumed here. **Evidence:** plugin tree and manifest validation.
- Stage 9.5.2 — remove or replace project coupling. **Deliverable:** neutral configuration and interfaces. **Verification:** repository scan reports zero live legacy project identifiers, proprietary backend systems, tenant URL/GUID, environment, or cross-repository runtime dependencies except explicit provenance documentation and negative-control fixtures. **Evidence:** raw scan output and reviewed exceptions.
- Stage 9.5.3 — preserve safe defaults. **Deliverable:** read-only-by-default behaviour for discovery candidates; explicit dry-run, confirmation, least-privilege, partial-failure, and evidence handling for any future write-capable capability. **Verification:** safety tests fail if unapproved writes become reachable. **Evidence:** safety test results.

#### Subphase 9.6 — Independent fixtures, tests, and parity proof
- Stage 9.6.1 — create neutral fixtures. **Deliverable:** sanitized, project-independent SharePoint fixtures and expected outputs. **Verification:** fixtures contain no live tenant identifiers, protected content, LegacySource schema, or ORDS data. **Evidence:** fixture audit.
- Stage 9.6.2 — prove destination independence. **Deliverable:** isolated test run with the legacy repository, source symlinks, source configuration, and source environment unavailable. **Verification:** all plugin tests and documented user journeys pass. **Evidence:** test report with exact counts.
- Stage 9.6.3 — prove semantic parity for deliberately retained behaviours. **Deliverable:** source-versus-destination comparison. **Verification:** selected generic behaviours match the pinned source oracle or have an explicitly reviewed contract improvement; no test is loosened merely to pass. **Evidence:** parity report and disposition of intentional differences.
- Stage 9.6.4 — run adversarial and mutation tests. **Deliverable:** tests for project-literal leakage, missing configuration, permission failure, malformed expected state, partial discovery, and silent-success prevention. **Verification:** deliberate defects reach their intended detectors. **Evidence:** mutation matrix.

#### Subphase 9.7 — Workbench integration and documentation
- Stage 9.7.1 — integrate plugin metadata and repository navigation. **Deliverable:** applicable plugin/marketplace metadata, README, architecture, dependency, and `start-here.md` updates. **Verification:** links resolve and descriptions distinguish implemented capabilities from future candidates. **Evidence:** documentation and metadata validation.
- Stage 9.7.2 — define lifecycle and ownership. **Deliverable:** owner, versioning, compatibility, review cadence, deprecation, and retirement policy for the extracted plugin. **Verification:** named decision owner and one exercised update/rollback or removal scenario where applicable. **Evidence:** lifecycle record.
- Stage 9.7.3 — assess agents and orchestration. **Deliverable:** decision record for source agents. **Verification:** agents are adapted only when the extracted plugin has a bounded user journey that benefits from one; no general router is created without satisfying the roadmap's multi-plugin gate. **Evidence:** decision record.

#### Subphase 9.8 — Source-repository preservation and non-rebinding proof
- Stage 9.8.1 — verify source preservation. **Deliverable:** source-repository status report. **Verification:** no source files, plugins, rules, manifests, or runbooks were removed or changed as a side effect of extraction. **Evidence:** pinned-baseline comparison.
- Stage 9.8.2 — verify independent operation. **Deliverable:** non-rebinding proof. **Verification:** the legacy repository has no new dependency on the workbench, no cross-repository symlink, and no required import from the extracted plugin. **Evidence:** dependency scan and source test result where safely available.
- Stage 9.8.3 — record any future consumer-rebind option. **Deliverable:** separate decision note only. **Verification:** explicitly states that rebinding LegacySource to the reusable plugin would require its own spec, regression plan, and approval. **Evidence:** decision note.

#### Subphase 9.9 — Remaining ecosystem roadmap
- Stage 9.9.1 — prioritize remaining plugin families. **Deliverable:** ranked roadmap for discovery, schema, page modernization, link analysis, provisioning, content migration, and validation based on evidence from the pilot extraction. **Verification:** no capability is scheduled merely because it existed in the source repository. **Evidence:** prioritization matrix.
- Stage 9.9.2 — review backlog and planned skills selectively. **Deliverable:** backlog disposition record. **Verification:** planned and incomplete source items are reviewed and prioritized rather than automatically migrated. **Evidence:** backlog decision record.
- Stage 9.9.3 — retrospective. **Deliverable:** `phase-9-retrospective.md`. **Verification:** cites every stage's evidence and recommends whether the extraction pattern should be repeated, changed, or stopped. **Evidence:** reviewed retrospective.

**Exit gate:** One approved generic SharePoint capability family has been independently extracted from a pinned legacy source baseline into a first-party SharePoint Knowledge Workbench plugin. The extracted plugin contains no live legacy project identifiers, proprietary backend systems, tenant, environment, credential, or cross-repository runtime dependency; passes independent, safety, adversarial, and semantic-parity tests using neutral fixtures; follows destination plugin, evidence, security, documentation, and lifecycle conventions; and leaves the original legacy repository and its plugins unchanged and independently operable. All remaining source capabilities and backlog items are classified and prioritized rather than copied automatically.

---

## Full Traceability Matrix

Every major vision item, mapped to where it actually lives — not just a workstream, but a specific phase
and stage, its disposition, its prerequisite, its eventual exit evidence, and (where deferred/rejected) the
reason. This replaces the earlier workstream-only table, which GPT 5.6's round-4 review correctly noted
asserted completeness without demonstrating it.

| Vision item | Phase / stage | Disposition | Prerequisite | Exit evidence | Reason if deferred |
|---|---|---|---|---|---|
| DOCX is a transitional extraction format, not the canonical management format | Phase 1 (done), Phase 2 (hardens the independence) | NOW | — | **Combined evidence (round-5 correction, GPT 5.6 — a single import-boundary test proves only that the renderer doesn't transitively import DOCX-analysis modules, not the full claim):** Phase 2 Stage 2.3.2's import-boundary test, PLUS Stage 2.5.1's independent-fixture proof (canonical package loads/renders with no DOCX ever having produced it), PLUS Stage 2.5.2's runtime-independence test (DOCX/intake/temp physically absent), PLUS Phase 3 Stage 3.1.3's source-of-truth rule naming canonical (not DOCX, not published SharePoint pages) as authoritative | — |
| Structured content authoring guidance (manual) | Phase 1, `references/content-authoring-guide.md` | DONE | — | existing contract-test coverage | — |
| Policies, procedures, training content types | Phase 5.5A, Subphase 5.5A.1 | RESEARCH | a real second content type identified | Stage 5.5A.1.7's generalization decision | no second content type exists yet |
| SharePoint publication (Phase 3 manual pilot) | Phase 3, Subphase 3.2 | DONE | Phase 3.0 confirms feasibility | Stage 3.2.3's manual upload record | Phase 3 complete/closed, historical — not reopened |
| SharePoint publication (reusable skill automation) | Phase 6, Task 0.15 | `AUTHORIZED_AND_IN_PROGRESS` | Phase 3's manual pilot proved feasibility | the 5 packaged `sharepoint-content-publication` skills + tests, per Task 0's exit gate | — |
| Multi-format rendering / non-SharePoint targets (broader vision) | Phase 6, Task 0.16 | `AUTHORIZED_AND_IN_PROGRESS` | a real second output-format need identified | the 7 packaged `structured-content-rendering` skills + fidelity/golden-master validation, per Task 0's exit gate | ASPX's need is evidenced (Phase 3.0 §15, Phase 5's grounding comparison); Word/PDF/PowerPoint remain unneeded |
| Workbench setup / destination configuration (`workbench-setup` plugin) | Phase 6, Task 0.17 | `AUTHORIZED_AND_IN_PROGRESS` | design-complete (`docs/superpowers/specs/2026-08-02-multi-document-destination-configuration-design.md` Section 8) | the 3 packaged `workbench-setup` skills + tests, per Task 0's exit gate | `initialize-publication-profile` absorbed into `initialize-document-workflow`, not a separate skill |
| Package-only vs. authorized-write deployment | Phase 3, Subphase 3.2/3.4.3 | NEXT (package-only), LATER (authorized-write) | approved write identity for authorized-write | Stage 3.2.3 (package-only); Stage 3.3.6 dry-run report (authorized-write gate) | write path needs an approved owner/identity first |
| Publication reconciliation, rollback, drift | Phase 3, Subphase 3.3 | NEXT | Subphase 3.2 pilot exists | Stage 3.3.6's dry-run reconciliation report | — |
| Source-of-truth lifecycle (editing/drift/republish rules) | Phase 3, Stage 3.1.4 | NEXT | — | `source-of-truth-lifecycle.md` | — |
| Native `SKILL.md` assets | Phase 4 | RESEARCH | Phase 3.0 confirms authoring availability | Stage 4.2.1's validated `SKILL.md` | tenant capability unconfirmed |
| `AgentAssets` | Phase 3.0, Stage 3.0.2.1 | NEXT (discovery only) | tenant access | probe transcript | — |
| Quiz generation (`generate-quiz-from-content`) | Phase 4, Subphase 4.1 (candidate list) | RESEARCH | Phase 4's first candidate (review-manual-topics) evaluated first | — | additional candidates only after first is evaluated, per original vision doc |
| Apply-content-outline capability | Phase 4, Subphase 4.1 (candidate list) | RESEARCH | same as quiz generation | — | same |
| SharePoint agent grounding | Phase 5 | RESEARCH | Phase 3 library exists; Phase 3.0 confirms agent-creation permissions | Stage 5.1.1's grounding-source record | gated on 3/3.0, NOT unconditionally on Phase 4 (corrected dependency) |
| Permission-aware / stale-content agent behavior | Phase 5, Subphase 5.2 | RESEARCH | Phase 5 entry gate | Stage 5.2.1/5.2.2 test transcripts | — |
| GitHub/Claude skills (existing skills, originally under `docx-to-content`, decomposed 2026-08-01 into `source-document-extraction`/`document-structure-analysis`/`structured-content-assembly`/`structured-content-rendering` — see `docs/reports/phase-4-5-core-plugin-refactoring/plugin-skill-name-migration.md`) | Phase 1/2/4.5 | DONE/NOW | — | existing skill files | — |
| Common capability definitions across runtimes | Phase 6 | LATER | ≥2 real runtimes | Stage 6.1.3's intent-preservation check | no second runtime exists yet |
| Cowork | Phase 7 | RESEARCH | concrete use case + owner | Stage 7.2.2's build/no-build decision | no owner/use case yet — NOT a scope rejection |
| Copilot Studio | Phase 7 | RESEARCH | concrete use case + owner | Stage 7.2.2's build/no-build decision | same |
| Evaluation and governance (cross-cutting) | Phase 2 (mutation suites), Phase 3-6 (target-specific) | NOW (Phase 2 portion), LATER (rest) | each target phase's own entry gate | each phase's own exit gate | rest gated behind the capabilities they evaluate existing |
| Lifecycle and retirement | Phase 8, Subphase 8.3 | LATER | Phase 3-5 operational experience | Stage 8.3.1's charter + incident record | no operational experience yet |
| Oversharing risk | Phase 3, Stage 3.4.2 | NEXT | Phase 3 pilot | Stage 3.4.2's discoverability test result | — |
| Repository/plugin extraction triggers | `references/extraction-triggers.md` (Phase 2, Stage 2.5.3) | **NOW — planned in Phase 2, not yet executed** (round-5 correction, GPT 5.6: Phase 2 has not run yet, so this cannot be marked DONE) | Phase 2 execution | the document itself, once Stage 2.5.3 actually runs | triggers not yet met for any workstream |
| Additional output formats (Word/PDF/HTML/PowerPoint) | Phase 5.5B, Subphase 5.5B.1 | RESEARCH | a real required output format identified | Stage 5.5B.1.5's fidelity/golden-master validation | no required format exists yet |
| Records, retention, audit | Phase 8, Subphase 8.4 | LATER | Phase 3 retrospective surfaces real requirements | Stage 8.4.5's policy/legal review | no pilot has run yet to derive real requirements from |

---


| Reusable SharePoint plugin extraction from the legacy source repository | Phase 9, Subphases 9.1–9.9 | LATER | Pinned source baseline, stable destination conventions, Phase 3 evidence patterns, and one approved pilot capability | Phase 9 exit gate: one independent reusable plugin with neutral fixtures, parity and independence proof, source repository unchanged | Must not interrupt current Phases 3–8 or copy project-specific plugins wholesale. **Updated 2026-08-03:** the LegacySource `sharepoint-migration` source inventory (34 skills, directly audited, corrected from earlier 31/33 estimates) has been directly audited — see `docs/superpowers/specs/phase-9-reusable-sharepoint-plugin-extraction-spec.md` §8c–§8e. Phase 9 covers all applicable `sharepoint-migration` capabilities, not only the subset overlapping Phase 6. Phase 9 reuses the final workbench plugin structure (destination-plugin-matching rule, §8e) — existing plugins are preferred over new ones. 5 of 7 candidate new engineering plugins (`sharepoint-discovery`, `sharepoint-schema`, `sharepoint-page-modernization`, `sharepoint-link-remediation`, `sharepoint-content-migration`) are provisionally evidence-justified; 2 (`sharepoint-provisioning`, `sharepoint-validation-and-reconciliation`) are not — all remain evidence-gated, none approved. No LegacySource migration or extraction has started; the legacy repository remains intact and unmodified. `ords-integration-migration` remains excluded from Phase 9 by default (`ORDS_SPECIFIC_OUT_OF_SCOPE`). |
| Selective reuse of generic skills currently housed under project-specific or ORDS plugins | Phase 9, Stages 9.2.2 and 9.9.2 | LATER | Skill-level responsibility and coupling review | Skill disposition and backlog decision records | ORDS integration framework and court-system business rules are out of scope; only independently generic SharePoint skills may qualify |
| Shared Claude/Copilot rule reconciliation from the legacy repository | Phase 9, Subphase 9.4 | LATER | Pinned source rules plus current destination instruction hierarchy | Rule-classification report, reviewed destination diffs, and proof that LegacySource/environment overlays remain in the source repository | Wholesale copying would mix reusable engineering rules with project and environment facts |

## Global Gating Rules (carried from architecture review, unchanged)

- Repository rename: **deferred**, not rejected — low-urgency, revisit anytime.
- No new plugins beyond the four Phase 4.5 core plugins (successors to `docx-to-content`, decommissioned
  2026-08-01) until Phase 3/4.5 evidence justifies the next one — **note (updated 2026-08-03):
  `sharepoint-content-publication` already exists as a `TRANSITIONAL_HOLDING_LOCATION` (see
  `CLAUDE.md`), being completed under Phase 6 Task 0.15. The naming reconciliation this line
  previously flagged is resolved: the approved domain name is `sharepoint-agents-and-skills` (not
  `sharepoint-knowledge`, that name is rejected/superseded — see `docs/superpowers/specs/
  2026-08-02-sharepoint-agents-and-skills-plugin-design.md`), being created under Phase 6 Task 0.
  `workbench-setup` (design-complete per `docs/superpowers/specs/2026-08-02-multi-document-
  destination-configuration-design.md` Section 8) is a third authorized exception, created under
  Phase 6 Task 0.17. All three are explicit, named exceptions to this gating rule, not violations
  of it.
- **No new general-purpose routing/orchestration agent** (e.g. a `knowledge-workbench-agent` that decides
  which plugin/journey to invoke) **until ≥2 plugins with ≥2 distinct user journeys exist.** This is
  distinct from Phase 5's bounded knowledge-agent pilot (round-5 clarification, GPT 5.6): a single,
  scoped agent grounded in one library, gated by Phase 5's own entry gate (governed library + confirmed
  agent-creation permissions), may proceed independent of this plugin-count gate — it is not the class of
  agent this rule exists to prevent.
- Nothing past Phase 2 is authorized to *build*; Phases 3.0+ are planned in structure, gated on evidence.
- Every far-phase stage is deliberately structural, not speculative: real requirements (tenant facts, pilot
  outcomes, a second runtime) are prerequisites, not assumptions.
- **RESEARCH vs. REJECTED discipline (round-4 fix):** a phase/workstream gated on a missing *fact* (tenant
  capability, second runtime) or a missing *use case/owner* (Cowork, Copilot Studio) is RESEARCH, not
  REJECTED — REJECTED is reserved for something this plan has an actual architectural objection to, which
  currently applies to nothing in this document. Workstream G (Cowork/Copilot Studio) was previously
  mislabeled REJECTED; it is RESEARCH, same species as Workstreams D/E, gated on an owner-and-use-case
  trigger, not a decision against scope.

---

## Traceability Statement

Every subject raised across this initiative, including the selective Phase 9 plugin-extraction path, is accounted for in the Full Traceability Matrix above — as an
active NOW/NEXT stage, a stated gating dependency with its own phase/stage home, or an explicit
LATER/RESEARCH disposition with its reason and prerequisite. Nothing is silently dropped; nothing beyond
Phase 2 is silently promoted to "planned in detail" without its prerequisite evidence existing first; and
nothing is labeled REJECTED merely for lacking evidence that could still arrive.
